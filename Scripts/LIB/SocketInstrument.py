from LIB.Exceptions import SocketConnectionException, SocketTalkError
import socket

SocketInstruments = {
	'DS345_Fred': {'IP': "csserial.1.nedm1", 'PORT': 101},
	'DS345_WeirdAl': {'IP': "csserial.1.nedm1", 'PORT': 102},
	'SR830_Michi': {'IP': "csserial.1.nedm1", 'PORT': 103},
	'LDC501_LAB': {'IP': "10.155.59.42", 'PORT': 8888} 
}


class SocketObject(object):
	Address, Port = None, None

	def __init__(self, address, port, buffer=4*1024, timeout=10, blocking=0, no_query=False):
		self.s = None
		self.timeout = timeout
		self.Address = address
		self.Port = port
		self.buffer = buffer
		self.blocking = blocking
		self.connect(address, port, no_query)

	def connect(self, address=None, port=None, no_query=False, blocking=None):
		if (self.Address is None and address is None) or (self.Port is None and port is None):
			raise ValueError("Provide instrument identifiers!")
		if address is None: address = self.Address
		if port is None: port = self.Port
		if not blocking is None:
			self.blocking = blocking

		self.s = socket.socket()
		try:
			self.s.connect((str(address), port))
			if self.s.gettimeout() is None or self.s.gettimeout() < self.timeout:
				self.s.settimeout(self.timeout)
			if self.blocking != 0:
				self.s.setblocking(1)
				self.s.settimeout(None)
		except socket.error, e:
			print "\n!!! ERROR !!!\nConnection to the instrument failed! [socket.error | #" + str(e.errno) + "]"
			print "Are you connected to the LAN/VPN and/or is the device running?"
			raise SocketConnectionException("Connection to the instrument at {addr}:{pt} failed!".format(addr=address, pt=port))
		if not no_query:
			self.cmd_and_return("*IDN?")
		return

	def cmd(self, cmd):
		try:
			self.s.send(cmd + "\r\n")
		except socket.error, e:
			raise SocketTalkError(e)
		return

	def read(self):
		astr = ""
		while not ('\r' in astr or '\n' in astr):
			try:
				r = self.s.recv(self.buffer)
			except socket.error, e:
				raise SocketTalkError(e)
			if not r: break
			astr += r
		return astr.strip()

	def cmd_and_return(self, cmd, check_for_return=False):
		self.cmd(cmd)
		if not (check_for_return or cmd.find("?") != -1):
			return ""
		return self.read()

	def close(self):
		self.s.close()

	def is_open(self):
		try:
			self.cmd_and_return("*IDN?")
		except:
			return False
		return True
