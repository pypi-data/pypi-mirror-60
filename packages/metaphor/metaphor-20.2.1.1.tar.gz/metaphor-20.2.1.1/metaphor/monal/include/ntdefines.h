/*
file:ntdefines.h
 *
 *  Created on: 20 oct. 2012
 *      Author: jeanluc
 */

#ifndef ntdefines_H
#define ntdefines_H

#ifdef linux
#define UNIX
#else
#ifdef linux
#define UNIX
#else
#ifdef Win32
#define WIN
#else
#ifdef Win64
#define WIN
#else
#ifdef WINNT
#define WIN
#endif
#endif
#endif
#endif
#endif

#endif

