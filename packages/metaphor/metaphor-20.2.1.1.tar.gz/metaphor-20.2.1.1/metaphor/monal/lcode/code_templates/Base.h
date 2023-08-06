/*  
file:%lNamel%_.h
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
  #define %UNameU%HIDDEN     %Hidden%
  #define %UNameU%ORDER      0
  #define %UNameU%COMMENTS   %CommentCount%
  #define %UNameU%CONFIG     "%Configuration%"
  #define %UNameU%BASE       "%Originbase%"
  #define %UNameU%NAME       "%ModelName%"
  #define %UNameU%MODULE     "%lNamel%"
  #define %UNameU%SMILES     "%Smiles%"

  #include "nttype.h"

#ifdef __cplusplus      
  extern "C" {
#endif

  char *%lNamel%comments[%UNameU%COMMENTS];	
  long %lNamel%wused[%UNameU%SYNAPSES];
  char *%lNamel%wnames[%UNameU%SYNAPSES];
  %InputNamesProto%
  char *%lNamel%outputnames[%UNameU%OUTPUTS];

  void %lNamel%transfer(real*%realptrdecl%, real*, real*);
  /*Module   : %lNamel%base
  Method     : %lNamel%transferw
  Visibility : Public
  Arguments  : weights: real* -> les poids courants
               (inputs: real* -> seulement si pertinent. variables d'entree)
               outputs: real* -> variables de sortie
			   outputnorm: real* -> normalisation de sortie

  Description: Effectue le transfert par le reseau. */

  void %lNamel%transfergradient(real*%realptrdecl%, real*, real*, real*%int_indexoutput%);
  /*Module   : %lNamel%grd
  Method     : %lNamel%transfergradient
  Visibility : Public
  Arguments  : weights: parametres courants
			   (inputs: real* -> seulement si pertinent. variables d'entree)
               outputs: real* -> variables de sorties
               gradient: real* -> vecteur gradient
			   outnorm: real* -> normalisation de sortie
               internini: int -> initialisation de la derivee
			   (indexoutput: int -> seulement si pertinent. Numero de la sortie visee pour le gradient)

  Description: Effectue un transfert a travers le reseau, et calcule le gradient.

  Note : Pour un reseau statique, le calcul du gradient est fait par
    retropropagation */
	
 #ifdef __cplusplus      
  }
#endif

#endif  // %UNameU%_BASE_H
 
