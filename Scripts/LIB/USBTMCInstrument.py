__author__ = 'Christian Velten'

from LIB.Exceptions import USBException, USBIOException

import usbtmc
from usb.core import USBError

import time

def _instrument_(vendorID, productID, serialNo=None):
	return {'vendorID': vendorID, 'productID': productID, 'serialNo': serialNo}

USBInstruments = {
	'LABOR_STR': "USB::0x0699::0x0401::INSTR",
	'LABOR': _instrument_(vendorID=1689, productID=1025),   # Tektronix DPO4104
	'HALLE': _instrument_(vendorID=1689, productID=930)     # Tektronix MSO2XXX
}

queriesMeasuInfo = ["TYPE", "SOURCE", "COUNT"]
queriesMeasuMinimal = ["VALUE"]
queriesMeasuMinimalStat = ["VALUE", "MEAN", "STDDEV"]
queriesMeasuNormal = ["VALUE", "MEAN", "MINIMUM", "MAXIMUM", "STDDEV"]
queriesMeasuFull = ["TYPE", "SOURCE", "COUNT", "VALUE", "MEAN", "MINIMUM", "MAXIMUM", "STDDEV", "UNITS"]
queriesChannelInfo = ["BANDWIDTH", "INVERT", "LABEL", "OFFSET", "POSITION", "SCALE", "TERMINATION", "YUNITS"]


class USBTMCObject(object):
	vendorID, productID, serialNumber = None, None, None

	def __init__(self, vendorID=None, productID=None, serialNumber=None, cstr="", term_character="\n", buffer=4*1024, timeout=10):
		self.s = None
		self.timeout = timeout
		self.vendorID = vendorID
		self.productID = productID
		self.serialNumber = serialNumber
		self.cstr = cstr
		self.tc = term_character
		self.buffer = buffer
		if self.cstr != "":
			self.connect(cstr=self.cstr)
		elif not vendorID is None and not productID is None:
			self.connect(vendorID, productID, serialNumber)
		else:
			raise ValueError("Supply valid connection information")

	def connect(self, vendorID=None, productID=None, serialNumber=None, cstr=""):
		if (self.vendorID is None or self.productID is None) and cstr=="":
			raise ValueError("Provide instrument identifiers!")
		if vendorID is None: vendorID = self.vendorID
		if productID is None: productID = self.productID
		if not self.serialNumber is None and serialNumber is None: serialNumber = self.serialNumber
		tries = 0
		while tries < 10:
			try:
				if cstr != "":
					s = usbtmc.Instrument(cstr)
				else:
					s = usbtmc.Instrument(vendorID, productID, serialNumber)
				self.s = s
				time.sleep(2)
				self.cmd("*WAI")
				self.ask("*IDN?")
				return
			except USBError:
				tries += 1
		raise USBException("could not connect to instrument")

	def instrument(self):
		return self.s

	def cmd(self, cmd):
		try:
			self.s.write(cmd + "\n")
		except USBError as e:
			raise USBIOException(e)
		return

	def read(self):
		astr = ''
		while not ('\r' in astr or '\n' in astr):
			try:
				r = self.s.read()
			except USBError as e:
				raise USBIOException(e)
			if not r: break
			astr += r
		return astr.strip()

	def ask(self, cmd):
		return self.s.ask(cmd + "\n")
	def write(self, cmd):
		return self.s.write(cmd + "\n")

	def cmd_and_return(self, cmd, check_for_return=False):
		self.cmd(cmd)
		if not (check_for_return or cmd.find("?") != -1):
			return ""
		return self.read()

	def is_open(self):
		try:
			self.cmd_and_return("*IDN?")
		except:
			return False
		return True
