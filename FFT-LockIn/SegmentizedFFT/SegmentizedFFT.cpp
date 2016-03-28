#include "stdhdr.h"

#include <CVcommon/CVcommon.h>
#include <CVcommon/Convert.h>
#include <CVcommon/File.h>
#include <CVcommon/MathTools.h>
#include <CVcommon/SegmentedFFT.h>
#include <CVcommon/Windows.h>
#include <CVcommon/Waveform.h>

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <algorithm>
#include <cmath>
#include <functional>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

using namespace std;
using namespace CVcommon;

int main(int argc, char *argv[], char *envp[])
{
	char *ifname;
	DTYPE fs, fr;
	string window = "HAMMING";

	if (argc < 4)
	{
		cerr << "Not enough arguments provided!" << endl;
		cerr << "> " << argv[0] << " ifile fsample fresolution [window]" << endl;
		return -1;
	}
	ifname = argv[1];
	fs = (DTYPE)atof(argv[2]);
	fr = (DTYPE)atof(argv[3]);
	if (argc >= 5) window = string(argv[4]);
	String::toupper(window);

	const WINDOW_TYPE wdw_type = Windows<DTYPE>::ParseWindowType(window.c_str());
	const float wdw_overlap = Windows<DTYPE>::IdealOverlap(wdw_type);

	// READ DATA AND CONVERT IT
	vector<byte> data_byte = File::ReadBINARY(ifname);

	WaveformHeader header;
	std::vector<DTYPE> data;
	ConvertRecordedWaveform(data_byte, data, header);

	// subtract the data-mean to reduce DC-impact
	DTYPE mean, stdev;
	{
		mean = std::accumulate(data.begin(), data.end(), (DTYPE)0.0) / data.size();

		std::vector<DTYPE> diff(data.size());
		std::transform(data.begin(), data.end(), diff.begin(), std::bind2nd(std::minus<DTYPE>(), mean));
		DTYPE sq_sum = std::inner_product(diff.begin(), diff.end(), diff.begin(), (DTYPE)0);
		stdev = std::sqrt(sq_sum / data.size());

		std::transform(data.begin(), data.end(), data.begin(), std::bind1st(std::minus<DTYPE>(), mean));
	}
#ifndef __QUIET_MODE__
	cout << "DATA ..." << endl;
	cout << "- MEAN: " << mean << endl;
	cout << "- STD : " << stdev << endl;
	cout << endl;
#endif

	SegmentedFFT<DTYPE> *fft = new SegmentedFFT<DTYPE>(&data, fs, fr, window, wdw_overlap, true);
	fft->Verbose(true);
	fft->Segmentize();
	fft->FFTExecute();

	// Create byte vector with header info + data
	vector<byte> fft_byte = fft->ToByte();

	File::WriteBINARY(String::ReplaceExtension(ifname, "bin.out").c_str(), fft_byte);

	return 0;
}
