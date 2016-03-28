/**
CVcommon
LockIn.h
Purpose: Provide LockIn functions/wrappers and structs.

@author Christian Velten
@version 1.0 07/22/2015
*/
#pragma once
#ifndef __CVc_LOCKIN_H
#define __CVc_LOCKIN_H

#include "CVcommon.h"
#include "Filters.h"
#include "MathTools.h"
#include "Waveform.h"

#include <iostream>
#include <cmath>

namespace CVcommon
{
	template <typename T>
	struct LockInReturn
	{
		T fsampling, flock;
		T Xavg, Yavg, Ravg, PHASE;
	};

	/**
		Provides static member functions that resemble a software Lock-In.
	*/
	template <typename T>
	class LockIn
	{
	private:

	public:
		/**
			Prepare data for double phase sensitive detection. Data is multiplied by 2sin(x) and 2cos(x) respectively with x ~ flock/fsample.

			@param len data array lengths
			@param in the input data
			@param X output for X data (multiplied with sin)
			@param Y output for Y data (multiplied with cos)
			@param fs the data's sampling frequency
			@param fl the lock-frequency
		*/
		static inline void DoublePSD(const size_t &len, const T *in, T *X, T *Y, const T &fs, const T &fl, const T &phase);
		/**
			Calculate the lock for a given lock frequency. Prepares the data, low-pass filters it and calculates the phase-independent magnitude.

			@param v vector holding the input data
			@param hdr waveform header holding information
			@param fs the data's sampling frequency
			@param fl the lock-frequency.
			@param ft the transmission frequency for the low-pass filters
			@param verbosity true for more output, default=false
			@return struct holding the averaged results and frequency information
		*/
		static LockInReturn<T> CalculateLock(const std::vector<T> &v, const WaveformHeader &hdr, const T &fs, const T &fl, const T &ft, bool verbosity = false);
	};

	template <typename T>
	void LockIn<T>::DoublePSD(const size_t &len, const T *in, T *X, T *Y, const T &fs, const T &fl, const T &phase)
	{
		size_t i;
		T z;
		const T Dt = (T)(2 * M_PI * fl / fs);
		for (i = 0; i < len; ++i)
		{
			z = i * Dt + phase;
			X[i] = in[i] * 2 * sin(z); // bc of 1/2 from addition theorem
			Y[i] = in[i] * 2 * cos(z);
		}
	}

	template <typename T>
	LockInReturn<T> LockIn<T>::CalculateLock(const std::vector<T> &v, const WaveformHeader &hdr, const T &fs, const T &fl, const T &ft, bool verbosity)
	{
		size_t N;
		T S1, S2;
		LockInReturn<T> rt = {};

		const T * data = v.data();

		N = hdr.N;
		assert(N >= 2048);

		T * X = new T[N], *Y = new T[N];
		T * Xfiltered = new T[N], *Yfiltered = new T[N];
		T * R = new T[N];
		T Xavg, Yavg;

		LockIn<T>::DoublePSD(N, data, X, Y, fs, fl, 0);

		Filters<T>::LowPass(N, X, Xfiltered, ft, fs, S1, S2);
		Filters<T>::LowPass(N, Y, Yfiltered, ft, fs, S1, S2);

		Xavg = Average(N, Xfiltered);
		Yavg = Average(N, Yfiltered);

		rt.fsampling = fs;
		rt.flock = fl;
		rt.Xavg = Xavg;
		rt.Yavg = Yavg;
		rt.Ravg = (T)(std::sqrt(Xavg*Xavg + Yavg*Yavg));
		rt.PHASE = std::atan2(Yavg, Xavg);

		if (verbosity)
			std::cout << "fl = " << fl << " | Ravg = " << rt.Ravg << std::endl;

		delete[N] R;
		delete[N] X;
		delete[N] Y;
		delete[N] Xfiltered;
		delete[N] Yfiltered;

		return rt;
	}

}

#endif