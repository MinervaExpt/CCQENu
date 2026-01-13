# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023


from re import L
import sys,os
import ROOT
import numpy as np
from ROOT import (
    gROOT,
    gStyle, 
    TFile,
    THStack,
    TH1D,
    TCanvas, 
    TColor,
    TObjArray,
    TH2F,
    THStack,
    TLegend,
    TLatex, 
    TString,
    TPad
)
from PlotUtils import MnvH1D, MnvPlotter
import datetime
mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")

TEST=False
global_noData=False  # use this to plot MC only types
sigtop=True # use this to place signal on top of background
dotuned=False
dowarp = False
doratio = True
dotypes = False

ROOT.TH1.AddDirectory(ROOT.kFALSE)
legendfontsize = 0.042
_xsize = 1800.0
_ysize = 1200.0

latex_x = 0.55
latex_y = 0.43


def MakePlotDir(subdir=""):
    """
    Subdir is the one for all plots that this script should ouptut. You will need to add
    any other subdirs in the script itself (e.g. based off input file name)
    """
    plotdir = ""
    base_plotdir = os.environ.get("PLOTSLOC")
    if base_plotdir != None:
        plotdir = os.path.join(base_plotdir, month + year)
    else:
        plotdir = os.path.join("/Users/nova/git/plots/", month + year)
    if not os.path.exists(plotdir):
        print("Can't find plot dir. Making it now... ", plotdir)
        os.mkdir(plotdir)
    if subdir == "":
        return plotdir
    if not os.path.exists(os.path.join(plotdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(plotdir, subdir))
        os.mkdir(os.path.join(plotdir, subdir))
    return os.path.join(plotdir, subdir)

def MakeDataMCRatio(i_data, i_mctot):
    mcratio = i_data.Clone(str(i_data.GetName().replace("data", "datamcratio")))
    mcratio.Divide(i_data, i_mctot)
    return mcratio

# def GetChi2NDF(i_data, i_mctot):
#     chi2 = -9999.
#     if i_data.GetNbinsX() != i_mctot.GetNbinsX(): return chi2
#     nbins = i_data.GetNbinsX()
#     for i in range(1,nbins+1):
#         datacont = i_data.GetBinContent(i)
#         mccont = i_mctot.GetBinContnent(i)
#         if data


def CCQECanvas(name,title,xsize=1100,ysize=720):
    c2 = ROOT.TCanvas(name, title, round(xsize), round(ysize))
    # c2.SetLeftMargin(0.1)
    c2.SetRightMargin(0.04)
    # c2.SetLeftMargin(0.1)
    c2.SetTopMargin(0.04)
    # c2.SetBottomMargin(0.1)
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

catstodo = [
    "data",
    "qelike",
    "chargedpion",
    "neutralpion",
    # "multipion",
    "other"
]
catsnames = {
"data":"data", 
"qelike":"QElike",
"chargedpion":"1#pi^{#pm}",
"neutralpion":"1#pi^{0}",
"multipion":"N#pi",
"other":"Other"
}

catscolors = {
"data":ROOT.kBlack, 
"qelike":ROOT.kBlue-6,
"chargedpion":ROOT.kMagenta-6,
"neutralpion":ROOT.kRed-6,
"multipion":ROOT.kGreen-6,
"other":ROOT.kYellow-6
}

samplenames = {
    "QElike_warped": "no 2p2h tune",
    "QElike": "QElike Signal Sample",
    "QElike_2track": "QElike 2 track Sample",
    "QElike0Blob": "QElike Signal w/o Blobs",
    "QElike1Blob": "QElike Signal w/ 1 Blob",
    "QElikeOld": "2D Era QElike Signal Sample",
    # "BlobSideband": "1 #pi^{0} Sideband",
    "BlobSideband": "Blob Sideband",
    "MultipBlobSideband": "Multiple #pi Sideband",
    "HiPionThetaSideband": "Backward #pi^{#pm} Sideband",
    "LoPionThetaSideband": "Forward #pi^{#pm} Sideband",
    "TrackSideband": "Track Sideband"
}
if len(sys.argv) == 1:
    print ("enter root file name and optional 2nd argument to get tuned version")
flag = "types_"
filename = sys.argv[1]
if len(sys.argv)> 2:
    flag = "tuned_type_"


f = TFile.Open(filename,"READONLY")

plotdirbase = os.getenv("OUTPUTLOC")

plotdir = MakePlotDir("Dists1D")
dirname = filename.replace(".root", "_Dists1D")
# outfilename=filebasename1.replace(".root","_2DPlots")
outdirname = os.path.join(plotdir, dirname)
if not os.path.exists(outdirname):
    print(outdirname)
    os.mkdir(outdirname)
keys = f.GetListOfKeys()

keys = f.GetListOfKeys()

h_pot = f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(2)
POTScale = dataPOT / mcPOTprescaled
print("POTScale: ",POTScale)

groups = {}
scaleX = ["Q2QE"]
scaleY = []#"recoil","EAvail"]


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
    hist = parse[0]
    sample = parse[1]
    cat = parse[2]
    variable = parse[3]
    if hist != "h": continue
    if "types" in parse[4]:
        continue
    if "simulfit" in parse[4]:
        continue
    if cat not in catstodo: continue
    if "reconstructed" not in parse[4]:
        continue
    if "tuned" in parse[4]:
        sample += "_Tuned"

    if sample not in groups.keys():
        groups[sample] = {}
        
    if variable not in groups[sample].keys():
        groups[sample][variable] = {}
        
    if cat not in groups[sample][variable].keys():
        groups[sample][variable][cat] = {}
    
    h = f.Get(name).Clone()
    if h.GetEntries() <= 0: 
        print("WARNING: hist ", name, " is empty. Skipping...")
        continue
    h.SetFillColor(catscolors[cat])
    h.SetLineColor(ROOT.kBlack)
    if "data" in cat:
        h.Scale(1.0, "width")
        # h.Scale(1.0)
        h.SetMarkerStyle(20)
        h.SetMarkerSize(1.5)
    else:
        print("scaling hist ", name)
        h.Scale(POTScale, "width")
        # h.Scale(POTScale)
    groups[sample][variable][cat] = h

ROOT.gStyle.SetOptStat(0)
for a_sample in groups.keys():
    datasample = a_sample
    plottitle = ""
    if "warped" in a_sample:
        datasample = datasample.replace("_warped","")
        plottitle += "Warped "
    if "_Tuned" in a_sample:
        dotuned = True
        datasample = datasample.replace("_Tuned","")
        plottitle += "Tuned "
    else:
        dotuned = False
    plottitle +=  samplenames[datasample]

    for b_var in groups[a_sample].keys():
        noData = global_noData
        if "data" not in groups[datasample][b_var].keys():
            noData = True
        # Figure out what order to put the mc in for stack plots (backgrounds first, then signal)
        mc_order = list([
            "qelikenot",
            "qelike"
            ])
        if "qelikenot" not in groups[a_sample][b_var].keys():
            mc_order = list([
                "other",
                "neutralpion",
                "chargedpion",
                "qelike"
                ])
        
        # Set up the legend
        leg = CCQELegend(0.6,0.75,1.,0.95)
        leg.SetNColumns(2)

        # Make a dummy data hist and put the data in it if needed
        data = MnvH1D()
        if not noData:
            data = groups[datasample][b_var]["data"]

        # Now make the stack for the plot, and total mc for the ratio and the chi2
        stack = THStack("stack","")
        mctot = MnvH1D()
        firstmc = True
        for c_cat in mc_order:
        # for c_cat in groups[a_sample][b_var].keys():
            if c_cat not in groups[a_sample][b_var].keys():
                print("WARNING: cat ", c_cat, "in mc_order but not in hists")
                continue
            if c_cat in ["data","mctot","stack"]:
                continue
            if firstmc:
                mctot = groups[a_sample][b_var][c_cat].Clone("mctot")
                firstmc = False
            else:
                mctot.Add(groups[a_sample][b_var][c_cat])
            stack.Add(groups[a_sample][b_var][c_cat])
            leg.AddEntry(groups[a_sample][b_var][c_cat],catsnames[c_cat],"f")
        if not noData:
            leg.AddEntry(data,"data","pe") # TODO need to figure out how to order this properly



        # Make the canvas
        thename = "%s_%s"%(a_sample,b_var)
        thetitle = "%s %s"%(a_sample,b_var)
        ysize = _ysize
        xsize = _xsize
        if doratio and not noData:
            ysize = 1.2 * _ysize
        cc = CCQECanvas(thename, thetitle, xsize, ysize)

        # If do ratio, set up the top and bottom pads for the hists
        if doratio and not noData:
            top = TPad("hist", "hist", 0, 0.278, 1, 1)
            top.SetRightMargin(0.04)
            top.SetBottomMargin(0)
            top.SetTopMargin(0.04)
            bottom = TPad("Ratio", "Ratio", 0, 0, 1, 0.278)
            bottom.SetRightMargin(0.04)
            bottom.SetTopMargin(0)
            top.Draw()
            bottom.Draw()

            bottomArea = bottom.GetWNDC() * bottom.GetHNDC()
            topArea = top.GetWNDC() * top.GetHNDC()
            areaScale = topArea / bottomArea
            # Move to top pad for hists
            top.cd()
        
        # Do stack first
        stack.Draw("")

        # set up its y axis
        stack.GetYaxis().SetTitle("Counts/unit")
        stack.GetYaxis().CenterTitle()
        stack.GetYaxis().SetTitleOffset(0.6)
        stack.GetYaxis().SetTitleSize(0.05)
        stack.GetYaxis().SetLabelSize(stack.GetYaxis().GetLabelSize() * 1.4)

        # set up its x axis if relevant
        x_title = ""
        if not noData:
            x_title = data.GetXaxis().GetTitle()
        else:
            x_title = groups[a_sample][b_var][mc_order[0]].GetXaxis().GetTitle()
        if not doratio or noData:
            stack.GetXaxis().SetTitle(x_title)
            stack.GetXaxis().CenterTitle()
            stack.GetXaxis().SetTitleSize(0.05)

        # figure out the maximums
        if not noData:
            stack.SetMaximum(1.2 * max(data.GetMaximum(), stack.GetMaximum()))
        else:
            stack.SetMaximum(1.2 * stack.GetMaximum())
        
        stack.Draw("hist")
        if not noData:
            data.Draw("PE same")
        leg.Draw()

        if doratio and not noData:
            bottom.cd()
            bottom.SetBottomMargin(0.3)

            # make the ratio and make it pretty
            mctot.SetFillStyle(1001)
            ratio = MakeDataMCRatio(data, mctot)
            ratio.SetMinimum(0.5)
            ratio.SetMaximum(1.5)

            ratio.SetLineColor(ROOT.kBlack)
            ratio.SetLineWidth(3)

            ratio.SetTitle("")            
            ratio.GetYaxis().SetTitle("Data / MC")
            ratio.GetYaxis().CenterTitle()
            ratio.GetYaxis().SetTitleSize(0.05 * areaScale)
            ratio.GetYaxis().SetLabelSize(ratio.GetYaxis().GetLabelSize() * areaScale*1.2)
            ratio.GetYaxis().SetNdivisions(-505)

            ratio.GetXaxis().SetTitle(x_title)
            ratio.GetXaxis().CenterTitle()
            ratio.GetXaxis().SetTitleSize(0.05 * areaScale)
            ratio.GetXaxis().SetLabelSize(ratio.GetXaxis().GetLabelSize() * areaScale*1.5)

            ratio.Draw()

            # Now do mc uncertainties
            mcerror = TH1D(mctot.GetTotalError(False, True, False))
            for bin in range(1, mcerror.GetXaxis().GetNbins() + 1):
                mcerror.SetBinError(bin, max(mcerror.GetBinContent(bin), 1.0e-9))
                mcerror.SetBinContent(bin, 1.0)
            mcerror.SetLineColor(ROOT.kRed)
            mcerror.SetLineWidth(3)
            mcerror.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
            mcerror.Draw("same E2")

            # Now do a line at 1
            straightline = mcerror.Clone()
            straightline.SetFillStyle(0)
            straightline.Draw("hist same")

            ratio.Draw("same")

            # Go back to the top pad 
            top.cd()
        # Dress plot with text
        prelim = AddPreliminary()
        titleonplot = MakeTitleOnPlot()
        prelim.DrawLatex(latex_x, latex_y, "MINER#nuA Work In Progress")
        titleonplot.DrawLatex(0.37, 0.9, plottitle)
        # calculate chi2 and do that too
        if not noData:
            # # tdata= TH1D()
            # tdata = data.GetCVHistoWithError()
            # tmctot = mctot.GetCVHistoWithError()
            # chi2 = tdata.Chi2Test(tmctot, "CHI2,UW")
            plotter = MnvPlotter()
            chi2 = plotter.Chi2DataMC(data,mctot)
            chi2_latex = ROOT.TLatex()
            chi2_latex.SetNDC()
            chi2_latex.SetTextSize(legendfontsize-0.004)
            chi2_latex.SetTextAlign(11)
            chi2_latex.DrawLatex(0.6,0.69, "#chi^{2} = "+ "{:g}".format(float('{:.{p}g}'.format(chi2, p=5))))
            # chi2_latex.DrawLatex(0.6,0.69, "#chi^{2} = "+str(chi2))
            del plotter
        canvas_name = thename + "_FinalStates"
        if dotypes:
            canvas_name = thename + "Types"
        if dotuned:
            canvas_name += "_tuned"

        cc.Print(os.path.join(outdirname, canvas_name + ".png"))
        cc.Print(os.path.join(outdirname, "source", canvas_name + ".C"))

        del cc

# # now that the structure is created, stuff histograms into it after scaling for POT
# for k in keys:
#     name = k.GetName()
#     parse = name.split("___")
#     if len(parse) < 5: continue
#     hist = parse[0]
#     if hist == "h2D": continue # only 1d
#     sample = parse[1]
#     cat = parse[2]
#     # if cat == "qelikenot": continue
#     if cat not in catstodo: continue
#     variable = parse[3]
#     if "reconstructed" not in parse[4]: continue
#     if "types" in parse[4]:
#         continue
#     if "simulfit" in parse[4]:
#         continue
#     if "tuned" not in parse[4] and dotuned and cat!="data":
#         continue
#     if "tuned" in parse[4] and not dotuned:
#         continue
#     # these are stacked histos
#     h = f.Get(name).Clone()
#     if h.GetEntries() <= 0: continue
#     h.SetFillColor(catscolors[cat])
#     h.SetLineColor(ROOT.kBlack)
    
#     if "data" in cat:
#         index = 0
#         h = f.Get(name)
#         if h.GetEntries() <= 0: continue
#         # h.Scale(1.,"width")
#         h.Scale(0.001,"width")
#         h.SetMarkerStyle(20)
#         h.SetMarkerSize(1.5)
#     if "data" not in cat:
#         print("scaling hist ",h.GetName())
#         # print("POTscale: ", POTScale)
#         h.Scale(POTScale*0.001,"width") #scale to data
#         # h.Scale(POTScale,"width") #scale to data
#     # if cat in ["chargedpion", "neutralpion", "multipion", "other"]:
#     #     h.SetFillStyle(3244)
#     groups[hist][sample][variable][cat]=h

#         #print ("data",groups[hist][sample][variable][c])

# for a_hist in groups.keys():
#     if a_hist != "h": continue # no 2D
#     #print ("a is",a)
#     for b_sample in groups[a_hist].keys():

#         datasample = b_sample
#         if b_sample == "QElike_warped":
#             datasample = "QElike"
#         if b_sample == "QElike" and dowarp: continue

#         for c_var in groups[a_hist][b_sample].keys():
#             firstmc = True
#             for d_cat in groups[a_hist][b_sample][c_var].keys():
#                 if d_cat in ["data","mctot"]:
#                     continue
#                 if firstmc:
#                     mctot = groups[a_hist][b_sample][c_var][d_cat].Clone("mctot")
#                     firstmc = False
#                 else:
#                     mctot.Add(groups[a_hist][b_sample][c_var][d_cat])
#             groups[a_hist][b_sample][c_var]["mctot"] = mctot
                
            


# # "h___MultiplicitySideband___qelike___pzmu___reconstructed"
# # h___MultipBlobSideband___other___pzmu___reconstructed
# # do the plotting


# # build an order which puts backgrounds below signal (assumes signal is first in list)
# bestorder = []

# ROOT.gStyle.SetOptStat(0)
# template = "%s___%s___%s___%s"
# print("here")
# for a_hist in groups.keys():
#     if a_hist != "h": continue # no 2D
#     #print ("a is",a)
#     for b_sample in groups[a_hist].keys():

#         datasample = b_sample
#         if b_sample == "QElike_warped":
#             datasample = "QElike"
#         if b_sample == "QElike" and dowarp: continue

#         for c_var in groups[a_hist][b_sample].keys():
#             noData = global_noData
#             if "data" not in groups[a_hist][b_sample][c_var].keys():
#                 noData = False
#             print("here")

#             first = 0
#             leg = CCQELegend(0.6,0.75,1.,0.95)
#             leg.SetNColumns(2)
#             thename = "%s_%s"%(b_sample,c_var)
#             thetitle = "%s %s"%(b_sample,c_var)
#             # do the data first
#             cc = CCQECanvas(name,name)
#             if c_var in scaleX:
#                 cc.SetLogx()
#             # if c_var in scaleY:
#             cc.SetLogy()
            
#             data = TH1D()
#             # if len(groups[a_hist][datasample][c_var]["data"]) < 1:
#             #     print (" no data",a_hist,b_sample,c_var)
#             #     continue
            
#             data = TH1D(groups[a_hist][datasample][c_var]["data"])
#             plottitle=samplenames[b_sample]
#             if dotuned:
#                 plottitle = "Tuned "+plottitle
#             # data.SetTitle(plottitle)
#             data.SetTitle("")
#             # data.GetYaxis().SetTitle("Counts/unit (bin width normalized)")
#             # data.GetYaxis().SetTitle("Counts/unit")
#             data.GetYaxis().SetTitle("Counts #times 10^{3}/GeV^{2}")
#             data.GetYaxis().CenterTitle()
#             data.GetYaxis().SetTitleSize(0.05)
#             data.GetYaxis().SetLabelSize(0.04)

#             # data.GetXaxis().SetTitle("Recoil in GeV")
#             data.GetXaxis().CenterTitle()
#             data.GetXaxis().SetTitleSize(0.05)    
#             data.GetXaxis().SetLabelSize(0.04)

#             dmax = data.GetMaximum()
#             if noData:
#                 dmax = 0.0
#             #data.Draw("PE")
#             if not noData: leg.AddEntry(data,"data","pe")
            
#             data.Print()
            
#             bestorder = list([
#                 "other",
#                 # "multipion",
#                 "neutralpion",
#                 "chargedpion",
#                 "qelike"
#             ])

#             for d_cat in bestorder:
#                 if d_cat == "data": continue
#                 if first == 0: # make a stack
#                     stack = THStack(name.replace("reconstructed","stack"),"")
#                 first+=1
#                 h = groups[a_hist][b_sample][c_var][d_cat]
#                 stack.Add(h)
#                 leg.AddEntry(h,catsnames[d_cat],"f")
#             smax = stack.GetMaximum()
#             #print ("max",smax,dmax)
#             max_multiplier = 1.4

#             if c_var in scaleY:
#                 max_multiplier = 2.0
#                 data.SetMinimum(0.)
#                 data.GetXaxis().SetRangeUser(0.0,0.5)
#             if smax > dmax:
#                 data.SetMaximum(smax*max_multiplier)
#                 stack.SetMaximum(smax*max_multiplier)
#             else:
#                 data.SetMaximum(dmax*max_multiplier)
#                 stack.SetMaximum(dmax*max_multiplier)
#             if not noData: 
#                 data.Draw("PE")
#                 stack.Draw("hist same")
#             else:
#                 data.Reset()
#                 data.Draw("hist")  # need to this to get the axis titles from data
#                 stack.Draw("hist same")
#                 data.Draw("AXIS same")
#             if not noData: 
#                 data.Draw("AXIS same")
#                 data.Draw("PE same")
#             leg.Draw()
#             prelim = AddPreliminary()
#             prelim.DrawLatex(0.6,0.72,"MINER#nuA Work In Progress")

#             chi2 = groups[a_hist][b_sample][c_var]["data"].Chi2Test(groups[a_hist][b_sample][c_var]["mctot"], "CHI2/NDF")
#             chi2_latex = ROOT.TLatex()
#             chi2_latex.SetNDC()
#             chi2_latex.SetTextSize(legendfontsize-0.004)
#             chi2_latex.SetTextAlign(11)
#             chi2_latex.DrawLatex(0.6,0.69,"#chi^{2} = %d"%chi2)

#             titleonplot = MakeTitleOnPlot()
#             titleonplot.DrawLatex(0.37,0.85,plottitle)
#             cc.Draw()

#             canvas_name=thename+"_FinalStates"
#             if dotuned:
#                 canvas_name = thename+"_FinalStates_tuned"
#             cc.Print(dirname+"/"+canvas_name+".png")
#             cc.Print(dirname+"/"+canvas_name+".C")

#             del cc
