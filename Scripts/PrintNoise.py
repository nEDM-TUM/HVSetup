#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Christian Velten'

from LIB.ROOT_IO import read_root_noise, COLORSET_DARK
import argparse
import numpy as np
import os
import sys

try:
	from LIB.ROOT_IO import ROOT_IO
	import ROOT
except ImportError:
	print "Couldn't find ROOT framework! Install it or set the appropriate envars (e.g. PYTHONPATH)!"
	sys.exit(1)

parser = argparse.ArgumentParser(description="Python script to print one/several ROOT files containing noise data.")
parser.add_argument("files", nargs="+", help="filename to convert")
parser.add_argument("-i", "--interactive", action="store_true")
args = parser.parse_args()

file_list = []
if args.files:
	for filename in args.files:
		if os.path.isfile(filename) and filename[-4:] == 'root':
			file_list.append(os.path.abspath(str(filename).strip()))
		else:
			print "This is not a valid file: '" + filename + "'"
	if len(file_list) == 0:
		print "No suitable file found!"
		sys.exit(1)
else:
	print "Need valid filename(s) to proceed!"
	sys.exit(1)

"""
	ROOT CONFIGURATION
"""
ROOT.gROOT.SetStyle("Plain")
# ...
canvas = ROOT.TCanvas("cNoise", "cNoise", 1366, 1024)
canvas.SetTopMargin(0.022)
canvas.SetBottomMargin(0.12)
canvas.SetLeftMargin(0.09)
canvas.SetRightMargin(0.02)
canvas.SetGrid()
canvas.SetLogx()
canvas.SetLogy()

print "\n\nTODO: SET GRID STYLE / SIZE / COLOR\n\n"
# ...
gMultiNoise = ROOT.TMultiGraph()
gMultiNoise.SetTitle(";frequency [Hz];noise [\xb5V/#sqrt{Hz}]")

data = [read_root_noise(filename, tree=None, verbose=True, raise_errors=False) for filename in file_list]

count = 0
for data_set in data:
	n, f, N, Nu = data_set['n'], data_set['f'], data_set['N'], data_set['Nu']

	# add two points: (90mHz, 1nV), (200kHz, 10mV)
	f, N, Nu = np.insert(f, 0, 9E-2), np.insert(N, 0, 1E-9), np.insert(Nu, 0, 0.0)
	f, N, Nu = np.append(f, 2E+5), np.append(N, 1E-3), np.append(Nu, 0.0)

	gNoise = ROOT.TGraphErrors(n+2, f, N*1E+6, np.zeros(n+2), Nu)
	gNoise.SetTitle(";frequency [Hz];noise [\xb5V/#sqrt{Hz}]")
	gNoise.SetMarkerStyle(7)
	gNoise.SetMarkerColor(COLORSET_DARK[count % len(COLORSET_DARK)])
	gNoise.SetLineColor(COLORSET_DARK[count % len(COLORSET_DARK)])
	gMultiNoise.Add(gNoise)
	count += 1

gMultiNoise.Draw("APX")

gMultiNoise.GetXaxis().SetRangeUser(0.1, 110E+3)
gMultiNoise.GetXaxis().SetTitleOffset(1.25)
gMultiNoise.GetYaxis().SetRangeUser(1.0, 1E+3)

ROOT.gPad.Update()

canvas.Print("Noise.pdf")

if args.interactive:
	cin = "."
	while cin != "":
		cin = raw_input("")
		if cin.upper() == 'L':
			gNoise.Draw("AL")
			continue
		if cin.upper() == 'C':
			gNoise.Draw("AC")
			continue
		if cin.lower() == 'print' or cin == 'p':
			cin = raw_input("Filename: ")
			canvas.Print(cin)
