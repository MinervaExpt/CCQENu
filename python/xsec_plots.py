# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023


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
# doratio = True
# dotypes = False

global_domodelcomp = False # Set to true if you want to do model comparisons, will need to give path to where files are

modelcomptodo = [
    # "Gv3_AR23",
    "G18_02a",
    "G18_02b",
    "G18_10a",
    "G18_10b",
    "NEUT_tune_LFG",
    "NEUT_tune_SF",
    "NuWro_CH_LFG",
    "NuWro_CH_SF",
    # "GIBUU",
]

modelsampletodo = [
    "QElike",
    "QElikeHyp",
]

typestodo = [
    "data",
    1,  #: "QE",
    8,  #: "2p2h",
    2,  #: "RES",
    3,  #: "DIS",
    4,  #: "COH",
]
typestodo_leg = typestodo[1:]
staterror_drawopt = "E1 X0"
typeslinedarker = True

modelplotinfo = {
    "G18_02a": {
        "name": "GENIE v3.0.6 G18_02a_02_11a",
        "shortname": "GENIEv3 G18_02a",
        "color": ROOT.kBlack, # TODO
        "linecolor":ROOT.kBlack,
    },
    "G18_02b": {
        "name": "GENIE v3.0.6 G18_02b_02_11a",
        "shortname": "GENIEv3 G18_02b",
        "color": ROOT.kBlack, # TODO
        "linecolor":ROOT.kBlack,
    },
    "G18_10a": {
        "name": "GENIE v3.0.6 G18_10a_02_11a",
        "shortname": "GENIEv3 G18_10a",
        "color": ROOT.kBlack, # TODO
        "linecolor":ROOT.kBlack,
    },
    "G18_10b": {
        "name": "GENIE v3.0.6 G18_10b_02_11a",
        "shortname": "GENIEv3 G18_10b",
        "fillcolor": ROOT.kBlack, # TODO
        "linecolor":ROOT.kBlack,
    },
    "NEUT_tune_LFG": {
        "name": "NEUT v5.4.1 LFG",
        "shortname": "NEUT LFG",
        "fillcolor": ROOT.kBlack, # TODO
        "linecolor":ROOT.kBlack,
    },
    "NEUT_tune_SF": {
        "name": "NEUT v5.4.1 SF",
        "shortname": "NEUT SF",
        "fillcolor": ROOT.kBlack, # TODO
        "linecolor":ROOT.kBlack,
    },
    "NuWro_CH_LFG": {
        "name": "NuWro v21.09 LFG",
        "shortname": "NuWro LFG",
        "fillcolor": ROOT.kBlack, # TODO
        "linecolor":ROOT.kBlack,
    },
    "NuWro_CH_SF": {
        "name": "NuWro v21.09 SF",
        "shortname": "NuWro SF",
        "fillcolor": ROOT.kBlack, # TODO
        "linecolor":ROOT.kBlack,
    },
}

ROOT.TH1.AddDirectory(ROOT.kFALSE)
_xsize = 1200.0
_ysize = 900.0

latex_x = 0.55
latex_y = 0.43

pad_lmarg = 0.10
pad_rmarg = 0.04
topmarg = 0.05
bottommarg = 0.3

# This is to set how tall the ratio should be in the pad
ratio_frac = 0.3 #0.278

data_marker_style = 20
data_marker_size = 1.5
data_marker_size2d = 0.75
end_error_size = 10

legendfontsize = 0.05
legx1 = 0.7
legx2 = 1.0
legy1 = 0.65
legy2 = 0.95

# lat_xoffset = 0.06
lat_xoffset = 0.0
lat_yoffset = 0.04

typeslinewidth = 1
typeslinewidth1D = 3

scaleX = ["Q2QE"]
scaleY = ["EAvail","E_{Avail}"]#"recoil","EAvail"]

skipstage_list = [
    "bkgsub",
    "unfolded",
    "effcorr",
    # "sigma",
    # "modelcomp",
]

skipvar_list = [
    # "EAvail",
]

errorbandsgroups = {
    "BeamAngle": [
        "BeamAngleX", 
        "BeamAngleY", 
    ],
    "Flux": [
        "Flux",
    ],
    "GENIE": [
        "GENIE_AGKYxF1pi", 
        "GENIE_AhtBY", 
        "GENIE_BhtBY", 
        "GENIE_CCQEPauliSupViaKF", 
        "GENIE_CV1uBY", 
        "GENIE_CV2uBY", 
        "GENIE_EtaNCEL", 
        "GENIE_FrAbs_N", 
        "GENIE_FrAbs_pi", 
        "GENIE_FrCEx_N", 
        "GENIE_FrCEx_pi", 
        "GENIE_FrElas_N", 
        "GENIE_FrElas_pi", 
        "GENIE_FrInel_N", 
        "GENIE_FrPiProd_N", 
        "GENIE_FrPiProd_pi", 
        "GENIE_MFP_N", 
        "GENIE_MFP_pi", 
        "GENIE_MaCCQE", 
        "GENIE_MaNCEL", 
        "GENIE_MaRES", 
        "GENIE_MvRES", 
        "GENIE_NormDISCC", 
        "GENIE_NormNCRES", 
        "GENIE_RDecBR1gamma", 
        "GENIE_Rvn1pi", 
        "GENIE_Rvn2pi", 
        "GENIE_Rvp1pi", 
        "GENIE_Rvp2pi", 
        "GENIE_Theta_Delta2Npi", 
        "GENIE_VecFFCCQEshape",     
    ],
    "GEANT": [
        "GEANT_Neutron", 
        "GEANT_Pion", 
        "GEANT_Proton", 
    ],
    "response": [
        "response_em", 
        "response_meson", 
        "response_other",
        "response_proton",         
    ],
    "Tune": [
        "LowQ2Pi", 
        "Low_Recoil_2p2h_Tune", 
        "RPA_HighQ2", 
        "RPA_LowQ2", 
    ],
    "MINOS": [
        "MINOS_Reconstruction_Efficiency", 
    ], 
    "Muon": [
        "Muon_Energy_MINERvA", 
        "Muon_Energy_MINOS", 
        "Muon_Energy_Resolution", 
    ]

}

errorbands = [ 
    "BeamAngleX", 
    "BeamAngleY", 
    "Flux", 
    "GEANT_Neutron", 
    "GEANT_Pion", 
    "GEANT_Proton", 
    "GENIE_AGKYxF1pi", 
    "GENIE_AhtBY", 
    "GENIE_BhtBY", 
    "GENIE_CCQEPauliSupViaKF", 
    "GENIE_CV1uBY", 
    "GENIE_CV2uBY", 
    "GENIE_EtaNCEL", 
    "GENIE_FrAbs_N", 
    "GENIE_FrAbs_pi", 
    "GENIE_FrCEx_N", 
    "GENIE_FrCEx_pi", 
    "GENIE_FrElas_N", 
    "GENIE_FrElas_pi", 
    "GENIE_FrInel_N", 
    "GENIE_FrPiProd_N", 
    "GENIE_FrPiProd_pi", 
    "GENIE_MFP_N", 
    "GENIE_MFP_pi", 
    "GENIE_MaCCQE", 
    "GENIE_MaNCEL", 
    "GENIE_MaRES", 
    "GENIE_MvRES", 
    "GENIE_NormDISCC", 
    "GENIE_NormNCRES", 
    "GENIE_RDecBR1gamma", 
    "GENIE_Rvn1pi", 
    "GENIE_Rvn2pi", 
    "GENIE_Rvp1pi", 
    "GENIE_Rvp2pi", 
    "GENIE_Theta_Delta2Npi", 
    "GENIE_VecFFCCQEshape", 
    "LowQ2Pi", 
    "Low_Recoil_2p2h_Tune", 
    "MINOS_Reconstruction_Efficiency", 
    "Muon_Energy_MINERvA", 
    "Muon_Energy_MINOS", 
    "Muon_Energy_Resolution", 
    "RPA_HighQ2", 
    "RPA_LowQ2", 
    "response_em", 
    "response_meson", 
    "response_other",
    "response_proton", 
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
    else:
        print("found dir ", plotdir)
    if subdir == "":
        return plotdir
    if not os.path.exists(os.path.join(plotdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(plotdir, subdir))
        os.mkdir(os.path.join(plotdir, subdir))
    else:
        print("found dir ", plotdir)

    return os.path.join(plotdir, subdir)

def GetModelCompFilePathsDict(pathtodir):
    """
    Get's all the file paths for the NUISANCE model comparisons. Expects files 
    to be in subdirs of the pathtodir and looks for ones without a prescale. 
    There should only be files for the 4 GENIEv3 options, and two each for NEUT
    and NuWro. Returns a dictionary of the files keyed to model names
    """
    if not os.path.exists(pathtodir):
        print("ERROR: path to modelcomp isn't there. Exiting.")
        sys.exit(1)
    path_dict = {}
    subdir_list = os.listdir(pathtodir)
    for model in modelcomptodo:
        tmpsubdir = ""
        for subdir in subdir_list:
            if model not in subdir:
                continue
            print("\tFound subdir for model %s: %s"%(model,subdir))
            tmpsubdir = subdir
            break
        if tmpsubdir == "":
            print("WARNING: model %s requested but not found. Skipping..."%(model))
            continue
        
        subdir_list.remove(tmpsubdir)
        subdirpath = os.path.join(pathtodir,subdir)
        # Now check if it has the right root files
        modelfile_list = os.listdir(subdirpath)
        filename = ""
        for name in modelfile_list:
            if ".root" not in name or "rawnominalreweight" in name:
                continue
            if "PRESCALE" in name:
                continue
            else:
                print("\tfound file for model %s"%(model))
                filename = name
                break
        if filename == "":
            print("WARNING: skipping model %s requested because could not find file in %s"%(model,subdirpath))
            continue
        path_dict[model] = os.path.join(subdirpath,filename)
    
    return file_dict
    
def GetModelHistDict(f):
    # Returned dict, dict structure is {histdim:{sample:{variable:{fluxnorm:TH1D()}}}
    histdict = {}
    keys = f.GetListOfKeys()
    for k in keys:
        name = k.GetName()
        if "___" not in name:
            continue
        parse = name.split("___")
        hist = parse[0]
        sample = parse[1]
        fluxnorm = parse[2]
        variable = parse[3]

        if "_" in variable and hist not in ["h2D","h2d"]:
            hist = "h2D"
        if sample not in modelsampletodo:
            continue
        
        if hist not in histdict:
            histdict[hist] = {}
        if sample not in histdict[hist]:
            histdict[hist][sample] = {}
        if variable not in histdict[hist][sample]:
            histdict[hist][sample][variable] = {}
        if fluxnorm not in histdict[hist][sample][variable]:
            histdict[hist][sample][variable][fluxnorm] = {}
        else:
            print("WARNING: GetModelHistDict() already have hist %s. Skipping for now..."%(name))
            continue
        h = f.Get(name).Clone()
        if h.GetEntries() <= 0:
            continue
        histdict[hist][sample][variable][fluxnorm] = h
    return histdict

def GetInputHistDict(f, input_dict = {}):
    keys = f.GetListOfKeys()
    print("Making dict of source hists in file %s..."%(f.GetName()))
    for k in keys:
        name = k.GetName()
        if "___" not in name:
            continue
        parse = name.split("___")
        if len(parse) < 5: continue
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
        # h.SetLineColor(ROOT.kBlack)
        h.SetLineColor(ROOT.TColor.GetColorDark(catscolors[cat]))
        if "data" in cat:
            # h.Scale(1.0, "width")
            # h.Scale(1.0)
            h.SetMarkerStyle(data_marker_style)
            h.SetMarkerSize(data_marker_size)
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
        h.SetFillColor(catscolors[cat])
        # h.SetLineColor(ROOT.TColor.GetColorDark(typescolors[inttype]))
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

        # if h.GetEntries() <= 0: 
        if h.GetEntries() <= 0 and inttype not in [1,2,3,4,8]: 
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
        # h.SetLineColor(ROOT.TColor.GetColorDark(typescolors[inttype]))
        # TODO width normalize?
        # h.Scale(1.0, "width")
        analyze_dict[hist][sample][var][stage][inttype] = h

    return analyze_dict 

def MakeDataMCRatio(i_data, i_mctot):
    mcratio = i_data.Clone(str(i_data.GetName().replace("data", "datamcratio")))
    mcratio.Divide(i_data, i_mctot,1.0,1.0, "B")
    return mcratio

def MakeDataMCRatioForPlot(i_data, i_mctot):
    ratio = i_data.Clone(str(i_data.GetName().replace("data", "datamcratio")))
    mctot = i_mctot.Clone()
    mctot.ClearAllErrorBands()
    mctot.AddMissingErrorBandsAndFillWithCV(i_mctot)
    ratio.Divide(ratio,mctot,1.0,1.0)
    return ratio

def MakeTypesMCRatioDict(i_typesdict, i_mctot):
    i_mctot.Print()
    typesratiodict = {}

    first = True
    tmp_typestot = MnvH1D()
    # Loop over types hists
    for key in i_typesdict.keys():
        # Make ratio to total mc
        tmp_hist = i_typesdict[key].Clone(str(i_typesdict[key].GetName()+"_ratiotomctot"))
        tmp_hist.Divide(tmp_hist, i_mctot,1.0,1.0,"B")
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

def GetPadMax(i_data_hist, i_mctot_hist, including_errors = True):
    data_max = i_data_hist.GetBinContent(i_data_hist.GetMaximumBin())
    mc_max = i_mctot_hist.GetBinContent(i_mctot_hist.GetMaximumBin())
    tmp_max = max(data_max, mc_max)
    if including_errors:
        tmp_data = i_data_hist.Clone()
        if type(i_data_hist)==type(MnvH1D()):
            tmp_data = i_data_hist.GetCVHistoWithError().Clone()
        
        for i in range(1,tmp_data.GetNbinsX()+1):
            print("\t%s\t%s"%(tmp_data.GetBinContent(i),tmp_data.GetBinError(i)))
            cont_and_err = tmp_data.GetBinContent(i) + tmp_data.GetBinError(i)
            if cont_and_err > tmp_max:
                print("\tcont_and_err:", cont_and_err, "\ttmp_max", tmp_max)
                return cont_and_err
    print("\tGoing with tmp max cont_and_err:", cont_and_err, "\ttmp_max:", tmp_max)
    return tmp_max


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

    mnv_data.SetMarkerStyle(data_marker_style)
    mnv_data.SetMarkerColor(ROOT.kBlack)
    mnv_data.SetLineWidth(2)
    mnv_data.SetLineColor(ROOT.kBlack)
    mnv_data.SetLineStyle(1)
    mnv_data.SetMarkerSize(data_marker_size)

    data_hist = mnv_data.GetCVHistoWithError(True,False)
    data_stat = mnv_data.GetCVHistoWithStatError()
    data_stat.SetMarkerStyle(1)
    data_stat.SetMarkerSize(1)

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
    top = TPad("hist", "hist", 0, ratio_frac, 1, 1)
    top.SetRightMargin(pad_rmarg)
    top.SetLeftMargin(pad_lmarg)
    top.SetTopMargin(topmarg)
    top.SetBottomMargin(0)
    top.SetFrameLineWidth(1)

    bottom = TPad("Ratio", "Ratio", 0, 0, 1, ratio_frac)
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
    # titlewidth = mnvPlotter.GetLegendWidthInLetters(["Data","MnvTunev2.0.1","COH","RES","DIS","2p2h","QE"])
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

    leg.AddEntry(data_hist, "Data","pe")
    leg.AddEntry(mc_band, "Simulation","fl")

    leg.Draw()
    
    # if doratio:
    bottom.cd()

    # ratio = MnvH1D()
    # ratio = MakeDataMCRatio(data_hist,mc_band)
    mnv_ratio = MakeDataMCRatioForPlot(mnv_data, mnv_mc)
    ratio, ratio_stat = GetDataHistsForPlot(mnv_ratio)
    ratio.SetFillStyle(1001)
    # ratio.SetMinimum(0.5)
    # ratio.SetMaximum(1.5)
    ratio.SetMinimum(0.001)
    ratio.SetMaximum(3.0)

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
    ratio_stat.Draw("E1 X0 same")
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

    ratio.Draw("E1 X0 same")
    ratio_stat.Draw("E1 X0 same")

    top.cd()
    prelim = AddPreliminary()
    # titleonplot = MakeTitleOnPlot()
    prelim.DrawLatex(x1.value-lat_xoffset, y1.value-2*lat_yoffset-0.01, "MINER#nuA Work In Progress")
    # titleonplot.DrawLatex(0.37, 0.9, plottitle)

    # canvas_name = thename + "_FinalStates"
    thename += "_FinalStates"

    if dotuned:
        thename += "_tuned" 


    cc.Print(os.path.join(outdirname, thename + ".png"))
    cc.Print(os.path.join(outdirname, "source", thename + ".C"))
    cc.Print(os.path.join(outdirname, canvas_name + ".pdf"),"Title:%s"%(canvas_title + " Final States"))

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
        hist = i_mc_typeshistdict[key].Clone()
        hist = i_mc_typeshistdict[key].GetCVHistoWithStatError()
        hist.Scale(1.0, "width")
        hist.SetLineWidth(typeslinewidth1D)
        typehistdict[typesnames[key]] = hist

    mnv_data.Print()

    mnv_data.SetMarkerStyle(data_marker_style)
    mnv_data.SetMarkerColor(ROOT.kBlack)
    mnv_data.SetLineWidth(2)
    mnv_data.SetLineColor(ROOT.kBlack)
    mnv_data.SetLineStyle(1)
    mnv_data.SetMarkerSize(data_marker_size)

    data_hist = mnv_data.GetCVHistoWithError(True,False)
    data_stat = mnv_data.GetCVHistoWithStatError()

    data_hist.GetYaxis().SetTitle(y_title)
    data_hist.GetYaxis().CenterTitle()
    data_hist.GetYaxis().SetTitleOffset(0.9)
    data_hist.GetYaxis().SetTitleSize(0.05)
    data_hist.GetYaxis().SetLabelSize(0.05)

    data_hist.SetMaximum(1.2* max(mnv_data.GetMaximum(),mnv_mc.GetMaximum()))
    data_stat.SetMarkerStyle(1)
    data_stat.SetMarkerSize(1)
    # mc_band = mnv_mc.GetCVHistoWithError(True,False)
    # mc_band.SetFillColor(ROOT.kRed-10)
    # mc_band.SetFillStyle(1001)
    # mc_band.SetLineColor(ROOT.kRed)
    # mc_band.SetMarkerStyle(0)

    mc_hist = mnv_mc.GetCVHistoWithError(True,False)
    mc_hist.SetFillColor(0)
    # mc_hist.SetLineColor(2)
    mc_hist.SetLineColor(typescolors[0])
    # mc_hist.SetLineColor(ROOT.TColor.GetColorDark(typescolors[0]))
   
    mc_hist.SetLineStyle(1)
    # mc_hist.SetLineWidth(3)
    mc_hist.SetLineWidth(typeslinewidth1D)

    # if doratio:
    top = TPad("hist", "hist", 0, ratio_frac, 1, 1)
    top.SetRightMargin(pad_rmarg)
    top.SetLeftMargin(pad_lmarg)
    top.SetTopMargin(topmarg)
    top.SetBottomMargin(0)
    top.SetFrameLineWidth(1)

    bottom = TPad("Ratio", "Ratio", 0, 0, 1, ratio_frac)
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

    ROOT.gStyle.SetErrorX(0) # This turns off the horizontal error bars
    ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer

    # Move to top pad for hists
    top.cd()
    if c_var in scaleY:
        top.SetLogy()
    leg_pos = "TR"
    top.SetLogy()
    # E1 draws a point with error bars, X0 turns off horizontal error bars
    data_hist.Draw("E1 X0")
    
    # if not issmooth:
    # mc_band.Draw("SAME E2")
    for key in typehistdict.keys():
        typehistdict[key].SetLineWidth(typeslinewidth1D)
        typehistdict[key].Draw("HIST SAME")

    typeskeys = typehistdict.keys()
    # mc_hist.Draw("SAME HIST X0")
    mc_hist.Draw("HIST SAME")
    
    data_hist.Draw("Same E1 X0")
    data_stat.Draw("SAME E1 X0")

    legend_list = [
        "Data", 
        "MnvTune431", # basemodelname,
    ]
    # if do_comparison:
    #     legend_list += [modelplotinfo[model]["shortname"] for model in modelcomptodo]
    # else:
    legend_list += [
        "QE",
        "2p2h",
        "RES",
        "DIS",
        "COH",
    ]
    # titlewidth = mnvPlotter.GetLegendWidthInLetters(["Data","MnvTunev431","COH","RES","DIS","2p2h","QE"])
    titlewidth = mnvPlotter.GetLegendWidthInLetters(legend_list)
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
    leg.AddEntry(data_hist, "Data","pe")
    # leg.AddEntry(mc_hist, "MnvTune v2.0.1","fl")
    leg.AddEntry(mc_hist, typesnames[0],"fl")
    for key in typehistdict:
        leg.AddEntry(typehistdict[key],typesnames[typesints[key]], "fl")

    leg.Draw()
    
    bottom.cd()

    mnv_ratio = MakeDataMCRatioForPlot(mnv_data, mnv_mc)
    ratio, ratio_stat = GetDataHistsForPlot(mnv_ratio)
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
    ratio.SetLineWidth(2)
    
    ratio_stat.SetLineColor(ROOT.kBlack)
    ratio_stat.SetMarkerStyle(1)
    ratio_stat.SetMarkerSize(1)
    ratio.Draw("E1 X0")
    ratio_stat.Draw("E1 X0 SAME")
    # Now do mc uncertainties
    mcerror = TH1D()
    mnv_mc.SetFillStyle(1001)
    mcerror = TH1D(mnv_mc.GetTotalError(False, True, False))
    for bin in range(0, mcerror.GetXaxis().GetNbins() + 2):
        mcerror.SetBinError(bin, max(mcerror.GetBinContent(bin), 1.0e-9))
        mcerror.SetBinContent(bin, 1.0)
    mcerror.SetLineColor(ROOT.kRed)
    mcerror.SetLineWidth(typeslinewidth1D)
    # mcerror.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
    # mcerror.SetFillColor(ROOT.kRed-10)
    # mcerror.Draw("same E2")

    # Now do a line at 1
    straightline = TH1D()
    straightline = mcerror.Clone()
    straightline.SetFillStyle(0)
    straightline.SetFillColor(typescolors[0])
    straightline.SetFillColor(typescolors[0])
    straightline.Draw("hist same")

    for key in typesratiodict:
        typesratiodict[key].SetLineWidth(typeslinewidth1D)
        typesratiodict[key].Draw("HIST SAME")

    ratio.Draw("same")
    top.cd()
    prelim = AddPreliminary()
    # titleonplot = MakeTitleOnPlot()
    prelim.DrawLatex(x1.value-lat_xoffset, y1.value-2*lat_yoffset-0.01, "MINER#nuA Work In Progress")
    # titleonplot.DrawLatex(0.37, 0.9, plottitle)
    thename += "_Types"
    # if dotuned:
    #     canvas_name += "_tuned" 

    cc.Print(os.path.join(outdirname, thename + ".png"))
    cc.Print(os.path.join(outdirname, "source", thename + ".C"))
    cc.Print(os.path.join(outdirname, canvas_name + ".pdf"),"Title:%s Types"%(thetitle))

    cc.cd()
    cc.Clear()
    cc.Modified()
    cc.Update()
    del cc

def DrawDataMCTypesPlot1D_AxisChange(i_data_hist, i_mctot_hist, i_mc_typeshistdict, x_title, y_title, outdirname, canvas_name, canvas_title):
    tmp_pad_rmarg = pad_rmarg + 0.02
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
    # cc.SetFrameLineWidth(1)

    mnv_data = i_data_hist.Clone()
    mnv_mc = i_mctot_hist.Clone()
    
    mnv_data.Scale(1.0, "width")
    mnv_mc.Scale(1.0, "width")

    typehistdict = {}
    for key in i_mc_typeshistdict:
        hist = i_mc_typeshistdict[key].GetCVHistoWithStatError()
        hist.Scale(1.0, "width")
        hist.SetLineWidth(typeslinewidth1D)
        typehistdict[typesnames[key]] = hist

    # mnv_data.Print()

    mnv_data.SetMarkerStyle(data_marker_style)
    mnv_data.SetMarkerColor(ROOT.kBlack)
    mnv_data.SetLineWidth(2)
    mnv_data.SetLineColor(ROOT.kBlack)
    mnv_data.SetLineStyle(1)
    mnv_data.SetMarkerSize(data_marker_size)

    data_hist = mnv_data.GetCVHistoWithError(True,False)
    data_stat = mnv_data.GetCVHistoWithStatError()
    
    data_hist.SetMaximum(1.2* max(mnv_data.GetMaximum(),mnv_mc.GetMaximum()))
    data_stat.SetMarkerStyle(1)
    data_stat.SetMarkerSize(1)
    # mc_band = mnv_mc.GetCVHistoWithError(True,False)
    # mc_band.SetFillColor(ROOT.kRed-10)
    # mc_band.SetFillStyle(1001)
    # mc_band.SetLineColor(ROOT.kRed)
    # mc_band.SetMarkerStyle(0)

    mc_hist = mnv_mc.GetCVHistoWithError(True,False)
    mc_hist.SetFillColor(0)
    mc_hist.SetLineColor(typescolors[0])
    # mc_hist.SetLineColor(ROOT.TColor.GetColorDark(typescolors[0]))
    mc_hist.SetLineStyle(1)
    mc_hist.SetLineWidth(typeslinewidth1D)

    # This is for figuring out how wide to make the pads for the hists, hardcoded for now
    left_histwidth = 0.015
    tot_histwidth = 0.5
    leftfrac = left_histwidth/tot_histwidth
    rightfrac = 1.0 - leftfrac


    # Other info to correctly get margins
    marginwidth = 1.0 - tmp_pad_rmarg - pad_lmarg

    rightscale = 10.0

    # Now make all the left and right hists
    data_hist_right = data_hist.Clone()
    data_hist_right.GetXaxis().SetRangeUser(left_histwidth, tot_histwidth)
    # data_hist_right.Scale(rightscale)
    # data_hist_right.SetMaximum(1.2*data_hist_right.GetBinContent(2))
    data_hist_right.SetMaximum(1.2 * mnv_data.GetMaximum()/10.0)
    data_hist_right.GetYaxis().SetLabelSize(0.05)

    data_hist_left = data_hist.Clone()
    data_hist_left.GetXaxis().SetRangeUser(0.0, left_histwidth)

    data_hist_lr = {"left": data_hist_left, "right": data_hist_right}

    data_stat_right = data_stat.Clone()
    data_stat_right.GetXaxis().SetRangeUser(left_histwidth, tot_histwidth)
    # data_stat_right.Scale(rightscale)
    data_stat_left = data_stat.Clone()
    data_stat_left.GetXaxis().SetRangeUser(0.0, left_histwidth)
    data_stat_lr = {"left": data_stat_left, "right": data_stat_right}

    mc_hist_left = mc_hist.Clone()
    mc_hist_left.GetXaxis().SetRangeUser(0.0,left_histwidth)
    mc_hist_right = mc_hist.Clone()
    # mc_hist_right.Scale(rightscale)

    mc_hist_right.GetXaxis().SetRangeUser(left_histwidth, tot_histwidth)
    mc_hist_lr = {"left": mc_hist_left, "right": mc_hist_right}

    typehistdict_right = {}
    typehistdict_left = {}
    typeskeys = typehistdict.keys()

    for key in typeskeys:
        tmp_left = typehistdict[key].Clone()
        tmp_left.GetXaxis().SetRangeUser(0.0, left_histwidth)
        typehistdict_left[key] = tmp_left
        tmp_right = typehistdict[key].Clone()
        # tmp_right.Scale(rightscale)
        tmp_right.GetXaxis().SetRangeUser(left_histwidth, tot_histwidth)
        typehistdict_right[key] = tmp_right
    typehistdict_lr = {"left":typehistdict_left, "right":typehistdict_right}
    # # if doratio:
    top = TPad("hist", "hist", 0, ratio_frac, 1, 1)
    top.SetRightMargin(tmp_pad_rmarg)
    top.SetLeftMargin(pad_lmarg)
    top.SetTopMargin(topmarg)
    top.SetBottomMargin(0)
    # top.SetFrameLineWidth(1)

    bottom = TPad("Ratio", "Ratio", 0, 0, 1, ratio_frac)
    bottom.SetRightMargin(tmp_pad_rmarg)
    bottom.SetLeftMargin(pad_lmarg)
    bottom.SetBottomMargin(bottommarg)
    bottom.SetTopMargin(0)
    # bottom.SetFrameLineWidth(3)

    # top_right = TPad("hist1", "hist1", pad_lmarg + leftfrac * marginwidth, ratio_frac, 1 - tmp_pad_rmarg, 1-topmarg*(1-ratio_frac))
    # top_right.SetRightMargin(0)
    top_right = TPad("hist1", "hist1", pad_lmarg + leftfrac * marginwidth, ratio_frac, 1.0, 1-topmarg*(1-ratio_frac))
    top_right.SetRightMargin(tmp_pad_rmarg*(1/(1-(pad_lmarg + leftfrac * marginwidth))))
    top_right.SetLeftMargin(0.0)
    top_right.SetTopMargin(0)
    top_right.SetBottomMargin(0)
    # top_right.SetFrameLineWidth(3)
    top.Draw()
    top_right.Draw()
    bottom.Draw()
    rightArea = top_right.GetWNDC() * top_right.GetHNDC()
    bottomArea = bottom.GetWNDC() * bottom.GetHNDC()
    topArea = top.GetWNDC() * top.GetHNDC()
    # topArea = leftArea + rightArea
    areaScale = topArea / bottomArea

    # areaScale_l = rightArea / leftArea
    # areaScale_r = topArea / rightArea

    # top.cd()

    # data_hist.Draw("HIST")
    ROOT.gStyle.SetErrorX(0) # This turns off the horizontal error bars
    ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer

    top_right.cd()

    data_hist_lr["right"].Draw("axis y+")
    for key in reversed(list(typehistdict_lr["right"].keys())):
        typehistdict_lr["right"][key].Draw("HIST SAME")

    mc_hist_lr["right"].Draw("HIST SAME")

    data_stat_lr["right"].Draw("SAME E1 X0")
    data_hist_lr["right"].Draw("Same E1 X0")
    leg_pos = "TR"
    titlewidth = mnvPlotter.GetLegendWidthInLetters([
        "Data",
        "MnvTunev431",
        "COH",
        "RES",
        "DIS",
        "2p2h",
        "QE",
    ])
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
    # leg.AddEntry(mc_hist_lr[lr], "MnvTune v2.0.1","fl")
    leg.AddEntry(data_hist_lr["right"], "Data","pe")

    leg.AddEntry(mc_hist_lr["right"], typesnames[0],"fl")
    for key in typehistdict_lr["right"]:
        leg.AddEntry(typehistdict_lr["right"][key],typesnames[typesints[key]],"fl")

    leg.Draw()

    # # Move to top pad for hists
    top.cd()
    # if c_var in scaleY:
    #     top_right.SetLogy()

    data_hist.GetYaxis().SetTitle(y_title)
    data_hist.GetYaxis().CenterTitle()
    data_hist.GetYaxis().SetTitleOffset(0.9)
    data_hist.GetYaxis().SetTitleSize(0.05)
    data_hist.GetYaxis().SetLabelSize(0.05)

    data_hist.Draw("axis")

    for key in reversed(list(typehistdict.keys())):
        typehistdict[key].Draw("HIST SAME")

    mc_hist.Draw("HIST SAME")
    data_hist.Draw("Same E1 X0")
    data_stat.Draw("SAME AP E1 Z XO")

    bottom.cd()

    # ratio = MnvH1D()
    # # ratio = MakeDataMCRatio(data_hist,mc_band)
    # mnv_ratio = MakeDataMCRatio(mnv_data, mnv_mc)
    # ratio = mnv_ratio.GetCVHistoWithError()
    # ratio_stat = mnv_ratio.GetCVHistoWithStatError()
    mnv_ratio = MakeDataMCRatioForPlot(mnv_data, mnv_mc)
    ratio, ratio_stat = GetDataHistsForPlot(mnv_ratio)
    typesratiodict= MakeTypesMCRatioDict(typehistdict, mc_hist)

    ratio.SetFillStyle(1001)
    ratio.SetMinimum(0.0)
    ratio.SetMaximum(2.0)
    # ratio.SetLineWidth(round(ratio.GetLineWidth()*areaScale))
    ratio.SetLineColor(ROOT.kBlack)

    ratio_stat.SetLineWidth(ratio.GetLineWidth())
    ratio_stat.SetLineColor(ROOT.kBlack)
    ratio_stat.SetMarkerStyle(1)
    ratio_stat.SetMarkerSize(1)


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
    ratio.SetLineWidth(2)
    ratio.Draw("E1 X0")
    ratio_stat.Draw("SAME E1 X0")
    # Now do mc uncertainties
    mcerror = TH1D()
    mnv_mc.SetFillStyle(1001)
    mcerror = TH1D(mnv_mc.GetTotalError(False, True, False))
    for bin in range(0, mcerror.GetXaxis().GetNbins() + 2):
        mcerror.SetBinError(bin, max(mcerror.GetBinContent(bin), 1.0e-9))
        mcerror.SetBinContent(bin, 1.0)
    mcerror.SetLineColor(typescolors[0])
    # mcerror.SetLineColor(ROOT.TColor.GetColorDark(typescolors[0]))
    mcerror.SetLineWidth(typeslinewidth1D)
    # mcerror.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
    mcerror.SetFillColor(ROOT.kRed-10)
    # mcerror.Draw("same E2")

    # Now do a line at 1
    straightline = TH1D()
    straightline = mcerror.Clone()
    straightline.SetFillStyle(0)
    straightline.SetFillColor(typescolors[0])
    straightline.Draw("hist same")

    for key in typesratiodict:
        typesratiodict[key].SetLineWidth(typeslinewidth1D)
        typesratiodict[key].Draw("HIST SAME")

    ratio.Draw("Axis same")

    top_right.cd()
    prelim = AddPreliminary()
    # titleonplot = MakeTitleOnPlot()
    prelim.DrawLatex(x1.value-lat_xoffset, y1.value-2*lat_yoffset-0.01, "MINER#nuA Work In Progress")

    multip_text = ROOT.TLatex()
    multip_text.SetNDC()
    multip_text.SetTextSize(0.05*1.03)
    multip_text.SetTextAlign(11)
    multip_text.SetTextFont(42)
    multip_text.DrawLatex(0.04,0.9, "10 #times")
    
    top.cd()
    axismultip_text = ROOT.TLatex()
    axismultip_text.SetNDC()
    axismultip_text.SetTextSize(0.05)
    axismultip_text.SetTextAlign(33)
    axismultip_text.SetTextFont(42)
    axismultip_text.DrawLatex(1-tmp_pad_rmarg/2, .995, "#times10^{#minus36}")

    top_right.cd()
    arrow = ROOT.TArrow(0.00, 0.85, 0.25, 0.85, 0.05, "|>")
    arrow.SetLineWidth(3)
    arrow.SetAngle(40)
    arrow.DrawArrow(0.2, 0.1, 0.2, 0.7, 0.05)
    # top.cd()
    # prelim = AddPreliminary()
    # # titleonplot = MakeTitleOnPlot()
    # prelim.DrawLatex(x1.value-lat_xoffset, y1.value-2*lat_yoffset-0.01, "MINER#nuA Work In Progress")
    # # titleonplot.DrawLatex(0.37, 0.9, plottitle)

    thename += "_Types_altaxis"

    # if dotuned:
    #     canvas_name += "_tuned" 


    cc.Print(os.path.join(outdirname, thename + ".png"))
    cc.Print(os.path.join(outdirname, "source", thename + ".C"))
    cc.Print(os.path.join(outdirname, canvas_name + ".pdf"),"Title:%s"%(canvas_title + " Types altaxis"))

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
    thetitle = canvas_title + " Error Summary"
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

    # canvas_name = thename + "_FinalStates"
    thename += "_FinalStates"
    # if dotypes:
    #     canvas_name = thename + "Types"
    # if dotuned:
    #     canvas_name += "_tuned" 

    cc.Print(os.path.join(outdirname, thename + ".png"))
    cc.Print(os.path.join(outdirname, "source", thename + ".C"))
    cc.Print(os.path.join(outdirname,canvas_name + ".pdf"),"Title:%s"%(thetitle))


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

    # mnvh.SetMarkerStyle(data_marker_style)
    # mnvh.SetMarkerColor(ROOT.kBlack)
    # mnvh.SetLineWidth(2)
    # mnvh.SetLineColor(ROOT.kBlack)
    # mnvh.SetLineStyle(1)
    # mnvh.SetMarkerSize(data_marker_size)

    hist = mnvh.GetCVHistoWithError(True,False)
    hist.SetMarkerStyle(data_marker_style)
    hist.SetMarkerColor(ROOT.kBlack)
    hist.SetLineWidth(typeslinewidth)
    hist.SetLineColor(ROOT.kBlack)
    hist.SetLineStyle(1)
    hist.SetMarkerSize(data_marker_size)

    stat = mnvh.GetCVHistoWithStatError()
    stat.SetMarkerStyle(1)
    stat.SetMarkerColor(ROOT.kBlack)
    stat.SetLineWidth(typeslinewidth)
    stat.SetLineColor(ROOT.kBlack)
    stat.SetFillColorAlpha(ROOT.kPink, 0.3)
    stat.SetLineStyle(1)
    stat.SetMarkerSize(1)

    return hist, stat

def GetMCHistsForPlot(mnv_mchist):
    mnvh = mnv_mchist.Clone()

    band = mnvh.GetCVHistoWithError(True,False)
    # band.SetFillColor(ROOT.kRed - 10)
    # band.SetFillColorAlpha(typescolors[0], 0.3)
    band.SetFillColorAlpha(catscolors[0], 0.3)
    band.SetFillStyle(1001)
    band.SetLineColor(ROOT.kRed)
    band.SetMarkerStyle(0)

    hist = mnvh.GetCVHistoWithError(True,False)
    hist.SetFillColor(0)
    # hist.SetLineColor(2)
    # hist.SetLineColor(typescolors[0])
    hist.SetLineColor(catscolors[0])
    # hist.SetLineColor(ROOT.TColor.GetColorDark(typescolors[0]))
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
            data_mnvprojtot = data_mnv2d_unscaled.ProjectionX("%s_proj%s"%(data_mnv2d_unscaled.GetName(),projaxis), 0, data_mnv2d_unscaled.GetNbinsY()+2, "width")# e")
            mc_mnvprojtot = mc_mnv2d_unscaled.ProjectionX("%s_proj%s"%(mc_mnv2d_unscaled.GetName(),projaxis), 0, mc_mnv2d_unscaled.GetNbinsY()+2, "width")# e")
        if projaxis == "y":
            data_mnvprojtot = data_mnv2d_unscaled.ProjectionY("%s_proj%s"%(data_mnv2d_unscaled.GetName(),projaxis), 0, data_mnv2d_unscaled.GetNbinsX()+2, "width")# e")
            mc_mnvprojtot = mc_mnv2d_unscaled.ProjectionY("%s_proj%s"%(mc_mnv2d_unscaled.GetName(),projaxis), 0, mc_mnv2d_unscaled.GetNbinsX()+2, "width")# e")

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
        print(plot_bins)
        # First do the total projections
        DrawDataMCPlot1D(data_mnvprojtot, mc_mnvprojtot, proj_xtitle, z_title, outdirname, thename+"_totalproj", canvas_title+" total proj")

        print("plot bins:", plot_bins)
        print("canvas n x bins: ",canvas_nxbins,",\t canvas n y bins: ",canvas_nybins)
        
        ROOT.gStyle.SetErrorX(0) # This turns off the horizontal error bars
        ROOT.gStyle.SetEndErrorSize(end_error_size/2) # This makes the ticks at the end of the error bars longer

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
            # binrange_latex.SetTextSize(0.025)
            binrange_latex.SetTextSize(0.028)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)

            multip_string = "#times {:g}".format(float('{:.{p}g}'.format(tmp_pad_scale, p=2)))
            multip_latex = ROOT.TLatex()
            multip_latex.SetTextAlign(32)
            multip_latex.SetNDC()
            multip_latex.SetTextFont(42)
            # multip_latex.SetTextSize(0.028)
            # multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.05), multip_string)
            multip_latex.SetTextSize(0.03)
            multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.06), multip_string)
            pad.Modified()
        pad = gc.cd(n_pads+1)
        padwidth = 1 - pad.GetLeftMargin() - pad.GetRightMargin()
        # leg = TLegend(pad.GetLeftMargin()+0.5,(1.-(pad.GetTopMargin())-0.05),pad.GetRightMargin()-0.5,(pad.GetBottomMargin()+0.05))
        leg = TLegend(pad.GetLeftMargin()+padwidth/10,(1.-(pad.GetTopMargin())-0.05), 1 - (pad.GetRightMargin() + padwidth/10),(pad.GetBottomMargin()+0.05))
        leg.SetNColumns(1)
        leg.SetBorderSize(0)
        leg.SetFillColor(-1)
        leg.SetTextSize(round(legendfontsize/3))

        leg.AddEntry(data_hist_list[0], "Data","pe")
        leg.AddEntry(mc_band_list[0], "Simulation","fl")

        leg.Draw()
        pad.Modified()
        gc.SetHistTexts()
        gc.Draw()
        # canvas_name = thename + "XSec_Proj" + projaxis

        gc.Print(os.path.join(outdirname, thename + ".png"))
        gc.Print(os.path.join(outdirname,"source", thename + ".C"))
        gc.Print(os.path.join(outdirname,canvas_name + ".pdf"),"Title:%s"%(thetitle))

        # del gc

        gc.cd()
        gc.ResetPads()
        leg.Clear()
        gc.SetYTitle("%s Data / MC"%(z_title))
        gc.SetXTitle(proj_xtitle)
        gc.Modified()
        gc.Update()

        ratio_list = []
        ratio_stat_list = []
        mcerror_list = []
        straightline_list = []
        for i in range(n_pads):
            # # ratio = MakeDataMCRatio(data_hist_list[i],mc_band_list[i])
            # ratio_mnvh = MakeDataMCRatio(data_mnvproj_list[i],mc_mnvproj_list[i])
            ratio_mnvh = MakeDataMCRatioForPlot(data_mnvproj_list[i],mc_mnvproj_list[i])
            ratio_hist, ratio_stat = GetDataHistsForPlot(ratio_mnvh)
            ratio_hist.SetMinimum(0.001)
            ratio_hist.SetMaximum(3)
            # ratio_stat = MakeDataMCRatio(data_stat_list[i],mc_band_list[i])

            ratio_hist.SetFillStyle(1001)
            ratio_hist.SetLineColor(ROOT.kBlack)
            ratio_hist.SetLineWidth(2)
            # ratio.SetTitle("")
            if n_pads < 8:
                ratio_hist.GetXaxis().SetNdivisions(207)
            ratio_hist.GetYaxis().SetNdivisions(205)
            ratio_list.append(ratio_hist)
            ratio_stat_list.append(ratio_stat)
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
            ratio_stat_list[i].Draw("E1 X0 same")
            ratio_list[i].Draw("E1 X0 same")
            ratio_list[i].Draw("axis same")
            
            range_string = "{loedge} < {var} < {hiedge}".format(loedge = round(plot_bins[i], 3), var =proj_ytitle.split(" (")[0], hiedge = round(plot_bins[i+1], 3))
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            # binrange_latex.SetTextSize(0.025)
            binrange_latex.SetTextSize(0.03)
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

        leg.AddEntry(data_hist_list[0], "Data","pe")
        leg.AddEntry(mc_band_list[0], "Simulation","fl")

        leg.Draw()
        pad.Modified()
        gc.SetHistTexts()
        gc.Draw()
        gc.Print(os.path.join(outdirname, thename + "_ratio.png"))
        gc.Print(os.path.join(outdirname,"source", thename + "_ratio.C"))
        gc.Print(os.path.join(outdirname,canvas_name + ".pdf"),"Title:%s Ratio"%(thetitle))

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
        gc.Print(os.path.join(outdirname,canvas_name + ".pdf"), "Title:%s Error Summary"%(thetitle))

            
        del gc


def DrawDataMCPlot1D_new(i_data_hist, i_mc_hist, i_mc_typeshistdict, x_title, y_title, outdirname, canvas_name, canvas_title,nametag = ""):
    # mnvPlotter = SetupErrorSummary(MnvPlotter(8))
    mnvPlotter = MnvPlotter(8)
    
    mnv_data = i_data_hist.Clone()
    mnv_mc = i_mc_hist.Clone()
    mnv_data.Scale(1.0, "width")
    mnv_mc.Scale(1.0, "width")

    my_catstodo = catstodo
    tmp_dotypes = False
    for key in i_mc_typeshistdict.keys():
        if key not in catstodo:
            my_catstodo = typestodo
            tmp_dotypes = True
            break
    # This just hacks to get a legend that works better if you do backgrounds
    if tmp_dotypes:
        typesttodo_leg = []
        if 11 in my_catstodo:
            types_order_leg = []
            for itype in my_catstodo:
                if type(itype) == str:
                    continue
                if itype > 10:
                    continue
                typestodo_leg.append(itype)
                typestodo_leg.append(itype+10)
        else:
            typesttodo_leg = my_catstodo[1:]
       
    my_catscolors = catscolors
    my_catsnames  = catsnames
    mc_typehistdict = {}
    stack = THStack("stack","")
    for cat in reversed(my_catstodo[1:]):
        hist = i_mc_typeshistdict[cat].Clone()
        hist.Scale(1.0, "width")
        hist.SetLineColor(ROOT.kBlack)
        if typeslinedarker:
            hist.SetLineColor(ROOT.TColor.GetColorDark(my_catscolors[cat]))
        hist.SetFillColor(my_catscolors[cat])
        hist.SetLineWidth(typeslinewidth1D+1)
        # if cat in bkgcats:
        #     hist.SetFillStyle(bkgfillstyle[cat]+100)
            # hist.SetFillColor(ROOT.TColor.GetColorDark(my_catscolors[cat]))
        if type(cat) == int:
            hist.SetLineColor(ROOT.kBlack)
            if cat >= 10: 
                hist.SetFillStyle(bkgfillstyle[cat]+100)
                # hist.SetFillColor(ROOT.TColor.GetColorDark(my_catscolors[cat]))
        stack.Add(hist)
        mc_typehistdict[cat] = hist.Clone()

    thename = canvas_name + nametag
    thetitle = canvas_title 
    if tmp_dotypes:
        thetitle += " Types"
    else: 
        thetitle += " Final States"

    ysize = _ysize
    xsize = _xsize

    mnv_data.SetMarkerStyle(data_marker_style)
    mnv_data.SetMarkerColor(ROOT.kBlack)
    mnv_data.SetLineWidth(2)
    mnv_data.SetLineColor(ROOT.kBlack)
    mnv_data.SetLineStyle(1)
    mnv_data.SetMarkerSize(data_marker_size)
    data_hist, data_stat = GetDataHistsForPlot(mnv_data)

    # Stuff for doing the ratios
    mc_hist = mnv_mc.GetCVHistoWithError(True,False)
    mc_hist.SetFillColor(0)
    mc_hist.SetLineColor(my_catscolors["mctot"])
    mc_hist.SetLineStyle(1)
    mc_hist.SetLineWidth(typeslinewidth1D+1)
    mnv_ratio = MakeDataMCRatioForPlot(mnv_data, mnv_mc)
    ratio, ratio_stat = GetDataHistsForPlot(mnv_ratio)

    ratio.SetFillStyle(0)
    ratio.SetMinimum(0.0001)
    ratio.SetMaximum(1.999)

    ratio.SetLineColor(ROOT.kBlack)
    ratio.SetLineWidth(2)
    ratio_stat.SetLineColor(ROOT.kBlack)
    ratio_stat.SetMarkerStyle(1)
    ratio_stat.SetMarkerSize(1)

    typesratio_dict = {}
    for key in my_catstodo[1:]:
        # tmp_typesratio = MakeDataMCRatio(mc_typehistdict[key], mnv_mc)
        tmp_typesratio = mc_typehistdict[key].Clone()
        tmp_typesratio.Divide(tmp_typesratio, mnv_mc,1.0,1.0)
        tmp_typesratio.SetLineWidth(typeslinewidth1D + 1)
        tmp_typesratio.SetFillStyle(0)
        tmp_typesratio.SetFillColor(0)
        tmp_typesratio.SetLineColor(catscolors[key])
        if tmp_dotypes:
            if key > 10:
                tmp_typesratio.SetLineStyle(2)
            else:
                if typeslinedarker:
                    tmp_typesratio.SetLineColor(ROOT.TColor.GetColorDark(catscolors[key]))

        typesratio_dict[key] = tmp_typesratio
    typesratio_stack_dict = {}
    # if tmp_dotypes:
    #     for key in typestodo_leg:
    #         if key > 10:
    #             tmp_hist = typesratio_dict[key].Clone()
    #             tmp_hist.SetLineStyle(7)
    #             tmp_hist.SetLineWidth(typeslinewidth1D + 1)
    #             print(key)
    #             tmp_hist.Print()
    #             tmp_stack = THStack()
    #             tmp_stack.Add(tmp_hist)
    #             typesratio_stack_dict[key-10] = tmp_stack
    #     for key in typestodo_leg:
    #         if key <= 10:
    #             tmp_hist = typesratio_dict[key].Clone()
    #             tmp_hist.SetLineWidth(typeslinewidth1D + 1)
    #             tmp_hist.Print()
    #             if tmp_hist.GetEntries() == 0: continue
    #             typesratio_stack_dict[key].Add(tmp_hist)
    #             # typesratio_stack_dict[key].SetFillStyle(0)
    #             # typesratio_stack_dict[key].SetFillColor(0)
    #     # sys.exit(1)
    if tmp_dotypes and 11 in my_catstodo[1:]:
        for key in reversed(my_catstodo[1:]):
            if key > 10: continue
            tmp_hist = typesratio_listdict[key].Clone()
            tmp_stack = THStack()
            if key + 10 not in my_catstodo[1:]:
                # tmp_stack.Add(tmp_hist)
                typesratiostack_listdict[key].append(tmp_hist)
                continue
            tmp_hist_bkg = typesratio_listdict[key+10].Clone()
            tmp_hist_bkg.SetLineStyle(7)
            tmp_stack.Add(tmp_hist_bkg)
            if tmp_hist.GetEntries() == 0: continue
            typesratio_stack_dict[key].Add(tmp_hist)
    
    tmp_mnvmc_band = mnv_mc.Clone()
    tmp_mnvmc_band.ClearAllErrorBands()
    tmp_mnvmc_band.AddMissingErrorBandsAndFillWithCV(mnv_mc)
    tmp_mnvmc_band.Divide(tmp_mnvmc_band,mnv_mc,1.0,1.0)
    tmp_mnvmc_band.SetFillColor(catscolors[0])
    tmp_mnvmc_band.SetFillColorAlpha(catscolors[0],0.3)
    tmp_mnvmc_band.SetLineColor(catscolors[0])
    tmp_mnvmc_band.SetLineWidth(typeslinewidth1D + 1)
    tmp_mnvmc_band.SetMarkerStyle(0)
    tmp_band = tmp_mnvmc_band.GetCVHistoWithError().Clone()
    
    straightline = tmp_band.Clone()
    straightline.SetFillStyle(0)
    straightline.SetFillColor(0)
    # ROOT.gStyle.SetErrorX(0) # This turns off the horizontal error bars
    ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer

    # Now set up the canvas
    cc = ROOT.TCanvas(thename, thetitle, round(xsize), round(ysize))
    cc.SetCanvasSize(_xsize,_ysize)
    cc.SetLeftMargin(0.25)
    cc.SetRightMargin(0.15)
    cc.SetBottomMargin(0.1)
    cc.SetFrameLineWidth(1)

    top = ROOT.TPad("hist", "hist", 0, ratio_frac, 1.0, 1.0)
    top.SetRightMargin(pad_rmarg)
    top.SetLeftMargin(pad_lmarg)
    top.SetTopMargin(topmarg)
    top.SetBottomMargin(0)
    top.SetFrameLineWidth(1)

    bottom = ROOT.TPad("Ratio", "Ratio", 0, 0, 1.0, ratio_frac)
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
    if x_title.split(" (")[0] in scaleY:
        top.SetLogy()

    # top.SetLogy()
    # # E1 draws a point with error bars, X0 turns off horizontal error bars
    # data_hist.Draw("9 E1 X0")

    stack.Draw()

    stack.GetYaxis().SetTitle(y_title)
    stack.GetYaxis().SetTitleFont(axistitle_font)
    stack.GetYaxis().CenterTitle()
    stack.GetYaxis().SetTitleOffset(0.6)
    stack.GetYaxis().SetTitleSize(0.07)
    stack.GetYaxis().SetLabelSize(0.05)

    # stack.SetMaximum(1.2 * max(mnv_data.GetMaximum(),mnv_mc.GetMaximum()))
    stack.SetMaximum(1.2 * GetPadMax(mnv_data.GetMaximum(),mnv_mc.GetMaximum(),True))
    stack.SetMinimum(stack.GetMaximum()*0.001)
    stack.Draw("hist ][ 9")

    data_hist.Draw("PE1 X0 same 9")

    # stack.Draw("9 HIST same")    
    data_stat.Draw("9 SAME %s"%staterror_drawopt)
    data_hist.Draw("9 Same PE1 X0")

    padwidth = 1 - cc.GetLeftMargin() - cc.GetRightMargin()
    padheight = 1 - cc.GetTopMargin() - cc.GetBottomMargin()
    x1 = cc.GetLeftMargin() + 0.7 * padwidth
    if tmp_dotypes:
        x1 = cc.GetLeftMargin() + 0.5 * padwidth
    y1 = 1. - cc.GetTopMargin() - 0.01
    x2 = 1.-  padwidth/10 
    y2 = cc.GetBottomMargin() + 0.4 * padheight
    leg = TLegend(x1,y1,x2,y2)
    leg.SetTextSize(legendfontsize * 1.05)
    leg.SetNColumns(1)
    leg.SetBorderSize(0)
    leg.SetFillColor(-1)
    ROOT.gStyle.SetLegendFont(42)
    leg.AddEntry(data_hist, "Data","pe")
    leg.AddEntry(tmp_band, my_catsnames["mctot"],"fl")
    # leg.AddEntry(mc_hist, my_catsnames["mctot"],"fl")
    if tmp_dotypes:
        for cat in typestodo_leg:
            leg.AddEntry(mc_typehistdict[cat],my_catsnames[cat], "f")
        leg.SetNColumns(2)

    else:
        for cat in my_catstodo[1:]:
            leg.AddEntry(mc_typehistdict[cat],my_catsnames[cat], "f")
    
    leg.Draw()
    top.Modified()
    top.Update()

    bottom.cd()

    ratio.SetTitle("")            
    ratio.GetYaxis().SetTitle("Data / MC")
    ratio.GetYaxis().SetTitleFont(axistitle_font)
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetTitleSize(0.07 * areaScale)
    ratio.GetYaxis().SetTitleOffset(0.6 / areaScale)
    ratio.GetYaxis().SetLabelSize(0.05 * areaScale)
    ratio.GetYaxis().SetNdivisions(505)

    # ratio.GetXaxis().SetTitle(vars_info[c_var]["title"])
    ratio.GetXaxis().SetTitle(x_title)
    ratio.GetXaxis().CenterTitle()
    ratio.GetXaxis().SetTitleSize(0.05 * areaScale)
    ratio.GetXaxis().SetLabelSize(ratio.GetXaxis().GetLabelSize() * areaScale*1.5)
    
    ratio.Draw("9 E1 X0")

    # Now do mc uncertainties
    tmp_band.Draw("9 E2 same ][")
    straightline.Draw("9 Hist same, ][")

    if tmp_dotypes:
        for cat in reversed(typestodo_leg):
            if cat > 10: continue
            typesratio_stack_dict[cat].Draw("9 HIST NOCLEAR SAME")
    else:
        for cat in reversed(my_catstodo):
            if cat == "data": continue
            typesratio_dict[cat].Draw("9 HIST SAME")

    ratio_stat.Draw("9 %s SAME"%staterror_drawopt)
    ratio.Draw("9 same E1 X0")
    ratio.Draw("9 same axis")
    bottom.Modified()
    bottom.Update()

    top.cd()
    prelim = AddPreliminary()

    # prelim.DrawLatex(x1.value-lat_xoffset, y1.value-2*lat_yoffset-0.01, "MINER#it{#nu}A Work In Progress")
    prelim.DrawLatex(x1-lat_xoffset, y2-2*lat_yoffset-0.01, "MINER#it{#nu}A Work In Progress")
    thename += "_Types"
    top.Modified()
    top.Update()
    if x_title.split(" (")[0] in scaleX:
        top.SetLogx()
        bottom.SetLogx()
        top.Modified()
        top.Update()
        bottom.Modified()
        bottom.Update()
    # top.cd()
    # top.Draw()

    # cc.Draw()
    # cc.Print(os.path.join(outdirname, thename + ".png"))
    # cc.Print(os.path.join(outdirname, "source", thename + ".C"))
    cc.Print(os.path.join(outdirname, canvas_name + ".pdf"),"Title:%s Types"%(thetitle))

    cc.cd()
    cc.Clear()
    cc.Modified()
    cc.Update()

    
    # Now do the unstacked hist
    mc_band = mc_hist.Clone()
    mc_band.SetFillColor(my_catscolors["mctot"])
    mc_band.SetFillColorAlpha(catscolors["mctot"],0.4)
    mc_band.SetLineColor(catscolors["mctot"])
    mc_band.SetLineWidth(typeslinewidth1D + 1)
    mc_band.SetMarkerStyle(0)
    mc_line = mc_band.Clone()
    mc_line.SetFillStyle(0)
    mc_line.SetFillColor(0)
    top = ROOT.TPad("hist", "hist", 0, ratio_frac, 1.0, 1.0)
    top.SetRightMargin(pad_rmarg)
    top.SetLeftMargin(pad_lmarg)
    top.SetTopMargin(topmarg)
    top.SetBottomMargin(0)
    top.SetFrameLineWidth(1)

    bottom = ROOT.TPad("Ratio", "Ratio", 0, 0, 1.0, ratio_frac)
    bottom.SetRightMargin(pad_rmarg)
    bottom.SetLeftMargin(pad_lmarg)
    bottom.SetBottomMargin(bottommarg)
    bottom.SetTopMargin(0)
    bottom.SetFrameLineWidth(1)

    top.Draw()    
    bottom.Draw()

    top.cd()
    top.Draw()
    if tmp_dotypes:
        leg.Clear()
        leg.SetNColumns(1)
        leg.AddEntry(data_hist, "Data", "fl")
        leg.AddEntry(tmp_band, my_catsnames["mctot"],"fl")

    if x_title.split(" (")[0] in scaleY:
        top.SetLogy()
    
    for hist in stack.GetHists():
        hist.SetFillStyle(0)
        if tmp_dotypes:
            hist.SetLineWidth(0)
            continue
        hist.SetLineWidth(typeslinewidth1D+1)
        
    stack.Draw("9 axis")
    stack.Draw("9 nostack, hist same")
    mc_band.Draw("9 E2 ][ same")
    stack.Draw("9 nostack, hist same")
    mc_line.Draw("9 hist same")
    data_hist.Draw("9 E1 X0, same")
    data_stat.Draw("9 SAME %s"%staterror_drawopt)
    leg.Draw()
    top.Modified()
    top.Update()
    
    bottom.cd()
    bottom.Draw()
    if x_title.split(" (")[0] in scaleY:
        bottom.SetLogy()
    ratio.Draw("9 E1 X0")

    # Now do mc uncertainties
    tmp_band.Draw("9 E2 same ][")
    straightline.Draw("9 Hist same, ][")

    # if tmp_dotypes:
    #     for cat in reversed(typestodo_leg):
    #         if cat > 10: continue
    #         typesratio_stack_dict[cat].Draw("9 HIST NOCLEAR SAME")
    # else:
    if not tmp_dotypes:
        for cat in reversed(my_catstodo):
            if cat == "data": continue
            typesratio_dict[cat].Draw("9 HIST SAME")

    ratio_stat.Draw("9 %s SAME"%staterror_drawopt)
    ratio.Draw("9 same E1 X0")
    ratio.Draw("9 same axis")
    bottom.Modified()
    bottom.Update()

    top.cd()
    prelim.DrawLatex(x1-lat_xoffset, y2-2*lat_yoffset-0.01, "MINER#it{#nu}A Work In Progress")
    thename += "_Types_unstack"
    top.Modified()
    top.Update()

    if x_title.split(" (")[0] in scaleX:
        top.SetLogx()
        bottom.SetLogx()
        top.Modified()
        top.Update()
        bottom.Modified()
        bottom.Update()

    top.cd()
    top.Draw()
    cc.Draw()
    # cc.Print(os.path.join(outdirname, thename + ".png"))
    # cc.Print(os.path.join(outdirname, "source", thename + ".C"))
    cc.Print(os.path.join(outdirname, canvas_name + ".pdf"),"Title: %s NoStack"%(thetitle))

    cc.cd()
    cc.Clear()
    cc.Modified()
    cc.Update()

    # del stack
    # del cc


def DrawDataMCPlot2D_new(i_data_hist, i_mc_hist, i_mc_typeshistdict, x_varname, x_units, x_bins, y_varname, y_units, y_bins, z_title, outdirname, canvas_name, canvas_title, nametag,i_multipliers = [], do_stack = True, do_nostack = True):
    data_mnv2d = i_data_hist.Clone()
    mc_mnv2d = i_mc_hist.Clone()
    data_mnv2d.Scale(1.0, "width")
    mc_mnv2d.Scale(1.0, "width")

    # These don't get bin width normalized before they get used for the total 1D projection hists
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

    n_xbins = data_mnv2d.GetNbinsX()
    n_ybins = data_mnv2d.GetNbinsY()
    print("hist n x bins: ",n_xbins,",\t hist n y bins: ",n_ybins)
    # my_catstodo = catstodo[1:]
    my_catstodo = [cat for cat in catstodo[1:]]
    tmp_dotypes = False
    for key in i_mc_typeshistdict.keys():
        if key not in my_catstodo:
            # my_catstodo = typestodo[1:]
            my_catstodo = [cat for cat in typestodo[1:]]
            tmp_dotypes = True
            break
    # This just hacks to get a legend that works better if you do backgrounds
    if tmp_dotypes:
        typesttodo_leg = []
        if 11 in my_catstodo:
            types_order_leg = []
            for itype in my_catstodo:
                if type(itype) == str:
                    continue
                if itype > 10:
                    continue
                typestodo_leg.append(itype)
                typestodo_leg.append(itype+10)
        else:
            typesttodo_leg = my_catstodo[1:]
            


    x_title = "%s (%s)"%(x_varname, x_units)
    y_title = "%s (%s)"%(y_varname, y_units)

    for projaxis in ["x","y"]:

        # thetitle = "%s %s %s proj%s"%(b_sample,c_var,"sigma",projaxis)
        thename = "%s_%s_proj%s"%(canvas_name, nametag, projaxis)
        thetitle = "%s%s proj%s"%(canvas_title,nametag.replace("_"," "),projaxis)
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
        
        # Make the projections
        data_mnvproj_list = MakeProjHistList(data_mnv2d,projaxis)
        mc_mnvproj_list = MakeProjHistList(mc_mnv2d,projaxis)
        mc_typesproj_listdict = {}

        for key in mc_typehistdict:
            if key not in mc_typesproj_listdict:
                mc_typesproj_listdict[key] = []
            tmp_list = MakeProjHistList(mc_typehistdict[key],projaxis)
            for hist in tmp_list:
                tmp_hist = hist.Clone()
                tmp_hist.SetFillColor(catscolors[key])
                # if key in bkgcats:
                #     # tmp_hist.SetFillStyle(bkgfillstyle)
                #     tmp_hist.SetFillStyle(bkgfillstyle[key])
                if tmp_dotypes:
                    # if key >= 10: tmp_hist.SetFillStyle(bkgfillstyle)
                    if key >= 10: 
                        tmp_hist.SetFillStyle(bkgfillstyle[key])
                    tmp_hist.SetLineColor(ROOT.TColor.GetColorDark(catscolors[key]))
                    # tmp_hist.SetLineColor(ROOT.kBlack)
                    mc_typesproj_listdict[key].append(tmp_hist.Clone())
                    continue

                tmp_hist.SetLineColor(ROOT.TColor.GetColorDark(catscolors[key]))
                mc_typesproj_listdict[key].append(tmp_hist.GetCVHistoWithStatError())

        # TODO: the 1D total projections
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
        projtot1d_y_title = z_title
        tmp_units = x_units
        if projaxis == "x":
            # tmp_units = "(%s"%x_title.split(" (")[1]
            # projtot1d_y_title = "Counts / %s"%tmp_units
            tmp_varname = x_varname
            tmp_units = x_units
        if projaxis == "y":
            # tmp_units = "(%s"%y_title.split(" (")[1]
            # projtot1d_y_title = "Counts / %s"%tmp_units
            tmp_varname = y_varname
            tmp_units = y_units
        if "#sigma" in z_title:
            projtot1d_y_title = "d#sigma /^{} d%s (cm^{2}/^{}%s/^{}Nucleon)"%(tmp_varname,tmp_units)
        else:
            projtot1d_y_title = "Counts / (%s)"%tmp_units

        # TODO
        DrawDataMCPlot1D_new(data_mnvprojtot, mc_mnvprojtot, mc_typestotproj_dict, proj_xtitle, projtot1d_y_title, outdirname, canvas_name, thetitle,"_totalproj%s"%(projaxis))
        # if "E_{Avail}" in proj_xtitle and not do_comparison:
        # if "E_{Avail}" in proj_xtitle:
        #     DrawDataMCTypesPlot1D_AxisChange(data_mnvprojtot, mc_mnvprojtot, mc_typestotproj_dict, proj_xtitle, z_title, outdirname, canvas_name, canvas_title+" total proj")
 
        # ROOT.gStyle.SetErrorX(0.) # This turns off the horizontal error bars
        ROOT.gStyle.SetEndErrorSize(end_error_size/2) # This makes the ticks at the end of the error bars longer


        n_pads = len(data_mnvproj_list)
        print(n_pads)

        # These are the hists w/ total error
        data_hist_list = []
        # These are the hists w/ just stat error
        data_stat_list = []
        # These are just used for the CV
        mc_hist_list = []
        # # These are used for the errors, to make a band around MC
        mc_band_list = []

        for hist in data_mnvproj_list:
            data_hist, data_stat = GetDataHistsForPlot(hist)
            data_hist.SetMarkerSize(data_marker_size2d)
            data_stat.SetMarkerSize(data_marker_size2d)
            data_hist_list.append(data_hist)
            data_stat_list.append(data_stat)
        # TODO: do I actually use these?
        for hist in mc_mnvproj_list:
            mc_hist, mc_band = GetMCHistsForPlot(hist)
            mc_hist_list.append(mc_hist)
            mc_band_list.append(mc_band)
        # maxlist = [hist.GetMaximum() for hist in data_hist_list] + [hist.GetMaximum() for hist in mc_hist_list]
        maxlist = [GetPadMax(data_hist_list[i],mc_hist_list[i], True) for i in range(len(data_hist_list))]
        global_max = max(maxlist)

        calc_tmp_pad_scale = True
        multipliers = []
        if len(i_multipliers) == n_pads:
            calc_tmp_pad_scale = False
            multipliers = i_multipliers
            if "#sigma" in z_title:
                global_max = 4.0E-37
        
        # Get the stacks ready
        stack_list = []
        for i in range(n_pads):
            stack_list.append(THStack("%s_%0.3d"%(key,i),"%s_%0.3d"%(key,i)))
        
        for i in range(n_pads):
            tmp_pad_scale = 1.0
            if calc_tmp_pad_scale:
                tmp_pad_max = 0.0
                tmp_pad_max = GetPadMax(data_hist_list[i],mc_hist_list[i], True)
                if tmp_pad_max == 0:
                    tmp_pad_max = 1.0
                tmp_pad_scale = eval('{:.{p}g}'.format(global_max / tmp_pad_max, p=3))
                multipliers.append(tmp_pad_scale)
            else:
                tmp_pad_scale = multipliers[i]
            
            data_hist_list[i].Scale(tmp_pad_scale)
            data_stat_list[i].Scale(tmp_pad_scale)
            mc_hist_list[i].Scale(tmp_pad_scale)
            mc_band_list[i].Scale(tmp_pad_scale)
            mc_hist_list[i].SetLineWidth(typeslinewidth+1)
            mc_band_list[i].SetLineWidth(typeslinewidth)
            # tmp_stack = THStack()
            # for key in mc_typesproj_listdict:
            for cat in reversed(my_catstodo):
                # if cat == "data": continue
                mc_typesproj_listdict[cat][i].Scale(tmp_pad_scale)
                tmp_type_hist = mc_typesproj_listdict[cat][i].Clone()
                # tmp_type_hist.Scale(tmp_pad_scale)
                # if cat in bkgcats:
                #     tmp_type_hist.SetFillStyle(bkgfillstyle[cat])
                hist.SetLineColor(ROOT.TColor.GetColorDark(catscolors[cat]))
                if type(cat) == int:
                    # hist.SetLineColor(ROOT.kBlack)
                    if cat >= 10: 
                        hist.SetFillStyle(bkgfillstyle[cat])

                tmp_type_hist.SetLineWidth(typeslinewidth)
                stack_list[i].Add(tmp_type_hist)

            data_hist_list[i].SetMaximum(1.2 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
            data_hist_list[i].SetMinimum(0.001*data_hist_list[i].GetMaximum())

            if proj_xtitle.split(" (")[0] in scaleY:
                # pad.SetLogy()
                data_hist_list[i].SetMaximum(1.5 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
                # data_hist_list[i].SetMinimum(data_hist_list[i].GetMaximum()*1000)
            
            data_hist_list[i].GetXaxis().SetNdivisions(505)
            data_hist_list[i].GetYaxis().SetNdivisions(505)
            data_hist_list[i].GetYaxis().SetLabelSize(data_hist_list[i].GetXaxis().GetLabelSize())
        # print(multipliers)
        # if projaxis == "y":
        #     sys.exit(1)
        gc = PanelCanvas(thename, canvas_nxbins, canvas_nybins, round(xsize), round(ysize))
        gc.SetTopMargin(0.05)
        gc.SetLeftMargin(0.08)
        gc.SetRightMargin(0.05)
        gc.SetBottomMargin(0.1)
        # gc.SetFrameLineWidth(1)
        gc.SetXTitle(proj_xtitle)
        gc.SetYTitle(z_title)
        gc.SetTitleSize(_xsize*0.03)

        gc.Draw()
        stack_unstack = []
        # This will plot the histograms stacked on top of each other
        if do_stack:
            stack_unstack.append("stack")
        # This will plot the histograms unstacked
        if do_nostack:
            stack_unstack.append("nostack")
        # This will just plot data and total mc
        stack_unstack.append("nobreakdown")
        for stackopt in stack_unstack:
            
            for i in range(n_pads):
                pad = gc.cd(i+1)
                if proj_xtitle.split(" (")[0] in scaleY:
                    pad.SetLogy()
                pad.SetFrameLineWidth(2)
                pad.Draw()
                data_hist_list[i].Draw("9 axis")
            for i in range(n_pads):
                pad = gc.cd(i+1)
                pad.Draw()
                tmp_stack_drawopts = ""
                if not pad.GetLogy():
                    tmp_stack_drawopts += " ]["
                if stackopt == "stack":
                    stack_list[i].Draw("9 HIST noclear same%s"%tmp_stack_drawopts)
                elif stackopt == "nobreakdown":
                    mc_band_list[i].Draw("9 E2 ][ same")
                    mc_hist_list[i].Draw("9 HIST ][ SAME")
                else:
                    tmp_stack = stack_list[i].Clone()
                    hist_index = len(my_catstodo) - 1
                    hist_list = []
                    for tmp_hist in tmp_stack.GetHists():
                        tmp_hist.SetFillStyle(0)
                        tmp_hist.SetLineWidth(typeslinewidth+1)
                        tmp_hist.SetLineColor(catscolors[my_catstodo[hist_index]])
                        hist_index -= 1
                    mc_band_list[i].Draw("9 E2 ][ same")
                    tmp_stack.Draw("9 nostack noclear hist same")
                    mc_hist_list[i].Draw("9 HIST ][ SAME")
                data_stat_list[i].Draw("9 SAME %s"%staterror_drawopt)
                data_hist_list[i].Draw("9 SAME E1 X0")
                data_hist_list[i].Draw("9 SAME axis")

                range_string = "{loedge} < {var} < {hiedge}".format(
                    # loedge = round(plot_bins[i], 3), var =proj_ytitle.split(" (")[0], hiedge = round(plot_bins[i+1], 3)
                    loedge = round(plot_bins[i], 3), var =tmp_varname + "#lower[-0.25]{#scale[0.6]{ (%s)}}"%tmp_units, hiedge = round(plot_bins[i+1], 3)
                )
                binrange_latex = ROOT.TLatex()
                binrange_latex.SetTextAlign(33) # top right
                binrange_latex.SetNDC()
                binrange_latex.SetTextFont(42)
                binrange_latex.SetTextSize(0.025)
                binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)

                multip_string = "#times {:g}".format(float('{:.{p}g}'.format(multipliers[i], p=2)))
                multip_latex = ROOT.TLatex()
                multip_latex.SetTextAlign(32)
                multip_latex.SetNDC()
                multip_latex.SetTextFont(52)
                multip_latex.SetTextSize(0.028)
                multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.05),multip_string)
                pad.Modified()
                pad.Update()
            pad = gc.cd(n_pads+1)
            pad.Draw()

            padwidth = 1 - pad.GetLeftMargin() - pad.GetRightMargin()
            leg = TLegend(pad.GetLeftMargin()+padwidth/20,(1.-(pad.GetTopMargin())-0.01), 1 - (pad.GetRightMargin() + padwidth/20),(pad.GetBottomMargin()+0.01))
            leg.SetBorderSize(0)
            leg.SetFillColor(-1)
            leg.SetTextSize(round(legendfontsize/3))
            leg.AddEntry(data_hist_list[0], catsnames["data"],"pe")
            leg.SetNColumns(1) #TODO is this right?
            if stackopt == "nobreakdown":
                leg.AddEntry(mc_band_list[i], catsnames[0],"fl")
            elif stackopt == "nostack":
                leg.AddEntry(mc_band_list[i], catsnames[0],"fl")
                for cat in my_catstodo:
                    mc_typesproj_listdict[cat][0].SetLineColor(catscolors[cat])
                    leg.AddEntry(mc_typesproj_listdict[cat][0],catsnames[cat],"l")
            else: # if "stack":
                for cat in my_catstodo:
                    leg.AddEntry(mc_typesproj_listdict[cat][0],catsnames[cat],"fl")
            leg.Draw()
            pad.Modified()

            gc.SetHistTexts()
            gc.Draw()
            sigma_canvas_name = "%s_Types_%s"%(thename, stackopt)
            gc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s %s"%(thetitle," Types", stackopt))


            gc.cd()
            gc.ResetPads()
            gc.Modified()
            gc.Update()
        # gc.SetYTitle("Ratio to "%ref_model)
        gc.SetYTitle("Data / Simulation")
        gc.SetXTitle(proj_xtitle)
        gc.Modified()
        gc.Update()

        leg.Clear()
        ratio_list = []
        ratio_stat_list = []
        straightline_list = []
        mcerror_list = []
        typesratio_listdict = {}
        typesratiostack_listdict = {}
        for i in range(n_pads):
            ratio_mnvh = MakeDataMCRatioForPlot(data_mnvproj_list[i],mc_mnvproj_list[i])
            ratio_hist, ratio_stat = GetDataHistsForPlot(ratio_mnvh)

            # ratio_hist.SetMinimum(0.001)
            ratio_hist.SetMaximum(2.999)
            ratio_hist.SetMinimum(0.0001)
            # ratio_hist.SetMaximum(1.9999)
            ratio_hist.SetFillStyle(1001)
            ratio_hist.SetLineColor(ROOT.kBlack)
            ratio_hist.SetLineWidth(typeslinewidth)
            ratio_hist.SetMarkerSize(data_marker_size2d)

            ratio_hist.GetXaxis().SetNdivisions(505)
            ratio_hist.GetYaxis().SetNdivisions(505)
            ratio_hist.GetYaxis().SetLabelSize(ratio_hist.GetXaxis().GetLabelSize())
            ratio_list.append(ratio_hist)
            ratio_stat.SetLineWidth(typeslinewidth)
            ratio_stat.SetFillStyle(1001)
            ratio_stat.SetMarkerSize(data_marker_size2d)
            ratio_stat.SetLineColor(ROOT.kBlack)
            ratio_stat_list.append(ratio_stat)

            # typesratio_dict = {}
            # for key in mc_typesproj_listdict:
            print(my_catstodo)
            for key in reversed(my_catstodo):
                tmp_typesratio = TH1D(mc_typesproj_listdict[key][i].Clone())
                tmp_typesratio.Divide(tmp_typesratio,mc_hist_list[i],1.0,1.0)
                tmp_typesratio.SetLineWidth(typeslinewidth+1)
                tmp_typesratio.SetFillColor(0)
                tmp_typesratio.SetLineColor(catscolors[key])
                if tmp_dotypes:
                    print(key)
                    if key >= 10:
                        tmp_typesratio.SetLineStyle(2)
                    # else:
                        if typeslinedarker:
                            tmp_typesratio.SetLineColor(ROOT.TColor.GetColorDark(catscolors[key]))
                if key not in typesratio_listdict.keys():
                    typesratio_listdict[key] = []
                typesratio_listdict[key].append(tmp_typesratio)
                # typesratio_dict[key] = tmp_typesratio
            if tmp_dotypes and 11 in my_catstodo[1:]:
                for key in reversed(my_catstodo[1:]):
                    if key > 10: continue
                    if key not in typesratiostack_listdict: 
                        typesratiostack_listdict[key] = []
                    tmp_hist = typesratio_listdict[key][i].Clone()
                    tmp_stack = THStack()
                    if key + 10 not in my_catstodo[1:]:
                        # tmp_stack.Add(tmp_hist)
                        typesratiostack_listdict[key].append(tmp_hist)
                        continue
                    tmp_hist_bkg = typesratio_listdict[key+10][i].Clone()
                    tmp_hist_bkg.SetLineStyle(7)
                    tmp_stack.Add(tmp_hist_bkg)
                    if tmp_hist.GetEntries() == 0: continue
                    tmp_stack.Add(tmp_hist)
                    typesratiostack_listdict[key].append(tmp_stack)
            straightline = TH1D()
            # straightline = fmcerror.Clone()
            straightline = mc_hist_list[i].Clone()
            # for bin in range(1,mc_hist_list[i].GetXaxis().GetNbins() + 1):
            for j in range(1,mc_hist_list[i].GetXaxis().GetNbins() + 1):
                straightline.SetBinContent(j,1.0)
            # straightline.SetLineColor(ROOT.kRed)
            straightline.SetLineColor(catscolors["mctot"])
            straightline.SetLineWidth(typeslinewidth+1)
            straightline.SetFillStyle(0)
            straightline_list.append(straightline)

            
            tmp_mnvh_mc = mc_mnvproj_list[i].Clone()
            tmp_mnvh_mc.ClearAllErrorBands()
            tmp_mnvh_mc.AddMissingErrorBandsAndFillWithCV(mc_mnvproj_list[i])
            tmp_mnvh_mc.Divide(tmp_mnvh_mc,mc_mnvproj_list[i],1.0,1.0)
            tmp_mnvh_mc.SetFillColor(catscolors["mctot"])
            tmp_mnvh_mc.SetFillColorAlpha(catscolors["mctot"],0.3)
            tmp_mnvh_mc.SetLineColor(catscolors["mctot"])
            tmp_mnvh_mc.SetLineWidth(typeslinewidth)
            tmp_mnvh_mc.SetMarkerStyle(0)
            tmp_mnvh_mc.SetFillStyle(1001)
            mcerror_list.append(tmp_mnvh_mc.GetCVHistoWithError())
            
        for i in range(n_pads):
            pad = gc.cd(i+1)
            pad.SetLogy(0)

            pad.Draw()
            ratio_list[i].Draw("9 E1 axis")
            mcerror_list[i].Draw("9 E2 same ][")
            straightline_list[i].Draw("9 hist same X0 ][")
            if tmp_dotypes and 11 in typestodo_leg:
                for cat in typestodo_leg:
                    if cat > 10: continue
                    typesratiostack_listdict[cat][i].Draw("9 HIST NOCLEAR SAME ][")
            else:
                for cat in typesratio_listdict:
                    typesratio_listdict[cat][i].Draw("9 HIST SAME ][")
            ratio_stat_list[i].Draw("9 same %s"%staterror_drawopt)
            ratio_list[i].Draw("9 same E1 X0")
            ratio_list[i].Draw("9 same axis")

            range_string = "{loedge} < {var} < {hiedge}".format(
                loedge = round(plot_bins[i], 3), var =tmp_varname + "#lower[-0.25]{#scale[0.6]{ (%s)}}"%tmp_units, hiedge = round(plot_bins[i+1], 3)
            )
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.03)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)
            pad.Modified()
            pad.Update()
        pad = gc.cd(n_pads+1)
        pad.Draw()

        leg.AddEntry(ratio_list[0], catsnames["data"],"pe")
        # leg.AddEntry(mcerror_list[0], "MnvTune v2.0.1", "fl")
        leg.AddEntry(mcerror_list[0], catsnames[0], "fl")
        if tmp_dotypes:
            for cat in typestodo_leg:
                leg.AddEntry(typesratio_listdict[cat][0],catsnames[cat],"fl")
        else:
            for cat in my_catstodo:
                leg.AddEntry(typesratio_listdict[cat][0],catsnames[cat],"fl")
        leg.Draw()
        pad.Modified()
        gc.SetHistTexts()
        gc.Draw()
        tmp_ratio_name = "%s_Typesratio"%(thename)
        # gc.Print(os.path.join(outdirname, thename + "_Types_ratio.png"))
        gc.Print(os.path.join(outdirname,"source", tmp_ratio_name + ".C"))
        gc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s"%(thetitle," Types Ratio"))
        gc.cd()
        gc.ResetPads()
        gc.Modified()
        gc.Update()
        

        del gc


def DrawDataMCTypesPlot2D(i_data_hist, i_mc_hist, i_mc_typeshistdict, x_title, x_bins, y_title, y_bins, z_title, outdirname, canvas_name, canvas_title, multipliers = []):#, do_comparison = False):
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
    # for projaxis in ["y"]:
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
        DrawDataMCTypesPlot1D(data_mnvprojtot, mc_mnvprojtot, mc_typestotproj_dict, proj_xtitle, z_title, outdirname, canvas_name, canvas_title+" total proj")
        # if "E_{Avail}" in proj_xtitle and not do_comparison:
        if "E_{Avail}" in proj_xtitle:
            DrawDataMCTypesPlot1D_AxisChange(data_mnvprojtot, mc_mnvprojtot, mc_typestotproj_dict, proj_xtitle, z_title, outdirname, canvas_name, canvas_title+" total proj")

        print("canvas n x bins: ",canvas_nxbins,",\t canvas n y bins: ",canvas_nybins)

        ROOT.gStyle.SetErrorX(0) # This turns off the horizontal error bars
        ROOT.gStyle.SetEndErrorSize(end_error_size/2) # This makes the ticks at the end of the error bars longer

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

        calc_tmp_pad_scale = True
        # print(multipliers)
        # print(len(multipliers),n_pads)
        # sys.exit(1)
        if len(multipliers) == n_pads:
            calc_tmp_pad_scale = False
            global_max = 4.0E-37
        for i in range(n_pads):

            pad = gc.cd(i+1)
            pad.SetFrameLineWidth(1)
            pad.Draw()
            tmp_pad_scale = 1.0
            # pad.SetLogy()
            if calc_tmp_pad_scale:
                tmp_pad_max = 0.0
                tmp_pad_max = max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum())
                if tmp_pad_max == 0:
                    tmp_pad_max = 1.0

                tmp_pad_scale = eval('{:.{p}g}'.format(global_max / tmp_pad_max, p=3))
            else:
                tmp_pad_scale = multipliers[i]
            data_hist_list[i].Scale(tmp_pad_scale)
            data_stat_list[i].Scale(tmp_pad_scale)
            mc_hist_list[i].Scale(tmp_pad_scale)
            mc_hist_list[i].SetLineWidth(typeslinewidth)
            for key in mc_typesproj_listdict:
                mc_typesproj_listdict[key][i].Scale(tmp_pad_scale)
                mc_typesproj_listdict[key][i].SetLineWidth(typeslinewidth)
            # mc_band_list[i].Scale(tmp_pad_scale)

            data_hist_list[i].SetMaximum(1.2 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
            data_hist_list[i].SetMinimum(0)
            if proj_xtitle.split(" (")[0] in scaleY:
                pad.SetLogy()
                data_hist_list[i].SetMaximum(1.5 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
                data_hist_list[i].SetMinimum(data_hist_list[i].GetMaximum()/1000)
            
            # data_hist_list[i].GetXaxis().SetNdivisions(207)
            data_hist_list[i].GetYaxis().SetNdivisions(205)
            data_hist_list[i].GetYaxis().SetLabelSize(data_hist_list[i].GetXaxis().GetLabelSize())

            data_hist_list[i].Draw("axis")
            # mc_band_list[i].Draw("SAME E2")

            for key in reversed(list(mc_typesproj_listdict)):
                mc_typesproj_listdict[key][i].Draw("HIST SAME")
            mc_hist_list[i].Draw("HIST SAME")

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
        leg.AddEntry(data_hist_list[0], "Data","pe")
        leg.AddEntry(mc_hist_list[0], typesnames[0],"fl")
        # Need to do these in order to put important stuff on top
        for key in mc_typesproj_listdict.keys():
            leg.AddEntry(mc_typesproj_listdict[key][0],typesnames[typesints[key]],"fl")
        leg.Draw()
        pad.Modified()

        gc.SetHistTexts()
        gc.Draw()
        sigma_canvas_name = thename + "_Types"
        # gc.Print(os.path.join(outdirname, sigma_canvas_name + ".png"))
        gc.Print(os.path.join(outdirname,"source", sigma_canvas_name + ".C"))
        gc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s"%(canvas_title," Types"))
        # del gc

        gc.cd()
        # leg.Clear()
        gc.ResetPads()
        gc.SetYTitle("Data / Simulation")
        gc.SetXTitle(proj_xtitle)
        gc.Modified()
        gc.Update()

        ratio_list = []
        ratio_stat_list = []
        typesratio_listdict = {}
        # mcerror_list = []
        straightline_list = []
        for i in range(n_pads):
            ratio_mnvh = MakeDataMCRatioForPlot(data_mnvproj_list[i],mc_mnvproj_list[i])
            ratio_hist, ratio_stat = GetDataHistsForPlot(ratio_mnvh)

            ratio_hist.SetMinimum(0.001)
            ratio_hist.SetMaximum(2.999)
            ratio_hist.SetFillStyle(1001)
            ratio_hist.SetLineColor(ROOT.kBlack)
            ratio_hist.SetLineWidth(2)
            # ratio_hist.GetXaxis().SetNdivisions(205)
            ratio_hist.GetYaxis().SetNdivisions(206)
            ratio_hist.GetYaxis().SetLabelSize(ratio_hist.GetXaxis().GetLabelSize())

            ratio_stat.SetLineWidth(2)
            ratio_list.append(ratio_hist)
            ratio_stat_list.append(ratio_stat)
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
            # straightline.SetLineColor(ROOT.TColor.GetColorDark(typescolors[0]))
            straightline.SetLineWidth(3)
            straightline.SetFillStyle(0)
            straightline_list.append(straightline)


        for i in range(n_pads):
            pad = gc.cd(i+1)
            pad.SetLogy(0)

            pad.Draw()
            ratio_list[i].Draw("axis")
            for key in reversed(list(typesratio_listdict.keys())):
                typesratio_listdict[key][i].Draw("HIST SAME")
                
            straightline_list[i].Draw("hist same")
            ratio_stat_list[i].Draw("same E1 X0")
            ratio_list[i].Draw("same E1 X0")
            ratio_list[i].Draw("same axis")

            range_string = "{loedge} < {var} < {hiedge}".format(loedge = round(plot_bins[i], 3), var =proj_ytitle.split(" (")[0], hiedge = round(plot_bins[i+1], 3))
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.03)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)
        pad = gc.cd(n_pads+1)
        pad.Draw()

        leg.Draw()
        pad.Modified()
        gc.SetHistTexts()
        gc.Draw()
        # gc.Print(os.path.join(outdirname, thename + "_Types_ratio.png"))
        gc.Print(os.path.join(outdirname,"source", thename + "_Types_ratio.C"))
        gc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s"%(canvas_title," Types Ratio"))
        gc.cd()
        gc.ResetPads()
        gc.Modified()
        gc.Update()
            
        del gc
    # return 0

def DrawErrorSumary2D():
    return 0

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


# modelplotinfo = {
#     "data": {
#         "name": "Data",
#         "shortname": "Data",
#         "markercolor": ROOT.kBlack,
#         "linecolor": ROOT.kBlack, 
#     },
#     "MnvTunev4.3.1": {
#         "name": "MINERvA Tune v4.3.1",
#         "shortname": "MnvTune v4.3.1",
#         # "markercolor": ROOT.kBlack,
#         "linecolor": typescolors[0], 
#         # "fillcolor": typescolors[0],
#         "type": 0,
#     },
#     "MnvTunev2.0.1": {
#         "name": "MINERvA Tune v2.0.1",
#         "shortname": "MnvTune v2.0.1",
#         # "markercolor": ROOT.kBlack,
#         "linecolor": typescolors[0], 
#         # "fillcolor": typescolors[0],
#         "type": 0,
#     },
#     "QE": {
#         "name": "Quasielastic",
#         "shortname": "QE",
#         # "markercolor": ROOT.kBlack,
#         "linecolor": typescolors[1], 
#         # "fillcolor": typescolors[0],
#         "type": 1,
#     },
#     "RES": {
#         "name": "Resonant pion",
#         "shortname": "RES",
#         # "markercolor": ROOT.kBlack,
#         "linecolor": typescolors[2], 
#         # "fillcolor": typescolors[0],
#         "type": 2,
#     },
#     "DIS": {
#         "name": "Deep Inelastic Scattering",
#         "shortname": "DIS",
#         # "markercolor": ROOT.kBlack,
#         "linecolor": typescolors[3], 
#         # "fillcolor": typescolors[0],
#         "type": 3,
#     },
#     "2p2h": {
#         "name": "Deep Inelastic Scattering",
#         "shortname": "DIS",
#         # "markercolor": ROOT.kBlack,
#         "linecolor": typescolors[3], 
#         # "fillcolor": typescolors[0],
#         "type": 3,
#     },
# }

bkgcats = [
    "chargedpion",
    "neutralpion",
    "multipion",
    "other",
]

catstodo = [
    "data",
    "qelike",
    "chargedpion",
    "neutralpion",
    "other",
    # "multipion",
    # "other_np",
]

catsnames = {
    "data":"data", 
    "qelike":"QElike",
    "chargedpion":"1#pi^{#pm}",
    "neutralpion":"1#pi^{0}",
    "other":"Other",
    "multipion":"N#pi",
    "other_np":"Other",
    0: "MnvTune v2.0.1",  # total mc
    1: "QE",             # QE
    2: "RES",            # RES
    3: "DIS",            # DIS
    4: "COH",            # COH
    8: "2p2h",           # 2p2h
}

catscolors = {
    "data":        ROOT.kBlack, 
    # "qelike":ROOT.kBlue-6,
    # "chargedpion":ROOT.kMagenta-6,
    # "neutralpion":ROOT.kRed-6,
    # "multipion":ROOT.kGreen-6,
    # "other":ROOT.kYellow-6,
    # "qelike":ROOT.kP6Blue,
    # "chargedpion":ROOT.kP6Yellow,
    # "neutralpion":ROOT.kP6Red,
    # "multipion":ROOT.kP6Grape,
    # "other":ROOT.kP6Gray,
    "qelike":       ROOT.kP10Blue,
    "chargedpion":  ROOT.kP10Yellow,
    "neutralpion":  ROOT.kP10Orange,
    "multipion":    ROOT.kP10Violet,
    "other":        ROOT.kP10Ash,
    "other_np":     ROOT.kP10Ash,
    # "mctot":        ROOT.kP10Red,
    "mctot":        ROOT.kP8Red,
    0:              ROOT.kP8Red,     # total mc
    1:              ROOT.kP8Blue,    # QE
    2:              ROOT.kP8Orange,  # RES
    3:              ROOT.kP8Pink,   # DIS
    4:              ROOT.kP8Green,    # COH
    8:              ROOT.kP8Azure,  # 2p2h
    # 0:              ROOT.kP8Red,     # total mc
    # 1:              ROOT.kP8Blue,    # QE
    # 2:              ROOT.kP8Pink,  # RES
    # 3:              ROOT.kP8Green,   # DIS
    # 4:              ROOT.kP8Gray,    # COH
    # 8:              ROOT.kP8Orange,  # 2p2h
}

typescolors = {
    # 0: ROOT.kP8Red,     # total mc
    # # 1: ROOT.kP6Grape,   # QE
    # 2: ROOT.kP8Orange,  # RES
    # # 3: ROOT.kP8Cyan,    # DIS
    # # 4: ROOT.kP8Azure,   # COH
    # # 8: ROOT.kP8Green,   # 2p2h
    # # 0: ROOT.kP6Red,     # total mc
    # 1: ROOT.kP6Violet,   # QE
    # # 2: ROOT.kP6Yellow,  # RES
    # 3: ROOT.kP6Gray,    # DIS
    # 4: ROOT.kP8Azure,   # COH
    # 8: ROOT.kP6Blue,   # 2p2h
    # 0: ROOT.kP6Red,     # total mc
    # 1: ROOT.kP6Blue,   # QE
    # 2: ROOT.kP6Yellow,  # RES
    # 3: ROOT.kP6Grape,    # DIS
    # 4: ROOT.kP6Gray,   # COH
    # 8: ROOT.kP6Violet,   # 2p2h,
    0:              ROOT.kP8Red,     # total mc
    1:              ROOT.kP8Blue,    # QE
    2:              ROOT.kP8Orange,  # RES
    3:              ROOT.kP8Pink,   # DIS
    4:              ROOT.kP8Green,    # COH
    # 8:              ROOT.kP8Azure,  # 2p2h
    8:              ROOT.kP8Azure,  # 2p2h
}

typesnames = {
    0: "MnvTune v2.0.1",  # total mc
    1: "QE",             # QE
    2: "RES",            # RES
    3: "DIS",            # DIS
    4: "COH",            # COH
    8: "2p2h",           # 2p2h
}
typesints = {
    "MnvTune v2.0.1": 0,  # total mc
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

domodelcomp = global_domodelcomp
if len(sys.argv) == 1 and not global_domodelcomp:
    print("python3 xsec_plots.py <path to analyze output files>")
    sys.exit(1)
if len(sys.argv) < 2 and global_domodelcomp:
    print("python3 xsec_plots.py <path to analyze output file> <path to dir with model comps")
    print("WARNING: no path specified for models for comparison... just doing it without models")
    domodelcomp = False

# First get the hists/files for the extracted cross section
raw_filename = sys.argv[1]

if "_tuned_analyze9" in raw_filename:
    tuned_filename = raw_filename
    untuned_filename = raw_filename.replace("_tuned_","_untuned_")
elif "_untuned_analyze9":
    untuned_filename = raw_filename
    tuned_filename = raw_filename.replace("_untuned_","_tuned_")

tuned_f = TFile.Open(tuned_filename,"READONLY")
untuned_f = TFile.Open(untuned_filename,"READONLY")

# Make your output directory if it doesn't exist, and store the path for later
plotdirbase = os.getenv("OUTPUTLOC")

plotdir = MakePlotDir("XSecPlots")
dirname = untuned_filename.replace("_untuned_analyze9.root", "_XSec")

# outfilename=filebasename1.replace(".root","_2DPlots")
outdirname = os.path.join(plotdir, dirname)
if not os.path.exists(outdirname):
    print(outdirname)
    os.mkdir(outdirname)
else:
    print("found dir ", outdirname)

# Figure out the model you're using to properly name the outfile
modelname = ""
raw_filename_split = raw_filename.split("_")
for part in raw_filename_split:
    if "MnvTunev" in part:
        print("Found model name as %s"%(part))
        modelname += part
# These need to happen in order, so it needs to be in a separate loop
for part in raw_filename_split:
    if part=="multipion" and "no_multipion" not in raw_filename:
        modelname += "_" + part
if modelname == "":
    print("Guessing model name is MnvTunev2.0.1")
    modelname = "MnvTunev2.0.1"
# Now write it out so the name is better
tmpmodelname = modelname
# if " " not in tmpmodelname:
    # replace the 
if "_" in tmpmodelname:
    tmpmodelname = modelname.replace('_',' ')
    # print(tmpmodelname)
if tmpmodelname[7]!= " ":
    tmpmodelname = tmpmodelname[:7] + " " + tmpmodelname[7:]
# if "multipion" in tmpmodelname:
tmpmodelname = tmpmodelname.replace(" multipion","")
# print(tmpmodelname)
# sys.exit(1)
typesnames[0] = tmpmodelname
typesints[tmpmodelname] = 0
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

# Get the POT summary and set up the POT scaling
# h_pot = untuned_f.Get("POT_summary")
# dataPOT = h_pot.GetBinContent(1)
# mcPOTprescaled = h_pot.GetBinContent(2)
# POTScale = dataPOT / mcPOTprescaled
# if ("potscaled_combined_" in untuned_filename):
#     POTScale = 1.0
# print("POTScale: ",POTScale)
POTScale = 1.0


# Find all the valid histograms from the analyze_v9 files and group by keywords
# First get the histograms that were inputs to analyze_v9
print("Making dict of source hists...")
print("\tLooking at untuned...")
input_hists = GetInputHistDict(untuned_f)
print("\tLooking at tuned...")
input_hists = GetInputHistDict(tuned_f, input_hists)
# Get the "type" histograms that are for the mcinttypes
print("Making dict of source types hists...")
input_typeshists = GetInputTypesHistDict(untuned_f)
input_typeshists = GetInputTypesHistDict(tuned_f,input_typeshists)

# analyze_stage_list = [
#     "mc_tot",
#     "mc_bkg_tot",
#     "signalfraction",
#     "bkgfraction",
#     "bkgsub",
#     "bkgsub_unfolded",
#     "bkgsub_unfolded_effcorr",
#     "efficiency",
#     "bkgsub_unfolded_effcorr_sigma",
#     "sigmaMC"
# ]


# Next get the histograms that were output by analyze_v9 (ie for each stage)
print("Making dict of analyze hists...")
print("\tLooking at untuned...")
analyze_hists = GetAnalyzeHistDict(untuned_f, False)
print("\tLooking at tuned...")
analyze_hists = GetAnalyzeHistDict(tuned_f, True, analyze_hists)
# And get their type histograms also (though really should only need them for the "truth" stage)
print("Making dict of analyze types hists...")
analyze_typeshists = GetAnalyzeTypesHistDict(untuned_f, False)
analyze_typeshists = GetAnalyzeTypesHistDict(tuned_f, True, analyze_typeshists)

# Next get the variable configs set up. This is useful for building the histograms and making plot info
keys = tuned_f.GetListOfKeys()
if "varsFile" not in keys:
    bigvarconfig_string = tuned_f.Get("varsFile_5A").GetTitle()
else:
    bigvarconfig_string = tuned_f.Get("varsFile").GetTitle()
bigvarconfig_dict = json.loads(re.sub("//.*", "", bigvarconfig_string, flags = re.MULTILINE))

# # Done with the analyze_v9 files, lets get the files for the model comparison. This has it's own method
# pathtodir_modelcomp = sys.argv[2]
# modelcomppath_dict = GetModelCompFilePathsDict(pathtodir_modelcomp)
# # Dict to put all the model hists in. Structure is {model:{histdim:{sample:{variable:{fluxnorm:TH1D()}}}
# model_hists = {}
# for model in modelcomppath_dict:
#     # Trying this out, feels very pythonic....
#     with TFile.Open(modelcomppath_dict[model],"READONLY") as tmpfile:
#         model_hists[model] = GetModelHistDict(tmpfile)


# print(analyze_hists)
# analyze_dict[hist][sample][var][stage] = hist
ROOT.gStyle.SetOptStat(0)
for a_hist in analyze_hists.keys():
    # if a_hist =="h":
    #     continue
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
            
            # print(tmp_sigmamc_tuned.GetVertErrorBandNames())
            # sys.exit(1)
            
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
                continue
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
            tmp_types_mcreco = []
            tmp_types_mcseltru = []
            tmp_types_mcalltru = []
            if found_inputtypes:
                print(a_hist, b_sample, c_var)
                print("keys", input_typeshists[a_hist][b_sample][c_var]["qelike"].keys())
                tmp_types_mcreco = input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed"]
                tmp_types_mcseltru = input_typeshists[a_hist][b_sample][c_var]["qelike"]["selected_truth"]
                tmp_types_mcalltru = input_typeshists[a_hist][b_sample][c_var]["qelike"]["all_truth"]
            if found_inputtypestuned:
                print("keys", input_typeshists[a_hist][b_sample][c_var]["qelike"].keys())
                tmp_types_mcreco = input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed_tuned"]
                tmp_types_mcseltru = input_typeshists[a_hist][b_sample][c_var]["qelike"]["selected_truth_tuned"]
                tmp_types_mcalltru = input_typeshists[a_hist][b_sample][c_var]["qelike"]["all_truth_tuned"]

            # tmp_model_hists = {}
            # for model in modelcomptodo:
            #     if a_hist in model_hists[model]:
            #         if b_sample in model_hists[model][a_hist]:
            #             if c_var in model_hists[model][a_hist][b_sample]:
            #                 tmp_model_hists[model] = model_hists[model][a_hist][b_sample][c_var]["reweight"]
            
            tmp_canvas_basename = "%s_%s_%s"%(modelname,b_sample,c_var)
            tmp_canvas_basetitle = "%s %s %s"%(modelname, b_sample,c_var)
            var_outdir = os.path.join(outdirname,c_var)
            if not os.path.exists(var_outdir):
                print( var_outdir)
                os.mkdir(var_outdir)
                os.mkdir(os.path.join(var_outdir,"source"))
            
            dummy_canvas = ROOT.TCanvas()

            pdf_canvas_name = tmp_canvas_basename+"_xsecplots"
            dummy_canvas.Print(os.path.join(var_outdir,pdf_canvas_name+".pdf")+"[","pdf")
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
                continue
                # bkg subtracted 
                if "bkgsub" not in skipstage_list:
                    # bkgsub_canvas_name = tmp_canvas_basename + "_bkgsub"
                    bkgsub_canvas_name = pdf_canvas_name
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
                    # unfolded_canvas_name = tmp_canvas_basename + "_unfolded"
                    unfolded_canvas_name = pdf_canvas_name
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
                        # tmp_canvas_name = "%siter%d"%(unfolded_canvas_name, i+1)
                        tmp_canvas_name = pdf_canvas_name
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
                    # effcorr_canvas_name = tmp_canvas_basename + "_effcorr"
                    effcorr_canvas_name = pdf_canvas_name
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
                    # sigma_canvas_name = tmp_canvas_basename + "_sigma"
                    sigma_canvas_name = pdf_canvas_name
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
                    # if "modelcomp" not in skipstage_list:
                    #     modelcomp_canvas_name = tmp_canvas_basename + "_sigma_modelcomp"
                    #     modelcomp_canvas_title = tmp_canvas_basetitle + " sigma Model Comparison"
                    #     DrawDataMCTypesPlot1D(
                    #         tmp_sigma_tuned,tmpsigmamc, tmp_model_hists,
                    #         "%s (%s)"%(var_title,var_units), sigma_ytitle, 
                    #         var_outdir,
                    #         modelcomp_canvas_name, modelcomp_canvas_title
                    #     )

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

                # if "reconstructed" not in skipstage_list:
                #     reco_canvas_name = pdf_canvas_name
                #     bkgsub_canvas_title = tmp_canvas_basetitle + " Reconstructed"
                #     # Need to make the reco hists
                #     tmp_bkg_types = []
                #     tmp_types_mcreco = input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed_tuned"]
                #     first = True
                #     for bkg in bkgcats:
                #         if bkg in input_typeshists[a_hist][b_sample][c_var][c_cat]:
                #             for itype in input_typeshists[a_hist][b_sample][c_var][c_cat]["reconstructed_tuned"]:
                #                 if first:
                                    
                #                     first = False
                #                     continue


                #     DrawDataMCPlot2D(
                #         tmp_bkgsub_tuned, tmp_mcrecosig_tuned, 
                #         xvar_title, xvar_bins, 
                #         yvar_title, yvar_bins, 
                #         counts_ztitle, 
                #         var_outdir, 
                #         bkgsub_canvas_name, bkgsub_canvas_title
                #     )

                # bkgsubtracted
                if "bkgsub" not in skipstage_list:
                    # bkgsub_canvas_name = tmp_canvas_basename + "_bkgsub"
                    bkgsub_canvas_name = pdf_canvas_name
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
                    # unfolded_canvas_name = tmp_canvas_basename + "_unfolded"
                    unfolded_canvas_name = pdf_canvas_name

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
                        # tmp_canvas_name = "%siter%d"%(unfolded_canvas_name, i+1)
                        tmp_canvas_name = pdf_canvas_name
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
                    # effcorr_canvas_name = tmp_canvas_basename + "_effcorr"
                    effcorr_canvas_name = pdf_canvas_name
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
                    # sigma_canvas_name = tmp_canvas_basename + "_sigma"
                    sigma_canvas_name = pdf_canvas_name
                    sigma_canvas_title = tmp_canvas_basetitle + " sigma"

                    # DrawDataMCPlot2D(
                    #     tmp_sigma_tuned, tmp_sigmamc, 
                    #     xvar_title, xvar_bins, yvar_title, yvar_bins, 
                    #     sigma_ztitle, 
                    #     var_outdir, 
                    #     sigma_canvas_name, sigma_canvas_title
                    # )
                    if found_typessigma:
                        eavail_mutlipliers = [
                            # 1.0,
                            # 12.0,
                            # 18.0,
                            # 26.0,
                            # 41.0,
                            # 82.0,
                            # 200.0,
                        ]
                        print(eavail_mutlipliers)
                        # DrawDataMCTypesPlot2D(
                        #     tmp_sigma_tuned, tmp_sigmamc, tmp_typessigma, 
                        #     xvar_title, xvar_bins, yvar_title, yvar_bins, 
                        #     sigma_ztitle, 
                        #     var_outdir, 
                        #     sigma_canvas_name, sigma_canvas_title,
                        #     eavail_mutlipliers
                        # )
                        tmp_nametag = ""
                        tmp_do_stack = True
                        tmp_do_nostack = True
                        DrawDataMCPlot2D_new(
                            tmp_sigma_tuned, tmp_sigmamc, tmp_typessigma, 
                            xvar_name, xvar_units, xvar_bins, yvar_name, yvar_units, yvar_bins,
                            sigma_ztitle, 
                            var_outdir, 
                            sigma_canvas_name, sigma_canvas_title, tmp_nametag,
                            eavail_mutlipliers,
                            tmp_do_stack, tmp_do_nostack
                        )


                    # if "modelcomp" not in skipstage_list:
                    #     modelcomp_canvas_name = tmp_canvas_basename + "_sigma_modelcomp"
                    #     modelcomp_canvas_title = tmp_canvas_basetitle + " sigma Model Comparison"
                    #     DrawDataMCTypesPlot2D(
                    #         tmp_sigma_tuned, tmpsigmamc, tmp_model_hists,
                    #         xvar_title, xvar_bins, yvar_title, yvar_bins,
                    #         sigma_ztitle,
                    #         var_outdir,
                    #         modelcomp_canvas_name, modelcomp_canvas_title
                    #     )
                    # close if found types sigma
                # DrawErrorSummary2D()
                # close if sigma
            # Close if h2d
            dummy_canvas.Print(os.path.join(var_outdir,pdf_canvas_name+".pdf")+"]","pdf")
        # close c_var loop
    # close b_sample loop
# close a_hist loop


sys.exit(1)
