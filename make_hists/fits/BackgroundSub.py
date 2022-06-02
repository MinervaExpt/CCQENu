import os,sys,string
from ROOT import *
from PlotUtils import *
import json

def map2TObjArray(thing,cat):
    r = TObjArray()
    for it in cat:
        thing[it].Print()
        r.Add(thing[it])
    return r

binWidth = False

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
mnvPlotter.draw_normalized_to_bin_width = binWidth
cF = TCanvas("fit","fit")
if (logPlot):
    gPad.SetLogy(1);

stack = {}
for s in sidebands:
    mc[s] = {}
    newdataname = template%(s,"data",variable)
    data[s] = MnvH1D()
    data[s] = inputfile.Get(newdataname).Clone()
    data[s].Print()
    
   
    mc[s]["tot"] = MnvH1D()
    mc[s]["bkg"] = MnvH1D()
    mc[s]["sig"] = MnvH1D()
    count = 0
    
    c = categories[0]
    newmcname = fitTemplate%(s,c,variable)
    temp = MnvH1D()
    temp = inputfile.Get(newmcname).Clone()
    mc[s]["tot"]=temp.Clone(newmcname.replace(c,"tot"))
    mc[s]["sig"]=temp.Clone(newmcname.replace(c,"sig"))
    mc[s]["bkg"]=temp.Clone(newmcname.replace(c,"bkg"))
    mc[s]["tot"].Reset()
    mc[s]["sig"].Reset()
    mc[s]["bkg"].Reset()
    stack[s] = TObjArray()
    for c in categories:
        newmcname = fitTemplate%(s,c,variable)
        mc[s][c] = MnvH1D()
        mc[s][c] = inputfile.Get(newmcname).Clone()
        mc[s][c].SetTitle(c)
        
        
        mc[s]["tot"].Add(mc[s][c])
        print (c,backgrounds)
        if c in backgrounds:
            mc[s]["bkg"].Add(mc[s][c])
        else:
            mc[s]["sig"].Add(mc[s][c])
        mc[s][c].Scale(1.,"width")
        
    
    bkgsub[s] = MnvH1D()
    bkgsub[s] = data[s].Clone(data[s].GetName().replace("data","bkgsub"))
    bkgsub[s].AddMissingErrorBandsAndFillWithCV(mc[s]["bkg"])
    bkgsub[s].Add(mc[s]["bkg"],-1.)

outputfile.cd()
extras = ["tot","sig","bkg"]
for s in sidebands:
    data[s].Write()
    bkgsub[s].Write()
    for c in categories + extras:
        mc[s][c].Write()
print ("done writing clones")

#outputfile.Close()

for s in sidebands:
    t = TText(.35,.95,"")
    t.SetNDC(1)
    t.SetTextSize(0.03)
    data[s].Scale(1., "width")
    bkgsub[s].Scale(1.,"width")
    for c in extras:
        mc[s][c].Scale(1.,"width")
    
    mnvPlotter.DrawDataMCWithErrorBand(data[s], mc[s]["tot"], 1., "TR")
    t.SetTitle("%s %s %s"%(variable,s,"total data + MC"))
    t.Draw("same")
    cF.Print(mc[s]["tot"].GetName()+".png");
    mnvPlotter.DrawDataMCWithErrorBand(bkgsub[s], mc[s]["sig"], 1., "TR")
    t.SetTitle("%s %s %s"%(variable,s,"fitted bkgsub"))
    t.Draw("same")
    cF.Print(mc[s]["sig"].GetName()+".png");
    
print ("end of scope for plotter clones")

for s in sidebands :
    data[s].Delete()
    bkgsub[s].Delete()
    for c in categories + extras:
        mc[s][c].Delete()
        
