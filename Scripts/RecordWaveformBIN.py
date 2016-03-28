#!/usr/bin/env python
__author__ = 'Christian Velten'

import LIB.File
from LIB.USBTMCInstrument import USBTMCObject, USBInstruments

from datetime import datetime
import argparse
import gzip
import logging, logging.handlers, signal
import numpy as np
import os, re, sys, time

precision = '4'

# argparse
parser = argparse.ArgumentParser(description='Measure data using the oscilloscope and transfer it into a binary file.')
parser.add_argument('-l', '--log', help="file to write log to")
parser.add_argument("-s", "--service", help="script run as service? disables all I/O from std(in|out).", action="store_true")
parser.add_argument("-v", "--verbose", help="set if you want to save more data to file / output", action="store_true")
parser.add_argument("-c", "--compress", action="store_true")
parser.add_argument('--precision', type=int, default=4)
parser.add_argument('--start', type=int, default=0)
parser.add_argument('-n', '--ndata', type=int, default=10000)
parser.add_argument('--xunit', default='S', choices=['S'])
parser.add_argument('--scale', type=float, default=1E+0, choices=[1E-3, 2E-3, 4E-3, 10E-3, 20E-3, 40E-3, 100E-3, 200E-3, 400E-3, 1E+0, 2E+0, 4E+0, 10E+0])
args = parser.parse_args()
#
LOG_FILENAME = "/tmp/RecordWaveformBIN.log" if args.log is None else args.log
print LOG_FILENAME
LOG_LEVEL = logging.INFO
#
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
#
SIGTERM = False
SIGINT = False

def signal_SIGTERM_handler(signal, frame):
	global SIGTERM
	SIGTERM = True
	sys.stderr.write("RECEIVED SIGTERM! Trying to terminate smooth and easy...")
def signal_SIGINT_handler(signal, frame):
	global SIGINT
	SIGINT = True
	sys.stderr.write("RECEIVED SIGINT! Trying to terminate smooth and easy...")
#
signal.signal(signal.SIGTERM, signal_SIGTERM_handler)
signal.signal(signal.SIGINT, signal_SIGINT_handler)
#
if args.service:
	odir = LIB.File.set_directory('/var/LABOR/RecordWaveformBIN/', ask=False)
else:
	odir = LIB.File.set_directory('./data/', ask=True)
fileprefix = 'RecWvfm_'

ndata = args.ndata if 10000000 >= args.ndata >= 1000 else 10000
if 10000000 > args.start >= 0:
	wvfm_start = args.start
else:
	wvfm_start = 0
if 10000000 >= args.start + args.ndata > wvfm_start:
	wvfm_stop = args.start + args.ndata
else:
	wvfm_stop = args.start + 1000

# connect to oscilloscope
sOsci = USBTMCObject(USBInstruments['LABOR']['vendorID'], USBInstruments['LABOR']['productID'])
print ("\tInstrument: " + str(sOsci.ask("*IDN?")))

#sOsci.cmd('PRE:XUNIT "{0}"'.format(args.xunit))
sOsci.cmd('HORIZONTAL:SCALE {0}'.format(args.scale))
sOsci.cmd('HORIZONTAL:RECORDLENGTH {0}'.format(ndata))

sOsci.cmd("HEADER 1")

print sOsci.ask('HORIZONTAL:SCALE?')
print sOsci.ask('HORIZONTAL:RECORDLENGTH?')

header = sOsci.ask("WFMOUTPRE?")
npoints = sOsci.ask("WFMOUTPRE:NR_PT?")
xzero = float(sOsci.ask("WFMOUTPRE:XZERO?").strip().split(' ')[-1].replace('"',''))
xincr = float(sOsci.ask("WFMOUTPRE:XINCR?").strip().split(' ')[-1].replace('"', ''))
xunit = sOsci.ask("WFMOUTPRE:XUNIT?").strip().split(' ')[-1].replace('"', '')
yzero = float(sOsci.ask("WFMOUTPRE:YZERO?").strip().split(' ')[-1].replace('"', ''))
yoffs = float(sOsci.ask("WFMOUTPRE:YOFF?").strip().split(' ')[-1].replace('"', ''))
ymult = float(sOsci.ask("WFMOUTPRE:YMULT?").strip().split(' ')[-1].replace('"', ''))
yunit = sOsci.ask("WFMOUTPRE:YUNIT?").strip().split(' ')[-1].replace('"', '')
bytnr = sOsci.ask("WFMOUTPRE:BYT_NR?")
sOsci.cmd("HEADER 0")
sOsci.cmd("VERBOSE 0")
sOsci.cmd("*WAI")

# set up for single acquisition
print "\nSTOPA", sOsci.ask("ACQ:STOPA?")
if sOsci.ask("ACQ:STOPA?") != 'SEQ':
	sOsci.cmd("ACQ:STOPAfter SEQ")
	sOsci.cmd("ACQ:STATE RUN")
time.sleep(10*args.scale + 1)
print "STOPA", sOsci.ask("ACQ:STOPA?")

# set up for waveform transfer
sOsci.cmd("DATA:SOURCE CH1")
sOsci.cmd("DATA:START {0}".format(wvfm_start))
sOsci.cmd("DATA:STOP {0}".format(wvfm_stop))
sOsci.cmd("DATA:ENCDG SRI")
sOsci.cmd("DATA:WIDTH 2")
sOsci.cmd("*WAI")

time.sleep(1)

# While True
today, lastday = None, datetime.today()
counter = 0

data = np.empty(wvfm_stop-wvfm_start, dtype=np.dtype('i2'))
d_volt, d_time = np.empty(wvfm_stop-wvfm_start, dtype=np.dtype('f'+precision)), np.empty(wvfm_stop-wvfm_start, dtype=np.dtype('f'+precision))
N = 0

while not SIGINT and not SIGTERM:
	try:
		today = datetime.today()
		if (today.date() > lastday.date()):
			lastday = today
			counter = 0
		else: counter += 1
		ofile = odir + '/' + fileprefix + today.strftime('%Y-%m-%d_') + "{:0>4}".format(counter) + ".bin"

		while int(sOsci.ask("ACQ:STATE?")) != 0:
			time.sleep(0.1)
		sOsci.instrument().write('CURVE?\n')
		buf = sOsci.instrument().read_raw()
		# start new acquisition
		sOsci.cmd("ACQ:STATE ON")

		""" buf[] = 
		0 = #
		1 = N
		2..2+N-1 = n-data-bytes
		2+N..len(buf)-1 = data
		"""
		N = int(buf[1])
		data = np.frombuffer(buf[2+N:-1], np.dtype('i2'))
		
		np.copyto(d_volt, data, casting='unsafe')
		d_volt -= yoffs
		d_volt *= ymult
		d_volt += yzero

		with open(ofile, 'wb') as handle:
			#handle.write(today.strftime('%Y-%m-%d_%H:%M:%S').encode())
			np.array([today.strftime('%Y,%m,%d,%H,%M,%S').split(',')], dtype=np.dtype('i4')).tofile(handle)
			np.array([precision], dtype=np.dtype('u1')).tofile(handle)
			np.array([len(d_volt)], dtype=np.dtype('u4')).tofile(handle)
			np.array([xzero, xincr, yzero, yoffs, ymult], dtype=np.dtype('f'+precision)).tofile(handle)
			handle.write((xunit+yunit).encode())
			d_volt.tofile(handle)
			print ofile
		if args.compress:
			with open(ofile, 'rb') as handle:
				f_out = gzip.open(ofile.replace('.bin','.bin.gz'), 'wb')
				f_out.writelines(handle)
				f_out.close()
				print ofile.replace('.bin','.bin.gz')
				os.remove(ofile)

	except KeyboardInterrupt:
		SIGINT = True
		continue
