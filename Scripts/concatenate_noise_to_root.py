#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'cvelten'

import argparse
import numpy as np
import os
import sys

try:
	from LIB.ROOT_IO import ROOT_IO
	import ROOT
except ImportError:
	print "Couldn't find ROOT framework! Install it or set the appropriate flags!"
	sys.exit(1)


def sort_data(obj):
	"""
	Sorts all the rows in obj's arrays wrt the same column.
	"""
	z = zip(obj['TIME'], obj['FREQUENCY'], obj['Vp'], obj['Vp_STDDEV'], obj['Vm'], obj['Vm_STDDEV'], obj['NOISE'], obj['NOISE_STDDEV'])
	obj_sorted = sorted(z, key=lambda z: z[0])
	for i in range(len(obj_sorted)):
		obj['TIME'][i] = obj_sorted[i][0]
		obj['FREQUENCY'][i] = obj_sorted[i][1]
		obj['Vp'][i] = obj_sorted[i][2]
		obj['Vp_STDDEV'][i] = obj_sorted[i][3]
		obj['Vm'][i] = obj_sorted[i][4]
		obj['Vm_STDDEV'][i] = obj_sorted[i][5]
		obj['NOISE'][i] = obj_sorted[i][6]
		obj['NOISE_STDDEV'][i] = obj_sorted[i][7]
	return obj
	return {'TIME': z[0], 'FREQUENCY': z[1], 'Vp': z[2], 'Vp_STDDEV': z[3], 'Vm': z[4], 'Vm_STDDEV': z[5], 'NOISE': z[6], 'NOISE_STDDEV': z[7]}


ROOT.gROOT.SetStyle("Plain")

parser = argparse.ArgumentParser(description="Python script to concatenate different Noise-ROOT files. Existing frequencies get averaged, new ones get concatenated.")
parser.add_argument("file_list", nargs="+", help="filenames of files to concatenate")
parser.add_argument("-o", "--out", help="filename of output file")
parser.add_argument("-i", "--interactive", action="store_true")
parser.add_argument("-t", "--time", help="concatenate time-based instead of frequency-based", action="store_true")
args = parser.parse_args()

if args.file_list:
	file_list = args.file_list
	for file_id in range(len(file_list)):
		if os.path.isfile(file_list[file_id]):
			file_list[file_id] = os.path.abspath(str(file_list[file_id]).strip())
		else:
			print "Need valid filename to proceed!\t'" + file_list[file_id] + "'"
			sys.exit(1)
else:
	print "Filelist is empty?!"
	sys.exit(1)

if args.out:
	filename_out = args.out if args.out[-5:] == '.root' else args.out+'.root'
	TFile = ROOT.TFile(filename_out, 'RECREATE')
else:
	print "File is not a ROOT file!"
	sys.exit(1)

data = {
	'TIME': np.empty(0),
	'FREQUENCY': np.empty(0),
	'NOISE': np.empty(0), 'NOISE_STDDEV': np.empty(0),
	'Vp': np.empty(0), 'Vp_STDDEV': np.empty(0),
	'Vm': np.empty(0), 'Vm_STDDEV': np.empty(0)
}

for filename in file_list:
	print "\nLoading file '" + filename + "'..."
	TFileConcat = ROOT.TFile(filename, 'READ')
	TFileConcat.ls()

	cin = raw_input("-> enter tree name [PowerBox_Characterize]: ")
	if cin == "": cin = "PowerBox_Characterize"
	T = TFileConcat.Get(cin)

	_t, _f, _N, _Nu = np.zeros(1), np.zeros(1), np.zeros(1), np.zeros(1)
	_Vp, _Vm, _Vpu, _Vmu = np.zeros(1), np.zeros(1), np.zeros(1), np.zeros(1)
	T.SetBranchAddress("TIME", _t)
	T.SetBranchAddress("FREQUENCY", _f)
	T.SetBranchAddress("NOISE", _N)
	T.SetBranchAddress("NOISE_STDDEV", _Nu)
	T.SetBranchAddress("Vp", _Vp)
	T.SetBranchAddress("Vm", _Vm)
	T.SetBranchAddress("Vp_STDDEV", _Vpu)
	T.SetBranchAddress("Vm_STDDEV", _Vmu)

	n = T.GetEntries()

	data_tmp = {'TIME': np.empty(n), 'FREQUENCY': np.empty(n), 'NOISE': np.empty(n), 'NOISE_STDDEV': np.empty(n), 'Vp': np.empty(n), 'Vp_STDDEV': np.empty(n), 'Vm': np.empty(n), 'Vm_STDDEV': np.empty(n)}

	t0 = data['TIME'][-1] if len(data['TIME']) > 0 else 0.0
	for i in range(n):
		T.GetEntry(i)
		data_tmp['TIME'][i] = _t + t0 if args.time else _t
		data_tmp['FREQUENCY'][i] = _f
		data_tmp['NOISE'][i] = _N
		data_tmp['NOISE_STDDEV'][i] = _Nu
		data_tmp['Vp'][i] = _Vp
		data_tmp['Vm'][i] = _Vm
		data_tmp['Vp_STDDEV'][i] = _Vpu
		data_tmp['Vm_STDDEV'][i] = _Vmu
	
	TFileConcat.Close()
	
	# simple concatenation: will produce ugly results if used with AC or AL if used on unsorted data
	for key in data.keys():
		data[key] = np.append(data[key], data_tmp[key])
# end for filename in file_list
data = sort_data(data)
#
print "\nSaving new data objects to file '" + filename_out + "'..."
ROOT_IO.write_data(filename_out, "PowerBox_Characterize", data)