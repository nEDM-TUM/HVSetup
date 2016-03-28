#include <stdio.h>
#include <math.h>
#define TWOPI 6.28318530717959
int main(void)
{
	double fs = 10000; /* sampling frequency [Hz] */
	double f1 = 234.32432; /* first signal frequency [Hz] */
	double amp1 = 2.82842712474619; /* 2 Vrms */
	double f2 = 2132.00000001; /* second signal frequency [Hz] */
	double amp2 = 5.0E-4 * sqrt(2.); /* 0.707 Vrms */
	double ulsb = 1e-3; /* Value of 1 LSB in Volt */
	int i;
	double t, u, ur;
	FILE *pFile;
	char *fname = "data.bin";
	remove(fname);
	fopen_s(&pFile, fname, "wb");
	for (i = 0; i < 1000000; i++)
	{
		t = (double)i / fs;
		u = amp1 * sin(TWOPI * f1 * t) + amp2 * sin(TWOPI * f2 * t + 1.345);
		ur = floor(u / ulsb + 0.5) * ulsb; /* Rounding */
		//printf("%10.6f %8.5f\n", t, ur); /* ASCII output */

		fwrite(&ur, sizeof(double), 1, pFile); /* alternative binary output */
	}
	fclose(pFile);




	return 0;
}