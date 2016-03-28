#pragma once
#ifndef __CVc__SEGMENTEDFFT_H
#define __CVc__SEGMENTEDFFT_H

#include "CVcommon.h"
#include "Convert.h"
#include "String.h"
#include "Windows.h"

#include <cassert>
#include <complex>
#include <typeinfo>
#include <vector>

#include <fftw3.h>

namespace CVcommon
{
	template <typename T>
	class SegmentedFFT
	{
	public:
		SegmentedFFT(const std::vector<T> *data_real, T fs, T fr, std::string window = "HANNING", T overlap = 0.0f, bool verbose = true);
		SegmentedFFT(const std::vector<T> *data_real, T fs, std::string window = "HANNING", T overlap = 0.0f, bool verbose = true);
		SegmentedFFT(const std::vector<T> *data_real, T fs, T fr, WINDOW_TYPE window = WINDOW_TYPE::HANNING, T overlap = 0.0f, bool verbose = true);
		SegmentedFFT(const std::vector<T> *data_real, T fs, WINDOW_TYPE window = WINDOW_TYPE::HANNING, T overlap = 0.0f, bool verbose = true);
		~SegmentedFFT();

	private:
		std::vector<T> d_real;
		T fs, fr;
		std::string swindow;
		WINDOW_TYPE window;
		T overlap;
		bool verbose = true;

		uint fft_count = 0;
		ulong N;
		size_t d_len;
		std::vector<std::vector<T>> d_segments;
		std::vector<std::vector<std::complex<T>>> d_complex;
		std::vector<T> d_avg_abs;
		std::vector<byte> b_header, b_data;

		T *w;
		T S1, S2, NENBW, ENBW;

		SegmentedFFT();
		void init();
		void resultsToByte();

	public:
		void Segmentize();
		//void SegmentizeIT();
		void FFTExecute();
		std::vector<byte> ToByte();

		const std::vector<T> & GetDataReal() const { return this->d_real; }
		void SetDataReal(std::vector<T> d) { this->d_real.assign(d.begin(), d.end()); }
		const std::vector<std::vector<std::complex<T>>> & GetDataComplex() const { return this->d_complex; }
		const std::vector<T> & GetDataAvgAbs() const { return this->d_avg_abs; }

		const std::string & GetWindow() const { return this->window; }
		void SetWindow(std::string window) { this->window = window; }
		const T GetOverlap() const { return this->overlap; }
		void SetOverlap(T overlap) { this->overlap = overlap; }

		T fResolution(T val = 0) { if (val > 0)this->fr = val; return this->fr; }
		T fSampling(T val = 0) { if (val > 0)this->fs = val; return this->fs; }
		const T GetS1() const { return this->S1; }
		const T GetS2() const { return this->S2; }
		const T GetNENBW() const { return this->NENBW; }
		const T GetENBW() const { return this->ENBW; }
		const uint Nffts() const { return this->fft_count; }
		void Verbose(bool verbose = true) { this->verbose = verbose; }
	};

	template <typename T>
	SegmentedFFT<T>::SegmentedFFT(const std::vector<T> *data_real, T fs, T fr, std::string window, T overlap, bool verbose)
		: d_real(data_real->begin(), data_real->end()), fs(fs), fr(fr), overlap(overlap), verbose(verbose)
	{
		this->swindow = String::toupper(window);
		this->window = Windows<T>::ParseWindowType(this->swindow.c_str());
		init();
	}
	template <typename T>
	SegmentedFFT<T>::SegmentedFFT(const std::vector<T> *data_real, T fs, std::string window, T overlap, bool verbose)
		: d_real(data_real->begin(), data_real->end()), fs(fs), fr(ceil(fs / data_real->size())), overlap(overlap), verbose(verbose)
	{
		this->swindow = String::toupper(window);
		this->window = Windows<T>::ParseWindowType(this->swindow.c_str());
		init();
	}
	template <typename T>
	SegmentedFFT<T>::SegmentedFFT(const std::vector<T> *data_real, T fs, T fr, WINDOW_TYPE window, T overlap, bool verbose)
		: d_real(data_real->begin(), data_real->end()), fs(fs), fr(fr), overlap(overlap), verbose(verbose)
	{
		this->window = window;
		init();
	}
	template <typename T>
	SegmentedFFT<T>::SegmentedFFT(const std::vector<T> *data_real, T fs, WINDOW_TYPE window, T overlap, bool verbose)
		: d_real(data_real->begin(), data_real->end()), fs(fs), fr(ceil(fs / data_real->size())), overlap(overlap), verbose(verbose)
	{
		this->window = window;
		init();
	}

	template <typename T>
	SegmentedFFT<T>::~SegmentedFFT()
	{
		delete[] w;
	}

	template <typename T>
	void SegmentedFFT<T>::init()
	{
		d_len = d_real.size();
		N = (ulong)floor(fs / fr);
		if (N > d_len) N = d_len;
		fr = fs / N;

		if (verbose)
		{
			cout << "N = " << N << " | d_len%N = " << d_len % N << endl;
			cout << "f[sampling]   = " << fs << endl;
			cout << "f[resolution] = " << fr << endl;
			cout << endl;
			cout << "using window: " << swindow << endl;
			cout << "with overlap: " << overlap << endl;
			cout << "------------------------------------" << endl;
		}

		w = new T[N];
		Windows<T>::Calculate_Window(window, N, w, S1, S2);

		NENBW = N * S2 / (S1 * S1);
		ENBW = NENBW * fr;

		if (verbose)
		{
			cout << "S1 = " << S1 << endl;
			cout << "S2 = " << S2 << endl;
			cout << endl;
			cout << "Normalized Equivalent Noise Bandwith, NENBW = " << NENBW << endl;
			cout << "Effective Noise Bandwith, ENBW = " << ENBW << endl;
		}
	}

	template <typename T>
	void SegmentedFFT<T>::Segmentize()
	{
		for (size_t first = 0, last = N - 1; last < d_len; first += (size_t)(N*(1 - overlap)), last = first + N - 1)
		{
			d_segments.push_back(std::vector<T>(N));
			for (size_t j = first, k = 0; j <= last; ++j, ++k)
			{
				(*(d_segments.end() - 1))[j - first] = d_real[j] * w[k];
			}
		}

		if (verbose)
			cout << "\nn(segments) = " << d_segments.size() << endl;
	}

	template <typename T>
	void SegmentedFFT<T>::FFTExecute()
	{
		static_assert(std::is_floating_point<T>::value, "FILTER may only take floating points as type!");
		assert(typeid(T).hash_code() == typeid(float).hash_code() || typeid(T).hash_code() == typeid(double).hash_code());

		// typedef for fftw_complex
		typedef T T2[2];

		/* CREATE FFT-RESULT-VECTOR */
		d_avg_abs.resize((*d_segments.cbegin()).size() / 2 + 1, 0);

		/* PERFORM FFT:
		* > define dft_real / dft_complex
		* > copy data into dft_real
		* > set the FFTW plan
		* > execute fftw
		* > copy complex data to results-vector and calculate abs-average
		*/
		size_t s_len = (*d_segments.begin()).size(), i;
		T * dft_real = new T[s_len];
		T2 * dft_complex = new T2[s_len / 2 + 1];

		std::vector<std::vector<T>>::const_iterator segment;

		for (segment = d_segments.cbegin(); segment != d_segments.cend(); ++segment, ++fft_count)
		{
			//d_complex.push_back(std::vector<complex<T>>());
			//d_complex[fft_count].reserve(s_len / 2 + 1);

			std::copy((*segment).begin(), (*segment).end(), dft_real);

			if (typeid(T).hash_code() == typeid(float).hash_code())
			{
				fftwf_plan plan = fftwf_plan_dft_r2c_1d(s_len, dft_real, dft_complex, FFTW_ESTIMATE);
				fftwf_execute(plan);
				fftwf_destroy_plan(plan);
			}
			else
			{
				fftw_plan plan = fftw_plan_dft_r2c_1d(s_len, (double*)dft_real, (fftw_complex*)dft_complex, FFTW_ESTIMATE);
				fftw_execute(plan);
				fftw_destroy_plan(plan);
			}

			for (i = 0; i < s_len / 2 + 1; ++i)
			{
				//d_complex[fft_count].push_back(complex<T>(dft_complex[i][0], dft_complex[i][1]));

				/* AVERAGING */
				d_avg_abs[i] += _abs(dft_complex[i][0], dft_complex[i][1]);
			}
		}

		/* DIVIDE AVERAGES BY N-samples */
		for (std::vector<T>::iterator it = d_avg_abs.begin(); it != d_avg_abs.end(); ++it)
			*it /= fft_count;

		delete[] dft_real;
		delete[] dft_complex;
	}

	template <typename T>
	void SegmentedFFT<T>::resultsToByte()
	{
		b_data = ConvertToByteVector(d_avg_abs);
	}

	template <typename T>
	std::vector<byte> SegmentedFFT<T>::ToByte()
	{
		std::vector<byte> b_return;

		size_t i;
		byte *buf = new byte[sizeof(T)];

		const char *opt = (char *)"fs,fr,S1,S2,NENBW,ENBW,WINDOW_TYPE";
		std::vector<string> split = String::Split(string(opt), ',', false);

		for (string s : split)
		{
			if (s.compare("fs") == 0) _memcpy(buf, sizeof(T), &this->fs, sizeof(T));
			else if (s.compare("fr") == 0) _memcpy(buf, sizeof(T), &this->fr, sizeof(T));
			else if (s.compare("S1") == 0) _memcpy(buf, sizeof(T), &this->S1, sizeof(T));
			else if (s.compare("S2") == 0) _memcpy(buf, sizeof(T), &this->S2, sizeof(T));
			else if (s.compare("NENBW") == 0) _memcpy(buf, sizeof(T), &this->NENBW, sizeof(T));
			else if (s.compare("ENBW") == 0) _memcpy(buf, sizeof(T), &this->ENBW, sizeof(T));
			/*
			else if (s.compare("WINDOW_TYPE") == 0)
			{
				T type = static_cast<T>(this->window);
				_memcpy(buf, sizeof(uint), &type, sizeof(uint));
			}
			*/
			else continue;

			for (i = 0; i < sizeof(T); b_header.push_back(buf[i++]));
		}
		delete[] buf;

		resultsToByte();

		b_return.assign(b_header.begin(), b_header.end());
		b_return.reserve(b_return.size() + b_data.size());
		b_return.insert(b_return.end(), b_data.begin(), b_data.end());

		return b_return;
	}

}

#endif