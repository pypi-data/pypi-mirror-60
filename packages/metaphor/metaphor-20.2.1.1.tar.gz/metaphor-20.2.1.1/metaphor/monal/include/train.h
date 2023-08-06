/*
 C code library for neuron network training
 Librairie de code C pour l'apprentissage d'un r�seau de neurones
file:train.h
 */
#ifndef TRAIN_H
#define TRAIN_H

#include "nttype.h"

#define CTOL       1e-15 /*Tolerance de calcul*/
#define styleFitEx(a, b) ((a & b)? 1: 0)

real trainCost; /* Cout d'apprentissage */
real lastPRESS;

#ifdef __cplusplus      
	extern "C" {
#endif
	long inittrain(long*, long);

	real* initwithnegtarget(real*, real*, long, long*, long);

	long dosettrainstyle(long);

	long LeverageLimited();

	long Moderate();

    long leveragesprimecompute(Ttransferprime, real*, real*, real*, real*, real*,
    	real*, real*, long*, long, long, long,	real);

    real dogetcost(Ttransfer, real*, real*, real*, long*, long, long, long,
    		long, long*);

    real dogetpress(Ttransferprime, real*, real*, real*, real*, real*, real*,
    	    real*, long*, long, long, long, long*, real*, long, long, long*);

    real dogetpressex(Ttransferprime, real*, real*, real*, real*, real*, real*,
    		real*, real*, long*, long, long, long, long*, real*, long, long,
			long*);

	long dotrain(Ttransfer, Ttransferprime, real*, real*, real*, long, long,
		long*, long*, long, long, real*, long*, cbk, long, long*, long);

    real fullcompute(real*, real*, real*, real*, real*, long, long, long*,
			real*, long, long, long*);

    real residuals2cost(real*, long, long*);
	
	/* Module   : train
	 Mathod     : jacobian2gradient
	 Visibility : Public
	 Arguments  : */
	real* jacobian2gradient(real*, real*, real*, real**, long, long);

	/* Module   : train
	 Mathod     : getislin
	 Visibility : Public
	 Arguments  :
		Ttransferprime transferprime -> fonction de calcul de la sortie et du 
			gradient 
		long paramcount -> nombre de parametres 
		long modelcount -> nombre de donn�es ou de modeles
	 return : boolean model linearity
*/
	long getislin(Ttransferprime, long, long);

#ifdef __cplusplus
	};
#endif

#endif
