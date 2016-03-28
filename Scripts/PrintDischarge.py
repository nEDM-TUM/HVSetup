#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'cvelten'

from LIB.ROOT_IO import read_root_discharge, COLORSET_DARK
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

parser = argparse.ArgumentParser(description="")
parser.add_argument("files", nargs="+", help="filenames to print")
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
canvas = ROOT.TCanvas("cDischarge", "cDischarge", 800, 800)
canvas.SetTopMargin(0.022)
canvas.SetBottomMargin(0.12)
canvas.SetLeftMargin(0.09)
canvas.SetRightMargin(0.02)
canvas.SetGrid()

print "\n\nTODO: SET GRID STYLE / SIZE / COLOR\n\n"
gMultiDischarge = ROOT.TMultiGraph()
gMultiDischarge.SetTitle(";time [s];voltage [V]")

data = [read_root_discharge(filename, tree=None, verbose=True, raise_errors=False) for filename in file_list]

count = 0
for data_set in data:
	n, t, VpVm, VpuVmu, Vp, Vpu, Vm, Vmu = data_set['n'], data_set['t'], data_set['VpVm'], data_set['VpuVmu'], data_set['Vp'], data_set['Vpu'], data_set['Vm'], data_set['Vmu']

	gDischargeA = ROOT.TGraphErrors(n, t, Vp, np.zeros(n), Vpu)
	gDischargeA.SetTitle("discharge of battery block (using 2x45W lamps);time [s];voltage [V]")
	gDischargeA.SetMarkerStyle(7)
	gDischargeA.SetMarkerColor(COLORSET_DARK[count % len(COLORSET_DARK)])
	gDischargeA.SetLineColor(COLORSET_DARK[count % len(COLORSET_DARK)])
	count += 1
	
	gDischargeB = ROOT.TGraphErrors(n, t, Vm, np.zeros(n), Vmu)
	gDischargeB.SetTitle("discharge of battery block (using 2x45W lamps);time [s];voltage [V]")
	gDischargeB.SetMarkerStyle(7)
	gDischargeB.SetMarkerColor(COLORSET_DARK[count % len(COLORSET_DARK)])
	gDischargeB.SetLineColor(COLORSET_DARK[count % len(COLORSET_DARK)])
	count += 1
	
	gMultiDischarge.Add(gDischargeA)
	gMultiDischarge.Add(gDischargeB)

gMultiDischarge.Draw("APX")

#gMultiNoise.GetXaxis().SetRangeUser(0.1, 110E+3)
#gMultiNoise.GetXaxis().SetTitleOffset(1.25)
#gMultiDischarge.GetYaxis().SetRangeUser(1.0, 1E+3)

ROOT.gPad.Update()

canvas.Print("BoxDischarge.pdf")

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
