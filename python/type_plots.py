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

nproc = len(process)

for x in range(0,nproc+1):
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

if len(sys.argv) == 1:
    print ("enter root file name and optional 2nd argument to get tuned version")
flag = "types_"
filename = sys.argv[1]
if len(sys.argv)> 2:
    flag = "tuned_type_"
    

f = TFile.Open(filename,"READONLY")

keys = f.GetListOfKeys()

h_pot = f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1);
mcPOTprescaled = h_pot.GetBinContent(3);
POTScale = dataPOT / mcPOTprescaled;
    
groups = {}
scaleX = ["Q2QE","Log10Recoil"]
scaleY = ["recoil"]
# find all the valid histogram and group by keywords
ncats = 0
for k in keys:
    name = k.GetName()
    if "___" not in name:
        continue
    parse = name.split("___")
    if len(parse) < 5: continue
    #print (parse)
    if not flag in parse[4] and not "data" in parse[2]: continue
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
        groups[d][s][v][c] = {}
    # need to know the #of categories later
    #print ("cats",groups[d][s][v].keys())
    if len(groups[d][s][v].keys())-1 > ncats:
        ncats = len(groups[d][s][v].keys())-1

for k in keys:
    name = k.GetName()
    parse = name.split("___")
    if len(parse) < 5: continue
    d = parse[0]
    if d == "h2D": continue # only 1d
    s = parse[1]
    c = parse[2]
    v = parse[3]
    if flag in parse[4]:
        index = int(parse[4].replace(flag,""))
        #print ("check",index,name)
        h = f.Get(name)
        if h.GetEntries() <= 0: continue
        h.Scale(POTScale,"width") #scale to data
        # h.Scale(POTScale) #scale to data
        h.SetFillColor(colors[index])
        
        if c in ["qelikenot","qelikenot_np"] :  # make a better way to do this, maybe code in the input file?
            index += 10
            h.SetFillStyle(3244)
        groups[d][s][v][c][index]=h
        #print ("mc",groups[d][s][v][c])
    if "data" in c:
        index = 0
        h = f.Get(name)
        
        if h.GetEntries() <= 0: continue
        h.Scale(1.,"width")
        h.SetMarkerStyle(20)
        groups[d][s][v][c][index]=h
        #print ("data",groups[d][s][v][c])
        
    
# do the plotting


# build an order which puts backgrounds below signal (assumes signal is first in list)
bestorder = []

ROOT.gStyle.SetOptStat(0)
template = "%s___%s___%s___%s"
for a in groups.keys():
    if a != "h": continue # no 2D
    #print ("a is",a)
    for b in groups[a].keys():
        for c in groups[a][b].keys():
        
            first = 0
            leg = CCQELegend(0.5,0.7,0.9,0.9)
            leg.SetNColumns(2)
            thename = "%s_%s_%s"%(b,c,d)
            thetitle = "%s %s %s"%(b,c,d)
            # do the data first
            cc = CCQECanvas(name,name)
            if c in scaleX:
                cc.SetLogx()
            if c in scaleY:
                cc.SetLogy()
            data = TH1D()
            if len(groups[a][b][c]["data"]) < 1:
                print (" no data",a,b,c)
                continue
            
            data = TH1D(groups[a][b][c]["data"][0])
            data.SetTitle(thetitle)
            data.GetYaxis().SetTitle("Counts/unit (bin width normalized)")
            data.Draw("PE")
            leg.AddEntry(data,"data","pe")
            
            data.Print()
            
            # do the MC
            # move the first category to the top of the plot
            bestorder = list(groups[a][b][c].keys()).copy()
            signal = bestorder[1]
            bestorder = bestorder[2:]
            bestorder.append(signal)
            for d in bestorder:
                if d == "data": continue
                if first == 0: # make a stack
                    stack = THStack(name.replace(flag,"stack"),"")
                first+=1
                for index in groups[a][b][c][d].keys(): #fill the stack
                    #print("index",index,bestorder,groups[a][b][c][d])
                    if index == 0: continue
                    if index not in groups[a][b][c][d]: continue
                    #print ("do this one ",  index,bestorder)
                    h = groups[a][b][c][d][index]
                    stack.Add(h)
                    leg.AddEntry(h,process[index],'f')
            
            max = (data.GetMaximum())*1.2
            stack.SetMaximum(max)
            stack.Draw("hist same")
            data.Draw("PE same")
            leg.Draw()
            cc.Draw()
            cc.Print(thename+"_"+flag+"v1_norecoilcut.png")
            # cc.Print(thename+"_"+flag+"v1_recoilcut.png")
            # cc.Print(thename+"_"+flag+"v12_norecoilcut.png")
            # cc.Print(thename+"_"+flag+"v12_recoilcut.png")
            
    
# flag = "types_v1_norecoilcut"
# flag = "types_v1_recoilcut"
# flag = "types_v12_norecoil"
# flag = "types_v12_norecoilcut"

