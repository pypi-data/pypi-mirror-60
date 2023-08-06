/*
   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   SLEPc - Scalable Library for Eigenvalue Problem Computations
   Copyright (c) 2002-2019, Universitat Politecnica de Valencia, Spain

   This file is part of SLEPc.
   SLEPc is distributed under a 2-clause BSD license (see LICENSE).
   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
*/

#include <petsc/private/fortranimpl.h>
#include <slepcbv.h>

#if defined(PETSC_HAVE_FORTRAN_CAPS)
#define bvsettype_                BVSETTYPE
#define bvgettype_                BVGETTYPE
#define bvsetoptionsprefix_       BVSETOPTIONSPREFIX
#define bvappendoptionsprefix_    BVAPPENDOPTIONSPREFIX
#define bvgetoptionsprefix_       BVGETOPTIONSPREFIX
#define bvview_                   BVVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE)
#define bvsettype_                bvsettype
#define bvgettype_                bvgettype
#define bvsetoptionsprefix_       bvsetoptionsprefix
#define bvappendoptionsprefix_    bvappendoptionsprefix
#define bvgetoptionsprefix_       bvgetoptionsprefix
#define bvview_                   bvview
#endif

SLEPC_EXTERN void PETSC_STDCALL bvsettype_(BV *bv,char *type PETSC_MIXED_LEN(len),PetscErrorCode *ierr PETSC_END_LEN(len))
{
  char *t;

  FIXCHAR(type,len,t);
  *ierr = BVSetType(*bv,t);if (*ierr) return;
  FREECHAR(type,t);
}

SLEPC_EXTERN void PETSC_STDCALL bvgettype_(BV *bv,char *name PETSC_MIXED_LEN(len),PetscErrorCode *ierr PETSC_END_LEN(len))
{
  BVType tname;

  *ierr = BVGetType(*bv,&tname); if (*ierr) return;
  *ierr = PetscStrncpy(name,tname,len);if (*ierr) return;
  FIXRETURNCHAR(PETSC_TRUE,name,len);
}

SLEPC_EXTERN void PETSC_STDCALL bvsetoptionsprefix_(BV *bv,char *prefix PETSC_MIXED_LEN(len),PetscErrorCode *ierr PETSC_END_LEN(len))
{
  char *t;

  FIXCHAR(prefix,len,t);
  *ierr = BVSetOptionsPrefix(*bv,t);if (*ierr) return;
  FREECHAR(prefix,t);
}

SLEPC_EXTERN void PETSC_STDCALL bvappendoptionsprefix_(BV *bv,char *prefix PETSC_MIXED_LEN(len),PetscErrorCode *ierr PETSC_END_LEN(len))
{
  char *t;

  FIXCHAR(prefix,len,t);
  *ierr = BVAppendOptionsPrefix(*bv,t);if (*ierr) return;
  FREECHAR(prefix,t);
}

SLEPC_EXTERN void PETSC_STDCALL bvgetoptionsprefix_(BV *bv,char *prefix PETSC_MIXED_LEN(len),PetscErrorCode *ierr PETSC_END_LEN(len))
{
  const char *tname;

  *ierr = BVGetOptionsPrefix(*bv,&tname); if (*ierr) return;
  *ierr = PetscStrncpy(prefix,tname,len);if (*ierr) return;
  FIXRETURNCHAR(PETSC_TRUE,prefix,len);
}

SLEPC_EXTERN void PETSC_STDCALL bvview_(BV *bv,PetscViewer *viewer,PetscErrorCode *ierr)
{
  PetscViewer v;
  PetscPatchDefaultViewers_Fortran(viewer,v);
  *ierr = BVView(*bv,v);
}

