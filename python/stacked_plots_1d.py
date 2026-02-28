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
_xsize = 1200.0
_ysize = 900.0

latex_x = 0.55
latex_y = 0.43

pad_lmarg = 0.07
pad_rmarg = 0.04
topmarg = 0.05
bottommarg = 0.3

legendfontsize = 0.05
legx1 = 0.7
legx2 = 1.0
legy1 = 0.65
legy2 = 0.95

lat_xoffset = 0.06
lat_yoffset = 0.04

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
    print(">>>>>>>> type of mctot", type(i_mctot))
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
    # c2 = ROOT.TCanvas(name, title)
    # c2.SetLeftMargin(0.1)
    # c2.SetRightMargin(0.04)
    # c2.SetLeftMargin(0.1)
    # c2.SetTopMargin(0.04)
    # c2.SetBottomMargin(0.1)
    return c2

def CCQELegend(xlow,ylow,xhigh,yhigh):
    leg = ROOT.TLegend(xlow,ylow,xhigh,yhigh)
    # leg = ROOT.TLegend(abs(xlow-xhigh),abs(ylow-yhigh))
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(legendfontsize)
    return leg


def AddPreliminary():
    font = 112
    color = ROOT.kRed +1
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(legendfontsize*0.9)
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

process=[
    "data",
    "QE",
    "RES",
    "DIS",
    "COH",
    "",
    "",
    "",
    "2p2h",
    "",
    ]
for proc in range(len(process) + 1):
    process.append(process[proc]+"-not")

typeindexorder = [
    # 0,
    1,
    8,
    2,
    3,
    4

]

typescolors = {
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
    19:ROOT.kTeal-6,
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

source_outdirname = os.path.join(outdirname, "source")
if not os.path.exists(source_outdirname):
    print(source_outdirname)
    os.mkdir(source_outdirname)

keys = f.GetListOfKeys()

keys = f.GetListOfKeys()

h_pot = f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(2)
POTScale = dataPOT / mcPOTprescaled
print("POTScale: ",POTScale)

groups = {}
types = {}
scaleX = ["Q2QE"]
scaleY = []#"recoil","EAvail"]


# find all the valid histogram and group by keywords
ncats = 5
for k in keys:
    foundtype = False
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
    if "types" in parse[4] and dotypes:
        foundtype = True
    if "types" in parse[4] and not dotypes:
        continue
    if "simulfit" in parse[4]:
        continue
    if cat not in catstodo: continue
    if "reconstructed" not in parse[4]:
        continue
    if "tuned" in parse[4]:
        sample += "_Tuned"
    if not foundtype:
        print("it's not a type, putting it in groups")

        if sample not in groups.keys():
            groups[sample] = {}
            
        if variable not in groups[sample].keys():
            groups[sample][variable] = {}
        
        if cat not in groups[sample][variable].keys():
            groups[sample][variable][cat] = {}
    
        h = f.Get(name).Clone()
        # h.GetXaxis().SetRangeUser(0.5,1.0)
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
        # h=h.GetCVHistoWithError()
        groups[sample][variable][cat] = h
        continue
    else:
        print("it's a type, not putting it in groups")
        if sample not in types:
            types[sample] = {}
                
        if variable not in types[sample].keys():
            types[sample][variable] = {}
        
        if cat not in types[sample][variable].keys():
            types[sample][variable][cat] = {}
        
        h = f.Get(name).Clone()
        if h.GetEntries() <= 0: 
            print("WARNING: hist ", name, " is empty. Skipping...")
            continue
        
        h.SetFillColor(typescolors[index])
        if cat not in ["data","qelike"]:
            h.SetFillStyle(3244)
            index += 10  # hacky way to get the naming right, see construction of process list

        # h.SetFillColor(catscolors[cat])
        # h.SetLineColor(ROOT.kBlack)
        
        h.Scale(POTScale,"width")
        
        # h.GetXaxis().SetRangeUser(0.5,1.0)

        itype = int(parse[4].split("_")[-1])
        types[sample][variable][cat][itype] = h

    
        


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
        leg = CCQELegend(legx1,legy1,legx2,legy2)
        # leg.SetNColumns(2)

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
                print(">>>>>>here", type(groups[a_sample][b_var][c_cat]), groups[a_sample][b_var][c_cat].Print())
                mctot = groups[a_sample][b_var][c_cat].Clone("mctot")
                firstmc = False
            else:
                mctot.Add(groups[a_sample][b_var][c_cat])
            stack.Add(groups[a_sample][b_var][c_cat])
            # leg.AddEntry(groups[a_sample][b_var][c_cat],catsnames[c_cat],"f")
        for c_cat in mc_order[::-1]:
            leg.AddEntry(groups[a_sample][b_var][c_cat],catsnames[c_cat],"f")
            if c_cat not in groups[a_sample][b_var].keys():
                continue
            if c_cat in ["data","mctot","stack"]:
                continue
        if not noData:
            leg.AddEntry(data,"data","pe") # TODO need to figure out how to order this properly


        # Make the canvas
        thename = "%s_%s"%(a_sample,b_var)
        thetitle = "%s %s"%(a_sample,b_var)
        ysize = _ysize
        xsize = _xsize
        # if doratio and not noData:
        #     ysize = 1.2 * _ysize
        # cc = CCQECanvas(thename, thetitle, xsize, ysize)
        cc = ROOT.TCanvas(thename, thetitle, round(xsize), round(ysize))
        cc.SetLeftMargin(0.15)
        cc.SetRightMargin(0.15)
        cc.SetBottomMargin(0.15)
        cc.SetFrameLineWidth(1)

        # If do ratio, set up the top and bottom pads for the hists
        if doratio and not noData:
            top = TPad("hist", "hist", 0, 0.278, 1, 1)
            top.SetRightMargin(pad_rmarg)
            top.SetLeftMargin(pad_lmarg)
            top.SetTopMargin(topmarg)
            top.SetBottomMargin(0)
            top.SetFrameLineWidth(1)

            bottom = TPad("Ratio", "Ratio", 0, 0, 1, 0.278)
            bottom.SetRightMargin(pad_rmarg)
            bottom.SetLeftMargin(pad_lmarg)
            bottom.SetBottomMargin(bottommarg)
            bottom.SetTopMargin(0)
            bottom.SetFrameLineWidth(1)

            top.Draw()
            bottom.Draw()

            bottomArea = bottom.GetWNDC() * bottom.GetHNDC()
            topArea = top.GetWNDC() * top.GetHNDC()
            areaScale = topArea / bottomArea
            # Move to top pad for hists
            top.cd()
        
        # Do stack first
        stack.Draw()
        # stack.GetXaxis().SetRangeUser(0.5,1.0)
        # stack.Draw()
        # set up its y axis
        stack.GetYaxis().SetTitle("Counts/unit")
        stack.GetYaxis().CenterTitle()
        stack.GetYaxis().SetTitleOffset(0.6)
        stack.GetYaxis().SetTitleSize(0.05)
        stack.GetYaxis().SetLabelSize(0.05)

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

            # make the ratio and make it pretty
            print(">>>>>>>> before type of mctot", type(mctot))
            mctot.SetFillStyle(1001)
            ratio = MnvH1D()
            ratio = MakeDataMCRatio(data, mctot)
            ratio.SetMinimum(0.5)
            ratio.SetMaximum(1.5)

            ratio.SetLineColor(ROOT.kBlack)
            ratio.SetLineWidth(3)

            ratio.SetTitle("")            
            ratio.GetYaxis().SetTitle("Data / MC")
            ratio.GetYaxis().CenterTitle()
            ratio.GetYaxis().SetTitleSize(0.05 * areaScale)
            ratio.GetYaxis().SetTitleOffset(0.6 / areaScale)
            ratio.GetYaxis().SetLabelSize(0.05 * areaScale)
            ratio.GetYaxis().SetNdivisions(205)

            ratio.GetXaxis().SetTitle(x_title)
            ratio.GetXaxis().CenterTitle()
            ratio.GetXaxis().SetTitleSize(0.05 * areaScale)
            ratio.GetXaxis().SetLabelSize(ratio.GetXaxis().GetLabelSize() * areaScale*1.5)

            ratio.Draw()

            # Now do mc uncertainties
            mcerror = TH1D()
            mcerror = TH1D(mctot.GetTotalError(False, True, False))
            for bin in range(1, mcerror.GetXaxis().GetNbins() + 1):
                mcerror.SetBinError(bin, max(mcerror.GetBinContent(bin), 1.0e-9))
                mcerror.SetBinContent(bin, 1.0)
            mcerror.SetLineColor(ROOT.kRed)
            mcerror.SetLineWidth(3)
            mcerror.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
            mcerror.Draw("same E2")

            # Now do a line at 1
            straightline = TH1D()
            straightline = mcerror.Clone()
            straightline.SetFillStyle(0)
            straightline.Draw("hist same")

            ratio.Draw("same")

            # Go back to the top pad 
            top.cd()
        # Dress plot with text
        prelim = AddPreliminary()
        titleonplot = MakeTitleOnPlot()
        # prelim.DrawLatex(latex_x, latex_y, "MINER#nuA Work In Progress")
        prelim.DrawLatex(legx1-lat_xoffset, legy1-2*lat_yoffset-0.01, "MINER#nuA Work In Progress")
        titleonplot.DrawLatex(0.37, 0.9, plottitle)
        # calculate chi2 and do that too
        if not noData:
            plotter = MnvPlotter()
            chi2 = plotter.Chi2DataMC(data,mctot)
            chi2_latex = ROOT.TLatex()
            chi2_latex.SetNDC()
            chi2_latex.SetTextSize(legendfontsize*0.9)
            chi2_latex.SetTextAlign(11)
            chi2_latex.DrawLatex(legx1-lat_xoffset,legy1-lat_yoffset, "#chi^{2} = "+ "{:g}".format(float('{:.{p}g}'.format(chi2, p=5))))
            # chi2_latex.DrawLatex(0.6,0.69, "#chi^{2} = "+str(chi2))
            del plotter
        canvas_name = thename + "_FinalStates"
        if dotuned:
            canvas_name += "_tuned"
        cc.cd()
        cc.Print(os.path.join(outdirname, canvas_name + ".png"))
        cc.Print(os.path.join(source_outdirname, canvas_name + ".C"))

        del cc, stack#, mctot
        if doratio and not noData:
            print("deleting data stuff")
            del top, bottom

        # Now making the types hist
        if not dotypes:
            continue
        # first check if there are types for this sample and var
        if a_sample not in types:
            if doratio and not noData:
                print("deleting data stuff")
                del ratio, straightline, mcerror, mctot
            continue
        if b_var not in types[a_sample]:
            if doratio and not noData:
                print("deleting data stuff")
                del ratio, straightline, mcerror, mctot
            continue
        # Make a qelikenot hist
        if "qelikenot" not in types[a_sample][b_var]:
            types[a_sample][b_var]["qelikenot"] = []
            for i in range(len(types[a_sample][b_var]["qelike"])):
                firstbkg = True
                for c_cat in types[a_sample][b_var]:
                    if c_cat in ["qelike","qelikenot","data"]:
                        continue
                    if firstbkg:
                        newname = types[a_sample][b_var][c_cat][i].GetName().replace(c_cat,"qelikenot")
                        types[a_sample][b_var]["qelikenot"][i] = types[a_sample][b_var][c_cat][i].Clone(newname)
                        firstbkg = False
                        continue
                    types[a_sample][b_var]["qelikenot"][i].Add(types[a_sample][b_var][c_cat][i])
        typesleg = CCQELegend(legx1,legy1,legx2,legy2)

        # For the legend, want to add signal first, then bkg, then data. TODO: make the order of the types QE, 2p2h, RES, DIS, Other/COH
        for c_cat in ["qelike","qelikenot"]:
            # for itype in types[a_sample][b_var][c_cat]:
            for itype in typeindexorder:
                typesleg.AddEntry(types[a_sample][b_var][c_cat][itype], process[itype], "f")
        if not noData:
            typesleg.AddEntry(data, "data", "pe")
        
        # Now make the stack, this will be in reverse order of the legend without any data
        typestack = THStack("typestack", "")
        for c_cat in ["qelikenot","qelike"]:
            # for itype in reversed(types[a_sample][b_var][c_cat].keys()): #janky, only works in 3.7 or newer
            for itype in typeindexorder[::-1]:
                typestack.Add(types[a_sample][b_var][c_cat][itype])
        smax = typestack.GetMaximum()

        if not noData:
            typestack.SetMaximum(1.2 * max(data.GetMaximum(), stack.GetMaximum()))
        else:
            typestack.SetMaximum(1.2 * stack.GetMaximum())

        cc = ROOT.TCanvas(thename, thetitle, round(xsize), round(ysize))
        cc.SetLeftMargin(0.15)
        cc.SetRightMargin(0.15)
        cc.SetBottomMargin(0.15)
        cc.SetFrameLineWidth(1)

        if doratio and not noData:
            top = TPad("hist", "hist", 0, 0.278, 1, 1)
            top.SetRightMargin(pad_rmarg)
            top.SetLeftMargin(pad_lmarg)
            top.SetTopMargin(topmarg)
            top.SetBottomMargin(0)
            top.SetFrameLineWidth(1)

            bottom = TPad("Ratio", "Ratio", 0, 0, 1, 0.278)
            bottom.SetRightMargin(pad_rmarg)
            bottom.SetLeftMargin(pad_lmarg)
            bottom.SetBottomMargin(bottommarg)
            bottom.SetTopMargin(0)
            bottom.SetFrameLineWidth(1)

            top.Draw()
            bottom.Draw()

            bottomArea = bottom.GetWNDC() * bottom.GetHNDC()
            topArea = top.GetWNDC() * top.GetHNDC()
            areaScale = topArea / bottomArea
            # Move to top pad for hists
            top.cd()

        typestack.Draw()

        # set up its y axis
        typestack.GetYaxis().SetTitle("Counts/unit")
        typestack.GetYaxis().CenterTitle()
        typestack.GetYaxis().SetTitleOffset(0.6)
        typestack.GetYaxis().SetTitleSize(0.05)
        typestack.GetYaxis().SetLabelSize(0.05)

        if not doratio or noData:
            typestack.GetXaxis().SetTitle(x_title)
            typestack.GetXaxis().CenterTitle()
            typestack.GetXaxis().SetTitleSize(0.05)
                
        typestack.Draw("hist")
        if not noData:
            data.Draw("PE same")
        leg.Draw()


        if doratio and not noData:
            bottom.cd()

            # make the ratio and make it pretty
            mctot.SetFillStyle(1001)
            ratio = MnvH1D()
            ratio = MakeDataMCRatio(data, mctot)
            ratio.SetMinimum(0.5)
            ratio.SetMaximum(1.5)

            ratio.SetLineColor(ROOT.kBlack)
            ratio.SetLineWidth(3)

            ratio.SetTitle("")            
            ratio.GetYaxis().SetTitle("Data / MC")
            ratio.GetYaxis().CenterTitle()
            ratio.GetYaxis().SetTitleSize(0.05 * areaScale)
            ratio.GetYaxis().SetTitleOffset(0.6 / areaScale)
            ratio.GetYaxis().SetLabelSize(0.05 * areaScale)
            ratio.GetYaxis().SetNdivisions(205)

            ratio.GetXaxis().SetTitle(x_title)
            ratio.GetXaxis().CenterTitle()
            ratio.GetXaxis().SetTitleSize(0.05 * areaScale)
            ratio.GetXaxis().SetLabelSize(ratio.GetXaxis().GetLabelSize() * areaScale*1.5)

            ratio.Draw()

            # Now do mc uncertainties
            mcerror = TH1D()
            mcerror = TH1D(mctot.GetTotalError(False, True, False))
            for bin in range(1, mcerror.GetXaxis().GetNbins() + 1):
                mcerror.SetBinError(bin, max(mcerror.GetBinContent(bin), 1.0e-9))
                mcerror.SetBinContent(bin, 1.0)
            mcerror.SetLineColor(ROOT.kRed)
            mcerror.SetLineWidth(3)
            mcerror.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
            mcerror.Draw("same E2")

            # Now do a line at 1
            straightline = TH1D()
            straightline = mcerror.Clone()
            straightline.SetFillStyle(0)
            straightline.Draw("hist same")

            ratio.Draw("same")

            # Go back to the top pad 
            top.cd()

        # Dress plot with text
        prelim = AddPreliminary()
        titleonplot = MakeTitleOnPlot()
        # prelim.DrawLatex(latex_x, latex_y, "MINER#nuA Work In Progress")
        prelim.DrawLatex(legx1-lat_xoffset, legy1-2*lat_yoffset-0.01, "MINER#nuA Work In Progress")
        titleonplot.DrawLatex(0.37, 0.9, plottitle)
        # calculate chi2 and do that too
        if not noData:
            plotter = MnvPlotter()
            chi2 = plotter.Chi2DataMC(data,mctot)
            chi2_latex = ROOT.TLatex()
            chi2_latex.SetNDC()
            chi2_latex.SetTextSize(legendfontsize*0.9)
            chi2_latex.SetTextAlign(11)
            chi2_latex.DrawLatex(legx1-lat_xoffset,legy1-lat_yoffset, "#chi^{2} = "+ "{:g}".format(float('{:.{p}g}'.format(chi2, p=5))))
            # chi2_latex.DrawLatex(0.6,0.69, "#chi^{2} = "+str(chi2))
            del plotter
        canvas_name = thename + "_Types"
        if dotuned:
            canvas_name += "_tuned"
        cc.cd()
        cc.Print(os.path.join(outdirname, canvas_name + ".png"))
        cc.Print(os.path.join(source_outdirname, canvas_name + ".C"))

        del cc, typestack
        if doratio and not noData:
            print("deleting data stuff")
            del ratio, straightline, mcerror, mctot
