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
legendfontsize = 0.03
# plottile = "Q^{2}_{QE} vs Primary Proton Score: 2 tracks"


varstodo = [
    "Q2QE_PrimaryProtonScore",
    "Q2QE_PrimaryProtonScore1"
]

varnames = {
    "Q2QE": "Q^{2}_{QE} (GeV^{2})",
    "PrimaryProtonScore": "Proton Score",
    "PrimaryProtonScore1": "Proton Score1"
}

catstodo = [
    "qelike",
    "qelikenot",
    "chargedpion"
]

catsnames = {
    "data":"data", 
    "qelike":"QElike",
    "chargedpion":"1#pi^{#pm}",
    "qelikenot": "QElikeNot"
    # "multipion":"N#pi",
    # "other":"Other"
}

catscolors = {
    "data":ROOT.kBlack, 
    "qelike":ROOT.kBlue+2,
    "qelikenot": ROOT.kRed+1,
    "chargedpion":ROOT.kRed+1,
    # "neutralpion":ROOT.kRed,
    # "multipion":ROOT.kGreen-6,
    # "other":ROOT.kYellow-6
}
scalevar = ["Q2QE"]



def CCQECanvas(name,title,xsize=1000,ysize=1800):
    c2 = ROOT.TCanvas(name,title,xsize,ysize)
    # c2.SetLeftMargin(0.1)
    c2.SetRightMargin(0.15)
    c2.SetLeftMargin(0.11)
    c2.SetTopMargin(0.1)
    c2.SetBottomMargin(0.1)
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



# 
if len(sys.argv) == 1:
    print ("enter root file name and optional 2nd argument to get tuned version")
flag = "types_"
filename = sys.argv[1]
if len(sys.argv)> 2:
    flag = "tuned_type_"


f = TFile.Open(filename,"READONLY")

dirname = filename.replace(".root","_BoxPlotComp")
if not os.path.exists(dirname): os.mkdir(dirname)

keys = f.GetListOfKeys()

h_pot = f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(3)
POTScale = dataPOT / mcPOTprescaled
print("POTScale: ",POTScale)

groups = {}


hist_dict = {}
for var in varstodo:
    hist_dict[var] = {}
    for cat in catstodo:
        hist_dict[var][cat]=None

for k in keys:
    name = k.GetName()
    if "___" not in name:
        continue
    parse = name.split("___")
    if len(parse) < 5: continue
    dim = parse[0]
    sample = parse[1]
    cat = parse[2]
    var = parse[3]
    type = parse[4]
    if dim!="h2D": continue
    if type!="reconstructed": continue
    if cat not in catstodo: continue
    if var not in varstodo: continue

    hist = f.Get(name).Clone()
    hist.SetLineColor(catscolors[cat])
    hist.SetLineWidth(3)
    hist.Scale(1.0,"width")
    # hist.RebinY()
    # hist.SetFillColor(catscolors[cat])
    hist_dict[var][cat] = hist

ROOT.gStyle.SetOptStat(0)

for var in varstodo:
    logX = False
    logY = False
    varsplit=var.split("_")
    if varsplit[0] in scalevar:
        logX = True
    if varsplit[1] in scalevar:
        logY = True
    plottitle = "%s vs %s: 2 tracks"%(varnames[varsplit[0]],varnames[varsplit[1]])
    hist_dict[var]["qelike"].SetTitle(plottitle)
    hist_dict[var]["qelike"].GetXaxis().SetTitle(varnames[varsplit[0]])
    hist_dict[var]["qelike"].GetYaxis().SetTitle(varnames[varsplit[1]])
    hist_dict[var]["qelike"].GetXaxis().CenterTitle()
    hist_dict[var]["qelike"].GetYaxis().CenterTitle()
    for cat in catstodo:
        if cat == "qelike":
            continue
        canvas_name = "%s_%s_BoxPlot"%(cat,var)
        # hist_dict[var][cat].SetTitle(plottitle)
        # hist_dict[var][cat].GetXaxis().SetTitle(varnames[varsplit[0]])
        # hist_dict[var][cat].GetYaxis().SetTitle(varnames[varsplit[1]])
        # hist_dict[var][cat].GetXaxis().CenterTitle()
        # hist_dict[var][cat].GetYaxis().CenterTitle()
        leg = CCQELegend(0.85,0.57,0.97,0.43)
        # leg.SetNColumns(2)

        dummyqelike = hist_dict[var]["qelike"].Clone()
        dummyqelike.SetFillColor(catscolors["qelike"])
        leg.AddEntry(dummyqelike,catsnames["qelike"],"f")


        hist_dict[var]["qelike"].SetFillColor(catscolors["qelike"])
        hist_dict[var]["qelike"].SetFillColorAlpha(catscolors["qelike"],0.6)

        hist_dict[var][cat].SetFillColor(catscolors[cat])
        hist_dict[var][cat].SetFillColorAlpha(catscolors[cat],0.6)

        # hist_dict[var][cat].SetFillColor(catscolors[cat])
        # leg.AddEntry(hist_dict[var][cat],catsnames[cat],"f")
        dummycat = hist_dict[var][cat].Clone()
        dummycat.SetFillColor(catscolors[cat])
        leg.AddEntry(dummycat,catsnames[cat], "f")

        hist_dict[var][cat].SetLineWidth(3)
        hist_dict[var]["qelike"].SetLineWidth(3)

        canvas = CCQECanvas(var,var)
        if logX:
            canvas.SetLogx()
        if logY:
            canvas.SetLogy()
        # canvas.SetLogz()
        # hist_dict[var][cat].Draw("BOX")
        # hist_dict[var]["qelike"].Draw("BOX same")
        hist_dict[var]["qelike"].Draw("BOX")
        hist_dict[var][cat].Draw("BOX same")
        leg.Draw()
        canvas.Print(dirname+"/"+canvas_name+".png")


    


