#!/usr/bin/env python
__author__ = 'Christian Velten'

from LIB.SerialInstrument import SerialObject, SerialInstruments
from LIB.STD import ms
import sys
import time


def exit(ser=None, code=0):
	if not ser is None:
		ser.cmd("LDON OFF")
		time.sleep(1)
	sys.exit(code)

# LDC501_SCAN_LIMITS
min_I, max_I = 100., 230.					# float [mA]
min_steps, max_steps = 10, 1000000			# int
min_dwelltime, max_dwelltime = 6*ms, 1.0	# float [s]

# connect to device
ser = SerialObject(SerialInstruments['LDC501'])
try:
	print "Instrument: " + ser.cmd_and_return("*IDN?")

	ser.cmd("TOKN ON")
	ser.cmd("LDON OFF")
	ser.cmd("MODU OFF;RNGE LOW;SMOD CC")
	ser.cmd("SYND 5")
	time.sleep(1)

	print "LD_I_LM: {0}".format(ser.cmd_and_return("SILM?"))
	print "LD_V_LM: {0}".format(ser.cmd_and_return("SVLM?"))

	cin = raw_input("I_lower [120]: ")
	try: cin = float(cin) 
	except ValueError: cin = 120
	scan_lower = cin if min_I <= cin <= max_I else 120
	cin = raw_input("I_upper [160]: ")
	try: cin = float(cin) 
	except ValueError: cin = 160
	scan_upper = cin if min_I <= cin <= max_I else 160

	cin = raw_input("step number [100]: ")
	try: cin = float(cin)
	except ValueError: cin = 100
	scan_number = cin if min_steps <= cin <= max_steps else 1000

	max_frequency, min_frequency = 1./(min_dwelltime*scan_number), 1./(max_dwelltime*scan_number)
	cin = raw_input("frequency ({0:2.3f},{1:2.3f}) [(max-min)/2]: ".format(min_frequency, max_frequency))
	try: cin = float(cin)
	except ValueError: cin = 0.5*(max_frequency-min_frequency)
	scan_frequency = cin if min_frequency <= cin <= max_frequency else 0.5*(max_frequency-min_frequency)

	scan_increment = (scan_upper - scan_lower) / float(scan_number)
	scan_dwelltime = (1. / (scan_frequency * scan_number)) / ms

	cin = raw_input("LD_ON @ {0}mA? [yN] ".format(scan_lower))
	if cin == "" or cin.lower() != "y": exit(ser, 0)
	ser.cmd("SILD {0}".format(scan_lower))
	ser.cmd("LDON ON")
	time.sleep(5)

	cin = raw_input("SCAN with {n} steps and {T}s period w/ {TD}ms dwelltime:\n{Ilow}mA -> {Iup}mA\nOK? [yN] ".format(n=scan_number, T=1./scan_frequency, Ilow=scan_lower, Iup=scan_upper, TD=scan_dwelltime))
	if cin == "" or cin.lower() != "y": exit(ser, 0)

	while True:
		ser.cmd("SILD {0}".format(scan_lower))
		ser.cmd("SCAN {0},{1},{2}".format(scan_increment, scan_number, scan_dwelltime))
		time.sleep(scan_number * scan_dwelltime*ms)

except KeyboardInterrupt:
	exit(ser, 1)
