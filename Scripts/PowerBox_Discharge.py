#!/usr/bin/env python
__author__ = 'Christian Velten'

HAS_ROOT_LIB = True

import LIB.File
import LIB.Compression
import LIB.Exceptions
from LIB.USBTMCInstrument import USBTMCObject, USBInstruments
import LIB.OsciUSB as OsciUSB
try: import LIB.ROOT_IO
except ImportError: HAS_ROOT_LIB = False

import argparse
import logging
import logging.handlers
import numpy as np
import os
import re
import signal
import sys
import time

"""
### --------------------------------------------------------------------------------------------------------------------
"""
# Defaults
LOG_FILENAME = "/tmp/PowerBox_Discharge.log"
LOG_LEVEL = logging.INFO
# Define and parse command-line arguments
parser = argparse.ArgumentParser(description="Python script to utlizie oscilloscope and lock-in amplifier to characterize the PowerBox.")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")
parser.add_argument("-s", "--service", help="script run as service? disables all I/O from std(in|out).", action="store_true")
parser.add_argument("--stepsleep", type=float, help="sleep how long (minimum/offset) after setting a new frequency", default=1.0)
parser.add_argument("--compress", help="compress data files after they have been written", action="store_true")
# parse
args = parser.parse_args()
if args.log:
	LOG_FILENAME = args.log
"""
### Configure logging into a file --------------------------------------------------------------------------------------
"""
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logHandler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=1000)
logFormatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
logHandler.setFormatter(logFormatter)
logger.addHandler(logHandler)
# Class to capture stdout and stderr
class MyLogger(object):
	def __init__(self, logger, level):
		""" Needs a logger and logger level. """
		self.logger = logger
		self.level = level
	def write(self, message):
		if message.rstrip() != "":
			self.logger.log(self.level, message.rstrip())
# Replace stdout and stderr with MyLogger if args.service
if args.service:
	sys.stdout = MyLogger(logger, logging.INFO)
	sys.stderr = MyLogger(logger, logging.ERROR)
logger.info("---------------------------------------------------------------------------------------------------------")
logger.info(time.strftime("timestamp: %Y-%m-%d (%A) @ %H:%M:%S (%Z)"))
"""
### --------------------------------------------------------------------------------------------------------------------
"""
SIGTERM = False


def signal_SIGTERM_handler(signal, frame):
	global SIGTERM
	SIGTERM = True
	sys.stderr.write("RECEIVED SIGTERM. Trying to terminate smooth and easy...")


def get_osci_mean_data(instrument, samples=10, sleep=0):
	# takes 0.5s/10s
	count = 0
	meanVp, meanVm = np.empty(samples), np.empty(samples)
	instrument.cmd("*WAI")
	while count < samples:
		meanVp[count] = float(instrument.cmd_and_return("MEASU:MEAS1:VAL?").strip().replace('"', ''))
		meanVm[count] = float(instrument.cmd_and_return("MEASU:MEAS2:VAL?").strip().replace('"', ''))
		count += 1
		time.sleep(sleep)
	return {'Vp': np.mean(meanVp), 'Vm': np.mean(meanVm), 'Vp_STDDEV': np.std(meanVp), 'Vm_STDDEV': np.std(meanVm)}


"""
### --------------------------------------------------------------------------------------------------------------------
"""

"""
	Registering the signal handler
"""
signal.signal(signal.SIGTERM, signal_SIGTERM_handler)


"""
	Set measurement parameters
"""
if args.service:
	data_directory = LIB.File.set_directory('/var/PowerBox_Characterization/data/', ask=False)
else:
	data_directory = LIB.File.set_directory('./data/', ask=True)
filename_pattern_begin = 'PowerBox_Discharge_'
sleep_time_frequency_step = 1.0  # seconds
sleep_time_sampling_rate = 0
""" ARGPARSE """
if args.stepsleep and args.stepsleep >= 0:
	sleep_time_frequency_step = args.stepsleep



"""
	Initialize oscilloscope for battery measurement
"""
while True:
	try:
		print "\n", "initializing USB instrument..."
		sOsci = USBTMCObject(USBInstruments['HALLE']['vendorID'], USBInstruments['HALLE']['productID'], USBInstruments['HALLE']['serialNo'])
		print "\tInstrument: " + str(sOsci.cmd_and_return("*IDN?"))
		OsciUSB.setup_measurement_mean(sOsci, channels=[1, 2], statistics=False, statistics_samples=-1)
		break
	except LIB.Exceptions.USBException as e:
		print e
		time.sleep(5.0)
		pass

"""
	START?
"""
if not args.service:
	cin = raw_input("\nBEGIN MEASUREMENT? [Y] ")
	if cin != "" and cin.upper() != "Y" and cin.upper() != "YES":
		sys.exit(0)

"""
	Measurement loop
"""
while not SIGTERM:
	strftime = time.strftime("%Y-%m-%d_%H%M%Z")
	starttime, offsettime, meas_time_start, meas_time_stop = time.time(), 0, 0, 0
	_count = 0

	i = 1
	while True:
		files = [True for f in os.listdir(data_directory) if re.match(r'' + filename_pattern_begin+("%0*d" % (4, i)) + '.*', f)]
		if len(files) == 0:
			break
		i += 1
	filename = filename_pattern_begin + ("%0*d" % (4, i)) + '_' + strftime + ".dat"

	handle = open(data_directory + filename, 'w')
	logger.info("File opened: '" + data_directory + filename + "'")

	try:
		handle.write("#Osci_CH1==" + OsciUSB.dict2string(OsciUSB.get_values_channel(sOsci, 1, OsciUSB.queriesChannelInfo)) + '\n')
		handle.write("#Osci_CH2==" + OsciUSB.dict2string(OsciUSB.get_values_channel(sOsci, 2, OsciUSB.queriesChannelInfo)) + '\n')
	except LIB.Exceptions.USBException:
		handle.close()
		os.remove(data_directory + filename)
		continue

	handle.write("#TIMESTAMP==" + strftime + '\n')
	handle.write("#Keys==TIME\tPowerBox_Vp_MEAN\tPowerBox_Vp_STDDEV\tPowerBox_Vm_MEAN\tPowerBox_Vm_STDDEV\n")

	data = {'TIME': [], 'Vp': [], 'Vm': [], 'Vp_STDDEV': [], 'Vm_STDDEV': []}

	while not SIGTERM:
		try:
			meas_time_start = time.time()
			data_PowerBox = get_osci_mean_data(sOsci, samples=20)
			meas_time_stop = time.time()

			data['TIME'].append(int((meas_time_stop+meas_time_start)/2.-starttime))
			for key in data_PowerBox.keys(): data[key].append(data_PowerBox[key])

			handle.write("{_t}\t".format(_t=int((meas_time_stop+meas_time_start)/2.-starttime)))
			handle.write("{_PowerVp}\t{_PowerVp_STDDEV}\t{_PowerVm}\t{_PowerVm_STDDEV}\n".format(_PowerVp=data_PowerBox['Vp'],
			                                                                                     _PowerVm=data_PowerBox['Vm'],
			                                                                                     _PowerVp_STDDEV=data_PowerBox['Vp_STDDEV'],
			                                                                                     _PowerVm_STDDEV=data_PowerBox['Vm_STDDEV']))

			#offsettime = time.time() - starttime
			time.sleep(sleep_time_frequency_step)
			_count += 1
			if _count % 100 == 0 or _count == 10:
				if args.service:
					logger.info("battery status: Vp = {_Vp:5.2f} V  |  Vm = {_Vm:5.2f} V".format(_Vp=data_PowerBox['Vp'], _Vm=data_PowerBox['Vm']))
				else:
					print time.strftime("%Y-%m-%d @ %H:%M:%S (%Z): ") + "battery status: Vp = {_Vp:5.2f} V  |  Vm = {_Vm:5.2f} V".format(_Vp=data_PowerBox['Vp'], _Vm=data_PowerBox['Vm'])
				handle.flush()
				os.fsync(handle.fileno())

		except LIB.Exceptions.USBException:
			logger.error("(USBError): trying to reconnect to our devices if necessary...")
			if not sOsci.is_open():
				sOsci.connect()
			continue
		except KeyboardInterrupt:
			SIGTERM = True
			logger.info("received KeyboardInterrupt at {_strftime}".format(_strftime=time.strftime("%Y-%m-%d @ %H:%M:%S (%Z)")))
	# while(True and not SIGTERM)

	handle.close()
	if args.compress:
		LIB.Compression.gzip_file(data_directory + filename)
		os.remove(data_directory + filename)
		print "wrote data to '" + data_directory + filename + ".gz'"
	else:
		print "wrote data to '" + data_directory + filename + "'"
	if HAS_ROOT_LIB:
		LIB.ROOT_IO.ROOT_IO.write_data(data_directory + filename, "PowerBox_Characterize", data)
#end while-not-SIGTERM
logger.info("#### END OF PROGRAM ####")
__author__ = 'Christian Velten'
