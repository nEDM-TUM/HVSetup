#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Christian Velten'

HAS_ROOT_LIB = True

import LIB.Exceptions
import LIB.File
import LIB.Compression
from LIB.USBTMCInstrument import USBTMCObject, USBInstruments
import LIB.OsciUSB as OsciUSB
from LIB.GPIOSensor import GPIOSensor, GPIOSensors
try: import LIB.ROOT_IO
except ImportError: HAS_ROOT_LIB = False

import argparse
import logging
import logging.handlers
import os
import signal
import sys
import time
"""
### --------------------------------------------------------------------------------------------------------------------
"""
# Defaults
LOG_FILENAME = "/tmp/Lab_ReadContinuous.log"
LOG_LEVEL = logging.INFO
# Define and parse command-line arguments
parser = argparse.ArgumentParser(description="Python script to continuously read data from the diode board in the lab.")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")
parser.add_argument("-s", "--service", help="script run as service? disables all I/O from std(in|out).", action="store_true")
parser.add_argument("-v", "--verbose", help="set if you want to save more data to file / output", action="store_true")
parser.add_argument("--acquire", help="how does the oscilloscope acquire data", choices=['SAMPLE', 'AVERAGE'], default='SAMPLE')
parser.add_argument("--samples", help="how many samples should be acquired when acquire is set to average", type=int, default=2, choices=[2**i for i in range(1, 10)])
parser.add_argument("--pattern", help="filename pattern")
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
"""
### --------------------------------------------------------------------------------------------------------------------
"""
# manual params
OSCI_CHANNELS = [1, 2, 3]
"""
### --------------------------------------------------------------------------------------------------------------------
"""
SIGTERM = False


def signal_SIGTERM_handler(signal, frame):
	global SIGTERM
	SIGTERM = True
	sys.stderr.write("RECEIVED SIGTERM! Trying to terminate smooth and easy...")


def get_osci_mean_data(instrument):
	instrument.cmd("*WAI")
	ch1 = float(instrument.cmd_and_return("MEASUREMENT:MEAS1:MEAN?").strip().replace('"', ''))
	ch1u = float(instrument.cmd_and_return("MEASUREMENT:MEAS1:STDDEV?").strip().replace('"', ''))
	ch2 = float(instrument.cmd_and_return("MEASUREMENT:MEAS2:MEAN?").strip().replace('"', ''))
	ch2u = float(instrument.cmd_and_return("MEASUREMENT:MEAS2:STDDEV?").strip().replace('"', ''))
	ch3 = float(instrument.cmd_and_return("MEASUREMENT:MEAS3:MEAN?").strip().replace('"', ''))
	ch3u = float(instrument.cmd_and_return("MEASUREMENT:MEAS3:STDDEV?").strip().replace('"', ''))
	return {'CH1': ch1, 'CH1u': ch1u, 'CH2': ch2, 'CH2u': ch2u, 'CH3': ch3, 'CH3u': ch3u}


def get_battery_status():
	return {'Up': 0, 'Um': 0, 'Upu': 0, 'Umu': 0}


def get_temperature(sensor):
	temp = float(sensor.read().strip())
	return {'TC': temp, 'TCu': 0.5}

"""
### --------------------------------------------------------------------------------------------------------------------
"""
signal.signal(signal.SIGTERM, signal_SIGTERM_handler)

"""
	Set measurement parameters
"""
# args
if args.service:
	data_directory = LIB.File.set_directory('/var/LabTableTop/data/', ask=False)
else:
	data_directory = LIB.File.set_directory('./data/', ask=True)
if not args.pattern is None:
    filename_pattern_begin = args.pattern
else:
    filename_pattern_begin = 'Lab_ReadContinuous_'

sleep_time_frequency_step = 1.0  # seconds
if args.stepsleep and args.stepsleep >= 0:
	sleep_time_frequency_step = args.stepsleep

"""
	Initialize oscilloscope for battery measurement
"""
while True:
	try:
		print "\n", "initializing USB instrument..."
		sOsci = USBTMCObject(USBInstruments['LABOR']['vendorID'], USBInstruments['LABOR']['productID'], USBInstruments['LABOR']['serialNo'])
		print "\tInstrument: " + str(sOsci.cmd_and_return("*IDN?"))
		OsciUSB.setup_acquire(sOsci, mode=args.acquire, num=args.samples)
		OsciUSB.setup_measurement_mean(sOsci, channels=[1, 2, 3], statistics=True, statistics_samples=10)
		print ""
		break
	except LIB.Exceptions.USBException as e:
		print e
		time.sleep(5.0)
		pass
"""
	Initialize temperature sensor
"""
while True:
	print "\n", "initializing temperature sensor..."
	sTherm = GPIOSensor(GPIOSensors['THERM_LAB'])
	if sTherm.read() is None:
		continue
	print ""
	break


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
	strftime = time.strftime("%Y-%m-%d_%H%M")
	starttime, offsettime, meas_time_start, meas_time_stop = time.time(), 0, 0, 0
	count = 0

	"""
	CREATE A NEW FILE WITH INCREASING FILE COUNT
	"""
	filename = LIB.File.get_filename_filecount(data_directory, filename_pattern_begin)

	handle = open(data_directory + filename, 'w')
	logger.info("File opened: '" + data_directory + filename + "'")

	"""
	WRITE OSCI-CHANNEL INFORMATION TO FILE
	"""
	try:
		handle.write("#Osci_CH1==" + OsciUSB.dict2string(OsciUSB.get_values_channel(sOsci, 1, OsciUSB.queriesChannelInfo)) + '\n')
		handle.write("#Osci_CH2==" + OsciUSB.dict2string(OsciUSB.get_values_channel(sOsci, 2, OsciUSB.queriesChannelInfo)) + '\n')
		handle.write("#Osci_CH3==" + OsciUSB.dict2string(OsciUSB.get_values_channel(sOsci, 3, OsciUSB.queriesChannelInfo)) + '\n')
		handle.write("#TEMP==" + GPIOSensors['THERM_LAB'] + '\n')
	except LIB.Exceptions.USBException:
		handle.close()
		os.remove(data_directory + filename)
		continue

	"""
	WRITE TIMESTAMP AND KEY LIST TO FILE
	"""
	handle.write("#TIMESTAMP==" + strftime + '\n')
	handle.write("#Keys==TIME\tUp\tUpu\tUm\tUmu\tCH1\tCH1u\tCH2\tCH2u\tCH3\tCH3u\tTC\tTCu" + '\n')

	"""
	DATA STORAGE IN RAM
	"""
	data = {
		'TIME': [], 'TIME_OFFSET': [],
		'CH1': [], 'CH1u': [],
		'CH2': [], 'CH2u': [],
		'CH3': [], 'CH3u': [],
		'Up': [], 'Upu': [],
		'Um': [], 'Umu': [],
		'TC': [], 'TCu': []
	}

	while not SIGTERM:
		try:
			meas_time_start = time.time()
			data_Osci = get_osci_mean_data(sOsci)
			data_Batt = get_battery_status()
			data_Temp = get_temperature(sTherm)
			meas_time_stop = time.time()
			meas_time = int((meas_time_stop+meas_time_start)/2.-starttime)

			data['TIME'].append(meas_time)
			data['TIME'].append(time.time())
			for key in data_Osci.keys(): data[key].append(data_Osci[key])
			for key in data_Batt.keys(): data[key].append(data_Batt[key])
			for key in data_Temp.keys(): data[key].append(data_Temp[key])

			handle.write("{_t}".format(_t=meas_time))
			handle.write("\t{Up}\t{Upu}\t{Um}\t{Umu}".format(Up=data['Up'][-1], Upu=data['Upu'][-1], Um=data['Um'][-1], Umu=data['Umu'][-1]))
			handle.write("\t{CH1}\t{CH1u}\t{CH2}\t{CH2u}\t{CH3}\t{CH3u}".format(
				CH1=data['CH1'][-1], CH1u=data['CH1u'][-1],
				CH2=data['CH2'][-1], CH2u=data['CH2u'][-1],
				CH3=data['CH3'][-1], CH3u=data['CH3u'][-1]))
			handle.write("\t{TC}\t{TCu}".format(TC=data['TC'][-1], TCu=data['TCu'][-1]))
			handle.write("\t{TO}".format(TO=data['TIME_OFFSET'][-1]))
			handle.write("\n")

			if count % 60 == 0:  # or count == 10:
				if args.service:
					logger.info("battery status: {0:5.2f} / {1:5.2f} (V)".format(0, 0) + \
						" | DIFF-CHANNEL: {0:5.2f} +/- {1:5.2f} mV".format(data['CH1'][-1]*1E+3, data['CH1u'][-1]*1E+3) + \
						" | TC: {0:5.2f} +/- {1:5.2f} °C".format(data['TC'][-1], data['TCu'][-1]))
				else:
					print time.strftime("%Y-%m-%d @ %H:%M:%S (%Z): ") + \
						"battery status: {0:5.2f} / {1:5.2f} (V)".format(0, 0) + \
						" | DIFF-CHANNEL: {0:5.2f} +/- {1:5.2f} mV".format(data['CH1'][-1]*1E+3, data['CH1u'][-1]*1E+3) + \
						" | TC: {0:5.2f} +/- {1:5.2f} °C".format(data['TC'][-1], data['TCu'][-1])
				handle.flush()
				os.fsync(handle.fileno())
			time.sleep(args.stepsleep)
		except LIB.Exceptions.USBException:
			logger.error("(USBError): trying to reconnect to our devices if necessary...")
			if not sOsci.is_open():
				sOsci.connect()
			continue
		except KeyboardInterrupt:
			SIGTERM = True
			logger.warning("received KeyboardInterrupt at {_strftime}".format(_strftime=time.strftime("%Y-%m-%d @ %H:%M:%S")))
			break
		count += 1
	# while not SIGTERM

	handle.close()

	# Either compress file and print saved message or just print that message
	if args.compress:
		LIB.Compression.gzip_file(data_directory + filename)
		os.remove(data_directory + filename)
		print "wrote data to '" + data_directory + filename + ".gz'"
	else:
		print "wrote data to '" + data_directory + filename + "'"
	# If ROOT libraries have been loaded -> create a root file with tree
	if HAS_ROOT_LIB:
		LIB.ROOT_IO.ROOT_IO.write_data(data_directory + filename, "Lab_ReadContinuous", data)
		print "created ROOT file from data ('" + data_directory + filename + ".root')"
#end while-not-SIGTERM
#
logger.info("#### END OF PROGRAM ####")
