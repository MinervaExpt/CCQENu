import ROOT
from ROOT import gROOT,gStyle, TFile,THStack,TH1D,TCanvas, TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex, TString

import sys,os,string

def CCQECanvas(name,title,xsize=750,ysize=750):
  c2 = ROOT.TCanvas(name,title,xsize,ysize)
  c2.SetLeftMargin(0.20);
  c2.SetRightMargin(0.05);
  c2.SetBottomMargin(0.15);
  return c2

def CCQELegend(xlow,ylow,xhigh,yhigh):
  leg = ROOT.TLegend(xlow,ylow,xhigh,yhigh)
  leg.SetFillStyle(0)
  leg.SetBorderSize(0)
  leg.SetTextSize(0.03)
  return leg
  
process=["data","QE","RES","DIS","Other","","","","2p2h","","background"]
colors = {
0:ROOT.kBlack,
1:ROOT.kBlue-6,
2:ROOT.kMagenta-6,
3:ROOT.kRed-6,
4:ROOT.kYellow-6,
5:ROOT.kWhite,
6:ROOT.kWhite,
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

filename = sys.argv[1]

f = TFile.Open(filename,"READONLY")

keys = f.GetListOfKeys()

stacks = {}
legs = {}

for k in keys:
    name = k.GetName()
    parse = name.split("___")
    if len(parse) < 5: continue
    if not "type" in parse[4]: continue
    if parse[0] not in stacks.keys():
        stacks[parse[0]] = {}
        legs[parse[0]] = {}
    if parse[1] not in stacks[parse[0]].keys():
        stacks[parse[0]][parse[1]] = {}
        legs[parse[0]][parse[1]] = {}
    if parse[2] not in stacks[parse[0]][parse[1]].keys():
        stacks[parse[0]][parse[1]][parse[2]] = {}
        legs[parse[0]][parse[1]][parse[2]] = {}
    if parse[3] not in stacks[parse[0]][parse[1]][parse[2]].keys():
        index = int(parse[4].replace("types_",""))
        if index != 0: continue
        s = THStack(name.replace("types","stack"),"")
            
        stacks[parse[0]][parse[1]][parse[2]][parse[3]] = s

         
        legs[parse[0]][parse[1]][parse[2]][parse[3]] = TLegend(0.5,0.7,0.9,0.9)
         

for k in keys:
    name = k.GetName()
    parse = name.split("___")
    if len(parse) < 5: continue
    if not "type" in parse[4]: continue
    index = int(parse[4].replace("types_",""))
    h = f.Get(name)
    print("title",h.GetTitle())
    h.Scale(1.,"width")
    stacks[parse[0]][parse[1]][parse[2]][parse[3]].SetTitle(h.GetTitle())
    print ("xaxis",h.GetXaxis().GetTitle())
    xaxis = h.GetXaxis().GetTitle()
    
    if h.GetEntries() <= 0: continue
    
    print (index)
    
    
    h.SetFillColor(colors[index])
    
    stacks[parse[0]][parse[1]][parse[2]][parse[3]].Add(h)
    legs[parse[0]][parse[1]][parse[2]][parse[3]].AddEntry(h,process[index],"f")
    h.Print()
    #stacks[parse[0]][parse[1]][parse[2]][parse[3]].Print()
    
template = "%s___%s___%s___%s"
for a in stacks.keys():
    for b in stacks[a].keys():
        for c in stacks[a][b].keys():
           for d in stacks[a][b][c].keys():
                stacks[a][b][c][d].Print()
                cc = CCQECanvas(template%(a,b,c,d),template%(a,b,c,d))
                stacks[a][b][c][d].Draw("hist")
                legs[a][b][c][d].Draw()
                cc.Draw()
                cc.Print(template%(a,b,c,d)+".png")
            
    

