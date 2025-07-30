import os, sys
from ROOT import TFile, TH1D, TH2D, TText, TGraph, TLatex, gPad, TLegend, TF1
from ROOT import TCanvas, gStyle, gROOT, TPad
import numpy as np
from ROOT import gStyle
from ROOT import SetOwnership

from PlotUtils import MnvH1D, MnvH2D
import numpy as np
import json
from ParameterFit import ParameterFit


DEBUG = False
def Hist2Array(hist):
    """Convert a ROOT histogram to 2D array"""
    arr = []
    for i in range(1, hist.GetNbinsX() + 1):
        row = []
        for j in range(1, hist.GetNbinsY() + 1):    
            row.append(hist.GetBinContent(i, j))
        arr.append(row)
    #print(arr)
    return arr

templates = {
    "fcn":"fcnh___2track_MultiPionCut___data___bdtgQELike___reconstructed_Q2QE_%02d",
    "parameter":"parameters_h___2track_MultiPionCut___data___bdtgQELike___reconstructed_Q2QE_%02d",
    "correlation":"correlation_h___2track_MultiPionCut___data___bdtgQELike___reconstructed_Q2QE_%02d",
    "covariance":"covariance_h___2track_MultiPionCut___data___bdtgQELike___reconstructed_Q2QE_%02d"
    }

referencehistname = "h2D___2track_MultiPionCut___data___bdtgQELike_Q2QE___reconstructed"

filename = os.path.join(os.getenv("CCQE"),"sean","NuFit_MAD_MultiPionCut_2track_multother_Q2QE_2D.root")
if not os.path.exists(filename):
    print("File does not exist: %s" % filename)
    sys.exit(1) 
file = TFile(filename, "READ")
#file.ls()
if not file.IsOpen():
    print("File could not be opened: %s" % filename)
    sys.exit(1)

referencehist = MnvH2D()
referencehist = file.Get(referencehistname)


# a lot of work to get the y bins from the reference histogram
if DEBUG: referencehist.GetYaxis().Print("ALL")
nybins = referencehist.GetNbinsY()
if nybins < 1:
    print("No Y bins found in reference histogram: %s" % referencehistname)
    sys.exit(1)
ybins = np.zeros(nybins+1, dtype=float)
for i in range(1,nybins+1):
    if DEBUG: print (i-1, referencehist.GetYaxis().GetBinLowEdge(i))
    ybins[i-1] = referencehist.GetYaxis().GetBinLowEdge(i)
ybins[0] = 0.01
ybins[nybins] = 4.0
print ("ybins",ybins)
#sys.exit(0)
parameters = {}
fcns = {}
covariances = {}
 
for thing,form in templates.items():
    for i in range(1,14):
        if thing in ["fcn", "parameter", "covariance"]:
            name = form % i
            if thing in ["fcn", "parameter"]:
                obj = MnvH1D()
            elif thing in [ "covariance"]:
                obj = MnvH2D()
            obj = file.Get(name)
            if not obj:
                print("Object %s not found in file %s" % (name, filename))
                continue
            if thing == "fcn":
                fcns[i]=obj
            elif thing == "parameter":
                if DEBUG: print ("found",name) 
                parameters[i]=obj
                
            elif thing == "covariance":              
                covariances[i]=obj

            else:   
                print("Unknown thing: %s" % thing)
        else:
            print("Unknown template: %s" % thing)   
            continue

if len(parameters)<1:
    print("No parameters found in file %s" % filename)
    sys.exit(1)

npars = parameters[1].GetNbinsX()

if npars < 1:
    print("No parameters found in first parameter histogram.")
    sys.exit(1)


parhists = {}
for i in range(npars):
    parhists[i] = MnvH1D("parhist_%02d" % i,"Parameters",nybins,ybins)
    parhists[i].SetTitle("Parameter %d" % i)
if DEBUG: parhists[1].Print("ALL")

parsdict = {}
covdict = {}

for bin in range(1,nybins+1):
    binhist = parameters[bin]
    covhist = covariances[bin]
    parsdict[bin] = []
    covdict[bin]=(Hist2Array(covhist))
    binhist.Print("")
    for par in range(0,npars):        
        parhists[par].SetBinContent(bin+1, binhist.GetBinContent(par+1))
        parsdict[bin].append(binhist.GetBinContent(par+1))
        
        if binhist.GetBinContent(par+1) < 0.1:
            parhists[par].SetBinError(bin+1, 1.0)
        else:
            parhists[par].SetBinError(bin+1, binhist.GetBinError(par+1))   

spar = json.dumps(parsdict, indent=4)
scov = json.dumps(covdict, indent=4)
data = {"parameters": parsdict, "covariances": covdict, "ybins": ybins.tolist()}
sdata = json.dumps(data, indent=4)
outputjson = "parameters.json"
with open(outputjson, "w") as f:
    f.write(sdata)
f.close
if DEBUG: print ("Parameters Dictionary:",spar)
if DEBUG: print ("Covariance Dictionary:",scov)


gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetPalette(1)
c1 = TCanvas("c1","Parameters",800,600)


if DEBUG: print ("parameters",parameters)
order = 1
chisq, status, Results, Errors, CovMatrix, CorMatrix = ParameterFit(order , fromFile=outputjson, fit_type=0 , first_bin=1, last_bin=None)

print ("Results",chisq,status,Results,Errors)
functions = {}


for par in range(npars):
    funcname = "par%02d"%par
    polname = "pol%d"%order
    functions[par] = TF1(funcname,polname,ybins[0],ybins[nybins])
    functions[par].SetLineColor(22)
    functions[par].SetLineWidth(4)
    offset = par*(order+1)
    for i in range(0,order+1):
        if DEBUG: print ("setting function",funcname,Results[offset+i])
        functions[par].SetParameter(i,Results[offset+i])

for par in range(0,npars):
    legend = TLegend(.1,.1,.6,.4)
    #parhists[par].Print("ALL")
    c1.SetLogx(1)
    parhists[par].SetMaximum(4.0)
    parhists[par].SetMinimum(-4.0)
    parhists[par].SetMarkerStyle(20)
    parhists[par].SetMarkerSize(0.8)
    parhists[par].SetLineColor(1)
    parhists[par].SetLineWidth(2)
    parhists[par].SetXTitle("Q^{2}_{QE} (GeV^{2})")
    parhists[par].SetYTitle("Parameter Value")
    parhists[par].SetTitle("Parameter %d" % par)
    parhists[par].SetStats(0)
    if DEBUG: parhists[par].Print("ALL")
    localpol = TF1()
    parhists[par].Fit("pol%d"%order,"E","",0.001,4.0)
    localpol = parhists[par].GetFunction("pol%d"%order)
    localchisq = localpol.GetChisquare()
    localdof = nybins - order - 1
    legend.AddEntry(parhists[par],"parameters",'pe')
    legend.AddEntry(localpol,"Local Fit chisq/dof = %4.1f/%d"%(localchisq,localdof),'l')
    parhists[par].Draw()
    functions[par].Draw("same")
    dof = (nybins-order -1)*npars 
    legend.AddEntry(functions[par],"Multi Fit chisq/dof = %4.1f/%d"%(chisq,dof),'l')
    legend.Draw()
    gPad.Update()
    gPad.SaveAs("parhist_%02d.png" % par)