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

def death_cycle(setpoint, temp):
	return (setpoint - temp) / 0.014738


# SET-UP OF ARGUMENT PARSER
parser = argparse.ArgumentParser(description="")
parser.add_argument("-l", "--log", help="file to write log to")
parser.add_argument("-s", "--service", help="script run as service? disables all I/O from std(in|out).", action="store_true")
parser.add_argument("--PROP", type=float, default=20.0)
parser.add_argument("--INTG", type=float, default=2.5)
parser.add_argument("--DIFF", type=float, default=1E-6)
parser.add_argument("--FREQ", type=float, default=50.0)
parser.add_argument("--PIN", type=int, default=17)
parser.add_argument("-T", "--temp", type=float, default=30.0)
parser.add_argument("--sleep", type=float, default=0.0)
args = parser.parse_args()

# SET-UP OF LOGGER
LOG_LEVEL = logging.INFO
LOG_FILENAME = args.log if args.log else "./data/DAVLL_TempStabil.log"
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logHandler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=1000)
logFormatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
logHandler.setFormatter(logFormatter)
logger.addHandler(logHandler)
class MyLogger(object):
	def __init__(self, logger, level):
		self.logger = logger
		self.level = level
	def write(self, message):
		if message.rstrip() != "":
			self.logger.log(self.level, message.rstrip())
if args.service:
	sys.stdout = MyLogger(logger, logging.INFO)
	sys.stderr = MyLogger(logger, logging.ERROR)
logger.info("---------------------------------------------------------------------------------------------------------")

# SIGNAL HANDLER
signal.signal(signal.SIGTERM, signal_SIGTERM_handler)
signal.signal(signal.SIGINT, signal_SIGINT_handler)

sensors = [GPIOSensor(GPIOSensors['THERM_DAVLL_'+str(i)]) for i in range(1,4)]

modulator = PWM(PIN=args.PIN, FREQ=args.FREQ)
modulator.changeFrequency(args.FREQ) # 50Hz
pid = PID(P=args.PROP, I=args.INTG, D=args.DIFF, nsize=25)
pid.SetSetpoint(args.temp)
pid.SetStateP(True)
pid.SetStateI(True)
pid.SetStateD(False)

f = open('/home/pi/daq/data/DAVLL_HEAT.dat', 'w')

was_above = False
SIGTERM, SIGINT = False, False
while not (SIGTERM or SIGINT):
	try:
		temp = get_temp(sensors)
		pid.feed(temp)
		pid_out = float(pid.output)
		if pid_out > 100.0: pid_out = 100.0
		elif pid_out < 0.0: pid_out = 0.0

		if temp < args.temp:
			pid.SetStateI(True)
			pid.SetStateD(False)
			if was_above:
				was_above = False
				pid.ClearData()
		else:
			was_above = True
			pid.SetStateI(False)
			if temp - args.temp < 1.0:
				pid.SetStateD(True)
			else:
				pid.SetStateD(False)

		modulator.changeDutyCycle(pid_out)

		logstr = "TEMP = {0:2.2f} | PID = {1:3.2f}".format(temp, pid_out)
		logger.info(logstr)
		f.write('{0}\t{1}\n'.format(temp, pid_out))
		if not args.service:
			print(logstr)
	except KeyboardInterrupt: SIGINT = True
	time.sleep(args.sleep)

f.close()

modulator.stop()
modulator.cleanup()
