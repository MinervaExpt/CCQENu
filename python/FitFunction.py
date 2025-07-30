# File: FitFunction.py
# Info: Python version of FitFunction class for minimization.
# Author: Translated from C++ by GitHub Copilot

import sys,os,string
import numpy as np
#import json
import array
import ROOT


class FitFunction:
    kFastChi2 = 1
    kSlowChi2 = 0
    kML = 2

    def __init__(self):
        self.fNDim = 0
    
    def SetVals(self, order, parameters, covariances, ybins, fit_type, first_bin=1, last_bin=None):
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
        print (self.fparameters["1"])
        self.fcovariance = covariances 
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


    def NDim(self):
        if not self.fDoFit:
            return 0
        else:
            return self.fNdim
        
    def Polynomial(self,x,fitpars,offset,order=None)   :    
        """Evaluate a polynomial at x with coefficients fitpars"""
        
        value = sum(fitpars[i] * (x ** i) for i in range(offset, offset + order + 1))
        #print (value)
        return value

    def DoEval(self, fitparameters):
        """ parameters are """
        print ("Eval fitparameters", fitparameters  )
        
        chi2 = 0.0
        
        for bin in range(self.fFirstBin, self.fLastBin):
            x = self.fybins[bin]
            #print ("bin,x",bin,x)
            sbin = "%d" % bin
            
            for i in range(self.fnpars):
                paroffset = i*self.forder
                #print ("paroffset", i, paroffset,paroffset+self.forder+1)
                #slice = fitparameters[paroffset:paroffset+self.forder+1]
                #print ("slice", slice)
                #if len(slice) != self.forder + 1:
                 #   raise ValueError("Slice length does not match order + 1")
                polval  = self.Polynomial(x,fitparameters,paroffset,self.forder)
                print ("polval",x,polval)
                if self.fType == FitFunction.kFastChi2:
                    # Fast Chi2 calculation - only uses diagonal - have to invert the covariance to use it propery
                    chi2 += (polval - self.fparameters[sbin][i]) ** 2 / self.fcovariance[sbin][i][i]
                # elif self.fType == FitFunction.kSlowChi2:
                #     # Slow Chi2 calculation
                #     chi2 += (self.Polynomial(bin, parameters[i]) - self.fparameters[i][bin]) ** 2 / self.fcovariance[i][bin]
                # elif self.fType == FitFunction.kML:
                #     # Maximum Likelihood calculation
                #     chi2 += poisson.logpmf(self.fparameters[i][bins], self.Polynomial(bins, parameters[i]))
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
