/* 
file:nttype.h
Include file for data <B>real</B> type definition. */
#ifndef _NETRALTYPE
#define _NETRALTYPE
#include <stdio.h>

#define DEBUG

#define FDACC 1E-5

#define HELPFILE "dlmdriverhelp.txt"
#ifdef WIN
	#define FSEP 92
#else
	#define FSEP 47
#endif

#define NPI 0
#define NSIGMA 1

/* Define the size of buffer */
/* Definit la taille du buffer */
#define BUFFERSIZE 2048

/* define the name of the weight section in weight files */
/* definit le nom de la section Poids dans le fichier de poids */
#define WEIGHTS "weights"

/* define the name of dispersion section in weight files */
/* definle nom de la section Dispersion dans le fichier de poids */
#define DISPERSION "dispersion"

// file analysis param
// Parametre d'analyse de fichier
#define COUNT "count"

#define STDDEV "stddev"

#define STUDENT "student"

#define VERBOSE 0 /* Verbose compiler constant. */
#define FRENCH
#define INF 1E308

#define code_toohighcost      1
#define code_dataaccessdenied 2
#define code_dvserror         3
#define code_reverseerror     4
#define code_finished         5
#define MAXWEIGHT  100   /*valeur max des poids*/
#define MAXCOST    1e100 /*Co�t maximum*/
#define square(x)  x*x
#define TRS_STD 0
#define TRS_BOOTSTRAP 1
#define TRS_LOO 2

/* Constants for getinfo */
#define ID_INPUT 1
#define ID_OUTPUT 2
#define ID_SYNAPSE 3
#define ID_ORDER 4
#define ID_LINEARITY 5
#define ID_COMMENTCOUNT 6
#define ID_DIMENSION 7

#define TFR_STD 0  /* Constantes pour le transfer */
#define TFR_GRADIENT 1
#define TFR_LEVERAGE 2
#define TFR_GRADIENTLEVERAGE 3
#define TFR_GRADIENTCONFIDENCE 4
#define TFR_GRADIENTINPUTS 5
#define TFR_GRADIENTHESSIAN 6

//#define RD_COST 1
#define RD_FINITEDIFF 2
#define RD_STUDENT 3
#define RD_STDDEV 4

#define VD_PARAM 1
#define VD_DISPERSION 2
#define VD_EXPERIMENTALSPACE 3
#define VD_PARAMSPACE 4

#define SD_MODELNAME 0
#define SD_INPUTNAME 1
#define SD_OUTPUTNAME 2
#define SD_PARAMNAME 3
#define SD_SMILES 4
#define SD_PROPERTY 5
#define SD_FULLMODULE 6
#define SD_MODULENAME 255

/* constante de style de calcul train, getcost, getprime, */
/* idem monalconst */
#define CS_MODERATE            0x0001  // 1
#define CS_LIMITED_LEVERAGE    0x0002  // 2
#define CS_SUPER_TRAIN         0x0004  // 4
#define CS_USE_DEBUGFILE_COST  0x0100  // 256
#define CS_USE_DEBUGFILE_PRIME 0x0200  // 512
#define CS_USE_DEBUGFILE_PRESS 0x0400  // 1024
#define CS_USE_DEBUGFILE_TRAIN 0x0800  // 2048
#define CS_DEBUG_SUPER_TRAIN   0x1000  // 4096
#define CS_DEBUG_MULTITRAIN    0x2000  // 8192

/* Display messages */
/* Messages d'affichage */ 
#ifdef FRENCH
  #define ST_USAGEWITH   "%s utilisation avec %s\n"
  #define ST_COMPUTED    "calcule_"
  #define ST_COMPUTEDS   "c_"
  #define ST_COMPUTED_   "%scalcule_%s"
  #define ST_RESIDUALS   "r_"
  #define ST_LEVERAGE_   "%slevier_%s"
  #define ST_LEVERAGE    "levier_"
  #define ST_LEVERAGES    "l_"
  #define ST_ERRORFD     "erreur dans le fichier %s\nligne %ld\ndonnee %ld/%ld\n"
  #define ST_DATASTD     "donnee : %s \necart type = "
  #define ST_ERRORSTD    "co�t d'apprentissage : %20.16f\n"
  #define ST_SOURCENO    "fichier source %s ne peut etre ouvert.\n"
  #define ST_TARGETNO    "fichier cible %s ne peut etre ouvert.\n"
  #define ST_USEHIST     "histoire de l'utilisation\n"
  #define ST_TRAINHIST   "%s histoire de l'apprentissage %ld/%ld\n"
  #define ST_PRESSANYK   "pressez une touche pour fermer.\n"
  #define ST_SIZEERRPOR  "erreur de dimension: \nlecture entrees + sorties : %ld\nvaleurs code : %ld\n"
  #define ST_DATALOADING "%s - Chargement des donnees\n"
  #define ST_DATALOADED  "fichier de donnees[%ld] %s - Total lignes %ld\n"
  #define ST_DATALOADEDL "fichier de donnees[%ld] %s - lignes %ld"
  #define ST_TOTALLINE   "total lignes %ld"
  #define ST_TRAINING    "Apprentissage %ld/%ld\n"
  #define ST_STRAINING   "%s Apprentissage %ld/%ld\n"
  #define ST_ENDTRAINING "fin d'apprentissage %ld"
  #define ST_DATAFIELDS  "champs de donnees : "
  #define ST_COSTL       "%ld - cout(%ld/%ld) = %20.16g  %20.16g\t%ld\n"
  #define ST_COSTS       "%ld - cout(%ld/%ld) = %20.16g\t%f\n"
  #define ST_FIRDSTDATA  "premiere ligne de donnees\n"
  #define ST_PILENULL    "pile NULL\n"
  #define ST_NEGDEL      "retard n�gatif\n" 
  #define ST_HIGHDEL     "retard %ld, sup�rieur � %ld\n"
  #define ST_FILEFILELINE "%ld lignes dans le fichier %s\n"
  #define ST_TOTFILELINE "nombre total de lignes %ld\n"
  #define ST_ERRORGENSTD  "cout de generalisation : %20.16f\n"
  #define ST_STARTINGCOST "cout initial           : %20.16g\n"
  #define ST_ENDINGCOST   "cout final             : %20.16g\n"
  #define ST_JACOBRANK    "rang du jacobien       : %5.3g\n"
  #define ST_COST         "\tcout[%ld] : %20.16g\n"
  #define ST_STDDEV       "\tecart type : %20.16g\n"
  #define ST_UNREACHFILE  "le fichier %s est introuvable.\n"
#else
  #define ST_USAGEWITH   "%s usage with %s\n"
  #define ST_COMPUTED    "computed_"
  #define ST_COMPUTEDS   "c_"
  #define ST_COMPUTED_   "%scomputed_%s"
  #define ST_RESIDUALS   "r_"
  #define ST_LEVERAGE_   "%sleverage_%s"
  #define ST_LEVERAGE    "leverage_"
  #define ST_LEVERAGES    "l_"
  #define ST_ERRORFD     "error in file %s\nline %ld\ndata %ld/%ld\n"
  #define ST_DATASTD     "data : %s \nstandard deviation = "
  #define ST_ERRORSTD    "training cost : %20.16f\n"
  #define ST_SOURCENO    "source file %s cannot be open.\n"
  #define ST_TARGETNO    "target file %s cannot be open.\n"
  #define ST_USEHIST     "usage history\n"
  #define ST_TRAINHIST   "%s history train %ld/%ld\n"
  #define ST_PRESSANYK   "press any key to close.\n"
  #define ST_SIZEERRPOR  "size error: \nread inputs + outputs : %ld\ncode values : %ld\n"
  #define ST_DATALOADING "%s - Data loading\n"
  #define ST_DATALOADED  "datafile[%ld] %s - Total lines %ld\n"
  #define ST_DATALOADEDL "datafile[%ld] %s - lines %ld"
  #define ST_TOTALLINE   "total lines %ld"
  #define ST_TRAINING    "training %ld/%ld\n"
  #define ST_STRAINING   "%s training %ld/%ld\n"
  #define ST_ENDTRAINING "end training %ld"
  #define ST_DATAFIELDS  "data fields : "
  #define ST_COSTL       "%ld - cost(%ld/%ld) = %20.16g  %20.16g\t%ld\n"
  #define ST_COSTS       "%ld - cost(%ld/%ld) = %20.16g\t%f\n"
  #define ST_FIRDSTDATA  "first data line\n"
  #define ST_PILENULL    "heap NULL\n"
  #define ST_NEGDEL      "negative delay\n" 
  #define ST_HIGHDEL     "delay %ld, higher than %ld\n"
  #define ST_FILEFILELINE "%ld lines in the file %s\n"
  #define ST_TOTFILELINE  "total line %ld\n"
  #define ST_ERRORGENSTD  "generalisation cost : %20.16f\n"
  #define ST_STARTINGCOST "initial cost        : %20.16g\n"
  #define ST_ENDINGCOST   "final cost          : %20.16g\n"
  #define ST_JACOBRANK    "jacobian rank       : %5.2g\n"
  #define ST_COST         "\tcost[%ld] : %20.16g\n"
  #define ST_STDDEV       "\tstandard deviation : %20.16g\n"
  #define ST_UNREACHFILE  "file %s cannot be found.\n"
#endif
 
 /*
   real variable type
   
   Description
   The type <B>real</B> is defined on each machine. Depending upon 
   the available accuracy, this type may one of the following :
   
	   * <B>double</B>
       * <B>float64</B>
       * other                                               

   type de variable r�elle
   
   Description
   Le type <B>real</B> est d�fini pour chaque machine. Selon la
   pr�cision de calcul disponible, ce type sera l'un des
   suivants :
   
       * <B>double</B>
       * <B>float64</B>
       * autre                                               */
 
#ifdef _64BITS  
  //typedef float_64 real;
  typedef double real;
#else  
  typedef double real;
#endif 

/* Enumeration of train end causes */
/* Enumeration des motifs de fin d'apprentissage */
enum ttrainend {
	teNone = 0, teTarget, teEpoch, teAccuracy, teHighWeight, teError,
	teUserDemand
};

/* Definition du type fonction de callback interne*/
typedef long (*cbk)(real, long);
/* Definition des types de fonction de transfert globales */
typedef void (*Ttransfer)(real*, real*, real*, long*, long, long);
typedef void (*Ttransferprime)(real*, real*, real*, real*, long*, long, long*, long, long);
	

#endif
