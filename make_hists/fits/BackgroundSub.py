import os,sys,string
from ROOT import *
from PlotUtils import *
import json



configfilename = sys.argv[1]
configfile = open(configfilename,'r')
config = json.load(configfile)

inputfilename = config["OutputFile"]
outputfilename = "bkg_"+config["OutputFile"]

inputfile = TFile.Open(inputfilename,"READONLY")
outputfile = TFile.Open(outputfilename,"RECREATE")

sidebands = config["Sidebands"]
categories = config["Categories"]
backgrounds = config["Backgrounds"]
variable = config["Variable"]

template =  config["Template"]
fitTemplate = config["FitTemplate"]
logPlot = config["LogPlot"];

signal = []
for s in sidebands:
    if s not in backgrounds:
        signal.append(s)
data = {}
bkgsub = {}
mc = {}
 
mnvPlotter = MnvPlotter(PlotUtils.kCCQEAntiNuStyle);
cF = TCanvas("fit","fit")
if (logPlot):
    gPad.SetLogy(1);

for s in sidebands:
    mc[s] = {}
    newdataname = template%(s,"data",variable)
    data[s] = MnvH1D()
    data[s] = inputfile.Get(newdataname).Clone()
    data[s].Print()
    bkgsub[s] = MnvH1D()
    bkgsub[s] = data[s].Clone(data[s].GetName().replace("data","bkgsub"))
    mc[s]["tot"] = MnvH1D()
    mc[s]["bkg"] = MnvH1D()
    mc[s]["sig"] = MnvH1D()
    count = 0
    for c in categories:
        newmcname = fitTemplate%(s,c,variable)
        
        mc[s][c] = MnvH1D()
        mc[s][c] = inputfile.Get(newmcname).Clone()
        if count == 0:
            mc[s]["tot"]=mc[s][c].Clone(newmcname.replace(c,"tot"))
            mc[s]["sig"]=mc[s][c].Clone(newmcname.replace(c,"sig"))
            mc[s]["bkg"]=mc[s][c].Clone(newmcname.replace(c,"bkg"))
            mc[s]["tot"].Reset()
            mc[s]["sig"].Reset()
            mc[s]["bkg"].Reset()
            count +=1
        mc[s]["tot"].Add(mc[s][c])
        print (c,backgrounds)
        if c in backgrounds:
            mc[s]["bkg"].Add(mc[s][c])
        else:
            mc[s]["sig"].Add(mc[s][c])
    bkgsub[s].AddMissingErrorBandsAndFillWithCV(mc[s]["tot"])
    mc[s]["bkg"].Print("ALL")
    bkgsub[s].Add(mc[s]["bkg"],-1.)
    mc[s]["tot"].Print()
    mc[s]["tot"].MnvH1DToCSV("tot","./bkg/")
    mnvPlotter.DrawDataMCWithErrorBand(data[s], mc[s]["tot"], 1., "R")
    t = TText(.3,.95,"%s %s %s"%(variable,s,"fitted tot"))
    t.SetNDC(1);
    t.SetTextSize(0.03)
    t.Draw("same")
    cF.Print(mc[s]["tot"].GetName()+".png");
    mnvPlotter.DrawDataMCWithErrorBand(bkgsub[s], mc[s]["sig"], 1., "R")
    t.SetTitle("%s %s %s"%(variable,s,"fitted bkgsub"))
    t.Draw("same")
    cF.Print(mc[s]["sig"].GetName()+".png");
    
print ("end of scope for plotter clones")
outputfile.cd()
extras = ["tot","sig","bkg"]
for s in sidebands:
    data[s].Write()
    bkgsub[s].Write()
    for c in categories + extras:
        mc[s][c].Write()
print ("done writing clones")
for s in sidebands :
    data[s].Delete()
    bkgsub[s].Delete()
    for c in categories + extras:
        mc[s][c].Delete()
        
