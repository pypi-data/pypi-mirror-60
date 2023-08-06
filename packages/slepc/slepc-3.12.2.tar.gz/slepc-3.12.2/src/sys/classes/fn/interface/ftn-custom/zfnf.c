/*
   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   SLEPc - Scalable Library for Eigenvalue Problem Computations
   Copyright (c) 2002-2019, Universitat Politecnica de Valencia, Spain

   This file is part of SLEPc.
   SLEPc is distributed under a 2-clause BSD license (see LICENSE).
   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
*/

#include <petsc/private/fortranimpl.h>
#include <slepc/private/slepcimpl.h>
#include <slepc/private/fnimpl.h>

#if defined(PETSC_HAVE_FORTRAN_CAPS)
#define fnview_                    FNVIEW
#define fnsetoptionsprefix_        FNSETOPTIONSPREFIX
#define fnappendoptionsprefix_     FNAPPENDOPTIONSPREFIX
#define fngetoptionsprefix_        FNGETOPTIONSPREFIX
#define fnsettype_                 FNSETTYPE
#define fngettype_                 FNGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE)
#define fnview_                    fnview
#define fnsetoptionsprefix_        fnsetoptionsprefix
#define fnappendoptionsprefix_     fnappendoptionsprefix
#define fngetoptionsprefix_        fngetoptionsprefix
#define fnsettype_                 fnsettype
#define fngettype_                 fngettype
#endif

SLEPC_EXTERN void PETSC_STDCALL fnview_(FN *fn,PetscViewer *viewer,PetscErrorCode *ierr)
{
  PetscViewer v;
  PetscPatchDefaultViewers_Fortran(viewer,v);
  *ierr = FNView(*fn,v);
}

SLEPC_EXTERN void PETSC_STDCALL fnsetoptionsprefix_(FN *fn,char *prefix PETSC_MIXED_LEN(len),PetscErrorCode *ierr PETSC_END_LEN(len))
{
  char *t;

  FIXCHAR(prefix,len,t);
  *ierr = FNSetOptionsPrefix(*fn,t);if (*ierr) return;
  FREECHAR(prefix,t);
}

SLEPC_EXTERN void PETSC_STDCALL fnappendoptionsprefix_(FN *fn,char *prefix PETSC_MIXED_LEN(len),PetscErrorCode *ierr PETSC_END_LEN(len))
{
  char *t;

  FIXCHAR(prefix,len,t);
  *ierr = FNAppendOptionsPrefix(*fn,t);if (*ierr) return;
  FREECHAR(prefix,t);
}

SLEPC_EXTERN void PETSC_STDCALL fngetoptionsprefix_(FN *fn,char *prefix PETSC_MIXED_LEN(len),PetscErrorCode *ierr PETSC_END_LEN(len))
{
  const char *tname;

  *ierr = FNGetOptionsPrefix(*fn,&tname); if (*ierr) return;
  *ierr = PetscStrncpy(prefix,tname,len);if (*ierr) return;
  FIXRETURNCHAR(PETSC_TRUE,prefix,len);
}

SLEPC_EXTERN void PETSC_STDCALL fnsettype_(FN *fn,char *type PETSC_MIXED_LEN(len),PetscErrorCode *ierr PETSC_END_LEN(len))
{
  char *t;

  FIXCHAR(type,len,t);
  *ierr = FNSetType(*fn,t);if (*ierr) return;
  FREECHAR(type,t);
}

SLEPC_EXTERN void PETSC_STDCALL fngettype_(FN *fn,char *name PETSC_MIXED_LEN(len),PetscErrorCode *ierr PETSC_END_LEN(len))
{
  FNType tname;

  *ierr = FNGetType(*fn,&tname);if (*ierr) return;
  *ierr = PetscStrncpy(name,tname,len);if (*ierr) return;
  FIXRETURNCHAR(PETSC_TRUE,name,len);
}


