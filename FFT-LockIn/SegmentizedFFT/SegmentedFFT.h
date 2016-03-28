#pragma once
#ifndef SegmentedFFT_H
#define SegmentedFFT_H

#include "stdhdr.h"

#include <CVcommon/CVcommon.h>

#include <complex>
#include <vector>

using namespace CVcommon;

class SegmentedFFT
{
public:
	SegmentedFFT(const std::vector<DTYPE> *data_real, DTYPE fs, DTYPE fr, std::string window = "HANNING", DTYPE overlap = 0.0f, bool verbose = true);
	SegmentedFFT(const std::vector<DTYPE> *data_real, DTYPE fs, std::string window = "HANNING", DTYPE overlap = 0.0f, bool verbose = true);
	~SegmentedFFT();

private:
	std::vector<DTYPE> d_real;
	DTYPE fs, fr;
	std::string window;
	DTYPE overlap;
	bool verbose = true;

	uint fft_count = 0;
	ulong N;
	size_t d_len;
	std::vector<std::vector<DTYPE>> d_segments;
	std::vector<std::vector<std::complex<DTYPE>>> d_complex;
	std::vector<DTYPE> d_avg_abs;
	std::vector<byte> b_header, b_data;

	DTYPE *w;
	DTYPE S1, S2, NENBW, ENBW;

	SegmentedFFT();
	void init();
	void resultsToByte();

public:
	void Segmentize();
	void SegmentizeIT();
	void FFTExecute();
	std::vector<byte> ToByte(char *opt = (char *)"fs,fr,S1,S2,NENBW,ENBW");

	const std::vector<DTYPE> & GetDataReal() const { return this->d_real; }
	void SetDataReal(std::vector<DTYPE> d) { this->d_real.assign(d.begin(), d.end()); }
	const std::vector<std::vector<std::complex<DTYPE>>> & GetDataComplex() const { return this->d_complex; }
	//void SetDataComplex(std::vector<std::complex<DTYPE>> d) { this->d_complex.assign(d.begin(), d.end()); }
	const std::vector<DTYPE> & GetDataAvgAbs() const { return this->d_avg_abs; }

	const std::string & GetWindow() const { return this->window; }
	void SetWindow(std::string window) { this->window = window; }
	const DTYPE GetOverlap() const { return this->overlap; }
	void SetOverlap(DTYPE overlap) { this->overlap = overlap; }

	DTYPE fResolution(DTYPE val = 0) { if (val > 0)this->fr = val; return this->fr; }
	DTYPE fSampling(DTYPE val = 0) { if (val > 0)this->fs = val; return this->fs; }
	const DTYPE GetS1() const { return this->S1; }
	const DTYPE GetS2() const { return this->S2; }
	const DTYPE GetNENBW() const { return this->NENBW; }
	const DTYPE GetENBW() const { return this->ENBW; }
	const uint Nffts() const { return this->fft_count; }
	void Verbose(bool verbose = true) { this->verbose = verbose; }
};

#endif