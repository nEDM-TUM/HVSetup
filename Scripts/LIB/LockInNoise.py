# -*- coding: utf-8 -*-

import numpy as np
import time


class LockInNoise(object):
	instrument = None
	external = False
	npoints = 1000
	dataX, dataY = [], []

	input_coupling_ac = True

	index2timeconstant = [10E-6, 30E-6, 100E-6, 300E-6, 1E-3, 3E-3, 10E-3, 30E-3, 100E-3, 300E-3,
	                      1., 3., 10., 30., 100., 300., 1E+3, 3E+3, 10E+3, 30E+3]
	index2gain = [2E-9, 5E-9, 10E-9, 20E-9, 50E-9, 100E-9, 200E-9, 500E-9, 1E-6, 2E-6, 5E-6, 10E-6, 20E-6,
				  50E-6, 100E-6, 200E-6, 500E-6, 1E-3, 2E-3, 5E-3, 10E-3, 20E-3, 50E-3, 100E-3, 200E-3, 500E-3, 1.0]
	
	def __init__(self, instrument, external=False):
		self.instrument = instrument
		self.external = external
		
		if not instrument or not instrument.is_open():
			raise ValueError("instrument not open!")

		"""
			REFERENCES
		"""
		# Set reference source to internal
		if not external:
			self.instrument.cmd("FMOD 1")
		else:
			self.instrument.cmd("FMOD 0")
		self.instrument.cmd("FREQ 1.0")
		# Set reference phase to zero
		self.instrument.cmd("PHAS 0")
		"""
			INPUT
		"""
		self.instrument.cmd("ICPL 0")  # coupling: AC
		"""
			GAIN and TIME CONSTANT
		"""
		# Set sensitivity to X
		#self.instrument.cmd("SENS ")
		# Set time constant to 1ms
		self.instrument.cmd("OFLT " + str(self.index2timeconstant.index(10E-3)))
		# Set reserve to low noise
		self.instrument.cmd("RMOD 2")
		# Set steep slope (i.e. 24dB/oct)
		self.instrument.cmd("OFSL 3")
		"""
			DISPLAY & OUTPUT
		"""
		self.instrument.cmd("DDEF 1,2")  # display CH1:XNOISE
		self.instrument.cmd("DDEF 2,2")  # display CH2:YNOISE
		self.instrument.cmd("FPOP 1,0")  # CH1 output: display
		self.instrument.cmd("FPOP 2,0")  # CH2 output: display
		"""
			DATA STORAGE COMMANDS
		"""
		# Set data sampling to 512Hz
		self.instrument.cmd("SRAT 13")
		# Set to LOOP-mode, ?:query, 0:shot, 1:loop
		self.instrument.cmd("SEND 1")

		return

	@staticmethod
	def get_data_from_string(data):
		if data.strip()[-1] == ',': data = data.strip()[:-1]
		d = np.array(data.split(','), dtype='float')
		return d

	@staticmethod
	def calculate_noise(dx, dy=None):
		if dy is None:
			dy = dx['Y']
			dx = dx['X']
		n = np.sqrt(dx['MEAN']**2 + dy['MEAN']**2)
		sn = 2./n * np.sqrt((dx['MEAN']*dx['STD'])**2 + (dy['MEAN']*dy['STD'])**2)
		return (n, sn)

	@staticmethod
	def get_index(list, value):
		try:
			return list.index(value)
		except ValueError:
			return len(list) - 1

	def set_input(self, inp):
		try: str = int(inp)
		except ValueError:
			if inp == 'A': str = 0
			elif inp == 'A-B': str = 1
			elif inp == 'I': str = 2
			elif inp == 'I100M': str = 3
		self.instrument.cmd("ISRC {0}".format(inp))
	def get_input(self):
		inp = self.instrument.cmd_and_return("ISRC?").strip()
		if inp == '0': return 'A'
		if inp == '1': return 'A-B'
		if inp == '2': return 'I'
		if inp == '3': return 'I100M'
		return False

	def set_time_constant(self, tc):
		self.instrument.cmd("OFLT {_tc}".format(_tc=LockInNoise.get_index(LockInNoise.index2timeconstant, tc)))
	def get_time_constant(self):
		tc = int(self.instrument.cmd_and_return("OFLT?"))
		return LockInNoise.index2timeconstant[tc]

	def set_gain(self, sens):
		self.instrument.cmd("SENS {_s}".format(_s=LockInNoise.get_index(LockInNoise.index2gain, sens)))
	def get_gain(self):
		sens = int(self.instrument.cmd_and_return("SENS?"))
		return LockInNoise.index2gain[sens]

	def set_frequency(self, f, sleep=0.0):
		self.instrument.cmd("FREQ {_f}".format(_f=f))
		time.sleep(sleep)

	def get_filter(self):
		return self.instrument.cmd_and_return("ILIN?")
	def set_filter(self, mode):
		try:
			mode = int(mode)
		except ValueError:
			if mode == 'Out': mode = 0
			elif mode == 'LineIn': mode = 1
			elif mode == '2xLineIn': mode = 2
			else: mode = 3
		self.instrument.cmd("ILIN {_mode}".format(_mode=mode))

	def set_input_coupling_ac(self, status=True):
		if status:
			self.instrument.cmd("ICPL 0")
			self.input_coupling_ac = True
		else:
			self.instrument.cmd("ICPL 1")
			self.input_coupling_ac = False
	def get_input_coupling_ac(self):
		status = int(self.instrument.cmd_and_return("ICPL?"))
		return True if status == 0 else False

	def acquire(self, frequency, npoints=None, sleep=None):
		if npoints is None:  # number of points from array
			npoints = self.npoints

		if sleep is None:  # sleep is the minimum time to get nice averaging results
			sleep = 10.0 * self.index2timeconstant[int(self.instrument.cmd_and_return("OFLT?"))]

		# if NOT external reference source
		if not self.external:
			# Set LockIn-ReferenceFreq:
			self.instrument.cmd("FREQ {_f}".format(_f=frequency))
			# Sleep for one period
			time.sleep(1./frequency)

		# Reset data buffer
		self.instrument.cmd("PAUS")
		self.instrument.cmd("REST")
		# Start DAQ
		self.instrument.cmd("STRT")
		# Sleep for useful data/calculation
		time.sleep(sleep)
		# Get offset for data-points (bad calculated noise points)
		n0 = int(self.instrument.cmd_and_return("SPTS?"))
		# Sleep for 1s until there are enough points in buffer, there have been queries with other than SPTS literals!
		while True:
			try:
				if int(self.instrument.cmd_and_return("SPTS?").strip()) >= n0 + npoints: break
				time.sleep(2.0)
			except ValueError: pass
		# Pause DAQ
		self.instrument.cmd("PAUS")
		# Read Data:
		blength = int(self.instrument.cmd_and_return("SPTS?").strip())
		xdata = self.instrument.cmd_and_return("TRCA? {_i},{_j},{_k}".format(_i=1, _j=blength-npoints, _k=npoints))
		ydata = self.instrument.cmd_and_return("TRCA? {_i},{_j},{_k}".format(_i=2, _j=blength-npoints, _k=npoints))

		# Extract np.arrays from string "value,value,value..."
		dx, dy = LockInNoise.get_data_from_string(xdata), LockInNoise.get_data_from_string(ydata)
		dx = {'FREQ': frequency, 'MEAN': np.mean(dx), 'STD': np.std(dx), 'DATA': dx}
		dy = {'FREQ': frequency, 'MEAN': np.mean(dy), 'STD': np.std(dy), 'DATA': dy}

		self.dataX.append(dx)
		self.dataY.append(dy)

		return {'X': dx, 'Y': dy}

