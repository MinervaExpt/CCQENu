import inspect
from re import L
import sys,os
import ROOT
ROOT.gROOT.SetBatch(True) # Run in batch mode
import numpy as np
from ROOT import (
    gROOT,
    gStyle, 
    TFile,
    THStack,
    TH1D,
    TH2D,
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
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter, HyperDimLinearizer, GridCanvas, MnvHist
import datetime
import ctypes
import math
import json, re
from optparse import OptionParser

mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")

# # stuff for plot style
# data_marker_size = 0.5
# data_marker_style = 20
# bkg_fill_style = 3244
band_alphalevel = 0.2

# catscolors = {
#     "data":        ROOT.kBlack, 
#     "qelike":       ROOT.kP10Blue,
#     "chargedpion":  ROOT.kP10Yellow,
#     "neutralpion":  ROOT.kP10Orange,
#     "multipion":    ROOT.kP10Violet,
#     "other":        ROOT.kP10Ash,
#     "other_np":     ROOT.kP10Ash,
#     # "mctot":        ROOT.kP10Red,
#     "mctot":        ROOT.kP8Red,
#     0:              ROOT.kP8Red,     # total mc
#     1:              ROOT.kP8Blue,    # QE
#     2:              ROOT.kP8Orange,  # RES
#     3:              ROOT.kP8Pink,   # DIS
#     4:              ROOT.kP8Green,    # COH
#     8:              ROOT.TColor.GetColorBright(ROOT.kP8Azure),  # 2p2h
#     11:              ROOT.kP8Blue,    # QE
#     12:              ROOT.kP8Orange,  # RES
#     13:              ROOT.kP8Pink,   # DIS
#     14:              ROOT.kP8Green,    # COH
#     18:              ROOT.TColor.GetColorBright(ROOT.kP8Azure),  # 2p2h
# }

# typestodo = [
#     1,
#     2,
#     3,
#     4,
#     8,
#     11,
#     12,
#     13,
#     14,
#     18,
# ]

# typesnames = {
#     1: "QE",
#     2: "RES",
#     3: "DIS",
#     4: "COH",
#     8: "2p2h",
#     11: "Bkg QE",
#     12: "Bkg RES",
#     13: "Bkg DIS",
#     14: "Bkg COH",
#     18: "Bkg 2p2h",
# }

# # Organization of cats
mainsig = "qelike"
mainbkg = "qelikenot"


signalcats = [
    "qelike",
    "qelike_neutron",
    "qelike_proton",
]
# signaltodo = [
#     "qelike",
#     # "qelike_neutron",
#     # "qelike_proton",
# ]

backgroundcats = [
    "qelikenot",
    "chargedpion",
    "neutralpion",
    "other",
    "multipion",
    "other_np",
]
# backgroundtodo = [
#     "chargedpion",
#     "neutralpion",
#     "other",
#     # "multipion",
#     # "other_np",
# ]

# catsorder = [
#     "qelike",
#     "qelike_neutron",
#     "qelike_proton",
#     "qelikenot",
#     "chargedpion",
#     "neutralpion",
#     "other",
#     "multipion",
#     "other_np",
#     1,
#     2,
#     3,
#     4,
#     8,
#     11,
#     12,
#     13,
#     14,
#     18,
# ]
catstodo = [
    "qelike",
    "chargedpion",
    "neutralpion",
    "other",
    "multipion",
    "other_np",
]
# catsgroups = {
#     "normal": [
#         "qelike",
#         "chargedpion",
#         "neutralpion",
#         "other",
#     ],
#     "multipion": [
#         "qelike",
#         "chargedpion",
#         "neutralpion",
#         "multipion",
#         "other_np",
#     ],
# }

# xsecgroup = [
#     "selected_truth": "unfolded",
#     "all_truth": "effcorr",
#     ""
# ]
samplestodo = [
    "QElike",
    "TrackSideband",
    "BlobSideband",
    "MultipBlobSideband",
]
catsgroups = {
    "normal": [
        "qelike",
        "chargedpion",
        "neutralpion",
        "other"
    ],
    "multipi": [
        "qelike",
        "chargedpion",
        "neutralpion",
        "mutlipion",
        "other_np",
    ],
    "qelike_split": [
        "qelike",
        "qelikeproton",
        "qelikeneutron"
        "chargedpion",
        "neutralpion",
        "other"
    ]
}
def GetHistDict(i_file, groups = {}, dotuned = False, POTScale = -1.0):
    # groups = {}
    # for filekey in i_file_dict:
        # dotuned = False
        # if filekey == "tuned": dotuned = True
        # if filekey == "modelcomp": continue
        # if filekey == "datacomp": continue
        # keys = i_file.GetListOfKeys()
        # i_file = i_file_dict[filekey]
    keys = i_file.GetListOfKeys()
    # keys.SetDirectory(ROOT.nullptr)
    for k in keys:
        # Need to reset this bc we don't scale the analyze hists, but other hists might need to be done
        tmp_POTScale = POTScale 
        # Default
        inttype = 0
        is_analyze = False
        name = k.GetName()
        if "___" in name:
            parse = name.split("___")
            if len(parse) < 5: 
                continue
            hist = parse[0]
            sample = parse[1]
            cat = parse[2]
            variable = parse[3]
            stage = parse[4] # equivalent to recotrutype
            if "types" in stage:
                if int(stage.split("_")[-1]) == 0: continue
                inttype = int(stage.split("_")[-1])
                stage = stage.replace("_types_%s"%(parse[4].split("_")[-1]), "")
            if "response" in stage:
                if "migration" not in stage or "noPOTscale" in stage:
                    continue
                if "tuned" in stage: stage = "response_migration_tuned" #This necessary?
        elif "_" in name:
            if name in ["flux_dewidthed" "POT_summary", "Combined_POT_summary"]:
                continue
            if "POT_Summary" in name or "POT_summary" in name: continue
            if type(i_file.Get(name)) not in [type(MnvH1D()), type(MnvH2D()), type(TH1D()), type(TH2D())]:
                continue
            print(name)
            parse = name.split("_")
            if len(parse) < 3: continue
            hist = parse[0]
            sample = parse[1]
            variable = parse[2]
            shift = 0

            if hist=="h2D":
                variable+="_"+parse[3]
                shift = 1
            # TODO need to figure out if mc_tot, mc_bkg_tot, signalfraction, bkgfraction ,etc should be kept...
            if parse[3+shift] in ["mc","signalfraction", "bkgfraction",]:
                continue
            elif parse[3+shift] in ["efficiency", "sigmaMC",]:
                cat = "qelike"
            else:
                cat = "data"
            typeshift = 0
            if "types" in parse:
                if int(parse[-1]) == 0: continue
                inttype = int(parse[-1])
                typeshift = 2

    
            # Old way would add everything, we just want the end I think
            stage = parse[len(parse) - typeshift - 1]
            if "unfold" in stage and "unfolded" not in stage: stage.replace("unfold","unfolded") #maybe this has been fixed...
            if dotuned: stage += "_tuned"
            tmp_POTScale = -1.0
            is_analyze = True
        else:
            continue
        if sample not in samplestodo:
            if variable == "EAvail_ptmu": sys.exit(1)
            continue

        # if cat not in catstodo:
        #     continue
        if cat in backgroundcats and inttype != 0:
            inttype += 10
        if type(i_file.Get(name)) not in [
            type(MnvH1D()), type(MnvH2D()), type(TH1D()), type(TH2D())
        ]:
            continue
        h = i_file.Get(name).Clone()
        h.SetDirectory(ROOT.nullptr)
        if h.GetEntries() <= 0:
            if stage in ["reconstructed", "reconstructed_tuned"]:
                    if inttype in [4,14]:
                        # if cat in ["qelike", "qelike_proton", "qelike_neutron"]:
                        h.Print()
                    else:
                        continue
                    # else:
                    #     continue

            else:
                continue
            #     print("hist %s has no entries, but might be a COH in reco signal that we need to make plotting work later")
            # else:
            #     print("hist %s has no entries. Skipping..."%name)

                # continue
        if cat != "data" and tmp_POTScale >= 0:
            h.Scale(tmp_POTScale)

        if hist not in groups.keys():
            groups[hist] = {}
        if sample not in groups[hist].keys():
            groups[hist][sample] = {}
        if variable not in groups[hist][sample]:
            groups[hist][sample][variable] = {}
        if stage not in groups[hist][sample][variable]:
            groups[hist][sample][variable][stage] = {}
        if cat not in groups[hist][sample][variable][stage]:
            groups[hist][sample][variable][stage][cat] = {}
        if inttype not in groups[hist][sample][variable][stage][cat]:
            groups[hist][sample][variable][stage][cat][inttype] = {}
        # else:
        #     # Don't overwrite things from previous files
        #     continue
        print("found hist %s"%name)
        groups[hist][sample][variable][stage][cat][inttype] = h.Clone()
        print(inttype)
        if inttype == 15: 
            print(h.GetEntries())
            sys.exit(1)
    # Make qelikenot and mctot
    print("making mctot and qelikenot")
    for a_hist in groups:
        for b_sample in groups[a_hist]:
            for c_var in groups[a_hist][b_sample]:
                for d_stage in groups[a_hist][b_sample][c_var]:
                    if d_stage not in ["reconstructed", "reconstructed_tuned"]: continue
                    tmp_stage_dict = groups[a_hist][b_sample][c_var][d_stage]
                    if "qelikenot" not in tmp_stage_dict:
                        tmp_bkgcats = []
                        for key in catsgroups:
                            badbkg = False
                            for cat in catsgroups[key]:
                                if cat not in tmp_stage_dict:
                                    badbkg = True
                                    break
                            if not badbkg: 
                                tmp_bkgcats = catsgroups[key]
                                break
                        tmp_qelikenot_dict = {}
                        for f_inttype in tmp_stage_dict[tmp_bkgcats[1]]:
                            first_cat = True
                            for e_cat in tmp_bkgcats:
                                # print(e_cat)
                                if e_cat in ["qelike"]: continue
                                if first_cat:
                                    tmp_hist = tmp_stage_dict[e_cat][f_inttype].Clone(tmp_stage_dict[e_cat][f_inttype].GetName().replace(e_cat, "qelikenot"))
                                    tmp_qelikenot_dict[f_inttype] = tmp_hist
                                    first_cat = False
                                    continue
                                tmp_qelikenot_dict[f_inttype].Add(tmp_stage_dict[e_cat][f_inttype])

                        if len(tmp_bkgcats) != 0: 
                            groups[a_hist][b_sample][c_var][d_stage]["qelikenot"] = tmp_qelikenot_dict
                    if "mctot" not in tmp_stage_dict and "qelike" in tmp_stage_dict and "qelikenot" in tmp_stage_dict:
                        tmp_mctot_dict = {}
                        for f_inttype in tmp_stage_dict["qelike"]:
                            tmp_mctot = tmp_stage_dict["qelike"][f_inttype].Clone(tmp_stage_dict["qelike"][f_inttype].GetName().replace("qelike","mctot"))
                            tmp_mctot.Add(tmp_stage_dict["qelike"][f_inttype])
                            tmp_mctot_dict[f_inttype] = tmp_mctot
                        groups[a_hist][b_sample][c_var][d_stage]["mctot"] = tmp_mctot_dict
    return groups

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
        os.makedirs(plotdir)
    if subdir == "":
        return plotdir
    if not os.path.exists(os.path.join(plotdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(plotdir, subdir))
        os.makedirs(os.path.join(plotdir, subdir))
    return os.path.join(plotdir, subdir)

def MakeThesisPlotDir(subdir = ""):
    plotdir = ""
    base_plotdir = os.environ.get("THESISPLOTDIR")
    if base_plotdir == None:
        return plotdir
    plotdir = base_plotdir
    if not os.path.exists(plotdir):
        print("Can't find plot dir. Making it now... ", plotdir)
        os.makedirs(plotdir)
    if subdir == "":
        return plotdir
    if not os.path.exists(os.path.join(plotdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(plotdir, subdir))
        os.makedirs(os.path.join(plotdir, subdir))
    return os.path.join(plotdir, subdir)


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

    print("HyperDPanelCanvas: Making a grid canvas named "+name+" with a grid of ",n_xbins,"    ",n_ybins,"    ",grid_x,"    ",grid_y)

    # gc2 = PlotUtils.GridCanvas(name, grid_x, grid_y, x_size, y_size)
    # gc2 = GridCanvas(name, grid_x, grid_y, x_size, y_size)
    gc2 = GridCanvas(name, grid_x, grid_y, x_size, y_size)
    # gc2.SetRightMargin(0.05)
    # gc2.SetLeftMargin(0.05)
    gc2.ResetPads()

    return gc2

def GetPadMax(i_data_hist, i_mctot_hist, including_errors = True):
    data_max = i_data_hist.GetBinContent(i_data_hist.GetMaximumBin())
    mc_max = i_mctot_hist.GetBinContent(i_mctot_hist.GetMaximumBin())
    tmp_max = max(data_max, mc_max)
    if including_errors:
        tmp_data = i_data_hist.Clone()
        if type(i_data_hist)==type(MnvH1D()):
            tmp_data = i_data_hist.GetCVHistoWithError().Clone()
        for i in range(1,tmp_data.GetNbinsX()+1):
            # print("\t%s\t%s"%(tmp_data.GetBinContent(i),tmp_data.GetBinError(i)))
            cont_and_err = tmp_data.GetBinContent(i) + tmp_data.GetBinError(i)
            if cont_and_err > tmp_max:
                # print("\tcont_and_err:", cont_and_err, "\ttmp_max", tmp_max)
                tmp_max = cont_and_err
                # return cont_and_err
    # print("\tGoing with tmp max cont_and_err:", cont_and_err, "\ttmp_max:", tmp_max)
    return tmp_max


def MakeMCtotPretty(i_mctot):
    mctot = i_mctot.Clone()
    mctot.SetLineColor(catscolors["mctot"])
    mctot.SetLineWidth(i_mctot.GetLineWidth())
    mctot.SetFillColor(0)
    return mctot

def GetMCBandAndCV(i_mc_mnv):
    mc_mnv = i_mc_mnv.Clone()

    cv = mc_mnv.GetCVHistoWithError(True, False)
    cv.SetFillColor(0)
    cv.SetLineColor(mc_mnv.GetLineColor())
    cv.SetLineWidth(mc_mnv.GetLineWidth())

    band = mc_mnv.Clone()
    band.SetFillStyle(1001)
    band.SetFillColorAlpha(mc_mnv.GetFillColor(), band_alphalevel)
    band.SetLineColor(mc_mnv.GetLineColor())
    band.SetLineWidth(mc_mnv.GetLineWidth())
    band.SetMarkerStyle(0)

    return cv, band

def GetDataStatAndSyst(i_data_mnv, do_pinkstat = False):
    data_mnv = i_data_mnv.Clone()

    stat = data_mnv.GetCVHistoWithStatError()
    stat.SetMarkerColor(data_mnv.GetMarkerColor())
    stat.SetLineWidth(data_mnv.GetLineWidth())
    stat.SetLineColor(data_mnv.GetLineColor())
    if do_pinkstat:
        stat.SetLineWidth(4)
        stat.SetLineColorAlpha(ROOT.kPink, band_alphalevel) #mnvh.GetLineColor())
        stat.SetFillColorAlpha(ROOT.kPink, band_alphalevel)
    stat.SetMarkerSize(0)
    stat.SetMarkerStyle(1)

    syst = data_mnv.GetCVHistoWithError()
    syst.SetMarkerColor(data_mnv.GetMarkerColor())
    syst.SetMarkerSize(data_mnv.GetMarkerSize())
    syst.SetMarkerStyle(data_mnv.GetMarkerStyle())
    syst.SetLineWidth(data_mnv.GetLineWidth())
    syst.SetLineColor(data_mnv.GetLineColor())
    
    return stat, syst

def MakeRatioHist(i_hist, i_ref_hist):
    ratio = i_hist.Clone()
    ref_hist = i_ref_hist.Clone()

    if type(hist) in [type(MnvH1D()), type(MnvH2D())]:
        ref_hist.ClearAllErrorBands()
        ref_hist.AddMissingErrorBandsAndFillWithCV(hist)
    
    ratio.Divide(hist, ref_hist, 1.0, 1.0)

    ratio.SetLineColor(i_hist.GetLineColor())
    ratio.SetLineWidth(i_hist.GetLineWidth())
    ratio.SetMarkerColor(i_hist.GetMarkerColor())
    ratio.SetMarkerStyle(i_hist.GetMarkerStyle())
    ratio.SetMarkerSize(i_hist.GetMarkerSize())


# def GetRatioMnvHists(i_data_mnv, i_mc_mnv_dict, ref_hist_name = "mctot"):
#     data_ratio_mnv = i_data_mnv.Clone()
#     ref_mnv = data_ratio_mnv.Clone()        
#     mc_ratio_mnv_dict = {}
#     for key in i_mc_mnv_dict:
#         tmp_ratio = i_mc_mnv_dict[key].Clone()
#         if ref_hist_name == key:
#             ref_mnv = tmp_ratio.Clone()
#         tmp_ratio.SetFillStyle(0)
#         mc_ratio_mnv_dict[key] = tmp_ratio
#     ref_mnv.ClearAllErrorBands()
#     if ref_hist = "data":
#         ref_mnv.AddMissingErrorBandsAndFillWithCV(mc_ratio_mnv_dict["mctot"])
#     else:
#         ref_mnv.AddMissingErrorBandsAndFillWithCV(data_ratio_mnv)

#     data_ratio_mnv.Divide(data_ratio_mnv, ref_mnv, 1.0, 1.0)
#     for key in mc_ratio_mnv_dict:
#         mc_ratio_mnv_dict[key].Divide(mc_ratio_mnv_dict[key], ref_mnv, 1.0, 1.0)

def SetTextsOnHists(hist):
    hist.SetTitle("Ra")

def DrawDataMCPlot1D(canvas, i_data_mnv, i_mc_mnv_dict, do_ratio = True, ):
    mnvPlotter = MnvPlotter(8)

    data_mnv = i_data_mnv.Clone()

    mc_mnv_dict = {}
    th1_ = {}
    for key in i_mc_mnv_dict:
        tmp_mc_mnv = i_mc_mnv_dict[key].Clone()
        mc_mnv_dict[key] = tmp_mc_mnv

    stack = THStack("stack","")
    first_mc = True
    for key in reversed(catsorder):
        if key not in i_mc_mnv_dict: continue
        tmp_mc_mnv = i_mc_mnv_dict[key].Clone()
        stack.Add(tmp_mc_mnv)
        if "mctot" not in i_mc_mnv_dict:
            if first_mc:
                mc_mnv_dict["mctot"] = tmp_mc_mnv.Clone()
                first_mc = False
                continue
            mc_mnv_dict["mctot"].Add(tmp_mc_mnv)

    if "mctot" not in i_mc_mnv_dict:
        mc_mnv_dict["mctot"] = MakeMCtotPretty(mc_mnv_dict["mctot"])


    data_stat, data_syst = GetDataStatAndSyst(data_mnv, do_pinkstat = False)
    mctot_cv, mctot_band = GetMCBandAndCV(mc_mnv_dict["mctot"])

    pad_max = GetPadMax(data_mnv, mc_mnv_dict["mctot"], including_errors = True)
    data_syst.SetMaximum(1.2 * pad_max)
    stack.SetMaximum(1.2 * pad_max)

    # Now make the ratio hists
    data_ratio_mnv, mc_ratio_mnv_dict = GetRatioMnvHists(data_mnv, mc_mnv_dict, ref_hist_name = "mctot")
    data_ratio_stat, data_ratio_syst = GetDataStatAndSyst(data_ratio_mnv, do_pinkstat = False)
    mctot_ratio_cv, mctot_ratio_band = GetMCBandAndCV(mc_ratio_mnv_dict["mctot"])

    canvas.cd()
    canvas.Draw()

    top = ROOT.TPad("hist", "hist", 0, ratio_frac, 1.0, 1.0)
    top.SetRightMargin(tmp_pad_rmarg)
    top.SetLeftMargin(pad_lmarg)
    top.SetTopMargin(tmp_topmarj)
    top.SetBottomMargin(0)
    top.SetFrameLineWidth(1)

    bottom = ROOT.TPad("Ratio", "Ratio", 0, 0, 1.0, ratio_frac)
    bottom.SetRightMargin(tmp_pad_rmarg)
    bottom.SetLeftMargin(pad_lmarg)
    bottom.SetBottomMargin(bottommarg)
    bottom.SetTopMargin(0)
    bottom.SetFrameLineWidth(1)
    
    top.Draw()
    bottom.Draw()

    bottomArea = bottom.GetWNDC() * bottom.GetHNDC()
    topArea = top.GetWNDC() * top.GetHNDC()
    areaScale = topArea / bottomArea

    padwidth = 1 - pad_lmarg - tmp_pad_rmarg
    padheight = 1 - tmp_topmarj - bottommarg

    top.cd()
    data_syst.Draw("PE1 E0 X0 9")
    stack.Draw("hist 9 same")
    data_stat.Draw("PE1 E0 X0 9 same") # TODO: add option for doing pink stat
    data_syst.Draw("PE1 E0 X0 9 same")
    data_syst.Draw("Axis same")

    prelim = AddPreliminary()
    prelim.SetTextAlign(11)
    prelim.DrawLatex(x1, y1 - 0.145, prelim_string)
    
    datapottext = AddDataPOTInfo()
    datapottext.SetTextAlign(11)
    datapottext.DrawLatex(x1, y1 - 0.045, datapot_string1)
    datapottext.DrawLatex(x1, y1 - 0.100, datapot_string2)
    chi2 = mnvPlotter.Chi2DataMC(mnv_data,mnv_mc,mnv_data.GetNbinsX())
    chi2text = AddChi2Info()
    # chi2text.SetTextAlign(11)
    # chi2text.DrawLatex(x1, y1 - 0.205, "#it{#chi^{2}} = %.02f"%chi2)
    # chi2text.DrawLatex(x1, y1 - 0.255, "#it{ndf} = %d"%mnv_data.GetNbinsX())
    chi2text.SetTextAlign(31)
    if do_chi2onplot:
        chi2text.DrawLatex(x2, y1 - 0.045, "#it{#chi^{2}} = %.02f"%chi2)
        chi2text.DrawLatex(x2, y1 - 0.100, "#it{ndf} = %d"%mnv_data.GetNbinsX())

    top.Modified()
    top.Update()

    bottom.cd()

    data_ratio_syst.SetTitle("")            
    # ratio.GetYaxis().SetTitle("Data / MC")
    data_ratio_syst.GetYaxis().SetTitle("Ratio")
    data_ratio_syst.GetYaxis().SetTitleFont(42)
    data_ratio_syst.GetYaxis().CenterTitle()
    data_ratio_syst.GetYaxis().SetTitleSize(axistitle_size * areaScale)
    data_ratio_syst.GetYaxis().SetTitleOffset(y_axistitle_offset / areaScale)
    data_ratio_syst.GetYaxis().SetLabelSize(axislabel_size * areaScale)
    data_ratio_syst.GetYaxis().SetNdivisions(505)

    # ratio.GetXaxis().SetTitle(vars_info[c_var]["title"])
    data_ratio_syst.GetXaxis().SetTitle(x_title)
    data_ratio_syst.GetXaxis().CenterTitle()
    data_ratio_syst.GetXaxis().SetTitleOffset(x_axistitle_offset)
    data_ratio_syst.GetXaxis().SetTitleSize(axistitle_size * areaScale)
    data_ratio_syst.GetXaxis().SetLabelSize(axislabel_size * areaScale)
    
    data_ratio_syst.Draw("9 E1 E0 X0")
    
    for key in mc_ratio_mnv_dict:
        if key == "mctot": continue
        mc_ratio_mnv_dict[key].Draw("9 HIST SAME")

    # Now do mc uncertainties
    mctot_ratio_band.Draw("9 E2 same ][")
    mctot_ratio_cv.Draw("9 hist same ][")
    data_ratio_syst.Draw("9 E1 E0 X0 same")
    data_ratio_stat.Draw("9 E1 E0 X0 same")
    data_ratio_syst.Draw("axis same")

    bottom.Modified()
    bottom.Update()
    canvas.cd()
    canvas.Modified()
    canvas.Update()
    return canvas

# def GetPanelProjHistList(i_mnv2d, projaxis="x", n_projbins = 0):
#     ret_list = []
#     hist = i_mnv2d.Clone()
#     if projaxis == "x":
#     if projaxis=="x":
#         if n_projbins == 0: n_projbins = hist.GetNbinsY()
        
#     elif projaxis == "y":
#         if n_projbins == 0: n_projbins = hist.GetNbinsX()
#     else:
#         print("ERROR: invalid projaxis %s, exiting"%(projaxis))
#         sys.exit(1)

#     linecolor = hist.GetLineColor()
#     linewidth = hist.GetLineWidth()
#     linestyle = hist.GetLineStyle()
#     fillcolor = hist.GetFillColor()
#     markercolor = hist.GetMarkerColor()
#     markerstyle = hist.GetMarkerStyle()
#     markersize = hist.GetMarkerSize()

#     for i in range(n_projbins):
#         tmp_proj_name = "%s_proj%sbin%s"%(hist.GetName(), projaxis, str(i))

#         if projaxis == "x":
#             tmp_proj = hist.ProjectionX(tmp_proj_name,i+1,i+1)#, "width")
#         else: # if projaxis == "y"
#             tmp_proj = hist.ProjectionY(tmp_proj_name,i+1,i+1)#, "width")
#         tmp_proj.SetLineColor(linecolor)
#         tmp_proj.SetLineWidth(linewidth)
#         tmp_proj.SetLineStyle(linestyle)
#         tmp_proj.SetFillColor(fillcolor)
#         tmp_proj.SetMarkerColor(markercolor)
#         tmp_proj.SetMarkerStyle(markerstyle)
#         tmp_proj.SetMarkerSize(markersize)

#         ret_list.append(tmp_proj)

#     return ret_list

# def GetTotalProjHist(i_mnvh2d, projaxis="x", varname = ""):
#     hist2d = i_mnv2d.Clone()

#     linecolor = hist2d.GetLineColor()
#     linewidth = hist2d.GetLineWidth()
#     linestyle = hist2d.GetLineStyle()
#     fillcolor = hist2d.GetFillColor()
#     markercolor = hist2d.GetMarkerColor()
#     markerstyle = hist2d.GetMarkerStyle()
#     markersize = hist2d.GetMarkerSize()
#     vartag = ""
#     if varname != "":
#         vartag = "_%s"%varname
#     proj_name = "%s_totalproj%s%s"%(hist2d.GetName(),projaxis.capitalize(),vartag)

#     if projaxis == "x":
#         totproj = hist2d.ProjectionX(proj_name, 0, -1)
#         # totproj.GetXaxis().SetTitle(hist2d.GetXaxis().GetTitle())


# def MakePlotDict(i_data_hist, i_mc_hist_dict):
#     plot_dict = {
#         "2D": {},
#         "1D": {
#             "data": {},
#             "mc": {}
#         },
#     }
#     if type(i_data_hist) == type(MnvH1D()):
#         plot_dict["1D"] = {
#             "data": {
#                 "mnv": {},
#                 "stat": {},
#                 "syst": {},
#                 "ratio_mnv": {},
#                 "ratio_stat": {},
#                 "ratio_syst": {},
#             },
#             "mc": {
#                 "mctot": {
#                     "mnv": {},
#                     "cv": {},
#                     "band": {},
#                     "ratio_mnv": {},
#                     "ratio_cv": {},
#                     "ratio_band": {},
#                 },
#                 "types": {
#                     "mnv": {},
#                     "cv": {},
#                     "band": {},
#                     "ratio_mnv": {},
#                     "ratio_cv": {},
#                     "ratio_band": {},
#                 },
#                 "FS": {
#                     "mnv": {},
#                     "cv": {},
#                     "band": {},
#                     "ratio_mnv": {},
#                     "ratio_cv": {},
#                     "ratio_band": {},                
#                 },
#             },
#             "misc": {
#                 "mnv": {},
#                 "cv": {},
#                 "band": {},
#                 "stat": {},
#                 "syst": {}
#                 "ratio_mnv": {},
#                 "ratio_cv": {},
#                 "ratio_band": {},
#             }
#         }



class PlotFactory:
    # This collects hists in a variable and puts them together for plots
    catsorder = [
        "mctot",
        "qelike",
        "qelike_proton",
        "qelike_neutron",
        "qelikenot",
        "chargedpion",
        "neutralpion",
        "other",
        "multipion",
        "other_np",
        0,
        1,
        2,
        3,
        4,
        8,
        11,
        12,
        13,
        14,
        18,
    ]
    catscolors = {
        "data":             ROOT.kBlack, 
        "qelike":           ROOT.kP10Blue,
        "qelikenot":        ROOT.kP10Red,
        "qelike_proton":    ROOT.TColor.GetColorDark(ROOT.kP10Blue),
        "qelike_neutron":   ROOT.TColor.GetColorBright(ROOT.kP10Blue),
        "chargedpion":      ROOT.kP10Yellow,
        "neutralpion":      ROOT.kP10Orange,
        "multipion":        ROOT.kP10Violet,
        "other":            ROOT.kP10Ash,
        "other_np":         ROOT.kP10Ash,
        "mctot":            ROOT.kP8Red,
        0:                  ROOT.kP8Red,     # total mc
        1:                  ROOT.kP8Blue,    # QE
        2:                  ROOT.kP8Orange,  # RES
        3:                  ROOT.kP8Pink,   # DIS
        4:                  ROOT.kP8Green,    # COH
        8:                  ROOT.TColor.GetColorBright(ROOT.kP8Azure),  # 2p2h
        11:                 ROOT.kP8Blue,    # QE
        12:                 ROOT.kP8Orange,  # RES
        13:                 ROOT.kP8Pink,   # DIS
        14:                 ROOT.kP8Green,    # COH
        18:                 ROOT.TColor.GetColorBright(ROOT.kP8Azure),  # 2p2h
    }
    catsfillstyle = {
        "data":             0, 
        "qelike":           1,
        "qelikenot":        3144,
        "qelike_proton":    1,
        "qelike_neutron":   1,
        "chargedpion":      3144,
        "neutralpion":      3144,
        "multipion":        3144,
        "other":            3144,
        "other_np":         3144,
        "mctot":            0,
        0:                  0,  # total mc
        1:                  1,  # QE
        2:                  1,  # RES
        3:                  1,  # DIS
        4:                  1,  # COH
        8:                  1,  # 2p2h
        11:                 3144,    # QE
        12:                 3144,   # RES
        13:                 3144,   # DIS
        14:                 3144,    # COH
        18:                 3144,  # 2p2h
    }
    global_catgroupstodo = [
        "normal",
        # "multipi",
        # "qelike_split",
    ]
    catgroups = {
        "normal": [
            "qelike",
            "chargedpion",
            "neutralpion",
            "other"
        ],
        "multipi": [
            "qelike",
            "chargedpion",
            "neutralpion",
            "mutlipion",
            "other_np",
        ],
        "qelike_split": [
            "qelike",
            "qelikeproton",
            "qelikeneutron"
            "chargedpion",
            "neutralpion",
            "other"
        ]
    }

    backgrounds = [
        "qelikenot",
        "chargedpion",
        "neutralpion",
        "other",
        "mutlipion",
        "other_np",
        # 10,
        11,
        12,
        13,
        14,
        18,
    ]
    signals = [
        "qelike",
        "qelike_proton",
        "qelike_neutron",
        "mctot",
        0,
        1,
        2,
        3,
        4,
        8,
    ]

    catslinestyle = {
        "data":             1, 
        "qelike":           1,
        "qelikenot":        1,
        "qelike_proton":    1,
        "qelike_neutron":   1,
        "chargedpion":      1,
        "neutralpion":      1,
        "multipion":        1,
        "other":            1,
        "other_np":         1,
        "mctot":            1,
        0:                  1,  # total mc
        1:                  1,  # QE
        2:                  1,  # RES
        3:                  1,  # DIS
        4:                  1,  # COH
        8:                  1,  # 2p2h
        11:                 2,    # QE
        12:                 2,   # RES
        13:                 2,   # DIS
        14:                 2,    # COH
        18:                 2,  # 2p2h
    }

    sigfillstyles = {
        "1D": 1001,
        "2D": 1001,
    }
    bkgfillstyles = {
        "1D": 3244,
        "2D": 3144,
    }

    catsnames = {
        "data":             "Data", 
        "qelike":           "QElike",
        "qelike_proton":    "QElike-proton",
        "qelike_neutron":   "QElike-neutron",
        "chargedpion":      "1#pi^{#pm}",
        "neutralpion":      "1#pi^{0}",
        "other":            "Other",
        "multipion":        "N#pi",
        "other_np":         "Other",
        "compdata":         "Data MnvTunev4.3.1",
        0:                  "MnvTune v2.0.1",  # total mc
        1:                  "QE",             # QE
        2:                  "RES",            # RES
        3:                  "DIS",            # DIS
        4:                  "COH",            # COH
        8:                  "2p2h",           # 2p2h
        11:                 "Bkg-QE",             # QE
        12:                 "Bkg-RES",            # RES
        13:                 "Bkg-DIS",            # DIS
        14:                 "Bkg-COH",            # COH
        18:                 "Bkg-2p2h",           # 2p2h
    }

    linewidths = {
        "1D": 1,
        "2D": 2,
    }
    data_marker_style = 20
    datamarkersizes = {
        "1D": 3.0,
        "2D": 2.0,
    }

    end_error_size = {
        12.0
    }

    # This maps how different things are paired between data in first entry and mc in second entry
    stagepairs = {
        "reco": ['reco', 'reco'],
        "bkgsub": ['bkgsub', 'sig'],
        "unfolded": ['unfolded', 'seltru'],
        "unfolditer": ['unfolditer', 'seltru'],
        "effcorr": ['effcorr', 'alltru'],
        "sigma": ['sigma','sigma'],
    }

    do_pinkstat = False
    prelim_string = "MINER#it{^{}#nu}A Work In Progress"
    datapot_string1 = "#it{POT Normalized}"
    datapot_string2 =  "#it{Data POT}: 1.12 #times 10^{21}"

    def __init__(self, i_varinfo_dict, i_hist_dict = {}, base_model="MnvTune v2.0.1", catgroup = ["normal"]):
    # def __init__(self, i_varinfo_dict, base_model="MnvTune v2.0.1", i_mc_dict = {}, i_data_dict = {}):
        # self.hist_dict = hist_dict
        if self.catsnames[0] != base_model: 
            self.catsnames[0] = base_model
        self.base_model = base_model

        # # vardict should have the histname version key, 
        self.varinfo_dict = i_varinfo_dict
        self.SetGlobalAxesTexts()
        # varinfo_dict = {
        #     "x": {
        #         "name": "EAvail",             # as named in the histname
        #         "tex_name": "E_{Avail}^{}",   # for title
        #         "units": "GeV",               # for title
        #         "bins": [],                   # maybe for bin range, necessary?
        #         "logx": False,                # log scales
        #         "logy": True,
        #     }
        #     "y": {
        #         "name": "ptmu",               # as named in the histname
        #         "tex_name": "p^{}_{T}^{}",    # for title
        #         "units": "GeV/c",             # for title
        #         "bins": [],
        #         "logx": False,
        #         "logy": False,
        #     }
        #     # Maybe leave th
        #     "z": { # If you have a 2D var, this will be the z axis naming
        #         "rate": "N_{events}",
        #         "sigma": ""
        #     }
        # }

        # This sets what group of cats you want to do, it will affect all plot factory instances
        self.SetCatGroupsToDo(catgroup)

        self.SetDataMCHists(i_hist_dict)

        self.MakeXSecPlotDict()
    

    def __contains__(self, attribute_name):
        # Helper to check if something is stored in this
        return hasattr(self, attribute_name)

    def SetCatGroupsToDo(self, i_catgroupstodo = ["normal"]):
        catgroupstodo = i_catgroupstodo
        if type(i_catgroupstodo) != list:
            catgroupstodo = [i_catgroupstodo]
        if "all" in catgroupstodo:
            print("PlotFactory: \tWill do all cat groups in printing")
            self.global_catgroupstodo = list(catgroups.keys())
        
        set_catgroupstodo = []
        for catgroup in catgroupstodo:
            if catgroup in self.global_catgroupstodo:
                print("PlotFactory: \tAdded %s to catgroups to do"%catgroup)            
                set_catgroupstodo.append(catgroup)
            else:
                print("PlotFactory: \tWARNING: asking for unconfigured catgroup %s."%(catgroup))
        if len(set_catgroupstodo) != 0:
            self.global_catgroupstodo = set_catgroupstodo

    def GetCatGroupsToDo(self):
        return self.global_catgroupstodo

    def SetDataMCHists(self, i_hist_dict):
        # This can have a mctot, cats, and types
        if "reconstructed" in i_hist_dict:
            self.mc_reco_dict = self.MakeCopyOfCatDict(i_hist_dict["reconstructed"], do_data = False)
        # The rest can have a mctot and types
        if "reconstructed_tuned" in i_hist_dict:
            self.mc_tuned_reco_dict = self.MakeCopyOfCatDict(i_hist_dict["reconstructed_tuned"], do_data = False)
        if "selected_truth" in i_hist_dict:
            self.mc_seltru_dict = self.MakeCopyOfCatDict(i_hist_dict["selected_truth"], do_data = False)
        if "selected_truth_tuned" in i_hist_dict:
            self.mc_tuned_seltru_dict = self.MakeCopyOfCatDict(i_hist_dict["selected_truth_tuned"], do_data = False)
        if "response_migration" in i_hist_dict:
            self.mc_migmatrix_dict = self.MakeCopyOfCatDict(i_hist_dict["response_migration"], do_data = False)
        if "response_tuned_migration" in i_hist_dict:
            self.mc_tuned_migmatrix_dict = self.MakeCopyOfCatDict(i_hist_dict["response_tuned_migration"], do_data = False)
        if "all_truth" in i_hist_dict:
            self.mc_alltru_dict = self.MakeCopyOfCatDict(i_hist_dict["all_truth"], do_data = False)
        if "all_truth_tuned" in i_hist_dict:
            self.mc_tuned_alltru_dict = self.MakeCopyOfCatDict(i_hist_dict["all_truth_tuned"], do_data = False)        
        if "sigmaMC" in i_hist_dict:
            self.mc_sigma_dict = self.MakeCopyOfCatDict(i_hist_dict["sigmaMC"], do_data = False, is_sigma = True)
        if "sigmaMC_tuned" in i_hist_dict:
            self.mc_tuned_sigma_dict = self.MakeCopyOfCatDict(i_hist_dict["sigmaMC_tuned"], do_data = False, is_sigma = True)

        if "reconstructed" in i_hist_dict:
            if "data" in i_hist_dict["reconstructed"]:
                self.data_reco = self.MakeCopyOfCatDict(i_hist_dict["reconstructed"])["data"][0]
        if "bkgsub" in i_hist_dict:
            if "data" in i_hist_dict["bkgsub"]:
                self.data_bkgsub = self.MakeCopyOfCatDict(i_hist_dict["bkgsub"])["data"][0]
        if "bkgsub_tuned" in i_hist_dict:
            if "data" in i_hist_dict["bkgsub_tuned"]:
                self.data_tuned_bkgsub = self.MakeCopyOfCatDict(i_hist_dict["bkgsub_tuned"])["data"][0]
        if "unfolded" in i_hist_dict:
            if "data" in i_hist_dict["unfolded"]:
                self.data_unfd = self.MakeCopyOfCatDict(i_hist_dict["unfolded"])["data"][0]
        if "unfolded_tuned" in i_hist_dict:
            if "data" in i_hist_dict["unfolded_tuned"]:
                self.data_tuned_unfolded = self.MakeCopyOfCatDict(i_hist_dict["unfolded_tuned"])["data"][0]
        
        data_unfolditer_list = []
        data_tuned_unfolditer_list = []
        for key in i_hist_dict:
            if "unfoldediter" not in key or "data" not in i_hist_dict[key]: continue
            tmp_unfolditer_hist = i_hist_dict[key]["data"][0].Clone()
            tmp_unfolditer_hist = self.SetHistAxisTexts(tmp_unfolditer_hist)
            tmp_unfolditer_hist = self.MakeHistPretty(tmp_unfolditer_hist, "data", 0)
            if "tuned" in key:
                data_tuned_unfolditer_list.append(tmp_unfolditer_hist)
                continue                
            data_unfolditer_list.append(tmp_unfolditer_hist)
        if len(data_unfolditer_list) != 0:
            self.data_unfolditer_list = data_unfolditer_list
        if len(data_tuned_unfolditer_list) != 0:
            self.data_tuned_unfolditer_list = data_tuned_unfolditer_list

        if "effcorr" in i_hist_dict:
            if "data" in i_hist_dict["unfolded_tuned"]:
                self.data_effcorr = self.MakeCopyOfCatDict(i_hist_dict["effcorr"])["data"][0]
        if "effcorr_tuned" in i_hist_dict:
            if "data" in i_hist_dict["unfolded_tuned"]:
                self.data_tuned_effcorr = self.MakeCopyOfCatDict(i_hist_dict["effcorr_tuned"])["data"][0]
        if "sigma" in i_hist_dict:
            if "data" in i_hist_dict["unfolded_tuned"]:
                self.data_sigma = self.MakeCopyOfCatDict(i_hist_dict["sigma"], is_sigma = True)["data"][0]
        if "sigma_tuned" in i_hist_dict:
            if "data" in i_hist_dict["unfolded_tuned"]:
                self.data_sigma_tuned = self.MakeCopyOfCatDict(i_hist_dict["sigma_tuned"], is_sigma = True)["data"][0]
        
        # tmp_efficiency = 0
        tmp_mc_efficiency_dict = {}
        tmp_mc_efficiency_dict = self.MakeEfficiencyDict()
        if len(list(tmp_mc_efficiency_dict.keys())) != 0:
            self.mc_efficiency_dict = tmp_mc_efficiency_dict


    # def MakeCopyOfMCCatDict(self, i_dict):
    def MakeCopyOfCatDict(self, i_dict, do_data = True, is_sigma = False):
        out_dict = {}
        tmp_catstodo = []
        for catgroup in self.global_catgroupstodo:
            tmp_catstodo += catgroup

        for a_cat in i_dict:
            # if a_cat not in tmp_catstodo and a_cat != "data": continue
            if a_cat == "data" and not do_data: continue
            if a_cat != "data" and do_data: continue
            if a_cat not in out_dict: out_dict[a_cat] = {}
            for b_type in i_dict[a_cat]:
                # tmp_hist = i_dict[a_cat][b_type].Clone()
                # MakeHistPretty(hist, a_cat, b_type)
                tmp_hist = i_dict[a_cat][b_type].Clone()
                tmp_hist = self.SetHistAxisTexts(tmp_hist, is_sigma)
                out_dict[a_cat][b_type] = self.MakeHistPretty(tmp_hist, a_cat, b_type)


        # for a_cat in i_dict:
        #     # if a_cat not in tmp_catstodo and a_cat != "data": continue
        #     if a_cat == "data" and not do_data: continue
        #     if a_cat != "data" and do_data: continue
        #     if a_cat not in out_dict: 
        #         out_dict[a_cat] = tmp_hist = i_dict[a_cat][0].Clone()
        #     if a_cat not in [mainsig, mainbkg]: continue
        #     for b_type in i_dict[a_cat]:
        #         if b_type == 0: continue
        #         if b_type in out_dict: 
        #             print("OUCH")
        #             sys.exit(1)
        #         out_dict[b_type] = i_dict[a_cat][b_type].Clone()
        if len(list(out_dict.keys())) == 0: 
            print("OUCH HERE")
            sys.exit(1)
        return out_dict
        
    def MakeEfficiencyDict(self):
        out_dict = {}
        if 'mc_seltru_dict' not in self or 'mc_alltru_dict' not in self:
            # return 0
            return out_dict
        for a_cat in self.mc_seltru_dict:
            if a_cat not in self.mc_alltru_dict: continue
            if a_cat not in out_dict: out_dict[a_cat] = {}
            for b_type in self.mc_seltru_dict[a_cat]:
                if b_type not in self.mc_alltru_dict[a_cat]: continue
                tmp_eff = self.mc_seltru_dict[a_cat][b_type].Clone(self.mc_seltru_dict[a_cat][b_type].GetName().replace("selected_truth", "efficiency"))
                tmp_eff.Divide(tmp_eff, self.mc_alltru_dict[a_cat][b_type])
                out_dict[a_cat][b_type] = tmp_eff.Clone()
        return out_dict



    # TODO
    def SetModelComp(self, i_dict):
        self.model_comp_dict = self.GetModelCompDict(i_dict)
    
    # TODO
    def GetModelCompDict(self, i_dict = {}):
        if 'model_comp_dict' in self: return self.model_comp_dict
        return i_dict

    def GetDataCompDict(self, i_dict = {}):
        self.data_comp_dict = self.GetDataCompDict(i_dict)

    # TODO
    def GetDataCompDict(self, i_dict = {}):
        if 'data_comp_dict' in self: return self.data_comp_dict
        return i_dict

    # TODO
    def DrawDataMCPlot1D(self, canvas, do_ratio_onplot = True, totproj = False):
        return
    def DrawDataMCPlot2D(self, canvas, projaxis = "both", do_ratio = False):
        return
    
    # TODO check that this is compatible with everything down stream, esp mctot and data => do later breaking up of these require things to be a certain way?
    def MakeHistPretty(self, i_hist, cat = "data", inttype = 0, ):
        # This gets hists into an initial state, later they'll may need specific things depending on what/how you're plotting
        hist = i_hist.Clone()
        cattype = inttype
        if inttype == 0:
            cattype = cat
        color = self.catscolors[cattype]
        darkcolor = ROOT.TColor.GetColorDark(self.catscolors[cat])
        fillstyle = self.catsfillstyle[cat]
        linestyle = 1 #catslinestyle[cat]
        datamarkerstyle = 20

        if type(i_hist) in [type(MnvH1D()), type(TH1D())]:
            linewidth = self.linewidths["1D"]
            data_marker_size = self.datamarkersizes["1D"]
            bkg_fillstyle = self.bkgfillstyles["1D"]
        else:
            linewidth = self.linewidths["2D"]
            data_marker_size = self.datamarkersizes["2D"]
            bkg_fillstyle = self.bkgfillstyles["2D"]
        
        hist.SetLineWidth(linewidth)

        # These require some special things
        if cat == "data":
            hist.SetMarkerColor(color)
            hist.SetMarkerStyle(datamarkerstyle)
            hist.SetMarkerSize(data_marker_size)
            # hist.SetLineWidth(linewidth)
            hist.SetFillStyle(0)
            return hist
        if cat == "mctot":
            hist.SetFillColor(color)
            hist.SetFillStyle(0)
            hist.SetLineColor(color)
            hist.SetLineStyle(1)
            # hist.SetLineWidth(linewidth)
            return hist
        if cat in ["qelike","qelike_proton","qelike_neutron"] or inttype < 10:
            hist.SetFillStyle(1001)
        else:
            hist.SetFillStyle(bkg_fillstyle)

        hist.SetFillColor(color)
        hist.SetLineColor(darkcolor)
        return hist

    def SetHistAxisTexts(self, i_hist, is_sigma = False):
        if 'varinfo_dict' not in self:
            print("PlotFactory: \tWARNING: called SetHistAxisTexts but no varinfo_dict set. Not doing anything...")
            return i_hist
        if 'x_title' not in self:
            self.SetGlobalAxesTexts()
        hist = i_hist.Clone()
        
        hist.GetXaxis().SetTitle(self.x_title)
        hist.GetXaxis().CenterTitle()
        if type(hist) in [type(MnvH1D()), type(TH1D())]:
            vert_axis_title = self.x_rate_title
            if is_sigma: 
                vert_axis_title = self.x_sigma_title
        else:
            vert_axis_title = self.y_title
            z_axis_title = self.xy_rate_title
            if is_sigma: 
                z_axis_title = self.xy_sigma_title
            hist.GetZaxis().SetTitle(z_axis_title)
            hist.GetZaxis().CenterTitle()        
        hist.GetYaxis().SetTitle(vert_axis_title)
        hist.GetYaxis().CenterTitle()
        return hist

    def SetGlobalAxesTexts(self):
        if 'varinfo_dict' not in self:
            print("PlotFactory: \tWARNING: called SetHistAxisTexts but no varinfo_dict set. Not doing anything...")
            return
        x_units = self.varinfo_dict["x"]["units"]
        x_texname = self.varinfo_dict["x"]["tex_name"]
        x_title = "%s #lower[-0.25]{#scale[0.6]{[%s]}}"%(x_units, x_texname)
        self.x_title = x_title

        # if the unit is a fraction (e.g. GeV/c) put parenths around it for the rate and sigma titles, unless it already has parenths
        if "/" in x_units and "(" not in x_units:
            x_units = "(%s)"%x_units
        self.x_rate_title = "N_{events}/^{}%s"%(x_units)
        self.x_sigma_title = "d#it{#sigma}/^{}d#it{%s}#lower[-0.15]{#scale[0.7]{ [cm^{2}/^{}%s/^{}Nucleon]}}"%(x_texname,x_units)

        if "y" in self.varinfo_dict:
            y_units = self.varinfo_dict["y"]["units"]
            y_texname = self.varinfo_dict["y"]["tex_name"]
            y_title = "%s #lower[-0.25]{#scale[0.6]{[%s]}}"%(y_units, y_texname)
            self.y_title = y_title

            if "/" in y_units and "(" not in y_units:
                y_units = "(%s)"%y_units
            self.y_rate_title = "N_{events}/^{}%s"%(y_units)
            self.y_sigma_title = "d#it{#sigma}/^{}d#it{%s}#lower[-0.15]{#scale[0.7]{ [cm^{2}/^{}%s/^{}Nucleon]}}"%(y_texname,y_units)
            
            self.xy_rate_title = "N_{events}/^{}%s/^{}%s"%(x_units, y_units)
            self.xy_sigma_title = "d^{2}#it{#sigma}/^{}d#it{%s}d#it{%s}#lower[-0.15]{#scale[0.7]{ (cm^{2}/(%s)/(%s)/Nucleon)}}"%(x_texname,y_texname,x_units,y_units)

    def CollectStageAttrNames(self):
        tmp_set_stage_name_dict = {}
        members = inspect.getmembers(self)
        for combo in self.stagepairs:
            tmp_data_attrnames = []
            tmp_mc_attrnames = []
            # tmp_data_tuned_attrnames = []
            # tmp_mc_tuned_attrnames = []
            for name, value in members:
                # attr = getattr(self, name)
                # if type(attr) == dict:
                #     bad_dict = False
                #     for key in attr:
                #         if type(attr[key]) not in [type(MnvH1D()), type(MnvH2D()), type(TH1D()), type(TH2D())]:
                #             bad_dict = True
                #             break
                #     if bad_dict:
                #         continue
                # if type(attr) not in [dict, type(MnvH1D()), type(MnvH2D()), type(TH1D()), type(TH2D())]:
                #     continue
                if self.stagepairs[combo][0] in name and 'data' in name:     
                    tmp_data_attrnames.append(name)
                if self.stagepairs[combo][1] in name and 'mc' in name:
                    tmp_mc_attrnames.append(name)
            if len(tmp_data_attrnames) == 0 or len(tmp_mc_attrnames) == 0:
                print("PlotFactory: \tWARNING couldn't find all hists for %s"%combo)
                continue
            tmp_set_stage_name_dict[combo] = [tmp_data_attrnames, tmp_mc_attrnames]
        self.set_stage_name_dict = tmp_set_stage_name_dict
    
    # TODO
    def MakeXSecPlotDict(self):
        plot_dict = {}
        if 'set_stage_name_dict' not in self:
            self.CollectStageAttrNames()
        print(self.set_stage_name_dict)
        for combo in self.set_stage_name_dict:
            for dataname in self.set_stage_name_dict[combo][0]:

                data1d = False
                data2d = False
                
                tmp_data_hist = getattr(self, dataname)
                if type(tmp_data_hist) in [type(MnvH1D()), type(TH1D())]: data1d = True
                elif type(tmp_data_hist) in [type(MnvH2D()), type(TH2D())]: data2d = True
                else:
                    # print("OUCH")
                    continue
                data_tag = "datauntuned"
                if 'tuned' in dataname: data_tag = "datatuned"

                for mcname in self.set_stage_name_dict[combo][1]:
                    mc1d = False
                    mc2d = False
                    tmp_mc_dict = getattr(self, mcname)
                    print(tmp_mc_dict.keys())
                    print(mcname)
                    # sys.exit(1)

                    if len(list(tmp_mc_dict.keys())) == 0: 
                        print("OUCH")
                        sys.exit(1)
                        continue
                    if type(tmp_mc_dict["qelike"][0]) in [type(MnvH1D()), type(TH1D())]: mc1d = True
                    elif type(tmp_mc_dict["qelike"][0]) in [type(MnvH2D()), type(TH2D())]: mc2d = True
                    else:
                        # print("OUCH")
                        continue
                    mc_tag = "mcuntuned"
                    if 'tuned' in mcname: mc_tag = "mctuned"
                    plot_tag = "%s_%s"%(data_tag, mc_tag)
                    print(plot_tag)
                    x_logx = self.varinfo_dict["x"]["logx"]
                    x_logy = self.varinfo_dict["x"]["logy"]
                    if data1d and mc1d:
                        tmp_data_hist.Print()
                        x_vert_title = self.x_rate_title
                        if 'sigma' in mcname:
                            x_vert_title = self.x_sigma_title
                        tmp_plot1d = Plot1D(
                            i_data_mnv = tmp_data_hist, 
                            i_mc_hist_dict = tmp_mc_dict, 
                            x_title = self.x_title,
                            x_vert_title = x_vert_title,
                            logx = x_logx, 
                            logy = x_logy, 
                            do_pinkstat = self.do_pinkstat, 
                            i_ref_hist = tmp_mc_dict["mctot"][0]
                        )
                        tmp_plot1d.SetTitles(self.x_title, x_vert_title)
                        if combo not in plot_dict: plot_dict[combo] = {}

                        if "%s_%s"%(data_tag, mc_tag) not in plot_dict[combo]: 
                            plot_dict[combo]["%s_%s"%(data_tag, mc_tag)] = tmp_plot1d
                    else:
                        print("OUCH no 1d or 2d")
                    if data2d and mc2d:
                        y_logx = self.varinfo_dict["y"]["logx"]
                        y_logy = self.varinfo_dict["y"]["logy"]
                        x_vert_title = self.x_rate_title
                        y_vert_title = self.y_rate_title
                        xy_vert_title = self.xy_rate_title
                        if 'sigma' in mcname: 
                            y_vert_title = self.y_sigma_title
                            x_vert_title = self.x_sigma_title
                            xy_vert_title = self.xy_sigma_title
                        tmp_plot2d = Plot2D(
                            i_data_mnv = tmp_data_hist, 
                            i_mc_hist_dict = tmp_mc_dict, 
                            x_title = self.x_title, 
                            y_title = self.y_title,
                            x_vert_title = x_vert_title,
                            y_vert_title = y_vert_title,
                            xy_vert_title = xy_vert_title,
                            x_logx = x_logx, 
                            x_logy = x_logy, 
                            y_logx = y_logx, 
                            y_logy = y_logy, 
                            do_pinkstat = self.do_pinkstat, 
                            i_ref_hist = tmp_mc_dict["mctot"][0]
                        )
                        # tmp_plot2d.SetTitles(self.x_title, self.y_title, x_vert_title, y_vert_title, xy_vert_title)
                        if combo not in plot_dict: plot_dict[combo] = {}
                        if "%s_%s"%(data_tag, mc_tag) not in plot_dict[combo]: 
                            plot_dict[combo]["%s_%s"%(data_tag, mc_tag)] = tmp_plot2d
        print(plot_dict.keys())
        if len(list(plot_dict.keys())) == 0:
            print("PlotFactory: \tWARNING could not find any combos in plots. Can't make plot dict." )
            return
        for combo in plot_dict:
            if len(plot_dict[combo]) == 0:
                print("PlotFactory: \tWARNING could not find any hists for %s. Skipping"%combo )
                # return
        print("PlotFactor \tMade Plot2d Dict")
        self.plot_dict = plot_dict

# def str_to_class(classname):
#     return getattr(sys.modules[__name__], classname)
class Plot2D:
    # TODO
    def __init__(self, i_data_mnv, i_mc_hist_dict, x_title = "xvar", y_title = "yvar", x_vert_title = "Counts/^{}unit^", y_vert_title = "Counts/^{}unit^", xy_vert_title = "Counts/^{}unit^{2}", x_logx = False, x_logy = False, y_logx = False, y_logy = False, do_pinkstat = False, i_ref_hist = 0):
        self.x_logx = x_logx
        self.x_logy = x_logy
        self.y_logx = y_logx
        self.y_logy = y_logy
        self.x_title = x_title
        self.y_title = y_title
        self.x_vert_title = x_vert_title
        self.y_vert_title = y_vert_title
        self.xy_vert_title = xy_vert_title

        self.n_xbins = i_data_mnv.GetNbinsX()
        self.n_ybins = i_data_mnv.GetNbinsY()

        self.do_pinkstat = do_pinkstat
        self.SetTitles(x_title, y_title, x_vert_title, y_vert_title, xy_vert_title)
        self.SetAllHists(i_data_mnv, i_mc_hist_dict, i_ref_hist, do_pinkstat)
        self.SetPanelPlot1DList()
        self.SetTotalProj1Ds()

    def SetTitles(self, x_title, y_title, x_vert_title, y_vert_title, xy_vert_title):
        self.x_title = x_title
        self.y_title = y_title
        self.x_vert_title = x_vert_title
        self.y_vert_title = y_vert_title
        self.xy_vert_title = xy_vert_title


    def __contains__(self, attribute_name):
        # Helper to check if something is stored in this
        return hasattr(self, attribute_name)
    
    # TODO
    def SetAllHists(self, i_data_mnv, i_mc_hist_dict, i_ref_hist, do_pinkstat):
        # This basically calls all the set hist things
        if type(i_data_mnv) != type(MnvH2D()):
            print("OUCH")
            sys.exit(1)
        for key in i_mc_hist_dict:
            if type(i_mc_hist_dict[key]) not in [type(MnvH2D()), type(TH2D())]:
                if type(i_mc_hist_dict[key][0]) not in [type(MnvH2D()), type(TH2D())]:
                    print("plot2dsetallhists OUCH HERE")
                    sys.exit(1)
        self.SetDataHist(i_data_mnv, do_pinkstat)
        self.SetMCHists(i_mc_hist_dict)

        # If you don't have a reference hist for the ratio, this picks one from what is here
        if i_ref_hist == 0:
            if 'mctot_mnv' in self:
                ref_hist = self.mctot_mnv.Clone()
                self.mctot_mnv.Print()
                # sys.exit(1)
            elif 'data_mnv' in self:
                ref_hist = self.data_mnv.Clone()
            else:
                return
        else:
            ref_hist = i_ref_hist.Clone()
        # ref_hist.Print()
        # sys.exit(1)
        self.ref_hist = ref_hist
        self.ref_hist_projx_list, self.ref_hist_projy_list = self.GetPanelProjHists(ref_hist)
        self.ref_hist_totalprojX, self.ref_hist_totalprojY = self.GetTotalProjHists(ref_hist)
        # self.SetRatioHists(ref_hist, do_pinkstat)

    def SetDataHist(self, i_data_mnv, do_pinkstat):
        # Store the data hists
        self.data_mnv = i_data_mnv.Clone()
        # self.data_syst, self.data_stat = self.GetDataSystAndStat(hist, do_pinkstat)
        self.data_mnv_projx_list, self.data_mnv_projy_list = self.GetPanelProjHists(self.data_mnv)
        self.data_mnv_totalprojX, self.data_mnv_totalprojY = self.GetTotalProjHists(self.data_mnv)
        # self.SetMaximum()

    def SetMCtotHist(self, hist):
        # Store these hists
        self.mctot_mnv = hist.Clone()
        # self.mctot_cv, self.mctot_band = self.GetMCtotCVAndBand(hist)
        # self.SetMaximum()

    def SetMCHists(self, mcdict):
        # This takes a dict of mc hists, if it finds what it needs, it will store them
        cats_dict = {}
        types_dict = {}

        mc_totalprojX_dict = {}
        mc_totalprojY_dict = {}
        # Temporarily store projections in here, it needs to be a list to iterate over when building the Plot1D's
        mc_projx_list = []
        mc_projy_list = []
        for a_cat in mcdict:
            if type( mcdict[a_cat]) == dict:
                if 0 not in mcdict[a_cat]: continue
                if a_cat not in cats_dict: cats_dict[a_cat] = mcdict[a_cat][0].Clone()
                if a_cat == "mctot":
                    self.mctot_mnv = mcdict[a_cat][0].Clone()
                    # self.SetMCtotHist(mcdict[a_cat][0].Clone())
                for b_type in mcdict[a_cat]:
                    # this is maybe temporary fix
                    if b_type == 0 or a_cat not in [mainsig, mainbkg]: continue
                    if b_type not in cats_dict: types_dict[b_type] = mcdict[a_cat][b_type].Clone()
            else:
                # the order of these the dict matters so these operations work
                tmp_hist = mcdict[a_cat].Clone()
                if a_cat == 0:
                    self.mctot_mnv = mcdict[a_cat].Clone()
                    # self.SetMCtotHist(mcdict[a_cat][0].Clone())
                if type(a_cat) == str:
                    cats_dict[a_cat] = tmp_hist
                if type(a_cat) == int:
                    types_dict[a_cat] = tmp_hist
        for a_cat in cats_dict:
            tmp_hist = cats_dict[a_cat].Clone()
            mc_totalprojX_dict[a_cat], mc_totalprojY_dict[a_cat] = self.GetTotalProjHists(tmp_hist)

            tmp_projx_list, tmp_projy_list = self.GetPanelProjHists(tmp_hist)
            if len(mc_projx_list) != len(tmp_projx_list):
                for i in range(len(tmp_projx_list)):
                    tmp_proj_dict = {a_cat: tmp_projx_list[i]}
                    mc_projx_list.append(tmp_proj_dict)
            else:
                for i in range(len(tmp_projx_list)):
                    mc_projx_list[i][a_cat] = tmp_projx_list[i]
            if len(mc_projy_list) != len(tmp_projy_list):
                for i in range(len(tmp_projy_list)):
                    tmp_proj_dict = {a_cat: tmp_projy_list[i]}
                    mc_projy_list.append(tmp_proj_dict)
            else:
                for i in range(len(tmp_projy_list)):
                    mc_projy_list[i][a_cat] = tmp_projy_list[i]
        for a_type in types_dict:
            tmp_hist = types_dict[a_type].Clone()
            mc_totalprojX_dict[a_type], mc_totalprojY_dict[a_type] = self.GetTotalProjHists(tmp_hist)

            tmp_projx_list, tmp_projy_list = self.GetPanelProjHists(tmp_hist)
            if len(mc_projx_list) != len(tmp_projx_list):
                for i in range(len(tmp_projx_list)):
                    tmp_proj_dict = {a_type: tmp_projx_list[i]}
                    mc_projx_list.append(tmp_proj_dict)
            else:
                for i in range(len(tmp_projx_list)):
                    mc_projx_list[i][a_type] = tmp_projx_list[i]
            if len(mc_projy_list) != len(tmp_projy_list):
                for i in range(len(tmp_projy_list)):
                    tmp_proj_dict = {a_type: tmp_projy_list[i]}
                    mc_projy_list.append(tmp_proj_dict)
            else:
                for i in range(len(tmp_projy_list)):
                    mc_projy_list[i][a_type] = tmp_projy_list[i]
        self.mc_projx_list = mc_projx_list
        self.mc_projy_list = mc_projy_list
        self.mc_totalprojX_dict = mc_totalprojX_dict
        self.mc_totalprojY_dict = mc_totalprojY_dict

        self.SetMCCatsHists(cats_dict)
        self.SetMCTypeHists(types_dict)
        # self.SetMaximum()
    
    def SetMCTypeHists(self, typesdict, do_stack = True):
        # If you have hists by types, this will store them, if you don't want to build a stack, say that
        types_hists_dict = {}
        for key in typesdict:
            if type(key) != int: continue
            tmp_hist = typesdict[key].Clone()
            types_hists_dict[key] = tmp_hist
        self.types_hists_dict = types_hists_dict

        # Build dicts for the bkg or sig, need to check there's actually things there
        types_sighists_dict = {}
        types_bkghists_dict = {}
        badsig = False
        badbkg = False
        for key in signalcats:
            if key in types_hists_dict:
                types_sighists_dict[key] = types_hists_dict[key].Clone()
            else: 
                badsig = True
                break
        if not badsig: self.types_sighists_dict = types_sighists_dict

        for key in backgroundcats:
            if key in types_hists_dict:
                types_bkghists_dict[key] = types_hists_dict[key].Clone()
            else: 
                badbkg = True
                break
        if not badbkg: self.types_bkghists_dict = types_bkghists_dict

    def SetMCCatsHists(self, catsdict, do_stack = True):
        # If you have hists by category, this will store them, if you don't want to build a stack, say that
        cats_hists_dict = {}
        for key in catsdict:
            if type(key) != str: continue
            cats_hists_dict[key] = catsdict[key].Clone()
        self.cats_hists_dict = cats_hists_dict

        # Build dicts for the bkg or sig, need to check there's actually things there
        cats_sighists_dict = {}
        cats_bkghists_dict = {}
        badsig = False
        badbkg = False
        for key in signalcats:
            if key in cats_hists_dict:
                cats_sighists_dict[key] = cats_hists_dict[key].Clone()
            else: 
                badsig = True
                break
        if not badsig: self.cats_sighists_dict = cats_sighists_dict
        for key in backgroundcats:
            if key in cats_hists_dict:
                cats_bkghists_dict[key] = cats_hists_dict[key].Clone()
            else: 
                badbkg = True
                break
        if not badbkg: self.cats_bkghists_dict = cats_bkghists_dict

    def GetPanelProjHists(self, i_hist):
        x_hist_list = []
        y_hist_list = []
        x_rangestring_list = []
        y_rangestring_list = []
        x_binwidth_list = []
        y_binwidth_list = []
        hist = i_hist.Clone()
        hist.Scale(1.0, "width")
        for i in range(1, hist.GetNbinsY()+1):
            tmp_proj_name = "%s_projX_%s"%(hist.GetName().replace("h2D", "h"), str(i))
            tmp_proj = hist.ProjectionX(tmp_proj_name, i, i)

            tmp_proj.GetXaxis().SetTitle(self.x_title)
            tmp_proj.GetXaxis().CenterTitle()
            tmp_proj.GetYaxis().SetTitle(self.xy_vert_title)
            tmp_proj.GetYaxis().CenterTitle()

            x_hist_list.append(tmp_proj)
            upedge = hist.GetYaxis().GetBinUpEdge(i)
            loedge = hist.GetYaxis().GetBinLowEdge(i)
            tmp_range_string = "{min} < {var} < {max}".format(
                min = round(loedge,4), 
                var = self.y_title, 
                max = round(upedge,4)
            )
            x_rangestring_list.append(tmp_range_string)
            x_binwidth_list.append(upedge - loedge)

        for i in range(1, hist.GetNbinsX()+1):
            tmp_proj_name = "%s_projY_%s"%(hist.GetName().replace("h2D", "h"), str(i))
            tmp_proj = hist.ProjectionY(tmp_proj_name, i, i)
            y_hist_list.append(tmp_proj)

            tmp_proj.GetXaxis().SetTitle(self.y_title)
            tmp_proj.GetXaxis().CenterTitle()
            tmp_proj.GetYaxis().SetTitle(self.xy_vert_title)
            tmp_proj.GetYaxis().CenterTitle()

            upedge = hist.GetXaxis().GetBinUpEdge(i)
            loedge = hist.GetXaxis().GetBinLowEdge(i)
            tmp_range_string = "{min} < {var} < {max}".format(
                min = round(loedge,4), 
                var = self.x_title, 
                max = round(upedge,4)
            )
            y_rangestring_list.append(tmp_range_string)
            y_binwidth_list.append(upedge - loedge)
        if 'x_rangestring_list' not in self:
            self.x_rangestring_list = x_rangestring_list
        if 'y_rangestring_list' not in self:
            self.y_rangestring_list = y_rangestring_list
        if 'x_binwidth_list' not in self:
            self.x_binwidth_list = x_binwidth_list
        if 'y_binwidth_list' not in self:
            self.y_binwidth_list = y_binwidth_list
        return x_hist_list, y_hist_list

    def GetTotalProjHists(self, hist):
        tmp_projx = hist.ProjectionX("%s_TotalProjX_%s"%(hist.GetName().replace("h2D","h"), self.x_title), 0, -1)
        tmp_projx.GetXaxis().SetTitle(self.y_title)
        tmp_projx.GetXaxis().CenterTitle()
        tmp_projx.GetYaxis().SetTitle(self.y_vert_title)
        tmp_projx.GetYaxis().CenterTitle()

        tmp_projy = hist.ProjectionY("%s_TotalProjY_%s"%(hist.GetName().replace("h2D","h"), self.y_title), 0, -1)
        tmp_projx.GetXaxis().SetTitle(self.x_title)
        tmp_projx.GetXaxis().CenterTitle()
        tmp_projx.GetYaxis().SetTitle(self.x_vert_title)
        tmp_projx.GetYaxis().CenterTitle()
        return tmp_projx, tmp_projy

    def SetPanelPlot1DList(self):
        print("Plot2D: \tMaking Panel projection Plot1Ds")

        panel_plot1d_projy_list = []
        panel_plot1d_projx_list = []

        y_global_max = 0.0
        for i in range(self.n_xbins):
            tmp_projbin_data_mnv = self.data_mnv_projy_list[i]
            tmp_projbin_mc_hist_dict = self.mc_projy_list[i]
            tmp_projbin_ref_hist = self.ref_hist_projy_list[i]
            tmp_plot1d = Plot1D(
                i_data_mnv = tmp_projbin_data_mnv, 
                i_mc_hist_dict = tmp_projbin_mc_hist_dict, 
                # x_title = self.x_title,
                # y_title = self.y_title,
                logx = self.y_logx, 
                logy = self.y_logy, 
                do_pinkstat = self.do_pinkstat, 
                i_ref_hist = tmp_projbin_ref_hist
            )
            tmp_pad_max = tmp_plot1d.GetPadMax()
            y_global_max = max(tmp_pad_max, y_global_max)
            panel_plot1d_projy_list.append(tmp_plot1d)
        for plot in panel_plot1d_projy_list:
            tmp_pad_max = plot.GetPadMax()
            tmp_pad_scale = 1.0
            if tmp_pad_max > 0:
                tmp_pad_scale = eval('{:.{p}g}'.format(y_global_max / tmp_pad_max, p=3))
            plot.Scale(tmp_pad_scale, multip = True)

        x_global_max = 0.0
        for i in range(self.n_ybins):
            tmp_projbin_data_mnv = self.data_mnv_projx_list[i]
            tmp_projbin_mc_hist_dict = self.mc_projx_list[i]
            tmp_projbin_ref_hist = self.ref_hist_projx_list[i]

            tmp_plot1d = Plot1D(
                i_data_mnv = tmp_projbin_data_mnv, 
                i_mc_hist_dict = tmp_projbin_mc_hist_dict, 
                # x_title = self.x_title,
                # y_title = self.y_title,
                logx = self.y_logx, 
                logy = self.y_logy, 
                do_pinkstat = self.do_pinkstat, 
                i_ref_hist = tmp_projbin_ref_hist
            )
            tmp_pad_max = tmp_plot1d.GetPadMax()
            x_global_max = max(tmp_pad_max, x_global_max)
            panel_plot1d_projx_list.append(tmp_plot1d)
        for plot in panel_plot1d_projx_list:
            tmp_pad_max = plot.GetPadMax()
            tmp_pad_scale = 1.0
            if tmp_pad_max > 0:
                tmp_pad_scale = eval('{:.{p}g}'.format(x_global_max / tmp_pad_max, p=3))
            plot.Scale(tmp_pad_scale, multip = True)
            plot.SetMaximum()

        self.panel_plot1d_projy_list = panel_plot1d_projy_list
        self.panel_plot1d_projx_list = panel_plot1d_projx_list

    def SetTotalProj1Ds(self):
        print("Plot2D: \tMaking Total projection Plot1Ds")
        plot1d_totalprojX = Plot1D(self.data_mnv_totalprojX, self.mc_totalprojX_dict, self.x_logx, self.x_logy, self.ref_hist_totalprojX)
        plot1d_totalprojY = Plot1D(self.data_mnv_totalprojY, self.mc_totalprojY_dict, self.y_logx, self.y_logy, self.ref_hist_totalprojY)

        plot1d_totalprojX.Scale(1.0, "width")
        plot1d_totalprojY.Scale(1.0, "width")

        self.plot1d_totalprojX = plot1d_totalprojX
        self.plot1d_totalprojY = plot1d_totalprojY

    # TODO
    def DrawHistPanelsOnCanvas(self):
        return

    # TODO
    def DrawRatioPanelsOnCanvas(self):
        return

    # TODO
    def DrawErrorSummaryOnCanvas(self):
        return

    # TODO
    def CopyHistStyle(self, i_hist, reference_hist):
        return
    def GetHistStyle(self, i_hist):
        return

    # TODO
    def DrawTotalProjOnCanvas(self, do_ratio = True):
        return


class Plot1D:
    def __init__(self, i_data_mnv, i_mc_hist_dict, x_title = "xvar", x_vert_title = "Counts / unit", logx = False, logy = False, do_pinkstat = False, i_ref_hist = False):
        self.logx = logx
        self.logy = logy
        self.SetAllHists(i_data_mnv, i_mc_hist_dict, i_ref_hist, do_pinkstat)

    def __contains__(self, attribute_name):
        # Helper to check if something is stored in this
        return hasattr(self, attribute_name)

    def SetTitles(self, x_title, x_vert_title):
        self.x_title = x_title
        self.y_title = x_vert_title

    def SetDataHist(self, hist, do_pinkstat = False):
        # Store the data hists
        self.data_mnv = hist.Clone()
        self.data_syst, self.data_stat = self.GetDataSystAndStat(hist, do_pinkstat)        
        # self.SetMaximum()

    def GetDataSystAndStat(self, i_mnv, do_pinkstat):
        # Get the data and stat hist, build them if you haven't yet, pink_stat is an option to draw a pink box instead of separate bars for stat 
        if 'data_syst' in self and 'data_stat' in self:
            return self.data_syst, self.data_stat

        hist = i_mnv.Clone()
        data_syst = hist.GetCVHistoWithError()
        data_syst.SetMarkerColor(hist.GetMarkerColor())
        data_syst.SetLineWidth(hist.GetLineWidth())
        data_syst.SetLineColor(hist.GetLineColor())
        data_syst.SetMarkerSize(hist.GetMarkerSize())
        data_syst.SetMarkerStyle(hist.GetMarkerStyle())

        data_stat = hist.GetCVHistoWithError()
        data_stat.SetMarkerColor(hist.GetMarkerColor())
        # end_error_size
        data_stat.SetLineWidth(hist.GetLineWidth())
        data_stat.SetLineColor(hist.GetLineColor())
        if do_pinkstat:
            data_stat.SetLineWidth(4)
            data_stat.SetLineColorAlpha(ROOT.kPink, band_alphalevel) #mnvh.GetLineColor())
            data_stat.SetFillColorAlpha(ROOT.kPink, band_alphalevel)
        data_stat.SetMarkerSize(0)
        data_stat.SetMarkerStyle(1)

        return data_syst, data_stat

    def SetMCtotHist(self, hist):
        # Store these hists
        self.mctot_mnv = hist.Clone()
        self.mctot_cv, self.mctot_band = self.GetMCtotCVAndBand(hist)
        # self.SetMaximum()

    def GetMCtotCVAndBand(self, i_mnv):
        # Get the mctot, and build the cv and band versions of the hist
        if 'mctot_cv' in self and 'mctot_band' in self:
            return self.mctot_cv, self.mctot_band

        hist = i_mnv.Clone()
        mctot_cv = hist.GetCVHistoWithError(True, False)
        mctot_band = hist.GetCVHistoWithError(True, False)

        # TODO: not sure what to do about color here, few choices there if needed
        mctot_cv.SetFillColor(0)
        mctot_cv.SetLineColor(hist.GetFillColor())
        # mctot_cv.SetLineColor(catscolors[0])
        # mctot_cv.SetLineColor(hist.GetLineColor())
        
        mctot_band.SetFillStyle(1001)
        mctot_band.SetFillColorAlpha(hist.GetFillColor(), band_alphalevel)
        # mctot_band.SetFillColorAlpha(catscolors[0], band_alphalevel)
        # mctot_band.SetFillColorAlpha(hist.GetLineColor(), band_alphalevel)
        mctot_band.SetLineColor(hist.GetFillColor())
        # mctot_band.SetLineColor(catscolors[0])
        # mctot_band.SetLineColor(hist.GetLineColor())
        mctot_band.SetMarkerStyle(0)
        return mctot_cv, mctot_band
    
    def SetMCTypeHists(self, typesdict, do_stack = True):
        # If you have hists by types, this will store them, if you don't want to build a stack, say that
        types_hists_dict = {}
        for key in typesdict:
            if type(key) != int: continue
            types_hists_dict[key] = typesdict[key].Clone()
        self.types_hists_dict = types_hists_dict

        # Build dicts for the bkg or sig, need to check there's actually things there
        types_sighists_dict = {}
        types_bkghists_dict = {}
        badsig = False
        badbkg = False
        for key in signalcats:
            if key in types_hists_dict:
                types_sighists_dict[key] = types_hists_dict[key].Clone()
            else: 
                badsig = True
                break
        if not badsig: self.types_sighists_dict = types_sighists_dict

        for key in backgroundcats:
            if key in types_hists_dict:
                types_bkghists_dict[key] = types_hists_dict[key].Clone()
            else: 
                badbkg = True
                break
        if not badbkg: self.types_bkghists_dict = types_bkghists_dict

        if do_stack:
            self.types_tot_stack = THStack("types_tot_stack","")
            for key in reversed(list(types_hists_dict.keys())):
                self.types_tot_stack.Add(types_hists_dict[key].Clone())
            if 'types_sighists_dict' in self:
                self.types_sig_stack = THStack("types_sig_stack","")
                for key in reversed(signalcats):
                    self.types_sig_stack.Add(types_hists_dict[key].Clone())
            if 'types_bkghists_dict' in self:
                self.types_bkg_stack = THStack("types_bkg_stack","")
                for key in reversed(signalcats):
                    self.types_bkg_stack.Add(types_hists_dict[key].Clone())
            # self.SetMaximum()

    def SetMCCatsHists(self, catsdict, do_stack = True):
        # If you have hists by category, this will store them, if you don't want to build a stack, say that
        cats_hists_dict = {}
        for key in catsdict:
            if type(key) != str: continue
            cats_hists_dict[key] = catsdict[key].Clone()
        self.cats_hists_dict = cats_hists_dict

        # Build dicts for the bkg or sig, need to check there's actually things there
        cats_sighists_dict = {}
        cats_bkghists_dict = {}
        badsig = False
        badbkg = False
        for key in signalcats:
            if key in cats_hists_dict:
                cats_sighists_dict[key] = cats_hists_dict[key].Clone()
            else: 
                badsig = True
                break
        if not badsig: self.cats_sighists_dict = cats_sighists_dict
        for key in backgroundcats:
            if key in cats_hists_dict:
                cats_bkghists_dict[key] = cats_hists_dict[key].Clone()
            else: 
                badbkg = True
                break
        if not badbkg: self.cats_bkghists_dict = cats_bkghists_dict

        if do_stack:
            cats_tot_stack = THStack("cats_tot_stack","")
            for key in reversed(list(cats_hists_dict.keys())):
                cats_tot_stack.Add(cats_hists_dict[key].Clone())
            self.cats_tot_stack = cats_tot_stack
            if 'cats_sighists_dict' in self:
                cats_sig_stack = THStack("cats_sig_stack","")
                for key in reversed(signalcats):
                    cats_sig_stack.Add(cats_hists_dict[key].Clone())
                self.cats_sig_stack = cats_sig_stack
            if 'cats_bkghists_dict' in self:
                cats_bkg_stack = THStack("cats_bkg_stack","")
                for key in reversed(backgroundcats):
                    cats_bkg_stack.Add(cats_hists_dict[key].Clone())
                self.cats_bkg_stack = cats_bkg_stack
        # TODO: maybe if you don't have mctot set, you could build one here?
        # self.SetMaximum()

    def SetMCHists(self, mcdict):
        # This takes a dict of mc hists, if it finds what it needs, it will store them
        cats_dict = {}
        types_dict = {}

        for a_cat in mcdict:
            if type( mcdict[a_cat]) == dict:
                if 0 not in mcdict[a_cat]: continue
                if a_cat not in cats_dict: cats_dict[a_cat] = mcdict[a_cat][0].Clone()
                if a_cat == "mctot":
                    self.SetMCtotHist(mcdict[a_cat][0].Clone())
                for b_type in mcdict[a_cat]:
                    # this is maybe temporary fix
                    if b_type == 0 or a_cat not in [mainsig, mainbkg]: continue
                    if b_type not in cats_dict: types_dict[b_type] = mcdict[a_cat][b_type].Clone()
            else:
                # the order of these the dict matters so these operations work
                tmp_hist = mcdict[a_cat].Clone()
                if a_cat == 0:
                    self.SetMCtotHist(tmp_hist)
                if type(a_cat) == str:
                    cats_dict[a_cat] = tmp_hist
                if type(a_cat) == int:
                    types_dict[a_cat] = tmp_hist
        
        self.SetMCCatsHists(cats_dict)
        self.SetMCTypeHists(types_dict)
        # self.SetMaximum()

    def SetMiscHists(self, name, histdict, draw_opt = "9 hist ]["):
        if 'misc_hist_dict' in self:
            misc_hist_dict = self.misc_hist_dict
        else:
            misc_hist_dict = {}
        
        for key in hist_dict:
            if key in misc_hist_dict: print("WARNING, overwriting misc hist %s"%key)
            misc_hist_dict[key] = histdict.Clone()

        self.misc_hist_dict = misc_hist_dict

        if 'misc_hist_dict' in self:
            misc_hist_dict = self.misc_hist_dict
        else:
            misc_hist_dict = {}
        
        for key in hist_dict:
            if key in misc_hist_dict: print("WARNING, overwriting misc hist %s"%key)
            misc_hist_dict[key] = histdict.Clone()
        self.misc_hist_dict = misc_hist_dict
        self.misc_draw_opt = draw_opt
        # self.SetMaximum()

    def GetPadMax(self):
        # Get the biggest thing in the pad, including errors
        pad_max = 0.0
        if 'data_syst' in self:
            data_max = max([self.data_syst.GetBinContent(i) + self.data_syst.GetBinError(i) for i in range(1, self.data_syst.GetNbinsX()+1)])
            if data_max > pad_max: pad_max = data_max
        elif 'data_stat' in self:
            data_max = max([self.data_stat.GetBinContent(i) + self.data_stat.GetBinError(i) for i in range(1, self.data_stat.GetNbinsX()+1)])
            if data_max > pad_max: pad_max = data_max
        if 'mctot_cv' in self:
            mc_max = max([self.mctot_cv.GetBinContent(i) + self.mctot_cv.GetBinError(i) for i in range(1, self.mctot_cv.GetNbinsX()+1)])
            if mc_max > pad_max: pad_max = mc_max
        # if you don't have a total mc, check everything else
        elif 'types_tot_stack' in self:
            types_max = self.types_tot_stack.GetMaximum()
            if types_max > pad_max: pad_max = types_max
        elif 'cats_tot_stack' in self:
            cats_max = self.cats_tot_stack.GetMaximum()
            if cats_max > pad_max: pad_max = cats_max
        elif 'misc_hist_dict' in self:
            misc_max = -1.0
            for key in misc_hist_dict:
                tmp_hist = misc_hist_dict[key]
                tmp_misc_max = max([self.tmp_hist.GetBinContent(i) + self.tmp_hist.GetBinError(i) for i in range(1, self.mcttmp_histot_cv.GetNbinsX()+1)])
                misc_max = max(misc_max, tmp_misc_max)
            if misc_max > pad_max: pad_max = misc_max
        # if there's nothing in the pad, set it to 1 so things don't freak out
        if pad_max == 0.0: pad_max = 1.0
        return pad_max
    
    def Scale(self, value = -1.0, opts = "", multip = False, onemember = ''):
        # scale hists by a value, 
        # if multip, store a multiplier that is used as a scale to print on it
        # opt is for scale opts from root e.g., "width"
        # setting onemember will scall just one thing, hope you get the name right
        if value < 0: return
        pad_scale = value
        if multip and onemember == '':
            multip_string = "#times {:g}".format(float('{:.{p}g}'.format(pad_scale, p=2)))
            self.scale_string = multip_string
        if value == 1.0:
            return
        members = inspect.getmembers(self)
        foundonemember = False
        for name, value in members:
            if "ratio" in name:
                continue
            if onemember != '':
                if name != onemember:
                    continue
                else:
                    foundonemember = True
            if type(getattr(self, name)) == dict:
                # tmp_baddict = False
                for key in getattr(self, name):
                    if type(getattr(self, name)[key]) not in [type(MnvH1D()), type(MnvH2D()), type(TH1D()), type(TH2D()),]:
                        break
                    getattr(self, name)[key].Scale(pad_scale, opts)
                if foundonemember: break
                continue
            if type(getattr(self, name)) not in [type(MnvH1D()), type(MnvH2D()), type(TH1D()), type(TH2D()),]:
                if foundonemember: break
                continue
            getattr(self, name).Scale(pad_scale, opts)
            if foundonemember: break
        if not foundonemember and onemember != '':
            print("Plot1D: WARNING couldn't find single member %s"%onemember)
        else:
            self.SetMaximum()

    def SetMaximum(self, value = -1.0, headroom_scale = -1.0):
        # This sets the maximums for everything

        # This gives some headroom above the hist, if it's already set, just use that one
        if 'headroom_scale' in self:
            headroom_scale = self.headroom_scale
        elif headroom_scale < 0.:
            headroom_scale = 1.2
        # If there's a log axis, give yourself a little more headroom
        elif self.logy:
            headroom_scale = 2.0
        # if it's set by the user, set that one so it sticks for any other changes made
        else:
            self.headroom_scale = headroom_scale
        # Get the max for the pad from the user set, if not use the calculated one
        padmax = value
        if value < 0.0:
            padmax = self.GetPadMax()
        self.padmax = padmax
        
        # Set the maxes of all the hists
        members = inspect.getmembers(self)
        for name, value in members:
            if type(getattr(self, name))  in [type(MnvH1D()), type(MnvH2D()), type(TH1D()), type(TH2D()), type(THStack())]:
                getattr(self, name).SetMaximum(headroom_scale * padmax)
            if type(getattr(self, name)) == dict:
                for key in getattr(self, name):
                    if type(getattr(self, name)[key]) not in [type(MnvH1D()), type(MnvH2D()), type(TH1D()), type(TH2D()),]:
                        break
                    getattr(self, name)[key].SetMaximum(headroom_scale * padmax)

        # if 'data_mnv' in self:
        #     data_syst.SetMaximum(headroom_scale * padmax)
        #     data_stat.SetMaximum(headroom_scale * padmax)
        # if 'mctot_cv' in self:
        #     mctot_cv.SetMaximum(headroom_scale * padmax)
        # if 'types_tot_stack' in self:
        #     types_tot_stack.SetMaximum(headroom_scale * padmax)
        # if 'cats_tot_stack' in self:
        #     cats_tot_stack.SetMaximum(headroom_scale * padmax)

    def SetRatioHists(self, i_ref_hist, do_pinkstat = False):
        # This builds all the ratio hists you need
        i_ref_hist.Print()
        sys.exit(1)
        if 'ref_hist' not in self:
            self.ref_hist = i_ref_hist.Clone()

        ref_hist = self.ref_hist.Clone()

        print("Plot1D:\t ref_hist set to %s"%ref_hist.GetName())        
        # sys.exit(1)
        ismnv = False
        if type(ref_hist) in [type(MnvH1D()), type(MnvH2D())]:
            print("Plot1D:\tSetRatioHists: ref_hist is Mnv")
            ismnv = True
            ref_hist.ClearAllErrorBands()

        # Make total data ratios (this is the main event)
        if 'data_mnv' in self:
            data_ratio_mnv = self.data_mnv.Clone(self.data_mnv.GetName()+"_ratioto_"+ref_hist.GetName())
            if type(ref_hist) in [type(MnvH1D()), type(MnvH2D())]:
                ref_hist.AddMissingErrorBandsAndFillWithCV(data_ratio_mnv)
            data_ratio_mnv.Divide(data_ratio_mnv, ref_hist, 1.0, 1.0)

            self.data_ratio_mnv = data_ratio_mnv.Clone()
            data_ratio_syst, data_ratio_stat = self.GetDataSystAndStat(data_ratio_mnv, do_pinkstat)
            data_ratio_syst.SetMaximum(2.0)
            tmp_max_bin = data_ratio_syst.GetMaximumBin()
            tmp_max = data_ratio_syst.GetBinContent(tmp_max_bin) + data_ratio_syst.GetBinError(tmp_max_bin)
            # This will likely be the basis of the plot, so make the max right, in increments of 0.5
            if tmp_max > 2.0:
                data_ratio_syst.SetMaximum(math.ceil(tmp_max * 2.0)/2.0)
                data_ratio_stat.SetMaximum(math.ceil(tmp_max * 2.0)/2.0)
            data_ratio_syst.SetMinimum(0.0001)
            # min set so the zero doesn't show up
            data_ratio_stat.SetMinimum(0.0001)

        # Make total mc ratios (likely will just be 1 if its the ref hist)
        if 'mctot_mnv' in self:
            mctot_ratio_mnv = self.mctot_mnv.Clone(self.mctot_mnv.GetName()+"_ratioto_"+ref_hist.GetName())
            if type(ref_hist) in [type(MnvH1D()), type(MnvH2D())]:
                ref_hist.AddMissingErrorBandsAndFillWithCV(mctot_ratio_mnv)
            mctot_ratio_mnv.Divide(mctot_ratio_mnv, ref_hist, 1.0, 1.0)

            self.mctot_ratio_mnv = mctot_ratio_mnv.Clone()
            mctot_ratio_cv, mctot_ratio_band = self.GetMCtotCVAndBand(mctot_ratio_mnv)
            mctot_ratio_cv.SetMaximum(2.0)
            tmp_max_bin = mctot_ratio_band.GetMaximumBin()
            tmp_max = mctot_ratio_band.GetBinContent(tmp_max_bin) + mctot_ratio_band.GetBinError(tmp_max_bin)
            # Make the max right, in increments of 0.5
            if tmp_max > 2.0:
                mctot_ratio_band.SetMaximum(math.ceil(tmp_max * 2.0)/2.0)
                mctot_ratio_cv.SetMaximum(math.ceil(tmp_max * 2.0)/2.0)
            # min set so the zero doesn't show up
            mctot_ratio_band.SetMinimum(0.0001)
            mctot_ratio_cv.SetMinimum(0.0001)
            self.mctot_ratio_cv = mctot_ratio_cv
            self.mctot_ratio_band = mctot_ratio_band

        # Make types ratios
        if 'types_hists_dict' in self:
            types_ratio_dict = {}
            for key in self.types_hists_dict:
                tmp_ratio = self.types_hists_dict[key].Clone()
                tmp_ratio.Divide(tmp_ratio, ref_hist, 1.0, 1.0, "B")
                # These hists are lines, so this makes the lines the right color, and removes the fill
                tmp_ratio.SetLineColor(tmp_ratio.GetFillColor())
                tmp_ratio.SetFillStyle(0)
                if key >= 10:
                    tmp_ratio.SetLineStyle(2)
                types_ratio_dict[key] = tmp_ratio
            self.types_ratio_dict = types_ratio_dict

            self.types_ratio_stack = THStack("types_ratio_stack", "")
            for key in reversed(list(types_ratio_dict.keys())):
                self.types_ratio_stack.Add(types_ratio_dict[key].Clone())
            
            # Make double stack dicts for reco plots, this stacks together each inttype 
            if 11 in self.types_ratio_dict:
                types_ratio_doublestack_dict = {}
                for key in types_ratio_dict:
                    if key > 10: continue
                    tmp_stack = THStack("types_ratio_double_stack_%s"%str(key), "")
                    tmp_bkg_hist = types_ratio_dict[key+10].Clone()
                    tmp_bkg_hist.SetLineStyle(2)
                    tmp_stack.Add(tmp_bkg_hist)
                    if key in types_ratio_dict:
                        tmp_stack.Add(types_ratio_dict[key].Clone())
                    types_ratio_doublestack_dict[key] = tmp_stack
                self.types_ratio_doublestack_dict = types_ratio_doublestack_dict

        # Make a dict of the cats ratios
        if 'cats_hists_dict' in self:
            cats_ratio_dict = {}
            for key in self.cats_hists_dict:
                tmp_ratio = self.cats_hists_dict[key].Clone()
                if type(ref_hist) in [type(MnvH1D()), type(MnvH2D())]:
                    ref_hist.AddMissingErrorBandsAndFillWithCV(tmp_ratio)
                tmp_ratio.Divide(tmp_ratio, ref_hist, 1.0, 1.0, "B")
                tmp_ratio.SetLineColor(tmp_ratio.GetFillColor())
                tmp_ratio.SetFillStyle(0)
                cats_ratio_dict[key] = tmp_ratio
            self.cats_ratio_dict = cats_ratio_dict

            self.cats_ratio_stack = THStack("cats_ratio_stack","")
            for key in reversed(list(cats_ratio_dict.keys())):
                self.cats_ratio_stack.Add(cats_ratio_dict[key].Clone())

    def SetAllHists(self, i_data_mnv, i_mc_hist_dict, i_ref_hist = 0, do_pinkstat = False):
        # This basically calls all the set hist things
        if type(i_data_mnv) != type(MnvH1D()):
            sys.exit(1)
        for a_cat in i_mc_hist_dict:
            print(a_cat)
            for b_type in i_mc_hist_dict[a_cat]:
                if type(i_mc_hist_dict[a_cat]) not in [type(MnvH1D()), type(TH1D())]:
                    if type(i_mc_hist_dict[a_cat][b_type]) not in [type(MnvH1D()), type(TH1D())]:
                        print("OUCH HERE")
                        sys.exit(1)
        self.SetDataHist(i_data_mnv, do_pinkstat)
        self.SetMCHists(i_mc_hist_dict)
        # If you don't have a reference hist for the ratio, this picks one from what is here
        i_ref_hist.Print()
        if type(i_ref_hist) not in [type(MnvH1D()),type(TH1D())]:
            if 'mctot_mnv' in self:
                self.ref_hist = self.mctot_mnv.Clone()
                ref_hist.Print()
                # sys.exit(1)
            elif 'data_mnv' in self:
                self.ref_hist = self.data_mnv.Clone()
            else:
                return
        else:
            self.ref_hist = i_ref_hist.Clone()

        self.SetRatioHists(self.ref_hist, do_pinkstat = do_pinkstat)

    def SetAxisTitle(self, axis, title):
        # Set an axis title
        if axis in [0, "x"]:
            self.xtitle = title
            if 'data_mnv' in self:
                self.data_syst.GetXaxis().SetTitle(title)
            if 'mctot_mnv' in self:
                self.mctot_cv.GetXaxis().SetTitle(title)
        if axis in [1, "y"]:
            self.ytitle = title
            if 'data_mnv' in self:
                self.data_syst.GetYaxis().SetTitle(title)
            if 'mctot_mnv' in self:
                self.mctot_cv.GetYaxis().SetTitle(title)
        if axis in [2, "z"]:
            self.ztitle = title
            if 'data_mnv' in self:
                self.data_syst.GetZaxis().SetTitle(title)
            if 'mctot_mnv' in self:
                self.mctot_cv.GetZaxis().SetTitle(title)
    
    def SetAxisVarName(self, axis, varname, units = "", settitle = True):
        # This takes in var nam and units. Useful to have them separate to build complicated axis titles
        if axis in [0, "x"]:
            self.xvar = varname
            if units != "":
                self.xunits = units
        if axis in [1, "y"]:
            self.yvar = varname
            if units != "":
                self.yunits = units
        if axis in [2, "z"]:
            self.zvar = varname
            if units != "":
                self.zunits = units
        # if you want to build the title, maybe should be careful if doing y or z axis for a 1d plot
        if settitle and axis: # not in [1,2,"y","z"]:
            title = varname
            if units != "":
                title = "%s #lower[-0.25]{#scale[0.6]{[%s]}}"%(title, units)
            self.SetAxisTitle(axis, title)

    def SetLegend(self, do_data = True, do_mctot = True, types_or_cats = "", do_misc = False ):
        leg = ROOT.TLegend()
        leg.SetBorderSize(0)
        leg.SetFillColor(-1)
        leg.SetFillStyle(0)
        leg.SetTextFont(42)
        # this is where entries go
        entry_list = []
        if do_data and 'data_mnv' in self:
            dataname = "Data"
            if 'data_syst' in self:
                dataname = "Data (stat+syst)"
            entry_list.append({"hist": self.data_syst, "name":dataname, "opt": "PE"})
        if do_mctot and 'mctot_mnv' in self:
             #TODO: get model name in this
            entry_list.append({"hist": self.mnv_band, "name": "Total MC", "opt": "fl"})
        # uncheck this if no mctot, used later to put a blank space if needed
        if 'mctot_mnv' not in self:
            do_mctot = 0
        if do_misc and 'misc_hist_dict' in self:
            # TODO: need to make sure the keys are named right
            for key in misc_hist_dict:
                entry_list.append({"hist":misc_hist_dict[key], "name": key, "opt": "fl"})

        # If you have a breakdown of the MC, this figures which one you want and puts it in its own dict for now
        mc_breakdown = {}
        if types_or_cats != "":
            if types_or_cats == "cats" and 'cats_hists_dict' in self:
                mc_breakdown = self.cats_hists_dict
            if types_or_cats == "sigcats" and 'cats_sighists_dict' in self:
                mc_breakdown = self.cats_sighists_dict
            if types_or_cats == "bkgcats" and 'cats_bkghists_dict' in self:
                mc_breakdown = self.cats_bkghists_dict
            if types_or_cats == "types" and 'types_hists_dict' in self:
                mc_breakdown = self.types_hists_dict
            if types_or_cats == "sigtypes" and 'types_sighists_dict' in self:
                mc_breakdown = self.types_sighists_dict
            if types_or_cats == "bkgtypes" and 'types_bkghists_dict' in self:
                mc_breakdown = self.types_bkghists_dict
            # This one just uses sighists for now, probably don't need more than that, but leaves room to change if needed
            if types_or_cats == "doubletypes" and 'types_sighists_dict' in self:
                mc_breakdown = self.types_sighists_dict
        # If you breakdown the backgrounds into sig and bkg types, this puts the two of the same type next to each other
        for key in mc_breakdown:
            #TODO: this relies on the types/cats having the right names, will catsnames work?
            if type(key) == int:
                if key >= 10: continue
                entry_list.append({"hist":mc_breakdown[key], "name": catsnames[key], "opt": "fl"})
                if key + 10 in mc_breakdown: 
                    entry_list.append({"hist":mc_breakdown[key+10], "name": "Bkg " + catsnames[key],  "opt":"fl"})

        # If you have a lot of entries, put them in two columns
        if len(entry_list) > 6:
            leg.SetNColumns(2)
        # Now build the legend
        for entry in entry_list:
            leg.AddEntry(entry["hist"], entry["name"], entry["opt"])
            # lots of things here, but in the end this puts an empty entry in so things end up next to each other that if they should be
            if "Data" in entry["name"] and not len(entry_list)%2==0 and not do_mctot and len(entry_list) > 6:
                leg.AddEntry(0, "", "")
        # store it for now
        self.legend = leg
        
    def DrawHistOnPad(self, pad, do_data = True, do_mctot = True, types_or_cats = "", do_misc = False):
        pad.cd()
        pad.Draw()
        if self.logx:
            pad.SetLogx(1)
        if self.logy:
            pad.SetLogy(1)
        
        data_syst.Draw("axis")
        if types_or_cats != "":
            mc_stack = {}
            if types_or_cats == "cats" and 'cats_hists_dict' in self:
                mc_stack = self.cats_tot_stack
            if types_or_cats == "sigcats" and 'cats_sighists_dict' in self:
                mc_stack = self.cats_sig_stack
            if types_or_cats == "bkgcats" and 'cats_bkghists_dict' in self:
                mc_stack = self.cats_bkg_stack
            if types_or_cats == "types" and 'types_hists_dict' in self:
                mc_stack = self.types_tot_stack
            if types_or_cats == "sigtypes" and 'types_sighists_dict' in self:
                mc_stack = self.types_sig_stack
            if types_or_cats == "bkgtypes" and 'types_bkghists_dict' in self:
                mc_stack = self.types_bkg_stack
            # This one just uses sighists for now, probably don't need more than that, but leaves room to change if needed
            if types_or_cats == "doubletypes" and 'types_sighists_dict' in self:
                mc_stack = self.types_tot_stack
            mc_stack.Draw("9 stack ][ same")
        if do_mctot and 'mctot_mnv' in self:
            self.mctot_band.Draw("9 E2 E0 ][ same")
            self.mctot_cv.Draw("9 hist same")
        if do_data:
            self.data_stat.Draw("9 E1 X0 same")
            self.data_syst.Draw("9 E1 X0 same")
        if do_misc and 'misc_hist_dict' in self:
            for key in self.misc_hist_dict:
                self.misc_hist_dict.Draw("same %s"%self.misc_draw_opt)
        pad.Modified()
        pad.Update()
    
    def DrawRatioOnPad(self, pad, do_data = True, do_mctot = True, types_or_cats = "", do_misc = False):
        pad.cd()
        pad.Draw()
        if self.logx:
            pad.SetLogx(1)

        data_ratio_syst.Draw("axis")
        if do_mctot and 'mctot_ratio_mnv' in self:
            self.mctot_ratio_band.Draw("9 E2 E0 ][ same")
            self.mctot_ratio_cv.Draw("9 hist same")
        if types_or_cats != "":
            mc_stack = {}
            stack_opt = "same 9 noclear ][ "
            if types_or_cats == "cats" and 'cats_ratio_dict' in self:
                mc_stack = self.cats_ratio_dict
                stackopt += "nostack"
            # if types_or_cats == "sigcats" and 'cats_sighists_dict' in self:
            #     mc_stack = self.cats_sig_stack
            # if types_or_cats == "bkgcats" and 'cats_bkghists_dict' in self:
            #     mc_stack = self.cats_bkg_stack
            if types_or_cats == "types" and 'types_ratio_dict' in self:
                mc_stack = self.types_ratio_dict
                stackopt += "nostack"

            # if types_or_cats == "sigtypes" and 'types_sighists_dict' in self:
            #     mc_stack = self.types_sig_stack
            # if types_or_cats == "bkgtypes" and 'types_bkghists_dict' in self:
            #     mc_stack = self.types_bkg_stack
            # This one just uses sighists for now, probably don't need more than that, but leaves room to change if needed
            if types_or_cats == "doubletypes" and 'types_sighists_dict' in self:
                mc_stack = self.types_ratio_doublestack_dict
            for key in mc_stack:
                mc_stack.Draw(stack_opt)
        if do_misc and 'misc_ratio_dict' in self:
            for key in self.misc_ratio_dict:
                self.misc_ratio_dict.Draw("same %s"%self.misc_draw_opt)
        if do_data:
            data_stat.Draw("9 E1 X0 same")
            data_syst.Draw("9 E1 X0 same")
        pad.Modified()
        pad.Update()

    def DrawHistAndRatioOnCanvas(self, canvas, do_data = True, do_mctot = True, types_or_cats = "", do_misc = False):
        canvas.cd()
        top = ROOT.TPad("hist", "hist", 0, ratio_frac, 1.0, 1.0)
        top.SetRightMargin(tmp_pad_rmarg)
        top.SetLeftMargin(pad_lmarg)
        top.SetTopMargin(tmp_topmarj)
        top.SetBottomMargin(0)
        top.SetFrameLineWidth(1)

        bottom = ROOT.TPad("Ratio", "Ratio", 0, 0, 1.0, ratio_frac)
        bottom.SetRightMargin(tmp_pad_rmarg)
        bottom.SetLeftMargin(pad_lmarg)
        bottom.SetBottomMargin(bottommarg)
        bottom.SetTopMargin(0)
        bottom.SetFrameLineWidth(1)
        
        top.Draw()
        bottom.Draw()

        bottomArea = bottom.GetWNDC() * bottom.GetHNDC()
        topArea = top.GetWNDC() * top.GetHNDC()
        areaScale = topArea / bottomArea

        padwidth = 1 - pad_lmarg - tmp_pad_rmarg
        padheight = 1 - tmp_topmarj - bottommarg

        top.cd()
        self.DrawHistOnPad(top, do_data = True, do_mctot = True, types_or_cats = "", do_misc = False)

        bottom.cd()
        self.DrawHistOnPad(top, do_data = True, do_mctot = True, types_or_cats = "", do_misc = False)

        top.cd()

        SetLegend(do_data = True, do_mctot = True, types_or_cats = "", do_misc = False)
        self.legend.Draw()

    # TODO
    def DrawErrorSummaryOnCanvas(self, data_or_mc = "data"):
        return

    # TODO
    def DrawSectionOfHistOnPad(self, pad, bin_range, do_data = True, do_mctot = True, types_or_cats = "", do_misc = False):
        # Need to 
        return
    
    # TODO
    def DrawSectionOfRatioOnPad(self, pad, bin_range, do_data = True, do_mctot = True, types_or_cats = "", do_misc = False):
        return

    # TODO
    def DrawSectionOfHistAndRatioOnCanvas(self, canvas, bin_range, do_data = True, do_mctot = True, types_or_cats = "", do_misc = False):
        return

ROOT.TH1.AddDirectory(ROOT.kFALSE)

checkformodelcomp = False
checkfordatacomp = False
if len(sys.argv) == 1:
    print("python3 general_hist_plotter.py <path to analyze or sidebands files>")
    sys.exit(1)
if len(sys.argv) == 2:
    checkifanalyze = True
    domodelcomp = False
if len(sys.argv) > 2:
    checkformodelcomp = True
    checkfordatacomp = True
# First get the hists/files for the extracted cross section
# raw_filename = sys.argv[1]

foundanalyze = False
file_dict = {}
for filename in sys.argv[1:]:
    if ".root" not in filename:
        print("WARNING: this arg is not gonna do anything %s"%filename)
        continue
    
    if "_tuned_analyze9" in filename and not foundanalyze:
        tuned_filename = filename
        untuned_filename = filename.replace("_tuned_","_untuned_")
        # file_dict["tuned"] = tuned_filename
        # file_dict["untuned"] = untuned_filename
        
        file_dict["tuned"] = TFile.Open(tuned_filename,"READONLY")
        file_dict["untuned"] = TFile.Open(untuned_filename,"READONLY")
        foundanalyze = True
    elif "_untuned_analyze9" in filename and not foundanalyze:
        untuned_filename = filename
        tuned_filename = filename.replace("_untuned_","_tuned_")
        # file_dict["tuned"] = tuned_filename
        # file_dict["untuned"] = untuned_filename
        
        file_dict["tuned"] = TFile.Open(tuned_filename,"READONLY")
        file_dict["untuned"] = TFile.Open(untuned_filename,"READONLY")
        foundanalyze = True
    else:
        untuned_filename = filename

        file_dict["untuned"] = TFile.Open(untuned_filename,"READONLY")

# sys.exit(1)
# hist_dict = GetHistDict(file_dict)
hist_dict = {}
# with TFile.Open(file_dict["tuned"]) as i_file:
#     hist_dict = GetHistDict(i_file = i_file, groups = {})
# with TFile.Open(file_dict["untuned"]) as i_file:
#     hist_dict = GetHistDict(i_file = i_file, groups = hist_dict)
for tag in file_dict:
    tmp_dotuned = False
    if tag == "tuned": tmp_dotuned = True
    hist_dict = GetHistDict(file_dict[tag], groups = hist_dict, dotuned = tmp_dotuned)

# hist_dict = GetHistDict(file_dict["tuned"], groups = hist_dict, dotuned = True)
# hist_dict = GetHistDict(file_dict["untuned"], groups = hist_dict)

if "varsFile" not in file_dict["untuned"].GetListOfKeys():
    bigvarconfig_string = file_dict["untuned"].Get("varsFile_5A").GetTitle()
else:
    bigvarconfig_string = file_dict["untuned"].Get("varsFile").GetTitle()

bigvarconfig_dict = json.loads(re.sub("//.*", "", bigvarconfig_string, flags = re.MULTILINE))

# for b_sample in hist_dict["h"]:
base_varinfo_dict = {
    "EAvail": {
        "name": "EAvail",
        "tex_name": "E_{Avail}^{}",
        "units": "GeV",
        "logx": False,
        "logy": True,
        "bins": [],
    },
    "EAvailWithRemoval": {
        "name": "EAvailWithRemoval",
        "tex_name": "E_{Avail}^{} w/ removal",
        "units": "GeV",
        "logx": False,
        "logy": True,
        "bins": [],
    },
    "ptmu": {
        "name": "ptmu",
        "tex_name": "p^{}_{T}^{}",
        "units": "GeV/c",
        "logx": False,
        "logy": False,
        "bins": [],
    },
    "pzmu" : {
        "name": "pzmu",
        "tex_name": "p_{||}",
        "units": "GeV/c",
        "logx": False,
        "logy": False,
        "bins": [],
    },
    "Q2QE": {
        "name": "Q2QE",
        "tex_name": "Q^{2}_{QE}",
        "units": "GeV^{2}",
        "logx": True,
        "logy": False,
        "bins": [],
    }
}
# build the varinfo_dicts for each variable
# for b_sample in hist_dict["h"]:
plotfactory_varinfo_dicts = {}
for a_hist in ["h", "h2D"]:
    if a_hist not in hist_dict: continue
    for b_sample in hist_dict[a_hist]:
        for c_var in hist_dict[a_hist][b_sample]:
            if c_var in plotfactory_varinfo_dicts: continue
            tmp_varinfo_dict = {}

            if a_hist == "h":
                if c_var not in base_varinfo_dict:
                    var_title = c_var
                    var_units = "unit"
                    tmp_varconfig = bigvarconfig_dict["1D"][c_var]
                    if "units" in tmp_varconfig:
                        var_units = tmp_varconfig["units"]
                    if "title" in tmp_varconfig:
                        # for badstr in ["eV", " in ", "(",]
                        var_title = tmp_varconfig["title"]
                    tmp_logx = False
                    tmp_logy = False
                    for key in base_varinfo_dict:
                        if key in c_var or var in key:
                            tmp_logx = base_varinfo_dict[key]["logx"]
                            tmp_logy = base_varinfo_dict[key]["logy"]
                    base_varinfo_dict[c_var] = {
                        "name": c_var,
                        "tex_name": var_title,
                        "units": var_units,
                        "logx": tmp_logx,
                        "logy": tmp_logy,
                    }
                tmp_varinfo_dict = {"x": base_varinfo_dict[c_var]}
                plotfactory_varinfo_dicts[c_var] = tmp_varinfo_dict

            if a_hist == "h2D":
                xvar = c_var.split("_")[0]
                yvar = c_var.split("_")[1]
                tmp_varslist = c_var.split("_")
                for var in tmp_varslist:
                    if var not in base_varinfo_dict:
                        var_title = var
                        var_units = "unit"
                        tmp_varconfig = bigvarconfig_dict["1D"][var]
                        if "units" in tmp_varconfig:
                            var_units = tmp_varconfig["units"]
                        if "title" in tmp_varconfig:
                            # for badstr in ["eV", " in ", "(",]
                            var_title = tmp_varconfig["title"]
                        tmp_logx = False
                        tmp_logy = False
                        for key in base_varinfo_dict:
                            if key in var or var in key:
                                tmp_logx = base_varinfo_dict[key]["logx"]
                                tmp_logy = base_varinfo_dict[key]["logy"]
                        base_varinfo_dict[var] = {
                            "name": var,
                            "tex_name": var_title,
                            "units": var_units,
                            "logx": tmp_logx,
                            "logy": tmp_logy,
                        }
                tmp_varinfo_dict = {"x": base_varinfo_dict[xvar], "y": base_varinfo_dict[yvar]}
                plotfactory_varinfo_dicts[c_var] = tmp_varinfo_dict


for a_hist in hist_dict:
    for b_sample in hist_dict[a_hist]:
        for c_var in hist_dict[a_hist][b_sample]:
            var_hist_dict = hist_dict[a_hist][b_sample][c_var]
            # print(plotfactory_varinfo_dicts)
            print(">>>>>>>>>>>>>>>",c_var)
            print(var_hist_dict.keys())
            # for key in var_hist_dict:
            #     print(var_hist_dict[key].keys())
            plot_factory = PlotFactory(i_varinfo_dict = plotfactory_varinfo_dicts[c_var], i_hist_dict = var_hist_dict, )

# for b_sample in hist_dict["h2D"]:
#     for c_var in hist_dict["h2D"][b_sample]:
#         var_hist_dict = hist_dict["h2D"][b_sample][c_var]
#         if "reconstructed" not in var_hist_dict: continue
#         reco_hist_dict = var_hist_dict["reconstructed"]
#         data_mnv = reco_hist_dict["data"][0].Clone()
#         mc_dict = {}
#         for cat in  ["qelike", "qelikenot", "chargedpion", "neutralpion","other"]:
#             mc_dict[cat] = reco_hist_dict[cat][0].Clone()
#         mc_dict[0] = reco_hist_dict["mctot"][0].Clone()
#         for inttype in reco_hist_dict["qelike"]:
#             # mc_dict["qelike"][inttype].Print()
#             if inttype == 0: continue
#             mc_dict[inttype] = reco_hist_dict["qelike"][inttype].Clone()
#         for inttype in reco_hist_dict["qelikenot"]:
#             if inttype == 0: continue
#             mc_dict[inttype] = reco_hist_dict["qelikenot"][inttype].Clone()
#         print("Justbefore init Plot2D")
#         # plot2D = Plot2D(data_mnv, mc_dict, x_title = big_vars_info[c_var.split("_")[0]]["title"], y_title = big_vars_info[c_var.split("_")[1]]["title"])
        
#         # plot2D.SetPanelPlot1DList()
#         # plot2D.SetTotalProj1DList()
