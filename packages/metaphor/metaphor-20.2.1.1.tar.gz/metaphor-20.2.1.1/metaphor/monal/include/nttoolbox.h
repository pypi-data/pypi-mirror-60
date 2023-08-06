/* 
file:nttoolbox.h
Include file for
utilities definition
 */
// ---------------------------------------------------------------------------

#ifndef nttoolboxH
#define nttoolboxH

#define mindex(i,j) (i>j)?(j+i*(i+1)/2):(i+j*(j+1)/2)
#include <stdio.h>

#include "nttype.h"

real* dot0(real**, real* , long, real*, int);

void getSortedIndexes(real*, long*, long, int, int);

void insertionSort(real a[], int, int);

void selectionSort(real*, int, int);

long reverseindex(long dim, long*row);

/* checking is the file exists */
long fileexists(char*fname);

/* Looking for the number of useful data lines in a csv file */
long numlines( char *fname);

long int xtol(const char*);

/* Performing str to float conversion with an optional extra decimal separator */
long double atofex(const char*, int *valid);

char* trimright(char*);

int checkkey(char* key, int target, char* buffer, int size, FILE *file);

int feeddblarray(double* target, int arraysize, char* buffer, int buffersize, char** names, FILE *file);

char* getfieldvaluesstr(char* buffer, real* source, char* sep,
	unsigned long dim);

char *trainhistoryfile(char*, char* , char* , long );

char *curusefile(char *dest, char* apath, char* aname, long index);

char *curfile(char *dest, char* apath, char* aname, long index);

char *usehistoryfile(char *dest, char* apath, char* aname);

char *bestweightfile(char *dest, char* apath, char* aname);

char* datatablefile(char *dest, char* apath);

char* stripfilename(char* dest, char* source, char* sub);

int hasinarg(char* target, int argc, char* argv[], int limited);

int file2stream(char* filename, FILE* stream);
// ---------------------------------------------------------------------------
#endif

