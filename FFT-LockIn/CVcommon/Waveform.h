#pragma once
#ifndef __CVc_WAVEFORM_H
#define __CVc_WAVEFORM_H

#include "CVcommon.h"
#include "Windows.h"

#include <ctime>

namespace CVcommon
{

	/*
		Struct containing waveform information read from an oscilloscope
	*/
	struct WaveformHeader
	{
		byte precision;
		uint N;
		std::tm time;
		float xzero, xincr, yzero, yoffs, ymult;
		char xunit, yunit;
	};

	/*
		Struct containing information for a FFT like sampling frequency of the initial data, resolution and (N)ENBW.
	*/
	template <typename T>
	struct FFTWindowedHeader
	{
		uint N;
		T fs, fr, S1, S2, NENBW, ENBW;
		WINDOW_TYPE window;
	};

}

#endif