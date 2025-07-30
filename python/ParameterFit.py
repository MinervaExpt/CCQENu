import sys,os,string
import numpy as np
import json
import ROOT
#from ROOT import Minuit2, Fit, Math
import array
import FitFunction

DEBUG = False
TEST = False
mini2 = ROOT.Minuit2.Minuit2Minimizer(0)
mini2.SetPrintLevel(1)
mini2.SetErrorDef(0.1)
#mini2.SetStrategy(2)
mini2.SetMaxFunctionCalls(1000)
mini2.SetMaxIterations(100)
mini2.SetTolerance(1e-4)



inputs = json.load(open("parameters.json"))
if DEBUG: print (inputs)
if "parameters" not in inputs or "covariances" not in inputs or "ybins" not in inputs:
    print("Invalid input JSON format. Expected keys: 'parameters', 'covariances', 'ybins'")
    sys.exit(1)
parameters = inputs["parameters"]
covariances = inputs["covariances"]
ybins = inputs["ybins"]
npars = len(parameters["1"])
nybins = len(ybins)
order = 1

#fitpars = np.array('d', [1.])
func2 = FitFunction.FitFunction()
func2.SetVals(order = order, parameters = parameters, covariances = covariances, ybins=ybins, fit_type=1 , first_bin=1, last_bin=None)
functor = func2.to_root_math_functor()
fitparams = array.array('d',[]) 
#print ("test",2., func2.DoEval(fitparams))
mini2.SetFunction(functor)
mini2.SetPrintLevel(4)
#mini2.SetErrorDef(1.0)
#test = func2.DoEval(fitparams)

for par in range(0, npars):
    for term in range(0, order+1):
        name = "pol%02d_par%02d" % (term,par)
        print ("name",name)
        mini2.SetVariable(par*(order+1)+term, name, 1.0, 0.1)
        fitparams.append(1.0)
mini2.Minimize()
if mini2.Status() != 0:
    print("Minimization failed with status:", mini2.Status())
    sys.exit(1)
status = mini2.Status()
Results = mini2.X()
mini2.PrintResults()
mini2.PrintResults()
combScaleResults = mini2.X()
#CovMatrix[i][j] = mini2.CovMatrix(i, j)
#fcn.SetBinContent(1, mini2.MinValue())
#covariance.SetBinContent(i + 1, j + 1, mini2.CovMatrix(i, j))
#fcnhist.SetBinContent(1, mini2.MinValue())
#chist.SetBinContent(i + 1, j + 1, mini2.CovMatrix(i, j))
