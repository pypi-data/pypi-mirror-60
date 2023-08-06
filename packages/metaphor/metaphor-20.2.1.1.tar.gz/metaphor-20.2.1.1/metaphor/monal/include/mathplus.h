/*
file:mathplus.h
  Fonctions math�matiques additionnelles

*/

#ifndef _MATHPLUS
/* file:mathplus.h file marker */
#define _MATHPLUS

#ifdef __cplusplus      
  extern "C" {
#endif
	int reducevec(double*, double*, long*, long);
	int reducemat(double*, double*, long*, long, long, long);
  	double ztMz0(double*, double*, long);
	double ztMz(double*, double**, long);
	double ztHMz0(double*, double*, long, long);
	double erfd(double);
	double erfd2(double);
    double erf_(double);
#ifdef __cplusplus      
  }
#endif

#endif
