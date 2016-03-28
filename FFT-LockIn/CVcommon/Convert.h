#pragma once
#ifndef __CVc_CONVERT_H
#define __CVc_CONVERT_H

#include "CVcommon.h"
#include "String.h"
#include "Waveform.h"

#include <complex>
#include <iostream>
#include <string>
#include <vector>

namespace CVcommon
{
	/**
		Copy data from the byte vector &raw[0]+offset into the address pointed to by addr. Increase the offset by sizeof(T).

		@param buf a binary buffer big enough to hold T
		@param raw the vector with binary data
		@param offset the index offset to use when reading from raw
		@param addr the address of a sane memory location for the data
	*/
	template <typename T>
	void CopyFromByteVector(byte *buf, const std::vector<byte> &raw, size_t &offset, T *addr);


	/**
		Convert data from a vector to a byte vector of size v.size*sizeof(T).

		@param v the vector which's data shall be converted
		@return byte vector of size v.size*sizeof(T)
	*/
	template <typename T>
	std::vector<T> ConvertFromByteVector(const std::vector<byte> &v);
	/**
		@param begin constant interator to the first element to convert
		@param end constant iterator to the last element to convert
		@param dst initialized destination vector
	*/
	template <typename T>
	void ConvertFromByteVector(const std::vector<byte>::const_iterator &begin, const std::vector<byte>::const_iterator &end, std::vector<T> *dst);


	/**
		Convert data from a vector to a byte vector of size v.size*sizeof(T).

		@param v the vector which's data shall be converted
		@return byte vector of size v.size*sizeof(T)
	*/
	template <typename T>
	std::vector<byte> ConvertToByteVector(const std::vector<T> &v);
	/**
		@param N number of elements in the input array
		@param in the array of values with type T that shall be converted to bytes
		@return byte vector of size v.size*sizeof(T)
	*/
	template <typename T>
	std::vector<byte> ConvertToByteVector(const size_t &N, const T *in);


	/**
		Convert a byte array from a recorded waveform to an array of values and fill the header.

		@param raw the recorded waveform's byte vector
		@param header the header for the recorded waveform to be filled
		@return array of waveform values
	*/
	template <typename T>
	T * ConvertRecordedWaveform(const std::vector<byte> &raw, WaveformHeader &header);
	/**
		@param raw the recorded waveform's byte vector
		@param data the destination vector for the values
		@param header the header for the recorded waveform to be filled
	*/
	template <typename T>
	void ConvertRecordedWaveform(const std::vector<byte> &raw, std::vector<T> &data, WaveformHeader &header);

	/**
		Convert FFT results to a byte vector with a header.

		@param N the size of the data array
		@param data the results from the fourier transform
		@param header object with information on frequencies and (N)ENBW
		@param opt string that specifies the order for header objects to be written
		@return final byte vector
	*/
	template <typename T>
	std::vector<byte> ToByteFromFFT(const size_t N, const T *data, const FFTWindowedHeader<T> &hdr, std::string opt = "fs,fr,S1,S2,NENBW,ENBW");

	/**
		Read the integers from the waveforms beginning '%Y%m%d%H%M%S' and put them into the header file.

		@param buf a binary buffer big enough to hold T
		@param raw the vector with binary data
		@param offset the index offset to use when reading from raw
		@param header the waveform's header with tm struct
	*/
	inline void ParseWaveformTimestamp(byte *buf, const std::vector<byte> &raw, size_t &offset, WaveformHeader &header);

	/*
		+ + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +
	*/

	template <typename T>
	void CopyFromByteVector(byte *buf, const std::vector<byte> &raw, size_t &offset, T *addr)
	{
		std::copy(raw.begin() + offset, raw.begin() + offset + sizeof(T), buf);
		_memcpy(addr, buf, sizeof(T));
		offset += sizeof(T);
	}
	template <typename T>
	std::vector<T> ConvertFromByteVector(const std::vector<byte> &v)
	{
		size_t vsize = v.size();
		byte *buf = new byte[sizeof(T)];
		typename std::vector<T> data(vsize / sizeof(T));
		data.reserve(vsize / sizeof(T));
		std::vector<byte>::const_iterator itSrc;
		typename std::vector<T>::iterator itDst;
		for (itSrc = v.begin(), itDst = data.begin(); itSrc < v.end(); itSrc += sizeof(T), ++itDst)
		{
			std::copy(itSrc, itSrc + sizeof(T), itDst);
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

		for (i = 0, j = 0; i < vsize; ++i, j += 2 * sizeof(T))
		{
			real = v[i].real();
			imag = v[i].imag();
			_memcpy(buf, sizeof(T), &real, sizeof(T));
			_memcpy(buf + sizeof(T), sizeof(T), &imag, sizeof(T));
			for (s = 0; s < 2 * sizeof(T); ++s)
				data[j + s] = buf[s];
		}

		delete[] buf;
		return data;
	}
	template <typename T>
	std::vector<byte> ConvertToByteVector(const std::vector<T> &v)
	{
		size_t i, j;
		const size_t vsize = v.size(), bsize = v.size()*sizeof(T);
		byte *buf = new byte[sizeof(T)];

		std::vector<byte> data(bsize);
		data.reserve(bsize);

		for (i = 0, j = 0; i < vsize, j < bsize; ++i, j += sizeof(T))
			_memcpy(&data[0] + j, &v[0] + i, sizeof(T));

		return data;
	}
	template <typename T>
	std::vector<byte> ConvertToByteVector(const size_t &N, const T *in)
	{
		size_t i, j;
		const size_t bsize = N * sizeof(T);

		std::vector<byte> data(bsize);
		data.reserve(bsize);

		for (i = 0, j = 0; i < N && j < bsize; ++i, j += sizeof(T))
			_memcpy(&data[0] + j, in + i, sizeof(T));
		
		return data;
	}

	template <typename T>
	void ConvertFromByteVector(const std::vector<byte>::const_iterator &begin, const std::vector<byte>::const_iterator &end, std::vector<T> *dst)
	{
		byte * buf = new byte[sizeof(T)];
		std::vector<byte>::const_iterator itSrc;
		typename std::vector<T>::iterator itDst;

		size_t count = 0;
		for (itSrc = begin, itDst = dst->begin(); itSrc < end && itDst != dst->end(); itSrc += sizeof(T), ++itDst)
		{
			//std::copy(itSrc, itSrc + sizeof(double), buf);
			_memcpy(buf, &(*itSrc), sizeof(T));
			_memcpy(&(*itDst), buf, sizeof(T));

			/*if (++count % 1000 == 0)
				cout << count << endl;*/
		}
		delete[] buf;
	}
	template <typename T>
	void ConvertFromByteVector(const std::vector<byte> &v, const size_t begin, const size_t end, std::vector<T> &dst)
	{
		size_t i, j;
		const size_t dst_size = (end - begin) / sizeof(T);
		byte *buf = new byte[sizeof(T)];
		dst.reserve(dst_size);
		for (i = 0, j = begin; i < dst_size && j < end; ++i, j += sizeof(T))
		{
			_memcpy(&dst[0] + i, &v[0] + j, sizeof(T));
		}
		delete[] buf;
	}
	template <typename T>
	T * ConvertFromByteVector(const std::vector<byte> &v, const size_t begin, const size_t end, size_t &len)
	{
		size_t i, j;
		len = (end - begin) / sizeof(T);
		byte *buf = new byte[sizeof(T)];
		T *dst = new T[len];
		for (i = 0, j = begin; i < len && j < end; ++i, j += sizeof(T))
		{
			_memcpy(dst + i, &v[0] + j, sizeof(T));
		}
		delete[] buf;
		return dst;
	}

	template <typename T>
	byte * ConvertToByteArray(const size_t n, T *v)
	{
		size_t i;
		byte *rt = new byte[n*sizeof(T)];
		for (i = 0; i < n; ++i)
			_memcpy(rt + i*sizeof(T), v + i, sizeof(T));
		return rt;
	}
	template <typename T>
	T * ConvertFromByteArray(size_t n, byte *b)
	{
		size_t i, Tsize = n / sizeof(T);
		T *rt = new T[Tsize];
		for (i = 0; i < Tsize; ++i)
			_memcpy(rt + i, b + i*sizeof(T), sizeof(T));
		return rt;
	}

	template <typename T>
	T * ConvertRecordedWaveform(const std::vector<byte> &raw, WaveformHeader &header)
	{
		size_t offset = 0, len;

		byte *buf = new byte[sizeof(long double)]; // double is the largest type used

		ParseWaveformTimestamp(raw, header, offset);

		CopyFromByteVector<uint>(buf, raw, offset, &(header.N));
		CopyFromByteVector<T>(buf, raw, offset, &(header.xzero));
		CopyFromByteVector<T>(buf, raw, offset, &(header.xincr));
		CopyFromByteVector<T>(buf, raw, offset, &(header.yzero));
		CopyFromByteVector<T>(buf, raw, offset, &(header.yoffs));
		CopyFromByteVector<T>(buf, raw, offset, &(header.ymult));
		CopyFromByteVector<char>(buf, raw, offset, &(header.xunit));
		CopyFromByteVector<char>(buf, raw, offset, &(header.yunit));

		T *data = ConvertFromByteVector<T>(raw, offset, raw.size(), len);
#ifndef __QUIET_MODE__
		if (len != header.N)
		{
			std::cerr << "WARNING: Length of remaining byte array is not equal to N from the header file!" << std::endl;
		}
#endif
		header.N = len;
		return data;
	}

	template <typename T>
	void ConvertRecordedWaveform(const std::vector<byte> &raw, std::vector<T> &data, WaveformHeader &header)
	{
		size_t offset = 0;
		byte *buf = new byte[sizeof(long double)]; // double is the largest type used

		ParseWaveformTimestamp(buf, raw, offset, header);

		CopyFromByteVector<byte>(buf, raw, offset, &(header.precision));
		CopyFromByteVector<uint>(buf, raw, offset, &(header.N));
		CopyFromByteVector<T>(buf, raw, offset, &(header.xzero));
		CopyFromByteVector<T>(buf, raw, offset, &(header.xincr));
		CopyFromByteVector<T>(buf, raw, offset, &(header.yzero));
		CopyFromByteVector<T>(buf, raw, offset, &(header.yoffs));
		CopyFromByteVector<T>(buf, raw, offset, &(header.ymult));
		CopyFromByteVector<char>(buf, raw, offset, &(header.xunit));
		CopyFromByteVector<char>(buf, raw, offset, &(header.yunit));

		data.resize(header.N);
		data.reserve(header.N);

		ConvertFromByteVector<T>(raw, offset, raw.size(), data);
	}

	template <typename T>
	std::vector<byte> ToByteFromFFT(const std::vector<T> &data, const FFTWindowedHeader<T> &hdr, std::string opt = "fs,fr,S1,S2,NENBW,ENBW")
	{
		std::vector<byte> b_return, b_data;
		size_t i;

		byte *buf = new byte[sizeof(T)];
		std::vector<string> split = CVcommon::String::Split(opt, ',', false);
		//for each (string s in split)
		for (std::string s : split)
		{
			if (s.compare("fs") == 0) _memcpy(buf, &hdr.fs, sizeof(T));
			else if (s.compare("fr") == 0) _memcpy(buf, &hdr.fr, sizeof(T));
			else if (s.compare("S1") == 0) _memcpy(buf, &hdr.S1, sizeof(T));
			else if (s.compare("S2") == 0) _memcpy(buf, &hdr.S2, sizeof(T));
			else if (s.compare("NENBW") == 0) _memcpy(buf, &hdr.NENBW, sizeof(T));
			else if (s.compare("ENBW") == 0) _memcpy(buf, &hdr.ENBW, sizeof(T));
			else continue;

			for (i = 0; i < sizeof(T); b_return.push_back(buf[i++]));
		}
		delete[] buf;

		b_data = ConvertToByteVector<T>(data);

		b_return.reserve(b_return.size() + b_data.size());
		b_return.insert(b_return.end(), b_data.begin(), b_data.end());

		return b_return;
	}

	void ParseWaveformTimestamp(byte *buf, const std::vector<byte> &raw, size_t &offset, WaveformHeader &header)
	{
		header.time = std::tm{};

		CopyFromByteVector<int>(buf, raw, offset, &(header.time.tm_year));
		CopyFromByteVector<int>(buf, raw, offset, &(header.time.tm_mon));
		CopyFromByteVector<int>(buf, raw, offset, &(header.time.tm_mday));
		CopyFromByteVector<int>(buf, raw, offset, &(header.time.tm_hour));
		CopyFromByteVector<int>(buf, raw, offset, &(header.time.tm_min));
		CopyFromByteVector<int>(buf, raw, offset, &(header.time.tm_sec));

		header.time.tm_year -=  1900;
		header.time.tm_mon -=  1;
		header.time.tm_hour -=  1;
		header.time.tm_min -= 1;
		header.time.tm_sec -= 1;
	}

	template <typename T>
	std::vector<byte> ToByteFromFFT(const size_t N, const T *data, const FFTWindowedHeader<T> &hdr, std::string opt)
	{
		std::vector<T> v = std::vector<T>(data, data + N);
		return ToByteFromFFT<T>(v, hdr, opt);
	}

}

#endif