#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Christian Velten'

HAS_ROOT_LIB = True

import LIB.Exceptions
import LIB.File
import LIB.Compression
from LIB.GPIOSensor import GPIOSensor, GPIOSensors
try: import LIB.ROOT_IO
except ImportError: HAS_ROOT_LIB = False

import argparse
import logging
import logging.handlers
import numpy as np
import os
import signal
import sys
import time
"""
### --------------------------------------------------------------------------------------------------------------------
"""
# Defaults
LOG_FILENAME = "/tmp/Temperature.log"
LOG_LEVEL = logging.INFO
# Define and parse command-line arguments
parser = argparse.ArgumentParser(description="Python script to continuously read data from the temperature sensor.")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")
parser.add_argument("-s", "--service", help="script run as service? disables all I/O from std(in|out).", action="store_true")
parser.add_argument("-v", "--verbose", help="set if you want to save more data to file / output", action="store_true")
parser.add_argument("--stepsleep", type=float, help="sleep how long (minimum/offset) between acquire-sets", default=1.0)
parser.add_argument("--compress", help="compress data files after they have been written", action="store_true")
parser.add_argument("--sensor")
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
SIGTERM = False


def signal_SIGTERM_handler(signal, frame):
	global SIGTERM
	SIGTERM = True
	sys.stderr.write("RECEIVED SIGTERM! Trying to terminate smooth and easy...")


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
	data_directory = LIB.File.set_directory('/var/Temperature/data/', ask=False)
else:
	data_directory = LIB.File.set_directory('./data/', ask=True)
filename_pattern_begin = 'Temperature_'

"""
	Initialize temperature sensor
"""
while True:
	print "\n", "initializing temperature sensor..."
	if not args.sensor or args.sensor == "":
		sTherm = GPIOSensor(GPIOSensors['THERM_LAB'])
	else:
		sTherm = GPIOSensor(GPIOSensors[args.sensor])
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
	WRITE TEMP INFORMATION TO FILE
	"""
	try:
		handle.write("#TEMP==" + GPIOSensors['THERM_LAB'])
	except LIB.Exceptions.USBException:
		handle.close()
		os.remove(data_directory + filename)
		continue

	"""
	WRITE TIMESTAMP AND KEY LIST TO FILE
	"""
	handle.write("#TIMESTAMP==" + strftime + '\n')
	handle.write("#Keys==TIME\tTC\tTCu" + '\n')

	"""
	DATA STORAGE IN RAM
	"""
	data = {
		'TIME': [],
		'TC': [], 'TCu': []
	}

	while not SIGTERM:
		try:
			meas_time_start = time.time()
			data_Temp = get_temperature(sTherm)
			meas_time_stop = time.time()
			meas_time = int((meas_time_stop+meas_time_start)/2.-starttime)

			data['TIME'].append(meas_time)
			for key in data_Temp.keys(): data[key].append(data_Temp[key])

			handle.write("{_t}".format(_t=meas_time))
			handle.write("\t{TC}\t{TCu}".format(TC=data['TC'][-1], TCu=data['TCu'][-1]))
			handle.write("\n")

			if count % 1 == 0:  # or count == 10:
				if args.service:
					logger.info("TC: {0:5.2f} +/- {1:5.2f} °C".format(data['TC'][-1], data['TCu'][-1]))
				else:
					print time.strftime("%Y-%m-%d @ %H:%M:%S (%Z): ") + \
						" | TC: {0:5.2f} +/- {1:5.2f} °C".format(data['TC'][-1], data['TCu'][-1])
				handle.flush()
				os.fsync(handle.fileno())
			time.sleep(args.stepsleep)
		except LIB.Exceptions.USBException:
			logger.error("(USBError): trying to reconnect to our devices if necessary...")
			if sTherm.read() is None:
				sTherm = GPIOSensor(GPIOSensors['THERM_LAB'])
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
