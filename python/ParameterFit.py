import sys,os,string
import numpy as np
import json
import math
import ROOT
#from ROOT import Minuit2, Fit, Math
import array
import FitFunction

DEBUG = True
TEST = False
kFastChi2 = 1
kSlowChi2 = 0

def ParameterFit(order = 1, inparameters = None, incovariances = None, inybins=None, fit_type=kSlowChi2 , first_bin=1, last_bin=None):
        mini2 = ROOT.Minuit2.Minuit2Minimizer(0)
        mini2.SetPrintLevel(1)
        mini2.SetErrorDef(0.1)
        #mini2.SetStrategy(2)
        mini2.SetMaxFunctionCalls(1000)
        mini2.SetMaxIterations(100)
        mini2.SetTolerance(1e-4)
        parameters = inparameters
        covariances = incovariances
        ybins = inybins
        if inparameters is None:
                print ("read in from file")
                inputs = json.load(open("parameters.json"))
                if DEBUG: print (inputs)

                if "parameters" not in inputs or "covariances" not in inputs or "ybins" not in inputs:
                        print("Invalid input JSON format. Expected keys: 'parameters', 'covariances', 'ybins'")
                        sys.exit(1)
                parameters = inputs["parameters"]
                covariances = inputs["covariances"]
                ybins = inputs["ybins"]
        
        print ("parameters",parameters)                
        npars = len(parameters["1"])
        nybins = len(ybins)
        order = 1

        #fitpars = np.array('d', [1.])
        func2 = FitFunction.FitFunction()
        func2.SetVals(order = order, parameters = parameters, covariances = covariances, ybins=ybins, fit_type=kSlowChi2 , first_bin=1, last_bin=None)
        functor = func2.to_root_math_functor()
        fitparams = array.array('d',[]) 
        #print ("test",2., func2.DoEval(fitparams))
        mini2.SetFunction(functor)
        mini2.SetPrintLevel(1)

        for par in range(0, npars):
                for term in range(0, order+1):
                        name = "pol%02d_par%02d" % (term,par)
                        print ("name",name)
                        mini2.SetVariable(par*(order+1)+term, name, 1.0, 0.1)
                        fitparams.append(1.0)
        nfitpars = len(fitparams)
        test = func2.DoEval(fitparams)
        print ("test", test)
        mini2.Minimize()

        if mini2.Status() != 0:
                print("Minimization failed with status:", mini2.Status())
                sys.exit(1)
        status = mini2.Status()
        X = mini2.X()
        errors = mini2.Errors()

        mini2.PrintResults()
        chisq = mini2.MinValue()
        Results = np.zeros(nfitpars)
        Errors = np.zeros(nfitpars)
        CovMatrix = np.zeros((nfitpars,nfitpars))
        CorMatrix = np.zeros((nfitpars,nfitpars))

        for i in range(nfitpars):
                Results[i] = (X[i])
                Errors[i] = (errors[i])
                for j in range(nfitpars):
                        CovMatrix[i][j] = mini2.CovMatrix(i,j)
        for i in range(nfitpars):
                for j in range(nfitpars):
                        CorMatrix[i][j] = CovMatrix[i][j]/math.sqrt(CovMatrix[i][i]*CovMatrix[j][j])
        print ("Covariance",CovMatrix)
        print ("Correlation",CorMatrix)
        return chisq,Results,Errors,CovMatrix,CorMatrix
        
if __name__ == '__main__':
        chisq, Results, Errors, CovMatrix, CorMatrix = ParameterFit(order = 1, inparameters = None, incovariances = None, inybins=None, fit_type=kSlowChi2 , first_bin=1, last_bin=None)
        print ("Results",Results,Errors)