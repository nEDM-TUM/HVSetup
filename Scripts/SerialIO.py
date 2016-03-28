#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Christian Velten'

from LIB.SerialInstrument import SerialObject, SerialInstruments

import serial
import sys
import time

instrument = [{
    'address': '/dev/ttyUSB0',
    'baudrate': 9600,
    'parity': serial.PARITY_NONE,
    'stopbits': serial.STOPBITS_TWO,
    'bytesize': serial.EIGHTBITS,
    'rtscts': False
	}]

# connect to device
ser = SerialObject(instrument[0])

ser.cmd("AMPL 4VP")
print ser.ask("*IDN?")

time.sleep(1)
