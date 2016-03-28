/**
CVcommon
Filters.h
Purpose: Provide functions for filters (Low-/High-Pass, Band-Pass and Band-Stop).

@author Christian Velten
@version 1.0 07/18/2015
*/
#pragma once
#ifndef __CVc_FILTERS_H
#define __CVc_FILTERS_H

#include "CVcommon.h"
#include "Windows.h"

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cassert>
#include <cmath>
#include <typeinfo>

#include <fftw3.h>

namespace CVcommon
{
	enum class FILTER_TYPE { NONE, LOW_PASS, HIGH_PASS, BAND_PASS, BAND_STOP };

	static const size_t MINIMUM_FFT_LEN = 2048;

	/**
		Provides static member functions for filtering data.
	*/
	template<typename T>
	class Filters
	{
	private:

	public:
		/**
			Calculate window values for a sinc(x)=sin(x)/x function.

			@param len length of the window
			@param freq_trans the sinc frequency, corresponds to transmission frequency
			@param freq_sample the data sample frequency
			@param type the filter type, can be low- or high-pass.
			@return pointer to output array
		*/
		static T * SINC1(size_t &, const T &freq_trans, const T &freq_sample, const FILTER_TYPE);
		/**
			Calculate window values for the difference of two sinc(x)=sin(x)/x functions.

			@param len length of the window
			@param freq_trans1 the first sinc frequency, corresponds to first transmission frequency
			@param freq_trans2 the second sinc frequency, corresponds to second transmission frequency
			@param freq_sample the data sample frequency
			@param type the filter type, can be low- or high-pass.
			@return pointer to the output array
		*/
		static T * SINC2(size_t &, const T &freq_trans1, const T &freq_trans2, const T &freq_sample, const FILTER_TYPE);
		/**
			@param len length of the window
			@param freq_trans the sinc frequency, corresponds to transmission frequency
			@param freq_sample the data sample frequency
			@param type the filter type, can be low- or high-pass.
			@param w the output array (initialized)
			@return true if success, false if failed
		*/
		static bool SINC1(size_t &, const T &freq_trans, const T &freq_sample, const FILTER_TYPE, T *);
		/**
			@param len length of the window
			@param freq_trans1 the first sinc frequency, corresponds to first transmission frequency
			@param freq_trans2 the second sinc frequency, corresponds to second transmission frequency
			@param freq_sample the data sample frequency
			@param type the filter type, can be low- or high-pass.
			@param w the output array (initialized)
			@return true if success, false if failed
		*/
		static bool SINC2(size_t &, const T &freq_trans1, const T &freq_trans2, const T &freq_sample, const FILTER_TYPE, T *);

		/**
			LOW-Pass filters the input data, i.e. suppresses frequencies higher than the transmission frequency.

			@param len the length of input and output array
			@param in pointer to the input data (initialized!)
			@param out pointer to the output data (initialized!)
			@param ft the transmission frequency
			@param fs the data's sampling frequency
			@param S1 first window scaling value
			@param S2 second window scaling value
			@param tWindow the window type to use prior to the DFT
			@param wdw_output if not nullptr, will contain the calculated window values over the data range
			@param fft_output if not nullptr, will countain the result of the DFT (scaled) with length len/2+1
		*/
		static void LowPass(size_t &len, const T *in, T *out, const T &ft, const T &fs, T &S1, T &S2, const WINDOW_TYPE tWindow = WINDOW_TYPE::HAMMING, T *wdw_output = nullptr, T *fft_output = nullptr);
		/**
			HIGH-Pass filters the input data, i.e. suppresses frequencies lower than the transmission frequency.

			@param len the length of input and output array
			@param in pointer to the input data (initialized!)
			@param out pointer to the output data (initialized!)
			@param ft the transmission frequency
			@param fs the data's sampling frequency
			@param S1 first window scaling value
			@param S2 second window scaling value
			@param tWindow the window type to use prior to the DFT
			@param wdw_output if not nullptr, will contain the calculated window values over the data range
			@param fft_output if not nullptr, will countain the result of the DFT (scaled) with length len/2+1
		*/
		static void HighPass(size_t &len, const T *in, T *out, const T &ft, const T &fs, T &S1, T &S2, const WINDOW_TYPE tWindow = WINDOW_TYPE::HAMMING, T *wdw_output = nullptr, T *fft_output = nullptr);
		/**
		BAND-Pass filters the input data, i.e. transmits one frequency (+/- width)

		@param len the length of input and output array
		@param in pointer to the input data (initialized!)
		@param out pointer to the output data (initialized!)
		@param ft the transmission frequency
		@param ftwidth the bandwith for transmission
		@param fs the data's sampling frequency
		@param S1 first window scaling value
		@param S2 second window scaling value
		@param tWindow the window type to use prior to the DFT
		@param wdw_output if not nullptr, will contain the calculated window values over the data range
		@param fft_output if not nullptr, will countain the result of the DFT (scaled) with length len/2+1
		*/
		static void BandPass(size_t &len, const T *in, T *out, const T &ft, const T &ftwidth, const T &fs, T &S1, T &S2, const WINDOW_TYPE tWindow = WINDOW_TYPE::HAMMING, T *wdw_output = nullptr, T *fft_output = nullptr);
		/**
		BAND-Stop filters the input data, i.e. suppresses one frequency (+/- width)

		@param len the length of input and output array
		@param in pointer to the input data (initialized!)
		@param out pointer to the output data (initialized!)
		@param ft the suppression frequency
		@param ftwidth the bandwith for suppression
		@param fs the data's sampling frequency
		@param S1 first window scaling value
		@param S2 second window scaling value
		@param tWindow the window type to use prior to the DFT
		@param wdw_output if not nullptr, will contain the calculated window values over the data range
		@param fft_output if not nullptr, will countain the result of the DFT (scaled) with length len/2+1
		*/
		static void BandStop(size_t &len, const T *in, T *out, const T &ft, const T &ftwidth, const T &fs, T &S1, T &S2, const WINDOW_TYPE tWindow = WINDOW_TYPE::HAMMING, T *wdw_output = nullptr, T *fft_output = nullptr);

	private:
		/**
			(private) General filter function that takes the most general list of arguments, including filter type. For parameter description see specialized filter functions above.
		*/
		static void FILTER(size_t &len, const T *in, T *out, const T &ft1, const T &ft2, const T &fs, T &S1, T &S2, const FILTER_TYPE tFilter, const WINDOW_TYPE tWindow, T *wdw_output, T *fft_output);
	};

	/*
	* TEMPLATE MEMBER FUNCTIONS -- DEFINITIONS
	*/
	template <typename T>
	void Filters<T>::LowPass(size_t &len, const T *in, T *out, const T &ft, const T &fs, T &S1, T &S2, const WINDOW_TYPE tWindow, T *wdw_output, T *fft_output)
	{
		T ft2 = 0;
		Filters<T>::FILTER(len, in, out, ft, ft2, fs, S1, S2, FILTER_TYPE::LOW_PASS, tWindow, wdw_output, fft_output);
	}
	template <typename T>
	void Filters<T>::HighPass(size_t &len, const T *in, T *out, const T &ft, const T &fs, T &S1, T &S2, const WINDOW_TYPE tWindow, T *wdw_output, T *fft_output)
	{
		T ft2 = 0;
		Filters<T>::FILTER(len, in, out, ft, ft2, fs, S1, S2, FILTER_TYPE::HIGH_PASS, tWindow, wdw_output, fft_output);
	}

	template <typename T>
	void Filters<T>::BandPass(size_t &len, const T *in, T *out, const T &ft, const T &ftwidth, const T &fs, T &S1, T &S2, const WINDOW_TYPE tWindow, T *wdw_output, T *fft_output)
	{
		T ft1 = ft - (T)0.5 * ftwidth;
		T ft2 = ft + (T)0.5 * ftwidth;
		Filters<T>::FILTER(len, in, out, ft1, ft2, fs, S1, S2, FILTER_TYPE::BAND_PASS, tWindow, wdw_output, fft_output);
	}
	template <typename T>
	void Filters<T>::BandStop(size_t &len, const T *in, T *out, const T &ft, const T &ftwidth, const T &fs, T &S1, T &S2, const WINDOW_TYPE tWindow, T *wdw_output, T *fft_output)
	{
		T ft1 = ft - (T)0.5 * ftwidth;
		T ft2 = ft + (T)0.5 * ftwidth;
		Filters<T>::FILTER(len, in, out, ft1, ft2, fs, S1, S2, FILTER_TYPE::BAND_STOP, tWindow, wdw_output, fft_output);
	}

	template <typename T>
	void Filters<T>::FILTER(size_t &len, const T *in, T *out, const T &ft1, const T &ft2, const T &fs, T &S1, T &S2, const FILTER_TYPE tFilter, const WINDOW_TYPE tWindow, T *wdw_output, T *fft_output)
	{
		static_assert(std::is_floating_point<T>::value, "FILTER may only take floating points as type!");
		assert(typeid(T).hash_code() == typeid(float).hash_code() || typeid(T).hash_code() == typeid(double).hash_code());

		// typedef for fftw_complex
		typedef T T2[2];

		size_t i, wdw_len, fft_len, fft_hlen;
		T *wdw_sinc, *wdw_window, *wdw, *dft_r2c_in, *dft_c2r_out;
		T2 *wdw_out, *dft_r2c_out, *dft_c2r_in;

		wdw_len = len;

		if (tFilter == FILTER_TYPE::LOW_PASS || tFilter == FILTER_TYPE::HIGH_PASS)
			wdw_sinc = Filters<T>::SINC1(wdw_len, ft1, fs, tFilter);
		else if (tFilter == FILTER_TYPE::BAND_PASS || tFilter == FILTER_TYPE::BAND_STOP)
			wdw_sinc = Filters<T>::SINC2(wdw_len, ft1, ft2, fs, tFilter);
		else
			wdw_sinc = nullptr;
		wdw_window = Windows<T>::Calculate_Window(tWindow, wdw_len, S1, S2);

		fft_len = (len < 2048) ? 2048 : len;
		fft_hlen = fft_len / 2 + 1;

		// resize the input arrays
		if (len < fft_len)
		{
			delete[len] out;
			out = new T[fft_len];
			if (wdw_output != nullptr)
			{
				delete[] wdw_output;
				wdw_output = new T[fft_hlen];
			}
			if (fft_output != nullptr)
			{
				delete[] fft_output;
				fft_output = new T[fft_hlen];
			}

			T *tmp_in = new T[fft_len];
			_memcpy(tmp_in, in, len*sizeof(T));
			for (i = len; i < fft_len; ++i) tmp_in[i] = 0;
			in = tmp_in;
		}

		wdw = new T[fft_len];
		wdw_out = new T2[fft_hlen];
		dft_r2c_in = new T[fft_len];
		dft_r2c_out = new T2[fft_hlen];
		dft_c2r_in = new T2[fft_hlen];
		dft_c2r_out = new T[fft_len];

		// wdw_sinc * wdw_window
		for (i = 0; i < wdw_len; ++i) wdw[i] = wdw_sinc[i] * wdw_window[i];
		for (; i < fft_len; ++i) wdw[i] = 0;

		// free up some space
		if (tFilter != FILTER_TYPE::NONE)
			delete[] wdw_sinc;
		wdw_sinc = nullptr;
		delete[] wdw_window; wdw_window = nullptr;


		if (tFilter != FILTER_TYPE::NONE)
		{
			// R2C: window
			if (typeid(T).hash_code() == typeid(float).hash_code())
			{
				fftwf_plan plan = fftwf_plan_dft_r2c_1d(fft_len, wdw, wdw_out, FFTW_ESTIMATE);
				fftwf_execute(plan);
				fftwf_destroy_plan(plan);
			}
			else
			{
				fftw_plan plan = fftw_plan_dft_r2c_1d(fft_len, (double*)wdw, (fftw_complex*)wdw_out, FFTW_ESTIMATE);
				fftw_execute(plan);
				fftw_destroy_plan(plan);
			}
		}
		else
		{
			for (i = 0; i < fft_hlen; ++i)
			{
				wdw_out[i][0] = 1.0f;
				wdw_out[i][1] = 0;
			}
		}

		if (wdw_output != nullptr)
			for (i = 0; i < fft_hlen; ++i)
				wdw_output[i] = sqrt(wdw_out[i][0] * wdw_out[i][0] + wdw_out[i][1] * wdw_out[i][1]);

		// R2C
		_memcpy(dft_r2c_in, in, len*sizeof(T));
		for (i = len; i < fft_len; ++i) dft_r2c_in[i] = 0;

		if (typeid(T).hash_code() == typeid(float).hash_code())
		{
			fftwf_plan plan = fftwf_plan_dft_r2c_1d(fft_len, dft_r2c_in, dft_r2c_out, FFTW_ESTIMATE);
			fftwf_execute(plan);
			fftwf_destroy_plan(plan);
		}
		else
		{
			fftw_plan plan = fftw_plan_dft_r2c_1d(fft_len, (double*)dft_r2c_in, (fftw_complex*)dft_r2c_out, FFTW_ESTIMATE);
			fftw_execute(plan);
			fftw_destroy_plan(plan);
		}

		T wdw_abs;
		// CONVOLUTE === MULTIPLY
		for (i = 0; i < fft_hlen; ++i)
		{
			// sqrt(2) to keep |z'|=sqrt(x'^2+y'^2)=|wdw|*|z|
			wdw_abs = sqrt(wdw_out[i][0] * wdw_out[i][0] + wdw_out[i][1] * wdw_out[i][1]) / (DTYPE)sqrt(2);
			dft_c2r_in[i][0] = dft_r2c_out[i][0] * wdw_abs; // unscaled
			dft_c2r_in[i][1] = dft_r2c_out[i][1] * wdw_abs; // unscaled

			//dft_c2r_in[i][0] = dft_r2c_out[i][0] * wdw_abs * (T)(std::sqrt(2) / S1);
			//dft_c2r_in[i][1] = dft_r2c_out[i][1] * wdw_abs * (T)(std::sqrt(2) / S1);

			if (fft_output != nullptr)
				fft_output[i] = sqrt(dft_r2c_out[i][0] * dft_r2c_out[i][0] + dft_r2c_out[i][1] * dft_r2c_out[i][1])*wdw_abs;
		}

		delete[] wdw_out;
		delete[] wdw;
		delete[] dft_r2c_in; dft_r2c_in = nullptr;
		delete[] dft_r2c_out; dft_r2c_out = nullptr;

		// C2R
		if (typeid(T).hash_code() == typeid(float).hash_code())
		{
			fftwf_plan plan = fftwf_plan_dft_c2r_1d(fft_len, dft_c2r_in, dft_c2r_out, FFTW_ESTIMATE);
			fftwf_execute(plan);
			fftwf_destroy_plan(plan);
		}
		else
		{
			fftw_plan plan = fftw_plan_dft_c2r_1d(fft_len, (fftw_complex*)dft_c2r_in, (double*)dft_c2r_out, FFTW_ESTIMATE);
			fftw_execute(plan);
			fftw_destroy_plan(plan);
		}

		_memcpy(out, dft_c2r_out, fft_len*sizeof(T));

		delete[] dft_c2r_in; dft_c2r_in = nullptr;
		delete[] dft_c2r_out; dft_c2r_out = nullptr;

		len = fft_len;
	}

	template <typename T>
	T * Filters<T>::SINC1(size_t &len, const T &freq_trans, const T &freq_sample, const FILTER_TYPE type)
	{
		T * rt = new T[len];
		if (!Filters<T>::SINC1(len, freq_trans, freq_sample, type, rt))
		{
			delete[] rt;
			rt = nullptr;
		}
		return rt;
	}
	template<typename T>
	T * Filters<T>::SINC2(size_t &len, const T &freq_trans1, const T &freq_trans2, const T &freq_sample, const FILTER_TYPE type)
	{
		T * rt = new T[len];
		if (!Filters<T>::SINC2(len, freq_trans1, freq_trans2, freq_sample, type, rt))
		{
			delete[] rt;
			rt = nullptr;
		}
		return rt;
	}

	template<typename T>
	bool Filters<T>::SINC1(size_t &len, const T &freq_trans, const T &freq_sample, const FILTER_TYPE type, T *w)
	{
		static_assert(std::is_floating_point<T>::value, "window1Sinc may only take floating points!");
		T ft, shift, val;

		if (type != FILTER_TYPE::LOW_PASS && type != FILTER_TYPE::HIGH_PASS)
		{
#ifndef __QUIET_MODE__
			std::cerr << "In window1Sinc: Wrong type specified. Must be either LOW_PASS or HIGH_PASS!" << std::endl;
#endif
			return false;
		}

		// normalized cut-off freq.
		ft = freq_trans / freq_sample;
		// shift sinc-center to window center
		shift = (T)(0.5 * (len - 1));

		val = (T)2.0 * ft;

		if (type == FILTER_TYPE::HIGH_PASS)
		{
			if (len % 2 == 0)
			{
				--len; // force odd window length
				delete[] w;
				w = new T[len];
			}
			val = (T)(1.0 - val);
			ft *= -1;
		}

		w[len / 2] = (T)val;
		for (uint n = 0; n < len / 2; ++n)
		{
			val = (T)(sin(2.0 * M_PI * ft * (n - shift)) / (M_PI * (n - shift)));
			w[n] = val;
			w[len - n - 1] = val;
		}

		return true;
	}

	template<typename T>
	bool Filters<T>::SINC2(size_t &len, const T &freq_trans1, const T &freq_trans2, const T &freq_sample, const FILTER_TYPE type, T *w)
	{
		static_assert(std::is_floating_point<T>::value, "window2Sinc may only take floating points!");
		T ft1, ft2, shift, val1, val2, tmp;

		if (type != FILTER_TYPE::BAND_PASS && type != FILTER_TYPE::BAND_STOP)
		{
#ifndef __QUIET_MODE__
			cerr << "In window2Sinc: Wrong type specified. Must be either BAND_PASS or STOP_PASS!" << endl;
#endif
			return false;
		}

		ft1 = freq_trans1 / freq_sample;
		ft2 = freq_trans2 / freq_sample;

		shift = (T)(0.5 * (len - 1));

		if (len % 2 == 0)
		{
			--len; // force odd window length
			delete[] w;
			w = new T[len];
		}

		val1 = (T)(2.0 * (ft2 - ft1));
		if (type == FILTER_TYPE::BAND_STOP) val1 = (T)(1.0 - val1);
		w[len / 2] = (T)val1;

		// Swap transition points if Band Stop
		if (type == FILTER_TYPE::BAND_STOP)
		{
			tmp = ft1;
			ft1 = ft2; ft2 = tmp;
		}

		for (uint n = 0; n < len / 2; ++n)
		{
			val1 = (T)(sin(2.0 * M_PI * ft1 * (n - shift)) / (M_PI * (n - shift)));
			val2 = (T)(sin(2.0 * M_PI * ft2 * (n - shift)) / (M_PI * (n - shift)));

			w[n] = val2 - val1;
			w[len - n - 1] = val2 - val1;
		}

		return true;
	}

}

#endif