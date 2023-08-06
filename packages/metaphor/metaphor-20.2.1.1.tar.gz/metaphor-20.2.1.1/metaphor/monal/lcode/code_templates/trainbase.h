/*
file:%lNamel%trainbase.h
  Interface d'exportation des fonctions d'apprentissage d'une base de modeles

Base utilisee : %lNamel%

 */
#ifndef %UNameU%_TRAINBASE_H
#define %UNameU%_TRAINBASE_H

#define MODULENAME     "%lNamel%"
#define TRAINABLE      %trainable%
#define NODECOUNT      %Nodes%
#define MODELCOUNT     %modelcount%
#define PARAMCOUNT     %Synapses%
#define BIASBASEDCOUNT %biasbasedcount%
#define OUTPUTSYNCOUNT %outputsynCount%
#define INPUTCOUNT     %Inputs%
#define OUTPUTCOUNT    %Outputs%
#define HIDDEN         %Hidden%
#define LINEAR         %linear%
#define CODEVERSION    %codeversion%
#define DYNAMICLINKING %dynamiclinking%
#define NLWCOUNT PARAMCOUNT - OUTPUTSYNCOUNT
#define NAMEBUFFERSIZE 64
#define CONFIG         "%Configuration%"
#if TRAINABLE == 0
  #define EXTRAWEIGHTS   %ExtraWeightCount%
  #define DIMENSION      %Dimension%
  #define SMILES         "%Smiles%"
  #define BASE           "%Originbase%"
#endif

//#define DEBUG

#define SUPERTYPE 1

#include "nttype.h"

#ifdef __cplusplus
  extern "C" {
#endif

/* Definition des types de fonction de transfert de modele */
#if MODELCOUNT > 1
    #if INPUTCOUNT
        typedef void (*tmultitransfer)(real*, real*, real*, real*);
        typedef void (*tmultitransferprime)(real*, real*, real*, real*, real*);
    #else
        typedef void (*tmultitransfer)(real*, real*, real*);
        typedef void (*tmultitransferprime)(real*, real*, real*, real*);
    #endif 
#endif // MODELCOUNT > 1
    real registeredinputs[INPUTCOUNT];
	real registeredWeights[PARAMCOUNT];
	real registereddispersion[PARAMCOUNT * PARAMCOUNT];
#if TRAINABLE == 0
	real inputrange[INPUTCOUNT][2];
	real outputrange[OUTPUTCOUNT][2];
	real outputs[OUTPUTCOUNT];
	real outputrange[OUTPUTCOUNT][2];
	real trainStd;
	real mu;
	real trainStudent95;
	#if EXTRAWEIGHTS > 0
		real registeredExtraWeights[EXTRAWEIGHTS * PARAMCOUNT];
		real registeredExtraDispersion[EXTRAWEIGHTS * PARAMCOUNT * PARAMCOUNT];
	#endif
#endif

#if MODELCOUNT <= 1
	void singletransfer(real*, real*, real*, real*);
	void singletransferprime(real*, real*, real*, real*, real*);
	void singletransferinputprime(real*, real*, real*, real*, real*);
#if TRAINABLE == 0
	void transferinputprime(real*, real*, real*, real*, long*, long, long*, long, long);
	void transfersinglewrapper(real*, real*, real*, long*, long, long);
#endif
    char* XML;
#else
    tmultitransfer multitransfers[MODELCOUNT];
    tmultitransferprime multitransferprimes[MODELCOUNT];
#endif // MODELCOUNT <= 1

	real *negtargets;
	real *negtargetsmem;
	long *director;
	long ldir;
	real **datatable;
    char **identifier;
	long datacount;
	long inputcount;
	real outputnorm[2];
	real inputnorm[INPUTCOUNT][2];
	long biasbased[BIASBASEDCOUNT];
	long outputsyn[OUTPUTSYNCOUNT];
	long nlinwlist[NLWCOUNT];
	char pptyBuffer[BUFFERSIZE];
	real curWeight[PARAMCOUNT];

	void registerInputs(real*);
	void registerWeights(real*);
	void registerDispersion(real*);
	void initbase();
	void inittrainbase(long, long);
	int writetraindata(real*, long, long);
	void freetrainbase();
	int readdata(long, real*);
	char *readproperty();
	char *writeproperty(char*);
	real *readtargets(real*);
	real readtarget(long);
	void writetargets(real*, int);
	char *readnames(int, int);
	int writeidentifier(long, char*);
	long dosettrainingset(int, int, real*);
	void transferbase(real*, real*, real*, long*, long, long);
	void transferprime(real*, real*, real*, real*, long*, long, long*, long, long);
	void transferex(real*, real*, real*, long*, long, long);
	void transferprimeex(real*, real*, real*, real*, long*, long, long*, long, long);

#ifdef __cplusplus      
  }
#endif

#endif  // %UNameU%_TRAINBASE_H
