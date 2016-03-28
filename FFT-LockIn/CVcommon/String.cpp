#ifndef CVCOMMON_EXPORTS
#	define CVCOMMON_EXPORTS
#endif
#include "String.h"

#include <algorithm>

const std::string CVcommon::String::STD_TRIM_DELIMS = " \f\n\r\t\v";

std::string CVcommon::String::ReplaceExtension(const std::string instr, const std::string replacement)
{
	std::size_t lastdot = instr.find_last_of('.') + 1;
	std::string tmp = instr.substr(0, lastdot);
	tmp.append(replacement);
	return tmp;
}

std::vector<std::string> CVcommon::String::Split(std::string str, const char delim, const bool keepEmpty)
{
	return CVcommon::String::Split(str, ToString(delim), keepEmpty);
}
std::vector<std::string> CVcommon::String::Split(std::string str, const std::string delim, const bool keepEmpty)
{
	std::vector<std::string> v;
	std::string substr;
	std::size_t pos;
	while (str.length() > 0)
	{
		pos = str.find_first_of(delim);
		substr = str.substr(0, pos);
		if (substr.empty() == false)
			v.push_back(substr);
		str = str.substr(pos + 1, str.length());
		if (pos == std::string::npos)
			break;
	}
	return v;
}

std::string CVcommon::String::toupper(std::string &str)
{
	std::transform(str.begin(), str.end(), str.begin(), ::toupper);
	return str;
}
std::string CVcommon::String::toupper(char *str)
{
	std::string s = std::string(str);
	return CVcommon::String::toupper(s);
}
std::string CVcommon::String::toupper(const char *str)
{
	std::string s = std::string(str);
	return CVcommon::String::toupper(s);
}