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
  
process=["data","QE","RES","DIS","Other","","","","2p2h",""]
l = len(process)
for x in range(0,l+1):
    process.append(process[x]+"-not")
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

groups = {}
#groups = {}
#legs = {}

# find all the valid histogram and group by keywords
for k in keys:
    name = k.GetName()
    if "___" not in name:
        continue
    parse = name.split("___")
    if len(parse) < 5: continue
    if not "type" in parse[4]: continue
    d = parse[0]
    s = parse[1]
    c = parse[2]
    v = parse[3]
    # reorder so category is last
    if d not in groups.keys():
        groups[d] = {}
        #legs[parse[0]] = {}
    if s not in groups[d].keys():
        groups[parse[0]][parse[1]] = {}
        
    if v not in groups[d][s].keys():
        groups[d][s][v] = {}
        
    if c not in groups[d][s][v].keys():
        groups[d][s][v][c] = []
        

for k in keys:
    name = k.GetName()
    parse = name.split("___")
    if len(parse) < 5: continue
    d = parse[0]
    s = parse[1]
    c = parse[2]
    v = parse[3]
    if not "type" in parse[4]: continue
    index = int(parse[4].replace("types_",""))
    print ("check",index,name)
    h = f.Get(name)
    if h.GetEntries() <= 0: continue
    h.Scale(1.,"width")
    h.SetFillColor(colors[index])
    
    if c == "qelikenot":  # make a better way to do this.
        index += 10
        h.SetFillStyle(3244)
    groups[d][s][v][c].append([index,h])
    print (groups[d][s][v][c])
    
    
template = "%s___%s___%s___%s"
for a in groups.keys():
    for b in groups[a].keys():
        for c in groups[a][b].keys():
            for d in groups[a][b][c].keys():
                name = template%(a,b,c,d)
                if d == "qelike":
                    stack = THStack(name.replace("types","stack"),"")
                    leg = CCQELegend(0.5,0.7,0.9,0.9)
                    cc = CCQECanvas(name,name)
                
                for g in groups[a][b][c][d]:
                    #print (g)
                    index = g[0]
                    h = g[1]
                    if d == "qelike":
                        xaxis = h.GetXaxis().GetTitle()
                        main = h.GetTitle()
                    
                    #if h.GetEntries()<=0.0:
                        #continue
                    #print ("g",a,b,c,d,g,index,h)
                    stack.Add(h)
                    leg.AddEntry(h,process[index],'f')
                    
            stack.SetTitle(b + "_" + c +";"+xaxis)
            stack.Draw("hist")
            leg.Draw()
            cc.Draw()
            cc.Print(a+"_" + b + "_" + c +".png")
            
    

