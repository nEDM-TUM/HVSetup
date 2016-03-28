/**
CVcommon
File.h
Purpose: Provide file I/O functions for ASCI and binary operations.

@author Christian Velten
@version 1.0 07/18/2015
*/
#pragma once
#ifndef __CVc_FILE_H
#define __CVc_FILE_H

#include "CVcommon.h"
#include "String.h"

#include <vector>

namespace CVcommon
{
	/**
		Provides static member functions for file I/O.
	*/
	class File
	{
	private:
		File() {};
	public:
		/**
			Check whether a file exists via fopen.

			@param filename to probe
			@return true if file exists, false otherwise
		*/
		static CVCOMMON_API bool Exists(const std::string filename);

		static CVCOMMON_API std::vector<std::string> ReadLines(const std::string filename);
		static CVCOMMON_API std::vector<std::vector<double>> ReadASCII(const std::string filename, const char delim = String::STD_DELIM);

		/**
			Read the contents of a file in binary mode and return a pointer to a binary array.

			@param filename file to read
			@param len length of output binary array
			@return pointer to read binary array
		*/
		static CVCOMMON_API byte * ReadBINARY(const std::string filename, size_t &len);
		/**
			Read the contents of a file in binary mode and return a binary vector.

			@param filename file to read
			@return binary vector with file contents
		*/
		static CVCOMMON_API std::vector<byte> ReadBINARY(const std::string filename);

		/**
			Write the contents of a byte array to file in binary mode.

			@param filename file to write to
			@param len number of bytes to write from 'const byte *v'
			@param v binary array to write to file
		*/
		static CVCOMMON_API void WriteBINARY(const std::string filename, const size_t len, const byte *v);
		/**
			Write the contents of a byte vector to file in binary mode.

			@param filename file to write to
			@param v binary vector to write to file
		*/
		static CVCOMMON_API void WriteBINARY(const std::string filename, const std::vector<byte> &v);
	};

}

#else
#endif
