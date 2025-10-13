# File: FitFunction.py
# Info: Python version of FitFunction class for minimization.
# Author: H. Schellman with some VSCode turning. 

import sys,os,string
import numpy as np
import array
import math
from ROOT import Math, TH2D

DEBUG = False
TEST = False

def Hist2Arrays(hist,nybins=None):
    """Convert a ROOT histogram to 2D array"""
    if nybins is None:
        nybins = hist.GetNbinsY()
    arr = np.zeros((hist.GetNbinsX(),nybins))
    err = np.zeros((hist.GetNbinsX(),nybins))
    for i in range(1, hist.GetNbinsX() + 1):
        row = []
        for j in range(1, nybins + 1):    
            arr[i-1][j-1] = hist.GetBinContent(i, j)
            err[i-1][j-1] = hist.GetBinError(i, j)
    #print(arr)
    return arr,err

def Arrays2Hist(array,error,name,title,xbins,ybins):
    """Convert a ROOT histogram to 2D array"""
    nxbins = len(xbins)-1
    nybins = len(ybins)-1
    hist = TH2D(name,title,nxbins,xbins,nybins,ybins)
    
    for i in range(1, hist.GetNbinsX() + 1):
        for j in range (1, hist.GetNbinsY() + 1 ):             
            hist.SetBinContent(i, j, array[i-1][j-1])
            hist.SetBinError(i, j, error[i-1][j-1])
    return hist

class FitFunction2D:
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
        self.hists = hists
        
        self.fxbins = np.array(xbins)
        self.fybins = np.array(ybins)
        
        self.fnxbins = len(self.fxbins) - 1
        self.fnybins = len(self.fybins) - 1
        
        self.fycent =   ( self.fybins + np.roll(self.fybins,-1) ) / 2.0
        print ("center", self.fybins,self.fycent)
        

        # Determine number of parameters per bin
        
        self.fncats = len(categories)
        self.fcategories = categories
        # Fit type default
        if fit_type is None:
            self.fType = FitFunction2D.kSlowChi2
        else:
            self.fType = fit_type

        self.fNdim = self.fncats * (self.forder + 1)
        self.fFirstBin = first_bin
        self.fLastBin = last_bin if last_bin is not None else self.fnxbins
        self.fDoFit = True

        if self.fLastBin <= self.fFirstBin:
            raise ValueError("Last bin must be greater than first bin")

        self.inputs = {}
        self.errors = {}
        for cat in self.fcategories+["data"]:
            self.inputs[cat],self.errors[cat] = Hist2Arrays(self.hists[cat],self.fnybins)
            if DEBUG: print ("H2NP",cat,self.inputs[cat])
        tot = np.zeros((self.fnxbins,self.fnybins))
        for cat in self.fcategories:
            tot += self.inputs[cat]
        #
    
    
        print ("data",self.inputs["data"])
        print ("test",tot)
        #self.InvertCovariance()

        if DEBUG:
            print("Full fit dimension is", self.fNdim)
            print("Fit type is", self.fType)

    def NDim(self):
        if not self.fDoFit:
            return 0
        else:
            return self.fNdim
        
    # def Polynomial(self,x,fitpars,subpar)   :    
    #     """Evaluate a polynomial at x with coefficients fitpars"""
    #     # copilot made several suggestions that crashed the program
    #     value = 0.0
    #     print ("pol",subpar)
    #     offset = self.parMap(subpar)
        
    #     for i in range(0,self.forder+1):
    #         value += fitpars[i+offset] * ((x) ** i) 
    #         if DEBUG: print ("pol",x, i, fitpars[i],value)         
    #     return value
    
    def Polynomials(self,fitpars,subpar)   :    
        """Evaluate a polynomial at x with coefficients fitpars"""
        # copilot made several suggestions that crashed the program
        #print ("subpar",subpar)
        values = np.zeros(self.fnybins)
        offset = self.parMap(subpar)
        
        for bin_idx in range(self.fnybins):
            y = self.fycent[bin_idx]
            value = 0.0
            for i in range(0,self.forder+1):
                value += fitpars[i+offset] * ((y) ** i) 
                if DEBUG: print ("pol",y, i, fitpars[i],value)   
            values[bin_idx] = value 
        if DEBUG: print ("pols",subpar,values)     
        return values

    def DoEval(self, fitparameters):
        """Evaluate the chi-squared (or likelihood) for the current fit parameters."""
        # copilot did improve the algorithm
        if DEBUG:
            print("Eval fitparameters", fitparameters)
        chi2 = 0.0      
        nuisance = 0.0
        self.total = np.zeros((self.fnxbins,self.fnybins))
        self.totalerr = np.zeros((self.fnxbins,self.fnybins))
        totalerr2 = np.zeros((self.fnxbins,self.fnybins))
        if DEBUG: print ("DoEval",self.fncats)
        for icat in range(self.fncats):
            cat = self.fcategories[icat]
            poly = self.Polynomials(fitparameters,icat)
            
            for xbin in range(self.fnxbins):
                for ybin in range(self.fnybins):                    
                    self.total[xbin][ybin] += self.inputs[cat][xbin][ybin]*poly[ybin]                  
                    totalerr2[xbin] += (self.errors[cat][xbin][ybin]*poly[ybin])**2
                    if poly[ybin] < 0:
                        nuisance += poly[ybin]*poly[ybin] * 1000.
        self.totalerr = np.sqrt(totalerr2)
        
        if DEBUG: print ("values", self.total[:4,:4],self.inputs["data"][:4,:4])
        if DEBUG: print ("errors",np.sqrt(totalerr2)[:4,:4])

        diff =  self.inputs["data"] - self.total
        if DEBUG: print ("diff",diff)
        #residuals = diff/np.sqrt(totalerr2+self.errors["data"]**2)
        residuals = diff/np.sqrt(self.errors["data"]**2)
        
        if DEBUG: print ("residuals",residuals)
        chi2 = np.sum(residuals*residuals) + nuisance

        print ("chi2",chi2)

        # for bin_idx in range(self.fFirstBin, self.fLastBin):
            

        #     diff = total - self.inputs[error]

        #     if self.fType == FitFunction2D.kFastChi2:
        #         # Only diagonal elements
        #         diag = np.diag(self.fcovariance[sbin])
        #         chi2 += np.sum((diff ** 2) / diag)
        #     elif self.fType == FitFunction2D.kSlowChi2:
        #         # Full covariance
        #         chi2 += diff @ self.finvCov[sbin] @ diff
        #     else:
        #         raise ValueError("Unknown fit type")

        return chi2

    def GetTotal(self):
        return self.total
    
    def GetTotalErr(self):
        return self.totalerr
    
    def GetTotalHist(self,name,title):
        return Arrays2Hist(self.total,self.totalerr,name,title,self.fxbins,self.fybins)
    
    def GetResiduals(self):
        diff = self.inputs["data"]-self.total
        #return diff/np.sqrt(self.totalerr**2 +self.errors["data"]**2)
        return diff/np.sqrt(self.errors["data"]**2)
    
    def GetResidualsHist(self,name,title):
        return Arrays2Hist(self.GetResiduals(),np.zeros((self.fnxbins,self.fnybins)),name,title,self.fxbins,self.fybins)
    
    def to_root_math_functor(self):
        # keep the callable alive for the functor:
        self._do_eval_callable = self.DoEval
        functor = Math.Functor(self._do_eval_callable, self.NDim())
        return functor
    
    
    def Clone(self):
        return FitFunction2D(self.forder,self.fparameters, self.fcovariance, self.fybins, self.fType, self.fFirstBin, self.fLastBin)
