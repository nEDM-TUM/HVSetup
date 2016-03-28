#ifndef STDHDR_H
#define STDHDR_H

#ifdef _WIN32
#ifndef _SCL_SECURE_NO_WARNINGS
#define _SCL_SECURE_NO_WARNINGS
#endif
#endif

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES // to include e.g. M_PI from <cmath>
#endif

#ifndef FFTW_TYPE
#define FFTW_TYPE 'f' // f[,d,l]
#if (FFTW_TYPE =='d')
typedef double DTYPE;
#elif (FFTW_TYPE == 'l')
typedef long double DTYPE;
#else
typedef float DTYPE;
#endif
#endif

#endif