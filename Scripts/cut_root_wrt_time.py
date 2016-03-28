#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Christian Velten'

import LIB.ROOT_IO

import argparse
import itertools
import numpy as np
import os
import ROOT
import sys


def robust_reshape(arr, group):
	output = np.zeros(len(arr)/group)
	for i in range( int(len(arr)/group) ):
		for j in range(group):
			output[i] += arr[i*group+j] / float(group)
	return output


def allen_data(xin, yin):
	group = np.arange(1, len(xin)/2, 1, dtype=int)
	std = np.empty(len(group))
	for i in range(len(group)):
		std[i] = robust_reshape(yin, group[i]).std()
	return group, std


parser = argparse.ArgumentParser()
parser.add_argument("ifile")
parser.add_argument("--sweep", action="store_true")
parser.add_argument("--stability", action="store_true")
args = parser.parse_args()
if not (args.stability or args.sweep): args.sweep = True

if not os.path.isfile(args.ifile):
	print "File does not exist!"
	sys.exit(1)

treename = "PI_Stability" if args.stability else "PI_Sweep"

TFile, T = LIB.ROOT_IO.ROOT_IO.get_tree(args.ifile, treename)
keys = []
for branch in T.GetListOfBranches():
	keys.append(str(branch.GetName()))
leaves = {key: np.zeros(1) for key in keys}
for key in keys:
	T.SetBranchAddress(key, leaves[key])
n = T.GetEntries()
data = {key: np.empty(n) for key in keys}
for i in range(n):
	T.GetEntry(i)
	for key in keys:
		data[key][i] = leaves[key]


constraint = -1
for i in range(n):
	if data['TIME'][i] > 2200.0 * 60.:
		constraint = i
		break
print constraint, data['TIME'][constraint]

for key in keys:
	data[key] = np.array(data[key][:constraint])

LIB.ROOT_IO.ROOT_IO.write_data(args.ifile+'-cut', treename, data)

