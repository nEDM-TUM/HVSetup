#!/usr/bin/env python
__author__ = 'Christian Velten'

SIGTERM = False
FORCE_DEBUG = False
HAS_ROOT_LIB = True

import LIB.Compression
import LIB.File
from LIB.GPIOSensor import GPIOSensor, GPIOSensors
import LIB.OsciUSB as OsciUSB
from LIB.SerialInstrument import SerialObject, SerialInstruments
try: from LIB.USBTMCInstrument import USBTMCObject, USBInstruments
except ImportError: FORCE_DEBUG = True
try: import LIB.ROOT_IO
except ImportError: HAS_ROOT_LIB = False

import argparse
import itertools
import logging
import logging.handlers
import numpy as np
import os
import signal
import sys
import time


def signal_SIGTERM_handler(signal, frame):
	global SIGTERM
	SIGTERM = True
	sys.stderr.write("RECEIVED SIGTERM! Trying to terminate smooth and easy...")

def signal_SIGINT_handler(signal, frame):
	global SIGINT
	SIGINT = True
	sys.stderr.write("RECEIVED SIGINT! Waiting for methods to finish before interrupting...")


def exit(ser=None, code=0, e=None, usbtmc=None):
	if not e is None:
		print e
	if not ser is None:
		ser.cmd("LDON OFF")
		time.sleep(1)
	if not usbtmc is None:
		pass
	sys.exit(code)


def get_osc_measurements(s, three=False):
	s.cmd("*WAI")
	ch1  = float(s.ask("MEASU:MEAS1:MEAN?").strip().replace('"',''))
	ch1u = float(s.ask("MEASU:MEAS1:STDDEV?").strip().replace('"',''))
	ch2  = float(s.ask("MEASU:MEAS2:MEAN?").strip().replace('"',''))
	ch2u = float(s.ask("MEASU:MEAS2:STDDEV?").strip().replace('"',''))
	if three:
		ch3  = float(s.ask("MEASU:MEAS3:MEAN?").strip().replace('"',''))
		ch3u = float(s.ask("MEASU:MEAS3:STDDEV?").strip().replace('"',''))
		return {'DIFF': ch1, 'DIFFu': ch1u, 'MODU': ch2, 'MODUu': ch2u, 'OSC3': ch3, 'OSC3u': ch3u}
	else:
		return {'DIFF': ch1, 'DIFFu': ch1u, 'MODU': ch2, 'MODUu': ch2u, 'OSC3': 0.0, 'OSC3u': 0.0}


def get_temperature(sensor):
	temp = float(sensor.read().strip())
	return {'TEMP': temp, 'TEMPu': 0.5} # todo fix

# SET-UP OF ARGUMENT PARSER
parser = argparse.ArgumentParser(description="")
parser.add_argument("-c", "--compress", help="", action="store_true")
parser.add_argument("-l", "--log", help="file to write log to")
parser.add_argument("-s", "--service", help="script run as service? disables all I/O from std(in|out).", action="store_true")
parser.add_argument("-d", "--debug", help="just print the values", action="store_true")
parser.add_argument("-o", "--ofile", help="specify the output file")
parser.add_argument("-P", "--PROP", type=float, default=-20.0)
parser.add_argument("-I", "--INTG", type=float, default=1000.0)
parser.add_argument("--LLIM", type=float, default=-10.0)
parser.add_argument("--ULIM", type=float, default=10.0)
parser.add_argument("--noosci", action="store_true")
args = parser.parse_args()
if FORCE_DEBUG: args.debug = True
LOG_LEVEL = logging.INFO
if args.log:
	LOG_FILENAME = args.log
else:
	LOG_FILENAME = "./data/PI_Stability.log"

# SET-UP OF LOGGER
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logHandler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=1000)
logFormatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
logHandler.setFormatter(logFormatter)
logger.addHandler(logHandler)
class MyLogger(object):
	def __init__(self, logger, level):
		self.logger = logger
		self.level = level
	def write(self, message):
		if message.rstrip() != "":
			self.logger.log(self.level, message.rstrip())
if args.service:
	sys.stdout = MyLogger(logger, logging.INFO)
	sys.stderr = MyLogger(logger, logging.ERROR)
logger.info("---------------------------------------------------------------------------------------------------------")
# SIGNAL HANDLER
signal.signal(signal.SIGTERM, signal_SIGTERM_handler)
signal.signal(signal.SIGINT, signal_SIGINT_handler)

# INITIAL PARAMETERS / RANGES
DATA_KEYS = ['TIME', 'TIME_OFFSET', 'LDC_I', 'LDC_T', 'PID_PROP', 'PID_INTG', 'PID_MEAS', 'PID_MEASu', 'PID_PXER', 'PID_PXERu', 'PID_OUTP', 'PID_OUTPu', 'DIFF', 'DIFFu', 'MODU', 'MODUu', 'TEMP', 'TEMPu', 'OSC3', 'OSC3u']
INI_LD_I = 290.65
INI_POLA, INI_PROP, INI_INTG, INI_DERV, INI_OFST = 'NEG', args.PROP, args.INTG, 1E-5, 0.
INI_PID_LLIM, INI_PID_ULIM = args.LLIM, args.ULIM
INI_INTERMEDIATE_STEPS = 10

#
# ___MAIN___
#

# CONNECT TO DEVICES
try:
	if not args.debug:
		LDC = SerialObject(SerialInstruments['LDC501'])
		PID = SerialObject(SerialInstruments['SIM960'], wait=0.01)
		if not args.noosci:
			OSC = USBTMCObject(USBInstruments['LABOR']['vendorID'], USBInstruments['LABOR']['productID'])
		TEM = GPIOSensor(GPIOSensors['THERM_LAB'])

		PID.cmd("*CLS")

		print "Instrument (LDC):\n\t" + LDC.ask("*IDN?")
		print "Instrument (PID):\n\t" + PID.ask("*IDN?")
		if not args.noosci:
			print "Instrument (OSC):\n\t" + OSC.ask("*IDN?")
		if TEM.read() is None:
			raise ValueError()

		LDC.cmd("TOKN ON")
		LDC.cmd("LDON OFF;MODU OFF; RNGE LOW; SMOD CC; SIBW LOW; SYND 5")
		time.sleep(1)

		PID.cmd("TOKN ON; CONS OFF")
		PID.cmd("INPT INT;SETP 0.0;RAMP OFF")
		PID.cmd("AMAN PID;MOUT 0.0")
		PID.cmd("ULIM {0};LLIM {1}".format(INI_PID_ULIM, INI_PID_LLIM))
		PID.cmd("APOL {0};GAIN {1:.4f}".format(INI_POLA, INI_PROP))
		PID.cmd("INTG {0};DERV {1};OFST {2}".format(INI_INTG, INI_DERV, INI_OFST))
		PID.cmd("PCTL ON;ICTL ON")
		PID.cmd("DCTL OFF;OCTL OFF") # (P,I,D,O)=(1,1,0,0)
		PID.cmd("SOUT; FPLC 50")
		PID.cmd("DISP EMN")

		if not args.noosci:
			#OsciUSB.setup_measurement_mean(OSC, [1, 2], True, 10)
			OsciUSB.setup_measurement_mean(OSC, [1, 2, 3], True, 10)
		time.sleep(1)
except Exception as e:
	exit(LDC, 1, e=e)

if not args.service:
	cin = raw_input("We are about to switch on the LASER, proceed? [yN] ")
	if cin is None or cin.lower() != "y":
		exit(LDC, 0)

try:
	if not args.debug:
		LDC.cmd("SILD {0}".format(INI_LD_I))
		LDC.cmd("LDON ON")
		time.sleep(6)
		LDC.cmd("MODU ON")
		time.sleep(4)
except Exception as e:
	exit(LDC, 1, e=e)

# CREATE A NEW FILE WITH INCREASING FILE COUNT
if args.service:
	data_directory = LIB.File.set_directory('/var/LABOR/data/', ask=False)
else:
	data_directory = LIB.File.set_directory('./data/', ask=True)
filename_pattern_begin = 'PI_Stability_'
if args.ofile is None or not os.exists(args.ofile):
	filename = LIB.File.get_filename_filecount(data_directory, filename_pattern_begin)
else:
	filename = args.ofile
if not args.debug:
	handle = open(data_directory + filename, 'w')
	logger.info("handle.open('"+data_directory+filename+"', 'w')")

data = {key: [] for key in DATA_KEYS}

SIGTERM, SIGINT, count = False, False, 0
starttime = time.time()
while not (SIGTERM or SIGINT):
	try:
		PID.ask("LCME?")
		time.sleep(1.0)

		istep = 0
		meas_time_start = time.time()
		while True:
			try:
				LDC_I = float(LDC.ask("RILD?"))
				LDC_T = float(LDC.ask("TTRD?"))
				PID_PROP = float(PID.ask("GAIN?"))
				PID_INTG = float(PID.ask("INTG?"))
				if not args.noosci: OSC_MEASU = get_osc_measurements(OSC, three=True)
				else: OSC_MEASU = {'DIFF': 0, 'DIFFu': 0, 'MODU': 0, 'MODUu': 0, 'OSC3': 0, 'OSC3u': 0}
				TEM_MEASU = get_temperature(TEM)
			except ValueError: continue
			except KeyboardInterrupt: SIGTERM = True
			finally: break

		# GET MMON;EMON;OMON X-times to get a MEAN and STDDEV
		_PID_MEAS, _PID_PXER, _PID_OUTP = np.empty(INI_INTERMEDIATE_STEPS), np.empty(INI_INTERMEDIATE_STEPS), np.empty(INI_INTERMEDIATE_STEPS)
		while istep < INI_INTERMEDIATE_STEPS:
			while True:
				try:
					MPO = PID.ask("MMON?;EMON?;OMON?").strip().split('\n')
					PID_MEAS = float(MPO[0].strip())
					PID_PXER = float(MPO[1].strip())
					PID_OUTP = float(MPO[2].strip())
				except ValueError: continue
				except KeyboardInterrupt: SIGTERM = True
				else:
					_PID_MEAS[istep] = np.fabs(PID_MEAS)
					_PID_PXER[istep] = np.fabs(PID_PXER)
					_PID_OUTP[istep] = np.fabs(PID_OUTP)
				finally: break
			time.sleep(1)
			istep += 1
		if SIGTERM: continue
		meas_time = int((meas_time_start+time.time())/2.-starttime)

		data['TIME'].append(meas_time)
		data['TIME_OFFSET'].append(meas_time+starttime)
		data['LDC_I'].append(LDC_I)
		data['LDC_T'].append(LDC_T)
		data['PID_PROP'].append(PID_PROP)
		data['PID_INTG'].append(PID_INTG)
		data['PID_MEAS'].append(_PID_MEAS.mean())
		data['PID_MEASu'].append(_PID_MEAS.std())
		data['PID_PXER'].append(_PID_PXER.mean())
		data['PID_PXERu'].append(_PID_PXER.std())
		data['PID_OUTP'].append(_PID_OUTP.mean())
		data['PID_OUTPu'].append(_PID_OUTP.std())
		for key in OSC_MEASU.keys(): data[key].append(OSC_MEASU[key])
		for key in TEM_MEASU.keys(): data[key].append(TEM_MEASU[key])

		for key in DATA_KEYS:
			handle.write("{0}\n".format(data[key][-1]) if key==DATA_KEYS[-1] else "{0}\t".format(data[key][-1]))

		if count % 10 == 0:
			handle.flush()
			os.fsync(handle.fileno())
			logger.info("MPO = {0:2.5f}  {1:2.5f}  {2:2.5f}".format(_PID_MEAS.mean(), _PID_PXER.mean(), _PID_OUTP.mean()))
		count += 1
	except KeyboardInterrupt:
		SIGTERM = True
		continue
	except Exception as e:
		handle.close()
		exit(LDC, 1, e=e, usbtmc=OSC)
	# end try
# end while not (SIGTERM or SIGINT)
if not args.debug:
	LDC.cmd("LDON 0")
	handle.close()


if not args.debug and args.compress:
	LIB.Compression.gzip_file(data_directory + filename)
	os.remove(data_directory + filename)
if not args.debug and HAS_ROOT_LIB:
	LIB.ROOT_IO.ROOT_IO.write_data(data_directory + filename, "PI_Stability", data)
print "wrote data files to: " + data_directory + "\nwith filename-begin: " + filename
print "### END OF PROGRAM REACHED ###"
exit(LDC, 0, usbtmc=OSC)
