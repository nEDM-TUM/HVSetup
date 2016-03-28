#!/usr/bin/env python
__author__ = 'Christian Velten'

FORCE_DRAW = False
HAS_ROOT_LIB = True

import LIB.Compression
try: from LIB.USBTMCInstrument import USBTMCObject, USBInstruments
except ImportError: FORCE_DRAW = True
try:
	import ROOT
	import LIB.ROOT_IO
except ImportError: HAS_ROOT_LIB = False

import argparse
import numpy as np
import os
import re
import sys
import time

parser = argparse.ArgumentParser(description="gets the waveform from the oscilloscope via usbtmc")
parser.add_argument("file")
parser.add_argument("-c", "--compress", action="store_true")
parser.add_argument("--start", type=int, default=1, help="first point")
parser.add_argument("--stop", type=int, default=1000000, help="last point")
parser.add_argument("-d", "--draw", help="just print the waveform specified by file (must be ROOT!)", action="store_true")
parser.add_argument("-i", "--interactive", action="store_true")
args = parser.parse_args()
if FORCE_DRAW: args.draw = True

if not args.draw:
	print "WARNING: Make sure, the part of the waveform you want to transfer is within the datapoint range of max. 1M!"

	# connect to oscilloscope
	sOsci = USBTMCObject(USBInstruments['LABOR']['vendorID'], USBInstruments['LABOR']['productID'])
	print "\tInstrument: " + str(sOsci.ask("*IDN?"))

	# set up for waveform transfer
	sOsci.cmd("DATA:SOURCE CH1")
	sOsci.cmd("DATA:START {0}".format(args.start))
	sOsci.cmd("DATA:STOP {0}".format(args.stop))
	sOsci.cmd("DATA:ENCDG ASCII")
	sOsci.cmd("DATA:WIDTH 2")
	sOsci.cmd("HEADER 1")
	sOsci.cmd("VERBOSE 1")
	sOsci.cmd("*WAI")

	header = sOsci.ask("WFMOUTPRE?")
	npoints = sOsci.ask("WFMOUTPRE:NR_PT?")
	xzero = float(re.findall(r'\b\d+\b', sOsci.ask("WFMOUTPRE:XZERO?"))[0])
	xincr = float(re.findall(r'\b\d+\b', sOsci.ask("WFMOUTPRE:XINCR?"))[0])
	xunit = sOsci.ask("WFMOUTPRE:XUNIT?")
	yzero = float(re.findall(r'\b\d+\b', sOsci.ask("WFMOUTPRE:YZERO?"))[0])
	yoffs = float(re.findall(r'\b\d+\b', sOsci.ask("WFMOUTPRE:YOFF?"))[0])
	ymult = float(re.findall(r'\b\d+\b', sOsci.ask("WFMOUTPRE:YMULT?"))[0])
	yunit = sOsci.ask("WFMOUTPRE:YUNIT?")
	bytnr = sOsci.ask("WFMOUTPRE:BYT_NR?")

	sOsci.cmd("HEADER 0")
	sOsci.cmd("*WAI")

	time.sleep(1)

	data = sOsci.ask('CURVE?')
	data = np.array(data.split(','), dtype=float)

	volts = (data - yoffs) * ymult + yzero
	time = np.arange(0, xincr * len(volts), xincr)

	if args.file is None or args.file == "":
		file = raw_input("Filename: ")
	else:
		output_file = args.file
	handle = open(output_file, "w")
	handle.write("#"+header+"\n")
	handle.write("#KEYS==[TIME in {0}]\t[VOLTAGE in {1}]\n".format(xunit, yunit))
	for i in range(len(time)):
		handle.write("{0}\t{1}\n".format(time[i], volts[i]))
	handle.close()

	if args.compress:
		LIB.Compression.gzip_file(output_file)
		os.remove(output_file)
		print "wrote data to '" + output_file + ".gz'"
	else:
		print "wrote data to '" + output_file + "'"
	if HAS_ROOT_LIB:
		data = {'HEADER': header, 'TIME': time, 'VOLTS': volts}
		LIB.ROOT_IO.ROOT_IO.write_data(output_file, "Waveform", data)
		print "created ROOT file from data ('" + output_file + ".root')"

else:
	if not HAS_ROOT_LIB:
		print "You need ROOT for drawing!"
		sys.exit(1)

	TFile, T = LIB.ROOT_IO.ROOT_IO.get_tree(args.file, 'Waveform')
	print TFile.ls()

	_t, _V = np.zeros(1), np.zeros(1)
	T.SetBranchAddress("TIME", _t)
	T.SetBranchAddress("VOLTS", _V)
	n = T.GetEntries()
	t, V = np.empty(n), np.empty(n)
	for i in range(n):
		T.GetEntry(i)
		t[i] = _t
		V[i] = _V

	group = 1000
	tReduced, VReduced = t.reshape(-1, group).mean(axis=1), V.reshape(-1, group).mean(axis=1)
	
	canvas_name, canvas_title = "cWaveform", "Waveform"
	"""
		ROOT SETTINGS
	"""
	ROOT.gROOT.SetStyle("Plain")
	canvas = ROOT.TCanvas(canvas_name, canvas_title, 1000, 768)
	canvas.SetTopMargin(0.04)
	canvas.SetBottomMargin(0.10)
	canvas.SetLeftMargin(0.08)
	canvas.SetRightMargin(0.04)
	canvas.SetGrid()

	graph = ROOT.TGraphErrors(len(tReduced), tReduced, VReduced, np.zeros(n), np.zeros(n))
	graph.SetTitle(";time [s] / laser diode current [a.u.];differential DAVLL signal [V]")
	graph.SetMarkerStyle(7)
	graph.SetMarkerColor(ROOT.kRed+2)
	graph.SetMarkerSize(3)
	graph.SetLineStyle(1)
	graph.SetLineColor(ROOT.kRed+2)
	graph.SetLineWidth(3)
	graph.GetXaxis().SetRangeUser(0, 10)
	#graph.GetYaxis().SetRangeUser(-3, 5)
	graph.GetXaxis().SetTitleOffset(1.0)
	graph.GetYaxis().SetTitleOffset(0.8)
	graph.GetXaxis().CenterTitle(1)
	graph.GetYaxis().CenterTitle(1)

	graph.Draw("ACX")

	ROOT.gPad.Update()
	canvas.Print("Waveform.pdf")

	cin = ''
	while cin.lower() != 'q' and args.interactive:
		cin = raw_input("> ")
	pass

