__author__ = 'Christian Velten'

from LIB.STD import get_largest_array_length
import gzip
import os
import numpy
import time

"""
### --------------------------------------------------------------------------------------------------------------------
"""


def get_measurement_amplitude(scope, channel=["CH2", "CH3"]):
	amps = []
	for ch in channel:
		scope.cmd_and_return("MEASUrement:IMMed:SOUrce " + ch)
		scope.cmd_and_return("MEASUrement:IMMed:TYPe AMPlitude")
		amp, unit = 0.0, ""
		while not _acquired_amp:
			try:
				amp = float(scope.cmd_and_return("MEASU:IMM:VAL?"))
				unit = scope.cmd_and_return("MEASU:IMM:UNI?").replace('"', '').strip()
				if amp > 1E+37 or amp < -1E+37:
					raise ValueError
				break
			except (ValueError, socket.error) as e:
				print e
				time.sleep(1.0)
		amps.append([amp, unit])
	return amps


def get_measurement_phase(scope, channel_pairs=[["CH2", "CH3"]]):
	phse = []
	for pair in channel_pairs:
		scope.cmd_and_return("MEASUrement:MEAS1:TYPe PHAse")
		scope.cmd_and_return("MEASUrement:MEAS1:SOUrce1 " + pair[0])
		scope.cmd_and_return("MEASUrement:MEAS1:SOUrce2 " + pair[1])
		scope.cmd_and_return("MEASU:MEAS1:STATE ON")
		phase, unit = 0.0, ""
		_acquired_phase = False
		while not _acquired_phase:
			try:
				phase = float(scope.cmd_and_return("MEASUrement:MEAS1:VAL?"))
				unit = scope.cmd_and_return("MEASUrement:MEAS1:UNI?")
				if phase > 1E+37 or phase < -1E+37:
					raise ValueError
			except (ValueError, socket.error) as e:
				print e
				time.sleep(1.0)
				continue
			_acquired_phase = True
		phse.append([phase, unit])

	return phse


def get_measurement_mean(scope, channel=["CH1", "CH2", "CH3"]):
	mean = []
	for ch in channel:
		m, unit = 0.0, ""
		while not _acquired_mean:
			try:
				scope.cmd_and_return("MEASUrement:IMMed:SOUrce " + ch)
				scope.cmd_and_return("MEASUrement:IMMed:TYPe MEAN")
				m = float(scope.cmd_and_return("MEASU:IMM:VAL?"))
				if m < -1E+37 or m > 1E+37:
					raise ValueError
				unit = scope.cmd_and_return("MEASU:IMM:UNI?").replace('"', '').strip()
				break
			except (ValueError, socket.error) as e:
				print e
				time.sleep(1.0)
		mean.append([m, unit])
	return mean


def get_channel_data(scope, channel):
	"""
	Retrieve data from the oscilloscopes channel specified as e.g. 'CH1'.
	:param scope:
	:param channel:
	:return:
	"""
	scope.cmd_and_return("DATA:SOU " + channel)
	scope.cmd_and_return("DATA:WIDTH 1")
	scope.cmd_and_return("DATA:ENC RPB")

	# ---- BEGIN: HANDLE MORE THAN 10k POINTS
	#recordLength = 10000000
	recordLength = 100000
	scope.cmd_and_return("HORizontal:RECordlength " + str(recordLength))
	scope.cmd_and_return("DATA:START 1")
	scope.cmd_and_return("DATA:STOP " + str(recordLength))
	# ------ END: HANDLE MORE THAN 10k POINTS

	ymult = float(scope.cmd_and_return('WFMPRE:YMULT?'))
	yzero = float(scope.cmd_and_return('WFMPRE:YZERO?'))
	yoff = float(scope.cmd_and_return('WFMPRE:YOFF?'))
	xincr = float(scope.cmd_and_return('WFMPRE:XINCR?'))

	data = scope.cmd_and_return('CURVE?')

	headerlength = 2 + int(data[1])
	ADC_header = data[:headerlength]
	ADC_Raw = data[headerlength:-1]
	ADC_Raw = numpy.array(unpack("%sB" % len(ADC_Raw), ADC_Raw))

	ADC_Volts = (ADC_Raw - yoff) * ymult + yzero
	ADC_Time = numpy.arange(0, xincr * len(ADC_Volts), xincr)

	return ADC_Time, ADC_Volts


def write_triple_channel_to_file(filename, ch1_time, ch1_volts, ch2_time, ch2_volts, ch3_time, ch3_volts, header="", verbose=True):
	"""
	Write data to a file via gzip.
	"""
	lines_tsv = [header]
	length = get_largest_array_length([ch1_time, ch1_volts, ch2_time, ch2_volts, ch3_time, ch3_volts])
	for i in range(length):
		string = str(ch1_time[i]) + "\t" + str(ch1_volts[i]) + "\t" + \
				 str(ch2_time[i]) + "\t" + str(ch2_volts[i]) + "\t" + \
				 str(ch3_time[i]) + "\t" + str(ch3_volts[i]) + "\n"
		lines_tsv.append(string)
	handle = gzip.open(os.path.abspath(filename), 'wb')
	handle.writelines(lines_tsv)
	handle.close()
	print "- - Wrote channel data to '" + filename + "'."


def organize_files(filelist, destination):
	# open destination for writing
	for f in filelist:
		print ""
		#unpack all files
		#write all unpacked files to destination stream
	# close destination
	print "Unpacked", len(filelist), "gzipped files and moved them to '" + destination + "'."
