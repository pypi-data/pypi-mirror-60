/*---------------------------------------------------------------------------
file:%lNamel%dll.h
      
  Netral compiled model 
  Export library for training
  Started with Graph machine. June 2014
  J.L. PLOIX

---------------------------------------------------------------------------*/

#ifndef INTERFACETRAIN_H
#define INTERFACETRAIN_H

#define _FILE_OFFSET_BITS  64 // added 04-10-2019

#ifdef WIN
  #include <windows.h>
  #include <stddef.h>
#endif

// define calling convention
#define NTCALLCONV
#include "nttype.h"
//#include "%lNamel%trainbase.h"
#ifdef WIN
  #define EXPORT __declspec(dllexport)
#else
  #define EXPORT
#endif

#ifdef __cplusplus
	extern "C" {
#endif

int NTCALLCONV entrypoint()
EXPORT int NTCALLCONV init%lNamel%();
EXPORT int NTCALLCONV moduletype();
EXPORT int NTCALLCONV close();
EXPORT int NTCALLCONV codeversion();
EXPORT int NTCALLCONV dynamiclinking();
EXPORT int NTCALLCONV datarange(char*);
EXPORT long NTCALLCONV settrainstyle(long);
EXPORT long NTCALLCONV gettrainstyle();
EXPORT long NTCALLCONV gettraintype();
EXPORT int NTCALLCONV lasterror(char*);
EXPORT int NTCALLCONV monalVersion(char*);
EXPORT int NTCALLCONV configuration(char*);
EXPORT int NTCALLCONV linear();
EXPORT int NTCALLCONV baselen();
EXPORT int NTCALLCONV modelCount();
EXPORT int NTCALLCONV dataCount();
EXPORT int NTCALLCONV paramCount();
EXPORT int NTCALLCONV inputCount();
EXPORT int NTCALLCONV outputCount();
EXPORT int NTCALLCONV hidden();
EXPORT int NTCALLCONV moduleName(char*);
EXPORT int NTCALLCONV mark(char*);
EXPORT int NTCALLCONV base(char*);
EXPORT int NTCALLCONV created(char*);
EXPORT int NTCALLCONV getbiasbased(long*);
EXPORT int NTCALLCONV getoutlinks(long*);
EXPORT int NTCALLCONV getnames(long, long, char*);
EXPORT int NTCALLCONV setidentifier(long, char*);
EXPORT int NTCALLCONV getinputnorm(real*);
EXPORT int NTCALLCONV setinputnorm(real*);
EXPORT int NTCALLCONV getinputranges(real*);
EXPORT int NTCALLCONV getoutputranges(real*);
EXPORT int NTCALLCONV getinputs(real*);
EXPORT int NTCALLCONV getoutputs(real*);
EXPORT int NTCALLCONV getnorm(real*);
EXPORT int NTCALLCONV setnorm(real*);
EXPORT int NTCALLCONV getproperty(char*);
EXPORT int NTCALLCONV setproperty(char*);
EXPORT int NTCALLCONV getdebugfile(char*);
EXPORT int NTCALLCONV setdebugfile(char*);
EXPORT int NTCALLCONV getdata(long, real*);
EXPORT int NTCALLCONV gettargets(long, real*);
EXPORT int NTCALLCONV settargets(real*, long);
EXPORT int NTCALLCONV getresiduals(real*, long, real*);
EXPORT int NTCALLCONV getlastcost(real*);
EXPORT int NTCALLCONV getcost(real*, real*);
EXPORT int NTCALLCONV getpress(real*, real*, real*, real*, real*, real*,
		real*, long, long*);
EXPORT int NTCALLCONV transferindex(long, real*, real*);
EXPORT int NTCALLCONV transfergradientindex(long, real*, real*, real*);
EXPORT int NTCALLCONV transfergradientindex(long, real*, real*, real*);
EXPORT int NTCALLCONV getfreedomindex(long);
EXPORT int NTCALLCONV getjacobian(real*, long, real*, real*);
EXPORT int NTCALLCONV getprime(real*, long, real*);
EXPORT int NTCALLCONV seed(long);
EXPORT int NTCALLCONV getdirector(long*);
EXPORT int NTCALLCONV setdirector(long*);
EXPORT int NTCALLCONV settrainingset(long, long, real*);
EXPORT int NTCALLCONV setcallback(cbk);
EXPORT int NTCALLCONV train(real*, long*, long*, real*);
EXPORT int NTCALLCONV trainex(real*, long*, long*, real*, real*, real*,
		real*, real*, real*, real*, real*, real*, long*);
EXPORT int NTCALLCONV loaddatabase(real*, long, long);
#if MODELCOUNT <= 1
	EXPORT int NTCALLCONV xml(char*);
	EXPORT int NTCALLCONV transfer(real*, real*, real*);
	EXPORT int NTCALLCONV transfergradient(real*, real*, real*, real*);
	EXPORT int NTCALLCONV transferleverage(real*, real*, real*, real*, real*);
	#if TRAINABLE == 0
		EXPORT int NTCALLCONV reversetrain(real*, long*, real*, long*, long*, real*);
	#endif  // TRAINABLE == 0
#endif  // MODELCOUNT <= 1

#ifdef __cplusplus
	}
#endif 

#endif //INTERFACETRAIN_H
