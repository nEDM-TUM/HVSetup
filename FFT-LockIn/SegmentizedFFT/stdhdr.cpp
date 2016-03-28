#include "stdhdr.h"

#include <cmath>

void *__cdecl _memcpy(void *_Dst, const void *_Src, size_t _Size)
{
#ifdef _WIN32
	return (void*)memcpy_s(_Dst, _Size, _Src, _Size);
#else
	return memcpy(_Dst, _Src, _Size);
#endif
}
void *__cdecl _memcpy(void *_Dst, size_t _DstSize, const void *_Src, size_t _MaxCount)
{
	return _memcpy(_Dst, _Src, _MaxCount);
}

void GetFactor(ulong x, ulong base, ulong &exponent)
{
	exponent = 0;
	while (x % base == 0)
	{
		++exponent;
		x /= base;
	}
}

float _abs(const std::complex<float> &z)
{
	return std::sqrtf(z._Val[0] * z._Val[0] + z._Val[1] * z._Val[1]);
}
float _abs(const float &x, const float &y)
{
	return std::sqrtf(x*x + y*y);
}
float _abs(const size_t &n, const float *x)
{
	float y = 0.0f;
	for (size_t i = 0; i < n; y += *(x + i), ++i);
	return std::sqrtf(y);
}
double _abs(const std::complex<double> &z)
{
	return std::sqrt(z._Val[0] * z._Val[0] + z._Val[1] * z._Val[1]);
}
double _abs(const double &x, const double &y)
{
	return std::sqrt(x*x + y*y);
}
double _abs(const size_t &n, const double *x)
{
	double y = 0.0f;
	for (size_t i = 0; i < n; y += *(x + i), ++i);
	return std::sqrt(y);
}
