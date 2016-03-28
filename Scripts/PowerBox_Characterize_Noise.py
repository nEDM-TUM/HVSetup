#!/usr/bin/env python
__author__ = 'Christian Velten'

HAS_ROOT_LIB = True

import LIB.Exceptions
import LIB.File
import LIB.Compression
from LIB.LockInNoise import LockInNoise
from LIB.USBTMCInstrument import USBTMCObject, USBInstruments
from LIB.SocketInstrument import SocketObject, SocketInstruments
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
LOG_FILENAME = "/tmp/PowerBox_Characterize.log"
LOG_LEVEL = logging.INFO
# Define and parse command-line arguments
parser = argparse.ArgumentParser(description="Python script to utlizie oscilloscope and lock-in amplifier to characterize the PowerBox.")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")
parser.add_argument("-s", "--service", help="script run as service? disables all I/O from std(in|out).", action="store_true")
parser.add_argument("-e", "--external", help="set if using external reference source for lock in", action="store_true")
parser.add_argument("-v", "--verbose", help="set if you want to save more data to file / output", action="store_true")
parser.add_argument("-t", "--timeconstant", help="set the lock-in's time constant", choices=LockInNoise.index2timeconstant, default=10E-3, type=float)
parser.add_argument("-g", "--gain", help="set the sensitivity/gain of the lock-in", choices=LockInNoise.index2gain, default=5E-3, type=float)
parser.add_argument("-n", "--nfreq", type=int, help="how many frequencies shall be probed?")
parser.add_argument("--beginPower", type=int, help="begin at which power of 10 (default 0, must be >=-1)", default=0, choices=xrange(-1, 6))
parser.add_argument("--endPower", type=int, help="end at which power of 10 (default 5, must be <=6)", default=5, choices=xrange(0, 7))
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
SIGTERM = False


def signal_SIGTERM_handler(signal, frame):
	global SIGTERM
	SIGTERM = True
	sys.stderr.write("RECEIVED SIGTERM! Trying to terminate smooth and easy...")


def get_osci_mean_data(instrument, samples=10):
	# takes 0.5s/10s
	count = 0
	meanVp, meanVm = np.empty(samples), np.empty(samples)
	instrument.cmd("*WAI")
	while count < samples:
		meanVp[count] = float(instrument.cmd_and_return("MEASU:MEAS1:VAL?").strip().replace('"', ''))
		meanVm[count] = float(instrument.cmd_and_return("MEASU:MEAS2:VAL?").strip().replace('"', ''))
		count += 1
	return {'Vp': np.mean(meanVp), 'Vm': np.mean(meanVm), 'Vp_STDDEV': np.std(meanVp), 'Vm_STDDEV': np.std(meanVm)}


def get_lockin_display_data(instrument, samples=10):
	# takes 0.8s/10s
	count = 0
	xnoise, ynoise = np.empty(samples), np.empty(samples)
	while count < samples:
		noise = instrument.cmd_and_return('SNAP? 10,11').strip().split(',')
		xnoise[count] = float(noise[0])
		ynoise[count] = float(noise[1])
		count += 1
	return {'XNOISE': np.mean(xnoise), 'XNOISE_STDDEV': np.std(xnoise), 'YNOISE': np.mean(ynoise), 'YNOISE_STDDEV': np.std(ynoise)}


"""
### --------------------------------------------------------------------------------------------------------------------
"""
signal.signal(signal.SIGTERM, signal_SIGTERM_handler)

"""
	Set measurement parameters
"""
print args
if args.service:
	data_directory = LIB.File.set_directory('/var/PowerBox_Characterization/data/', ask=False)
else:
	data_directory = LIB.File.set_directory('./data/', ask=True)
frequencies_beginPower = 1
frequencies_endPower = 5
frequencies_number = 6000
if -1 <= args.beginPower < 6:
	frequencies_beginPower = args.beginPower
if -1 < args.endPower <= 6:
	frequencies_endPower = args.endPower
if frequencies_beginPower > frequencies_endPower:
	tmp = frequencies_beginPower
	frequencies_beginPower = frequencies_endPower
	frequencies_endPower = tmp
elif frequencies_beginPower == frequencies_endPower:
	frequencies_beginPower = -1
	frequenceis_endPower = 5
if args.nfreq and args.nfreq > 0:
	frequencies_number = args.nfreq
filename_pattern_begin = 'PowerBox_Characterization_'
frequencies_list = np.logspace(frequencies_beginPower, frequencies_endPower, frequencies_number)

lock_in_time_constant = 10E-3
lock_in_sleeping_factor = 100  #80
if args.timeconstant:
	try:
		LockInNoise.get_index(LockInNoise.index2timeconstant, args.timeconstant)
		lock_in_time_constant = args.timeconstant
	except ValueError:
		pass

lock_in_gain = 5E-3
if args.gain:
	try:
		LockInNoise.get_index(LockInNoise.index2gain, args.gain)
		lock_in_gain = args.gain
	except ValueError:
		pass

sleep_time_frequency_step = 1.0  # seconds

""" ARGPARSE """
if args.stepsleep and args.stepsleep >= 0:
	sleep_time_frequency_step = args.stepsleep

logger.info("nfreq = " + str(frequencies_number))
logger.info("beginPower = " + str(frequencies_beginPower))
logger.info("endPower = " + str(frequencies_endPower))


"""
	Initialize oscilloscope for battery measurement
"""
while True:
	try:
		print "\n", "initializing USB instrument..."
		sOsci = USBTMCObject(USBInstruments['HALLE']['vendorID'], USBInstruments['HALLE']['productID'], USBInstruments['HALLE']['serialNo'])
		print "\tInstrument: " + str(sOsci.cmd_and_return("*IDN?"))
		OsciUSB.setup_measurement_mean(sOsci, channels=[1, 2], statistics=False, statistics_samples=-1)
		print ""
		break
	except LIB.Exceptions.USBException as e:
		print e
		time.sleep(5.0)
		pass

"""
	Initialize FuncGen to feed lock in
"""
while args.external:
	try:
		print "\n", "initializing FUNC-GEN via socket..."
		sFuncGen = SocketObject(SocketInstruments['DS345_Fred']['IP'], SocketInstruments['DS345_Fred']['PORT'])
		print "\tInstrument: " + str(sFuncGen.cmd_and_return("*IDN?"))
		sFuncGen.cmd("OFFS 0.0")
		sFuncGen.cmd("FREQ " + str(frequencies_list[0]))
		sFuncGen.cmd("PHSE 0.0")
		sFuncGen.cmd("AMPL 5.0VP")
		print ""
		break
	except LIB.Exceptions.SocketException:
		time.sleep(5.0)
		pass

"""
	Initialize Lock-In for noise measurement
"""
while True:
	try:
		print "\n", "initializing LOCK-IN via socket..."
		sLockIn = SocketObject(SocketInstruments['SR830_Michi']['IP'], SocketInstruments['SR830_Michi']['PORT'])
		print "\tInstrument: " + str(sLockIn.cmd_and_return("*IDN?"))
		sLockIn.cmd_and_return("SENS?")
		#
		LockInNoiseObj = LockInNoise(sLockIn, external=True if args.external else False)  # NEW
		LockInNoiseObj.set_input('A')
		LockInNoiseObj.set_time_constant(lock_in_time_constant)
		LockInNoiseObj.set_gain(lock_in_gain)
		while LockInNoiseObj.get_filter() != '0':
			LockInNoiseObj.set_filter(0)  # 'Out'
			time.sleep(1)
		#
		print "\tSensitivity: " + str(LockInNoiseObj.get_gain()) + " V"
		print "\tTime constant: " + str(LockInNoiseObj.get_time_constant()) + " s"
		print "\tSample rate: " + str(sLockIn.cmd_and_return("SRAT?"))
		print "\tFilter: " + str(LockInNoiseObj.get_filter())
		print ""
		#
		break
	except LIB.Exceptions.SocketException:
		time.sleep(5)
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
	strftime = time.strftime("%Y-%m-%d_%H%M")
	starttime, offsettime, meas_time_start, meas_time_stop = time.time(), 0, 0, 0
	_count = 0

	"""
	CREATE A NEW FILE WITH INCREASING FILE COUNT
	"""
	i = 1
	while True:
		files = [True for f in os.listdir(data_directory) if re.match(r'' + filename_pattern_begin+("%0*d" % (4, i)) + '.*', f)]
		if len(files) == 0:
			break
		i += 1
	filename = filename_pattern_begin + ("%0*d" % (4, i)) + '.dat'

	handle = open(data_directory + filename, 'w')
	logger.info("File opened: '" + data_directory + filename + "'")

	"""
	WRITE OSCI-CHANNEL INFORMATION TO FILE
	"""
	try:
		handle.write("#Osci_CH1==" + OsciUSB.dict2string(OsciUSB.get_values_channel(sOsci, 1, OsciUSB.queriesChannelInfo)) + '\n')
		handle.write("#Osci_CH2==" + OsciUSB.dict2string(OsciUSB.get_values_channel(sOsci, 2, OsciUSB.queriesChannelInfo)) + '\n')
	except LIB.Exceptions.USBException:
		handle.close()
		os.remove(data_directory + filename)
		continue

	"""
	WRITE LOCK-IN INFORMATION TO FILE
	"""
	try:
		handle.write("#LOCK-IN==")
		handle.write("SENS:" + str(LockInNoiseObj.get_gain()) + "\t")
		handle.write("TC:" + str(LockInNoiseObj.get_time_constant()) + "\t")
		handle.write("ACCOUPLING:" + str(LockInNoiseObj.get_input_coupling_ac()) + "\t")
		handle.write("FILTER:" + str(LockInNoiseObj.get_filter()) + "\t")
		handle.write("\n")
	except LIB.Exceptions.SocketException:
		handle.close()
		os.remove(data_directory + filename)
		continue

	"""
	WRITE TIMESTAMP AND KEY LIST TO FILE
	"""
	handle.write("#TIMESTAMP==" + strftime + '\n')
	if args.verbose:
		handle.write("#Keys==TIME\tFREQUENCY\tPowerBox_Vp_MEAN\tPowerBox_Vp_STDDEV\tPowerBox_Vm_MEAN\tPowerBox_Vm_STDDEV\tNOISE\tNOISE_STDDEV\tXNOISE\tXNOISE_STDDEV\tYNOISE\tYNOISE_STDDEV\n")
	else:
		handle.write("#Keys==TIME\tFREQUENCY\tPowerBox_Vp_MEAN\tPowerBox_Vp_STDDEV\tPowerBox_Vm_MEAN\tPowerBox_Vm_STDDEV\tNOISE\tNOISE_STDDEV\n")

	"""
	DATA STORAGE IN RAM
	"""
	data = {
		'TIME': [], 'FREQUENCY': [],
		'Vp': [], 'Vm': [], 'Vp_STDDEV': [], 'Vm_STDDEV': [],
		'XNOISE': [], 'YNOISE': [], 'XNOISE_STDDEV': [], 'YNOISE_STDDEV': [],
		'NOISE': [], 'NOISE_STDDEV': []
	}

	number_of_points = 1000

	while _count < frequencies_number and not SIGTERM:
		freq = frequencies_list[_count]
		try:
			"""
			IF EXTERNAL, USE FUNCTION GENERATOR
			"""
			if args.external:
				# Set function generator to new values and wait...
				sFuncGen.cmd("FREQ {_f}".format(_f=freq))
				time.sleep(sleep_time_frequency_step + 2./freq)
			
			meas_time_start = time.time()
			data_LockIn = LockInNoiseObj.acquire(freq, npoints=number_of_points, sleep=lock_in_sleeping_factor*lock_in_time_constant)
			data_PowerBox = get_osci_mean_data(sOsci, samples=20)
			meas_time_stop = time.time()
			meas_time = int((meas_time_stop+meas_time_start)/2.-starttime)

			noise_tuple = LockInNoise.calculate_noise(data_LockIn['X'], data_LockIn['Y'])
			data_Noise = {'XNOISE': data_LockIn['X']['MEAN'], 'XNOISE_STDDEV': data_LockIn['X']['STD']/np.sqrt(number_of_points),
			              'YNOISE': data_LockIn['Y']['MEAN'], 'YNOISE_STDDEV': data_LockIn['Y']['STD']/np.sqrt(number_of_points),
			              'NOISE': noise_tuple[0], 'NOISE_STDDEV': noise_tuple[1]/np.sqrt(number_of_points)}

			data['TIME'].append(meas_time)
			data['FREQUENCY'].append(freq)
			for key in data_PowerBox.keys(): data[key].append(data_PowerBox[key])
			for key in data_Noise.keys(): data[key].append(data_Noise[key])

			handle.write("{_t}\t{_f}\t".format(_t=meas_time, _f=frequencies_list[_count]))
			handle.write("{_PowerVp}\t{_PowerVp_STDDEV}\t{_PowerVm}\t{_PowerVm_STDDEV}\t".format(_PowerVp=data_PowerBox['Vp'],
			                                                                                     _PowerVm=data_PowerBox['Vm'],
			                                                                                     _PowerVp_STDDEV=data_PowerBox['Vp_STDDEV'],
			                                                                                     _PowerVm_STDDEV=data_PowerBox['Vm_STDDEV']))
			handle.write("{_noise}\t{_noise_STDDEV}".format(_noise=data_Noise['NOISE'], _noise_STDDEV=data_Noise['NOISE_STDDEV']))
			if args.verbose:
				handle.write("\t{_xnoise}\t{_xnoise_STDDEV}\t{_ynoise}\t{_ynoise_STDDEV}".format(_xnoise=data_Noise['XNOISE'],
																								 _ynoise=data_Noise['YNOISE'],
																								 _xnoise_STDDEV=data_Noise['XNOISE_STDDEV'],
																								 _ynoise_STDDEV=data_Noise['YNOISE_STDDEV']))
			handle.write("\n")

			if _count % 10 == 0:  # or _count == 10:
				if args.service:
					logger.info("{0:6.2f}%\t{1:12.4f} Hz  |  battery status: {2:5.2f} / {3:5.2f} (V)  |  noise: {4:6.4f} +/- {5:6.4f} mV".format(
						100.*_count/frequencies_number, frequencies_list[_count],
						data_PowerBox['Vp'], data_PowerBox['Vm'],
						1E+3*data_Noise['NOISE'], 1E+3*data_Noise['NOISE_STDDEV']))
				else:
					print time.strftime("%Y-%m-%d @ %H:%M:%S (%Z): ") + "{0:6.2f}%\t{1:12.4f} Hz  |  battery status: {2:5.2f} / {3:5.2f} (V)  |  noise: {4:6.4f} +/- {5:6.4f} mV".format(
						100.*_count/frequencies_number, frequencies_list[_count],
						data_PowerBox['Vp'], data_PowerBox['Vm'],
						1E+3*data_Noise['NOISE'], 1E+3*data_Noise['NOISE_STDDEV'])
				handle.flush()
				os.fsync(handle.fileno())
		except (LIB.Exceptions.SocketException, LIB.Exceptions.USBException):
			logger.error("(socket.error, USBError): trying to reconnect to our devices if necessary...")
			if args.external and not sFuncGen.is_open():
				sFuncGen.connect()
			if not sLockIn.is_open():
				sLockIn.connect()
			if not sOsci.is_open():
				sOsci.connect()
			continue
		except KeyboardInterrupt:
			SIGTERM = True
			logger.warning("received KeyboardInterrupt at {_strftime}".format(_strftime=time.strftime("%Y-%m-%d @ %H:%M:%S")))
			break
		_count += 1
	# while _count < ... AND not SIGTERM

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
		LIB.ROOT_IO.ROOT_IO.write_data(data_directory + filename, "PowerBox_Characterize", data)
		print "created ROOT file from data ('" + data_directory + filename + ".root')"
#end while-not-SIGTERM
logger.info("#### END OF PROGRAM ####")
