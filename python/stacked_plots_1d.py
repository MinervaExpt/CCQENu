# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023



from re import L
import sys,os
import ROOT
from ROOT import gROOT,gStyle, TFile,THStack,TH1D,TCanvas, TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex, TString

TEST=False
noData=True  # use this to plot MC only types
sigtop=True # use this to place signal on top of background
dotuned=False
ROOT.TH1.AddDirectory(ROOT.kFALSE)

legendfontsize = 0.042



def CCQECanvas(name,title,xsize=1000,ysize=720):
    c2 = ROOT.TCanvas(name,title,xsize,ysize)
    # c2.SetLeftMargin(0.1)
    c2.SetRightMargin(0.04)
    c2.SetLeftMargin(0.13)
    c2.SetTopMargin(0.04)
    c2.SetBottomMargin(0.14)
    return c2

def CCQELegend(xlow,ylow,xhigh,yhigh):
    leg = ROOT.TLegend(xlow,ylow,xhigh,yhigh)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(legendfontsize)
    return leg


def AddPreliminary():
    font = 112
    color = ROOT.kRed +1
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(legendfontsize-0.004)
    latex.SetTextColor(color)
    latex.SetTextFont(font)
    latex.SetTextAlign(11)
    return latex

def MakeTitleOnPlot():
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.058)
    latex.SetTextAlign(21)
    return latex


catsnames = {
"data":"data", 
"qelike":"QElike",
"chargedpion":"1#pi^{#pm}",
"neutralpion":"1#pi^{0}",
"multipion":"N#pi",
"other":"Other"}
catscolors = {
"data":ROOT.kBlack, 
"qelike":ROOT.kBlue-6,
"chargedpion":ROOT.kMagenta-6,
"neutralpion":ROOT.kRed-6,
"multipion":ROOT.kGreen-6,
"other":ROOT.kYellow-6}

samplenames = {
    "BlobSideband": "1 #pi^{0} Sideband",
    "MultipBlobSideband": "Multiple #pi Sideband",
    "QElike": "QElike Signal Sample",
    "QElikeOld": "2D Era QElike Signal Sample",
    "HiPionThetaSideband": "Backward #pi^{#pm} Sideband",
    "LoPionThetaSideband": "Forward #pi^{#pm} Sideband",
}
if len(sys.argv) == 1:
    print ("enter root file name and optional 2nd argument to get tuned version")
flag = "types_"
filename = sys.argv[1]
if len(sys.argv)> 2:
    flag = "tuned_type_"


f = TFile.Open(filename,"READONLY")

dirname = filename.replace(".root","_FinalStates")
if not os.path.exists(dirname): os.mkdir(dirname)

keys = f.GetListOfKeys()

h_pot = f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(3)
POTScale = dataPOT / mcPOTprescaled
print("POTScale: ",POTScale)

groups = {}
scaleX = ["Q2QE"]
scaleY = ["recoil","EAvail"]


# find all the valid histogram and group by keywords
ncats = 5
for k in keys:
    name = k.GetName()
    if "___" not in name:
        continue
    parse = name.split("___")
    if len(parse) < 5: continue
    #print (parse)
    # names look like : hist___Sample___category__variable___types_0;
    # if not flag in parse[4] and not "data" in parse[2]: continue
    if "reconstructed" not in parse[4]: continue
    hist = parse[0]
    sample = parse[1]
    cat = parse[2]
    variable = parse[3]
    if "types" in parse[4]:
        continue
    # reorder so category is last
    if hist == "h2D": continue
    if cat == "qelikenot": continue
    if hist not in groups.keys():
        groups[hist] = {}
        #legs[parse[0]] = {}
    if sample not in groups[hist].keys():
        groups[hist][sample] = {}
        
    if variable not in groups[hist][sample].keys():
        groups[hist][sample][variable] = {}
        
    if cat not in groups[hist][sample][variable].keys():
        groups[hist][sample][variable][cat] = {}
    # neehist to know the #of categories later
    #print ("cats",groups[d][s][variable].keys())
    # if len(groups[hist][sample][variable].keys())-1 > ncats:
    #     ncats = len(groups[hist][sample][variable].keys())-1

# now that the structure is created, stuff histograms into it after scaling for POT
for k in keys:
    name = k.GetName()
    parse = name.split("___")
    if len(parse) < 5: continue
    hist = parse[0]
    if hist == "h2D": continue # only 1d
    sample = parse[1]
    cat = parse[2]
    if cat == "qelikenot": continue

    variable = parse[3]
    if "reconstructed" not in parse[4]: continue
    if "tuned" not in parse[4] and dotuned and cat!="data":
        continue
    if "tuned" in parse[4] and not dotuned:
        continue
    # these are stacked histos
    h = f.Get(name).Clone()
    if h.GetEntries() <= 0: continue
    h.SetFillColor(catscolors[cat])
    h.SetLineColor(catscolors[cat]+1)
    
    if "data" in cat:
        index = 0
        h = f.Get(name)
        if h.GetEntries() <= 0: continue
        # h.Scale(1.,"width")
        h.Scale(0.001,"width")
        h.SetMarkerStyle(20)
        h.SetMarkerSize(1.5)
    if "data" not in cat:
        print("scaling hist ",h.GetName())
        # print("POTscale: ", POTScale)
        h.Scale(POTScale*0.001,"width") #scale to data
        # h.Scale(POTScale,"width") #scale to data
    # if cat in ["chargedpion", "neutralpion", "multipion", "other"]:
    #     h.SetFillStyle(3244)
    groups[hist][sample][variable][cat]=h

        #print ("data",groups[hist][sample][variable][c])
    
# "h___MultiplicitySideband___qelike___pzmu___reconstructed"
# h___MultipBlobSideband___other___pzmu___reconstructed
# do the plotting


# build an order which puts backgrounds below signal (assumes signal is first in list)
bestorder = []

ROOT.gStyle.SetOptStat(0)
template = "%s___%s___%s___%s"

for a_hist in groups.keys():
    if a_hist != "h": continue # no 2D
    #print ("a is",a)
    for b_sample in groups[a_hist].keys():
        for c_var in groups[a_hist][b_sample].keys():
        
            first = 0
            leg = CCQELegend(0.6,0.75,1.,0.95)
            leg.SetNColumns(2)
            thename = "%s_%s"%(b_sample,c_var)
            thetitle = "%s %s"%(b_sample,c_var)
            # do the data first
            cc = CCQECanvas(name,name)
            if c_var in scaleX:
                cc.SetLogx()
            if c_var in scaleY:
                cc.SetLogy()
            
            data = TH1D()
            if len(groups[a_hist][b_sample][c_var]["data"]) < 1:
                print (" no data",a_hist,b_sample,c_var)
                continue
            
            data = TH1D(groups[a_hist][b_sample][c_var]["data"])
            plottitle=samplenames[b_sample]
            if dotuned:
                plottitle = "Tuned "+plottitle
            # data.SetTitle(plottitle)
            data.SetTitle("")
            # data.GetYaxis().SetTitle("Counts/unit (bin width normalized)")
            # data.GetYaxis().SetTitle("Counts/unit")
            data.GetYaxis().SetTitle("Counts #times 10^{3}/GeV^{2}")
            data.GetYaxis().CenterTitle()
            data.GetYaxis().SetTitleSize(0.05)
            data.GetYaxis().SetLabelSize(0.04)

            # data.GetXaxis().SetTitle("Recoil in GeV")
            data.GetXaxis().CenterTitle()
            data.GetXaxis().SetTitleSize(0.05)    
            data.GetXaxis().SetLabelSize(0.04)

            dmax = data.GetMaximum()
            if noData:
                dmax = 0.0
            #data.Draw("PE")
            if not noData: leg.AddEntry(data,"data","pe")
            
            data.Print()
            
            bestorder = list(["other","multipion","neutralpion","chargedpion","qelike"])

            for d_cat in bestorder:
                if d_cat == "data": continue
                if first == 0: # make a stack
                    stack = THStack(name.replace("reconstructed","stack"),"")
                first+=1
                h = groups[a_hist][b_sample][c_var][d_cat]
                stack.Add(h)
                leg.AddEntry(h,catsnames[d_cat],"f")
            smax = stack.GetMaximum()
            #print ("max",smax,dmax)
            max_multiplier = 1.4

            if c_var in scaleY:
                max_multiplier = 2.0
                data.SetMinimum(500.)
                data.GetXaxis().SetRangeUser(0.0,0.5)
            if smax > dmax:
                data.SetMaximum(smax*max_multiplier)
                stack.SetMaximum(smax*max_multiplier)
            else:
                data.SetMaximum(dmax*max_multiplier)
                stack.SetMaximum(dmax*max_multiplier)
            if not noData: 
                data.Draw("PE")
                stack.Draw("hist same")
            else:
                data.Reset()
                data.Draw("hist")  # need to this to get the axis titles from data
                stack.Draw("hist same")
                data.Draw("AXIS same")
            if not noData: 
                data.Draw("AXIS same")
                data.Draw("PE same")
            leg.Draw()
            prelim = AddPreliminary()
            prelim.DrawLatex(0.6,0.72,"MINER#nuA Work In Progress")
            titleonplot = MakeTitleOnPlot()
            titleonplot.DrawLatex(0.37,0.85,plottitle)
            cc.Draw()
            canvas_name=thename+"_FinalStates"
            if dotuned:
                canvas_name = thename+"_FinalStates_tuned"
            cc.Print(dirname+"/"+canvas_name+".png")
            
    

