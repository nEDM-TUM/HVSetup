#pragma once
#ifndef __CVc_STRING_H
#define __CVc_STRING_H

#include "CVcommon.h"

#include <sstream>
#include <string>
#include <vector>

namespace CVcommon
{
	/**
		Convert any object's contents to string using stringstream.

		@param obj the object whose value shall be converted.
		@return stringstream result of obj
	*/
	template <typename Type>
	std::string ToString(Type obj)
	{
		std::stringstream oss;
		oss << obj;
		return oss.str();
	}
	/**
		Try to convert a string to a value of type Type. Prone to lose information for complex datatypes, though.

		@param str the string to convert
		@return best guess of stringstream for string to Type
	*/
	template <typename Type>
	Type StringTo(const std::string str)
	{
		std::stringstream iss(str);
		Type t;
		if (!(iss >> t))
			return 0;
		return t;
	}

	class String
	{
	public:
		static const CVCOMMON_API char STD_DELIM = ';';
		static const CVCOMMON_API std::string STD_TRIM_DELIMS;

		/**
			Replace the extension in a string. An extension is defined as the characters that follow the last dot. The dot itself is preserved.

			@param instr the input string
			@param replacement the new extension
			@return the input string with replaced extension
		*/
		static CVCOMMON_API std::string ReplaceExtension(std::string instr, std::string replacement);

		/**
			Split the string at occurences of a delimiter.

			@param str the string to split
			@param delim the delimiter
			@param keepEmpty if splitting creates empty strings, keep them?
			@return string vector with split results
		*/
		static CVCOMMON_API std::vector<std::string> Split(std::string str, const char delim = STD_DELIM, const bool keepEmpty = false);   
		static CVCOMMON_API std::vector<std::string> Split(std::string str, const std::string delim = ToString(STD_DELIM), const bool keepEmpty = false);

		/**
			Convert a string to all-uppercase

			@param str the string to make uppercase
			@return uppercase string
		*/
		static CVCOMMON_API std::string toupper(std::string &str);
		static CVCOMMON_API std::string toupper(char *str);
		static CVCOMMON_API std::string toupper(const char *str);

		/**
			Create a new string consisting of the old string with all whitespaces removed to the right.

			@param s the string to trim
			@param delimiters characters to remove, default=" \f\n\r\t\v"
			@return trimmed copy of string
		*/
		static inline std::string trim_right_copy(const std::string &s, const std::string &delimiters = STD_TRIM_DELIMS)
		{
			return s.substr(0, s.find_last_not_of(delimiters) + 1);
		}
		/**
			Create a new string consisting of the old string with all whitespaces removed to the left.

			@param s the string to trim
			@param delimiters characters to remove, default=" \f\n\r\t\v"
			@return trimmed copy of string
		*/
		static inline std::string trim_left_copy(const std::string &s, const std::string &delimiters = STD_TRIM_DELIMS)
		{
			return s.substr(s.find_first_not_of(delimiters));
		}
		/**
			Create a new string consisting of the old string with all whitespaces removed to both ends.

			@param s the string to trim
			@param delimiters characters to remove, default=" \f\n\r\t\v"
			@return trimmed copy of string
		*/
		static inline std::string trim_copy(const std::string &s, const std::string &delimiters = STD_TRIM_DELIMS)
		{
			return trim_left_copy(trim_right_copy(s, delimiters), delimiters);
		}
	};

}

#else
#endif
