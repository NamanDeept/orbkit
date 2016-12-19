import cython
 
# import both numpy and the Cython declarations for numpy
import numpy as np
cimport numpy as np

@cython.boundscheck(False)
@cython.wraparound(False)
def get_enum(list zero,
             list sing,
             np.ndarray[double, ndim=2, mode="c"] moom not None):

  # Initialize the variables
  cdef int sta
  cdef int iz,jz,ks
  cdef double citmp = 0.0
  cdef int nz = len(zero[0])
  cdef int ns = len(sing[0])
  cdef double en = 0.0

  for iz in range(nz):
    for jz in range(len(zero[0][iz])):
      sta = zero[1][iz][jz]
      citmp = zero[0][iz][jz]   
      en += citmp*moom[sta,sta]
  for ks in range(ns):
    sta = sing[1][ks][0]
    stb = sing[1][ks][1]
    citmp = sing[0][ks]
    en += citmp*moom[sta,stb]

  return en

@cython.boundscheck(False)
@cython.wraparound(False)
def get_mu(list zero,
           list sing,
           np.ndarray[double, ndim=3, mode="c"] omr not None,
           np.ndarray[double, ndim=3, mode="c"] omv not None):

  # Initialize the variables
  cdef int sta,stb
  cdef int iz,jz,ks,d
  cdef double citmp = 0.0
  cdef int nz = len(zero[0])
  cdef int ns = len(sing[0])
  cdef np.ndarray[double, ndim=1, mode="c"] mur = np.zeros(3,dtype=np.float64)
  cdef np.ndarray[double, ndim=1, mode="c"] muv = np.zeros(3,dtype=np.float64)

  for iz in range(nz):
    for jz in range(len(zero[0][iz])):
      sta = zero[1][iz][jz]
      citmp = zero[0][iz][jz]
      for d in range(3):
        mur[d] += citmp*omr[d,sta,sta]
  for ks in range(ns):
    sta = sing[1][ks][0]
    stb = sing[1][ks][1]
    citmp = sing[0][ks]
    for d in range(3):
      mur[d] += citmp*omr[d,sta,stb]
      muv[d] += 0.5*citmp*(omv[d,sta,stb]-omv[d,stb,sta])

  return mur,muv

@cython.boundscheck(False)
@cython.wraparound(False)
def get_rho(int i,int j, 
           list zero,
           list sing,
           np.ndarray[double, ndim=2, mode="c"] molist not None):

  # Initialize the variables
  cdef int slen = j-i
  cdef np.ndarray[double, ndim=1, mode="c"] rho = np.zeros([slen],dtype=np.float64)
  cdef int sta,stb
  cdef int iz,jz,ks,x
  cdef double citmp = 0.0
  cdef int nz = len(zero[0])
  cdef int ns = len(sing[0])

  for iz in range(nz):
    for jz in range(len(zero[0][iz])):
      sta = zero[1][iz][jz]
      citmp = zero[0][iz][jz]   
      for x in range(slen):
        rho[x] += citmp*molist[sta,(x+i)]*molist[sta,(x+i)]
  for ks in range(ns):
    sta = sing[1][ks][0]
    stb = sing[1][ks][1]
    citmp = sing[0][ks]
    for x in range(slen):
      rho[x] += citmp*molist[sta,(x+i)]*molist[stb,(x+i)]
  
  return rho 

@cython.boundscheck(False)
@cython.wraparound(False)
def get_rho_full(np.ndarray[double, ndim=2, mode="c"] ReS not None,
                 np.ndarray[double, ndim=2, mode="c"] chi_n not None):
  cdef int nbasis = ReS.shape[0]
  cdef int npts = chi_n.shape[1]
  cdef np.ndarray[double, ndim=1, mode="c"] rho = np.zeros(npts,dtype=np.float64)
  cdef int r,n,m
  cdef double tmp 
  for r in prange(npts, nogil=True): 
    tmp = 0.0
    for n in range(nbasis):
      tmp = tmp +ReS[n,n] * chi_n[n,r] * chi_n[n,r] 
      for m in range(n):
        tmp = tmp + 2. * ReS[n,m] * chi_n[n,r] * chi_n[m,r] 
    rho[r] = tmp 
  return rho

  
@cython.boundscheck(False)
@cython.wraparound(False)
def get_jab(int i,int j, 
        list zero,
        list sing,
        np.ndarray[double, ndim=2, mode="c"] molist not None,
        np.ndarray[double, ndim=3, mode="c"] molistdrv not None):
  # Initialize the variables
  cdef int slen = abs(j-i)
  cdef np.ndarray[double, ndim=2, mode="c"] jab = np.zeros(([3,slen]),dtype=np.float64)
  cdef int sta,stb
  cdef int ks,x,d
  cdef double citmp = 0.0
  cdef int nz = len(zero[0])
  cdef int ns = len(sing[0])

  for ks in range(ns):
    sta = sing[1][ks][0]
    stb = sing[1][ks][1]
    citmp = sing[0][ks]
    for d in range(3):
      for x in range(slen):
        jab[d,x] += 0.5*(citmp*(molist[sta,(x+i)]*molistdrv[d,stb,(x+i)] 
                  - molist[stb,(x+i)]*molistdrv[d,sta,(x+i)]))

  return jab

@cython.boundscheck(False)
@cython.wraparound(False)
def get_jab_full(np.ndarray[double, ndim=2, mode="c"] ImS not None,
                 np.ndarray[double, ndim=2, mode="c"] chi_n not None,
                 np.ndarray[double, ndim=3, mode="c"] nabla_chi_n not None,
                 double mu):
  cdef int nbasis = ImS.shape[0]
  cdef int npts = chi_n.shape[1]
  cdef np.ndarray[double, ndim=2, mode="c"] j = np.zeros([nabla_chi_n.shape[0],npts],dtype=np.float64)
  cdef int c,r,n,m
  cdef double f = 1./mu,tmp
  for c in range(nabla_chi_n.shape[0]):
    for r in prange(npts, nogil=True):     
      tmp = 0.0
      for n in range(nbasis):
        for m in range(n):
          tmp = tmp +f * ImS[n,m] * (chi_n[n,r] * nabla_chi_n[c,m,r] - chi_n[m,r] * nabla_chi_n[c,n,r])
      j[c,r] = tmp
  return j

@cython.boundscheck(False)
@cython.wraparound(False)
def get_a_nabla_b(int i,int j, 
        list zero,
        list sing,
        np.ndarray[double, ndim=2, mode="c"] molist not None,
        np.ndarray[double, ndim=3, mode="c"] molistdrv not None):

  # Initialize the variables
  cdef int slen = abs(j-i)
  cdef np.ndarray[double, ndim=2, mode="c"] jab = np.zeros(([3,slen]),dtype=np.float64)
  cdef int sta,stb
  cdef int ks,x,d
  cdef double citmp = 0.0
  cdef int nz = len(zero[0])
  cdef int ns = len(sing[0])

  for ks in range(ns):
    sta = sing[1][ks][0]
    stb = sing[1][ks][1]
    citmp = sing[0][ks]
    for d in range(3):
      for x in range(slen):
        jab[d,x] += citmp*(molist[sta,(x+i)]*molistdrv[d,stb,(x+i)] )

  return jab