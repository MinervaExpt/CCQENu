# File: FitFunction.py
# Info: Python version of FitFunction class for minimization.
# Author: Translated from C++ by GitHub Copilot

import sys,os,string
import numpy as np
#import json
import array
import ROOT
import math

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


    
    def SetVals(self, order, parameters, covariances, ybins, fit_type=kSlowChi2, first_bin=1, last_bin=None):
        """
        parameters: dict of unfit histograms for each sample
        covariances: dict of covariance matrices for each sample
        ybins: array of y-bin edges
        fit_type: type of fit (kFastChi2, kSlowChi2, kML)
        first_bin: first bin to consider in the fit
        last_bin: last bin to consider in the fit (default is None, meaning all bins
        """
        self.forder = order # order of polynomials
        # ("parameters",parameters)
        self.fnpars = len(parameters["1"]) # number of parameters to fit
        self.fparameters = parameters
        #print (self.fparameters["1"])
        self.fcovariance = covariances 
        self.InvertCovariance() # invert the covariance matrices
        self.fybins = np.array(ybins)
        self.fnbins = len(ybins) - 1
        self.fType = fit_type
        self.fNdim = self.fnpars*(self.forder + 1)
        self.fFirstBin = first_bin
        self.fLastBin = last_bin
        if last_bin is None:
            self.fLastBin = self.fnbins 
        self.fDoFit = True
        if self.fLastBin <= self.fFirstBin:
            raise ValueError("Last bin must be greater than first bin")
        print ("full fit dimension is", self.fNdim)
        print ("Fit type is", self.fType)

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
        value = 0.0
        offset = self.parMap(subpar)
        for i in range(0,self.forder+1):
            value += fitpars[i+offset] * ((x) ** i) 
            if DEBUG: print ("pol",x, i, fitpars[i],value)         
        return value

    def DoEval(self, fitparameters):
        """ parameters are """
        if DEBUG: print ("Eval fitparameters", fitparameters  )
        
        chi2 = 0.0
        
        for bin in range(self.fFirstBin, self.fLastBin):
            x = self.fybins[bin-1] + (self.fybins[bin] - self.fybins[bin-1]) / 2.0
            sbin = "%d" % bin
            
            # determine polynomials first to save time
            polvals = np.zeros(self.fnpars)
            for i in range(self.fnpars):
                polvals[i] = self.Polynomial(x,fitparameters,i)
            if DEBUG: print ("polvals", self.forder, self.fnpars, bin, x, polvals)
            for i in range(self.fnpars):            
                if self.fType == FitFunction.kFastChi2:
                    # Fast Chi2 calculation - only uses diagonal errors
                    chi2 += (polvals[i] - self.fparameters[sbin][i]) ** 2 / self.fcovariance[sbin][i][i]
                elif self.fType == FitFunction.kSlowChi2:
                    for j in range(self.fnpars):
                        chi2 += (polvals[i]- self.fparameters[sbin][i]) * (polvals[j] - self.fparameters[sbin][j]) * self.finvCov[sbin][i][j]
                else:
                    raise ValueError("Unknown fit type")
        return chi2

    def to_root_math_functor(self):
        # keep the callable alive for the functor:
        self._do_eval_callable = self.DoEval
        functor = ROOT.Math.Functor(self._do_eval_callable, self.NDim())
        return functor
    
    
    def Clone(self):
        return FitFunction(self.forder,self.fparameters, self.fcovariance, self.fybins, self.fType, self.fFirstBin, self.fLastBin)
