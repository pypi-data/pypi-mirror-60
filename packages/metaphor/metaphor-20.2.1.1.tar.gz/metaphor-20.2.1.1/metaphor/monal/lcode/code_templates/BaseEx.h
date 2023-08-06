/*
file:%lNamel%.h
   C code transfer functions for Neuron Network
*/
#ifndef %UNameU%_BASE_H
#define %UNameU%_BASE_H

  #define %UNameU%INPUTS     %Inputs%
  #define %UNameU%OUTPUTS    %Outputs%
  #define %UNameU%INOUTPUTS  %InOutputs%
  #define %UNameU%SYNAPSES   %Synapses%
  #define %UNameU%DIMENSION  %Dimension%
  #define %UNameU%NODES      %Nodes%
  #define %UNameU%ORDER      0
  #define %UNameU%COMMENTS   %CommentCount%

  #include "nttype.h"

#ifdef __cplusplus      
  extern "C" {
#endif

  char *%lNamel%comments[%UNameU%COMMENTS];	
  %InputRangesProto%
  real %lNamel%outrange[%UNameU%OUTPUTS][2];
  real %lNamel%wrange[%UNameU%SYNAPSES][2];

  void %lNamel%transferw(real*%realptrdecl%, real*);
  /*Module   : %lNamel%base
  Method     : %lNamel%transferw
  Visibility : Public
  Arguments  : weights: real* -> les poids courants
               inputs: real* -> variables d'entr�e
               outputs: real* -> variables de sortie

  Description: Effectue le transfert par le r�seau. */

  void %lNamel%transfergradientw(real*%realptrdecl%, real*, real*%int_indexoutput%);//
  /*Module   : %lNamel%grd
  Method     : %lNamel%transfergradient
  Visibility : Public
  Arguments  : weights: parametres courants
			   inputs: real* -> variables d'entr�e
               outputs: real* -> variables de sorties
               gradient: real* -> vecteur gradient
              

  Description: Effectue un transfert � travers le r�seau, et calcule le gradient.

  Note : Pour un r�seau statique, le calcul du gradient est fait par
    r�tropropagation */
	
  void %lNamel%transfergradientw1(real*%realptrdecl%, real*, real*, int%int_indexoutput%);//
  /*Module   : %lNamel%grd
  Method     : %lNamel%transfergradient
  Visibility : Public
  Arguments  : weights: parametres courants
			   inputs: real* -> variables d'entr�e
               outputs: real* -> variables de sorties
               gradient: real* -> vecteur gradient
               internini: int -> initialisation de la d�riv�e

  Description: Effectue un transfert � travers le r�seau, et calcule le gradient.

  Note : Pour un r�seau statique, le calcul du gradient est fait par
    r�tropropagation */
	
  void %lNamel%transfergradientinputw(real*%realptrdecl%, real*, real*, real*);//
  /*Module   : %lNamel%grd
  Method     : %lNamel%transfergradient
  Visibility : Public
  Arguments  : weights: parametres courants
			   inputs: real* -> variables d'entr�e
               outputs: real* -> variables de sorties
               gradient: real* -> vecteur gradient
               iniback: real* -> initialisation de la d�riv�e

  Description: Effectue un transfert � travers le r�seau, et calcule le gradient.

  Note : le calcul du gradient est fait par r�tropropagation */

  char *%lNamel%inputname(long);
  /*Module   : %lNamel%tfr
  Method     : %lNamel%inputname
  Visibility : Public
  Arguments  : index: long -> le rang de l'entr�e
  Return     : char* -> le nom de l'entr�e vis�e

  Description: retourne le nom de l'entr�e vis�e. */

  real *%lNamel%inputrange(long);
  /*Module   : %lNamel%tfr
  Method     : %lNamel%inputrange
  Visibility : Public
  Arguments  : index: long -> le rang de l'entr�e
  Return     : real* -> pointeur sur le tableau des valeurs Min et Max

  Description: retourne les valeurs min et max de l'entr�e vis�e. Ces valeurs
    sont celles constat�es lors de l'apprentissage */

  real *%lNamel%outputrange(long);
  /*Module   : %lNamel%tfr
  Method     : %lNamel%outputrange
  Visibility : Public
  Arguments  : index: long -> le rang de la sortie
  Return     : real* -> pointeur sur le tableau des valeurs Min et Max

  Description: retourne les valeurs min et max de la sortie vis�e. Ces valeurs
    sont celles constat�es lors de l'apprentissage */

 #ifdef __cplusplus      
  }
#endif

#endif  // %UNameU%_BASE_H
 