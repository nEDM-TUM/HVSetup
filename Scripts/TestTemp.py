#!/usr/bin/env python
__author__ = 'Christian Velten'

from LIB.GPIOSensor import GPIOSensor, GPIOSensors
from LIB.PID import PID
import argparse
import logging
import logging.handlers
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
		print("PWM pin has been set to: " + str(PIN))
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
parser = argparse.ArgumentParser(description="")
parser.add_argument("-l", "--log", help="file to write log to")
parser.add_argument("-s", "--service", help="script run as service? disables all I/O from std(in|out).", action="store_true")
parser.add_argument("--PROP", type=float, default=10.0)
parser.add_argument("--INTG", type=float, default=1.0)
parser.add_argument("--FREQ", type=float, default=50.0)
parser.add_argument("--PIN", type=int, default=17)
parser.add_argument("-T", "--temp", type=float, default=30.0)
parser.add_argument("--sleep", type=float, default=0.5)
args = parser.parse_args()

# SIGNAL HANDLER
signal.signal(signal.SIGTERM, signal_SIGTERM_handler)
signal.signal(signal.SIGINT, signal_SIGINT_handler)

sensors = [GPIOSensor(GPIOSensors['THERM_DAVLL_'+str(i)]) for i in range(1,4)]

modulator = PWM(PIN=args.PIN, FREQ=args.FREQ)
modulator.changeFrequency(args.FREQ) # 50Hz
pid = PID(P=args.PROP, I=args.INTG) # 10(%/K), 1(1/s*K)
pid.SetSetpoint(args.temp)
pid.SetStateP(True)
pid.SetStateI(False)
pid.SetStateD(False)

handle = open("TempTest.dat", "w")
handle.write("time\tcycle\ttemp\n")

modulator.changeDutyCycle(100)
time.sleep(60)

heattime, safetime = 60, 5
cycle, temp, stoptemp =	25, 0, 0
timestart = time.time()
SIGTERM, SIGINT = False, False
while not (SIGTERM or SIGINT):
	try:
		currenttime = time.time() - timestart
		if cycle == 0 and temp <= stoptemp and currenttime > heattime+safetime:
			break
		if currenttime >= heattime and cycle != 0:
			cycle = 0
			stoptemp = temp
		temp = get_temp(sensors)

		modulator.changeDutyCycle(cycle)

		handle.write('{0}\t{1:2.3f}\t{2}\n'.format(currenttime, temp, cycle))
	except KeyboardInterrupt: SIGINT = True

handle.close()
modulator.stop()
modulator.cleanup()