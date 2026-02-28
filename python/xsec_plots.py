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
# import PlotUtils
from PlotUtils import MnvH1D, MnvPlotter, HyperDimLinearizer, GridCanvas
import datetime
import ctypes
import math
import json, re

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

pad_lmarg = 0.10
pad_rmarg = 0.04
topmarg = 0.05
bottommarg = 0.3

legendfontsize = 0.05
legx1 = 0.7
legx2 = 1.0
legy1 = 0.65
legy2 = 0.95

# lat_xoffset = 0.06
lat_xoffset = 0.0
lat_yoffset = 0.04

typeslinewidth = 3

scaleX = ["Q2QE"]
scaleY = ["EAvail","E_{Avail}"]#"recoil","EAvail"]

skipstage_list = [
    # "bkgsub",
    # "unfolded",
    # "effcorr",
    # "sigma"
]

skipvar_list = [
    # "EAvail",
]

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

def GetInputHistDict(f, input_dict = {}):
    keys = f.GetListOfKeys()
    print("Making dict of source hists in file %s..."%(f.GetName()))
    for k in keys:
        name = k.GetName()
        if "___" not in name:
            continue
        parse = name.split("___")
        if len(parse) < 5: continue
        #print (parse)
        # names look like : hist___Sample___category__variable___types_0
        # if not flag in parse[4] and not "data" in parse[2]: continue
        hist = parse[0]
        sample = parse[1]
        cat = parse[2]
        variable = parse[3]
        recotrutype = parse[4]
        if "types" in recotrutype:
            # print("WARNING: types not set up yet")
            continue
        if "simulfit" in recotrutype:
            continue
        if cat not in catstodo: continue
        # if "reconstructed" not in recotrutype:
        #     continue
        # if "tuned" in recotrutype:
        #     sample += "_Tuned"
        #     recotrutype.replace("_tuned","")

        if hist not in input_dict.keys():
            input_dict[hist] = {}
        if sample not in input_dict[hist].keys():
            input_dict[hist][sample] = {}
        if variable not in input_dict[hist][sample].keys():
            input_dict[hist][sample][variable] = {}
        if cat not in input_dict[hist][sample][variable].keys():
            input_dict[hist][sample][variable][cat] = {}
        if recotrutype not in input_dict[hist][sample][variable][cat]:
            input_dict[hist][sample][variable][cat][recotrutype] = {}
        else:
            print("\talready have hist %s, skipping for now..."%(name))
            continue
        h = f.Get(name).Clone()
        if h.GetEntries() <= 0: 
            # print("WARNING: hist ", name, " is empty. Skipping...")
            continue
        h.SetFillColor(catscolors[cat])
        h.SetLineColor(ROOT.kBlack)
        if "data" in cat:
            # h.Scale(1.0, "width")
            # h.Scale(1.0)
            h.SetMarkerStyle(20)
            h.SetMarkerSize(1.5)
        else:
            print("scaling hist ", name)
            # h.Scale(1.0, "width")
            # h.Scale(POTScale, "width")
            h.Scale(POTScale)
        input_dict[hist][sample][variable][cat][recotrutype] = h
    return input_dict

def GetInputTypesHistDict(f, input_dict = {}):
    keys = f.GetListOfKeys()
    print("Making dict of source hists in file %s..."%(f.GetName()))
    for k in keys:
        name = k.GetName()
        if "___" not in name:
            continue
        parse = name.split("___")
        if len(parse) < 5: 
            if len(parse) == 4 and "selected_truth_tuned" in parse[3]:
                newsplit = parse[3].split("__")
                parse[3] = newsplit[0]
                parse.append(newsplit[1])
            else:
                continue
        #print (parse)
        # names look like : hist___Sample___category__variable___types_0
        # if not flag in parse[4] and not "data" in parse[2]: continue
        hist = parse[0]
        sample = parse[1]
        cat = parse[2]
        variable = parse[3]
        recotrutype = parse[4]
        if "types" not in recotrutype:
            # print("WARNING: types not set up yet")
            continue
        if "simulfit" in recotrutype:
            continue
        if cat not in catstodo: continue
        # if "reconstructed" not in recotrutype:
        #     continue

        h = f.Get(name).Clone()
        if h.GetEntries() <= 0: 
            # print("WARNING: hist ", name, " is empty. Skipping...")
            continue
        # if "tuned" in recotrutype:
        #     sample += "_Tuned"
        #     recotrutype.replace("_tuned","")
        
        inttype = int(recotrutype.split("_")[-1])
        recotrutype = recotrutype.replace("_types_%s"%(parse[4].split("_")[-1]), "")
        if hist not in input_dict.keys():
            input_dict[hist] = {}
        if sample not in input_dict[hist].keys():
            input_dict[hist][sample] = {}
        if variable not in input_dict[hist][sample].keys():
            input_dict[hist][sample][variable] = {}
        if cat not in input_dict[hist][sample][variable].keys():
            input_dict[hist][sample][variable][cat] = {}
        if recotrutype not in input_dict[hist][sample][variable][cat]:
            input_dict[hist][sample][variable][cat][recotrutype] = {}
        if inttype not in input_dict[hist][sample][variable][cat][recotrutype]:
            input_dict[hist][sample][variable][cat][recotrutype][inttype] = {}
        else:
            print("\talready have hist %s, skipping for now..."%(name))
            continue
        # h.SetFillColor(catscolors[cat])
        h.SetLineColor(typescolors[inttype])
        # h.Scale(POTScale, "width")
        h.Scale(POTScale)
        input_dict[hist][sample][variable][cat][recotrutype][inttype] = h

    return input_dict
 

def GetAnalyzeHistDict(f, tuned=False, analyze_dict = {}):
    keys = f.GetListOfKeys()
    for k in keys:
        name = k.GetName()
        if "___" in name:
            continue
        if "_" not in name or name in ["flux_dewidthed", "POT_summary", "Combined_POT_summary"]:
            continue

        parse = name.split("_")
        hist = parse[0]
        sample = parse[1]
        var = parse[2]
        shift = 0

        if "types" in parse:
            continue
        print("found key", name)

        if hist=="h2D":
            var+="_"+parse[3]
            shift = 1
        
        # Now to find the stage of analyze
        stage = ""
        for i in range(3 + shift,len(parse)):
            if parse[i] == "unfold":
                stage += "unfolded"
            else:
                stage += parse[i]
            if i == len(parse)-1:
                continue
            stage+= "_"
        if tuned:
            stage += "_tuned"

        if hist not in analyze_dict.keys():
            analyze_dict[hist] = {}
        if sample not in analyze_dict[hist].keys():
            analyze_dict[hist][sample] = {}
        if var not in analyze_dict[hist][sample].keys():
            analyze_dict[hist][sample][var] = {}
        if stage not in analyze_dict[hist][sample][var].keys():
            analyze_dict[hist][sample][var][stage] = {}
        elif not tuned:
            print("\talready have hist %s, skipping for now..."%(name))
            continue

        h = f.Get(name).Clone()
        if h.GetEntries() <= 0: 
            # print("WARNING: hist ", name, " is empty. Skipping...")
            continue
        # TODO width normalize?
        # h.Scale(1.0, "width")
        analyze_dict[hist][sample][var][stage] = h
    return analyze_dict

def GetAnalyzeTypesHistDict(f, tuned = False, analyze_dict = {}):
    keys = f.GetListOfKeys()
    for k in keys:
        name = k.GetName()
        if "___" in name:
            continue
        if "_" not in name or name in ["flux_dewidthed", "POT_summary", "Combined_POT_summary"]:
            continue
        parse = name.split("_")
        hist = parse[0]
        sample = parse[1]
        var = parse[2]
        shift = 0
        if "types" not in parse:
            continue
        print("found key", name)
        inttype = int(parse[-1])
        if hist=="h2D":
            var+="_"+parse[3]
            shift = 1
        
        # Now to find the stage of analyze. Since this is a type hist, end before you get to the "types_<inttype>" part.
        stage = ""
        for i in range(3 + shift,len(parse) - 2):
            if parse[i] == "unfold":
                stage += "unfolded"
            else:
                stage += parse[i]
            if i == len(parse) - 3:
                continue
            stage+= "_"
        if tuned:
            stage += "_tuned"
        
        # Do this before so we only pick up the type hists we're interested in
        h = f.Get(name).Clone()

        if h.GetEntries() <= 0: 
            # print("WARNING: hist ", name, " is empty. Skipping...")
            continue

        if hist not in analyze_dict.keys():
            analyze_dict[hist] = {}
        if sample not in analyze_dict[hist].keys():
            analyze_dict[hist][sample] = {}
        if var not in analyze_dict[hist][sample].keys():
            analyze_dict[hist][sample][var] = {}
        if stage not in analyze_dict[hist][sample][var].keys():
            analyze_dict[hist][sample][var][stage] = {}        
        if stage not in analyze_dict[hist][sample][var].keys():
            analyze_dict[hist][sample][var][stage] = {}        
        if inttype not in analyze_dict[hist][sample][var][stage].keys():
            analyze_dict[hist][sample][var][stage][inttype] = {}
        elif not tuned:
            print("\talready have hist %s, skipping for now..."%(name))
            continue
        h.SetLineColor(typescolors[inttype])
        # TODO width normalize?
        # h.Scale(1.0, "width")
        analyze_dict[hist][sample][var][stage][inttype] = h

    return analyze_dict 


def MakeDataMCRatio(i_data, i_mctot):
    mcratio = i_data.Clone(str(i_data.GetName().replace("data", "datamcratio")))
    mcratio.Divide(i_data, i_mctot)
    return mcratio

def MakeTypesMCRatioDict(i_typesdict, i_mctot):
    i_mctot.Print()
    typesratiodict = {}

    first = True
    tmp_typestot = MnvH1D()
    # Loop over types hists
    for key in i_typesdict.keys():
        # Make ratio to total mc
        tmp_hist = i_typesdict[key].Clone(str(i_typesdict[key].GetName()+"_ratiotomctot"))
        tmp_hist.Divide(tmp_hist, i_mctot)
        typesratiodict[key] = tmp_hist

        # Add original to get an mctot
        if first:
            tmp_typestot = i_typesdict[key].Clone("typestot")
            first = False
            continue
        tmp_typestot.Add(i_typesdict[key])
    
    # Check if types mctot is similar to the 
    if tmp_typestot.GetMaximumBin() != i_mctot.GetMaximumBin():
        print("ERROR: types hist total is different than mctot...", i_mctot.GetName())
        sys.exit(1)
    
    return typesratiodict

# def GetChi2NDF(i_data, i_mctot):
#     chi2 = -9999.
#     if i_data.GetNbinsX() != i_mctot.GetNbinsX(): return chi2
#     nbins = i_data.GetNbinsX()
#     for i in range(1,nbins+1):
#         datacont = i_data.GetBinContent(i)
#         mccont = i_mctot.GetBinContnent(i)
#         if data

def DrawDataMCPlot1D(i_data_hist, i_mc_hist, x_title, y_title, outdirname, canvas_name, canvas_title):
    mnvPlotter = SetupErrorSummary(MnvPlotter(8))

    # thename = "%s_%s_%s"%(b_sample,c_var,"sigma")
    # thetitle = "%s %s %s"%(b_sample,c_var,"sigma")
    thename = canvas_name
    thetitle = canvas_title
    ysize = _ysize
    xsize = _xsize
    cc = ROOT.TCanvas(thename, thetitle, round(xsize), round(ysize))
    cc.SetLeftMargin(0.25)
    cc.SetRightMargin(0.15)
    cc.SetBottomMargin(0.15)
    cc.SetFrameLineWidth(1)

    mnv_data = i_data_hist.Clone()
    mnv_mc = i_mc_hist.Clone()
    
    mnv_data.Scale(1.0, "width")
    mnv_mc.Scale(1.0, "width")

    mnv_data.Print()

    mnv_data.SetMarkerStyle(20)
    mnv_data.SetMarkerColor(ROOT.kBlack)
    mnv_data.SetLineWidth(2)
    mnv_data.SetLineColor(ROOT.kBlack)
    mnv_data.SetLineStyle(1)
    mnv_data.SetMarkerSize(1.5)

    data_hist = mnv_data.GetCVHistoWithError(True,False)
    data_stat = mnv_data.GetCVHistoWithStatError()

    data_hist.GetYaxis().SetTitle(y_title)
    data_hist.GetYaxis().CenterTitle()
    data_hist.GetYaxis().SetTitleOffset(0.9)
    data_hist.GetYaxis().SetTitleSize(0.05)
    data_hist.GetYaxis().SetLabelSize(0.05)

    data_hist.SetMaximum(1.2* max(mnv_data.GetMaximum(),mnv_mc.GetMaximum()))

    mc_band = mnv_mc.GetCVHistoWithError(True,False)
    mc_band.SetFillColor(ROOT.kRed-10)
    mc_band.SetFillStyle(1001)
    mc_band.SetLineColor(ROOT.kRed)
    mc_band.SetMarkerStyle(0)

    mc_hist = mnv_mc.GetCVHistoWithError(True,False)
    mc_hist.SetFillColor(0)
    mc_hist.SetLineColor(2)
    mc_hist.SetLineStyle(1)
    mc_hist.SetLineWidth(3)

    # if doratio:
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
    if c_var in scaleY:
        top.SetLogy()
    if "E_{Avail}" in x_title:
        top.SetLogy()
    
    leg_pos = "TR"

    data_hist.Draw("E1 X0")
    
    # if not issmooth:
    mc_band.Draw("SAME E2")
    mc_hist.Draw("SAME HIST")

    data_stat.Draw("SAME E1 X0")
    data_hist.Draw("Same E1 X0")

    titlewidth = mnvPlotter.GetLegendWidthInLetters(["Data","Simulation"])
    # titlewidth = mnvPlotter.GetLegendWidthInLetters(["Data","MnvTunev4.3.1","COH","RES","DIS","2p2h","QE"])
    # print(titlewidth)
    x1 = ctypes.c_double(0)
    y1 = ctypes.c_double(0)
    x2 = ctypes.c_double(0)
    y2 = ctypes.c_double(0)
    mnvPlotter.DecodeLegendPosition(x1,y1,x2,y2, leg_pos, 2, titlewidth, legendfontsize)

    leg = TLegend(x1,y1,x2,y2)
    leg.SetNColumns(1)
    leg.SetBorderSize(0)
    leg.SetFillColor(-1)
    leg.SetTextSize(legendfontsize)

    leg.AddEntry(data_hist, "Data","p")
    leg.AddEntry(mc_band, "Simulation","fl")

    leg.Draw()
    
    # if doratio:
    bottom.cd()

    # ratio = MnvH1D()
    ratio = MakeDataMCRatio(data_hist,mc_band)
    ratio.SetFillStyle(1001)
    # ratio.SetMinimum(0.5)
    # ratio.SetMaximum(1.5)
    ratio.SetMinimum(0.0)
    ratio.SetMaximum(2.0)

    ratio.SetLineColor(ROOT.kBlack)

    ratio.SetTitle("")            
    ratio.GetYaxis().SetTitle("Data / MC")
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetTitleSize(0.05 * areaScale)
    ratio.GetYaxis().SetTitleOffset(0.9 / areaScale)
    ratio.GetYaxis().SetLabelSize(0.05 * areaScale)
    ratio.GetYaxis().SetNdivisions(205)

    # ratio.GetXaxis().SetTitle(vars_info[c_var]["title"])
    ratio.GetXaxis().SetTitle(x_title)
    ratio.GetXaxis().CenterTitle()
    ratio.GetXaxis().SetTitleSize(0.05 * areaScale)
    ratio.GetXaxis().SetLabelSize(ratio.GetXaxis().GetLabelSize() * areaScale*1.5)
    ratio.SetLineWidth(round(2 / areaScale))
    ratio.Draw("E1 X0")

    # Now do mc uncertainties
    mcerror = TH1D()
    mnv_mc.SetFillStyle(1001)
    mcerror = TH1D(mnv_mc.GetTotalError(False, True, False))
    for bin in range(0, mcerror.GetXaxis().GetNbins() + 2):
        mcerror.SetBinError(bin, max(mcerror.GetBinContent(bin), 1.0e-9))
        mcerror.SetBinContent(bin, 1.0)
    mcerror.SetLineColor(ROOT.kRed)
    mcerror.SetLineWidth(3)
    # mcerror.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
    mcerror.SetFillColor(ROOT.kRed-10)
    mcerror.Draw("same E2")

    # Now do a line at 1
    straightline = TH1D()
    straightline = mcerror.Clone()
    straightline.SetFillStyle(0)
    straightline.Draw("hist same")

    ratio.Draw("same")
    top.cd()
    prelim = AddPreliminary()
    # titleonplot = MakeTitleOnPlot()
    prelim.DrawLatex(x1.value-lat_xoffset, y1.value-2*lat_yoffset-0.01, "MINER#nuA Work In Progress")
    # titleonplot.DrawLatex(0.37, 0.9, plottitle)

    canvas_name = thename + "_FinalStates"

    if dotypes:
        canvas_name = thename + "Types"
    if dotuned:
        canvas_name += "_tuned" 


    cc.Print(os.path.join(outdirname, canvas_name + ".png"))
    cc.Print(os.path.join(outdirname, "source", canvas_name + ".C"))

    cc.cd()
    cc.Clear()
    cc.Modified()
    cc.Update()
    del cc

def DrawDataMCTypesPlot1D(i_data_hist, i_mctot_hist, i_mc_typeshistdict, x_title, y_title, outdirname, canvas_name, canvas_title):
    mnvPlotter = SetupErrorSummary(MnvPlotter(8))

    # thename = "%s_%s_%s"%(b_sample,c_var,"sigma")
    # thetitle = "%s %s %s"%(b_sample,c_var,"sigma")
    thename = canvas_name
    thetitle = canvas_title
    ysize = _ysize
    xsize = _xsize
    cc = ROOT.TCanvas(thename, thetitle, round(xsize), round(ysize))
    cc.SetLeftMargin(0.25)
    cc.SetRightMargin(0.15)
    cc.SetBottomMargin(0.15)
    cc.SetFrameLineWidth(1)

    mnv_data = i_data_hist.Clone()
    mnv_mc = i_mctot_hist.Clone()
    
    mnv_data.Scale(1.0, "width")
    mnv_mc.Scale(1.0, "width")

    typehistdict = {}
    for key in i_mc_typeshistdict:
        hist = i_mc_typeshistdict[key].GetCVHistoWithStatError()
        hist.Scale(1.0, "width")
        hist.SetLineWidth(6)
        typehistdict[typesnames[key]] = hist

    mnv_data.Print()

    mnv_data.SetMarkerStyle(20)
    mnv_data.SetMarkerColor(ROOT.kBlack)
    mnv_data.SetLineWidth(2)
    mnv_data.SetLineColor(ROOT.kBlack)
    mnv_data.SetLineStyle(1)
    mnv_data.SetMarkerSize(1.5)

    data_hist = mnv_data.GetCVHistoWithError(True,False)
    data_stat = mnv_data.GetCVHistoWithStatError()

    data_hist.GetYaxis().SetTitle(y_title)
    data_hist.GetYaxis().CenterTitle()
    data_hist.GetYaxis().SetTitleOffset(0.9)
    data_hist.GetYaxis().SetTitleSize(0.05)
    data_hist.GetYaxis().SetLabelSize(0.05)

    data_hist.SetMaximum(1.2* max(mnv_data.GetMaximum(),mnv_mc.GetMaximum()))

    # mc_band = mnv_mc.GetCVHistoWithError(True,False)
    # mc_band.SetFillColor(ROOT.kRed-10)
    # mc_band.SetFillStyle(1001)
    # mc_band.SetLineColor(ROOT.kRed)
    # mc_band.SetMarkerStyle(0)

    mc_hist = mnv_mc.GetCVHistoWithError(True,False)
    mc_hist.SetFillColor(0)
    # mc_hist.SetLineColor(2)
    mc_hist.SetLineColor(typescolors[0])
    mc_hist.SetLineStyle(1)
    # mc_hist.SetLineWidth(3)
    mc_hist.SetLineWidth(6)

    # if doratio:
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
    if c_var in scaleY:
        top.SetLogy()
    leg_pos = "TR"

    data_hist.Draw("E1 X0")
    
    # if not issmooth:
    # mc_band.Draw("SAME E2")
    typeskeys = typehistdict.keys()
    if "COH" in typeskeys:
        typehistdict["COH"].Draw("HIST SAME")
    if "DIS" in typeskeys:
        typehistdict["DIS"].Draw("HIST SAME")
    if "RES" in typeskeys:
        typehistdict["RES"].Draw("HIST SAME")
    if "2p2h" in typeskeys:
        typehistdict["2p2h"].Draw("HIST SAME")
    if "QE" in typeskeys:
        typehistdict["QE"].Draw("HIST SAME")
    # mc_hist.Draw("SAME HIST X0")
    mc_hist.Draw("HIST SAME")

    data_stat.Draw("SAME E1 X0")
    data_hist.Draw("Same E1 X0")

    titlewidth = mnvPlotter.GetLegendWidthInLetters(["Data","MnvTunev431","COH","RES","DIS","2p2h","QE"])
    # print(titlewidth)
    x1 = ctypes.c_double(0)
    y1 = ctypes.c_double(0)
    x2 = ctypes.c_double(0)
    y2 = ctypes.c_double(0)
    mnvPlotter.DecodeLegendPosition(x1,y1,x2,y2, leg_pos, 2+len(typehistdict.keys()), titlewidth, legendfontsize)

    leg = TLegend(x1,y1,x2,y2)
    leg.SetTextSize(legendfontsize)
    leg.SetNColumns(1)
    leg.SetBorderSize(0)
    leg.SetFillColor(-1)
    leg.AddEntry(mc_hist, "MnvTune4.3.1","fl")
    if "QE" in typeskeys:
        leg.AddEntry(typehistdict["QE"], "QE","fl")
    if "2p2h" in typeskeys:
        leg.AddEntry(typehistdict["2p2h"], "2p2h","fl")
    if "RES" in typeskeys:
        leg.AddEntry(typehistdict["RES"], "RES","fl")
    if "DIS" in typeskeys:
        leg.AddEntry(typehistdict["DIS"], "DIS","fl")
    if "COH" in typeskeys:
        leg.AddEntry(typehistdict["COH"], "COH","fl")
    leg.AddEntry(data_hist, "Data","p")

    leg.Draw()
    
    # if doratio:
    bottom.cd()

    # ratio = MnvH1D()
    # ratio = MakeDataMCRatio(data_hist,mc_band)
    ratio = MakeDataMCRatio(data_hist, mc_hist)
    typesratiodict= MakeTypesMCRatioDict(typehistdict, mc_hist)

    ratio.SetFillStyle(1001)
    ratio.SetMinimum(0.0)
    ratio.SetMaximum(2.0)

    ratio.SetLineColor(ROOT.kBlack)

    ratio.SetTitle("")            
    ratio.GetYaxis().SetTitle("Data / MC")
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetTitleSize(0.05 * areaScale)
    ratio.GetYaxis().SetTitleOffset(0.9 / areaScale)
    ratio.GetYaxis().SetLabelSize(0.05 * areaScale)
    ratio.GetYaxis().SetNdivisions(205)

    # ratio.GetXaxis().SetTitle(vars_info[c_var]["title"])
    ratio.GetXaxis().SetTitle(x_title)
    ratio.GetXaxis().CenterTitle()
    ratio.GetXaxis().SetTitleSize(0.05 * areaScale)
    ratio.GetXaxis().SetLabelSize(ratio.GetXaxis().GetLabelSize() * areaScale*1.5)
    ratio.SetLineWidth(round(2 / areaScale))
    ratio.Draw("E1 X0")

    # Now do mc uncertainties
    mcerror = TH1D()
    mnv_mc.SetFillStyle(1001)
    mcerror = TH1D(mnv_mc.GetTotalError(False, True, False))
    for bin in range(0, mcerror.GetXaxis().GetNbins() + 2):
        mcerror.SetBinError(bin, max(mcerror.GetBinContent(bin), 1.0e-9))
        mcerror.SetBinContent(bin, 1.0)
    mcerror.SetLineColor(ROOT.kRed)
    mcerror.SetLineWidth(round(typeslinewidth*2))
    # mcerror.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
    mcerror.SetFillColor(ROOT.kRed-10)
    mcerror.Draw("same E2")

    # Now do a line at 1
    straightline = TH1D()
    straightline = mcerror.Clone()
    straightline.SetFillStyle(0)
    straightline.Draw("hist same")

    for key in typesratiodict:
        typesratiodict[key].SetLineWidth(round(typeslinewidth*2))
        typesratiodict[key].Draw("HIST SAME")

    ratio.Draw("same")
    top.cd()
    prelim = AddPreliminary()
    # titleonplot = MakeTitleOnPlot()
    prelim.DrawLatex(x1.value-lat_xoffset, y1.value-2*lat_yoffset-0.01, "MINER#nuA Work In Progress")
    # titleonplot.DrawLatex(0.37, 0.9, plottitle)

    canvas_name = thename + "_Types"

    # if dotuned:
    #     canvas_name += "_tuned" 


    cc.Print(os.path.join(outdirname, canvas_name + ".png"))
    cc.Print(os.path.join(outdirname, "source", canvas_name + ".C"))

    cc.cd()
    cc.Clear()
    cc.Modified()
    cc.Update()
    del cc

def SetupErrorSummary(mnvPlotter):
    mnvPlotter.axis_minimum = 0.0
    mnvPlotter.axis_maximum = 0.6
    mnvPlotter.error_color_map["Flux"] = ROOT.kViolet + 6
    mnvPlotter.error_color_map["Recoil Reconstruction"] = ROOT.kOrange + 2
    mnvPlotter.error_color_map["Cross Section Models"] = ROOT.kMagenta
    mnvPlotter.error_color_map["FSI Model"] = ROOT.kRed
    mnvPlotter.error_color_map["Muon Reconstruction"] = ROOT.kGreen
    mnvPlotter.error_color_map["Muon Energy"] = ROOT.kGreen + 3
    mnvPlotter.error_color_map["Muon_Energy_MINERvA"] = ROOT.kRed - 3
    mnvPlotter.error_color_map["Muon_Energy_MINOS"] = ROOT.kViolet - 3
    mnvPlotter.error_color_map["Other"] = ROOT.kGreen + 3
    mnvPlotter.error_color_map["Low Recoil Fits"] = ROOT.kRed + 3
    mnvPlotter.error_color_map["GEANT4"] = ROOT.kBlue
    mnvPlotter.error_color_map["Background Subtraction"] = ROOT.kGreen
    mnvPlotter.error_color_map["Tune"] = ROOT.kOrange + 2

    mnvPlotter.error_summary_group_map.clear()
    FSI_Model_list = [
        "GENIE_FrAbs_N",
        "GENIE_FrAbs_pi",
        "GENIE_FrCEx_N",
        "GENIE_FrCEx_pi",
        "GENIE_FrElas_N",
        "GENIE_FrElas_pi",
        "GENIE_FrInel_N",
        "GENIE_FrInel_pi",
        "GENIE_FrPiProd_N",
        "GENIE_FrPiProd_pi",
        "GENIE_MFP_N",
        "GENIE_MFP_pi",
    ]
    mnvPlotter.error_summary_group_map["FSI Model"] = FSI_Model_list

    Genie_Interaction_Model_list = [
        "GENIE_AGKYxF1pi",
        "GENIE_AhtBY",
        "GENIE_BhtBY",
        "GENIE_CCQEPauliSupViaKF",
        "GENIE_CV1uBY",
        "GENIE_CV2uBY",
        "GENIE_EtaNCEL",
        "GENIE_MaCCQE",
        "GENIE_MaCCQEshape",
        "GENIE_MaNCEL",
        "GENIE_MaRES",
        "GENIE_MvRES",
        "GENIE_NormCCQE",
        "GENIE_NormCCRES",
        "GENIE_NormDISCC",
        "GENIE_NormNCRES",
        "GENIE_RDecBR1gamma",
        "GENIE_Rvn1pi",
        "GENIE_Rvn2pi",
        "GENIE_Rvn3pi",
        "GENIE_Rvp1pi",
        "GENIE_Rvp2pi",
        "GENIE_Theta_Delta2Npi",
        "GENIE_VecFFCCQEshape",
    ]
    mnvPlotter.error_summary_group_map["Genie Interaction Model"] = Genie_Interaction_Model_list

    Tune_list = [
        "RPA_LowQ2",
        "RPA_HighQ2",
        "NonResPi",
        "2p2h",
        "LowQ2Pi",
        "Low_Recoil_2p2h_Tune",
    ]
    mnvPlotter.error_summary_group_map["Tune"] = Tune_list

    Response_list = [    
        "response_em",
        "response_proton",
        "response_pion",
        "response_meson",
        "response_other",
        "response_low_neutron",
        "response_mid_neutron",
        "response_high_neutron",
    ]
    mnvPlotter.error_summary_group_map["Response"] = Response_list

    Geant_list = [
        "GEANT_Neutron",
        "GEANT_Proton",
        "GEANT_Pion",
    ]
    mnvPlotter.error_summary_group_map["Geant"] = Geant_list

    Muon_list = [
        "Muon_Energy_MINOS",
        "Muon_Energy_MINERvA",
        "MINOS_Reconstruction_Efficiency",
        "Muon_Energy_Resolution",
        "BeamAngleX",
        "BeamAngleY",
    ]
    mnvPlotter.error_summary_group_map["Muon"] = Muon_list


    return mnvPlotter

def DrawErrorSummary1D(i_hist, x_title, outdirname, canvas_name, canvas_title):
    mnvPlotter = SetupErrorSummary(MnvPlotter(8))
    # thename = "%s_%s_%s"%(b_sample,c_var,"sigma")
    # thetitle = "%s %s %s"%(b_sample,c_var,"sigma")
    thename = canvas_name + "_ErrorSummary"
    thetitle = canvas_title + " ErrorSummary"
    ysize = _ysize
    xsize = _xsize
    cc = ROOT.TCanvas(thename, thetitle, round(xsize), round(ysize))
    cc.SetLeftMargin(0.15)
    cc.SetRightMargin(0.15)
    cc.SetBottomMargin(0.15)
    cc.SetFrameLineWidth(1)
    mnv_hist = i_hist.Clone()
    mnv_hist.Scale(1.0, "Scale")
    mnv_hist.SetXTitle("%s (%s)"%(var_title,var_units))

    include_stat_error = True
    solid_lines_only = False
    ignore_Threshold = 0.0
    do_cov_area_norm = False
    error_group_name = ""
    do_fractional_uncertainty = True
    mnvPlotter.DrawErrorSummary(mnv_hist, "TL", include_stat_error, solid_lines_only, ignore_Threshold, do_cov_area_norm, error_group_name, do_fractional_uncertainty)

    canvas_name = thename + "_FinalStates"
    # if dotypes:
    #     canvas_name = thename + "Types"
    # if dotuned:
    #     canvas_name += "_tuned" 

    cc.Print(os.path.join(outdirname, canvas_name + ".png"))
    cc.Print(os.path.join(outdirname, "source", canvas_name + ".C"))

def PanelCanvas(name, n_xbins, n_ybins, x_size=1000, y_size=750):
    """name is the name for the canvas
    title is the title for the canvas
    n_xbins and n_ybins are number of x and y bins of each 2D hist
    x_size and y_size is the dimensions of the canvas
    returns a grid canvas with the correct number of pads"""

    # TODO: These might need the n_xbins swapped for n_ybins (currently set up basically how it is in Dan's), maybe just hard code these for now?
    grid_x = int(math.sqrt(n_ybins)+1)
    grid_y = int(n_ybins/(grid_x-1))

    if grid_x*grid_y-n_ybins==grid_x:
        grid_y-=1
    
    print("PanelCanvas: Making a grid canvas named "+name+" with a grid of ",n_xbins,"    ",n_ybins,"    ",grid_x,"    ",grid_y)

    # gc2 = PlotUtils.GridCanvas(name, grid_x, grid_y, x_size, y_size)
    gc2 = GridCanvas(name, grid_x, grid_y, x_size, y_size)
    # gc2.SetRightMargin(0.01)
    # gc2.SetLeftMargin(0.1)
    gc2.ResetPads()

    return gc2

def MakeProjHistList(i_hist, projaxis="x"):
    ret_list = []
    hist = i_hist.Clone()
    n_projbins = 0
    if projaxis=="x":
        n_projbins = hist.GetNbinsY()
        proj_nametail = "_projybin"
    elif projaxis == "y":
        n_projbins = hist.GetNbinsX()
        proj_nametail = "_projxbin"
    else:
        print("ERROR: invalid projaxis %s, exiting"%(projaxis))
        sys.exit(1)

    for i in range(n_projbins):
        tmp_proj_name = hist.GetName() + proj_nametail + str(i)
        if projaxis == "x":
            tmp_proj = hist.ProjectionX(tmp_proj_name,i+1,i+1)#, "width")
            ret_list.append(tmp_proj)
            continue
        else: # if projaxis == "y"
            tmp_proj = hist.ProjectionY(tmp_proj_name,i+1,i+1)#, "width")
            ret_list.append(tmp_proj)
            continue
    return ret_list    

def GetDataHistsForPlot(mnv_datahist):
    mnvh = mnv_datahist.Clone()

    mnvh.SetMarkerStyle(20)
    mnvh.SetMarkerColor(ROOT.kBlack)
    mnvh.SetLineWidth(2)
    mnvh.SetLineColor(ROOT.kBlack)
    mnvh.SetLineStyle(1)
    mnvh.SetMarkerSize(1.5)

    hist = mnvh.GetCVHistoWithError(True,False)
    stat = mnvh.GetCVHistoWithStatError()

    return hist, stat

def GetMCHistsForPlot(mnv_mchist):
    mnvh = mnv_mchist.Clone()

    band = mnvh.GetCVHistoWithError(True,False)
    band.SetFillColor(ROOT.kRed - 10)
    band.SetFillStyle(1001)
    band.SetLineColor(ROOT.kRed)
    band.SetMarkerStyle(0)

    hist = mnvh.GetCVHistoWithError(True,False)
    hist.SetFillColor(0)
    # hist.SetLineColor(2)
    hist.SetLineColor(typescolors[0])
    hist.SetLineStyle(1)
    hist.SetLineWidth(3)

    return hist, band
    
def DrawDataMCPlot2D(i_data_hist, i_mc_hist, x_title, x_bins, y_title, y_bins, z_title, outdirname, canvas_name, canvas_title, do_ratio = False):
    mnvPlotter = SetupErrorSummary(MnvPlotter(8))

    data_mnv2d = i_data_hist.Clone()
    mc_mnv2d = i_mc_hist.Clone()
    data_mnv2d_unscaled = i_data_hist.Clone()
    mc_mnv2d_unscaled = i_mc_hist.Clone()

    data_mnv2d.Scale(1.0, "width")
    mc_mnv2d.Scale(1.0, "width")

    n_xbins = data_mnv2d.GetNbinsX()
    n_ybins = data_mnv2d.GetNbinsY()
    print("hist n x bins: ",n_xbins,",\t hist n y bins: ",n_ybins)

    for projaxis in ["x","y"]:
        # Panel projections by each bin
        data_mnvproj_list = MakeProjHistList(data_mnv2d,projaxis)
        mc_mnvproj_list = MakeProjHistList(mc_mnv2d,projaxis)

        # total projection to 1D
        data_mnvprojtot = MnvH1D()
        mc_mnvprojtot = MnvH1D()
        if projaxis == "x":
            data_mnvprojtot = data_mnv2d_unscaled.ProjectionX("%s_proj%s"%(data_mnv2d_unscaled.GetName(),projaxis), 0, data_mnv2d_unscaled.GetNbinsY()+2, "width e")
            mc_mnvprojtot = mc_mnv2d_unscaled.ProjectionX("%s_proj%s"%(mc_mnv2d_unscaled.GetName(),projaxis), 0, mc_mnv2d_unscaled.GetNbinsY()+2, "width e")
        if projaxis == "y":
            data_mnvprojtot = data_mnv2d_unscaled.ProjectionY("%s_proj%s"%(data_mnv2d_unscaled.GetName(),projaxis), 0, data_mnv2d_unscaled.GetNbinsX()+2, "width e")
            mc_mnvprojtot = mc_mnv2d_unscaled.ProjectionY("%s_proj%s"%(mc_mnv2d_unscaled.GetName(),projaxis), 0, mc_mnv2d_unscaled.GetNbinsX()+2, "width e")

        # thename = "%s_%s_%s_proj%s"%(b_sample,c_var,"sigma",projaxis)
        # thetitle = "%s %s %s proj%s"%(b_sample,c_var,"sigma",projaxis)
        thename = "%s_proj%s"%(canvas_name,projaxis)
        thetitle = "%s proj%s"%(canvas_title,projaxis)

        ysize = _ysize
        xsize = _xsize
        canvas_nxbins = n_xbins
        canvas_nybins = n_ybins
        # these are the bin edges for each panel, printed on each panel
        plot_bins = y_bins

        proj_xtitle = x_title
        proj_ytitle = y_title
        if projaxis == "y":
            canvas_nxbins = n_ybins
            canvas_nybins = n_xbins
            plot_bins = x_bins 
            proj_xtitle = y_title
            proj_ytitle = x_title

        # First do the total projections
        DrawDataMCPlot1D(data_mnvprojtot, mc_mnvprojtot, proj_xtitle, z_title, outdirname, thename+"_totalproj", canvas_title+" total proj")

        print("plot bins:", plot_bins)
        print("canvas n x bins: ",canvas_nxbins,",\t canvas n y bins: ",canvas_nybins)

        gc = PanelCanvas(thename, canvas_nxbins, canvas_nybins, round(xsize), round(ysize))
        gc.SetLeftMargin(0.1)
        gc.SetRightMargin(0.05)
        gc.SetBottomMargin(0.1)
        # gc.SetFrameLineWidth(1)
        gc.SetXTitle(proj_xtitle)
        gc.SetYTitle(z_title)
        gc.Draw()
        n_pads = len(data_mnvproj_list)
        print(n_pads)
        data_hist_list = []
        data_stat_list = []

        mc_hist_list = []
        mc_band_list = []

        for hist in data_mnvproj_list:
            data_hist, data_stat = GetDataHistsForPlot(hist)
            data_hist_list.append(data_hist)
            data_stat_list.append(data_stat)
        for hist in mc_mnvproj_list:
            mc_hist, mc_band = GetMCHistsForPlot(hist)
            mc_hist_list.append(mc_hist)
            mc_band_list.append(mc_band)
        maxlist = [hist.GetMaximum() for hist in data_hist_list] + [hist.GetMaximum() for hist in mc_hist_list]
        global_max = max(maxlist)

        for i in range(n_pads):
            pad = gc.cd(i+1)
            pad.Draw()
            tmp_pad_max = 0.0
            tmp_pad_scale = 1.0

            tmp_pad_max = max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum())
            if tmp_pad_max == 0:
                tmp_pad_max = 1.0

            tmp_pad_scale = eval('{:.{p}g}'.format(global_max / tmp_pad_max, p=3))

            data_hist_list[i].Scale(tmp_pad_scale)
            data_stat_list[i].Scale(tmp_pad_scale)
            mc_hist_list[i].Scale(tmp_pad_scale)
            mc_band_list[i].Scale(tmp_pad_scale)

            data_hist_list[i].SetMaximum(1.2 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
            data_hist_list[i].SetMinimum(0)
            if proj_xtitle.split(" (")[0] in scaleY:
                pad.SetLogy()
                data_hist_list[i].SetMaximum(1.5 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
                data_hist_list[i].SetMinimum(data_hist_list[i].GetMaximum()/1000)
            
            data_hist_list[i].GetXaxis().SetNdivisions(207)
            data_hist_list[i].GetYaxis().SetNdivisions(205)


            data_hist_list[i].Draw("axis")
            mc_band_list[i].Draw("SAME E2")
            mc_hist_list[i].Draw("SAME HIST")

            data_stat_list[i].Draw("SAME E1 X0")
            data_hist_list[i].Draw("SAME E1 X0")
            data_hist_list[i].Draw("SAME axis")

            range_string = "{loedge} < {var} < {hiedge}".format(loedge = round(plot_bins[i], 3), var =proj_ytitle.split(" (")[0], hiedge = round(plot_bins[i+1], 3))
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.025)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)

            multip_string = "#times {:g}".format(float('{:.{p}g}'.format(tmp_pad_scale, p=2)))
            multip_latex = ROOT.TLatex()
            multip_latex.SetTextAlign(32)
            multip_latex.SetNDC()
            multip_latex.SetTextFont(42)
            multip_latex.SetTextSize(0.028)
            multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.05), multip_string)
            pad.Modified()
        pad = gc.cd(n_pads+1)
        padwidth = 1 - pad.GetLeftMargin() - pad.GetRightMargin()
        # leg = TLegend(pad.GetLeftMargin()+0.5,(1.-(pad.GetTopMargin())-0.05),pad.GetRightMargin()-0.5,(pad.GetBottomMargin()+0.05))
        leg = TLegend(pad.GetLeftMargin()+padwidth/10,(1.-(pad.GetTopMargin())-0.05), 1 - (pad.GetRightMargin() + padwidth/10),(pad.GetBottomMargin()+0.05))
        leg.SetNColumns(1)
        leg.SetBorderSize(0)
        leg.SetFillColor(-1)
        leg.SetTextSize(round(legendfontsize/3))

        leg.AddEntry(data_hist_list[0], "Data","p")
        leg.AddEntry(mc_band_list[0], "Simulation","fl")

        leg.Draw()
        pad.Modified()
        gc.SetHistTexts()
        gc.Draw()
        # canvas_name = thename + "XSec_Proj" + projaxis

        gc.Print(os.path.join(outdirname, thename + ".png"))
        gc.Print(os.path.join(outdirname,"source", thename + ".C"))
        # del gc

        gc.cd()
        gc.ResetPads()
        leg.Clear()
        gc.SetYTitle("%s Data / MC"%(z_title))
        gc.SetXTitle(proj_xtitle)
        gc.Modified()
        gc.Update()

        ratio_list = []
        mcerror_list = []
        straightline_list = []
        for i in range(n_pads):
            ratio = MakeDataMCRatio(data_hist_list[i],mc_band_list[i])
            ratio = MakeDataMCRatio(data_hist_list[i],mc_band_list[i])
            ratio.SetMinimum(0.1)
            ratio.SetMaximum(2)

            ratio.SetFillStyle(1001)
            ratio.SetLineColor(ROOT.kBlack)
            ratio.SetLineWidth(2)
            # ratio.SetTitle("")
            ratio.GetYaxis().SetNdivisions(205)
            ratio_list.append(ratio)

            mcerror = TH1D()
            mc_mnvproj_list[i].SetFillStyle(1001)
            mcerror = TH1D(mc_mnvproj_list[i].GetTotalError(False,True,False))
            for bin in range(0, mcerror.GetXaxis().GetNbins() + 2):
                mcerror.SetBinError(bin,max(mcerror.GetBinContent(bin),1.0E-9))
                mcerror.SetBinContent(bin, 1.0)
            mcerror.SetLineColor(ROOT.kRed)
            mcerror.SetLineWidth(3)
            mcerror.SetFillColor(ROOT.kRed - 10)

            mcerror_list.append(mcerror)

            straightline = TH1D()
            straightline = mcerror.Clone()
            straightline.SetFillStyle(0)
            straightline_list.append(straightline)


        for i in range(n_pads):
            pad = gc.cd(i+1)
            pad.SetLogy(0)
            pad.Draw()
            ratio_list[i].Draw()
            mcerror_list[i].Draw("same E2")
            straightline_list[i].Draw("hist same")
            ratio_list[i].Draw("E1 X0 same")
            ratio_list[i].Draw("axis same")

            range_string = "{loedge} < {var} < {hiedge}".format(loedge = round(plot_bins[i], 3), var =proj_ytitle.split(" (")[0], hiedge = round(plot_bins[i+1], 3))
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.025)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)

        pad = gc.cd(n_pads+1)
        pad.SetLogy(0)
        pad.Draw()
        padwidth = 1 - pad.GetLeftMargin() - pad.GetRightMargin()
        leg = TLegend(pad.GetLeftMargin()+padwidth/10,(1.-(pad.GetTopMargin())-0.05), 1 - (pad.GetRightMargin() + padwidth/10),(pad.GetBottomMargin()+0.05))
        leg.SetNColumns(1)
        leg.SetBorderSize(0)
        leg.SetFillColor(-1)
        leg.SetTextSize(round(legendfontsize/3))

        leg.AddEntry(data_hist_list[0], "Data","p")
        leg.AddEntry(mc_band_list[0], "Simulation","fl")

        leg.Draw()
        pad.Modified()
        gc.SetHistTexts()
        gc.Draw()
        gc.Print(os.path.join(outdirname, thename + "_ratio.png"))
        gc.Print(os.path.join(outdirname,"source", thename + "_ratio.C"))

        gc.cd()
        gc.ResetPads()
        leg.Clear()
        gc.SetYTitle("Fractional Uncertainty")
        gc.SetXTitle(proj_xtitle)
        gc.Modified()
        gc.Update()
        # Now do error summary
        gc.SetXTitle(proj_xtitle)

        mnvPlotter = SetupErrorSummary(MnvPlotter(8))
        include_stat_error = True
        solid_lines_only = False
        ignore_Threshold = 0.0
        do_cov_area_norm = False
        error_group_name = ""
        do_fractional_uncertainty = True

        for i in range(n_pads):
            pad = gc.cd(i+1)
            mnvPlotter.DrawErrorSummary(data_mnvproj_list[i], "N", include_stat_error, solid_lines_only, ignore_Threshold, do_cov_area_norm, error_group_name, do_fractional_uncertainty)
        
        gc.SetHistTexts()
        gc.Draw()
        gc.Print(os.path.join(outdirname, thename + "_ErrorSummary.png"))
        gc.Print(os.path.join(outdirname,"source", thename + "_ErrorSummary.C"))

            
        del gc

def DrawDataMCTypesPlot2D(i_data_hist, i_mc_hist, i_mc_typeshistdict, x_title, x_bins, y_title, y_bins, z_title, outdirname, canvas_name, canvas_title, do_ratio = False):
    mnvPlotter = SetupErrorSummary(MnvPlotter(8))    
    data_mnv2d = i_data_hist.Clone()
    mc_mnv2d = i_mc_hist.Clone()
    data_mnv2d_unscaled = i_data_hist.Clone()
    mc_mnv2d_unscaled = i_mc_hist.Clone()

    mc_typehistdict = {}
    mc_typehistdict_unscaled = {}
    for key in i_mc_typeshistdict:
        tmphist = i_mc_typeshistdict[key].Clone()
        tmphist_unscaled = i_mc_typeshistdict[key].Clone()
        tmphist.Scale(1.0,"width")
        mc_typehistdict[key] = tmphist
        mc_typehistdict_unscaled[key] = tmphist_unscaled
    data_mnv2d.Scale(1.0, "width")
    mc_mnv2d.Scale(1.0, "width")

    n_xbins = data_mnv2d.GetNbinsX()
    n_ybins = data_mnv2d.GetNbinsY()
    print("hist n x bins: ",n_xbins,",\t hist n y bins: ",n_ybins)


    for projaxis in ["x","y"]:
        data_mnvproj_list = MakeProjHistList(data_mnv2d,projaxis)
        mc_mnvproj_list = MakeProjHistList(mc_mnv2d,projaxis)
        
        mc_typesproj_listdict = {}
        # typeskeys = i_mc_typeshistdict.keys()
        # print("******************2D Plotting typeskeys: ", typeskeys)
        for key in mc_typehistdict:
            tmp_list = MakeProjHistList(mc_typehistdict[key],projaxis)
            mc_typesproj_listdict[typesnames[key]] = [hist.GetCVHistoWithStatError() for hist in tmp_list]
        typeskeys = mc_typesproj_listdict.keys()

        # total projection to 1D
        data_mnvprojtot = MnvH1D()
        mc_mnvprojtot = MnvH1D()
        mc_typestotproj_dict = {}
        if projaxis == "x":
            data_mnvprojtot = data_mnv2d_unscaled.ProjectionX("%s_proj%s"%(data_mnv2d_unscaled.GetName(),projaxis), 0, data_mnv2d_unscaled.GetNbinsY()+2)#, "width e")
            mc_mnvprojtot = mc_mnv2d_unscaled.ProjectionX("%s_proj%s"%(mc_mnv2d_unscaled.GetName(),projaxis), 0, mc_mnv2d_unscaled.GetNbinsY()+2)#, "width e")
            for key in mc_typehistdict:
                tmp_totproj = mc_typehistdict_unscaled[key].ProjectionX("%s_proj%s"%(mc_typehistdict_unscaled[key].GetName(),projaxis), 0, mc_typehistdict_unscaled[key].GetNbinsY()+2)#, "width e")
                mc_typestotproj_dict[key] = tmp_totproj
        if projaxis == "y":
            data_mnvprojtot = data_mnv2d_unscaled.ProjectionY("%s_proj%s"%(data_mnv2d_unscaled.GetName(),projaxis), 0, data_mnv2d_unscaled.GetNbinsX()+2)#, "width e")
            mc_mnvprojtot = mc_mnv2d_unscaled.ProjectionY("%s_proj%s"%(mc_mnv2d_unscaled.GetName(),projaxis), 0, mc_mnv2d_unscaled.GetNbinsX()+2)#, "width e")
            for key in mc_typehistdict:
                tmp_totproj = mc_typehistdict_unscaled[key].ProjectionY("%s_proj%s"%(mc_typehistdict_unscaled[key].GetName(),projaxis), 0, mc_typehistdict_unscaled[key].GetNbinsY()+2)#, "width e")
                mc_typestotproj_dict[key] = tmp_totproj

        # thename = "%s_%s_%s_proj%s"%(b_sample,c_var,"sigma",projaxis)
        # thetitle = "%s %s %s proj%s"%(b_sample,c_var,"sigma",projaxis)
        thename = "%s_proj%s"%(canvas_name,projaxis)
        thetitle = "%s proj%s"%(canvas_title,projaxis)
        ysize = _ysize
        xsize = _xsize
        canvas_nxbins = n_xbins
        canvas_nybins = n_ybins
        # these are the bin edges for each panel, printed on each panel
        plot_bins = y_bins

        proj_xtitle = x_title
        proj_ytitle = y_title
        if projaxis == "y":
            canvas_nxbins = n_ybins
            canvas_nybins = n_xbins
            plot_bins = x_bins 
            proj_xtitle = y_title
            proj_ytitle = x_title

        # First do the total projection
        DrawDataMCTypesPlot1D(data_mnvprojtot, mc_mnvprojtot, mc_typestotproj_dict, proj_xtitle, z_title, outdirname, thename+"_totalproj", canvas_title+" total proj")

        print("canvas n x bins: ",canvas_nxbins,",\t canvas n y bins: ",canvas_nybins)

        gc = PanelCanvas(thename, canvas_nxbins, canvas_nybins, round(xsize), round(ysize))
        gc.SetLeftMargin(0.1)
        gc.SetRightMargin(0.05)
        gc.SetBottomMargin(0.1)
        # gc.SetFrameLineWidth(1)
        gc.SetXTitle(proj_xtitle)
        gc.SetYTitle(z_title)
        gc.Draw()
        n_pads = len(data_mnvproj_list)
        print(n_pads)
        data_hist_list = []
        data_stat_list = []

        mc_hist_list = []
        # mc_band_list = []

        for hist in data_mnvproj_list:
            data_hist, data_stat = GetDataHistsForPlot(hist)
            data_hist_list.append(data_hist)
            data_stat_list.append(data_stat)
        for hist in mc_mnvproj_list:
            mc_hist, mc_band = GetMCHistsForPlot(hist)
            mc_hist_list.append(mc_hist)
            # mc_band_list.append(mc_band)
        
        maxlist = [hist.GetMaximum() for hist in data_hist_list] + [hist.GetMaximum() for hist in mc_hist_list]
        global_max = max(maxlist)

        for i in range(n_pads):

            pad = gc.cd(i+1)
            pad.Draw()
            tmp_pad_max = 0.0
            tmp_pad_scale = 1.0

            tmp_pad_max = max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum())
            if tmp_pad_max == 0:
                tmp_pad_max = 1.0

            tmp_pad_scale = eval('{:.{p}g}'.format(global_max / tmp_pad_max, p=3))

            data_hist_list[i].Scale(tmp_pad_scale)
            data_stat_list[i].Scale(tmp_pad_scale)
            mc_hist_list[i].Scale(tmp_pad_scale)
            mc_hist_list[i].SetLineWidth(typeslinewidth*2)
            for key in mc_typesproj_listdict:
                mc_typesproj_listdict[key][i].Scale(tmp_pad_scale)
                mc_typesproj_listdict[key][i].SetLineWidth(typeslinewidth*2)
            # mc_band_list[i].Scale(tmp_pad_scale)

            data_hist_list[i].SetMaximum(1.2 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
            data_hist_list[i].SetMinimum(0)
            if proj_xtitle.split(" (")[0] in scaleY:
                pad.SetLogy()
                data_hist_list[i].SetMaximum(1.5 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
                data_hist_list[i].SetMinimum(data_hist_list[i].GetMaximum()/1000)
            
            data_hist_list[i].GetXaxis().SetNdivisions(207)
            data_hist_list[i].GetYaxis().SetNdivisions(205)


            data_hist_list[i].Draw("axis")
            # mc_band_list[i].Draw("SAME E2")
            if "COH" in typeskeys:
                mc_typesproj_listdict["COH"][i].Draw("HIST SAME")
            if "DIS" in typeskeys:
                mc_typesproj_listdict["DIS"][i].Draw("HIST SAME")
            if "RES" in typeskeys:
                mc_typesproj_listdict["RES"][i].Draw("HIST SAME")
            if "2p2h" in typeskeys:
                mc_typesproj_listdict["2p2h"][i].Draw("HIST SAME")
            if "QE" in typeskeys:
                mc_typesproj_listdict["QE"][i].Draw("HIST SAME")
            # for key in mc_typesproj_listdict:
            #     mc_typesproj_listdict[key][i].Draw("HIST L SAME")
            # mc_hist_list[i].Draw("SAME HIST")
            mc_hist_list[i].Draw("HIST SAME")

            data_stat_list[i].Draw("SAME E1 X0")
            data_hist_list[i].Draw("SAME E1 X0")

            range_string = "{loedge} < {var} < {hiedge}".format(loedge = round(plot_bins[i], 3), var =proj_ytitle.split(" (")[0], hiedge = round(plot_bins[i+1], 3))
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.025)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)

            multip_string = "#times {:g}".format(float('{:.{p}g}'.format(tmp_pad_scale, p=2)))
            multip_latex = ROOT.TLatex()
            multip_latex.SetTextAlign(32)
            multip_latex.SetNDC()
            multip_latex.SetTextFont(42)
            multip_latex.SetTextSize(0.028)
            multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.05),multip_string)
            pad.Modified()
        pad = gc.cd(n_pads+1)
        pad.Draw()

        padwidth = 1 - pad.GetLeftMargin() - pad.GetRightMargin()
        leg = TLegend(pad.GetLeftMargin()+padwidth/10,(1.-(pad.GetTopMargin())-0.01), 1 - (pad.GetRightMargin() + padwidth/10),(pad.GetBottomMargin()+0.01))
        leg.SetNColumns(1)
        leg.SetBorderSize(0)
        leg.SetFillColor(-1)
        leg.SetTextSize(round(legendfontsize/3))

        leg.AddEntry(mc_hist_list[0], "MnvTune4.3.1","fl")
        if "QE" in typeskeys:
            leg.AddEntry(mc_typesproj_listdict["QE"][0], "QE","fl")
        if "2p2h" in typeskeys:
            leg.AddEntry(mc_typesproj_listdict["2p2h"][0], "2p2h","fl")
        if "RES" in typeskeys:
            leg.AddEntry(mc_typesproj_listdict["RES"][0], "RES","fl")
        if "DIS" in typeskeys:
            leg.AddEntry(mc_typesproj_listdict["DIS"][0], "DIS","fl")
        if "COH" in typeskeys:
            leg.AddEntry(mc_typesproj_listdict["COH"][0], "COH","fl")
        leg.AddEntry(data_hist_list[0], "Data","p")
        leg.Draw()
        pad.Modified()

        gc.SetHistTexts()
        gc.Draw()
        # canvas_name = thename + "XSec_Proj" + projaxis + "_Types"

        gc.Print(os.path.join(outdirname, thename + "_Types.png"))
        gc.Print(os.path.join(outdirname,"source", thename + "_Types.C"))
        # del gc

        gc.cd()
        leg.Clear()
        gc.ResetPads()
        gc.SetYTitle("Data / MC")
        gc.SetXTitle(proj_xtitle)
        gc.Modified()
        gc.Update()

        ratio_list = []
        typesratio_listdict = {}
        # mcerror_list = []
        straightline_list = []
        for i in range(n_pads):
            # ratio = MakeDataMCRatio(data_hist_list[i],mc_band_list[i])
            ratio = MakeDataMCRatio(data_hist_list[i],mc_hist_list[i])

            ratio.SetMinimum(0.0)
            ratio.SetMaximum(2)

            ratio.SetFillStyle(1001)
            ratio.SetLineColor(ROOT.kBlack)
            ratio.SetLineWidth(2)
            # ratio.SetTitle("")
            ratio.GetYaxis().SetNdivisions(205)
            ratio_list.append(ratio)

            for key in mc_typesproj_listdict:
                tmp_typesratio = MakeDataMCRatio(mc_typesproj_listdict[key][i],mc_hist_list[i])
                tmp_typesratio.SetLineWidth(typeslinewidth)
                if key not in typesratio_listdict.keys():
                    typesratio_listdict[key] = []
                typesratio_listdict[key].append(tmp_typesratio)
            straightline = TH1D()
            # straightline = mcerror.Clone()
            straightline = mc_hist_list[i].Clone()
            # for bin in range(1,mc_hist_list[i].GetXaxis().GetNbins() + 1):
            for bin in range(0,mc_hist_list[i].GetXaxis().GetNbins() + 2):
                straightline.SetBinContent(bin,1.0)
            straightline.SetLineColor(typescolors[0])
            straightline.SetLineWidth(3)
            straightline.SetFillStyle(0)
            straightline_list.append(straightline)


        for i in range(n_pads):
            pad = gc.cd(i+1)
            pad.SetLogy(0)

            pad.Draw()
            ratio_list[i].Draw("axis")
            if "COH" in typeskeys:
                typesratio_listdict["COH"][i].Draw("HIST SAME")
            if "DIS" in typeskeys:
                typesratio_listdict["DIS"][i].Draw("HIST SAME")
            if "RES" in typeskeys:
                typesratio_listdict["RES"][i].Draw("HIST SAME")
            if "2p2h" in typeskeys:
                typesratio_listdict["2p2h"][i].Draw("HIST SAME")
            if "QE" in typeskeys:
                typesratio_listdict["QE"][i].Draw("HIST SAME")
                
            straightline_list[i].Draw("hist same")
            ratio_list[i].Draw("same E1 X0")

            range_string = "{loedge} < {var} < {hiedge}".format(loedge = round(plot_bins[i], 3), var =proj_ytitle.split(" (")[0], hiedge = round(plot_bins[i+1], 3))
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.025)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)
        pad = gc.cd(n_pads+1)
        pad.Draw()

        padwidth = 1 - pad.GetLeftMargin() - pad.GetRightMargin()
        leg = TLegend(pad.GetLeftMargin()+padwidth/10,(1.-(pad.GetTopMargin())-0.05), 1 - (pad.GetRightMargin() + padwidth/10),(pad.GetBottomMargin()+0.05))
        leg.SetNColumns(1)
        leg.SetBorderSize(0)
        leg.SetFillColor(-1)
        leg.SetTextSize(round(legendfontsize/3))

        leg.AddEntry(mc_hist_list[0], "MnvTune4.3.1","fl")
        if "QE" in typeskeys:
            leg.AddEntry(mc_typesproj_listdict["QE"][0], "QE","fl")
        if "2p2h" in typeskeys:
            leg.AddEntry(mc_typesproj_listdict["2p2h"][0], "2p2h","fl")
        if "RES" in typeskeys:
            leg.AddEntry(mc_typesproj_listdict["RES"][0], "RES","fl")
        if "DIS" in typeskeys:
            leg.AddEntry(mc_typesproj_listdict["DIS"][0], "DIS","fl")
        if "COH" in typeskeys:
            leg.AddEntry(mc_typesproj_listdict["COH"][0], "COH","fl")
        leg.AddEntry(data_hist_list[0], "Data","p")
        leg.Draw()
        pad.Modified()
        gc.SetHistTexts()
        gc.Draw()
        gc.Print(os.path.join(outdirname, thename + "_Types_ratio.png"))
        gc.Print(os.path.join(outdirname,"source", thename + "_Types_ratio.C"))

        # # No do error summary
        # gc.cd()
        # gc.ResetPads()
        # gc.SetYTitle("Fractional Uncertainty")
        # gc.SetXTitle(proj_xtitle)
        # gc.Modified()
        # gc.Update()
        # # Now do error summary
        # gc.SetXTitle(proj_xtitle)

        # mnvPlotter = SetupErrorSummary(MnvPlotter(8))
        # include_stat_error = True
        # solid_lines_only = False
        # ignore_Threshold = 0.0
        # do_cov_area_norm = False
        # error_group_name = ""
        # do_fractional_uncertainty = True

        # for i in range(n_pads):
        #     pad = gc.cd(i+1)
        #     mnvPlotter.DrawErrorSummary(data_mnvproj_list[i], "N", include_stat_error, solid_lines_only, ignore_Threshold, do_cov_area_norm, error_group_name, do_fractional_uncertainty)
        
        # gc.SetHistTexts()
        # gc.Draw()
        # gc.Print(os.path.join(outdirname, canvas_name + "_ErrorSummary.png"))
        # gc.Print(os.path.join(outdirname,"source", canvas_name + "_ErrorSummary.C"))

            
        del gc
    # return 0

def DrawErrorSumary2D():
    return 0





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

bkgcats = [
    "chargedpion",
    "neutralpion",
    # "multipion",
    "other",
]

catstodo = [
    "data",
    "qelike",
    "chargedpion",
    "neutralpion",
    # "multipion",
    "other",
]

catsnames = {
    "data":"data", 
    "qelike":"QElike",
    "chargedpion":"1#pi^{#pm}",
    "neutralpion":"1#pi^{0}",
    "multipion":"N#pi",
    "other":"Other",
}

catscolors = {
    "data":ROOT.kBlack, 
    "qelike":ROOT.kBlue-6,
    "chargedpion":ROOT.kMagenta-6,
    "neutralpion":ROOT.kRed-6,
    "multipion":ROOT.kGreen-6,
    "other":ROOT.kYellow-6,
}

typescolors = {
    0: ROOT.kP8Red,     # total mc
    1: ROOT.kP6Grape,   # QE
    2: ROOT.kP8Orange,  # RES
    3: ROOT.kP8Cyan,    # DIS
    4: ROOT.kP8Azure,   # COH
    8: ROOT.kP8Green,   # 2p2h
}

typesnames = {
    0: "MnvTunev4.3.1",  # total mc
    1: "QE",             # QE
    2: "RES",            # RES
    3: "DIS",            # DIS
    4: "COH",            # COH
    8: "2p2h",           # 2p2h
}
typesints = {
    "MnvTunev4.3.1": 0,  # total mc
    "QE": 1,             # QE
    "RES": 2,            # RES
    "DIS": 3,            # DIS
    "COH": 4,            # COH
    "2p2h": 8,           # 2p2h
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

vars_info = {
    "EAvail": {
        "title": "E_{Avail}",
        "units": "GeV",
        "bins": [],
    },
    "ptmu": {
        "title": "p_{T}",
        "units": "GeV/c",
        "bins": [],

    },
    "pzmu" : {
        "title": "p_{||}",
        "units": "GeV/c",
        "bins": [],

    }
}

if len(sys.argv) == 1:
    print ("enter root file name and optional 2nd argument to get tuned version")
flag = "types_"
raw_filename = sys.argv[1]
if len(sys.argv)> 2:
    flag = "tuned_type_"

if "_tuned_analyzev9" in raw_filename:
    tuned_filename = raw_filename
    untuned_filename = raw_filename.replace("_tuned_","_untuned_")
elif "_untuned_analyzev9":
    untuned_filename = raw_filename
    tuned_filename = raw_filename.replace("_untuned_","_tuned_")

tuned_f = TFile.Open(tuned_filename,"READONLY")
untuned_f = TFile.Open(untuned_filename,"READONLY")

plotdirbase = os.getenv("OUTPUTLOC")

plotdir = MakePlotDir("XSecPlots")
dirname = untuned_filename.replace("_untuned_analyzev9.root", "_XSec")

# outfilename=filebasename1.replace(".root","_2DPlots")
outdirname = os.path.join(plotdir, dirname)
if not os.path.exists(outdirname):
    print(outdirname)
    os.mkdir(outdirname)

# source_outdirname = os.path.join(outdirname, "source")
# if not os.path.exists(source_outdirname):
#     print(source_outdirname)
#     os.mkdir(source_outdirname)

# if not os.path.exists(os.path.join(outdirname,"bkgsub")):
#     print( os.path.join(outdirname,"bkgsub"))
#     os.mkdir(os.path.join(outdirname,"bkgsub"))
#     os.mkdir(os.path.join(outdirname,"bkgsub","source"))

# if not os.path.exists(os.path.join(outdirname,"unfolded")):
#     print( os.path.join(outdirname,"unfolded"))
#     os.mkdir(os.path.join(outdirname,"unfolded"))
#     os.mkdir(os.path.join(outdirname,"unfolded","source"))

# if not os.path.exists(os.path.join(outdirname,"efficiency")):
#     print( os.path.join(outdirname,"efficiency"))
#     os.mkdir(os.path.join(outdirname,"efficiency"))
#     os.mkdir(os.path.join(outdirname,"efficiency","source"))

# if not os.path.exists(os.path.join(outdirname,"sigma")):
#     print( os.path.join(outdirname,"sigma"))
#     os.mkdir(os.path.join(outdirname,"sigma"))
#     os.mkdir(os.path.join(outdirname,"sigma","source"))

# keys = f.GetListOfKeys()

h_pot = untuned_f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(2)
POTScale = dataPOT / mcPOTprescaled
if ("potscaled_combined_" in untuned_filename):
    POTScale = 1.0
print("POTScale: ",POTScale)


# find all the valid histogram and group by keywords
print("Making dict of source hists...")
print("\tLooking at untuned...")
input_hists = GetInputHistDict(untuned_f)
print("\tLooking at tuned...")
input_hists = GetInputHistDict(tuned_f, input_hists)
print("Making dict of source types hists...")
input_typeshists = GetInputTypesHistDict(untuned_f)
input_typeshists = GetInputTypesHistDict(tuned_f,input_typeshists)
# print(input_typeshists)
# sys.exit(1)
# print(input_hists)

analyze_stage_list = [
    "mc_tot",
    "mc_bkg_tot",
    "signalfraction",
    "bkgfraction",
    "bkgsub",
    "bkgsub_unfolded",
    "bkgsub_unfolded_effcorr",
    "efficiency",
    "bkgsub_unfolded_effcorr_sigma",
    "sigmaMC"
]


print("Making dict of analyze hists...")
print("\tLooking at untuned...")
analyze_hists = GetAnalyzeHistDict(untuned_f, False)
print("\tLooking at tuned...")
analyze_hists = GetAnalyzeHistDict(tuned_f, True, analyze_hists)

print("Making dict of analyze types hists...")
analyze_typeshists = GetAnalyzeTypesHistDict(untuned_f, False)
analyze_typeshists = GetAnalyzeTypesHistDict(tuned_f, True, analyze_typeshists)

keys = tuned_f.GetListOfKeys()
if "varsFile" not in keys:
    bigvarconfig_string = tuned_f.Get("varsFile_5A").GetTitle()
else:
    bigvarconfig_string = tuned_f.Get("varsFile").GetTitle()
bigvarconfig_dict = json.loads(re.sub("//.*", "", bigvarconfig_string, flags = re.MULTILINE))


# print(analyze_hists)
# analyze_dict[hist][sample][var][stage] = hist
ROOT.gStyle.SetOptStat(0)
for a_hist in analyze_hists.keys():
    # if a_hist == "h2D":
    #     print("2d not set up, skipping")
    #     continue
    print(a_hist)
    for b_sample in analyze_hists[a_hist].keys():
        datasample = b_sample
        plottitle = ""
        print(b_sample)
        if "_Tuned" in b_sample:
            dotuned = True
            datasample = datasample.replace("_Tuned","")
            plottitle += "Tuned "
        # else: 
        #     print ("This is an untuned sample. Skipping...")
        #     continue
        for c_var in analyze_hists[a_hist][b_sample].keys():
            if c_var in skipvar_list:
                continue
            if "pzmu" in c_var: continue
            mnvPlotter = MnvPlotter()
            print(c_var)

            tmp_mcrecosig_tuned = input_hists[a_hist][b_sample][c_var]["qelike"]["reconstructed_tuned"]
            tmp_mcseltru_tuned = input_hists[a_hist][b_sample][c_var]["qelike"]["selected_truth_tuned"]
            tmp_mcalltru_tuned = input_hists[a_hist][b_sample][c_var]["qelike"]["all_truth_tuned"]

            tmp_bkgsub = analyze_hists[a_hist][b_sample][c_var]["bkgsub"]
            tmp_bkgsub_tuned = analyze_hists[a_hist][b_sample][c_var]["bkgsub_tuned"]

            # unfolded
            tmp_unfolded = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded"]
            # Make a list for the unfolded by iteration
            tmp_unfoldediter_list = []
            for key in analyze_hists[a_hist][b_sample][c_var].keys():
                # print(">>>>>>>unfolded iter check on ", key)
                if "unfolded" not in key: continue
                if "iter" not in key: continue
                if "tuned" in key: continue
                print("untuned unfolded iter hist:", key)
                tmp_unfoldediter_list.append(analyze_hists[a_hist][b_sample][c_var][key])
            # want to add the last iter
            tmp_unfoldediter_list.append(tmp_unfolded)

            tmp_unfolded_tuned = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_tuned"]
            tmp_unfoldediter_tuned_list = []
            index = 0
            for key in analyze_hists[a_hist][b_sample][c_var].keys():
                # print(">>>>>>>unfolded iter check on ", key)
                if "unfolded" not in key: continue
                if "iter" not in key: continue
                if "tuned" not in key: continue
                print("tuned unfolded iter hist:", key)
                tmp_unfoldediter_tuned_list.append(analyze_hists[a_hist][b_sample][c_var][key])
            tmp_unfoldediter_tuned_list.append(tmp_unfolded_tuned)

            # Efficiency related things
            tmp_efficiency = analyze_hists[a_hist][b_sample][c_var]["efficiency"]
            tmp_efficiency_tuned = analyze_hists[a_hist][b_sample][c_var]["efficiency_tuned"]

            tmp_effcorr = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_effcorr"]
            tmp_effcorr_tuned = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_effcorr_tuned"]

            # Cross sections  
            tmp_sigma = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_effcorr_sigma"]
            tmp_sigma_tuned = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_effcorr_sigma_tuned"]
            tmp_sigmamc = analyze_hists[a_hist][b_sample][c_var]["sigmaMC"]
            tmp_sigmamc_tuned = analyze_hists[a_hist][b_sample][c_var]["sigmaMC_tuned"]

            found_typessigma = False
            found_typessigmatuned = False
            if a_hist in analyze_typeshists:
                if b_sample in analyze_typeshists[a_hist]:
                    if c_var in analyze_typeshists[a_hist][b_sample]:
                        if "sigmaMC" in analyze_typeshists[a_hist][b_sample][c_var]:
                            print("found types sigmamc")
                            tmp_typessigma = analyze_typeshists[a_hist][b_sample][c_var]["sigmaMC"]
                            found_typessigma = True
                        if "sigmaMC_tuned" in analyze_typeshists[a_hist][b_sample][c_var]:
                            print("found tuned types sigmamc")
                            tmp_typessigma = analyze_typeshists[a_hist][b_sample][c_var]["sigmaMC_tuned"]
                            found_typessigmatuned = True
            
            found_inputtypes = False
            found_inputtypestuned = False
            # print(input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed_tuned"].keys())

            if a_hist in input_typeshists:

                if b_sample in input_typeshists[a_hist].keys():

                    if c_var in input_typeshists[a_hist][b_sample].keys():
                        print("keys for input typehists: ", input_typeshists[a_hist][b_sample][c_var].keys())

                        if "reconstructed" in input_typeshists[a_hist][b_sample][c_var]["qelike"].keys():
                            print("found types inputhists")
                            found_inputtypes = True
                        if "reconstructed_tuned" in input_typeshists[a_hist][b_sample][c_var]["qelike"].keys():
                            print("found tuned types inputhists")
                            found_inputtypestuned = True
            # sys.exit(1)

            tmp_types_mcreco = []
            tmp_types_mcseltru = []
            tmp_types_mcalltru = []
            if found_inputtypes:
                tmp_types_mcreco = input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed"]
                tmp_types_mcseltru = input_typeshists[a_hist][b_sample][c_var]["qelike"]["selected_truth"]
                tmp_types_mcalltru = input_typeshists[a_hist][b_sample][c_var]["qelike"]["all_truth"]
            if found_inputtypestuned:
                print("keys", input_typeshists[a_hist][b_sample][c_var]["qelike"].keys())
                tmp_types_mcreco = input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed_tuned"]
                tmp_types_mcseltru = input_typeshists[a_hist][b_sample][c_var]["qelike"]["selected_truth_tuned"]
                tmp_types_mcalltru = input_typeshists[a_hist][b_sample][c_var]["qelike"]["all_truth_tuned"]

            tmp_canvas_basename = "%s_%s"%(b_sample,c_var)
            tmp_canvas_basetitle = "%s %s"%(b_sample,c_var)
            
            var_outdir = os.path.join(outdirname,c_var)
            if not os.path.exists(var_outdir):
                print( var_outdir)
                os.mkdir(var_outdir)
                os.mkdir(os.path.join(var_outdir,"source"))

            if a_hist=="h":
                var_title = c_var
                var_units = "unit"
                if c_var in vars_info:
                    var_title = vars_info[c_var]["title"]
                    var_units = vars_info[c_var]["units"]
                    if len(vars_info[c_var]["bins"]) == 0:
                        print("making bins")
                        varconfig = bigvarconfig_dict["1D"][c_var]
                        if "bins" in varconfig.keys():
                            bins1D = [float(tmpbin) for tmpbin in varconfig["bins"]]
                            vars_info[c_var]["bins"] = bins1D
                        elif "nbins" in varconfig.keys():
                            mini = varconfig["min"]
                            maxi = varconfig["max"]
                            width = (maxi - mini)/varconfig["nbins"]
                            bins1D = [mini + tmpbin * width for tmpbin in range(0,varconfig["nbins"]+1)]
                            # print(bins1D)
                            vars_info[c_var]["bins"] = bins1D
                counts_ytitle = "Counts/%s"%(var_units)

                # bkg subtracted 
                if "bkgsub" not in skipstage_list:
                    bkgsub_canvas_name = tmp_canvas_basename + "_bkgsub"
                    bkgsub_canvas_title = tmp_canvas_basetitle + " Background Subtracted"
                    DrawDataMCPlot1D(
                        tmp_bkgsub_tuned, tmp_mcrecosig_tuned, 
                        "Reconstructed %s (%s)"%(var_title, var_units), counts_ytitle, 
                        var_outdir, 
                        bkgsub_canvas_name, bkgsub_canvas_title
                    )
                    if found_inputtypestuned:
                        DrawDataMCTypesPlot1D(
                            tmp_bkgsub_tuned, tmp_mcrecosig_tuned, tmp_types_mcreco, 
                            "%s (%s)"%(var_title,var_units), counts_ytitle, 
                            var_outdir, 
                            bkgsub_canvas_name, bkgsub_canvas_title
                        )
                    DrawErrorSummary1D(
                        tmp_bkgsub_tuned, 
                        "%s (%s)"%(var_title, var_units), 
                        var_outdir, 
                        bkgsub_canvas_name+"_tuned", bkgsub_canvas_title + " Tuned"
                    )
                    DrawErrorSummary1D(
                        tmp_bkgsub, 
                        "%s (%s)"%(var_title, var_units), 
                        var_outdir, 
                        bkgsub_canvas_name+"_untuned", bkgsub_canvas_title + " Untuned"
                    )
                    # TODO types

                # unfolded hists
                if "unfolded" not in skipstage_list:
                    unfolded_canvas_name = tmp_canvas_basename + "_unfolded"
                    unfolded_canvas_title = tmp_canvas_basetitle + " Unfolded"
                    DrawDataMCPlot1D(
                        tmp_unfolded_tuned, tmp_mcseltru_tuned, 
                        "%s (%s)"%(var_title,var_units), counts_ytitle, 
                        var_outdir, 
                        unfolded_canvas_name, unfolded_canvas_title
                    )
                    if found_inputtypestuned:
                        DrawDataMCTypesPlot1D(
                            tmp_unfolded_tuned, tmp_mcseltru_tuned, tmp_types_mcseltru, 
                            "%s (%s)"%(var_title,var_units), counts_ytitle, 
                            var_outdir, 
                            unfolded_canvas_name, unfolded_canvas_title
                        )
                    for i in range(len(tmp_unfoldediter_tuned_list)):
                        tmp_canvas_name = "%siter%d"%(unfolded_canvas_name, i+1)
                        tmp_canvas_title = "%s iter %d"%(unfolded_canvas_title, i+1)
                        DrawDataMCPlot1D(
                            tmp_unfoldediter_tuned_list[i], tmp_mcseltru_tuned, 
                            "Unfolded %s (%s)"%(var_title, var_units), counts_ytitle, 
                            var_outdir, 
                            tmp_canvas_name, tmp_canvas_title
                        )
                        if found_inputtypestuned:
                            DrawDataMCTypesPlot1D(
                                tmp_unfoldediter_tuned_list[i], tmp_mcseltru_tuned, tmp_types_mcseltru, 
                                "%s (%s)"%(var_title,var_units), counts_ytitle, 
                                var_outdir, 
                                tmp_canvas_name, tmp_canvas_title
                            )
                    DrawErrorSummary1D(
                        tmp_unfolded_tuned, 
                        "%s (%s)"%(var_title, var_units), 
                        var_outdir, 
                        unfolded_canvas_name, unfolded_canvas_title
                    )
                    # TODO types

                # effcorr hists
                if "effcorr" not in skipstage_list:
                    effcorr_canvas_name = tmp_canvas_basename + "_effcorr"
                    effcorr_canvas_title = tmp_canvas_basename + " Efficiency Corrected"
                    DrawDataMCPlot1D(
                        tmp_effcorr_tuned, tmp_mcalltru_tuned, 
                        "True %s (%s)"%(var_title,var_units), counts_ytitle, 
                        var_outdir, 
                        effcorr_canvas_name, effcorr_canvas_title
                        )
                    DrawErrorSummary1D(
                        tmp_effcorr_tuned, 
                        "%s (%s)"%(var_title,var_units), 
                        var_outdir, 
                        effcorr_canvas_name, effcorr_canvas_title
                    )
                    if found_inputtypestuned:
                        DrawDataMCTypesPlot1D(
                            tmp_effcorr_tuned, tmp_mcalltru_tuned, tmp_types_mcalltru, 
                            "%s (%s)"%(var_title,var_units), counts_ytitle, 
                            var_outdir, 
                            effcorr_canvas_name, effcorr_canvas_title
                        )
                    # TODO types
                    # TODO effieciency


                # cross section
                if "sigma" not in skipstage_list:
                    sigma_ytitle = "d#sigma/d%s (cm^{2}/%s/Nucleon)"%(var_title,var_units)
                    sigma_canvas_name = tmp_canvas_basename + "_sigma"
                    sigma_canvas_title = tmp_canvas_basetitle + " sigma"
                    DrawDataMCPlot1D(
                        tmp_sigma_tuned,tmp_sigmamc, 
                        "%s (%s)"%(var_title,var_units), sigma_ytitle, 
                        var_outdir, 
                        sigma_canvas_name, sigma_canvas_title
                    )
                    DrawErrorSummary1D(
                        tmp_sigma, 
                        "%s (%s)"%(var_title, var_units), 
                        var_outdir, 
                        sigma_canvas_name, sigma_canvas_title
                    )
                    if found_typessigma:
                        DrawDataMCTypesPlot1D(
                            tmp_sigma_tuned, tmp_sigmamc, tmp_typessigma, 
                            "%s (%s)"%(var_title,var_units), sigma_ytitle, 
                            var_outdir, 
                            sigma_canvas_name, sigma_canvas_title
                        )

            if a_hist == "h2D":
                print(">>>>>> doing 2D")
                xvar = c_var.split("_")[0]
                yvar = c_var.split("_")[1]

                xvar_name = xvar
                xvar_units = "xunits"
                if xvar in vars_info:
                    xvar_name = vars_info[xvar]["title"]
                    xvar_units = vars_info[xvar]["units"]
                    xvar_bins =  vars_info[xvar]["bins"]
                yvar_name = yvar
                yvar_units = "yunits"
                if yvar in vars_info:
                    yvar_name = vars_info[yvar]["title"]
                    yvar_units = vars_info[yvar]["units"]
                    yvar_bins =  vars_info[yvar]["bins"]
                    print(yvar, yvar_bins)
                    
                xvar_title = "%s (%s)"%(xvar_name,xvar_units)
                yvar_title = "%s (%s)"%(yvar_name, yvar_units)
                counts_ztitle = "Counts/%s/%s"%(xvar_units, yvar_units)

                # bkgsubtracted
                if "bkgsub" not in skipstage_list:
                    bkgsub_canvas_name = tmp_canvas_basename + "_bkgsub"
                    bkgsub_canvas_title = tmp_canvas_basetitle + " Background Subtracted"
                    DrawDataMCPlot2D(
                        tmp_bkgsub_tuned, tmp_mcrecosig_tuned, 
                        xvar_title, xvar_bins, 
                        yvar_title, yvar_bins, 
                        counts_ztitle, 
                        var_outdir, 
                        bkgsub_canvas_name, bkgsub_canvas_title
                    )
                    if found_inputtypestuned:
                        DrawDataMCTypesPlot2D(
                            tmp_bkgsub_tuned, tmp_mcrecosig_tuned, tmp_types_mcreco, 
                            xvar_title, xvar_bins, yvar_title, yvar_bins, 
                            counts_ztitle, 
                            var_outdir, 
                            bkgsub_canvas_name, bkgsub_canvas_title
                        )
                # unfolded
                if "unfolded" not in skipstage_list:
                    unfolded_canvas_name = tmp_canvas_basename + "_unfolded"
                    unfolded_canvas_title = tmp_canvas_basetitle + " Unfolded"
                    DrawDataMCPlot2D(
                        tmp_unfolded_tuned, tmp_mcseltru_tuned, 
                        xvar_title, xvar_bins, 
                        yvar_title, yvar_bins, 
                        counts_ztitle, 
                        var_outdir, 
                        unfolded_canvas_name, unfolded_canvas_title
                    )
                    if found_inputtypestuned:
                        DrawDataMCTypesPlot2D(
                            tmp_unfolded_tuned, tmp_mcseltru_tuned, tmp_types_mcseltru, 
                            xvar_title, xvar_bins, yvar_title, yvar_bins, 
                            counts_ztitle, 
                            var_outdir, 
                            unfolded_canvas_name, unfolded_canvas_title
                        )

                    for i in range(len(tmp_unfoldediter_tuned_list)):
                        tmp_canvas_name = "%siter%d"%(unfolded_canvas_name, i+1)
                        tmp_canvas_title = "%s iter %d"%(unfolded_canvas_title, i+1)
                        DrawDataMCPlot2D(
                            tmp_unfoldediter_tuned_list[i], tmp_mcseltru_tuned, 
                            xvar_title, xvar_bins, 
                            yvar_title, yvar_bins, 
                            counts_ztitle, 
                            var_outdir, 
                            tmp_canvas_name, tmp_canvas_title
                        )
                        if found_inputtypestuned:
                            DrawDataMCTypesPlot2D(
                                tmp_unfoldediter_tuned_list[i], tmp_mcseltru_tuned, tmp_types_mcseltru, 
                                xvar_title, xvar_bins, yvar_title, yvar_bins, 
                                counts_ztitle, 
                                var_outdir, 
                                unfolded_canvas_name, unfolded_canvas_title
                            )

                # eff corr
                if "effcorr" not in skipstage_list:
                    effcorr_canvas_name = tmp_canvas_basename + "_effcorr"
                    effcorr_canvas_title = tmp_canvas_basename + " Efficiency Corrected"
                    DrawDataMCPlot2D(
                        tmp_effcorr_tuned, tmp_mcalltru_tuned, 
                        xvar_title, xvar_bins, 
                        yvar_title, yvar_bins, 
                        counts_ztitle, 
                        var_outdir, 
                        effcorr_canvas_name, effcorr_canvas_title
                    )
                    if found_inputtypestuned:
                        DrawDataMCTypesPlot2D(
                            tmp_effcorr_tuned, tmp_mcalltru_tuned, tmp_types_mcalltru, 
                            xvar_title, xvar_bins, yvar_title, yvar_bins, 
                            counts_ztitle, 
                            var_outdir, 
                            effcorr_canvas_name, effcorr_canvas_title
                        )

                # cross section
                if "sigma" not in skipstage_list:
                    sigma_ztitle = "d^{2}#sigma/d%sd%s (cm^{2}/%s/%s/Nucleon)"%(xvar_name,yvar_name,xvar_units,yvar_units)
                    sigma_canvas_name = tmp_canvas_basename + "_sigma"
                    sigma_canvas_title = tmp_canvas_basetitle + " sigma"

                    DrawDataMCPlot2D(
                        tmp_sigma_tuned, tmp_sigmamc, 
                        xvar_title, xvar_bins, yvar_title, yvar_bins, 
                        sigma_ztitle, 
                        var_outdir, 
                        sigma_canvas_name, sigma_canvas_title
                    )
                    if found_typessigma:
                        DrawDataMCTypesPlot2D(
                            tmp_sigma_tuned, tmp_sigmamc, tmp_typessigma, 
                            xvar_title, xvar_bins, yvar_title, yvar_bins, 
                            sigma_ztitle, 
                            var_outdir, 
                            sigma_canvas_name, sigma_canvas_title
                        )
                # DrawErrorSummary2D()


sys.exit(1)
