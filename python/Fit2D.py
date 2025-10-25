''' take parameters from BDT fits to Q2 bins from Sean Gilligan
This program plots and does local fits using the ROOT TH1 fitting.
It stores the parameters in a json file by bin index (which gets changed into a string by json writing).
It calls ParameterFit which sets up the fit with the goodness being calculated by FitFunction

Fun facts - root passes the parameters to the fit function as a pointer to double in memory - you can access elements via [] but not via most other methods fail miserably. 

Author: Heidi Schellman - based loosely on the MINERvA fitting code. 
Date: 2025-07-29

'''

import os, sys
from ROOT import TFile, TH1D, TH2D, TText, TGraph, TLatex, gPad, TLegend, TF1
from ROOT import TCanvas, gStyle, gROOT, TPad, Minuit2
import numpy as np
from ROOT import gStyle
from ROOT import SetOwnership

from PlotUtils import MnvH1D, MnvH2D
import numpy as np
import commentjson as json
import math
#from ParameterFit import ParameterFit
import FitFunction2D
kFastChi2 = 1
kSlowChi2 = 0

DEBUG = False
# def Hist2Array(hist):
#     """Convert a ROOT histogram to 2D array"""
#     arr = []
#     for i in range(1, hist.GetNbinsX() + 1):
#         row = []
#         for j in range(1, hist.GetNbinsY() + 1):    
#             row.append(hist.GetBinContent(i, j))
#         arr.append(row)
#     #print(arr)
#     return arr

rebinx = 1
rebiny = 1

np.set_printoptions(precision=4, threshold=200, linewidth=100, floatmode="maxprec")
referencehistname = "h2D___2track_MultiPionCut___data___bdtgQELike_Q2QE___reconstructed"

#filename = os.path.join(os.getenv("CCQE"),"sean","NuFit_MAD_MultiPionCut_2track_multother_Q2QE_2D.root")
filename = os.path.join(os.getenv("CCQE"),"sean","SB_NuConfig_bdtg_MAD_MultiPionCut_2track_me1N_1_test_multother.root")
if not os.path.exists(filename):
    print("File does not exist: %s" % filename)
    sys.exit(1) 
file = TFile(filename, "READ")
if DEBUG: file.ls()
if not file.IsOpen():
    print("File could not be opened: %s" % filename)
    sys.exit(1)

referencehist = MnvH2D()
referencehist = file.Get(referencehistname)
referencehist.Rebin2D(rebinx,rebiny)

configname  = "NuFit_MAD_2track_MultiPionCut_multother.json"
config = json.load(open(configname,'r'))
sidebands = config["Sidebands"]
includeinfit = config["IncludeInFit"]
categories = config["Categories"]
background = config["Backgrounds"]


# a lot of work to get the y bins from the reference histogram
if DEBUG: referencehist.GetYaxis().Print("ALL")
nxbins = referencehist.GetNbinsX()
nybins = referencehist.GetNbinsY()

if nybins < 1:
    print("No Y bins found in reference histogram: %s" % referencehistname)
    sys.exit(1)
xbins = np.zeros(nxbins+1, dtype=float)
ybins = np.zeros(nybins+1, dtype=float)

for i in range(1,nxbins+2):
    if DEBUG: print (i-1, referencehist.GetXaxis().GetBinLowEdge(i))
    xbins[i-1] = referencehist.GetXaxis().GetBinLowEdge(i)

for i in range(1,nybins+2):
    if DEBUG: print (i-1, referencehist.GetYaxis().GetBinLowEdge(i))
    ybins[i-1] = referencehist.GetYaxis().GetBinLowEdge(i)
ybins[0] = 0.01
#ybins[nybins] = 4.0
print ("xbins",xbins)
print ("ybins",ybins)


hists = {}

datanorm = referencehist.Integral()
mcnorm = 0.0

hists["data"] = referencehist
for cat in categories:
    histname = referencehistname.replace("data",cat)
    print ("hist",histname)
    hist = MnvH2D()
    
    hist = file.Get(histname)
    hist.Rebin2D(rebinx,rebiny)
    if hist:
        hists[cat] = hist
        hists[cat].Print()
    else:
        print (histname, " not in file")
    
    mcnorm += hist.Integral()

for cat in categories:
     hists[cat].Scale(datanorm/mcnorm)

#print (hists)
out = TFile.Open("Output.root","RECREATE")
for hist in hists:
    hists[hist].Write()
#sys.exit(0)
order = 1
npars = len(categories)
fitparameters = np.zeros ((order+1)*npars)
nfitparameters = (order+1)*npars
mini2 = Minuit2.Minuit2Minimizer(0)
func2 = FitFunction2D.FitFunction2D()
func2.SetVals(order , hists, categories, xbins=xbins, ybins=ybins, fit_type=kSlowChi2 , first_bin=1, last_bin=None)
functor = func2.to_root_math_functor()
mini2.SetPrintLevel(2)
mini2.SetTolerance(1e-4)
mini2.SetFunction(functor)
mini2.SetPrintLevel(1)

for par in range(len(categories)):
    for term in range(order+1):
        name = "pol%02d_par%s" % (term,categories[par])
        if term != 0:
             val = 0.0
        else:
             val = 1.0
        mini2.SetVariable(par*(order+1)+term, name, val, 0.1)
        fitparameters[par*(order+1)+term] = val

ndof = nxbins*nybins - func2.NDim()

print ("test",func2.DoEval(fitparameters))
prefit = func2.GetTotalHist("BeforeFit","before the fit")
prefit.Print()
mini2.Minimize()
if mini2.Status() != 0:
    print("Minimization failed with status:", mini2.Status())
status = mini2.Status()
X = mini2.X()
errors = mini2.Errors()
mini2.PrintResults()
chisq = mini2.MinValue()
status = mini2.Status()
#            CovMatrix[i][j] = mini2.CovMatrix(i,j) 
Results = np.zeros(nfitparameters)
Errors = np.zeros(nfitparameters)
CovMatrix = np.zeros((nfitparameters,nfitparameters))
CorMatrix = np.zeros((nfitparameters,nfitparameters))

for i in range(nfitparameters):
    Results[i] = (X[i])
    Errors[i] = (errors[i])
    for j in range(nfitparameters):
            CovMatrix[i][j] = mini2.CovMatrix(i,j)
for i in range(nfitparameters):
        for j in range(nfitparameters):
                CorMatrix[i][j] = CovMatrix[i][j]/math.sqrt(CovMatrix[i][i]*CovMatrix[j][j])
print ("Covariance\n",CovMatrix)
print ("Correlation\n",CorMatrix)
print ("results",chisq, ndof, status, Results,Errors)

total = TH2D()
total = func2.GetTotalHist("AfterFit","result of fit")
hists["data"].Print()
total.Print("")
residuals = func2.GetResiduals()

stattest = TH1D("stattest","Residuals from fit",30,-3.,3.)
for x in range(nxbins):
    for y in range(nybins):
         
         stattest.Fill(residuals[x][y])
print ("residuals\n",residuals)
print ("residuals2\n",residuals*residuals)
print ("chi2test",np.sum(residuals*residuals))
residualhist = func2.GetResidualsHist("residuals","residuals")
stattest.Write()
#hists["data"].Write()
total.Write()
residualhist.Write()
out.Close()