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
	size_t crop_group;
	DTYPE fs, fl;
	// CALCULATED/OTHERS
	DTYPE fn, ft;

	// INPUT - DECLARATION
	crop_group = 1;

#ifndef DEBUG
	if (argc < 4)
	{
		if (argc > 1)
		{
			if (!strcmp(argv[1], "help"))
			{
				cerr << "Not enough arguments provided!" << endl;
				cerr << "> " << argv[0] << " ifile fsample flock [crop_group] [ftrans]" << endl;
			}
		}
		return -1;
	}
	ifname = argv[1];
	fs = (DTYPE)atof(argv[2]);
	fl = (DTYPE)atof(argv[3]);
	if (argc > 4)
		ft = (DTYPE)atof(argv[4]);
	else
		ft = (DTYPE)(0.001);
	if (argc > 5) crop_group = (size_t)atoi(argv[5]);
#else
	ifname = (char *)"D:\\Users\\Christian Velten\\Dropbox\\dev\\PSD-DFT\\RecWvfm_0001.bin";
	fs = 250000.0f;
	fl = 1.0f;
#endif
	fn = fs / 2;

	if (!File::Exists(ifname))
	{
		cerr << "Input file was not found!\n\t" << "'" << ifname << "'" << endl;
		return -1;
	}

	WaveformHeader hdr;
	vector<byte> bdata = File::ReadBINARY(ifname);
	vector<DTYPE> vdata;
	ConvertRecordedWaveform<DTYPE>(bdata, vdata, hdr);

	vdata = CropData(vdata, crop_group);
	hdr.N /= crop_group;
	fs /= crop_group;

	size_t i;
	vector<DTYPE> _fl, _Ravg, _PH;

	const size_t n = 1;
	const DTYPE fl_low = (DTYPE)(0.8 * fl), fl_high = (DTYPE)(1.2 * fl);
	//
	vector<LockInReturn<DTYPE>> rt(n);
	rt.reserve(n);
	for (i = 0; i < n; ++i)
	{
		DTYPE tmp_fl = (fl_high - fl_low)*i / (DTYPE)n + fl_low;
		rt[i] = LockIn<DTYPE>::CalculateLock(vdata, hdr, fs, tmp_fl, ft);
	}

	_fl.resize(n);
	_Ravg.resize(n);
	_PH.resize(n);
	for (i = 0; i < n; ++i)
	{
		_fl[i] = rt[i].flock;
		_Ravg[i] = rt[i].Ravg;
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
