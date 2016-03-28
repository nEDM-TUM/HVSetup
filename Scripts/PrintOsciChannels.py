#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Christian Velten'

from LIB.ROOT_IO import read_root_channels, COLORSET_DARK
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

parser = argparse.ArgumentParser(description="Python script to print one/several ROOT files containing oscilloscope channel data.")
parser.add_argument("files", nargs="+", help="filename to convert")
parser.add_argument("-i", "--interactive", action="store_true")
parser.add_argument("-n", "--nchannels", choices=[1,2,3], type=int, default=1, help="number of channels to read")
parser.add_argument("--has_temp", action="store_true")
parser.add_argument("--has_voltage", action="store_true")
parser.add_argument("-v", "--verbose", action="store_true")
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

data = [read_root_channels(filename, tree=None, channels=args.nchannels, verbose=args.verbose, raise_errors=False, has_temp=args.has_temp) for filename in file_list]

"""
	ROOT CONFIGURATION
"""
ROOT.gROOT.SetStyle("Plain")
# ...
canvas = ROOT.TCanvas("cChannels", "cChannels", 1366, 1024)
canvas.SetTopMargin(0.022)
canvas.SetBottomMargin(0.12)
canvas.SetLeftMargin(0.09)
canvas.SetRightMargin(0.02)
canvas.SetGrid()
#canvas.SetLogx()
#canvas.SetLogy()

print "\n\nTODO: SET GRID STYLE / SIZE / COLOR\n\n"
# ...
gMultiChannels = ROOT.TMultiGraph()
gMultiChannels.SetTitle(";time [s];channel mean [mV]")

count = 0
for data_set in data:
	n, t, CH1, CH1u, CH2, CH2u, CH3, CH3u = data_set['n'], data_set['t'], data_set['CH1'], data_set['CH1u'], data_set['CH2'], data_set['CH2u'], data_set['CH3'], data_set['CH3u']
	TC, TCu = data_set['TC'], data_set['TCu']

	for i in range(args.nchannels):
	    if i == 0: ch, chu = CH1, CH1u
	    if i == 1: ch, chu = CH2, CH2u
	    if i == 2: ch, chu = CH3, CH3u
	    gChannels = ROOT.TGraphErrors(n, t, ch, np.zeros(n), chu)
	    #gChannels = ROOT.TGraphErrors(n, t, ch/ch[1], np.zeros(n), chu/chu[1])
	    #gChannels = ROOT.TGraphErrors(n, t, ch/ch[1] / (TC/TC[1]), np.zeros(n), chu/chu[1] / (TC/TC[1]))
	    gChannels.SetTitle(";time [s];channel mean [mV]")
	    gChannels.SetMarkerStyle(7)
	    gChannels.SetMarkerColor(COLORSET_DARK[count % len(COLORSET_DARK)])
	    gChannels.SetLineColor(COLORSET_DARK[count % len(COLORSET_DARK)])
	    gMultiChannels.Add(gChannels)
	    count += 1

	if args.has_temp:
		gTemp = ROOT.TGraphErrors(n, t, TC, np.zeros(n), TCu)
		gTemp.SetMarkerColor(COLORSET_DARK[count+1 % len(COLORSET_DARK)])
		gTemp.SetLineColor(COLORSET_DARK[count+1 % len(COLORSET_DARK)])
		gMultiChannels.Add(gTemp)

gMultiChannels.Draw("APX")

#gMultiChannels.GetXaxis().SetRangeUser(0.1, 110E+3)
#gMultiChannels.GetXaxis().SetTitleOffset(1.25)
#gMultiChannels.GetYaxis().SetRangeUser(1.0, 1E+3)

ROOT.gPad.Update()


if args.interactive:
	cin = "."
	while cin != "":
		cin = raw_input("")
		if cin.upper() == 'L':
			gChannels.Draw("AL")
			continue
		if cin.upper() == 'C':
			gChannels.Draw("AC")
			continue
		if cin.lower() == 'print' or cin == 'p':
			cin = raw_input("Filename: ")
			canvas.Print(cin)
