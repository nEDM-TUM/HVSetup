#ifndef CVCOMMON_EXPORTS
#	define CVCOMMON_EXPORTS
#endif
#include "File.h"

#include <cstdlib>
#include <fstream>
#include <sstream>

using CVcommon::byte;

bool CVcommon::File::Exists(const std::string filename)
{
	if (FILE *file = fopen(filename.c_str(), "r"))
	{
		fclose(file);
		return true;
	}
	else
		return false;
}

std::vector<std::string> CVcommon::File::ReadLines(const std::string filename)
{
	std::ifstream ifs(filename.data(), std::ifstream::in);

	std::string tmpLine;
	std::vector<std::string> row_data;

	while (ifs.good())
	{
		std::getline(ifs, tmpLine);
		row_data.push_back(tmpLine);
	}

	ifs.close();

	return row_data;
}

std::vector<std::vector<double>> CVcommon::File::ReadASCII(const std::string filename, const char delim)
{
	std::vector<std::string> row_data, split_data;
	std::vector<std::vector<double>> data_columns;
	size_t i, j;

	row_data = CVcommon::File::ReadLines(filename);

	for (i = 0; i < row_data.size(); ++i)
	{
		split_data = String::Split(row_data[i], delim);

		while (split_data.size() > data_columns.size())
		{
			std::vector<double> new_col;
			data_columns.push_back(new_col);
		}

		for (j = 0; j < split_data.size(); ++j)
		{
			data_columns[j].push_back(StringTo<double>(split_data[j]));
		}
	}

	return data_columns;
}

/*
byte * CVcommon::File::ReadBINARY(const std::string filename, size_t &len)
{
	// open
	std::streampos size;
	std::ifstream file(filename, std::ios::binary);

	// get file size
	file.seekg(0, std::ios::end);
	size = file.tellg();
	len = (size_t)size;
	file.seekg(0, std::ios::beg);

	// read
	byte * data = new byte[len];
	file.read((char*)data, size);

	return data;
}
*/

std::vector<byte> CVcommon::File::ReadBINARY(const std::string filename)
{
	// open
	std::streampos size;
	std::ifstream file(filename, std::ios::binary);

	// get file size
	file.seekg(0, std::ios::end);
	size = file.tellg();
	file.seekg(0, std::ios::beg);

	std::vector<byte> data((size_t)size);
	file.read((char*)&data[0], size);
	file.close();

	return data;
}

void CVcommon::File::WriteBINARY(const std::string filename, const size_t len, const byte *v)
{
	// open
	std::streampos size;
	std::ofstream file(filename, std::ios::binary);

	// write
	file.write((char*)v, len);
}
void CVcommon::File::WriteBINARY(const std::string filename, const std::vector<byte> &v)
{
	// open
	std::streampos size;
	std::ofstream file(filename, std::ios::binary);

	file.write((char*)&v[0], v.size());
	file.close();
}
