#include "SegmentedFFT.h"

#include <CVcommon/Convert.h>
#include <CVcommon/File.h>
#include <CVcommon/MathTools.h>
#include <CVcommon/String.h>
#include <CVcommon/Windows.h>

#include <iostream>
#include <string>

#include <fftw3.h>

using namespace std;
using namespace CVcommon;

SegmentedFFT::SegmentedFFT(const vector<DTYPE> *data_real, DTYPE fs, DTYPE fr, string window, DTYPE overlap, bool verbose)
	: d_real(data_real->begin(), data_real->end()), fs(fs), fr(fr), overlap(overlap), verbose(verbose)
{
	this->window = String::toupper(window);
	init();
}

SegmentedFFT::SegmentedFFT(const vector<DTYPE> *data_real, DTYPE fs, string window, DTYPE overlap, bool verbose)
	: d_real(data_real->begin(), data_real->end()), fs(fs), fr(ceil(fs / data_real->size())), overlap(overlap), verbose(verbose)
{
	this->window = String::toupper(window);
	init();
}

SegmentedFFT::~SegmentedFFT()
{
	delete[] w;
}

void SegmentedFFT::init()
{
	d_len = d_real.size();
	N = (ulong)floor(fs / fr);
	if (N > d_len) N = d_len;
	fr = fs / N;

#ifndef __QUIET_MODE__
	if (verbose)
	{
		cout << "N = " << N << " | d_len%N = " << d_len % N << endl;
		cout << "f[sampling]   = " << fs << endl;
		cout << "f[resolution] = " << fr << endl;
		cout << endl;
		cout << "using window: " << window << endl;
		cout << "with overlap: " << overlap << endl;
		cout << "------------------------------------" << endl;
	}
#endif

	w = new DTYPE[N];
	Windows<DTYPE>::Calculate_Window(window.c_str(), N, w, S1, S2);

	NENBW = N * S2 / (S1 * S1);
	ENBW = NENBW * fr;

#ifndef __QUIET_MODE__
	if (verbose)
	{
		cout << "S1 = " << S1 << endl;
		cout << "S2 = " << S2 << endl;
		cout << endl;
		cout << "Normalized Equivalent Noise Bandwith, NENBW = " << NENBW << endl;
		cout << "Effective Noise Bandwith, ENBW = " << ENBW << endl;
	}
#endif

}

void SegmentedFFT::Segmentize()
{
	for (size_t first = 0, last = N - 1; last < d_len; first += (size_t)(N*(1 - overlap)), last = first + N - 1)
	{
		d_segments.push_back(vector<FFTW_DTYPE>(N));
		for (size_t j = first, k = 0; j <= last; ++j, ++k)
		{
			(*(d_segments.end() - 1))[j - first] = d_real[j] * w[k];
		}
	}

#ifndef __QUIET_MODE__
	if (verbose)
		cout << "\nn(segments) = " << d_segments.size() << endl;
#endif
}

void SegmentedFFT::FFTExecute()
{
	/* CREATE FFT-RESULT-VECTOR */
	//d_complex.reserve(d_segments.size());
	d_avg_abs.resize((*d_segments.cbegin()).size() / 2 + 1, 0.0);

	/* PERFORM FFT:
	* > define dft_real / dft_complex
	* > copy data into dft_real
	* > set the FFTW plan
	* > execute fftw
	* > copy complex data to results-vector and calculate abs-average
	*/
	size_t s_len = (*d_segments.begin()).size(), i;
	FFTW_REAL * dft_real = new FFTW_REAL[s_len];
	FFTW_COMPLEX * dft_complex = new FFTW_COMPLEX[s_len / 2 + 1];
	FFTW_PLAN plan;
	vector<vector<DTYPE>>::const_iterator segment;

	for (segment = d_segments.cbegin(); segment != d_segments.cend(); ++segment, ++fft_count)
	{
		//d_complex.push_back(vector<complex<DTYPE>>());
		//d_complex[fft_count].reserve(s_len / 2 + 1);

		std::copy((*segment).begin(), (*segment).end(), dft_real);
		plan = FFTW_PLAN_DFT_R2C_1D(s_len, dft_real, dft_complex, FFTW_ESTIMATE);

		FFTW_EXECUTE(plan);

		for (i = 0; i < s_len / 2 + 1; ++i)
		{
			//d_complex[fft_count].push_back(complex<DTYPE>(dft_complex[i][0], dft_complex[i][1]));

			/* AVERAGING */
			d_avg_abs[i] += _abs(dft_complex[i][0], dft_complex[i][1]);
		}

		FFTW_DESTROY_PLAN(plan);
	}

	/* DIVIDE AVERAGES BY N-samples */
	for (vector<FFTW_DTYPE>::iterator it = d_avg_abs.begin(); it != d_avg_abs.end(); ++it)
		*it /= fft_count;
	
	delete[] dft_real;
	delete[] dft_complex;
}

void SegmentedFFT::resultsToByte()
{
	b_data = ConvertToByteVector(d_avg_abs);
}

vector<byte> SegmentedFFT::ToByte(char *opt)
{
	vector<byte> b_return;

	size_t i;
	byte *buf = new byte[sizeof(DTYPE)];
	vector<string> split = String::Split(string(opt), ',', false);
	//for each (string s in split)
	for (string s : split)
	{
		if (s.compare("fs") == 0) _memcpy(buf, sizeof(DTYPE), &this->fs, sizeof(DTYPE));
		else if (s.compare("fr") == 0) _memcpy(buf, sizeof(DTYPE), &this->fr, sizeof(DTYPE));
		else if (s.compare("S1") == 0) _memcpy(buf, sizeof(DTYPE), &this->S1, sizeof(DTYPE));
		else if (s.compare("S2") == 0) _memcpy(buf, sizeof(DTYPE), &this->S2, sizeof(DTYPE));
		else if (s.compare("NENBW") == 0) _memcpy(buf, sizeof(DTYPE), &this->NENBW, sizeof(DTYPE));
		else if (s.compare("ENBW") == 0) _memcpy(buf, sizeof(DTYPE), &this->ENBW, sizeof(DTYPE));
		else continue;

		for (i = 0; i < sizeof(DTYPE); b_header.push_back(buf[i++]));
	}
	delete[] buf;

	resultsToByte();

	b_return.assign(b_header.begin(), b_header.end());
	b_return.reserve(b_return.size() + b_data.size());
	b_return.insert(b_return.end(), b_data.begin(), b_data.end());

	return b_return;
}