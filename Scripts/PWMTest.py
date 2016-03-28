#!/usr/bin/env python
__author__ = 'Christian Velten'

import RPi.GPIO as GPIO

pin = 17
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
pwm = GPIO.PWM(pin, 50)
pwm.start(1)

cin = raw_input("")

pwm.stop()
GPIO.cleanup()