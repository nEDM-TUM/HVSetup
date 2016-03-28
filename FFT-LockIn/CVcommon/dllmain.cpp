#ifndef CVCOMMON_EXPORTS
#	define CVCOMMON_EXPORTS
#endif
#include "CVcommon.h"

/**
	Define DLL entry point when compiling for windows 32/64-bit machines.
*/
#if (defined(_WIN32) || defined(_WIN64)) && defined(CVCOMMON_EXPORTS)

BOOL APIENTRY DllMain( HMODULE hModule,
					  DWORD  ul_reason_for_call,
					  LPVOID lpReserved
					  )
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
	case DLL_THREAD_ATTACH:
	case DLL_THREAD_DETACH:
	case DLL_PROCESS_DETACH:
		break;
	}
	return TRUE;
}

#else
#endif
