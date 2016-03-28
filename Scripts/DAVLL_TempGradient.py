#!/usr/bin/env python
__author__ = 'Christian Velten'

from LIB.GPIOSensor import GPIOSensor, GPIOSensors
import argparse
import numpy
import signal
import sys
import time
import RPi.GPIO as GPIO
	
# PULSE-WIDTH-MODULATION @ raspberryPI
class PWM():
	def __init__(self, PIN, FREQ=50.0):
		self.PIN = int(PIN)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.PIN, GPIO.OUT)
		self.pwm = GPIO.PWM(self.PIN, FREQ)
		self.pwm.start(0)
		self.starttime = time.time()
		logger.info("PWM pin has been set to: " + str(PIN))
	def changeDutyCycle(self,cycle):
		self.pwm.ChangeDutyCycle(cycle)
	def changeFrequency(self,frequency):
		self.pwm.ChangeFrequency(frequency)
	def stop(self):
		self.pwm.stop()
	def cleanup(self):
		GPIO.cleanup()
		

def signal_SIGTERM_handler(signal, frame):
	global SIGTERM
	SIGTERM = True
	sys.stderr.write("RECEIVED SIGTERM! Trying to terminate smooth and easy...")
def signal_SIGINT_handler(signal, frame):
	global SIGINT
	SIGINT = True
	sys.stderr.write("RECEIVED SIGINT! Waiting for methods to finish before interrupting...")

def get_temp(sensors):
	temp = 0.0
	for sensor in sensors:
		temp += float(sensor.read())
	return temp / float(len(sensors))


# SET-UP OF ARGUMENT PARSER
parser = argparse.ArgumentParser(description="measurs and calculates the temperature gradient inside the DAVLL box")
parser.add_argument("-l", "--log")
parser.add_argument("-s", "--service", action="store_true")
parser.add_argument("--FREQ", type=float, default=50.0)
parser.add_argument("--PIN", type=int, default=17)
parser.add_argument("-T", "--temp", type=float, default=30.0)
parser.add_argument("--csleep", type=float, default=0.5)
parser.add_argument("--hsleep", type=float, default=5.0)
args = parser.parse_args()

# SIGNAL HANDLER
signal.signal(signal.SIGTERM, signal_SIGTERM_handler)
signal.signal(signal.SIGINT, signal_SIGINT_handler)

sensors = [GPIOSensor(GPIOSensors['THERM_DAVLL_'+str(i)]) for i in range(1,4)]
outer_sensor = GPIOSensor(GPIOSensors['THERM_LAB'])

modulator = PWM(PIN=args.PIN, FREQ=args.FREQ)
modulator.changeFrequency(args.FREQ) # 50Hz

data = {'HEATING': [], 'COOLING': []}

timestart = 0
heating = False
SIGTERM, SIGINT = False, False
while not (SIGTERM or SIGINT):
	try:
		temp = get_temp(sensors)
		outer_temp = get_temp(outer_sensor)
	except: KeyboardInterrupt: SIGINT = True

	if not heating and temp <= outer_temp + 1.0:
		if not len(data['HEATING']) == 0:
			print("Gradient:\n", numpy.gradient(data['COOLING'][i]['OUTER'], data['COOLING'][i]['TIME']))

		try: modulator.changeDutyCycle(100)
		except KeyboardInterrupt: SIGINT = True
		heating = True
		data['HEATING'].append({'INI_OUTER':outer_temp, 'INI_INNER':temp, 'END_OUTER':0, 'END_INNER':0, 'DURATION':-time.time()})
		data['COOLING'].append({'TIME': [], 'OUTER': [], 'INNER': []})
		time.sleep(args.hsleep)
	elif heating and temp >= args.temp:
		try: modulator.changeDutyCycle(0)
		except KeyboardInterrupt: SIGINT = True
		heating, timestart = False, time.time()
		data['HEATING'][-1]['END_OUTER'], data['HEATING'][-1]['END_INNER'] = outer_temp, inner_temp
		data['HEATING'][-1]['DURATION'] += timestart
	else:
		if len(data['COOLING'][-1]['TIME']) == 0:
			data['COOLING'][-1]['TIME'].append(time.time()-timestart)
		else:
			data['COOLING'][-1]['TIME'].append(time.time()-data['COOLING'][-1]['TIME'][-1])
		data['COOLING'][-1]['OUTER'].append(outer_temp)
		data['COOLING'][-1]['INNER'].append(temp)
		time.sleep(args.csleep)

	except KeyboardInterrupt: SIGINT = True

hkeys, ckeys = data['HEATING'][0].keys(), data['COOLING'][0].keys()
handle = open("DAVLL_TempGradient.out", 'w')
for i in range(len(data['HEATING'])):
	handle.write('###NEW###\n')
	handle.write('>HEATING\n')
	for hkey in hkeys: handle.write('{0}={1}\n'.format(hkey, data['HEATING'][i][hkey]))
	handle.write('>COOLING\n')
	for ckey in ckeys: 
		astr = ''
		for item in data['COOLING'][i][hkey]: astr += str(item)+','
		handle.write('{0}={1}\n'.format(ckey, astr[:-1]))
	handle.write('>GRADIENT\n')
	for t in data['COOLING'][i]['TIME']:
		handle.write('{0},'.format(t))
	for grad in numpy.gradient(data['COOLING'][i]['INNER'], data['COOLING'][i]['TIME']):
		handle.write('{0},'.format(grad))
	handle.write('\n')
handle.close()

modulator.stop()
modulator.cleanup()
