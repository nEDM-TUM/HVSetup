#ifndef CVCOMMON_EXPORTS
#	define CVCOMMON_EXPORTS
#endif
#include "CVcommon.h"

#include <cstring>

void *__cdecl CVcommon::_memcpy(void *_Dst, const void *_Src, size_t _Size)
{
#ifdef _WIN32
	return (void*)memcpy_s(_Dst, _Size, _Src, _Size);
#else
	return memcpy(_Dst, _Src, _Size);
#endif
}
void *__cdecl CVcommon::_memcpy(void *_Dst, size_t _DstSize, const void *_Src, size_t _MaxCount)
{
	return CVcommon::_memcpy(_Dst, _Src, _MaxCount);
}
