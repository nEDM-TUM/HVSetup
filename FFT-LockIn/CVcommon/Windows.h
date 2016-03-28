/**
CVcommon
Windows.h
Purpose: Provide window function methods.

@author Christian Velten
@version 1.0 07/18/2015
*/
#pragma once
#ifndef __CVc_WINDOWS_H
#define __CVc_WINDOWS_H

#include "CVcommon.h"

#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif
#include <cmath>
#include <cstring>

#include <boost/math/tr1.hpp>
#include <boost/math/special_functions/bessel.hpp>

namespace CVcommon
{
	enum class WINDOW_TYPE : unsigned int { BARTLETT=0, WELCH, HANNING, HAMMING,
		NUTTALL3=10, NUTTALL3A, NUTTALL3B, NUTTALL4, NUTTALL4A, NUTTALL4B, NUTTALL4C,
		KAISER20=20, KAISER25, KAISER30, KAISER35, KAISER40, KAISER45, KAISER50, KAISER55, KAISER60, KAISER65, KAISER70,
		HFT116D=100, HFT248D, RECTANGULAR=1000 };

	/**
		Provides static member functions for window value calculation.
	*/
	template <typename T>
	class Windows
	{
	private:
		static inline T Kaiser(ulong, ulong, T);

	public:
		static T * Calculate_Window(const WINDOW_TYPE, ulong, T &, T &);
		static T * Calculate_Window(const char *, ulong, T &, T &);
		static T * Calculate_Window(T(*)(ulong, ulong), ulong, T &, T &);
		static void Calculate_Window(const WINDOW_TYPE, ulong, T *, T &, T &);
		static void Calculate_Window(const char *, ulong, T *, T &, T &);
		static void Calculate_Window(T(*)(ulong, ulong), ulong, T *, T &, T &);

		static WINDOW_TYPE ParseWindowType(const char *);
		static float IdealOverlap(const WINDOW_TYPE);

		static inline T Bartlett(ulong, ulong);
		static inline T Welch(ulong, ulong);
		static inline T Hanning(ulong, ulong);
		static inline T Hamming(ulong, ulong);
		static inline T Nuttall3(ulong, ulong);
		static inline T Nuttall3a(ulong, ulong);
		static inline T Nuttall3b(ulong, ulong);
		static inline T Nuttall4(ulong, ulong);
		static inline T Nuttall4a(ulong, ulong);
		static inline T Nuttall4b(ulong, ulong);
		static inline T Nuttall4c(ulong, ulong);

		static inline T Kaiser20(ulong, ulong);
		static inline T Kaiser25(ulong, ulong);
		static inline T Kaiser30(ulong, ulong);
		static inline T Kaiser35(ulong, ulong);
		static inline T Kaiser40(ulong, ulong);
		static inline T Kaiser45(ulong, ulong);
		static inline T Kaiser50(ulong, ulong);
		static inline T Kaiser55(ulong, ulong);
		static inline T Kaiser60(ulong, ulong);
		static inline T Kaiser65(ulong, ulong);
		static inline T Kaiser70(ulong, ulong);

		/* FLAT-TOP-WINDOWS */
		static inline T HFT116D(ulong, ulong);
		static inline T HFT248D(ulong, ulong);

		/* BAD */
		static inline T Rectangular(ulong, ulong);

	};

	/*
	 * TEMPLATE MEMBER FUNCTIONS -- DEFINITIONS
	 */
	/**
		Calculate the window values and calculate the scaling values S1 and S2.

		@param type window function to use
		@param N length of the window
		@param S1 sum over all window values
		@param S2 sum over all squared window values
		@return pointer to the calculated window values
	*/
	template <typename T>
	T * Windows<T>::Calculate_Window(const WINDOW_TYPE type, ulong N, T &S1, T &S2)
	{
		T * rt = new T[N];
		Windows<T>::Calculate_Window(type, N, rt, S1, S2);
		return rt;
	}
	/**
		Calculate the window values and calculate the scaling values S1 and S2.

		@param cwdw char array defining the window type
		@param N length of the window
		@param S1 sum over all window values
		@param S2 sum over all squared window values
		@return pointer to the calculated window values
	*/
	template <typename T>
	T * Windows<T>::Calculate_Window(const char *cwdw, ulong N, T &S1, T &S2)
	{
		T * rt = new T[N];
		Windows<T>::Calculate_Window(cwdw, N, rt, S1, S2);
		return rt;
	}
	/**
		Calculate the window values and calculate the scaling values S1 and S2.

		@param wdw pointer to the window function to use
		@param N length of the window
		@param S1 sum over all window values
		@param S2 sum over all squared window values
		@return pointer to the calculated window values
	*/
	template <typename T>
	T * Windows<T>::Calculate_Window(T(*wdw)(ulong, ulong), ulong N, T &S1, T &S2)
	{
		T * rt = new T[N];
		Windows<T>::Calculate_Window(wdw, N, w, S1, S2);
		return rt;
	}
	/**
		Calculate the window values and calculate the scaling values S1 and S2.

		@param type window function to use
		@param N length of the window
		@param w initialized pointer to the window array
		@param S1 sum over all window values
		@param S2 sum over all squared window values
	*/
	template <typename T>
	void Windows<T>::Calculate_Window(const WINDOW_TYPE type, ulong N, T *w, T &S1, T &S2)
	{
		T(*wdw)(ulong, ulong) = nullptr;
		switch (type)
		{
		case WINDOW_TYPE::BARTLETT: wdw = Windows<T>::Bartlett; break;
		case WINDOW_TYPE::WELCH: wdw = Windows<T>::Welch; break;
		case WINDOW_TYPE::HANNING: wdw = Windows<T>::Hanning; break;
		case WINDOW_TYPE::HAMMING: wdw = Windows<T>::Hamming; break;
		case WINDOW_TYPE::NUTTALL3: wdw = Windows<T>::Nuttall3; break;
		case WINDOW_TYPE::NUTTALL3A: wdw = Windows<T>::Nuttall3a; break;
		case WINDOW_TYPE::NUTTALL3B: wdw = Windows<T>::Nuttall3b; break;
		case WINDOW_TYPE::NUTTALL4: wdw = Windows<T>::Nuttall4; break;
		case WINDOW_TYPE::NUTTALL4A: wdw = Windows<T>::Nuttall4a; break;
		case WINDOW_TYPE::NUTTALL4B: wdw = Windows<T>::Nuttall4b; break;
		case WINDOW_TYPE::NUTTALL4C: wdw = Windows<T>::Nuttall4c; break;
		case WINDOW_TYPE::KAISER20: wdw = Windows<T>::Kaiser20; break;
		case WINDOW_TYPE::KAISER25: wdw = Windows<T>::Kaiser25; break;
		case WINDOW_TYPE::KAISER30: wdw = Windows<T>::Kaiser30; break;
		case WINDOW_TYPE::KAISER35: wdw = Windows<T>::Kaiser35; break;
		case WINDOW_TYPE::KAISER40: wdw = Windows<T>::Kaiser40; break;
		case WINDOW_TYPE::KAISER45: wdw = Windows<T>::Kaiser45; break;
		case WINDOW_TYPE::KAISER50: wdw = Windows<T>::Kaiser50; break;
		case WINDOW_TYPE::KAISER55: wdw = Windows<T>::Kaiser55; break;
		case WINDOW_TYPE::KAISER60: wdw = Windows<T>::Kaiser60; break;
		case WINDOW_TYPE::KAISER65: wdw = Windows<T>::Kaiser65; break;
		case WINDOW_TYPE::KAISER70: wdw = Windows<T>::Kaiser70; break;
		case WINDOW_TYPE::HFT116D: wdw = Windows<T>::HFT116D; break;
		case WINDOW_TYPE::HFT248D: wdw = Windows<T>::HFT248D; break;
		case WINDOW_TYPE::RECTANGULAR:
		default:
			wdw = Windows<T>::Rectangular; break;
		}

		Windows<T>::Calculate_Window(wdw, N, w, S1, S2);
	}
	/**
		Calculate the window values and calculate the scaling values S1 and S2.

		@param cwdw char array defining the window type
		@param N length of the window
		@param w initialized pointer to the window array
		@param S1 sum over all window values
		@param S2 sum over all squared window values
	*/
	template <typename T>
	void Windows<T>::Calculate_Window(const char *cwdw, ulong N, T *w, T &S1, T &S2)
	{
		WINDOW_TYPE wdw = ParseWindowType(cwdw);
		Calculate_Window(wdw, N, w, S1, S2);
	}

	/**
		Calculate the window values and calculate the scaling values S1 and S2.

		@param wdw pointer to the window function to use
		@param N length of the window
		@param w initialized pointer to the window array
		@param S1 sum over all window values
		@param S2 sum over all squared window values
	*/
	template <typename T>
	void Windows<T>::Calculate_Window(T(*wdw)(ulong, ulong), ulong N, T *w, T &S1, T &S2)
	{
		ulong i;

		// 0 and N/2 appear once, every other twice (symmetry)

		w[N / 2] = wdw(N / 2, N);
		S1 = w[N / 2];
		S2 = S1 * S1;

		w[0] = wdw(0, N);
		S1 += w[0];
		S2 += w[0] * w[0];

		for (i = 1; i < N / 2; ++i)
		{
			w[i] = wdw(i, N);
			w[N - i] = w[i];
			S1 += 2 * w[i];
			S2 += 2 * w[i] * w[i];
		}
	}

	/**
		Searches for an existing window type as enum and returns it.
		Default return is WINDOW_TYPE::RECTANGULAR.

		@param cwdw the char array to parse
		@return item of WINDOW_TYPE
	*/
	template <typename T>
	WINDOW_TYPE Windows<T>::ParseWindowType(const char *cwdw)
	{
		if (strcmp(cwdw, "BARTLETT") == 0) return WINDOW_TYPE::BARTLETT;
		else if (strcmp(cwdw, "WELCH") == 0) return WINDOW_TYPE::WELCH;
		else if (strcmp(cwdw, "HANNING") == 0) return WINDOW_TYPE::HANNING;
		else if (strcmp(cwdw, "HAMMING") == 0) return WINDOW_TYPE::HAMMING;
		else if (strcmp(cwdw, "NUTTALL3") == 0) return WINDOW_TYPE::NUTTALL3;
		else if (strcmp(cwdw, "NUTTALL3A") == 0) return WINDOW_TYPE::NUTTALL3A;
		else if (strcmp(cwdw, "NUTTALL3B") == 0) return WINDOW_TYPE::NUTTALL3B;
		else if (strcmp(cwdw, "NUTTALL4") == 0) return WINDOW_TYPE::NUTTALL4;
		else if (strcmp(cwdw, "NUTTALL4A") == 0) return WINDOW_TYPE::NUTTALL4A;
		else if (strcmp(cwdw, "NUTTALL4B") == 0) return WINDOW_TYPE::NUTTALL4B;
		else if (strcmp(cwdw, "NUTTALL4C") == 0) return WINDOW_TYPE::NUTTALL4C;
		else if (strcmp(cwdw, "KAISER20") == 0) return WINDOW_TYPE::KAISER20;
		else if (strcmp(cwdw, "KAISER25") == 0) return WINDOW_TYPE::KAISER25;
		else if (strcmp(cwdw, "KAISER30") == 0) return WINDOW_TYPE::KAISER30;
		else if (strcmp(cwdw, "KAISER35") == 0) return WINDOW_TYPE::KAISER35;
		else if (strcmp(cwdw, "KAISER40") == 0) return WINDOW_TYPE::KAISER40;
		else if (strcmp(cwdw, "KAISER45") == 0) return WINDOW_TYPE::KAISER45;
		else if (strcmp(cwdw, "KAISER50") == 0) return WINDOW_TYPE::KAISER50;
		else if (strcmp(cwdw, "KAISER55") == 0) return WINDOW_TYPE::KAISER55;
		else if (strcmp(cwdw, "KAISER60") == 0) return WINDOW_TYPE::KAISER60;
		else if (strcmp(cwdw, "KAISER65") == 0) return WINDOW_TYPE::KAISER65;
		else if (strcmp(cwdw, "KAISER70") == 0) return WINDOW_TYPE::KAISER70;
		else if (strcmp(cwdw, "HFT116D") == 0) return WINDOW_TYPE::HFT116D;
		else if (strcmp(cwdw, "HFT248D") == 0) return WINDOW_TYPE::HFT248D;
		else return WINDOW_TYPE::RECTANGULAR;
	}
	/**
		Returns the ideal overlap for a given window type.

		@param type the window as an enum item
		@return ideal overlap as float (0,1)
	*/
	template <typename T>
	float Windows<T>::IdealOverlap(const WINDOW_TYPE type)
	{
		switch (type)
		{
		case WINDOW_TYPE::BARTLETT: return 0.5f;
		case WINDOW_TYPE::WELCH: return 0.293f;
		case WINDOW_TYPE::HANNING: return 0.5f;
		case WINDOW_TYPE::HAMMING: return 0.5f;
		case WINDOW_TYPE::NUTTALL3: return 0.647f;
		case WINDOW_TYPE::NUTTALL3A: return 0.612f;
		case WINDOW_TYPE::NUTTALL3B: return 0.598f;
		case WINDOW_TYPE::NUTTALL4: return 0.705f;
		case WINDOW_TYPE::NUTTALL4A: return 0.68f;
		case WINDOW_TYPE::NUTTALL4B: return 0.663f;
		case WINDOW_TYPE::NUTTALL4C: return 0.656f;
		case WINDOW_TYPE::KAISER20: return 0.534f;
		case WINDOW_TYPE::KAISER25: return 0.583f;
		case WINDOW_TYPE::KAISER30: return 0.619f;
		case WINDOW_TYPE::KAISER35: return 0.647f;
		case WINDOW_TYPE::KAISER40: return 0.67f;
		case WINDOW_TYPE::KAISER45: return 0.689f;
		case WINDOW_TYPE::KAISER50: return 0.705f;
		case WINDOW_TYPE::KAISER55: return 0.719f;
		case WINDOW_TYPE::KAISER60: return 0.731f;
		case WINDOW_TYPE::KAISER65: return 0.741f;
		case WINDOW_TYPE::KAISER70: return 0.751f;
		case WINDOW_TYPE::HFT116D: return 0.782f;
		case WINDOW_TYPE::HFT248D: return 0.841f;
		case WINDOW_TYPE::RECTANGULAR:
		default:
			return 0.0f;
		}
	}

	template <typename T> inline
	T Windows<T>::Bartlett(ulong i, ulong N)
	{
		T z = (T)(2.0*((T)i / (T)N));
		if (z <= 1) return (T)(z);
		else return (T)(2 - z);
	}
	template <typename T> inline
	T Windows<T>::Welch(ulong i, ulong N)
	{
		T z = (T)(2.0*((T)i / (T)N) - 1);
		return (T)(1 - z * z);
	}
	template <typename T> inline
	T Windows<T>::Hanning(ulong i, ulong N)
	{
		T z = (T)(2.0*M_PI*((T)i / (T)N));
		return (T)(0.5 * (1 - cos(z)));
	}
	template <typename T> inline
	T Windows<T>::Hamming(ulong i, ulong N)
	{
		T z = (T)(2.0*M_PI*i / N);
		return (T)(0.54 - 0.46*cos(z));
	}
	template <typename T> inline
	T Windows<T>::Nuttall3(ulong i, ulong N)
	{
		T z = (T)(2.0*M_PI*((T)i / (T)N));
		return (T)(0.375 - 0.5*cos(z) + 0.125*cos(2 * z));
	}
	template <typename T> inline
	T Windows<T>::Nuttall3a(ulong i, ulong N)
	{
		T z = (T)(2.0*M_PI*((T)i / (T)N));
		return (T)(0.40897 - 0.5*cos(z) + 0.09103*cos(2 * z));
	}
	template <typename T> inline
	T Windows<T>::Nuttall3b(ulong i, ulong N)
	{
		T z = (T)(2.0*M_PI*((T)i / (T)N));
		return (T)(0.4243801 - 0.4973406*cos(z) + 0.0782793*cos(2 * z));
	}
	template <typename T> inline
	T Windows<T>::Nuttall4(ulong i, ulong N)
	{
		T z = (T)(2.0*M_PI*((T)i / (T)N));
		return (T)(0.3125 - 0.46875*cos(z) + 0.1875*cos(2 * z) - 0.03125*cos(3 * z));
	}
	template <typename T> inline
	T Windows<T>::Nuttall4a(ulong i, ulong N)
	{
		T z = (T)(2.0*M_PI*((T)i / (T)N));
		return (T)(0.338946 - 0.481973*cos(z) + 0.161054*cos(2 * z) - 0.018027*cos(3 * z));
	}
	template <typename T> inline
	T Windows<T>::Nuttall4b(ulong i, ulong N)
	{
		T z = (T)(2.0*M_PI*((T)i / (T)N));
		return (T)(0.355768 - 0.487396*cos(z) + 0.144232*cos(2 * z) - 0.012604*cos(3 * z));
	}
	template <typename T> inline
	T Windows<T>::Nuttall4c(ulong i, ulong N)
	{
		T z = (T)(2.0*M_PI*((T)i / (T)N));
		return (T)(0.3635819 - 0.4891775*cos(z) + 0.1365995*cos(2 * z) - 0.0106411*cos(3 * z));
	}

	template <typename T> inline
	T Windows<T>::Kaiser(ulong i, ulong N, T alpha)
	{
		const T z = (T)(2.0 * i / (T)N - 1.0);
		const T nom = boost::math::cyl_bessel_i((T)0, (T)(M_PI * alpha * sqrt(1 - z*z)));
		const T den = boost::math::cyl_bessel_i((T)0, (T)(M_PI * alpha));
		return nom / den;
	}
	template <typename T> inline T Windows<T>::Kaiser20(ulong i, ulong N) { return Kaiser(i, N, (T)2.0); }
	template <typename T> inline T Windows<T>::Kaiser25(ulong i, ulong N) { return Kaiser(i, N, (T)2.5); }
	template <typename T> inline T Windows<T>::Kaiser30(ulong i, ulong N) { return Kaiser(i, N, (T)3.0); }
	template <typename T> inline T Windows<T>::Kaiser35(ulong i, ulong N) { return Kaiser(i, N, (T)3.5); }
	template <typename T> inline T Windows<T>::Kaiser40(ulong i, ulong N) { return Kaiser(i, N, (T)4.0); }
	template <typename T> inline T Windows<T>::Kaiser45(ulong i, ulong N) { return Kaiser(i, N, (T)4.5); }
	template <typename T> inline T Windows<T>::Kaiser50(ulong i, ulong N) { return Kaiser(i, N, (T)5.0); }
	template <typename T> inline T Windows<T>::Kaiser55(ulong i, ulong N) { return Kaiser(i, N, (T)5.5); }
	template <typename T> inline T Windows<T>::Kaiser60(ulong i, ulong N) { return Kaiser(i, N, (T)6.0); }
	template <typename T> inline T Windows<T>::Kaiser65(ulong i, ulong N) { return Kaiser(i, N, (T)6.5); }
	template <typename T> inline T Windows<T>::Kaiser70(ulong i, ulong N) { return Kaiser(i, N, (T)7.0); }

	/* FLAT-TOP-WINDOWS */
	template <typename T> inline
	T Windows<T>::HFT116D(ulong i, ulong N)
	{
		T z = (T)(2.0*M_PI*((T)i / (T)N));
		return (T)(1 - 1.9575375*cos(z) + 1.4780705*cos(2 * z) - 0.6367431*cos(3 * z) + 0.1228389*cos(4 * z) - 0.0066288*cos(5 * z));
	}
	template <typename T> inline
	T Windows<T>::HFT248D(ulong i, ulong N)
	{
		T z = (T)(2.0*M_PI*((T)i / (T)N));
		return (T)((1 - 1.985844164102*cos(z) + 1.791176438506*cos(2 * z) - 1.282075284005*cos(3 * z) + 0.667777530266*cos(4 * z) - 0.240160796576*cos(5 * z) + 0.056656381764*cos(6 * z) - 0.008134974479*cos(7 * z) + 0.000624544650*cos(8 * z) - 0.000019808998*cos(9 * z) + 0.000000132974*cos(10 * z)));
	}

	template <typename T> inline
	T Windows<T>::Rectangular(ulong i, ulong N)
	{
		return (T)(1);
	}

}

#endif