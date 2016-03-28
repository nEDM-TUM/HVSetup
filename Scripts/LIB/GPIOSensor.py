__author__ = 'Christian Velten'

import re
import time

GPIOSensors = {
	'THERM_LAB': '/sys/bus/w1/devices/10-000802e0eb8d/w1_slave',
	'THERM_DAVLL_1': '/sys/bus/w1/devices/28-00000677dffa/w1_slave',
	'THERM_DAVLL_2': '/sys/bus/w1/devices/28-00000695373a/w1_slave',
	'THERM_DAVLL_3': '/sys/bus/w1/devices/28-000006955314/w1_slave'
} 

class GPIOSensor():
	def __init__(self, path):
		self.path = path
		print('\t' + self.path)

	def read_sensor(self):
		m = None
		value = "U"
		try:
			f = open(self.path, "r")
			line = f.readline()
			if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
				line = f.readline()
				m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
			if not (m is None and m):
				value = str(float(m.group(2)) / 1000.0)
			f.close()
		except IOError as e:
			print(time.strftime("%x %X"), "Error reading", self.path, ": ", e)
			return None
		return value

	def read(self):
		return self.read_sensor()