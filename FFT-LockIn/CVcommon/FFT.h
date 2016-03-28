#ifndef __CVc_FFT_H
#define __CVc_FFT_H

#include "CVcommon.h"

#include <complex>
#include <vector>

#include <fftw3.h>

template <typename T>
void FFT_DFT_R2C_1D(const ulong n, const T *d_real, T *d_complex[2]);

template <typename T>
void FFT_DFT_R2C_1D(const std::vector<T> &d_real, std::vector<std::complex<T>> &d_complex);


void FFT_DFT_R2C_1D(const ulong n, const float *d_real, fftwf_complex *d_complex);
void FFT_DFT_R2C_1D(const ulong n, const double *d_real, fftw_complex *d_complex);
void FFT_DFT_R2C_1D(const ulong n, const long double *d_real, fftwl_complex *d_complex);

template <typename T>
void FFT_DFT_R2C_1D(const std::vector<T> &d_real, std::vector<std::complex<T>> &d_complex, std::vector<T> &d_abs)
{
	static_assert(std::is_floating_point<T>::value, "NEED FLOATING POINT TYPE!");
	typedef T T2[2];
	const size_t len = d_real.size();
	T *R = new T[len];
	T2 *C = new T2[len];

	d_complex.resize(len / 2 + 1);
	d_abs.resize(len / 2 + 1);

	std::copy(d_real.cbegin(), d_real.cend(), R);

	FFT_DFT_R2C_1D(len, R, C);

	for (uint i = 0; i < len / 2 + 1; ++i)
	{
		d_complex[i] = std::complex<T>(C[i][0], C[i][1]);
		d_abs[i] = sqrt(C[i][0] * C[i][0] + C[i][1] * C[i][1]);
	}
}

#endif