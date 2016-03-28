#ifndef __CVc_MATHTOOLS_H
#define __CVc_MATHTOOLS_H

#include "CVcommon.h"

#include <cmath>

namespace CVcommon
{
	template <typename T>
	T Average(size_t n, T *x)
	{
		size_t i;
		T val = (T)0;
		if (n < 1000)
		{
			for (i = 0; i < n; val += x[i++]);
			return val / n;
		}
		else
		{
			for (i = 0; i < n; val += x[i++] / n);
			return val;
		}
	}

	template <typename T>
	T * CalculatePhase(size_t n, T *x, T *y)
	{
		T *ph = new T[n];
		for (size_t i = 0; i < n; ++i)
			ph[i] = std::atan2(y[i], x[i]);
		return ph;
	}

	template <typename T>
	T _abs(const std::complex<T> &z)
	{
		return std::sqrt(z._Val[0] * z._Val[0] + z._Val[1] * z._Val[1]);
	}
	template <typename T>
	T _abs(const T &x, const T &y)
	{
		return std::sqrt(x*x + y*y);
	}
	template <typename T>
	T _abs(const size_t &n, const T *x)
	{
		float y = 0.0f;
		for (size_t i = 0; i < n; y += *(x + i), ++i);
		return std::sqrtf(y);
	}

	template <typename T>
	ulong GetFactor(T x, ulong base)
	{
		ulong exponent = 0;
		while (x % base == 0)
		{
			++exponent;
			x /= base;
		}
		return exponent;
	}

	template <typename T>
	class Logspace
	{
	private:
		T curValue, base;
	public:
		Logspace(T first, T base) : curValue(first), base(base) {}

		T operator()()
		{
			T retval = curValue;
			curValue *= base;
			return retval;
		}
	};

	template <typename T>
	std::vector<T> pyLogspace(T start, T stop, size_t num = 50, T base = (T)10)
	{
		T realStart = std::pow(base, start);
		T realBase = std::pow(base, (stop - start) / num);

		std::vector<T> retval;
		retval.reserve(num);

		std::generate_n(std::back_inserter(retval), num, Logspace<T>(realStart, realBase));
		return retval;
	}
}

#endif