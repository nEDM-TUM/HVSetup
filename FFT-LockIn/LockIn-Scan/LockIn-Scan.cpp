#include "stdhdr.h"

#include <CVcommon/Algorithm.h>
#include <CVcommon/CVcommon.h>
#include <CVcommon/Convert.h>
#include <CVcommon/File.h>
#include <CVcommon/Filters.h>
#include <CVcommon/LockIn.h>
#include <CVcommon/MathTools.h>
#include <CVcommon/Windows.h>
#include <CVcommon/Waveform.h>

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>
#include <complex>
#include <iostream>
#include <vector>

#include <fftw3.h>

using namespace std;
using namespace CVcommon;

int main(int argc, char *argv[])
{
	// INPUT
	char *ifname;
	size_t crop_group = 1;
	DTYPE fs, ft = -1, fn;
	// CALCULATED/OTHERS
	DTYPE fl_low = -1, fl_high = -1, fl_res = -1;

	if (argc < 3)
	{
		cerr << "Not enough arguments provided!" << endl;
		cerr << "> " << argv[0] << " ifile fsample [lock_min] [lock_max] [lock_resolution] [crop_group] [ftrans]" << endl;
		return -1;
	}
	ifname = argv[1];
	fs = (DTYPE)atof(argv[2]);
	if (argc > 3) fl_low = (DTYPE)atof(argv[3]);
	if (argc > 4) fl_high = (DTYPE)atof(argv[4]);
	if (argc > 5) fl_res = (DTYPE)atof(argv[5]);
	if (argc > 6) crop_group = (size_t)atoi(argv[6]);
	if (crop_group < 1) crop_group = 1;
	if (argc > 7) ft = (DTYPE)atof(argv[7]);
	if (ft <= 0) ft = (DTYPE)0.1;

	if (!File::Exists(ifname))
	{
		cerr << "Input file was not found!\n\t" << "'" << ifname << "'" << endl;
		return -1;
	}

	WaveformHeader hdr;
	vector<byte> bdata = File::ReadBINARY(ifname);
	vector<DTYPE> vdata;
	ConvertRecordedWaveform<DTYPE>(bdata, vdata, hdr);

	cout << "Crop by: " << crop_group << endl;
	vdata = CropData(vdata, crop_group);
	hdr.N /= crop_group;
	fs /= crop_group;
	fn = fs / 2;

	size_t i;
	vector<DTYPE> _fl, _Ravg, _PH;

	if (fl_res <= 0) fl_res = (DTYPE)(fn / hdr.N * 100) * crop_group;
	if (fl_low < 0)	fl_low = (DTYPE)(fs / hdr.N);
	if (fl_high < 0) fl_high = (DTYPE)(fn);
	const size_t n = (size_t)((fl_high - fl_low) / fl_res) + 1;
	
	vector<LockInReturn<DTYPE>> rt;
	rt.reserve(n);

	cout << "Performing LockIn calculation n=" << n << " times from " << fl_low << "Hz to " << fl_high << "Hz in " << fl_res << "Hz intervals with " << ft << " ftrans" << endl;
	cout << "\t";
	
	for (i = 0; i < n; ++i)
	{
		DTYPE tmp_fl = i * fl_res + fl_low;
		rt.push_back(LockIn<DTYPE>::CalculateLock(vdata, hdr, fs, tmp_fl, ft, false));
		if (n >= 10 && (i + 1) % (n / 10) == 0)
			cout << (size_t)ceil(100 * (double)i / (double)n) << "%  ";
	}

	_fl.resize(n);
	_Ravg.resize(n);
	_PH.resize(n);
	for (i = 0; i < n; ++i)
	{
		_fl[i] = rt[i].flock;
		_Ravg[i] = rt[i].Ravg  / (DTYPE)hdr.N;
		_PH[i] = rt[i].PHASE;
	}

	vector<byte> bout;
	vector<DTYPE> fout;
	fout.assign(_fl.begin(), _fl.end());
	fout.insert(fout.end(), _Ravg.begin(), _Ravg.end());
	fout.insert(fout.end(), _PH.begin(), _PH.end());
	bout = ConvertToByteVector(fout);
	File::WriteBINARY(String::ReplaceExtension(ifname, "bin.lock").c_str(), bout);

	return 0;
}
