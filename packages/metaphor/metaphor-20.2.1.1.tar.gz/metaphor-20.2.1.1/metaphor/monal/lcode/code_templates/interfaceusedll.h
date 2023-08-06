/*---------------------------------------------------------------------------
file:%lNamel%dll.h
      
  Netral compiled model 
  Export library for usage
  Started with Graph machine. June 2014
  J.L. PLOIX

---------------------------------------------------------------------------*/
#ifndef INTERFACEUSE_H
#define INTERFACEUSE_H

#ifdef WIN
  #include <windows.h>
  #include <stddef.h>
#endif
// define calling convention
#define NTCALLCONV
#include "nttype.h"
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
	EXPORT int NTCALLCONV lasterror(char* target);
	EXPORT int NTCALLCONV getnames(long, long, char*);
	EXPORT int NTCALLCONV monalVersion(char*);
	EXPORT int NTCALLCONV paramCount();
	EXPORT int NTCALLCONV inputCount();
	EXPORT int NTCALLCONV outputCount();
	EXPORT int NTCALLCONV hidden();
	EXPORT int NTCALLCONV modelName(char*);
	EXPORT int NTCALLCONV moduleName(char*);
	EXPORT int NTCALLCONV dimension();
	EXPORT int NTCALLCONV trainbase(char*);
	EXPORT int NTCALLCONV mark(char*);
	EXPORT int NTCALLCONV created(char*);
	EXPORT int NTCALLCONV smiles(char*);
	EXPORT int NTCALLCONV configuration(char*);
	EXPORT int NTCALLCONV getnorm(real*);
	EXPORT int NTCALLCONV setnorm(real*);
	EXPORT int NTCALLCONV getproperty(char*);
	EXPORT int NTCALLCONV setproperty(char*);
	EXPORT int NTCALLCONV seed(long);
	EXPORT int NTCALLCONV transfer(real*%realptrdecl%, real*, real*); //"params", "output", "outnorm"
	EXPORT int NTCALLCONV transferprime(real*%realptrdecl%, real*, real*, real*);  //"params", "output", "gradient", "outnorm"
	EXPORT int NTCALLCONV transferleverage(real*%realptrdecl%, real*, real*, real*);  //"params", "output", "leverage", "outnorm"
	EXPORT int NTCALLCONV transferleverageex(real*, real*%realptrdecl%, real*, real*, real*, real*);  //"params", "disp", "output", "gradient", "leverage", "outnorm"
//	EXPORT int NTCALLCONV transferleverage2(real*%realptrdecl%, real*, real*, real*);  //"params", "output", "leverage", "outnorm"
	EXPORT int NTCALLCONV getstddev(real*);  //"target"
	EXPORT int NTCALLCONV setstddev(real);  //"source"
	EXPORT int NTCALLCONV getparams(real*);  //"target"
	EXPORT int NTCALLCONV setparams(real*, long);  //"source"
	EXPORT int NTCALLCONV getwused(long*);  //"target"
	EXPORT int NTCALLCONV getfreedom(long);  //"style"
	EXPORT int NTCALLCONV getdispersion(real*);  //"target"
	EXPORT int NTCALLCONV setdispersion(real*, long);  //"source"
//	EXPORT int NTCALLCONV gethalfdispersion(real*);  //"target"
//	EXPORT int NTCALLCONV sethalfdispersion(real*, long);  //"source"
	EXPORT int NTCALLCONV getbaselen();  //"target" 
	EXPORT int NTCALLCONV setbaselen(long);  // "value"
	
#ifdef __cplusplus
	}
#endif 

#endif //INTERFACEUSE_H
