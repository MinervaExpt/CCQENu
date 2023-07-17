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

h_pot = f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1);
mcPOTprescaled = h_pot.GetBinContent(3);
POTScale = dataPOT / mcPOTprescaled;
    
groups = {}
# find all the valid histogram and group by keywords
for k in keys:
    name = k.GetName()
    if "___" not in name:
        continue
    parse = name.split("___")
    if len(parse) < 5: continue
    print (parse)
    if not "type" in parse[4] and not "data" in parse[2]: continue
    d = parse[0]
    s = parse[1]
    c = parse[2]
    v = parse[3]
    # reorder so category is last
    if d == "h2D": continue
    if d not in groups.keys():
        groups[d] = {}
        #legs[parse[0]] = {}
    if s not in groups[d].keys():
        groups[d][s] = {}
        
    if v not in groups[d][s].keys():
        groups[d][s][v] = {}
        
    if c not in groups[d][s][v].keys():
        groups[d][s][v][c] = []
        

for k in keys:
    name = k.GetName()
    parse = name.split("___")
    if len(parse) < 5: continue
    d = parse[0]
    if d == "h2D": continue # only 1d
    s = parse[1]
    c = parse[2]
    v = parse[3]
    if "type" in parse[4]:
        index = int(parse[4].replace("types_",""))
        print ("check",index,name)
        h = f.Get(name)
        if h.GetEntries() <= 0: continue
        h.Scale(POTScale,"width") #scale to data
        h.SetFillColor(colors[index])
        
        if c == "qelikenot":  # make a better way to do this, maybe code in the input file?
            index += 10
            h.SetFillStyle(3244)
        groups[d][s][v][c].append([index,h])
        print ("mc",groups[d][s][v][c])
    if "data" in c:
        index = 0
        h = f.Get(name)
        
        if h.GetEntries() <= 0: continue
        h.Scale(1.,"width")
        h.SetMarkerStyle(20)
        groups[d][s][v][c].append([index,h])
        print ("data",groups[d][s][v][c])
        
    
# do the plotting
ROOT.gStyle.SetOptStat(0)
template = "%s___%s___%s___%s"
for a in groups.keys():
    if a != "h": continue # no 2D
    print ("a is",a)
    for b in groups[a].keys():
        for c in groups[a][b].keys():
            first = 0
            leg = CCQELegend(0.5,0.7,0.9,0.9)
            leg.SetNColumns(2)
            name = "%s_%s_%s"%(a,b,c)
            
            # do the data first
            cc = CCQECanvas(name,name)
            data = TH1D()
            if len(groups[a][b][c]["data"]) < 1:
                print (" no data",a,b,c)
                continue
            data = TH1D(groups[a][b][c]["data"][0][1])
            data.SetTitle(name)
            data.Draw("PE")
            leg.AddEntry(data,"data","pe")
            
            data.Print()
            
            # do the MC
            for d in groups[a][b][c].keys():
                if d == "data": continue
                
                if first == 0:
                    stack = THStack(name.replace("types","stack"),"")
                    
                first+=1
                
                for g in groups[a][b][c][d]:
                    
                    index = g[0]
                    g[1].Print()
                    #print (g)
                    if index == 0: continue
                    h = g[1]
                    #if d == "qelike":
                    #    xaxis = h.GetXaxis().GetTitle()
                    #    main = h.GetTitle()
            
                    stack.Add(h)
                    leg.AddEntry(h,process[index],'f')
            
            stack.Draw("hist same")
            data.Draw("PE same")
            leg.Draw()
            cc.Draw()
            cc.Print(name+".png")
            
    

