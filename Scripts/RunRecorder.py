#!/usr/bin/env python
__author__ = 'Christian Velten'

try: from LIB.USBTMCInstrument import USBTMCObject, USBInstruments
except ImportError: FORCE_DRAW = True

from datetime import datetime
import gzip
import numpy as np
import os, re, sys, time


# argparse
if len(sys.argv) < 2: odir = './'
else: odir = str(sys.argv[1]).strip()
fileprefix = 'RecWvfm_'

wvfm_start, wvfm_stop = 0, 1000000

# connect to oscilloscope
sOsci = USBTMCObject(USBInstruments['LABOR']['vendorID'], USBInstruments['LABOR']['productID'])
print ("\tInstrument: " + str(sOsci.ask("*IDN?")))

# set up for single acquisition
print sOsci.ask("ACQ:MAXS?")
sOsci.cmd("ACQ:MODE HIRes")
sOsci.cmd("ACQ:STOPAfter SEQ")
sOsci.cmd("ACQ:STATE RUN")

# set up for waveform transfer
sOsci.cmd("DATA:SOURCE CH1")
sOsci.cmd("DATA:START {0}".format(wvfm_start))
sOsci.cmd("DATA:STOP {0}".format(wvfm_stop))
sOsci.cmd("DATA:ENCDG SRI")
sOsci.cmd("DATA:WIDTH 2")
sOsci.cmd("HEADER 1")
sOsci.cmd("VERBOSE 0")
sOsci.cmd("*WAI")

time.sleep(0.5)

header = sOsci.ask("WFMOUTPRE?")
npoints = sOsci.ask("WFMOUTPRE:NR_PT?")
xzero = float(sOsci.ask("WFMOUTPRE:XZERO?").strip().split(' ')[-1].replace('"',''))
xincr = float(sOsci.ask("WFMOUTPRE:XINCR?").strip().split(' ')[-1].replace('"', ''))
xunit = sOsci.ask("WFMOUTPRE:XUNIT?").replace('"', '')
yzero = float(sOsci.ask("WFMOUTPRE:YZERO?").strip().split(' ')[-1].replace('"', ''))
yoffs = float(sOsci.ask("WFMOUTPRE:YOFF?").strip().split(' ')[-1].replace('"', ''))
ymult = float(sOsci.ask("WFMOUTPRE:YMULT?").strip().split(' ')[-1].replace('"', ''))
yunit = sOsci.ask("WFMOUTPRE:YUNIT?")
bytnr = sOsci.ask("WFMOUTPRE:BYT_NR?")

sOsci.cmd("HEADER 0")
sOsci.cmd("VERBOSE 0")
sOsci.cmd("*WAI")

time.sleep(1)

# While True
SIGINT = False
today, lastday = None, datetime.today()
counter = 0

data = np.empty(wvfm_stop-wvfm_start, dtype=np.dtype('i2'))
d_volt, d_time = np.empty(wvfm_stop-wvfm_start, dtype=np.dtype('f8')), np.empty(wvfm_stop-wvfm_start, dtype=np.dtype('f8'))
N = 0

while not SIGINT:
	try:
		today = datetime.today()
		if (today.date() > lastday.date()):
			lastday = today
			counter = 0
		else: counter += 1
		ofile = fileprefix + "{:0>4}".format(counter) + ".bin"

		while int(sOsci.ask("ACQ:STATE?")) != 0:
			time.sleep(0.1)
			#print "slept"
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
		
		#d_time = np.arange(0, xincr * len(d_volt), xincr, dtype=np.dtype('f8'))

		with open(ofile, 'wb') as handle:
			np.array([len(d_volt)], dtype=np.dtype('u4')).tofile(handle)
			np.array([xzero, xincr, yzero, yoffs, ymult], dtype=np.dtype('f8')).tofile(handle)
			handle.write((xunit+yunit).encode())
			d_volt.tofile(handle)
			print "created", ofile
	except KeyboardInterrupt:
		SIGINT = True
		continue