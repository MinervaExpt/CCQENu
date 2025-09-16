# File: FitFunction.py
# Info: Python version of FitFunction class for minimization.
# Author: H. Schellman with some VSCode turning. 

import sys,os,string
import numpy as np
import array
import math
from ROOT import Math

DEBUG = False
class FitFunction:
    kFastChi2 = 1
    kSlowChi2 = 0
    kML = 2

    def __init__(self):
        self.fNDim = 0
        

    def parMap(self,subpar):  # map parameters for series of subfits
        ''' order goes pol ... pol ... pol '''
        return subpar*(self.forder+1)
    
    def SetVals(self, order, hists, categories, xbins, ybins, fit_type=None, first_bin=1, last_bin=None):
        """
        Initialize fit function parameters and configuration.

        Args:
            order (int): Order of the polynomial.
            parameters (dict): Dict of parameter arrays for each sample/bin.
            covariances (dict): Dict of covariance matrices for each sample/bin.
            ybins (array-like): Array of y-bin edges.
            fit_type (int, optional): Fit type (kFastChi2, kSlowChi2, kML). Defaults to kSlowChi2.
            first_bin (int, optional): First bin index (inclusive). Defaults to 1.
            last_bin (int, optional): Last bin index (exclusive). Defaults to None (all bins).
        """
        self.forder = order
        self.fparameters = parameters
        self.fcovariance = covariances
        self.fybins = np.array(ybins)
        self.fnbins = len(self.fybins) - 1

        # Determine number of parameters per bin
        
        self.fnpars = len(parameters["1"])

        # Fit type default
        if fit_type is None:
            self.fType = FitFunction.kSlowChi2
        else:
            self.fType = fit_type

        self.fNdim = self.fnpars * (self.forder + 1)
        self.fFirstBin = first_bin
        self.fLastBin = last_bin if last_bin is not None else self.fnbins
        self.fDoFit = True

        if self.fLastBin <= self.fFirstBin:
            raise ValueError("Last bin must be greater than first bin")

        self.InvertCovariance()

        if DEBUG:
            print("Full fit dimension is", self.fNdim)
            print("Fit type is", self.fType)

    def InvertCovariance(self):
        """ Invert the covariance matrix for the fit """
        self.finvCov = {}
        for sbin in self.fcovariance:
            cov = self.fcovariance[sbin]
            if len(cov) != self.fnpars:
                raise ValueError("Covariance matrix size does not match number of parameters")
            inv_cov = np.linalg.inv(np.array(cov))
            self.finvCov[sbin] = inv_cov

    def NDim(self):
        if not self.fDoFit:
            return 0
        else:
            return self.fNdim
        
    def Polynomial(self,x,fitpars,subpar)   :    
        """Evaluate a polynomial at x with coefficients fitpars"""
        # copilot made several suggestions that crashed the program
        value = 0.0
        offset = self.parMap(subpar)
        
        for i in range(0,self.forder+1):
            value += fitpars[i+offset] * ((x) ** i) 
            if DEBUG: print ("pol",x, i, fitpars[i],value)         
        return value

    def DoEval(self, fitparameters):
        """Evaluate the chi-squared (or likelihood) for the current fit parameters."""
        # copilot did improve the algorithm
        if DEBUG:
            print("Eval fitparameters", fitparameters)

        chi2 = 0.0      

        for bin_idx in range(self.fFirstBin, self.fLastBin):
            x = self.fybins[bin_idx - 1] + (self.fybins[bin_idx] - self.fybins[bin_idx - 1]) / 2.0
            sbin = str(bin_idx)

            # Evaluate all polynomials for this bin at once
            polvals = np.array([self.Polynomial(x, fitparameters, i) for i in range(self.fnpars)])
            if DEBUG:
                print("polvals", self.forder, self.fnpars, bin_idx, x, polvals)

            diff = polvals - np.array(self.fparameters[sbin])

            if self.fType == FitFunction.kFastChi2:
                # Only diagonal elements
                diag = np.diag(self.fcovariance[sbin])
                chi2 += np.sum((diff ** 2) / diag)
            elif self.fType == FitFunction.kSlowChi2:
                # Full covariance
                chi2 += diff @ self.finvCov[sbin] @ diff
            else:
                raise ValueError("Unknown fit type")

        return chi2

    def to_root_math_functor(self):
        # keep the callable alive for the functor:
        self._do_eval_callable = self.DoEval
        functor = Math.Functor(self._do_eval_callable, self.NDim())
        return functor
    
    
    def Clone(self):
        return FitFunction(self.forder,self.fparameters, self.fcovariance, self.fybins, self.fType, self.fFirstBin, self.fLastBin)
