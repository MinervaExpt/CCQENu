# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023



from re import L
import sys,os
import ROOT
ROOT.gROOT.SetBatch(True) # Run in batch mode
from ROOT import gROOT,gStyle, TFile,THStack,TH1D,TCanvas, TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex, TString
from PlotUtils import MnvH1D
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
    "multipion",
    "other",
    "other_np",
]

catsnames = {
    "data":"data", 
    "qelike":"QElike",
    "chargedpion":"1#pi^{#pm}",
    "neutralpion":"1#pi^{0}",
    "qelikenot": "QElikeNot",
    "multipion":"N#pi",
    "other":"Other",
    "other_np":"Other",
}

skipcats = [
#     "other",
#     "other_np"
]
# catscolors = {
#     "data":ROOT.kBlack, 
#     "qelike":ROOT.kBlue+2,
#     "chargedpion":ROOT.kMagenta-1,
#     "neutralpion":ROOT.kRed-2,
#     "multipion":ROOT.kGreen-1,
#     "other":ROOT.kYellow-6,
#     "other_np":ROOT.kYellow-6,
# }
catscolors = {
    "data":ROOT.kBlack, 
    "qelike":ROOT.kP6Blue,
    "chargedpion":ROOT.kP6Yellow,
    "neutralpion":ROOT.kP6Red,
    "multipion":ROOT.kP6Grape,
    "other":ROOT.kP6Gray,
    "other_np":ROOT.kP6Gray,
}
hist_fill_style = "PE1"


scalevar = ["Q2QE"]



# def CCQECanvas(name,title,xsize,ysize):
# # def CCQECanvas(name,title,xsize=1200,ysize=900):
#     c2 = ROOT.TCanvas(name,title,xsize,ysize)
#     # c2.SetLeftMargin(0.1)
#     # c2.SetRightMargin(0.15)
#     # c2.SetLeftMargin(0.11)
#     # c2.SetTopMargin(0.1)
#     # c2.SetBottomMargin(0.1)
#     c2.SetLeftMargin(0.1)
#     c2.SetRightMargin(0.07)
#     c2.SetBottomMargin(0.11)
#     c2.SetTopMargin(0.1)
#     return c2

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
# for var in varstodo:
#     hist_dict[var] = {}
#     for cat in catstodo:
#         hist_dict[var][cat] = {}
#         for htype in scalefrac:
#             hist_dict[var][cat][htype] = None

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
    htype = parse[4]
    if dim!="h": continue
    if htype not in scalefrac: continue
    if cat in skipcats: continue
    # if var not in varstodo: continue
    if var not in hist_dict:
        hist_dict[var] = {}
    if cat not in hist_dict[var]:
        hist_dict[var][cat] = {}
    if htype not in hist_dict[var][cat]:
        hist_dict[var][cat][htype] = {}
    
    hist = f.Get(name).Clone()
    hist.SetLineColor(catscolors[cat])
    hist.SetMarkerColor(catscolors[cat])
    # hist.SetLineWidth(3)
    # hist.Scale(1.0,"width")
    # hist.RebinY()
    # hist.SetFillColor(catscolors[cat])
    hist.Print()
    hist_dict[var][cat][htype] = hist


ROOT.gStyle.SetOptStat(0)

for var in hist_dict:
    # canvas = CCQECanvas("scalefactorplots","scalefactorplots")
    canvas = ROOT.TCanvas()
    canvas.Print("scalefactorplots.pdf[","pdf")
    for htype in hist_dict[var]["qelike"]:
        print(var, htype)
# for var in varstodo:
#     for htype in scalefrac:
        logX = False
        logY = False
        if var in scalevar:
            logX = True
        
        plottitle = "%s vs %s"%(typenames[htype],varnames[var])

        first = True
        canvas_name = "%s_%s"%(var,htype)

        
        # leg = CCQELegend(0.6,0.9,0.9,0.7)
        # leg.SetNColumns(2)
        leg = ROOT.TLegend(0.7,0.25,0.9,0.55)
        leg.SetLineWidth(0)
        leg.SetFillStyle(-1)
        leg.SetTextSize(legendfontsize)
        for cat in hist_dict[var]:
            print(var, cat, htype)
            hist_dict[var][cat][htype].Print()
            leg.AddEntry(hist_dict[var][cat][htype],catsnames[cat],"fl")

            if logX:
                canvas.SetLogx()
            if logY:
                canvas.SetLogy()
            
            # canvas.SetLogz()
            # hist_dict[var][cat].Draw("BOX")
            # hist_dict[var]["qelike"].Draw("BOX same")
            if first:
                hist_dict[var][cat][htype].SetTitle(plottitle)
                hist_dict[var][cat][htype].GetXaxis().SetTitle(varnames[var])
                hist_dict[var][cat][htype].GetYaxis().SetTitle(typenames[htype])
                hist_dict[var][cat][htype].GetXaxis().CenterTitle()
                hist_dict[var][cat][htype].GetYaxis().CenterTitle()
                hist_dict[var][cat][htype].SetMinimum(0.0)
                hist_dict[var][cat][htype].SetLineWidth(2)
                if htype == "scale":
                    hist_dict[var][cat][htype].SetMaximum(1.4)
                    hist_dict[var][cat][htype].SetMinimum(0.1)                    
                    line = ROOT.TLine(0, 1., 4., 1.)
                    line.SetLineStyle(3)
                    line.SetLineWidth(3)
                    line.SetLineColor(36)
                    hist_dict[var][cat][htype].Draw("%s"%(hist_fill_style))
                    # hist_dict[var][cat][htype].GetCVHistoWithError().Draw("%s"%(hist_fill_style))
                    # hist_dict[var][cat][htype].GetCVHistoWithStatError().Draw("%s same"%(hist_fill_style))
                    line.Draw("same")
                    hist_dict[var][cat][htype].Draw("%s same"%(hist_fill_style))
                    # hist_dict[var][cat][htype].GetCVHistoWithStatError().Draw("%s same"%(hist_fill_style))

                else:
                    hist_dict[var][cat][htype].SetMaximum(1.)
                    hist_dict[var][cat][htype].Draw("%s"%(hist_fill_style))
                    # hist_dict[var][cat][htype].GetCVHistoWithError().Draw("%s"%(hist_fill_style))
                    # hist_dict[var][cat][htype].GetCVHistoWithStatError().Draw("%s same"%(hist_fill_style))
                first = False
            else:
                hist_dict[var][cat][htype].SetLineWidth(2)
                hist_dict[var][cat][htype].Draw("%s same"%(hist_fill_style))
                # hist_dict[var][cat][htype].GetCVHistoWithError().Draw("%s same"%(hist_fill_style))
                # hist_dict[var][cat][htype].GetCVHistoWithStatError().Draw("%s same"%(hist_fill_style))

        hist_dict[var]["qelike"][htype].Draw("%s same"%(hist_fill_style))

        leg.Draw()
        # canvas.Print(dirname+"/"+canvas_name+".pdf")
        canvas.Print("scalefactorplots.pdf","pdf")
    canvas.Print("scalefactorplots.pdf]","pdf")


    


