#!/usr/bin/env python
__author__ = 'Christian Velten'

from LIB.ROOT_IO import ROOT_IO

import argparse
import gzip
import os
import sys

parser = argparse.ArgumentParser(description="Python script to convert noise data to a ROOT file.")
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

cols = [[], [], [],[], [],[], [],[]]

for line in lines:
	if len(line.strip()) == 0 or line.strip()[0] == '#': continue
	tmp_line = line.strip().split('\t')
	for j in range(len(cols)):
		cols[j].append(float(tmp_line[j]))

data = {
	'TIME': cols[0],
	'FREQUENCY': cols[1],
	'Vp': cols[2], 'Vm': cols[4],
	'Vp_STDDEV': cols[3], 'Vm_STDDEV': cols[5],
	'NOISE': cols[6], 'NOISE_STDDEV': cols[7]
}

ROOT_IO.write_data(filename, "PowerBox_Characterize", data)