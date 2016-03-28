#ifndef CVCOMMON_EXPORTS
#	define CVCOMMON_EXPORTS
#endif
#include "FFT.h"

void FFT_DFT_R2C_1D(const ulong n, const float *d_real, fftwf_complex *d_complex)
{
	float *dft_real = new float[n];
	fftwf_complex *dft_complex = (fftwf_complex *)fftwf_malloc(sizeof(fftwf_complex) * n);
	fftwf_plan plan;

	_memcpy(dft_real, d_real, n*sizeof(float));
	plan = fftwf_plan_dft_r2c_1d(n, dft_real, dft_complex, FFTW_ESTIMATE);
	fftwf_execute(plan);
	_memcpy(d_complex, dft_complex, (n / 2 + 1)*sizeof(fftwf_complex));

	fftwf_destroy_plan(plan);
	fftwf_free(dft_real);
	fftwf_free(dft_complex);
}

void FFT_DFT_R2C_1D(const ulong n, const double *d_real, fftw_complex *d_complex)
{
	double *dft_real = new double[n];
	fftw_complex *dft_complex = (fftw_complex *)fftw_malloc(sizeof(fftw_complex) * n);
	fftw_plan plan;

	_memcpy(dft_real, d_real, n*sizeof(double));
	plan = fftw_plan_dft_r2c_1d(n, dft_real, dft_complex, FFTW_ESTIMATE);
	fftw_execute(plan);
	_memcpy(d_complex, dft_complex, (n / 2 + 1)*sizeof(fftw_complex));

	fftw_destroy_plan(plan);
	fftw_free(dft_real);
	fftw_free(dft_complex);
}

void FFT_DFT_R2C_1D(const ulong n, const long double *d_real, fftwl_complex *d_complex)
{
	long double *dft_real = new long double[n];
	fftwl_complex *dft_complex = (fftwl_complex *)fftwl_malloc(sizeof(fftwl_complex) * n);
	fftwl_plan plan;

	_memcpy(dft_real, d_real, n*sizeof(long double));
	plan = fftwl_plan_dft_r2c_1d(n, dft_real, dft_complex, FFTW_ESTIMATE);
	fftwl_execute(plan);
	_memcpy(d_complex, dft_complex, (n / 2 + 1)*sizeof(fftwl_complex));

	fftwl_destroy_plan(plan);
	fftwl_free(dft_real);
	fftwl_free(dft_complex);
}

