__author__ = 'Christian Velten'

import numpy
import ROOT
import sys
from LIB.STD import dictinvert


COLORSET_DARK = [ROOT.kBlack, ROOT.kGray+2, ROOT.kRed+2, ROOT.kBlue+2, ROOT.kOrange+5, ROOT.kGreen+3, ROOT.kCyan+2, ROOT.kMagenta+2]
COLORSET_LIGHT = [ROOT.kRed, ROOT.kBlue, ROOT.kOrange, ROOT.kGreen, ROOT.kCyan, ROOT.kMagenta]


class ROOT_IO(object):
	def __init__(self, filename, mode='RECREATE'):
		self.file = ROOT.TFile(filename, mode)

	def __delete__(self, instance):
		instance.file.Close()

	def readfile(self, filename):
		"""
		if not filename[-5:] == '.root':
			raise ValueError("Not a ROOT file!")
		return ROOT.TFile(filename, 'READ')
		"""
		pass

	@staticmethod
	def get_tree(filename, tree=None):
		if not filename[-5:] == '.root':
			raise ValueError("Not a ROOT file?!")
		TFile = ROOT.TFile(filename, 'READ')
		while tree is None:
			tree = raw_input("\nenter tree name: ")
			if tree == "": tree = None
		TTree = TFile.Get(tree)
		return TFile, TTree

	@staticmethod
	def write_data(filename, name, data, description='', mode='RECREATE'):
		"""

		:param filename:
		:param name:
		:param data: data in the format: {'NAME': [, , ... , ,], ... }
		:param description:
		:param mode:
		:return:
		"""
		if not filename[-5:] == '.root': filename += '.root'
		n = len(data[data.keys()[0]])

		# Open ROOT-File
		file = ROOT.TFile(filename, mode)

		# Create Tree
		tree = ROOT.TTree(name, description)

		# Create variables and set the branches
		var = {key: numpy.zeros(1, dtype=float) for key in data.keys()}
		branches = []
		
		for key in data.keys():
			branches.append(tree.Branch(key, var[key], key+'/D'))

		for i in range(n):
			for key in data.keys():
				try:
					var[key][0] = data[key][i]
				except IndexError:
					print "got IndexError, check last line?"
					break
			tree.Fill()

		file.Write()
		file.Save()
		file.Close()
		return filename


def read_root_noise(rootfile, tree=None, verbose=True, raise_errors=False):
	#SETTING UP FILE HANDLE
	if rootfile[-4:] == 'root':
		TFile = ROOT.TFile(rootfile, 'READ')
	else:
		print "File is not a ROOT file!"
		if raise_errors:
			raise ValueError("File '"+rootfile+"' is not a ROOT file!")
		return False

	if verbose:
		TFile.ls()

	if tree is None:
		tree = raw_input("\nenter tree name [PowerBox_Characterize]: ")
		if tree == "": tree = "PowerBox_Characterize"
	T = TFile.Get(tree)

	_t, _f, _N, _Nu = numpy.zeros(1), numpy.zeros(1), numpy.zeros(1), numpy.zeros(1)
	_Vp, _Vm, _Vpu, _Vmu = numpy.zeros(1), numpy.zeros(1), numpy.zeros(1), numpy.zeros(1)
	T.SetBranchAddress("TIME", _t)
	T.SetBranchAddress("FREQUENCY", _f)
	T.SetBranchAddress("NOISE", _N)
	T.SetBranchAddress("NOISE_STDDEV", _Nu)
	T.SetBranchAddress("Vp", _Vp)
	T.SetBranchAddress("Vm", _Vm)
	T.SetBranchAddress("Vp_STDDEV", _Vpu)
	T.SetBranchAddress("Vm_STDDEV", _Vmu)

	n = T.GetEntries()

	t, f, N, Nu, Vp, Vm, Vpu, Vmu = numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n)

	for i in range(n):
		T.GetEntry(i)
		t[i] = _t
		f[i] = _f
		N[i] = _N
		Nu[i] = _Nu
		Vp[i] = _Vp
		Vm[i] = _Vm
		Vpu[i] = _Vpu
		Vmu[i] = _Vmu

	VpVm = Vp + Vm
	VpuVmu = numpy.sqrt(Vpu**2 + Vmu**2)
	
	return {'n': n, 't': t, 'f': f, 'N': N, 'Nu': Nu, 'Vp': Vp, 'Vm': Vm, 'Vpu': Vpu, 'Vmu': Vmu, 'VpVm': VpVm, 'VpuVmu': VpuVmu}


def read_root_discharge(rootfile, tree=None, verbose=True, raise_errors=False):
	#SETTING UP FILE HANDLE
	if rootfile[-4:] == 'root':
		TFile = ROOT.TFile(rootfile, 'READ')
	else:
		print "File is not a ROOT file!"
		if raise_errors:
			raise ValueError("File '"+rootfile+"' is not a ROOT file!")
		return False

	if verbose:
		TFile.ls()

	if tree is None:
		tree = raw_input("\nenter tree name [PowerBox_Discharge]: ")
		if tree == "": tree = "PowerBox_Discharge"
	T = TFile.Get(tree)

	_t = numpy.zeros(1)
	_Vp, _Vm, _Vpu, _Vmu = numpy.zeros(1), numpy.zeros(1), numpy.zeros(1), numpy.zeros(1)
	T.SetBranchAddress("TIME", _t)
	T.SetBranchAddress("Vp", _Vp)
	T.SetBranchAddress("Vm", _Vm)
	T.SetBranchAddress("Vp_STDDEV", _Vpu)
	T.SetBranchAddress("Vm_STDDEV", _Vmu)

	n = T.GetEntries()

	t, Vp, Vm, Vpu, Vmu = numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n)

	for i in range(n):
		T.GetEntry(i)
		t[i] = _t
		Vp[i] = _Vp
		Vm[i] = _Vm
		Vpu[i] = _Vpu
		Vmu[i] = _Vmu

	VpVm = Vp + Vm
	VpuVmu = numpy.sqrt(Vpu**2 + Vmu**2)
	
	return {'n': n, 't': t, 'Vp': Vp, 'Vm': Vm, 'Vpu': Vpu, 'Vmu': Vmu, 'VpVm': VpVm, 'VpuVmu': VpuVmu}


def read_root_channels(rootfile, tree=None, channels=[1], verbose=True, raise_errors=False, has_temp=False, has_voltage=False):
	nchannels = len(channels)
	#SETTING UP FILE HANDLE
	if rootfile[-4:] == 'root':
		TFile = ROOT.TFile(rootfile, 'READ')
	else:
		print "File is not a ROOT file!"
		if raise_errors:
			raise ValueError("File '"+rootfile+"' is not a ROOT file!")
		return False
	if 0 > nchannels > 3:
		if raise_errors:
		    raise ValueError("Invalid number of channels provided!")
		else:
		    return False

	if verbose:
		TFile.ls()

	if tree is None:
		tree = raw_input("\nenter tree name [Lab_ReadContinuous]: ")
		if tree == "": tree = "Lab_ReadContinuous"
	T = TFile.Get(tree)

	_t, _tO = numpy.zeros(1), numpy.zeros(1)
	_CH1, _CH1u, _CH2, _CH2u, _CH3, _CH3u = numpy.zeros(1), numpy.zeros(1), numpy.zeros(1), numpy.zeros(1), numpy.zeros(1), numpy.zeros(1)
	_Up, _Um, _Upu, _Umu = numpy.zeros(1), numpy.zeros(1), numpy.zeros(1), numpy.zeros(1)
	_TC, _TCu = numpy.zeros(1), numpy.zeros(1)
	T.SetBranchAddress("TIME", _t)
	T.SetBranchAddress("TIME_OFFSET", _tO)
	if 1 in channels:
		T.SetBranchAddress("CH1", _CH1)
		T.SetBranchAddress("CH1u", _CH1u)
	if 2 in channels:
		T.SetBranchAddress("CH2", _CH2)
		T.SetBranchAddress("CH2u", _CH2u)
	if 3 in channels:
		T.SetBranchAddress("CH3", _CH3)
		T.SetBranchAddress("CH3u", _CH3u)
	if has_voltage:
		T.SetBranchAddress("Up", _Up)
		T.SetBranchAddress("Um", _Um)
		T.SetBranchAddress("Upu", _Upu)
		T.SetBranchAddress("Umu", _Umu)
	if has_temp:
		T.SetBranchAddress("TC", _TC)
		T.SetBranchAddress("TCu", _TCu)

	n = T.GetEntries()

	t, tO, Up, Um, Upu, Umu = numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n)
	CH1, CH1u, CH2, CH2u, CH3, CH3u = numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n), numpy.empty(n)
	TC, TCu = numpy.empty(n), numpy.empty(n)

	for i in range(n):
		T.GetEntry(i)
		t[i] = _t
		tO[i] = _tO
		if 1 in channels:
			CH1[i] = _CH1
			CH1u[i] = _CH1u
		if 2 in channels:
			CH2[i] = _CH2u
			CH2u[i] = _CH2u
		if 3 in channels:
			CH3[i] = _CH3
			CH3u[i] = _CH3u
		if has_voltage:
			Up[i] = _Up
			Um[i] = _Um
			Upu[i] = _Upu
			Umu[i] = _Umu
		if has_temp:
			TC[i] = _TC
			TCu[i] = _TCu

	UpUm = Up + Um
	UpuUmu = numpy.sqrt(Upu**2 + Umu**2)
	
	return {'n': n, 't': t, 'TIME_OFFSET': tO, 'CH1': CH1, 'CH2': CH2, 'CH3': CH3, 'CH1u': CH1u, 'CH2u': CH2u, 'CH3u': CH3u,
		'Up': Up, 'Um': Um, 'Upu': Upu, 'Umu': Umu, 'UpUm': UpUm, 'UpuUmu': UpuUmu, 'TC': TC, 'TCu': TCu}

