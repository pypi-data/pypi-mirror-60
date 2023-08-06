/*
file:%lNamel%usebase.h
  Interface d'exportation des fonctions d'utilisation d'un modele

*/
#ifndef %UNameU%_USEBASE_H
#define %UNameU%_USEBASE_H

#include "nttype.h"

#define %UNameU%EXTRAWEIGHTS %ExtraWeightCount%
#define INPUTCOUNT   %Inputs%
#define OUTPUTCOUNT  %Outputs%
#define PARAMCOUNT   %Synapses%
#define DIMENSION    %Dimension%
#define CODEVERSION %codeversion%
#define HIDDEN        %Hidden%
#define NODECOUNT      %Nodes%
#define COMMENTCOUNT %CommentCount%
#define SMILES       "%Smiles%"
#define BASE         "%Originbase%"
#define CONFIG     "%Configuration%"

#ifdef __cplusplus      
	extern "C" {
#endif

	real params[PARAMCOUNT]; 
	real dispersionmem[PARAMCOUNT * PARAMCOUNT];
	real halfdispersion[PARAMCOUNT * DIMENSION];
	long usedweights[PARAMCOUNT];
	real outputnorm[2];
	real trainstddev;
	char pptyBuffer[BUFFERSIZE];
	char fullmoduleBuffer[BUFFERSIZE];
	long baselen;
    char *readnames(int, int);
	void inituse();  
	void freeuse();
	char *readproperty();
	char *writeproperty(char*);
	int modeltransfer(real*%realptrdecl%, real*, real*);
	int modeltransferprime(real*%realptrdecl%, real*, real*, real*);  //"params", ?"input", "output", "gradient", "outnorm"

#ifdef __cplusplus      
	}
#endif

#endif  // %UNameU%_USEBASE_H
