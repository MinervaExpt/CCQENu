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
legendfontsize = 0.05
# plottile = "Q^{2}_{QE} vs Primary Proton Score: 2 tracks"

scalefrac = [
    "scale",
    "fraction"
]
typenames = {
    "scale": "Scale",
    "fraction": "Fraction"
}

varstodo = [
    "Q2QE"
]

varnames = {
    "Q2QE": "Q^{2}_{QE} (GeV^{2})",
    "PrimaryProtonScore": "Proton Score",
    "PrimaryProtonScore1": "Proton Score1"
}

catstodo = [
    "qelike",
    # "qelikenot",
    "chargedpion",
    "neutralpion",
    "other"
]

catsnames = {
    "data":"data", 
    "qelike":"QElike",
    "chargedpion":"1#pi^{#pm}",
    "neutralpion":"1#pi^{0}",
    # "qelikenot": "QElikeNot"
    # "multipion":"N#pi",
    "other":"Other"
}

catscolors = {
    "data":ROOT.kBlack, 
    "qelike":ROOT.kBlue,
    "chargedpion":ROOT.kMagenta,
    "neutralpion":ROOT.kRed,
    # "multipion":ROOT.kGreen-6,
    "other":ROOT.kYellow-5
}


scalevar = ["Q2QE"]



def CCQECanvas(name,title,xsize=1200,ysize=900):
    c2 = ROOT.TCanvas(name,title,xsize,ysize)
    # c2.SetLeftMargin(0.1)
    # c2.SetRightMargin(0.15)
    # c2.SetLeftMargin(0.11)
    # c2.SetTopMargin(0.1)
    # c2.SetBottomMargin(0.1)
    c2.SetLeftMargin(0.1)
    c2.SetRightMargin(0.07)
    c2.SetBottomMargin(0.11)
    c2.SetTopMargin(0.1)
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

# h_pot = f.Get("POT_summary")
# dataPOT = h_pot.GetBinContent(1)
# mcPOTprescaled = h_pot.GetBinContent(3)
# POTScale = dataPOT / mcPOTprescaled
# print("POTScale: ",POTScale)

groups = {}


hist_dict = {}
for var in varstodo:
    hist_dict[var] = {}
    for cat in catstodo:
        hist_dict[var][cat] = {}
        for type in scalefrac:
            hist_dict[var][cat][type] = None

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
    if dim!="h": continue
    if type not in scalefrac: continue
    if cat not in catstodo: continue
    if var not in varstodo: continue

    hist = f.Get(name).Clone()
    hist.SetLineColor(catscolors[cat])
    hist.SetMarkerColor(catscolors[cat])
    # hist.SetLineWidth(3)
    # hist.Scale(1.0,"width")
    # hist.RebinY()
    # hist.SetFillColor(catscolors[cat])
    hist_dict[var][cat][type] = hist

ROOT.gStyle.SetOptStat(0)

for var in varstodo:
    for type in scalefrac:
        logX = False
        logY = False
        if var in scalevar:
            logX = True
        
        plottitle = "%s vs %s"%(typenames[type],varnames[var])

        first = True
        canvas_name = "%s_%s"%(var,type)
        canvas = CCQECanvas(canvas_name,canvas_name)

        
        leg = CCQELegend(0.6,0.9,0.9,0.7)
        leg.SetNColumns(2)
        for cat in catstodo:
            leg.AddEntry(hist_dict[var][cat][type],catsnames[cat])

            if logX:
                canvas.SetLogx()
            if logY:
                canvas.SetLogy()
            
            # canvas.SetLogz()
            # hist_dict[var][cat].Draw("BOX")
            # hist_dict[var]["qelike"].Draw("BOX same")
            if first:
                hist_dict[var][cat][type].SetTitle(plottitle)
                hist_dict[var][cat][type].GetXaxis().SetTitle(varnames[var])
                hist_dict[var][cat][type].GetYaxis().SetTitle(typenames[type])
                hist_dict[var][cat][type].GetXaxis().CenterTitle()
                hist_dict[var][cat][type].GetYaxis().CenterTitle()
                hist_dict[var][cat][type].SetMinimum(0.0)
                hist_dict[var][cat][type].SetLineWidth(4)
                if type == "scale":
                    hist_dict[var][cat][type].SetMaximum(1.6)
                    line = ROOT.TLine(0, 1., 4., 1.)
                    line.SetLineStyle(2)
                    line.SetLineWidth(3)
                    line.SetLineColor(36)
                    hist_dict[var][cat][type].Draw("PE1")
                    line.Draw("same")
                    hist_dict[var][cat][type].Draw("PE1 same")
                else:
                    hist_dict[var][cat][type].SetMaximum(1.0)
                    hist_dict[var][cat][type].Draw("PE1")
                first = False
            else:
                hist_dict[var][cat][type].SetLineWidth(3)
                hist_dict[var][cat][type].Draw("PE1 same")
        leg.Draw()
        canvas.Print(dirname+"/"+canvas_name+".png")


    


