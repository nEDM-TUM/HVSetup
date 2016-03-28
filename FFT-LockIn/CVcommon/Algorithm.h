/**
CVcommon
LockIn.h
Purpose: Provide LockIn functions/wrappers and structs.

@author Christian Velten
@version 1.0 07/22/2015
*/
#pragma once
#ifndef __CVc_ALGORITHM_H
#define __CVc_ALGORITHM_H

#include "CVcommon.h"

#include <cctype>
#include <vector>

namespace CVcommon
{
	/**
		Reduce the amount of data by averaging adjacent values in groups. 

		@param v the input data
		@param group the number of values to group
		@return vector of data with new length
	*/
	template <typename T>
	std::vector<T> CropData(const std::vector<T> &v, size_t group = 1)
	{
		if (group <= 1) return std::vector<T>(v);

		const size_t vsize = v.size();
		std::vector<T> vnew;
		vnew.reserve(vsize / group);
		vnew.resize(vsize / group);

		for (size_t i = 0, k = 0; i < vsize; i += group, ++k)
		{
			for (size_t j = i; j - i < group; vnew[k] += v[j++]);
			vnew[k] /= (T)group;
		}
		return vnew;
	}
	/**
		@param n the length of the data array
		@param v the input data
		@param group the number of values to group
		@return vector of data with new length
	*/
	template <typename T>
	std::vector<T> CropData(size_t &n, T *v, size_t group = 1)
	{
		if (group <= 1) return v;

		T *vnew = new T[n / group];

		for (size_t i = 0, k = 0; i < n; i += group, ++k)
		{
			for (size_t j = i; j - i < group; vnew[k] += v[j++]);
			vnew[k] /= (T)group;
		}

		n /= group;
		delete[] v;
		return vnew;
	}

}
#endif