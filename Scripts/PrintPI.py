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
	group = np.arange(1, 1+len(xin)/2, 5, dtype=int)
	std = np.empty(len(group))
	for i in range(len(group)):
		std[i] = robust_reshape(yin, int(group[i])).std()
	return group, std


parser = argparse.ArgumentParser()
parser.add_argument("ifile")
parser.add_argument("-i", "--interactive", action="store_true")
parser.add_argument("--sweep", action="store_true")
parser.add_argument("--stability", action="store_true")
parser.add_argument("--diff", action="store_true")
args = parser.parse_args()
if not (args.stability or args.sweep): args.sweep = True

keys = ['TIME', 'TIME_OFFSET', 'LDC_I', 'LDC_T', 'PID_PROP', 'PID_INTG', 'PID_MEAS', 'PID_MEASu', 'PID_PXER', 'PID_PXERu', 'PID_OUTP', 'PID_OUTPu', 'DIFF', 'DIFFu', 'MODU', 'MODUu', 'TEMP', 'TEMPu', 'OSC3', 'OSC3u']
data = {key: [] for key in keys}

if not os.path.isfile(args.ifile):
	print "File does not exist!"
	sys.exit(1)

treename = "PI_Stability" if args.stability else "PI_Sweep"

if not args.ifile[-4:] == 'root':
	handle = open(args.ifile, 'r')
	lines = handle.readlines()
	handle.close()

	for line in lines:
		if line.strip().startswith('#'): continue
		tmp = line.strip().split('\t')
		for i in range(len(keys)):
			data[keys[i]].append(float(tmp[i].strip()))
	if not os.path.isfile(args.ifile+'.root'):
		LIB.ROOT_IO.ROOT_IO.write_data(args.ifile, treename, data)
else:
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
	pass


t, TEMP, TEMPu = np.array(data['TIME']), np.array(data['TEMP']), np.array(data['TEMPu'])
P, I, PXER, PXERu = np.array(data['PID_PROP']), np.array(data['PID_INTG']), np.array(data['PID_PXER']), np.array(data['PID_PXERu'])
MEAS, MEASu, OUTP, OUTPu = np.array(data['PID_MEAS']), np.array(data['PID_MEASu']), np.array(data['PID_OUTP']), np.array(data['PID_OUTPu'])
DIFF, DIFFu, MODU, MODUu = np.array(data['DIFF']), np.array(data['DIFFu']), np.array(data['MODU']), np.array(data['MODUu'])
OSC3 = np.array(data['OSC3']) if 'OSC3' in keys else np.zeros(len(t))
OSC3u = np.array(data['OSC3u']) if 'OSC3u' in keys else np.zeros(len(t))
LDC_I, LDC_T = np.array(data['LDC_I']), np.array(data['LDC_T'])

ER = np.absolute(PXER/P)
ERu = PXERu

print "MEAS-Mean/STD =", MEAS.mean(), MEAS.std()

"""
	ROOT SETTINGS
"""
ROOT.gROOT.SetStyle("Plain")
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadGridX(1)
ROOT.gStyle.SetPadGridY(1)
ROOT.gStyle.SetMarkerStyle(6)
ROOT.gStyle.SetMarkerSize(1)
ROOT.gStyle.SetLineWidth(2)
ROOT.gStyle.SetLineStyle(1)
ROOT.gStyle.SetFillStyle(3001)
ROOT.gStyle.SetMarkerColor(ROOT.kRed+2)
ROOT.gStyle.SetLineColor(ROOT.kRed+2)
ROOT.gStyle.SetFillColor(ROOT.kRed)

canvas_name, canvas_title = "cPI", "PI"
canvas = ROOT.TCanvas(canvas_name, canvas_title, 1366, 768)

if not args.stability:
	canvas_name, canvas_title = "cPxER", "PxER"
	tmargin, bmargin, lmargin, rmargin = 0.04, 0.10, 0.12, 0.12
	canvas = ROOT.TCanvas(canvas_name, canvas_title, 1366, 768)

	canvas.Divide(2, 1)
	canvas.cd(1).SetTopMargin(tmargin)
	canvas.cd(1).SetBottomMargin(bmargin)
	canvas.cd(1).SetLeftMargin(lmargin)
	canvas.cd(1).SetRightMargin(rmargin)
	canvas.cd(2).SetTopMargin(tmargin)
	canvas.cd(2).SetBottomMargin(bmargin)
	canvas.cd(2).SetLeftMargin(lmargin)
	canvas.cd(2).SetRightMargin(rmargin)

	I /= 1E+3
	nbinsx, nbinsy = len(np.unique(P)), len(np.unique(I))
	xbins_size, ybins_size = (max(P)-min(P))/nbinsx, (max(I)-min(I))/nbinsy
	xlow, xup = min(P)-xbins_size/2., max(P)+xbins_size/2.
	ylow, yup = min(I)-ybins_size/2., max(I)+ybins_size/2.

	TH2_ER = ROOT.TH2D("PIERR", "PIERR", nbinsx, xlow, xup, nbinsy, ylow, yup)
	TH2_ER.SetTitle("|PxER/P|;;integral coefficient [10^{3}s^{-1}];")
	TH2_ER.GetXaxis().SetTitleOffset(1.1)
	TH2_ER.GetYaxis().SetTitleOffset(1.4)
	TH2_ERu = ROOT.TH2D("PIERRu", "PIERRu", nbinsx, xlow, xup, nbinsy, ylow, yup)
	TH2_ERu.SetTitle("|PxERu/P|;proportional coefficient [V/V];")
	TH2_ERu.GetXaxis().SetTitleOffset(1.1)
	TH2_ERu.GetYaxis().SetTitleOffset(1.4)

	for i in range(len(P)):
	    for j in range(len(I)):
		TH2_ER.Fill(P[i], I[j], np.log10(ER[i*j+j]))
		TH2_ERu.Fill(P[i], I[j], np.log10(ERu[i*j+j]))

	canvas.cd(1)
	TH2_ER.Draw("CONT4 Z")
	canvas.cd(2)
	TH2_ERu.Draw("CONT4 Z")

	ROOT.gPad.Update()

	# TODO: print @data path
	canvas.Print("PIERR.pdf")
elif args.stability:
	tmargin, bmargin, lmargin, rmargin = 0.04, 0.10, 0.10, 0.10

	pad1 = ROOT.TPad("pad1","",0,0,1,1)
	pad2 = ROOT.TPad("pad2","",0,0,1,1)
	pad2.SetFillStyle(4000)
	pad2.SetFrameFillStyle(0)

	pad1.SetTopMargin(tmargin)
	pad1.SetBottomMargin(bmargin)
	pad1.SetLeftMargin(lmargin)
	pad1.SetRightMargin(rmargin)
	pad2.SetTopMargin(tmargin)
	pad2.SetBottomMargin(bmargin)
	pad2.SetLeftMargin(lmargin)
	pad2.SetRightMargin(rmargin)

	pad1.SetGrid(1, 0)
	pad1.Draw()
	pad1.cd()

	scale_MEAS = 1E+6 # uV
	scale_OUTP = 1E+0 # V
	scale_PXER = 1E+0 # V

	"""
	group = 1
	t = t.reshape(-1, group).mean(axis=1)
	MEAS, MEASu = MEAS.reshape(-1, group).mean(axis=1), MEASu.reshape(-1, group).mean(axis=1)
	OUTP, OUTPu = OUTP.reshape(-1, group).mean(axis=1), OUTPu.reshape(-1, group).mean(axis=1)
	"""

	n = len(MEAS)
	TG_MEAS = ROOT.TGraphErrors(n, t, (MEAS)*scale_MEAS, np.zeros(n), MEASu*scale_MEAS/np.sqrt(10.))
	TG_OUTP = ROOT.TGraphErrors(n, t, (OUTP)*scale_OUTP, np.zeros(n), OUTPu*scale_OUTP/np.sqrt(10.))
	TG_PXER = ROOT.TGraphErrors(n, t, PXER*scale_PXER, np.zeros(n), PXERu*scale_PXER/np.sqrt(10.))

	TG_PXER.SetMarkerColor(ROOT.kGreen+1)
	TG_PXER.SetLineColor(ROOT.kGreen+1)

	TG_MEAS.SetTitle(";time of day [HH:MM]; PID input signal [µV]")
	TG_MEAS.SetMarkerColor(ROOT.kBlue+2)
	TG_MEAS.SetLineColor(ROOT.kBlue+2)
	TG_MEAS.SetLineWidth(1)
	TG_MEAS.SetFillColor(ROOT.kBlue)
	TG_MEAS.SetFillStyle(3001)
	TG_MEAS.GetXaxis().SetRangeUser(t[0], t[-1])
	TG_MEAS.GetXaxis().SetTitleOffset(1.1)
	TG_MEAS.GetXaxis().SetTimeDisplay(1)
	TG_MEAS.GetXaxis().SetTimeFormat("%H:%M")
	TG_MEAS.GetXaxis().SetTimeOffset(data['TIME_OFFSET'][0])
	TG_MEAS.GetXaxis().SetNdivisions(8)
	TG_MEAS.GetYaxis().SetAxisColor(ROOT.kBlue+2)
	TG_MEAS.GetYaxis().SetLabelColor(ROOT.kBlue+2)
	TG_MEAS.GetYaxis().SetNdivisions(510)
	TG_MEAS.GetYaxis().SetTickLength(0.01)
	TG_MEAS.Draw("AL 3")

	pad2.SetGrid(0, 1)
	pad2.Draw()
	pad2.cd()

	TG_OUTP.SetTitle(";;PID output signal [V]")
	TG_OUTP.SetMarkerColor(ROOT.kRed+2)
	TG_OUTP.SetLineColor(ROOT.kRed+2)
	TG_OUTP.SetLineWidth(2)
	TG_OUTP.SetFillColor(ROOT.kRed)
	TG_OUTP.SetFillStyle(3001)
	TG_OUTP.GetXaxis().SetRangeUser(t[0], t[-1])
	TG_OUTP.GetXaxis().SetNdivisions(0)
	TG_OUTP.GetYaxis().SetAxisColor(ROOT.kRed+2)
	TG_OUTP.GetYaxis().SetLabelColor(ROOT.kRed+2)
	TG_OUTP.GetYaxis().SetNdivisions(510)
	TG_OUTP.GetYaxis().SetTickLength(0.01)
	TG_OUTP.Draw("ALY+ 3")

	ROOT.gPad.Update()
	canvas.Print("PIStability.pdf")

	if args.diff:
		"""
		canvasDIFF = ROOT.TCanvas("cDiff", "cDiff", 1366, 768)
		canvasDIFF.Draw()
		t_A, DIFF_A = allen_data(t, DIFF)
		TG_DIFF_ALLEN = ROOT.TGraph(len(t_A), t_A/1.0, DIFF_A)
		TG_DIFF_ALLEN.SetTitle(";bin size; std-dev")
		TG_DIFF_ALLEN.SetLineWidth(1)
		TG_DIFF_ALLEN.SetFillStyle(3001)
		TG_DIFF_ALLEN.Draw("AP")
		"""
		ROOT.gPad.Update()

		TG_DIFF = ROOT.TGraphErrors(len(t), t, DIFF, np.zeros(len(t)), DIFFu)
		TG_PD1 = ROOT.TGraphErrors(len(t), t, MODU, np.zeros(len(t)), MODUu)
		TG_PD2 = ROOT.TGraphErrors(len(t), t, OSC3, np.zeros(len(t)), OSC3u)

		TG_DIFF.SetTitle(";time [];DIFF signal [V]")
		TG_PD1.SetTitle(";time [];PD1 signal [V]")
		TG_PD2.SetTitle(";time [];PD2 signal [V]")

		TG_DIFF.SetFillStyle(3001)
		TG_PD1.SetFillStyle(3001)
		TG_PD2.SetFillStyle(3001)

		TG_DIFF.GetXaxis().SetRangeUser(t[0], t[-1])
		TG_DIFF.GetYaxis().SetRangeUser(min(DIFF)-0.005*np.fabs(DIFF.mean()), max(DIFF)+0.005*np.fabs(DIFF.mean()))
		TG_DIFF.GetXaxis().SetTimeDisplay(1)
		TG_DIFF.GetXaxis().SetTimeFormat("%H:%M")
		TG_DIFF.GetXaxis().SetTimeOffset(data['TIME_OFFSET'][0])
		TG_DIFF.GetXaxis().SetNdivisions(8)

		TG_PD1.GetXaxis().SetRangeUser(t[0], t[-1])
		TG_PD1.GetYaxis().SetRangeUser(min(MODU)-0.005*np.fabs(MODU.mean()), max(MODU)+0.005*np.fabs(MODU.mean()))
		TG_PD1.GetXaxis().SetTimeDisplay(1)
		TG_PD1.GetXaxis().SetTimeFormat("%H:%M")
		TG_PD1.GetXaxis().SetTimeOffset(data['TIME_OFFSET'][0])
		TG_PD1.GetXaxis().SetNdivisions(8)

		TG_PD2.GetXaxis().SetRangeUser(t[0], t[-1])
		TG_PD2.GetYaxis().SetRangeUser(min(OSC3)-0.005*np.fabs(OSC3.mean()), max(OSC3)+0.005*np.fabs(OSC3.mean()))
		TG_PD2.GetXaxis().SetTimeDisplay(1)
		TG_PD2.GetXaxis().SetTimeFormat("%H:%M")
		TG_PD2.GetXaxis().SetTimeOffset(data['TIME_OFFSET'][0])
		TG_PD2.GetXaxis().SetNdivisions(8)

		tmargin, bmargin, lmargin, rmargin = 0.04, 0.10, 0.10, 0.04
		canvas3 = ROOT.TCanvas("c3", "c3", 1366, 768)
		canvas3.Draw()
		canvas3.Divide(3,1)
		ROOT.gPad.Update()
		canvas3.cd(1).SetTopMargin(tmargin)
		canvas3.cd(1).SetBottomMargin(bmargin)
		canvas3.cd(1).SetLeftMargin(lmargin)
		canvas3.cd(1).SetRightMargin(rmargin)
		canvas3.cd(2).SetTopMargin(tmargin)
		canvas3.cd(2).SetBottomMargin(bmargin)
		canvas3.cd(2).SetLeftMargin(lmargin)
		canvas3.cd(2).SetRightMargin(rmargin)
		canvas3.cd(3).SetTopMargin(tmargin)
		canvas3.cd(3).SetBottomMargin(bmargin)
		canvas3.cd(3).SetLeftMargin(lmargin)
		canvas3.cd(3).SetRightMargin(rmargin)

		canvas3.cd(1)
		TG_DIFF.Draw("AL X")
		canvas3.cd(2)
		TG_PD1.Draw("AL X")
		canvas3.cd(3)
		TG_PD2.Draw("AL X")

		ROOT.gPad.Update()

		canvasSINGLE = ROOT.TCanvas("cS", "cS", 1366, 768)
		canvasSINGLE.Draw()
		ROOT.gPad.Update()
		canvasSINGLE.SetTopMargin(tmargin)
		canvasSINGLE.SetBottomMargin(bmargin)
		canvasSINGLE.SetLeftMargin(lmargin)
		canvasSINGLE.SetRightMargin(rmargin)
		ROOT.gPad.Update()
		TG_DIFF.Draw("AL X")
		ROOT.gPad.Update()
		canvasSINGLE.Print("TG_DIFF.pdf")
		TG_PD1.Draw("AL X")
		ROOT.gPad.Update()
		canvasSINGLE.Print("TG_PD1.pdf")
		TG_PD2.Draw("AL X")
		ROOT.gPad.Update()
		canvasSINGLE.Print("TG_PD2.pdf")
else:
	pass


cin = ""
while cin.lower() != 'q' and args.interactive:
	cin = raw_input("> ")
