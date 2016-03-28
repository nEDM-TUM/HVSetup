/**
CVcommon
CVcommon.h
Purpose: Common header file for preprocessor directives, typedefs and workarounds.

@author Christian Velten
@version 1.0 07/18/2015
*/
#pragma once
#ifndef __CVc_STDHDR_H
#define __CVc_STDHDR_H

#if defined(_WIN32) || defined(_MSC_VER)
#   ifndef _CRT_SECURE_NO_WARNINGS
#       define _CRT_SECURE_NO_WARNINGS
#   endif
#elif defined __GNUC__
#elif defined __CINT__
#endif

/* ** Make exportable ** */
#if defined(_WIN32) || defined(_WIN64)
#	ifdef CVCOMMON_EXPORTS
#		define CVCOMMON_API __declspec(dllexport)
#		define EXPIMP_TEMPLATE
#	else
#		define CVCOMMON_API __declspec(dllimport)
#		define EXPIMP_TEMPLATE extern
#	endif
#else
#	ifdef CVCOMMON_EXPORTS
#		define CVCOMMON_API 
#		define EXPIMP_TEMPLATE
#	else
#		define CVCOMMON_API
#		define EXPIMP_TEMPLATE extern
#	endif
#endif

#if (defined(_WIN32) || defined(_WIN64)) && defined(CVCOMMON_EXPORTS)
#	define WIN32_LEAN_AND_MEAN	// Selten verwendete Teile der Windows-Header nicht einbinden.
#	include <SDKDDKVer.h>
#	// Windows-Headerdateien:
#	include <windows.h>
#endif

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES // to include e.g. M_PI from <cmath>
#endif

namespace CVcommon
{
	/*
	* typedef
	*/
	typedef unsigned int uint;
	typedef unsigned long ulong;
	typedef unsigned char byte;

	// stdlib-workaround for portability between unix/ms
	CVCOMMON_API void *__cdecl _memcpy(void *_Dst, const void *_Src, size_t _Size);
	CVCOMMON_API void *__cdecl _memcpy(void *_Dst, size_t _DstSize, const void *_Src, size_t _MaxCount);
}

#endif