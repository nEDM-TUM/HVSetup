#!/usr/bin/env python
__author__ = 'Christian Velten'

from LIB.ROOT_IO import ROOT_IO

import argparse
import gzip
import numpy as np
import os
import sys

parser = argparse.ArgumentParser(description="Python script to convert waveform data to a ROOT file.")
parser.add_argument("file", help="filename to convert")
args = parser.parse_args()

if args.file and os.path.isfile(args.file):
	filename = os.path.abspath(str(args.file).strip())
else:
	print "Need valid filename to proceed!"
	sys.exit(1)

if filename[-2:] == 'gz':
	handle = gzip.open(filename, 'rb')
else:
	handle = open(filename, 'r')
lines = handle.readlines()
handle.close()

cols = [[], []]

for line in lines:
	if len(line.strip()) == 0 or line.strip()[0] == '#': continue
	tmp_line = line.strip().split('\t')
	for j in range(len(cols)):
		cols[j].append(float(tmp_line[j]))

cols[0] = np.array(cols[0])
cols[1] = np.array(cols[1])

xincr = 10E-6
cols[0] = np.arange(0, xincr*len(cols[1]), xincr)
ymult = 156.25E-6 / 156.
cols[1] = cols[1] * ymult

data = {
	'TIME': cols[0],
	'VOLTS': cols[1]
}



ROOT_IO.write_data(filename, "Waveform", data)
