__author__ = 'Christian Velten'

import re
import serial
import sys
import time


SerialInstruments = {
	'SIM960': {
	    'address': '/dev/ttyUSB0',
	    'baudrate': 9600,
	    'parity': serial.PARITY_NONE,
	    'stopbits': serial.STOPBITS_ONE,
	    'bytesize': serial.EIGHTBITS,
	    'rtscts': True },
	'LDC501': {
		'address': '/dev/ttyUSB1',
		'baudrate': 38400,
		'parity': serial.PARITY_NONE,
		'stopbits': serial.STOPBITS_ONE,
		'bytesize': serial.EIGHTBITS,
		'rtscts': False }
}


class SerialObject(object):
	instrument = None

	def __init__(self, instrument, wait=0.):
		self.wait = wait
		self.instrument = instrument
		self.connect(instrument)

	def connect(self, instrument):
		if instrument is None and self.instrument is None:
			raise ValueError("Provide instrument!")
		if instrument is None: instrument = self.instrument

		self.s = serial.Serial(
			port=instrument['address'],
			baudrate=instrument['baudrate'],
			parity=instrument['parity'],
			stopbits=instrument['stopbits'],
			bytesize=instrument['bytesize'],
			rtscts=instrument['rtscts'])

		if not self.s.isOpen():
			self.s.open()

	def cmd(self, cmd):
		self.s.write(cmd + "\n")
		time.sleep(self.wait)
		#time.sleep(1./self.instrument['baudrate'])
		return

	def read(self):
		time.sleep(1)
		astr = b""
		while self.s.inWaiting() > 0:
			astr += self.s.read(1)
		return astr

	def cmd_and_return(self, cmd, check_for_return=False):
		self.cmd(cmd)
		if not (check_for_return or cmd.find("?") != -1):
			return ""
		return self.read()

	def ask(self, cmd, check_for_return=False):
		s = self.cmd_and_return(cmd, check_for_return)
		return s

	def is_open(self):
		try:
			return self.s.isOpen()
		except:
			return False

	def close(self):
		self.s.close()
