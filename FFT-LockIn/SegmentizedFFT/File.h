#pragma once
#ifndef FILE_H
#define FILE_H

#include "stdhdr.h"
#include "String.h"

#include <cassert>
#include <complex>
#include <vector>
#include <iostream>

template <typename T>
std::vector<T> ConvertFromByteVector(const std::vector<byte> &v)
{
	size_t i, j, s, vsize = v.size();
	byte *buf = new byte[sizeof(T)];
	T val;
	std::vector<T> data(vsize / sizeof(T));
	data.reserve(vsize / sizeof(T));

	std::vector<byte>::const_iterator itSrc;
	typename std::vector<T>::iterator itDst;
	for (itSrc = v.begin(), itDst = data.begin(); itSrc < v.end(); itSrc += sizeof(T), ++itDst)
	{
		std::copy(itSrc, itDst + sizeof(T), buf);
		_memcpy(&(*itDst), buf, sizeof(T));
	}
	delete[] buf;
	return data;
}


template <typename T>
std::vector<byte> ConvertToByteVector(const std::vector<std::complex<T>> &v)
{
	size_t i, j, s, vsize = v.size(), bsize = 2 * v.size() * sizeof(T);
	byte *buf = new byte[2 * sizeof(T)];
	T real, imag;

	std::vector<byte> data(bsize);
	data.reserve(bsize);

	for (i = 0, j = 0; i < vsize; ++i, j += 2*sizeof(T))
	{
		real = v[i].real();
		imag = v[i].imag();
		_memcpy(buf, sizeof(T), &real, sizeof(T));
		_memcpy(buf+sizeof(T), sizeof(T), &imag, sizeof(T));
		for (s = 0; s < 2 * sizeof(T); ++s)
			data[j + s] = buf[s];
	}

	delete[] buf;
	return data;
}
template <typename T>
std::vector<byte> ConvertToByteVector(const std::vector<T> &v)
{
	size_t bsize = v.size()*sizeof(T);
	byte *buf = new byte[sizeof(T)];

	std::vector<byte> data(bsize);
	data.reserve(bsize);

	typename std::vector<T>::const_iterator itSrc;
	std::vector<byte>::iterator itDst;

	for (itSrc = v.begin(), itDst = data.begin(); itSrc < v.end(); ++itSrc, itDst += sizeof(T))
	{
		_memcpy(buf, &(*itSrc), sizeof(T));
		std::copy(buf, buf + sizeof(T), &(*itDst));
	}
	/*
	for (i = 0, j = 0; i < vsize; ++i, j += sizeof(T))
	{
		_memcpy(buf, sizeof(T), &v1[i], sizeof(T));
		for (k = 0; k < sizeof(T); ++k)
			data[j + k] = buf[k];
	}
	*/

	delete[] buf;
	return data;
}

template <typename T>
void ConvertFromByteVector(std::vector<byte>::const_iterator begin, std::vector<byte>::const_iterator end, std::vector<T> &dst)
{
	byte * buf = new byte[sizeof(T)];
	std::vector<byte>::const_iterator itSrc;
	typename std::vector<T>::iterator itDst;

	for (itSrc = begin, itDst = dst.begin(); itSrc < end && itDst != dst.end(); itSrc += sizeof(T), ++itDst)
	{
		//std::copy(itSrc, itSrc + sizeof(double), buf);
		_memcpy(buf, &(*itSrc), sizeof(T));
		_memcpy(&(*itDst), buf, sizeof(T));
	}
	delete[] buf;
}

template <typename T>
void ConvertRecordedWaveform(const std::vector<byte> &raw, std::vector<T> &data, WaveformHeader &header)
{
	size_t offset = 0;

	byte *buf = new byte[sizeof(long double)]; // double is the largest type used

	CopyFromByteVector<unsigned __int32>(buf, raw, offset, &(header.N));
	CopyFromByteVector<T>(buf, raw, offset, &(header.xzero));
	CopyFromByteVector<T>(buf, raw, offset, &(header.xincr));
	CopyFromByteVector<T>(buf, raw, offset, &(header.yzero));
	CopyFromByteVector<T>(buf, raw, offset, &(header.yoffs));
	CopyFromByteVector<T>(buf, raw, offset, &(header.ymult));
	CopyFromByteVector<char>(buf, raw, offset, &(header.xunit));
	CopyFromByteVector<char>(buf, raw, offset, &(header.yunit));

	data.resize(header.N);
	data.reserve(header.N);

	ConvertFromByteVector<T>(raw.begin() + offset, raw.end(), data);
}

class File
{
private:
	File() {};
public:
	static std::vector<std::string> ReadLines(const std::string filename);
	static std::vector<std::vector<double>> ReadASCII(const std::string filename, const char delim = String::STD_DELIM);
	static std::vector<byte> ReadBINARY(const std::string filename);

	static void WriteBINARY(const std::string filename, const std::vector<byte> &v);
};

#else
#endif
