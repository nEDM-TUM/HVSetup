#include "stdhdr.h"

#include <CVcommon/Algorithm.h>
#include <CVcommon/CVcommon.h>
#include <CVcommon/Convert.h>
#include <CVcommon/File.h>
#include <CVcommon/Filters.h>
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
	DTYPE fs, ft, ftwidth;
	// CALCULATED/OTHERS
	DTYPE fn;
	ftwidth = 1;

	// INPUT - DECLARATION
	crop_group = 1;

	if (argc < 4)
	{
		if (argc > 1)
		{
			if (!strcmp(argv[1], "help"))
			{
				cerr << "Not enough arguments provided!" << endl;
				cerr << "> " << argv[0] << " ifile fsample ftrans [ftwidth=1Hz] [crop_group]" << endl;
			}
		}
		return -1;
	}
	ifname = argv[1];
	fs = (DTYPE)atof(argv[2]);
	ft = (DTYPE)atof(argv[3]);
	if (argc > 4) ftwidth = (DTYPE)atof(argv[4]);
	if (argc > 5) crop_group = (size_t)atoi(argv[5]);

	fn = fs / 2;

	if (!File::Exists(ifname))
	{
		cerr << "Input file was not found!\n\t" << "'" << ifname << "'" << endl;
		return -1;
	}

	vector<DTYPE> vdata, vout;
	vector<byte> bdata, bout;

	WaveformHeader hdr;
	bdata = File::ReadBINARY(ifname);
	ConvertRecordedWaveform<DTYPE>(bdata, vdata, hdr);

	vdata = CropData(vdata, crop_group);
	hdr.N /= crop_group;
	fs /= crop_group;

	DTYPE S1 = 0, S2 = 0;
	DTYPE *out = new DTYPE[hdr.N];

	Filters<DTYPE>::BandPass(hdr.N, vdata.data(), out, ft, ftwidth, fs, S1, S2, WINDOW_TYPE::HAMMING);

	vout.reserve(2 + hdr.N);

	vout.push_back(ft);
	vout.push_back(ftwidth);
	vout.insert(vout.end(), out, out + hdr.N);

	bout = ConvertToByteVector(vout);
	File::WriteBINARY(String::ReplaceExtension(ifname, "bin.bandpass").c_str(), bout);

	delete[] out;
	return 0;
}
