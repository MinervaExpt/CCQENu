import ROOT

from PlotUtils import MnvH1D
from ROOT import gROOT,gStyle, TFile,THStack,TH1D,TCanvas, TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex, TString

colors = {
0:ROOT.kBlack,
1:ROOT.kBlue-6,
2:ROOT.kMagenta-6,
3:ROOT.kRed-6,
4:ROOT.kYellow-6,
5:ROOT.kGreen-6,
6:ROOT.kTeal-6,
7:ROOT.kWhite,
8:ROOT.kGreen-6,
9:ROOT.kTeal-6,
10:ROOT.kBlue-1,
11:ROOT.kBlue-10,
12:ROOT.kMagenta-10,
13:ROOT.kRed-10,
14:ROOT.kYellow-10,
15:ROOT.kGray,
16:ROOT.kBlack,
17:ROOT.kBlack,
18:ROOT.kGreen-6,
19:ROOT.kTeal-6}


import os,sys
gStyle.SetOptStat(000000)

# readin in put
filename = "SB_NuConfig_mult1pBDTG_me1N_1.root"
r = TFile.Open(filename,"READONLY")
r.ls()
keys = r.GetListOfKeys()

# make some definitions

signal = "qelike"
variable = "bdtgQELike"
datatype="reconstructed"
hist = {}
eff = {}
total = 0.0
all = MnvH1D()
stack = THStack("total","")
icolor = 0
eff = {}
colorme = {}
# read things in and make histograms 
for k in keys:
    
    name = k.GetName()
    if variable not in name: continue
    if "h2D" in name: continue
    if datatype not in name: continue
    if "data" in name: continue
    icolor +=1
    
    classify = name.split("___")
    thetype = classify[2]
    colorme[thetype]=colors[icolor]
    hist[thetype]=MnvH1D()
    hist[thetype]=r.Get(name)

    # eff will be the fraction of events below some cut

    eff[thetype]=TH1D()
    eff[thetype] = hist[thetype].Clone(thetype+"_eff")
    eff[thetype] = eff[thetype].GetCumulative()
    eff[thetype].Scale(1./hist[thetype].Integral())
    hist[thetype].SetFillColor(colors[icolor])
    stack.Add(hist[thetype])
    total += hist[thetype].Integral()


# plot the stack
c2 = TCanvas()
stack.Draw("hist")
c2.Draw()
c2.Print("stack.jpg")


# build up a total and a background estimate
all = MnvH1D()
all = hist[signal].Clone("all")
all.Reset()

bak = MnvH1D()
bak = hist[signal].Clone("background")
bak.Reset()

for h in hist:
   all.Add(hist[h])
   if h != signal: bak.Add(hist[h])
cbak = MnvH1D()
cbak = bak.GetCumulative()
cbak.Scale(1./bak.Integral())

# plot the efficiency for
c3 = TCanvas()
leg = TLegend(0.6,0.15,0.9,0.30)
leg.SetFillStyle(0)
leg.SetBorderSize(0)
leg.SetTextSize(0.03)
eff[signal].Print("ALL")
eff[signal].SetTitle("Fraction of events below BDT selection")
eff[signal].GetYaxis().SetTitle("fraction below BDT response")
eff[signal].Draw("hist")
for h in eff:
    color = colorme[h]
    eff[h].SetLineColor(color)  
    eff[h].SetMarkerColor(color)
    eff[h].SetMarkerStyle(20)
    eff[h].SetLineWidth(3)
    if h == signal: 
        eff[h].SetLineWidth(5)
    #eff[h].SetFillColor(0)
    #eff[h].SetLineWidth(2)
    eff[h].Draw("hist same")
    leg.AddEntry(eff[h],h,'lf')
cbak.SetLineColor(1)
cbak.SetLineWidth(4)
cbak.SetFillColor(0)

leg.AddEntry(bak,"all background",'l')
cbak.Draw("hist same")
leg.Draw()
c3.Draw()
c3.Print("fractions.jpg")







    

