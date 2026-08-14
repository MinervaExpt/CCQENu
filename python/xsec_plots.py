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
from PlotUtils import MnvH1D, MnvPlotter, HyperDimLinearizer, GridCanvas, MnvHist
import datetime
import ctypes
import math
import json, re
from optparse import OptionParser

mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")

TEST=False
global_noData=False  # use this to plot MC only types
sigtop=True # use this to place signal on top of background
dotuned=False
alphalevel = 0.2 #0.3
dothesisplot = True
# doratio = True
# dotypes = False

global_domodelcomp = True # Set to true if you want to do model comparisons, will need to give path to where files are

vars_info = {
    "EAvail": {
        "title": "E_{Avail}^{}",
        "units": "GeV",
        "bins": [],
    },
    "EAvailWithRemoval": {
        "title": "E_{Avail}^{} w/ removal",
        "units": "GeV",
        "bins": [],
    },
    "ptmu": {
        "title": "p^{}_{T}^{}",
        "units": "GeV/c",
        "bins": [],
    },
    "pzmu" : {
        "title": "p_{||}",
        "units": "GeV/c",
        "bins": [],

    }
}
bkgfillstyle = {
    "chargedpion":  3144,
    "neutralpion":  3144,
    "other":        3144,
    "multipion":    3144,
    "other_np":     3144,
    11:             3144,    # "Bkg QE"
    12:             3144,  # "Bkg RES",
    13:             3144,   # "Bkg DIS",
    14:             3144,    # "Bkg COH",
    18:             3144,  #"Bkg 2p2h",
}

modelcomptodo = {
    "NUISANCE": [
        # "G18_02a",
        # "G18_02b",
        "G18_10a",
        # "G18_10b",
        "NEUT_tune_LFG",
        # "NEUT_tune_SF",
        "NuWro_CH_LFG",
        # "NuWro_CH_SF",
    ],
    "analyze_v9": [
        "MnvTunev4.3.1",
        "MnvTunev2.0.1",
        "MnvTunev4.3.1_multipi",
        "MnvTunev2.0.1_multipi",
    ]
}

modelsampletodo = [
    "QElike",
    "QElikeHyp",
]

staterror_drawopt = "E1 X0"
typeslinedarker = True

modelplotinfo = {
    "G18_02a": {
        "base": "GENIEv3",
        "name": "GENIE v3.0.6 G18_02a_02_11a",
        "shortname": "GENIEv3 G18_02a",
        "shortshortname": "02a",
        "color": ROOT.kP8Blue, # TODO
        "linecolor":ROOT.kP8Blue,
        "linestyle": 2,
    },
    "G18_02b": {
        "base": "GENIEv3",
        "name": "GENIE v3.0.6 G18_02b_02_11a",
        "shortname": "GENIEv3 G18_02b",
        "shortshortname": "02b",
        "color": ROOT.kP8Blue, # TODO
        "linecolor":ROOT.kP8Blue,
        "linestyle": 3,
    },
    "G18_10a": {
        "base": "GENIEv3",
        "name": "GENIE v3.0.6 G18_10a_02_11a",
        "shortname": "GENIEv3 G18_10a",
        "shortshortname": "10a",
        "color": ROOT.kP8Blue, # TODO
        "linecolor":ROOT.kP8Blue,
        "linestyle": 5,

    },
    "G18_10b": {
        "base": "GENIEv3",
        "name": "GENIE v3.0.6 G18_10b_02_11a",
        "shortname": "GENIEv3 G18_10b",
        "shortshortname": "10b",
        "fillcolor": ROOT.kP8Blue, # TODOx
        "linecolor":ROOT.kP8Blue,
        "linestyle": 2,#6,
    },
    "NEUT_tune_LFG": {
        "base": "NEUT",
        "name": "NEUT v5.4.1 LFG",
        "shortname": "NEUT LFG",
        "fillcolor": ROOT.kP8Orange, # TODO
        "linecolor":ROOT.kP8Orange,
        "linestyle": 8,#2,

    },
    "NEUT_tune_SF": {
        "base": "NEUT",
        "name": "NEUT v5.4.1 SF",
        "shortname": "NEUT SF",
        "fillcolor": ROOT.kP8Orange, # TODO
        "linecolor":ROOT.kP8Orange,
        "linestyle": 3,
    },
    "NuWro_CH_LFG": {
        "base": "NuWro",
        "name": "NuWro v21.09 LFG",
        "shortname": "NuWro LFG",
        "fillcolor": ROOT.kP8Pink, # TODO
        "linecolor":ROOT.kP8Pink,
        "linestyle": 2,#2,

    },
    "NuWro_CH_SF": {
        "base": "NuWro",
        "name": "NuWro v21.09 SF",
        "shortname": "NuWro SF",
        "fillcolor": ROOT.kP8Pink, # TODO
        "linecolor":ROOT.kP8Pink,
        "linestyle": 3,

    },
    "MnvTunev4.3.1": {
        "base": "MnvTune",
        "name": "MINERvA Tune v4.3.1",
        "shortname": "MnvTune v4.3.1",
        "fillcolor": ROOT.kP8Red, # TODO
        "linecolor":ROOT.kP8Red,
        "linestyle":1,
    },
    "MnvTunev2.0.1": {
        "base": "MnvTune",
        "name": "MINERvA Tune v2.0.1",
        "shortname": "MnvTune v2.0.1",
        "fillcolor": ROOT.kP8Red, # TODO
        "linecolor":ROOT.kP8Red,
        "linestyle":1,
    },
    "MnvTunev4.3.1_multipion": {
        "base": "MnvTune",
        "name": "MINERvA Tune v4.3.1 w/ multi-pion fit",
        "shortname": "MnvTune v4.3.1 N#pi",
        "fillcolor": ROOT.kP8Red, # TODO
        "linecolor":ROOT.kP8Red,
        "linestyle":1,
    },
    "MnvTunev2.0.1_multipion": {
        "base": "MnvTune",
        "name": "MINERvA Tune v2.0.1 w/ multi-pion fit",
        "shortname": "MnvTune v2.0.1 N#pi",
        "fillcolor": ROOT.kP8Red, # TODO
        "linecolor":ROOT.kP8Red,
        "linestyle":1,
    },
}
ROOT.TH1.AddDirectory(ROOT.kFALSE)
_xsize = 3200
_ysize = 2700

latex_x = 0.55
latex_y = 0.43

ratio_frac = 0.35 #0.278

pad_lmarg = 0.12
pad_rmarg = 0.025
topmarg = 0.05
bottommarg = ratio_frac - 0.03#0.32
# This is to set how tall the ratio should be in the pad

data_marker_style = 20
data_marker_size = 3.0
data_marker_size2d = 2.0
end_error_size = 12.0
do_pinkstat = False

legendfontsize = 0.05
legx1 = 0.7
legx2 = 1.0
legy1 = 0.65
legy2 = 0.95

do_titleonplot = True
do_chi2onplot = True

# lat_xoffset = 0.06
lat_xoffset = 0.0
lat_yoffset = 0.04

typeslinewidth = 1
typeslinewidth1D = 2

prelim_string = "MINER#it{^{}#nu}A Work In Progress"
datapot_string1 = "#it{POT Normalized}"
datapot_string2 =  "#it{Data POT}: 1.12 #times 10^{21}"

scaleX = [
    "Q2QE", 
]
scaleY = [
    "EAvail",
    "E_{Avail}",
    "E_{Avail}^{}",
    vars_info["EAvail"]["title"],
    vars_info["EAvailWithRemoval"]["title"],
    #"recoil",
]

skipstage_list = [
    # "reconstructed",
    # "bkgsub",
    "unfolded",
    "unfolditers",
    # "effcorr",
    # "sigma",
    # "modelcomp",
]

rangeuser_dict = {
    # "ptmu": [
    #     0.0,
    #     1.5
    # ],
}

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
    if dothesisplot:
        plotdir = "/Users/nova/Documents/Thesis/Noah-Vaughan-Thesis-Copy/figures"
    else:
        plotdir = ""
        base_plotdir = os.environ.get("PLOTSLOC")
        if base_plotdir != None:
            plotdir = os.path.join(base_plotdir, month + year)
        else:
            plotdir = os.path.join("/Users/nova/git/plots/", month + year)
        if not os.path.exists(plotdir):
            print("Can't find plot dir. Making it now... ", plotdir)
            os.makedirs(plotdir)
        else:
            print("found dir ", plotdir)
    if subdir == "":
        return plotdir
    if not os.path.exists(os.path.join(plotdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(plotdir, subdir))
        os.makedirs(os.path.join(plotdir, subdir))
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
    for model in modelcomptodo["NUISANCE"]:
        tmpsubdir = ""
        for subdir in subdir_list:
            if model not in subdir:
                # print("WARNING: model %s requested but not found. Skipping..."%(model))
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
            # if ".root" not in name or "rawnominalreweight" in name:
            if ".root" not in name:
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
    # print(path_dict)
    # sys.exit(1)
    return path_dict
    
def GetModelHistDict(f, model):
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
        h = f.Get(name).Clone()
        if h.GetEntries() <= 0:
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
        h.Print()
        if h.GetEntries() == 0:
            print("WARNING: no entries in the hist %s, skipping"%(name))
        h.SetLineColor(modelplotinfo[model]["linecolor"])
        h.SetLineStyle(modelplotinfo[model]["linestyle"])
        h.SetFillColor(modelplotinfo[model]["linecolor"])
        h.SetLineWidth(typeslinewidth)
        h.SetFillStyle(0)
        catscolors[model] = modelplotinfo[model]["linecolor"]
        catsnames[model] = modelplotinfo[model]["shortname"]
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
        if "data" in cat:
            # h.Scale(1.0, "width")
            # h.Scale(1.0)
            h.SetFillColor(0)
            h.SetMarkerStyle(data_marker_style)
            h.SetLineColor(ROOT.kBlack)
            h.SetMarkerStyle(data_marker_style)
            h.SetMarkerSize(data_marker_size)
            if hist == "h":
                h.SetLineWidth(typeslinewidth1D)
            if hist == "h2D":
                h.SetLineWidth(typeslinewidth)
        else:
            print("scaling hist ", name)
            h.SetFillColor(catscolors[cat])
            # h.SetFillColorAlpha(catscolors[0], 0.4)
            h.SetLineColor(ROOT.TColor.GetColorDark(catscolors[cat]))
            if hist == "h":
                h.SetLineWidth(typeslinewidth1D)
            if hist == "h2D":
                h.SetLineWidth(typeslinewidth)
            # if hist == "h":
            #     h.SetLineWidth(typeslinewidth1D)
            # if hist == "h2D":
            #     h.SetLineWidth(typeslinewidth)
            # h.SetLineColor(ROOT.kBlack)
            # h.Scale(1.0, "width")
            # h.Scale(POTScale, "width")
            h.Scale(POTScale)
        if variable in rangeuser_dict:
            h.GetXaxis().SetRangeUser(rangeuser_dict[variable][0],rangeuser_dict[variable][1])
        if hist == "h2D":
            if variable.split("_")[0] in rangeuser_dict:
                h.GetXaxis().SetRangeUser(rangeuser_dict[variable.split("_")[0]][0],rangeuser_dict[variable.split("_")[0]][1])
            if variable.split("_")[1] in rangeuser_dict:
                h.GetYaxis().SetRangeUser(rangeuser_dict[variable.split("_")[1]][0],rangeuser_dict[variable.split("_")[1]][1])

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

        inttype = int(recotrutype.split("_")[-1])
        h = f.Get(name).Clone()
        if h.GetEntries() <= 0 and inttype not in [1,2,3,4,8]: 
            continue
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
        
        h.SetLineWidth(typeslinewidth)
        h.SetFillColor(catscolors[inttype])
        h.SetLineColor(ROOT.TColor.GetColorDark(catscolors[inttype]))
        h.Scale(POTScale)

        if variable in rangeuser_dict:
            h.GetXaxis().SetRangeUser(rangeuser_dict[variable][0],rangeuser_dict[variable][1])
        if hist == "h2D":
            if variable.split("_")[0] in rangeuser_dict:
                h.GetXaxis().SetRangeUser(rangeuser_dict[variable.split("_")[0]][0],rangeuser_dict[variable.split("_")[0]][1])
            if variable.split("_")[1] in rangeuser_dict:
                h.GetYaxis().SetRangeUser(rangeuser_dict[variable.split("_")[1]][0],rangeuser_dict[variable.split("_")[1]][1])

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
        if "MC" in stage or "mc" in stage:
            h.SetLineColor(catscolors[0])
            h.SetFillColorAlpha(catscolors[0], alphalevel)
            h.SetLineWidth(typeslinewidth1D)
        else:
            h.SetLineColor(ROOT.kBlack)
            h.SetMarkerColor(ROOT.kBlack)
            h.SetMarkerStyle(data_marker_style)
            h.SetFillColor(0)
            if hist == "h":
                h.SetMarkerSize(data_marker_size)
                h.SetLineWidth(typeslinewidth)
            if hist == "h2D":
                # h.SetMarkerSize(data_marker_size2d)
                h.SetMarkerSize(data_marker_size)
                h.SetLineWidth(typeslinewidth)
        # TODO width normalize?
        # h.Scale(1.0, "width")
        if var in rangeuser_dict:
            h.GetXaxis().SetRangeUser(rangeuser_dict[var][0],rangeuser_dict[var][1])
        if hist == "h2D":
            if var.split("_")[0] in rangeuser_dict:
                h.GetXaxis().SetRangeUser(rangeuser_dict[var.split("_")[0]][0],rangeuser_dict[var.split("_")[0]][1])
            if var.split("_")[1] in rangeuser_dict:
                h.GetYaxis().SetRangeUser(rangeuser_dict[var.split("_")[1]][0],rangeuser_dict[var.split("_")[1]][1])

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
        if "MC" not in stage and "mc" not in stage:
            print(stage)
            sys.exit(1)
        
        h.SetFillColor(catscolors[inttype])
        h.SetLineColor(ROOT.TColor.GetColorDark(catscolors[inttype]))
        h.SetLineWidth(typeslinewidth)
        
        # TODO width normalize?
        # h.Scale(1.0, "width")
        if var in rangeuser_dict:
            h.GetXaxis().SetRangeUser(rangeuser_dict[var][0],rangeuser_dict[var][1])
        if hist == "h2D":
            if var.split("_")[0] in rangeuser_dict:
                h.GetXaxis().SetRangeUser(rangeuser_dict[var.split("_")[0]][0],rangeuser_dict[var.split("_")[0]][1])
            if var.split("_")[1] in rangeuser_dict:
                h.GetYaxis().SetRangeUser(rangeuser_dict[var.split("_")[1]][0],rangeuser_dict[var.split("_")[1]][1])
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
    # mctot.AddMissingErrorBandsAndFillWithCV(i_mctot)
    mctot.AddMissingErrorBandsAndFillWithCV(ratio)
    ratio.Divide(ratio,mctot,1.0,1.0)
    
    ratio.SetLineColor(i_data.GetLineColor())
    ratio.SetLineWidth(i_data.GetLineWidth())
    ratio.SetMarkerColor(i_data.GetMarkerColor())
    ratio.SetMarkerStyle(i_data.GetMarkerStyle())
    ratio.SetMarkerSize(i_data.GetMarkerSize())
    
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
        tmp_hist.SetLineColor(i_typesdict[key].GetLineColor())
        tmp_hist.SetLineWidth(i_typesdict[key].GetLineWidth())
        tmp_hist.SetFillColor(0)
        typesratiodict[key] = tmp_hist

    #     # Add original to get an mctot
    #     if first:
    #         tmp_typestot = i_typesdict[key].Clone("typestot")
    #         first = False
    #         continue
    #     tmp_typestot.Add(i_typesdict[key])
    
    # # Check if types mctot is similar to the 
    # if tmp_typestot.GetMaximumBin() != i_mctot.GetMaximumBin():
    #     print("ERROR: types hist total is different than mctot...", i_mctot.GetName())
    #     sys.exit(1)
    
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
            # print("\t%s\t%s"%(tmp_data.GetBinContent(i),tmp_data.GetBinError(i)))
            cont_and_err = tmp_data.GetBinContent(i) + tmp_data.GetBinError(i)
            if cont_and_err > tmp_max:
                # print("\tcont_and_err:", cont_and_err, "\ttmp_max", tmp_max)
                tmp_max = cont_and_err
                # return cont_and_err
    # print("\tGoing with tmp max cont_and_err:", cont_and_err, "\ttmp_max:", tmp_max)
    return tmp_max

def DrawDataMCTypesPlot1D_AxisChange(i_data_hist, i_mctot_hist, i_mc_typeshistdict, x_title, y_title, outdirname, canvas_name, canvas_title):
    tmp_pad_rmarg = pad_rmarg + 0.02
    mnvPlotter = MnvPlotter(8)
    SetupErrorSummary(mnvPlotter)

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
    if do_titleonplot:
        top.SetTopMargin(topmarg+0.08)
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
    # ratio.GetYaxis().SetTitle("Data / MC")
    ratio.GetYaxis().SetTitle("Ratio")
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


    # cc.Print(os.path.join(outdirname, thename + ".png"))
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
    # mnvPlotter.error_color_map["Flux"] = ROOT.kViolet + 6
    # # mnvPlotter.error_color_map["Recoil Reconstruction"] = ROOT.kOrange + 2
    # mnvPlotter.error_color_map["GENIE Int. Model"] = ROOT.kMagenta
    # mnvPlotter.error_color_map["FSI Model"] = ROOT.kRed
    # mnvPlotter.error_color_map["Muon"] = ROOT.kGreen + 3
    # # mnvPlotter.error_color_map["Muon Reconstruction"] = ROOT.kGreen
    # # mnvPlotter.error_color_map["Muon Energy"] = ROOT.kGreen + 3
    # # mnvPlotter.error_color_map["Muon_Energy_MINERvA"] = ROOT.kRed - 3
    # # mnvPlotter.error_color_map["Muon_Energy_MINOS"] = ROOT.kViolet - 3
    # # mnvPlotter.error_color_map["Other"] = ROOT.kGreen + 3
    # # mnvPlotter.error_color_map["Low Recoil Fits"] = ROOT.kRed + 3
    # mnvPlotter.error_color_map["Response"] = ROOT.kRed + 3
    # mnvPlotter.error_color_map["GEANT"] = ROOT.kBlue
    # # mnvPlotter.error_color_map["Background Subtraction"] = ROOT.kGreen
    # mnvPlotter.error_color_map["Tune"] = ROOT.kOrange + 2

    mnvPlotter.error_color_map["Flux"] = ROOT.kP10Violet
    mnvPlotter.error_color_map["GENIE Int. Model"] = ROOT.kP10Blue
    mnvPlotter.error_color_map["FSI Model"] = ROOT.kP10Red
    mnvPlotter.error_color_map["Muon"] = ROOT.kP10Orange
    mnvPlotter.error_color_map["Response"] = ROOT.kP10Green
    mnvPlotter.error_color_map["GEANT"] = ROOT.kP10Cyan
    mnvPlotter.error_color_map["Tune"] = ROOT.kP10Yellow


    out_name_dict = {}
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
    out_name_dict["FSI Model"] = FSI_Model_list
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
    mnvPlotter.error_summary_group_map["GENIE Int. Model"] = Genie_Interaction_Model_list
    out_name_dict["GENIE Int. Model"] = Genie_Interaction_Model_list

    Tune_list = [
        "RPA_LowQ2",
        "RPA_HighQ2",
        "NonResPi",
        "2p2h",
        "LowQ2Pi",
        "Low_Recoil_2p2h_Tune",
    ]
    mnvPlotter.error_summary_group_map["Tune"] = Tune_list
    out_name_dict["MnvTune"] = Tune_list

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
    out_name_dict["Response"] = Response_list

    Geant_list = [
        "GEANT_Neutron",
        "GEANT_Proton",
        "GEANT_Pion",
    ]
    mnvPlotter.error_summary_group_map["GEANT"] = Geant_list
    out_name_dict["GEANT"] = Geant_list

    Muon_list = [
        "Muon_Energy_MINOS",
        "Muon_Energy_MINERvA",
        "MINOS_Reconstruction_Efficiency",
        "Muon_Energy_Resolution",
        "BeamAngleX",
        "BeamAngleY",
    ]
    mnvPlotter.error_summary_group_map["Muon"] = Muon_list
    out_name_dict["Muon"] = Muon_list

def DrawErrorSummary1D(i_hist, x_title, outdirname, canvas_name, canvas_title):
    mnvPlotter = MnvPlotter(8)
    SetupErrorSummary(mnvPlotter)
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
    mnv_hist.SetXTitle("%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(var_title,var_units))

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

    # cc.Print(os.path.join(outdirname, thename + ".png"))
    # cc.Print(os.path.join(outdirname, "source", thename + ".C"))

    cc.Print(os.path.join(outdirname,canvas_name + ".pdf"),"Title:%s"%(thetitle))


def PanelCanvas(name, n_xbins, n_ybins, x_size=1000, y_size=750, do_tall= True):
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
    
    if grid_x * grid_y == n_ybins:
        # grid_y+=1
        grid_x+=1
        grid_y = int(n_ybins/(grid_x-1))

    # if do_tall:
        # grid_x = 2
        # grid_y = int(n_ybins/(grid_x-1))
        # tmp_y_size = round(x_size * 3)
        # x_size = y_size
        # y_size = tmp_y_size
        # if grid_x * grid_y == n_ybins:
        #     grid_y+=1

    print("PanelCanvas: Making a grid canvas named "+name+" with a grid of ",n_xbins,"    ",n_ybins,"    ",grid_x,"    ",grid_y)

    # gc2 = PlotUtils.GridCanvas(name, grid_x, grid_y, x_size, y_size)
    gc2 = GridCanvas(name, grid_x, grid_y, x_size, y_size)
    # gc2.SetRightMargin(0.01)
    # gc2.SetLeftMargin(0.1)
    gc2.SetInterpadSpace(0.0)
    gc2.ResetPads()

    return gc2

def MakeProjHistList(i_hist, projaxis="x", n_projbins = 0):
    ret_list = []
    hist = i_hist.Clone()
    if projaxis=="x":
        if n_projbins == 0: n_projbins = hist.GetNbinsY()
        proj_nametail = "_projybin"
    elif projaxis == "y":
        if n_projbins == 0: n_projbins = hist.GetNbinsX()
        proj_nametail = "_projxbin"
    else:
        print("ERROR: invalid projaxis %s, exiting"%(projaxis))
        sys.exit(1)

    linecolor = hist.GetLineColor()
    linewidth = hist.GetLineWidth()
    linestyle = hist.GetLineStyle()
    fillcolor = hist.GetFillColor()
    markercolor = hist.GetMarkerColor()
    markerstyle = hist.GetMarkerStyle()
    markersize = hist.GetMarkerSize()
    
    for i in range(n_projbins):
        tmp_proj_name = hist.GetName() + proj_nametail + str(i)

        if projaxis == "x":
            tmp_proj = hist.ProjectionX(tmp_proj_name,i+1,i+1)#, "width")
            # ret_list.append(tmp_proj)
            # continue
        else: # if projaxis == "y"
            tmp_proj = hist.ProjectionY(tmp_proj_name,i+1,i+1)#, "width")
            # ret_list.append(tmp_proj)
            # continue
        tmp_proj.SetLineColor(linecolor)
        tmp_proj.SetLineWidth(linewidth)
        tmp_proj.SetLineStyle(linestyle)
        tmp_proj.SetFillColor(fillcolor)
        tmp_proj.SetMarkerColor(markercolor)
        tmp_proj.SetMarkerStyle(markerstyle)
        tmp_proj.SetMarkerSize(markersize)

        ret_list.append(tmp_proj)

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
    hist.SetMarkerColor(mnvh.GetMarkerColor())
    hist.SetLineWidth(mnvh.GetLineWidth())
    hist.SetLineColor(mnvh.GetLineColor())
    hist.SetMarkerSize(data_marker_size2d)
    hist.SetMarkerStyle(mnvh.GetMarkerStyle())
    # hist.SetLineStyle(1)

    stat = mnvh.GetCVHistoWithStatError()
    stat.SetMarkerColor(mnvh.GetMarkerColor())
    # end_error_size
    stat.SetLineWidth(mnvh.GetLineWidth())
    stat.SetLineColor(mnvh.GetLineColor())
    if do_pinkstat:
        stat.SetLineWidth(4)
        stat.SetLineColorAlpha(ROOT.kPink, alphalevel) #mnvh.GetLineColor())
        stat.SetFillColorAlpha(ROOT.kPink, alphalevel)
    stat.SetMarkerSize(0)
    stat.SetMarkerStyle(1)
    # stat.SetLineStyle(1)

    return hist, stat

def GetMCHistsForPlot(mnv_mchist):
    mnvh = mnv_mchist.Clone()

    hist = mnvh.GetCVHistoWithError(True,False)
    hist.SetFillColor(0)
    hist.SetLineColor(catscolors[0])
    hist.SetLineWidth(typeslinewidth+1)
    # hist.SetLineStyle(1)

    band = mnvh.GetCVHistoWithError(True,False)
    band.SetFillStyle(1001)
    # band.SetFillColorAlpha(typescolors[0], 0.3)
    # band.SetFillColor(ROOT.kRed - 10)
    band.SetFillColorAlpha(catscolors[0], alphalevel)
    band.SetLineColor(catscolors[0])
    band.SetLineWidth(typeslinewidth+1)
    band.SetMarkerStyle(0)

    return hist, band

# def MakeMCTypesHistsPretty(i_mc_types_dict, whichstack = "ratio", is1d=True):
#     tmp_linewidth = typeslinewidth1D
#     if not is1d: 
#         tmp_linewidth = typeslinewidth
#     if whichstack = ""
#     for key in i_mc_types_dict:
        



def DrawDataMCPlot1D_new(i_data_hist, i_mc_hist, i_mc_typeshistdict, x_title, y_title, outdirname, canvas_name, canvas_title,nametag = "", do_stack = True, do_nostack = True, i_comp_data_hist = False):
    # mnvPlotter = SetupErrorSummary(MnvPlotter(8))
    mnvPlotter = MnvPlotter(8)
    SetupErrorSummary(mnvPlotter)
    
    mnv_data = i_data_hist.Clone()
    mnv_data.Scale(1.0, "width")
    if i_comp_data_hist:
        mnv_compdata = i_comp_data_hist.Clone()
        mnv_compdata.Scale(1.0, "width")

    mnv_mc = i_mc_hist.Clone()
    mnv_mc.Scale(1.0, "width")
    my_catstodo = catstodo
    if "data" in catstodo:
        my_catstodo = [cat for cat in catstodo[1:]]
    bad_keys = []
    for key in my_catstodo:
        if key not in i_mc_typeshistdict: 
            bad_keys.append(key)
            continue
    for key in bad_keys:
        my_catstodo.remove(key)
    if global_domodelcomp and len(my_catstodo) == 0:
        print("HERE")
        my_catstodo = list(i_mc_typeshistdict.keys())


    mc_typeshistdict = {}
    stack = THStack("stack","")
    for key in reversed(my_catstodo):
        if key not in i_mc_typeshistdict: continue
        hist = i_mc_typeshistdict[key].Clone()
        hist.Scale(1.0, "width")
        hist.SetLineWidth(typeslinewidth1D)
        if key in bkgcats:
            hist.SetFillStyle(bkgfillstyle[key]+100)
        stack.Add(hist)
        mc_typeshistdict[key] = hist.Clone()

    thename = canvas_name + nametag
    thetitle = canvas_title 

    ysize = _ysize
    xsize = _xsize

    # plottitle_string = "%s - %s"%(canvas_title, x_title.split(" (")[0])
    plottitle_string = "%s"%(canvas_title)

    axislabel_size = 0.07 #0.04
    axistitle_size = 0.09 #0.07
    y_axistitle_offset = 0.55 #0.6
    for name in scaleY:
        if name in x_title:
            y_axistitle_offset = 0.65
            break
    if x_title.split(" (")[0] in scaleY:
        y_axistitle_offset = 0.65
    x_axistitle_offset =  0.8#0.8
    mnv_data.SetLineWidth(typeslinewidth1D)
    data_hist, data_stat = GetDataHistsForPlot(mnv_data)
    data_hist.SetMarkerSize(data_marker_size)
    data_stat.SetMarkerSize(data_marker_size)
    data_hist.GetYaxis().SetTitle(y_title)
    data_hist.GetYaxis().SetTitleFont(42)
    data_hist.GetYaxis().CenterTitle()
    data_hist.GetYaxis().SetTitleOffset(y_axistitle_offset)
    data_hist.GetYaxis().SetTitleSize(axistitle_size)
    data_hist.GetYaxis().SetLabelSize(axislabel_size)


    mc_hist, mc_band = GetMCHistsForPlot(mnv_mc)
    mc_hist.SetLineWidth(typeslinewidth1D)
    mc_band.SetLineWidth(typeslinewidth1D)

    mnv_ratio = MakeDataMCRatioForPlot(mnv_data, mnv_mc)
    ratio, ratio_stat = GetDataHistsForPlot(mnv_ratio)
    ratio.SetMarkerSize(data_marker_size)
    ratio.SetLineWidth(typeslinewidth1D)
    ratio_stat.SetMarkerSize(data_marker_size)
    ratio_stat.SetLineWidth(typeslinewidth1D)

    ratio.SetFillStyle(0)
    ratio.SetMinimum(0.0001)
    ratio.SetMaximum(1.999)

    if i_comp_data_hist:
        mnv_compdata.SetLineWidth(typeslinewidth1D)
        compdata_hist, compdata_stat = GetDataHistsForPlot(mnv_compdata)
        compdata_hist.SetMarkerSize(data_marker_size)
        compdata_hist.SetMarkerColorAlpha(ROOT.kP8Pink, 0.8)
        compdata_hist.SetLineColorAlpha(ROOT.kP8Pink, 0.8)
        compdata_stat.SetMarkerSize(data_marker_size)
        compdata_stat.SetMarkerColorAlpha(ROOT.kP8Pink, 0.8)
        compdata_stat.SetLineColorAlpha(ROOT.kP8Pink, 0.8)

        compmnv_ratio = MakeDataMCRatioForPlot(mnv_compdata, mnv_mc)
        compratio, compratio_stat = GetDataHistsForPlot(compmnv_ratio)
        compratio.SetMarkerSize(data_marker_size)
        compratio.SetLineWidth(typeslinewidth1D)
        compratio.SetMarkerColorAlpha(ROOT.kP8Pink, 0.8)
        compratio.SetLineColorAlpha(ROOT.kP8Pink, 0.8)
        compratio_stat.SetMarkerSize(data_marker_size)
        compratio_stat.SetLineWidth(typeslinewidth1D)
        compratio_stat.SetMarkerColorAlpha(ROOT.kP8Pink, 0.8)
        compratio_stat.SetLineColorAlpha(ROOT.kP8Pink, 0.8)

    typesratio_dict = {}
    for key in my_catstodo:
        if key not in mc_typeshistdict: continue
        tmp_typesratio = mc_typeshistdict[key].Clone()
        tmp_typesratio.Divide(tmp_typesratio, mnv_mc,1.0,1.0)
        tmp_typesratio.SetLineWidth(typeslinewidth1D)
        tmp_typesratio.SetFillStyle(0)
        tmp_typesratio.SetFillColor(0)
        # tmp_typesratio.SetLineColor(mc_typeshistdict[key].GetLineColor())
        tmp_typesratio.SetLineColor(catscolors[key])

        if type(key) == int:
            if key > 10:
                tmp_typesratio.SetLineStyle(2)

        typesratio_dict[key] = tmp_typesratio
    typesratio_stack_dict = {}
    if 11 in my_catstodo:
        for key in reversed(my_catstodo):
            tmp_hist = typesratio_dict[key].Clone()
            tmp_hist.SetLineColor(catscolors[key])
            if key not in typesratio_dict: continue
            if key > 10: continue
            if key not in typesratio_stack_dict:
                typesratio_stack_dict[key] = {}
            tmp_stack = THStack("tmpstack, i", "")
            if key + 10 not in my_catstodo:
                typesratio_stack_dict[key] = tmp_hist
                continue
            tmp_hist_bkg = typesratio_dict[key+10].Clone()
            tmp_hist.Add(tmp_hist_bkg,1.0)
            typesratio_stack_dict[key] = tmp_hist
            continue
            # tmp_hist_bkg.SetLineStyle(7)
            # tmp_stack.Add(tmp_hist_bkg)
            # typesratio_stack_dict[key] = tmp_stack
            # if tmp_hist.GetEntries() == 0: continue
            # typesratio_stack_dict[key].Add(tmp_hist)            
    ratio_mnvmc_band = mnv_mc.Clone()
    ratio_mnvmc_band.ClearAllErrorBands()
    ratio_mnvmc_band.AddMissingErrorBandsAndFillWithCV(mnv_mc)
    ratio_mnvmc_band.Divide(ratio_mnvmc_band,mnv_mc,1.0,1.0)
    straightline, band_ratio = GetMCHistsForPlot(ratio_mnvmc_band) 
    straightline.SetLineWidth(typeslinewidth1D)
    band_ratio.SetLineWidth(typeslinewidth1D)
    
    ROOT.gStyle.SetEndErrorSize(round(end_error_size*1.5)) # This makes the ticks at the end of the error bars longer

    pad_max = GetPadMax(mnv_data,mnv_mc,True)


    # mc_band.SetMaximum(1.2 * pad_max)
    # mc_band.SetMinimum(data_hist.GetMaximum()*0.001)

    # Now set up the canvas
    plottitle_size = 0.07 #0.058
    my_xsize = _xsize
    tmp_pad_rmarg = pad_rmarg
    # if x_title.split(" (")[0] in scaleY:
    #     my_xsize = round(1.05 * _xsize)
    #     tmp_pad_rmarg = pad_rmarg * (1 + _xsize/my_xsize)
    cc = ROOT.TCanvas(thename, thetitle,my_xsize, _ysize)
    cc.SetCanvasSize(my_xsize,_ysize)
    cc.SetLeftMargin(0.25)
    cc.SetRightMargin(0.15)
    cc.SetBottomMargin(0.1)
    tmp_topmarg = topmarg
    if do_titleonplot:
        cc.SetTopMargin(0.1)
        tmp_topmarj = topmarg + plottitle_size + 0.01
    cc.SetFrameLineWidth(1)
    cc.cd()
    cc.Draw()

    plottitle = ROOT.TLatex(pad_lmarg+((1-tmp_pad_rmarg -pad_lmarg)/2), 0.96,plottitle_string)
    plottitle.SetTextAlign(22)
    plottitle.SetTextFont(52)
    plottitle.SetTextSize(plottitle_size)

    # top = ROOT.TPad("hist", "hist", 0, 0.0, 1.0, 1.0)
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

    x2 = 1. - tmp_pad_rmarg - (0.02 * padwidth)
    x1 = x2 - 0.3 # padwidth * 0.17
    y2 = 1 - tmp_topmarj - (0.02 * padheight)
    y1 = y2 - 0.45 # * padheight
    tmp_latex_x = x2
    tmp_latex_y = y1 - 0.05
    leg = TLegend(x1, y1, x2, y2)
    leg.SetBorderSize(0)
    leg.SetFillColor(-1)
    leg.SetFillStyle(0)
    # leg.SetTextSize(legendfontsize)
    # leg.SetNColumns(2)
    leg.SetTextFont(42)

    
    stack_unstack = []
    # This will plot the histograms stacked on top of each other
    if do_stack:
        stack_unstack.append("stack")
    # This will plot the histograms unstacked
    if do_nostack:
        stack_unstack.append("nostack")
    # This will just plot data and total mc
    stack_unstack.append("nobreakdown")
    npasses = 0
    for whichstack in stack_unstack:

        top.cd()
        data_hist.SetMaximum(1.2 * pad_max)
        data_hist.SetMinimum(data_hist.GetMaximum()*0.001)
        # if x_title.split(" (")[0] in scaleY:
        for name in scaleY:
            if name in x_title:
                data_hist.SetMaximum(2.0 * pad_max)
                # data_hist.SetMinimum(data_hist.GetMaximum()*0.0005)
                data_hist.SetMinimum(data_hist.GetBinContent(data_hist.GetMinimumBin())*0.17)
                top.SetLogy()
                break

        top.Modified()
        top.Update()
        # leg.Clear()
        data_hist.Draw("PE1 E0 X0 9")
        if whichstack == "stack":
            stack.Draw("hist 9 same")
        elif whichstack == "nostack":
            mc_band.Draw("9 E2 E0 ][ same")
            tmp_stack = stack.Clone()
            for hist in tmp_stack.GetHists():
                hist.SetFillStyle(0)
                hist.SetLineColor(hist.GetFillColor())
                hist.SetLineWidth(typeslinewidth1D)
            tmp_stack.Draw("hist nostack noclear 9 same")
            mc_hist.Draw("9 hist same")
        else:
            mc_band.Draw("9 E2 E0 ][ same")
            mc_hist.Draw("9 hist same")

        data_hist.Draw("PE1 E0 X0 same 9")
        
        if do_pinkstat:
            ROOT.gStyle.SetEndErrorSize(0) # This makes the ticks at the end of the error bars longer
            data_stat.Draw("9 SAME X0 %s E0"%staterror_drawopt)
            ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer
        else:
            data_stat.Draw("9 SAME X0 %s E0"%staterror_drawopt)

        if i_comp_data_hist:
            compdata_hist.Draw("PE1 E0 X0 same 9")
            compdata_stat.Draw("9 SAME X0 %s E0"%staterror_drawopt)

        data_hist.Draw("9 Same PE1 E0 X0")
        data_hist.Draw("Axis same")

        prelim = AddPreliminary()
        prelim.SetTextAlign(11)
        prelim.DrawLatex(x1, y1 - 0.145, prelim_string)

        datapottext = AddDataPOTInfo()
        datapottext.SetTextAlign(11)
        datapottext.DrawLatex(x1, y1 - 0.045, datapot_string1)
        datapottext.DrawLatex(x1, y1 - 0.100, datapot_string2)

        # chi2 = mnvPlotter.Chi2DataMC(mnv_data,mnv_mc,mnv_data.GetNbinsX()-1)
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


        ratio.SetTitle("")            
        # ratio.GetYaxis().SetTitle("Data / MC")
        ratio.GetYaxis().SetTitle("Ratio")
        ratio.GetYaxis().SetTitleFont(42)
        ratio.GetYaxis().CenterTitle()
        ratio.GetYaxis().SetTitleSize(axistitle_size * areaScale)
        ratio.GetYaxis().SetTitleOffset(y_axistitle_offset / areaScale)
        ratio.GetYaxis().SetLabelSize(axislabel_size * areaScale)
        ratio.GetYaxis().SetNdivisions(505)

        # ratio.GetXaxis().SetTitle(vars_info[c_var]["title"])
        ratio.GetXaxis().SetTitle(x_title)
        ratio.GetXaxis().CenterTitle()
        ratio.GetXaxis().SetTitleOffset(x_axistitle_offset)
        ratio.GetXaxis().SetTitleSize(axistitle_size * areaScale)
        ratio.GetXaxis().SetLabelSize(axislabel_size * areaScale)
        
        ratio.Draw("9 E1 E0 X0")

        # Now do mc uncertainties
        band_ratio.Draw("9 E2 same ][")
        straightline.Draw("9 Hist same, ][")
        if 11 in my_catstodo:
            for key in reversed(typestodo_leg):
                if key > 10: continue
                # typesratio_stack_dict[key].Draw("9 HIST NOCLEAR SAME")
                typesratio_stack_dict[key].Draw("9 HIST SAME")
        elif whichstack!="nobreakdown":
            for key in reversed(my_catstodo):
                if key not in typesratio_dict: continue
                if key == "data": continue
                # typesratio_dict[key].SetLineColor(catscolors[key])
                typesratio_dict[key].SetLineColor(catscolors[key])
                typesratio_dict[key].Draw("9 HIST SAME")
        
        if do_pinkstat:
            ROOT.gStyle.SetEndErrorSize(0) # This makes the ticks at the end of the error bars longer
            ratio_stat.Draw("9 SAME X0 %s E0"%staterror_drawopt)
            ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer
        else:
            ratio_stat.Draw("9 SAME X0 %s E0"%staterror_drawopt)
        ratio.Draw("9 same E1 E0 X0")
        if i_comp_data_hist:
            compratio.Draw("9 SAME X0 E1 E0")
            compratio_stat.Draw("9 SAME X0 E1 E0")
        ratio.Draw("9 same axis")
        bottom.Modified()
        bottom.Update()
        top.cd()
        if 11 in mc_typeshistdict:
            leg.SetNColumns(2)
        leg.AddEntry(data_hist, catsnames["data"],"pe")
        leg.AddEntry(band_ratio, catsnames[0],"fl")
        if i_comp_data_hist:
            leg.AddEntry(compdata_hist, catsnames["compdata"], "pe")
        if whichstack == "stack":
            for cat in my_catstodo:
                if 11 in mc_typeshistdict and cat > 10: continue
                if cat not in mc_typeshistdict: continue
                leg.AddEntry(mc_typeshistdict[cat],catsnames[cat], "fl")
                if 11 in mc_typeshistdict:
                    leg.AddEntry(mc_typeshistdict[cat + 10],catsnames[cat + 10], "fl")
        elif whichstack == "nostack":
            for cat in my_catstodo:
                if 11 in mc_typeshistdict and cat > 10: continue
                if cat not in mc_typeshistdict: continue
                mc_typeshistdict[cat].SetLineColor(mc_typeshistdict[cat].GetFillColor())
                mc_typeshistdict[cat].SetLineWidth(typeslinewidth1D+1)
                leg.AddEntry(mc_typeshistdict[cat],catsnames[cat], "l")
                if 11 in mc_typeshistdict:
                    mc_typeshistdict[cat+10].SetLineColor(mc_typeshistdict[cat+10].GetFillColor())
                    mc_typeshistdict[cat+10].SetLineWidth(typeslinewidth1D+1)
                    mc_typeshistdict[cat+10].SetLineStyle(7)
                    leg.AddEntry(mc_typeshistdict[cat + 10],catsnames[cat + 10], "l")

        leg.Draw()
        for name in scaleX:
            if name in x_title:

            # if x_title.split(" (")[0] in scaleX:
                top.SetLogx()
                bottom.SetLogx()
                top.Modified()
                top.Update()
                bottom.Modified()
                bottom.Update()
                break
        cc.cd()
        if do_titleonplot:
            plottitle.Draw()
        cc.Modified()
        cc.Update
        cc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s %s"%(thetitle,nametag, whichstack))
        leg.Clear()
        top.Clear()
        bottom.Clear()
        top.Modified()
        top.Update()
        bottom.Modified()
        bottom.Update()
        cc.Modified()
        cc.Update()

    cc.cd()
    cc.Clear()
    cc.Modified()
    cc.Update()

def DrawDataMCPlot2D_new(
    i_data_hist, i_mc_hist, i_mc_typeshistdict, 
    x_varname, x_units, x_bins, 
    y_varname, y_units, y_bins, 
    z_title, 
    outdirname, canvas_name, canvas_title, nametag,
    i_multipliers = [],
    do_stack = True, do_nostack = True, 
    do_error_summary = True,
    i_comp_data_hist = False
):
    mnvPlotter = MnvPlotter(8)
    SetupErrorSummary(mnvPlotter)

    data_mnv2d = i_data_hist.Clone()
    data_mnv2d.Scale(1.0, "width")
    data_mnv2d_unscaled = i_data_hist.Clone()

    if i_comp_data_hist:
        compdata_mnv2d = i_comp_data_hist.Clone()
        compdata_mnv2d.Scale(1.0, "width")
        compdata_mnv2d_unscaled = i_comp_data_hist.Clone()

    mc_mnv2d = i_mc_hist.Clone()
    mc_mnv2d.Scale(1.0, "width")

    # These don't get bin width normalized before they get used for the total 1D projection hists
    mc_mnv2d_unscaled = i_mc_hist.Clone()

    mc_typeshistdict = {}
    mc_typeshistdict_unscaled = {}
    for key in i_mc_typeshistdict:
        tmphist = i_mc_typeshistdict[key].Clone()
        tmphist_unscaled = i_mc_typeshistdict[key].Clone()
        tmphist.Scale(1.0,"width")
        mc_typeshistdict[key] = tmphist
        mc_typeshistdict_unscaled[key] = tmphist_unscaled
    # n_xbins = data_mnv2d.GetNbinsX()
    # n_ybins = data_mnv2d.GetNbinsY()
    n_xbins = len(x_bins) - 1 
    n_ybins = len(y_bins) - 1
    print("hist n x bins: ",n_xbins,",\t hist n y bins: ", n_ybins)
    # my_catstodo = catstodo[1:]
    my_catstodo = catstodo
    if "data" in catstodo:
        my_catstodo = [cat for cat in catstodo[1:]]
    bad_keys = []
    for key in my_catstodo:
        if key not in mc_typeshistdict: 
            bad_keys.append(key)
            continue
    for key in bad_keys:
        my_catstodo.remove(key)
    if global_domodelcomp and len(my_catstodo) == 0:
        print("HERE")
        my_catstodo = list(mc_typeshistdict.keys())

    x_title = "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(x_varname, x_units)
    y_title = "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(y_varname, y_units)
    prelim = AddPreliminary()
    prelim.SetTextAlign(31)
    datapottext = AddDataPOTInfo()
    datapottext.SetTextAlign(31)
    chi2 = mnvPlotter.Chi2DataMC(data_mnv2d,mc_mnv2d, ctypes.c_int(n_xbins*n_ybins))
    # chi2 = mnvPlotter.Chi2DataMC(data_mnv2d,mc_mnv2d)
    chi2text = AddChi2Info()
    # chi2text.SetTextAlign(11)
    # chi2text.DrawLatex(x1, y1 - 0.205, "#it{#chi^{2}} = %.02f"%chi2)
    # chi2text.DrawLatex(x1, y1 - 0.255, "#it{ndf} = %d"%mnv_data.GetNbinsX())
    chi2text.SetTextAlign(31)
    chi2_string = "#it{#chi^{2}} = %.02f"%chi2
    
    ndf_string = "#it{ndf} = %d"%(n_xbins*n_ybins)

    axislabel_size = 0.05 #0.04
    axistitle_size = 0.06 #0.07
    y_axistitle_offset = 0.55 #0.6
    x_axistitle_offset =  0.8#0.8
    plottitle_size = 0.068 # 0.058
    for projaxis in ["x","y"]:
        # Info needed for the canvas
        thename = "%s_%s_proj%s"%(canvas_name, nametag, projaxis)
        thetitle = "%s%s proj%s"%(canvas_title,nametag.replace("_"," "),projaxis)
        ysize = _ysize
        xsize = round(_xsize*1.15)
        canvas_nxbins = n_xbins
        canvas_nybins = n_ybins

        # Info needed for panels
        # This is the bin ranges for the panels
        plot_bins = y_bins

        projtot1d_y_title = z_title
        proj_x_varname = x_varname
        proj_x_units = x_units
        proj_y_varname = y_varname
        proj_y_units = y_units

        if projaxis == "y":
            canvas_nxbins = n_ybins
            canvas_nybins = n_xbins
            plot_bins = x_bins
            proj_x_varname = y_varname
            proj_x_units = y_units
            proj_y_varname = x_varname
            proj_y_units = x_units
        # proj_xtitle = "%s (%s)"%(proj_x_varname, proj_x_units)
        proj_xtitle = "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(proj_x_varname, proj_x_units)
        if "#sigma" in z_title:
            projtot1d_y_title = "d#it{#sigma}/^{}d#it{%s}#lower[-0.15]{#scale[0.7]{ (cm^{2}/^{}(%s)/^{}Nucleon)}}"%(proj_x_varname,proj_x_units)
        else:
            projtot1d_y_title = "Counts / (%s)"%proj_x_units
        binrange_list = []
        for i in range(len(plot_bins)-1):
            range_string = "{loedge} < {var} < {hiedge}".format(
                loedge = round(plot_bins[i], 3), 
                var = "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(proj_y_varname, proj_y_units), 
                hiedge = round(plot_bins[i+1], 3)
            )
            binrange_list.append(range_string)

        # Make the projections
        data_mnvproj_list = MakeProjHistList(data_mnv2d, projaxis, canvas_nybins)
        if len(data_mnvproj_list) ==0:
            print("here")
            data_mnv2d.Print()
            print(vars_info["EAvailWithRemoval"]["bins"])
            print(x_varname)
            print(y_varname)
            print(projaxis)
            sys.exit(1)
        compdata_mnvproj_list = []
        if i_comp_data_hist:
            compdata_mnvproj_list = MakeProjHistList(compdata_mnv2d, projaxis, canvas_nybins)
        mc_mnvproj_list = MakeProjHistList(mc_mnv2d, projaxis, canvas_nybins)
        mc_typesproj_listdict = {}
        for key in mc_typeshistdict:
            if key not in mc_typesproj_listdict:
                mc_typesproj_listdict[key] = []
            tmp_list = MakeProjHistList(mc_typeshistdict[key],projaxis, canvas_nybins)
            for hist in tmp_list:
                tmp_hist = hist.Clone()
                if key in bkgcats:
                    tmp_hist.SetFillStyle(bkgfillstyle[key]+100)
                # mc_typesproj_listdict[key].append(tmp_hist.GetCVHistoWithStatError())
                mc_typesproj_listdict[key].append(tmp_hist.Clone())

        # 1D total projections
        data_mnvprojtot = MnvH1D()
        mc_mnvprojtot = MnvH1D()
        mc_typestotproj_dict = {}
        if projaxis == "x":
            data_mnvprojtot = data_mnv2d_unscaled.ProjectionX("%s_proj%s"%(data_mnv2d_unscaled.GetName(),projaxis), 0, data_mnv2d_unscaled.GetNbinsY()+2)#, "width e")
            mc_mnvprojtot = mc_mnv2d_unscaled.ProjectionX("%s_proj%s"%(mc_mnv2d_unscaled.GetName(),projaxis), 0, mc_mnv2d_unscaled.GetNbinsY()+2)#, "width e")
            for key in mc_typeshistdict:
                tmp_totproj = mc_typeshistdict_unscaled[key].ProjectionX("%s_proj%s"%(mc_typeshistdict_unscaled[key].GetName(),projaxis), 0, mc_typeshistdict_unscaled[key].GetNbinsY()+2)#, "width e")
                mc_typestotproj_dict[key] = tmp_totproj
            if i_comp_data_hist:
                compdata_mnvprojtot = compdata_mnv2d_unscaled.ProjectionX("%s_proj%s"%(compdata_mnv2d_unscaled.GetName(),projaxis), 0, compdata_mnv2d_unscaled.GetNbinsY()+2)#, "width e")
        if projaxis == "y":
            data_mnvprojtot = data_mnv2d_unscaled.ProjectionY("%s_proj%s"%(data_mnv2d_unscaled.GetName(),projaxis), 0, data_mnv2d_unscaled.GetNbinsX()+2)#, "width e")
            mc_mnvprojtot = mc_mnv2d_unscaled.ProjectionY("%s_proj%s"%(mc_mnv2d_unscaled.GetName(),projaxis), 0, mc_mnv2d_unscaled.GetNbinsX()+2)#, "width e")
            for key in mc_typeshistdict:
                tmp_totproj = mc_typeshistdict_unscaled[key].ProjectionY("%s_proj%s"%(mc_typeshistdict_unscaled[key].GetName(),projaxis), 0, mc_typeshistdict_unscaled[key].GetNbinsX()+2)#, "width e")
                mc_typestotproj_dict[key] = tmp_totproj
            if i_comp_data_hist:
                compdata_mnvprojtot = compdata_mnv2d_unscaled.ProjectionY("%s_proj%s"%(compdata_mnv2d_unscaled.GetName(),projaxis), 0, compdata_mnv2d_unscaled.GetNbinsX()+2)#, "width e")
        data_mnvprojtot.SetLineColor(data_mnv2d_unscaled.GetLineColor())
        data_mnvprojtot.SetLineWidth(data_mnv2d_unscaled.GetLineWidth())
        data_mnvprojtot.SetMarkerStyle(data_mnv2d_unscaled.GetMarkerStyle())
        data_mnvprojtot.SetMarkerColor(data_mnv2d_unscaled.GetMarkerColor())
        if i_comp_data_hist:
            compdata_mnvprojtot.SetLineWidth(compdata_mnv2d_unscaled.GetLineWidth())
            compdata_mnvprojtot.SetMarkerStyle(compdata_mnv2d_unscaled.GetMarkerStyle())
            compdata_mnvprojtot.SetMarkerColorAlpha(ROOT.kP8Pink, 0.8)
            compdata_mnvprojtot.SetLineColorAlpha(ROOT.kP8Pink, 0.8)
        
        mc_mnvprojtot.SetLineWidth(mc_mnvprojtot.GetLineWidth())
        mc_mnvprojtot.SetLineColor(mc_mnvprojtot.GetLineColor())
        mc_mnvprojtot.SetLineStyle(mc_mnvprojtot.GetLineStyle())
        mc_mnvprojtot.SetFillColor(mc_mnvprojtot.GetFillColor())
        for key in mc_typestotproj_dict:
            mc_typestotproj_dict[key].SetLineWidth(mc_typestotproj_dict[key].GetLineWidth())
            mc_typestotproj_dict[key].SetLineColor(mc_typestotproj_dict[key].GetLineColor())
            mc_typestotproj_dict[key].SetLineStyle(mc_typestotproj_dict[key].GetLineStyle())
            mc_typestotproj_dict[key].SetFillColor(mc_typestotproj_dict[key].GetFillColor())

        # TODO
        if not i_comp_data_hist:
            DrawDataMCPlot1D_new(
                data_mnvprojtot, mc_mnvprojtot, mc_typestotproj_dict, 
                proj_xtitle, 
                projtot1d_y_title, 
                outdirname, 
                canvas_name, 
                canvas_title,
                "_totalproj%s_%s"%(projaxis,nametag), 
                do_stack, do_nostack
            )
        else:
            DrawDataMCPlot1D_new(
                data_mnvprojtot, mc_mnvprojtot, mc_typestotproj_dict, 
                proj_xtitle, 
                projtot1d_y_title, 
                outdirname, 
                canvas_name, 
                canvas_title,
                "_totalproj%s_%s"%(projaxis,nametag), 
                do_stack, do_nostack,
                compdata_mnvprojtot
            )
        # if "E_{Avail}" in proj_xtitle and not do_comparison:
        # if "E_{Avail}" in proj_xtitle:
        #     DrawDataMCTypesPlot1D_AxisChange(data_mnvprojtot, mc_mnvprojtot, mc_typestotproj_dict, proj_xtitle, z_title, outdirname, canvas_name, canvas_title+" total proj")

        ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer


        n_pads = len(data_mnvproj_list)

        # These are the hists w/ total error
        data_hist_list = []
        # These are the hists w/ just stat error
        data_stat_list = []

        compdata_hist_list = []
        compdata_stat_list = []

        # These are just used for the CV
        mc_hist_list = []
        # These are used for the errors, to make a band around MC
        mc_band_list = []

        ratio_list = []
        ratio_stat_list = []
        compratio_list = []
        compratio_stat_list = []

        straightline_list = []
        mcerror_list = []
        typesratio_listdict = {}
        typesratiostack_listdict = {}

        for hist in data_mnvproj_list:
            data_hist, data_stat = GetDataHistsForPlot(hist)
            data_hist_list.append(data_hist)
            data_stat_list.append(data_stat)

        for comphist in compdata_mnvproj_list:
            compdata_hist, compdata_stat = GetDataHistsForPlot(comphist)
            compdata_hist.SetMarkerColorAlpha(ROOT.kP8Pink, 0.8)
            compdata_hist.SetLineColorAlpha(ROOT.kP8Pink, 0.8)
            compdata_stat.SetMarkerColorAlpha(ROOT.kP8Pink, 0.8)
            compdata_stat.SetLineColorAlpha(ROOT.kP8Pink, 0.8)
            compdata_hist_list.append(compdata_hist)
            compdata_stat_list.append(compdata_stat)

        # TODO: do I actually use these?
        for hist in mc_mnvproj_list:
            mc_hist, mc_band = GetMCHistsForPlot(hist)
            mc_hist_list.append(mc_hist)
            mc_band_list.append(mc_band)
        maxlist = [GetPadMax(data_hist_list[i],mc_hist_list[i], True) for i in range(len(data_hist_list))]
        if len(maxlist) == 0:
            print(mc_hist_list)
            print(x_varname)
            print(y_varname)
            print(projaxis)
        global_max = max(maxlist)
        minlist = [data_hist_list[i].GetBinContent(data_hist_list[i].GetMinimumBin()) for i in range(len(data_hist_list))]
        global_min = max(minlist)
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
            for cat in reversed(my_catstodo):
                # if cat == "data": continue
                if cat not in mc_typesproj_listdict: continue
                mc_typesproj_listdict[cat][i].Scale(tmp_pad_scale)
                tmp_type_hist = mc_typesproj_listdict[cat][i].Clone()
                stack_list[i].Add(tmp_type_hist)

            data_hist_list[i].SetMaximum(1.2 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
            data_hist_list[i].SetMinimum(0.0001*data_hist_list[i].GetMaximum())
            
            data_hist_list[i].GetXaxis().SetNdivisions(505)
            data_hist_list[i].GetYaxis().SetNdivisions(505)
            # data_hist_list[i].GetYaxis().SetLabelSize(data_hist_list[i].GetXaxis().GetLabelSize())
            data_hist_list[i].GetYaxis().SetLabelSize(axislabel_size)
            data_hist_list[i].GetXaxis().SetLabelSize(axislabel_size)

            if proj_x_varname in scaleY:
                data_hist_list[i].SetMaximum(2.2 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
                # data_hist_list[i].SetMinimum(0.0001*data_hist_list[i].GetMaximum())
                data_hist_list[i].SetMinimum(0.1*global_min)
                data_hist_list[i].GetXaxis().SetNdivisions(504)
                # data_hist_list[i].GetYaxis().SetLabelSize(data_hist_list[i].GetXaxis().GetLabelSize()*0.67)
                data_hist_list[i].GetYaxis().SetLabelSize(axislabel_size*0.67)
            # else:
            #     print(global_max)
            #     sys.exit(1)
            ratio_mnvh = MakeDataMCRatioForPlot(data_mnvproj_list[i],mc_mnvproj_list[i])
            ratio_hist, ratio_stat = GetDataHistsForPlot(ratio_mnvh)

            ratio_hist.SetMaximum(2.9999)
            ratio_hist.SetMinimum(0.0001)

            ratio_hist.GetXaxis().SetNdivisions(505)
            ratio_hist.GetYaxis().SetNdivisions(505)
            if proj_x_varname in scaleY:
                ratio_hist.GetXaxis().SetNdivisions(504)

            # ratio_hist.GetYaxis().SetLabelSize(ratio_hist.GetXaxis().GetLabelSize())
            ratio_hist.GetYaxis().SetLabelSize(axislabel_size)
            ratio_hist.GetXaxis().SetLabelSize(axislabel_size)

            ratio_list.append(ratio_hist)
            ratio_stat_list.append(ratio_stat)
            if len(compdata_hist_list) == len(data_hist_list):
                compdata_hist_list[i].Scale(tmp_pad_scale)
                compdata_stat_list[i].Scale(tmp_pad_scale)
                compratio_mnvh = MakeDataMCRatioForPlot(compdata_mnvproj_list[i],mc_mnvproj_list[i])
                compratio_hist, compratio_stat = GetDataHistsForPlot(compratio_mnvh)

                compratio_hist.SetMarkerColorAlpha(ROOT.kP8Pink, 0.8)
                compratio_hist.SetLineColorAlpha(ROOT.kP8Pink, 0.8)
                compratio_stat.SetMarkerColorAlpha(ROOT.kP8Pink, 0.8)
                compratio_stat.SetLineColorAlpha(ROOT.kP8Pink, 0.8)

                compratio_list.append(compratio_hist)
                compratio_stat_list.append(compratio_stat)

            for key in reversed(my_catstodo):
                if key not in mc_typesproj_listdict: continue
                tmp_typesratio = TH1D(mc_typesproj_listdict[key][i].Clone())
                tmp_typesratio.Divide(tmp_typesratio,mc_hist_list[i],1.0,1.0)
                tmp_typesratio.SetLineWidth(typeslinewidth+1)
                tmp_typesratio.SetFillColor(0)
                tmp_typesratio.SetLineColor(mc_typesproj_listdict[key][i].GetFillColor())
                # if type(key) == int:
                #     if key >= 10: tmp_typesratio.SetLineStyle(2)
                if key not in typesratio_listdict.keys():
                    typesratio_listdict[key] = []
                typesratio_listdict[key].append(tmp_typesratio)
            if 11 in mc_typesproj_listdict:
                for key in reversed(my_catstodo):
                    if key not in mc_typesproj_listdict: continue
                    if key > 10: continue
                    if key not in typesratiostack_listdict: 
                        typesratiostack_listdict[key] = []
                    tmp_hist = typesratio_listdict[key][i].Clone()
                    tmp_stack = THStack()
                    if key + 10 not in my_catstodo[1:]:
                        # tmp_stack.Add(tmp_hist)
                        typesratiostack_listdict[key].append(tmp_hist)
                        continue
                    typesratiostack_listdict[key].append(tmp_stack)
                    tmp_hist_bkg = typesratio_listdict[key+10][i].Clone()
                    tmp_hist_bkg.SetLineStyle(7)
                    typesratiostack_listdict[key][i].Add(tmp_hist_bkg)
                    if tmp_hist.GetEntries() == 0: continue
                    typesratiostack_listdict[key][i].Add(tmp_hist)

            straightline = TH1D()
            straightline = mc_hist_list[i].Clone()
            for j in range(1,mc_hist_list[i].GetXaxis().GetNbins() + 1):
                straightline.SetBinContent(j,1.0)
            straightline.SetLineColor(catscolors[0])
            straightline.SetLineWidth(typeslinewidth+1)
            straightline.SetFillStyle(0)
            straightline_list.append(straightline)

            
            tmp_mnvh_mc = mc_mnvproj_list[i].Clone()
            tmp_mnvh_mc.ClearAllErrorBands()
            tmp_mnvh_mc.AddMissingErrorBandsAndFillWithCV(mc_mnvproj_list[i])
            tmp_mnvh_mc.Divide(tmp_mnvh_mc,mc_mnvproj_list[i],1.0,1.0)
            tmp_mnvh_mc.SetFillColor(catscolors[0])
            tmp_mnvh_mc.SetFillColorAlpha(catscolors[0], alphalevel)
            tmp_mnvh_mc.SetLineColor(catscolors[0])
            tmp_mnvh_mc.SetLineWidth(typeslinewidth)
            tmp_mnvh_mc.SetMarkerStyle(0)
            tmp_mnvh_mc.SetFillStyle(1001)
            mcerror_list.append(tmp_mnvh_mc.GetCVHistoWithError())
            


        # print(multipliers)
        # if projaxis == "y":
        #     sys.exit(1)
        gc = PanelCanvas(thename, canvas_nxbins, canvas_nybins, round(xsize), round(ysize))
        my_topmarg = 0.05
        if do_titleonplot: 
            # my_topmarg += 0.065
            my_topmarg = (axistitle_size/2) + 0.04
        my_bottommarg = 0.1
        my_rightmarg = pad_rmarg # 0.03
        my_leftmarg = pad_lmarg #0.08
        
        gc.SetTopMargin(my_topmarg)
        gc.SetBottomMargin(my_bottommarg)
        gc.SetRightMargin(my_rightmarg)
        gc.SetLeftMargin(my_leftmarg)
        # if proj_x_varname in scaleY:
        #     # gc.SetLeftMargin(0.11)
        # plottitle_string = "%s - %s, %s"%(canvas_title, x_varname, y_varname)
        plottitle_string = "%s"%(canvas_title)#, x_varname, y_varname)
        # plottitle = ROOT.TLatex(0.5, 0.96,plottitle_string)
        plottitle = ROOT.TLatex(my_leftmarg + 0.5*(1 - my_leftmarg - my_rightmarg), 0.97, plottitle_string)
        plottitle.SetTextAlign(22)
        plottitle.SetTextFont(52)
        plottitle.SetTextSize(plottitle_size)

        # gc.SetFrameLineWidth(1)
        gc.SetXTitle(proj_xtitle)
        # gc.SetYTitle(z_title)
        ytitle_latex = ROOT.TLatex()
        ytitle_latex.SetTextFont(43)
        ytitle_latex.SetTextSize(_ysize * axistitle_size)
        ytitle_latex.SetTextAngle(90)
        ytitle_latex.SetTextAlign(23)
        ytitle_latex.SetX(0.0)
        ytitle_latex.SetY(my_bottommarg + 0.5*(1 - my_topmarg - my_bottommarg))
        ytitle_latex.SetTitle(z_title)

        # gc.SetTitleSize(_xsize*0.03)
        gc.SetTitleSize(_ysize * axistitle_size)
        gc.Draw()
        ytitle_latex.Draw()
        stack_unstack = []
        # This will plot the histograms stacked on top of each other
        if do_stack:
            stack_unstack.append("stack")
        # This will plot the histograms unstacked
        if do_nostack:
            stack_unstack.append("nostack")
        # This will just plot data and total mc
        stack_unstack.append("nobreakdown")
        leg_dict = {}
        for whichstack in stack_unstack:
            print("doing 2D for %s"%whichstack)
            for i in range(n_pads):
                pad = gc.cd(i+1)
                if proj_x_varname in scaleY:
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
                if whichstack == "stack":
                    stack_list[i].Draw("9 HIST same%s"%tmp_stack_drawopts)
                elif whichstack == "nobreakdown":
                    mc_band_list[i].Draw("9 E2 ][ same")
                    mc_hist_list[i].Draw("9 HIST ][ SAME")
                else: # if whichstack == "nostack":
                    tmp_stack = stack_list[i].Clone()
                    for tmp_hist in tmp_stack.GetHists():
                        tmp_hist.SetLineWidth(typeslinewidth+1)
                        tmp_hist.SetLineColor(tmp_hist.GetFillColor())
                        # # Make the bkgs dotted
                        if tmp_hist.GetFillStyle() not in [0,1001]:
                            tmp_hist.SetLineStyle(7)
                        tmp_hist.SetFillStyle(0)
                    # sys.exit(1)
                    mc_band_list[i].Draw("9 E2 ][ same")
                    tmp_stack.Draw("9 nostack noclear hist same")
                    mc_hist_list[i].Draw("9 HIST ][ SAME")
                if do_pinkstat:
                    ROOT.gStyle.SetEndErrorSize(0) # This makes the ticks at the end of the error bars longer
                    data_stat_list[i].Draw("9 SAME %s E0"%staterror_drawopt)
                    ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer
                else:
                    data_stat_list[i].Draw("9 SAME %s E0"%staterror_drawopt)
                data_hist_list[i].Draw("9 SAME E1 E0 X0")
                if len(compdata_hist_list) == len(data_hist_list):
                    compdata_hist_list[i].Draw("9 SAME E1 E0 X0")
                    compdata_stat_list[i].Draw("9 SAME E1 E0 X0")
                data_hist_list[i].Draw("9 SAME axis")

                tmp_range_string = binrange_list[i]
                binrange_latex = ROOT.TLatex()
                binrange_latex.SetTextAlign(33) # top right
                binrange_latex.SetNDC()
                binrange_latex.SetTextFont(42)
                binrange_latex.SetTextSize(0.028)
                binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),tmp_range_string)

                multip_string = "#times {:g}".format(float('{:.{p}g}'.format(multipliers[i], p=2)))
                multip_latex = ROOT.TLatex()
                multip_latex.SetTextAlign(32)
                multip_latex.SetNDC()
                multip_latex.SetTextFont(52)
                multip_latex.SetTextSize(0.03)
                multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.052),multip_string)

                
                pad.Modified()
                pad.Update()
            pad = gc.cd(n_pads+1)
            pad.Draw()

            padwidth = 1 - pad.GetLeftMargin() - pad.GetRightMargin()
            padheight = 1 - pad.GetTopMargin() - pad.GetBottomMargin()
            x1 = pad.GetLeftMargin() #+padwidth*.05
            y1 = (1.-(pad.GetTopMargin())-0.01)
            x2 =  1 - (pad.GetRightMargin()) + padwidth*0.1
            y2 =  (pad.GetBottomMargin()-0.02)
            if 11 in my_catstodo:
            # if whichstack in ["nostack", "stack"]:
                if proj_x_varname in scaleY:
                    x2 += padwidth * 0.50#0.6
                else: 
                    x2 += padwidth * 0.4
            leg = TLegend(x1+0.01, y1, x2-0.01, y2)
            # leg.SetTextSize(legendfontsize*0.6)
            leg.SetBorderSize(0)
            leg.SetFillColorAlpha(0,0.0)
            leg.SetFillStyle(0)
            leg.AddEntry(data_hist_list[0], catsnames["data"],"pe")
            if len(compdata_hist_list) == len(data_hist_list):
                leg.AddEntry(compdata_hist_list[0], catsnames["compdata"], "pe")
            if whichstack == "nobreakdown":
                leg.SetNColumns(1) #TODO is this right?
                leg.AddEntry(mc_band_list[i], catsnames[0],"fl")
            elif whichstack == "nostack":
                leg.AddEntry(mc_band_list[i], catsnames[0],"fl")
                # leg.SetNColumns(2)
                for key in my_catstodo:
                    mc_typesproj_listdict[key][0].SetLineWidth(typeslinewidth+2)
                    mc_typesproj_listdict[key][0].SetLineColor(mc_typesproj_listdict[key][0].GetFillColor())
                if 11 in my_catstodo:
                    leg.SetNColumns(2)
                    for key in my_catstodo:
                        if key > 10: continue
                        leg.AddEntry(mc_typesproj_listdict[key][0],catsnames[key],"l")
                        mc_typesproj_listdict[key+10][0].SetLineStyle(7)
                        leg.AddEntry(mc_typesproj_listdict[key+10][0],catsnames[key+10],"l")
                else:
                    for key in my_catstodo:
                        leg.AddEntry(mc_typesproj_listdict[key][0],catsnames[key],"l")
            else: # if "stack":
                for key in my_catstodo:
                    mc_typesproj_listdict[key][0].SetLineWidth(typeslinewidth+2)
                if 11 in my_catstodo:
                    leg.AddEntry(0,"","")
                    leg.SetNColumns(2)
                    for key in my_catstodo:
                        if key > 10: continue
                        leg.AddEntry(mc_typesproj_listdict[key][0],catsnames[key],"fl")
                        leg.AddEntry(mc_typesproj_listdict[key+10][0],catsnames[key+10],"fl")
                else:
                    for key in my_catstodo:
                        # if key not in mc_typesproj_listdict: continue
                        leg.AddEntry(mc_typesproj_listdict[key][0],catsnames[key],"fl")
            leg.Draw()
            leg_dict[whichstack] = leg.Clone()
            pad.Modified()
            pad = gc.cd(n_pads+2)
            latex_x = 1.0 - gc.GetRightMargin() - 0.01
            latex_y = (1.-(pad.GetTopMargin())) - 0.17*padheight
            prelim.SetTextSize(legendfontsize*0.57)
            datapottext.SetTextSize(legendfontsize*0.7)
            # prelim.DrawLatex(latex_x, latex_y, "MINER#it{^{}#nu}A Work In Progress")
            # datapottext.DrawLatex(latex_x, latex_y-0.05, "Data POT: 1.12 #times 10^{21}")
            datapottext.DrawLatex(latex_x, latex_y, datapot_string1)
            datapottext.DrawLatex(latex_x, latex_y-0.04, datapot_string2)
            prelim.DrawLatex(latex_x, latex_y-0.073, prelim_string)
            chi2text.SetTextSize(legendfontsize*0.6)
            if do_chi2onplot:
                chi2text.DrawLatex(latex_x, latex_y - 0.106, "%s, %s"%(chi2_string, ndf_string))
            if do_titleonplot:
                plottitle.Draw()
            gc.SetHistTexts()
            gc.Draw()
            sigma_canvas_name = "%s_Types_%s"%(thename, whichstack)
            gc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s %s"%(thetitle," Types2D", whichstack))
            for key in my_catstodo:
                if key not in mc_typesproj_listdict: continue
                mc_typesproj_listdict[key][0].SetLineWidth(typeslinewidth)
                mc_typesproj_listdict[key][0].SetLineColor(ROOT.TColor.GetColorDark((catscolors[key])))

       
            gc.cd()
            gc.ResetPads()
            gc.Modified()
            gc.Update()
            leg.Clear()

        ytitle_latex.SetTitle("Ratio to %s"%catsnames[0])
        ytitle_latex.SetX(0.04)
        # gc.SetYTitle("Ratio to %s"%catsnames[0])
        gc.SetXTitle(proj_xtitle)
        gc.SetLeftMargin(my_leftmarg)
        gc.Modified()
        gc.Update()
        leg = leg_dict["nostack"].Clone()

        ratio_maxlist = [GetPadMax(ratio_list[i],mcerror_list[i], True) for i in range(len(ratio_list))]
        ratio_global_max = max(ratio_maxlist)
        if ratio_global_max > 3.:
            for hist in ratio_list:
                hist.SetMaximum(int(ratio_global_max * 2 + 1)*0.5-0.0001)

        for i in range(n_pads):
            pad = gc.cd(i+1)
            pad.SetLogy(0)

            pad.Draw()
            ratio_list[i].Draw("9 E1 E0 axis")
            mcerror_list[i].Draw("9 E2 E0 same ][")
            straightline_list[i].Draw("9 hist same X0 ][")
            if 11 in mc_typesproj_listdict:
                print(typesratiostack_listdict.keys())
                for key in typestodo_leg:
                    if key > 10: continue
                    typesratiostack_listdict[key][i].Draw("9 HIST NOCLEAR SAME ][")
            else:
                for key in typesratio_listdict:
                    typesratio_listdict[key][i].Draw("9 HIST SAME ][")
            ratio_stat_list[i].Draw("9 same %s"%staterror_drawopt)
            ratio_list[i].Draw("9 same E1 E0 X0")
            if len(compratio_list) == len(ratio_list):
                compratio_stat_list[i].Draw("9 SAME E1 E0 X0")
                compratio_list[i].Draw("9 SAME E1 E0 X0")

            ratio_list[i].Draw("9 same axis")

            tmp_range_string = binrange_list[i]
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.028)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),tmp_range_string)
            pad.Modified()
            pad.Update()
        pad = gc.cd(n_pads+1)
        pad.Draw()

        leg.Draw()
        pad.Modified()
        gc.SetHistTexts()
        gc.Draw()
        ytitle_latex.Draw()
        plottitle.Modify()
        plottitle_string = plottitle_string.replace(canvas_title,canvas_title+" Ratio ")
        plottitle.SetTitle(plottitle_string)
        if do_titleonplot:
            plottitle.Draw()

        tmp_ratio_name = "%s_Typesratio"%(thename)
        gc.Print(os.path.join(outdirname,"source", tmp_ratio_name + ".C"))
        gc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s"%(thetitle," Types Ratio"))
        gc.cd()
        gc.ResetPads()
        gc.Modified()
        gc.Update()
        
        if not do_error_summary:
            del gc 
            continue
        # gc.SetYTitle("Fractional Uncertainty")
        ytitle_latex.SetTitle("Fractional Uncertainty")
        ytitle_latex.SetX(0.02)

        gc.SetXTitle(proj_xtitle)
        gc.SetLeftMargin(my_leftmarg)
        # gc.SetTitleSize(_xsize*0.03)
        gc.SetTitleSize(_ysize * axistitle_size)
        gc.Modified()
        gc.Update()

        mnvPlotter = MnvPlotter(8)
        SetupErrorSummary(mnvPlotter)
        include_stat_error = True
        solid_lines_only = False
        ignore_Threshold = 0.00001
        do_cov_area_norm = False
        error_group_name = ""
        do_fractional_uncertainty = True

        leg.Clear()
        padwidth = 1.0 - pad.GetLeftMargin() - pad.GetRightMargin()
        if x1 > 0.4:
            leg = TLegend(x1+0.01, y1, x2-0.01 + 0.4* padwidth, y2- pad.GetBottomMargin()*0.2)
        else:
            leg = TLegend(x1+0.01, y1, x2-0.01 + 0.7* padwidth, y2- pad.GetBottomMargin()*0.2)
            leg.SetNColumns(2)

        leg.SetBorderSize(0)
        leg.SetFillColorAlpha(0,0.0)

        # leg.SetFillColor(-1)
        # leg.SetNColumns(2)
        global_max = 0.0
        for i in range(n_pads):
            tmp_data_mnvh = data_mnvproj_list[i].Clone()
            total_error = tmp_data_mnvh.GetTotalError(include_stat_error, do_fractional_uncertainty, do_cov_area_norm).Clone()
            pad_max = total_error.GetBinContent(total_error.GetMaximumBin()) #.GetMaximum()
            if pad_max > global_max:
                global_max = pad_max
        if global_max > 1.0:
            global_max = 1.0
        # global_max = 0.5

        for i in range(n_pads):
            pad = gc.cd(i+1)
            tmp_data_mnvh = data_mnvproj_list[i].Clone()
            error_hists = mnvPlotter.GetSysErrorGroupHists(tmp_data_mnvh, do_fractional_uncertainty, do_cov_area_norm, ignore_Threshold)
            # error_hists = GetErrorHistsInGroup(tmp_data_mnvh, "GENIE Int. Model")[:6]
            # error_hists = GetErrorHistsInGroup(tmp_data_mnvh, "Tune")
            # error_hists = GetErrorHistsInGroup(tmp_data_mnvh, "FSI Model")
            # error_hists = GetErrorHistsInGroup(tmp_data_mnvh, "Flux")


            total_error = tmp_data_mnvh.GetTotalError(include_stat_error, do_fractional_uncertainty, do_cov_area_norm).Clone()
            total_error.SetMaximum(global_max * 1.3)
            mnvPlotter.ApplyNextLineStyle(total_error, True, True)
            total_error.SetLineWidth(typeslinewidth + 1)
            total_error.GetXaxis().SetNdivisions(505)
            total_error.GetYaxis().SetNdivisions(505)
            if proj_x_varname in scaleY:
                total_error.GetXaxis().SetNdivisions(504)

            # total_error.GetYaxis().SetLabelSize(total_error.GetXaxis().GetLabelSize())
            total_error.GetYaxis().SetLabelSize(axislabel_size)
            total_error.GetXaxis().SetLabelSize(axislabel_size)
            
            
            stat_error = tmp_data_mnvh.GetStatError(do_fractional_uncertainty)
            mnvPlotter.ApplyNextLineStyle(stat_error, False, True)
            stat_error.SetLineWidth(typeslinewidth + 1)
            stat_error.SetLineColor(12)
            stat_error.SetLineStyle(2)
            # stat_error.SetLineColor(12)
            if i == 0:
                tmp_total_err = total_error.Clone()
                tmp_total_err.SetLineWidth(total_error.GetLineWidth()+1)
                tmp_stat_error = stat_error.Clone()
                tmp_stat_error.SetLineWidth(stat_error.GetLineWidth()+1)
                leg.AddEntry(tmp_total_err, "Total Unc.", "l")
                # leg.AddEntry(0,"","")
                leg.AddEntry(tmp_stat_error, "Statistical", "l")

            total_error.Draw("9 axis")
            total_error.Draw("9 HIST same")
            stat_error.Draw("9 HIST same")


            # hist_index = 2
            for hist in error_hists:
                mnvPlotter.ApplyNextLineStyle(hist, False, True)
                hist.SetLineColor(mnvPlotter.error_color_map[hist.GetTitle()])
                hist.SetLineWidth(typeslinewidth + 1)
                hist.DrawCopy("9 HIST SAME")
                if i == 0:
                    # # tmp = hist.Clone()
                    # tmp.SetLineStyle(hist.GetLineStyle())
                    # tmp.SetLineColor(hist.GetLineColor())
                    hist.SetLineWidth(typeslinewidth+2)
                    leg.AddEntry(hist, hist.GetTitle(), "l")
            total_error.Draw("9 axis same")

            tmp_range_string = binrange_list[i]
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.028)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),tmp_range_string)

            pad.Update()
            pad.Modified()

        pad = gc.cd(n_pads+1)
        pad.Draw()
        leg.Draw()
        if do_titleonplot:
            plottitle_string = plottitle_string.replace(canvas_title + " Ratio ",canvas_title+" Error Summary")
            plottitle.SetTitle(plottitle_string)
            plottitle.Draw()
        
        # prelim.Modify()
        # prelim.DrawLatex(latex_x, latex_y, prelim_string)
        # datapottext.Modify()
        # datapottext.DrawLatex(latex_x, latex_y, "")
        

        gc.SetHistTexts()
        # gc.Draw()


        tmp_errror_summary_name = "%s_ErrorSummary"%(thename)
        # gc.Print(os.path.join(outdirname, thename + "_Types_ratio.png"))
        gc.Print(os.path.join(outdirname,"source", tmp_errror_summary_name + ".C"))
        gc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s"%(thetitle," Types Error Summary"))
        gc.cd()
        gc.ResetPads()
        gc.Modified()
        gc.Update()
    
        del gc

def DrawLegOnNewCanvas(i_hist_dict, canvas_title, canvas_name, outdirname, labeltype = "fl"):
    # To use with a 2D plot where the legend might be small, allows you to place anywhere you want at any size in a presentation
    leg_canvas = ROOT.TCanvas(canvas_name+"_legend", "Legend", 500,500)
    leg_canvas.SetTopMargin(0.)
    leg_canvas.SetBottomMargin(0.)
    leg_canvas.SetRightMargin(0.)
    leg_canvas.SetLeftMargin(0.)
    # leg = TLegend(0.2, 0.2, 0.8, 0.8)
    leg = TLegend(0., 0., 1., 1.)
    leg.SetBorderSize(0)
    leg.SetFillColor(-1)
    leg.SetFillStyle(0)
    # leg.SetTextSize(round(legendfontsize/3))
    if len(list(i_hist_dict.keys())) > 7:
        leg.SetNColumns(2)
    for name in i_hist_dict:
        tmp_labeltype = labeltype
        if name == "data":
            tmp_labeltype = "pe"
        leg.AddEntry(i_hist_dict[name], catsnames[name], tmp_labeltype)
    leg.Draw()
    leg_canvas.cd()
    leg_canvas.Modified()
    leg_canvas.Update()
    leg_canvas.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s"%(canvas_title," Legend"))
    leg_canvas.Modified()
    leg_canvas.Update()

def DrawEfficiency1D(i_seltrue_hist, i_alltrue_hist, x_varname, x_units, outdirname, canvas_name, canvas_title):
    seltrue_mnv = i_seltrue_hist.Clone()
    alltrue_mnv = i_alltrue_hist.Clone()
    
    efficiency = seltrue_mnv.Clone()
    efficiency.Divide(efficiency, alltrue_mnv, 1.0, 1.0, "B")
    efficiency.SetTitle("Efficiency in %s"%x_varname)
    efficiency.GetXaxis().SetTitle("%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(x_varname, x_units))
    efficiency.GetYaxis().SetTitle("Efficiency")
    
    efficiency.GetYaxis().CenterTitle()
    efficiency.GetYaxis().SetTitleOffset(0.6)
    efficiency.GetYaxis().SetTitleSize(0.05)
    efficiency.GetYaxis().SetLabelSize(0.05)
    efficiency.GetYaxis().SetNdivisions(505)

    efficiency.GetXaxis().CenterTitle()
    efficiency.GetXaxis().SetTitleOffset(0.9)
    efficiency.GetXaxis().SetTitleSize(0.05)
    efficiency.GetXaxis().SetLabelSize(0.05)
    efficiency.GetXaxis().SetNdivisions(505)

    efficiency.SetLineColor(ROOT.kRed)
    efficiency.SetLineWidth(3)

    thename = "%s_Efficiency1D"%(canvas_name) 
    thetitle = canvas_title + " Efficiency"
    cc = ROOT.TCanvas(thename, thetitle, _xsize, _ysize)
    cc.SetLeftMargin(pad_lmarg)
    cc.SetRightMargin(pad_rmarg)
    cc.SetBottomMargin(0.1)
    cc.SetTopMargin(0.1)
    cc.SetFrameLineWidth(1)
    cc.cd()
    cc.Draw()

    efficiency.Draw()

    cc.Modified()
    cc.Update()
    cc.Print(os.path.join(outdirname, "source", thename + ".C"))
    cc.Print(os.path.join(outdirname, canvas_name + ".pdf"),"Title:%s Efficiency"%(thetitle))

def DrawEfficiencyTypes1D(i_seltrue_hist, i_alltrue_hist, i_seltrue_typeshistdict, i_alltrue_typehistdict, x_varname, x_units, outdirname, canvas_name, canvas_title):
    seltrue_mnv = i_seltrue_hist.Clone()
    alltrue_mnv = i_alltrue_hist.Clone()
    
    efficiency = seltrue_mnv.Clone()
    efficiency.Divide(efficiency, alltrue_mnv, 1.0, 1.0, "B")
    efficiency.SetTitle("Efficiency in %s"%x_varname)
    efficiency.GetXaxis().SetTitle("%s (%s)"%(x_varname, x_units))
    efficiency.GetYaxis().SetTitle("Efficiency")
    
    efficiency.GetYaxis().CenterTitle()
    efficiency.GetYaxis().SetTitleOffset(0.6)
    efficiency.GetYaxis().SetTitleSize(0.05)
    efficiency.GetYaxis().SetLabelSize(0.05)
    efficiency.GetYaxis().SetNdivisions(505)

    efficiency.GetXaxis().CenterTitle()
    efficiency.GetXaxis().SetTitleOffset(0.9)
    efficiency.GetXaxis().SetTitleSize(0.05)
    efficiency.GetXaxis().SetLabelSize(0.05)
    efficiency.GetXaxis().SetNdivisions(505)

    efficiency.SetLineColor(ROOT.kRed)
    efficiency.SetLineWidth(3)

    thename = "%s_Efficiency1D"%(canvas_name) 
    thetitle = canvas_title + " Efficiency"
    cc = ROOT.TCanvas(thename, thetitle, _xsize, _ysize)
    cc.SetLeftMargin(pad_lmarg)
    cc.SetRightMargin(pad_rmarg)
    cc.SetBottomMargin(0.1)
    cc.SetTopMargin(0.1)
    cc.SetFrameLineWidth(1)
    cc.cd()
    cc.Draw()

    efficiency.Draw()

    cc.Modified()
    cc.Update()
    cc.Print(os.path.join(outdirname, "source", thename + ".C"))
    cc.Print(os.path.join(outdirname, canvas_name + ".pdf"),"Title:%s Efficiency"%(thetitle))


def DrawEfficiency2D(i_seltrue_hist, i_alltrue_hist, i_seltrue_typeshistdict, i_alltrue_typehistdict, x_varname, x_units, x_bins, y_varname, y_units, y_bins, outdirname, canvas_name, canvas_title):
    mnvplotter = MnvPlotter()
    seltrue_mnv = i_seltrue_hist.Clone()
    alltrue_mnv = i_alltrue_hist.Clone()
    
    tot_efficiency = seltrue_mnv.Clone()
    tot_efficiency.Divide(tot_efficiency, alltrue_mnv, 1.0, 1.0, "B")

    toteff_typesdict = {}
    typeseff_typesdict = {}
    for key in i_seltrue_typeshistdict:
        tmp_toteff = i_seltrue_typeshistdict[key].Clone()
        tmp_toteff.Divide(tmp_toteff, alltrue_mnv, 1.0, 1.0, "B")
        tmp_toteff.SetLineColor(catscolors[key])
        toteff_typesdict[key] = tmp_toteff
        tmp_typeseff = i_seltrue_typeshistdict[key].Clone()
        tmp_typesalltru = i_alltrue_typehistdict[key].Clone()
        tmp_typeseff.Divide(tmp_typeseff, tmp_typesalltru, 1.0, 1.0, "B")
        tmp_typeseff.SetLineColor(catscolors[key])
        typeseff_typesdict[key] = tmp_typeseff

    # First draw the 2D efficiency
    x_title = "%s (%s)"%(x_varname, x_units)
    y_title = "%s (%s)"%(y_varname, y_units)
    tot_efficiency.SetTitle("Efficiency in %s"%x_varname)
    tot_efficiency.GetXaxis().SetTitle(x_title)
    tot_efficiency.GetYaxis().SetTitle("%s (%s)"%(y_varname, y_units))
    tot_efficiency.GetZaxis().SetTitle("Efficiency")
    tot_efficiency.GetZaxis().CenterTitle()

    tot_efficiency.GetYaxis().CenterTitle()
    tot_efficiency.GetYaxis().SetTitleOffset(0.9)
    tot_efficiency.GetYaxis().SetTitleSize(0.05)
    # tot_efficiency.GetYaxis().SetLabelSize(0.05)
    tot_efficiency.GetYaxis().SetNdivisions(505)

    tot_efficiency.GetXaxis().CenterTitle()
    tot_efficiency.GetXaxis().SetTitleOffset(0.9)
    tot_efficiency.GetXaxis().SetTitleSize(0.05)
    # tot_efficiency.GetXaxis().SetLabelSize(0.05)
    tot_efficiency.GetXaxis().SetNdivisions(505)

    mnvplotter.SetROOT6Palette(ROOT.kBird)
    # efficiency.SetLineColor(ROOT.kRed)
    # efficiency.SetLineWidth(3)

    thename = "%s_Efficiency2D"%(canvas_name)#, x_varname, y_varname) 
    thetitle = canvas_title + " Efficiency"
    cc = ROOT.TCanvas(thename, thetitle, _xsize, _ysize)
    cc.SetLeftMargin(pad_lmarg)
    cc.SetRightMargin(0.13)
    cc.SetBottomMargin(0.1)
    cc.SetTopMargin(0.1)
    cc.SetFrameLineWidth(1)
    cc.cd()
    cc.Draw()
    ROOT.gStyle.SetPaintTextFormat("0.2f")
    tot_efficiency.SetMarkerSize(0.85)
    tot_efficiency.Draw("colz TEXT")
    prelim = AddPreliminary()
    prelim.DrawLatex(0.15, 0.93, prelim_string)

    cc.Modified()
    cc.Update()
    cc.Print(os.path.join(outdirname, "source", thename + ".C"))
    cc.Print(os.path.join(outdirname, canvas_name + ".pdf"),"Title:%s Efficiency"%(thetitle))

    # n_xbins = tot_efficiency.GetNbinsX()
    # n_ybins = tot_efficiency.GetNbinsY()
    n_xbins = len(x_bins) - 1 
    n_ybins = len(y_bins) -1
    # Now do the projected efficiencies
    for projaxis in ["x", "y"]:

        canvas_nxbins = n_xbins
        canvas_nybins = n_ybins
        # these are the bin edges for each panel, printed on each panel
        plot_bins = y_bins

        proj_xtitle = x_title
        proj_ytitle = y_title
        proj_x_varname = x_varname
        proj_y_varname = y_varname
        proj_x_units = x_units
        proj_y_units = y_units
        if projaxis == "y":
            canvas_nxbins = n_ybins
            canvas_nybins = n_xbins
            plot_bins = x_bins 
            proj_xtitle = y_title
            proj_ytitle = x_title
            proj_x_varname = y_varname
            proj_y_varname = x_varname
            proj_x_units = y_units
            proj_y_units = x_units

        tot_eff_projlist = MakeProjHistList(tot_efficiency, projaxis, canvas_nybins)
        for hist in tot_eff_projlist:
            hist.SetLineColor(catscolors[0])
            hist.SetFillColor(0)
            hist.SetMaximum(1.3)
            hist.SetMinimum(0.0001)
            hist.GetYaxis().SetNdivisions(305)
            hist.GetXaxis().SetNdivisions(505)
            hist.GetYaxis().SetLabelSize(hist.GetXaxis().GetLabelSize())

        toteff_types_projlistdict = {}
        typeseff_types_projlistdict = {}
        linestyle = 2
        for key in toteff_typesdict:
            tmp_types_projlist = MakeProjHistList(toteff_typesdict[key], projaxis, canvas_nybins)
            tmp_typestot_projlist = MakeProjHistList(typeseff_typesdict[key], projaxis, canvas_nybins)
            for i in range(len(tmp_types_projlist)):
                tmp_types_projlist[i].SetLineColor(toteff_typesdict[key].GetLineColor())
                tmp_types_projlist[i].SetFillColor(0)
                tmp_types_projlist[i].SetLineStyle(linestyle)
                tmp_typestot_projlist[i].SetLineColor(typeseff_typesdict[key].GetLineColor())
                tmp_typestot_projlist[i].SetFillColor(0)
                tmp_typestot_projlist[i].SetLineStyle(linestyle)
            linestyle+=1
                # tmp_typestot_projlist[i].SetLineStyle(typeseff_typesdict[key].GetLineColor())
            toteff_types_projlistdict[key] = tmp_types_projlist
            typeseff_types_projlistdict[key] = tmp_typestot_projlist

        binrange_list = []
        for i in range(len(plot_bins)-1):
            range_string = "{loedge} < {var} < {hiedge}".format(
                loedge = round(plot_bins[i], 3), 
                var = "%s #lower[-0.25]{#scale[0.6]{ (%s)}}"%(proj_y_varname, proj_y_units), 
                hiedge = round(plot_bins[i+1], 3)
            )
            binrange_list.append(range_string)

        gc = PanelCanvas("%s_proj%s"%(thename,projaxis), canvas_nxbins, canvas_nybins, round(_xsize), round(_ysize))
        my_topmarg = 0.05
        my_bottommarg = 0.1
        my_rightmarg = 0.03
        my_leftmarg = 0.08
        
        gc.SetTopMargin(my_topmarg)
        gc.SetBottomMargin(my_bottommarg)
        gc.SetRightMargin(my_rightmarg)
        gc.SetLeftMargin(my_leftmarg)
        gc.SetXTitle(proj_xtitle)
        gc.SetYTitle("Efficiency")
        gc.SetTitleSize(_xsize*0.03)
        gc.Draw()

        n_pads = len(tot_eff_projlist)
        for i in range(n_pads):
            pad = gc.cd(i+1)
            pad.Draw()

            tot_eff_projlist[i].Draw("HIST ][")
            # for key in toteff_types_projlistdict:
            #     print("Drawing ", key)
            #     # toteff_types_projlistdict[key][i].Draw("HIST same")
            #     typeseff_types_projlistdict[key][i].Draw("HIST same")
            
            tmp_range_string = binrange_list[i]
            range_string = "{loedge} < {var} < {hiedge}".format(
                    loedge = round(plot_bins[i], 3), var = "%s #lower[-0.25]{#scale[0.6]{ (%s)}}"%(proj_y_varname, proj_y_units), hiedge = round(plot_bins[i+1], 3)
            )
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.028)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)
            pad.Modified()
            pad.Update()
        pad = gc.cd(n_pads + 1)
        pad.Draw()
        padheight = 1 - pad.GetTopMargin() - pad.GetBottomMargin()

        latex_x = 1.0 - gc.GetRightMargin() - 0.01
        latex_y = (1.-(pad.GetTopMargin())) - 0.17*padheight
        prelim.SetTextSize(legendfontsize*0.57)
        prelim.SetTextAlign(31)
        prelim.DrawLatex(latex_x, latex_y-0.073, prelim_string)

        x1 = pad.GetLeftMargin() #+padwidth*.05
        y1 = (1.-(pad.GetTopMargin())-0.01)
        x2 =  1 - (pad.GetRightMargin())# + padwidth*.05)
        y2 =  (pad.GetBottomMargin()+0.01)
        leg = TLegend(x1, y1, x2, y2)
        leg.SetTextSize(round(legendfontsize/3))
        leg.SetBorderSize(0)
        leg.SetFillColor(-1)
        leg.SetFillStyle(0)
        leg.AddEntry(tot_eff_projlist[0], "Total Efficiency", "fl")
        for key in typeseff_types_projlistdict:
            leg.AddEntry(typeseff_types_projlistdict[key][0], catsnames[key], "fl")
        # leg.Draw()
        pad.Modified()
        pad.Update
        gc.cd()
        gc.SetHistTexts()
        gc.Draw()
        gc.Print(os.path.join(outdirname, "source", "%s_proj%s"%(thename,projaxis) + ".C"))
        gc.Print(os.path.join(outdirname, canvas_name + ".pdf"),"Title:%s Efficiency proj%s"%(thetitle,projaxis))

        gc.cd()
        gc.ResetPads()
        gc.Modified()
        gc.Update()

def GetErrorHistsInGroup(i_mnv_hist, group_name):
    include_stat_error = True
    solid_lines_only = False
    ignore_Threshold = 0.00001
    do_cov_area_norm = False
    error_group_name = ""
    do_fractional_uncertainty = True
    mnv_hist = i_mnv_hist.Clone()

    mnvplotter = MnvPlotter(8)
    SetupErrorSummary(mnvplotter)
    error_summary_group_dict = mnvplotter.error_summary_group_map
    group_list = error_summary_group_dict[group_name]
    out_list = []
    vertnames = list(mnv_hist.GetVertErrorBandNames())
    for name in vertnames:
        if name not in group_list:
            continue
        # print("found vert band %s"%name)
        band = mnv_hist.GetVertErrorBand(name)
        band_hist = band.GetErrorBand(do_fractional_uncertainty, do_cov_area_norm).Clone()
        if band_hist.GetBinContent(band_hist.GetMaximumBin()) < ignore_Threshold:
            continue
        band_hist.SetTitle(str(name))
        out_list.append(band_hist)
    
    latnames = list(mnv_hist.GetLatErrorBandNames())
    for name in latnames:
        if name not in group_list:
            continue
        if name in out_list:
            print("ERROR: found lat band that is also a vert band")
            sys.exit(1) 
        # print("found lat band %s"%name)
        band = mnv_hist.GetLatErrorBand(name)
        band_hist = band.GetErrorBand(do_fractional_uncertainty, do_cov_area_norm).Clone()
        if band_hist.GetBinContent(band_hist.GetMaximumBin()) < ignore_Threshold:
            continue
        band_hist.SetTitle(str(name))
        out_list.append(band_hist)
    uncorrnames = list(mnv_hist.GetUncorrErrorNames())
    for name in uncorrnames:
        if name not in group_list:
            continue
        if name in out_list:
            print("ERROR: found uncorr band that is also a vert band")
            sys.exit(1) 
        # print("found uncorr band %s"%name)
        band_hist = band.GetUncorrErrorAsHist(name, do_fractional_uncertainty).Clone()
        if band_hist.GetBinContent(band_hist.GetMaximumBin()) < ignore_Threshold:
            continue
        band_hist.SetTitle(str(name))
        out_list.append(band_hist)

    return out_list



def DrawErrorSumary2D():
    return 0

def AddPreliminary():
    font = 112
    color = ROOT.kRed +1
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(legendfontsize*0.7)
    latex.SetTextColor(color)
    latex.SetTextFont(font)
    # latex.SetTextAlign(11)
    return latex

def AddDataPOTInfo():
    font = 42
    # color = ROOT.kBlack
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(legendfontsize*0.85)
    # latex.SetTextColor(color)
    latex.SetTextFont(font)
    # latex.SetTextAlign(11)
    return latex

def AddChi2Info():
    font = 42
    # color = ROOT.kBlack
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(legendfontsize*0.85)
    # latex.SetTextColor(color)
    latex.SetTextFont(font)
    # latex.SetTextAlign(11)
    return latex

def MakeTitleOnPlot():
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.058)
    latex.SetTextFont(52)
    latex.SetTextAlign(21)
    return latex

def PrintSelectionBreakDown(i_mnv_data, i_mnv_mc, i_mc_typeshistdict):
    mnv_mc = i_mnv_mc.Clone()
    mnv_data = i_mnv_data.Clone()
    mc_typeshistdict = {}
    for key in i_mc_typeshistdict:
        mc_typeshistdict[key] = i_mc_typeshistdict[key].Clone()
    print("=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-Selection breakdown:=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-")
    tot_area = mnv_mc.Integral()#0,mnv_mc.GetNbinsX()+1)
    print("Total data area:\t%f"%mnv_data.Integral())
    print("Total MC area:\t%f"%tot_area)
    for key in mc_typeshistdict:
        type_area = mc_typeshistdict[key].Integral()#0,mnv_mc.GetNbinsX()+1)
        # if 11 in mc_typeshistdict:
        #     if key > 10:
        #         continue
        #     type_area+= mc_typeshistdict[key+10].Integral()#0,mnv_mc.GetNbinsX()+1)
        frac = type_area/tot_area
        print("\t %s:\t\t%.04f\t%f"%(key,frac,type_area))
    if "qelike" not in mc_typeshistdict and 11 in mc_typeshistdict: 
        print("Types totals: ")    
        for key in mc_typeshistdict:
            type_area = mc_typeshistdict[key].Integral()#0,mnv_mc.GetNbinsX()+1)
            if 11 in mc_typeshistdict:
                if key > 10:
                    continue
                type_area+= mc_typeshistdict[key+10].Integral()#0,mnv_mc.GetNbinsX()+1)
            frac = type_area/tot_area
            print("\t %s:\t\t%.04f\t%f"%(key,frac,type_area))
    print(">>>>>>>>>>>>>>>>>>>> NEntries info <<<<<<<<<<<<<<<<<<<<")
    tot_entries = mnv_mc.GetEntries()
    print("Total entries in data:\t%f"%mnv_data.GetEntries())
    print("Total entries in MC:\t%f"%tot_entries)
    for key in mc_typeshistdict:
        entries = mc_typeshistdict[key].GetEntries()
        frac = entries/tot_entries
        print("\t %s:\t\t%0.4f\t%f"%(key,frac,entries))
    if "qelike" not in mc_typeshistdict and 11 in mc_typeshistdict: 
        print("Types totals: ")    
        for key in mc_typeshistdict:
            entries = mc_typeshistdict[key].GetEntries()
            if 11 in mc_typeshistdict:
                if key > 10:
                    continue
            entries += mc_typeshistdict[key + 10].GetEntries()
            frac = entries/tot_entries
            print("\t %s:\t\t%0.4f\t%f"%(key,frac,entries))        
    print("=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-")

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
    "other",
    "multipion",
    "other_np",
    11,
    12,
    13,
    14,
    18,
]

catstodo = [
    "data",
    "qelike",
    "chargedpion",
    "neutralpion",
    "other",
    # "multipion",
    # "other_np",
    1,
    8,
    2,
    3,
    4,
    11,
    18,
    12,
    13,
    14,
]

typestodo = [
    "data",
    1,  #: "QE",
    8,  #: "2p2h",
    2,  #: "RES",
    3,  #: "DIS",
    4,  #: "COH",
]


typestodo_leg = [
    1,  #: "QE",
    11, #: "Bkg QE",
    8,  #: "2p2h",
    18, #: "Bkg 2p2h",
    2,  #: "RES",
    12, #: "Bkg RES",
    3,  #: "DIS",
    13, #: "Bkg DIS",
    4,  #: "COH",
    14, #: "Bkg COH",
]

catsnames = {
    "data": "Data", 
    "qelike":"QElike",
    "chargedpion":"1#pi^{#pm}",
    "neutralpion":"1#pi^{0}",
    "other":"Other",
    "multipion":"N#pi",
    "other_np":"Other",
    "compdata": "Data MnvTunev4.3.1",
    0: "MnvTune v2.0.1",  # total mc
    1: "QE",             # QE
    2: "RES",            # RES
    3: "DIS",            # DIS
    4: "COH",            # COH
    8: "2p2h",           # 2p2h
    11: "Bkg-QE",             # QE
    12: "Bkg-RES",            # RES
    13: "Bkg-DIS",            # DIS
    14: "Bkg-COH",            # COH
    18: "Bkg-2p2h",           # 2p2h
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
    8:              ROOT.TColor.GetColorBright(ROOT.kP8Azure),  # 2p2h
    11:              ROOT.kP8Blue,    # QE
    12:              ROOT.kP8Orange,  # RES
    13:              ROOT.kP8Pink,   # DIS
    14:              ROOT.kP8Green,    # COH
    18:              ROOT.TColor.GetColorBright(ROOT.kP8Azure),  # 2p2h
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
    8:              ROOT.TColor.GetColorBright(ROOT.kP8Azure),  # 2p2h
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


domodelcomp = global_domodelcomp
docompdata = False

if len(sys.argv) == 1 and not global_domodelcomp:
    print("python3 xsec_plots.py <path to analyze output files>")
    sys.exit(1)
if len(sys.argv) <= 2 and global_domodelcomp:
    print("python3 xsec_plots.py <path to analyze output file> <path to dir with model comps")
    print("WARNING: no path specified for models for comparison... just doing it without models")
    domodelcomp = False
if len(sys.argv) > 2:
    if ".root" in sys.argv[2]:
        print("Found a root file for the second file, assuming you want to compare the data, from that one")
        docompdata = True
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
if dothesisplot:
    outdirname = plotdir
else:
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
if "_" in tmpmodelname:
    tmpmodelname = modelname.replace('_',' ')
if tmpmodelname[7]!= " ":
    tmpmodelname = tmpmodelname[:7] + " " + tmpmodelname[7:]
tmpmodelname = tmpmodelname.replace(" multipion","")
catsnames[0] = str(tmpmodelname)
typesints[tmpmodelname] = 0
print(catsnames)

model_hists = {}
if domodelcomp and len(sys.argv) > 2:
    pathtodir_modelcomp = sys.argv[2]
    modelcomppath_dict = GetModelCompFilePathsDict(pathtodir_modelcomp)
    for model in modelcomppath_dict:
        # Trying this out, feels very pythonic....
        with TFile.Open(modelcomppath_dict[model],"READONLY") as tmpfile:
            print("looking at file ", modelcomppath_dict[model])
            model_hists[model] = GetModelHistDict(tmpfile, model)


POTScale = 1.0
# if ("potscaled_combined_" in filename):
#     POTScale = 1.0
# else:
h_pot = untuned_f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1)
print("data pot:", dataPOT)
# sys.exit(1)
# mcPOTprescaled = h_pot.GetBinContent(2)
print("POTScale: ", POTScale)


# Find all the valid histograms from the analyze_v9 files and group by keywords
# First get the histograms that were inputs to analyze_v9
print("Making dict of source hists...")
print("\tLooking at untuned...")
input_hists = {}
input_hists = GetInputHistDict(untuned_f,input_hists)
print("\tLooking at tuned...")
input_hists = GetInputHistDict(tuned_f, input_hists)

# Get the "type" histograms that are for the mcinttypes
print("Making dict of source types hists...")
input_typeshists = {}
input_typeshists = GetInputTypesHistDict(untuned_f,input_typeshists)
input_typeshists = GetInputTypesHistDict(tuned_f,input_typeshists)

# Next get the histograms that were output by analyze_v9 (ie for each stage)
print("Making dict of analyze hists...")
print("\tLooking at untuned...")
analyze_hists = {}
analyze_hists = GetAnalyzeHistDict(untuned_f, False, analyze_hists)
print("\tLooking at tuned...")
analyze_hists = GetAnalyzeHistDict(tuned_f, True, analyze_hists)
# And get their type histograms also (though really should only need them for the "truth" stage)
print("Making dict of analyze types hists...")
analyze_typeshists = {}
analyze_typeshists = GetAnalyzeTypesHistDict(untuned_f, False, analyze_typeshists)
analyze_typeshists = GetAnalyzeTypesHistDict(tuned_f, True, analyze_typeshists)

if docompdata:
    compraw_filename = sys.argv[2]
    if "_tuned_analyze9" in compraw_filename:
        comptuned_filename = compraw_filename
        compuntuned_filename = compraw_filename.replace("_tuned_","_untuned_")
    elif "_untuned_analyze9":
        compuntuned_filename = compraw_filename
        comptuned_filename = compraw_filename.replace("_untuned_","_tuned_")
    comptuned_f = TFile.Open(comptuned_filename,"READONLY")
    compuntuned_f = TFile.Open(compuntuned_filename,"READONLY")

    # compinput_hists = {}
    # compinput_hists = GetInputHistDict(compuntuned_f, compinput_hists)
    # # print("\tLooking at tuned...")
    # compinput_hists = GetInputHistDict(comptuned_f, compinput_hists)

    # # Get the "type" histograms that are for the mcinttypes
    # print("Making dict of source types hists...")
    # compinput_typeshists = GetInputTypesHistDict(compuntuned_f)
    # compinput_typeshists = GetInputTypesHistDict(comptuned_f,compinput_typeshists)

    # Next get the histograms that were output by analyze_v9 (ie for each stage)
    print("Making dict of analyze hists...")
    print("\tLooking at untuned...")
    companalyze_hists = {}
    companalyze_hists = GetAnalyzeHistDict(compuntuned_f, False, companalyze_hists)
    print("\tLooking at tuned...")
    companalyze_hists = GetAnalyzeHistDict(comptuned_f, True, companalyze_hists)
    # And get their type histograms also (though really should only need them for the "truth" stage)
    # print("Making dict of analyze types hists...")
    # companalyze_typeshists = GetAnalyzeTypesHistDict(compuntuned_f, False)
    # companalyze_typeshists = GetAnalyzeTypesHistDict(comptuned_f, True, companalyze_typeshists)


# Next get the variable configs set up. This is useful for building the histograms and making plot info
keys = tuned_f.GetListOfKeys()
if "varsFile" not in keys:
    bigvarconfig_string = tuned_f.Get("varsFile_5A").GetTitle()
else:
    bigvarconfig_string = tuned_f.Get("varsFile").GetTitle()
bigvarconfig_dict = json.loads(re.sub("//.*", "", bigvarconfig_string, flags = re.MULTILINE))

for b_sample in analyze_hists["h"]:
    for c_var in analyze_hists["h"][b_sample]:
        var_title = c_var
        var_units = "unit"
        if c_var in vars_info:
            var_title = vars_info[c_var]["title"]
            var_units = vars_info[c_var]["units"]
            if len(vars_info[c_var]["bins"]) == 0:
                print("making bins")
                varconfig = bigvarconfig_dict["1D"][c_var]
                tmp_bins1D = []
                if "bins" in varconfig.keys():
                    tmp_bins1D = [float(tmpbin) for tmpbin in varconfig["bins"]]
                    # vars_info[c_var]["bins"] = tmp_bins1D
                elif "nbins" in varconfig.keys():
                    mini = varconfig["min"]
                    maxi = varconfig["max"]
                    width = (maxi - mini)/varconfig["nbins"]
                    tmp_bins1D = [mini + tmpbin * width for tmpbin in range(0,varconfig["nbins"]+1)]
                    # print(bins1D)
                bins1D = []
                if c_var in rangeuser_dict:
                    # print("I am here")
                    for edge in tmp_bins1D:
                        # print("\t",edge)
                        # print("\t",rangeuser_dict[c_var][0])
                        # print("\t",rangeuser_dict[c_var][1])
                        if edge >= rangeuser_dict[c_var][0] and edge < rangeuser_dict[c_var][1]:
                            bins1D.append(edge)
                            continue
                        if edge == rangeuser_dict[c_var][1]:
                            bins1D.append(edge)
                            break
                        if edge > rangeuser_dict[c_var][1]:
                            bins1D.append(rangeuser_dict[c_var][1])
                            break
                else:
                    bins1D = tmp_bins1D
                vars_info[c_var]["bins"] = bins1D
                print(bins1D)
    for c_var in analyze_hists["h2D"][b_sample]:
        for tmpvar in c_var.split("_"):
            if tmpvar in vars_info:
                if len(vars_info[tmpvar]["bins"])==0:
                    print("making bins")
                    varconfig = bigvarconfig_dict["1D"][tmpvar]
                    tmp_bins1D = []
                    if "bins" in varconfig.keys():
                        tmp_bins1D = [float(tmpbin) for tmpbin in varconfig["bins"]]
                        # vars_info[c_var]["bins"] = tmp_bins1D
                    elif "nbins" in varconfig.keys():
                        mini = varconfig["min"]
                        maxi = varconfig["max"]
                        width = (maxi - mini)/varconfig["nbins"]
                        tmp_bins1D = [mini + tmpbin * width for tmpbin in range(0,varconfig["nbins"]+1)]
                        # print(bins1D)
                    bins1D = []
                    if tmpvar in rangeuser_dict:
                        # print("I am here")
                        for edge in tmp_bins1D:
                            # print("\t",edge)
                            # print("\t",rangeuser_dict[c_var][0])
                            # print("\t",rangeuser_dict[c_var][1])
                            if edge >= rangeuser_dict[tmpvar][0] and edge < rangeuser_dict[tmpvar][1]:
                                bins1D.append(edge)
                                continue
                            if edge == rangeuser_dict[tmpvar][1]:
                                bins1D.append(edge)
                                break
                            if edge > rangeuser_dict[tmpvar][1]:
                                bins1D.append(rangeuser_dict[tmpvar][1])
                                break
                    else:
                        bins1D = tmp_bins1D
                    vars_info[tmpvar]["bins"] = bins1D
                    print(bins1D)

# # Done with the analyze_v9 files, lets get the files for the model comparison. This has it's own method
# pathtodir_modelcomp = sys.argv[2]
# modelcomppath_dict = GetModelCompFilePathsDict(pathtodir_modelcomp)
# # Dict to put all the model hists in. Structure is {model:{histdim:{sample:{variable:{fluxnorm:TH1D()}}}
# model_hists = {}
# for model in modelcomppath_dict:
#     # Trying this out, feels very pythonic....
#     with TFile.Open(modelcomppath_dict[model],"READONLY") as tmpfile:
#         model_hists[model] = GetModelHistDict(tmpfile)

ROOT.gStyle.SetOptStat(0)
for a_hist in input_hists:
    if "reconstructed" in skipstage_list: break
    # catsnames["data"] = "Data (stat. err.)"
    for b_sample in input_hists[a_hist]:
        for c_var in input_hists[a_hist][b_sample]:
            if "pzmu" in c_var: continue
            reco_data = input_hists[a_hist][b_sample][c_var]["data"]["reconstructed"]

            reco_sig_untuned = input_hists[a_hist][b_sample][c_var]["qelike"]["reconstructed"].Clone()
            reco_sig_tuned = input_hists[a_hist][b_sample][c_var]["qelike"]["reconstructed_tuned"].Clone()
            reco_mctot_untuned = reco_sig_untuned.Clone(reco_sig_untuned.GetName().replace("qelike","mctot"))
            reco_mctot_tuned = reco_sig_tuned.Clone(reco_sig_tuned.GetName().replace("qelike","mctot"))

            reco_sig_untuned_typesdict = {}
            reco_sig_tuned_typesdict = {}
            for itype in input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed"]:
                reco_sig_untuned_typesdict[itype] = input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed"][itype].Clone()
                reco_sig_tuned_typesdict[itype] = input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed_tuned"][itype].Clone()
            reco_untuned_typesdict = reco_sig_untuned_typesdict
            reco_tuned_typesdict = reco_sig_tuned_typesdict
            # Now build the other dicts
            reco_untuned_dict = {"qelike": reco_sig_untuned}
            reco_tuned_dict = {"qelike": reco_sig_tuned}
            for bkg in bkgcats:
                if bkg in input_hists[a_hist][b_sample][c_var]: 
                    reco_untuned_dict[bkg] = input_hists[a_hist][b_sample][c_var][bkg]["reconstructed"]
                    reco_mctot_untuned.Add(input_hists[a_hist][b_sample][c_var][bkg]["reconstructed"])
                    reco_tuned_dict[bkg] = input_hists[a_hist][b_sample][c_var][bkg]["reconstructed_tuned"]
                    reco_mctot_tuned.Add(input_hists[a_hist][b_sample][c_var][bkg]["reconstructed_tuned"])
                if bkg in input_typeshists[a_hist][b_sample][c_var]:
                    
                    tmp_untuned_histdict = input_typeshists[a_hist][b_sample][c_var][bkg]["reconstructed"]
                    tmp_tuned_histdict = input_typeshists[a_hist][b_sample][c_var][bkg]["reconstructed_tuned"]
                    # for itype in tmp_untuned_histdict:
                    # print(input_typeshists[a_hist][b_sample][c_var][bkg]["reconstructed_tuned"].keys())
                    for itype in input_typeshists[a_hist][b_sample][c_var][bkg]["reconstructed_tuned"]:
                        bkgtype = itype
                        
                        if itype <= 10:
                            bkgtype += 10
                        if bkgtype not in reco_untuned_typesdict:
                            reco_untuned_typesdict[bkgtype] = tmp_untuned_histdict[itype].Clone(tmp_untuned_histdict[itype].GetName().replace(bkg,"qelikenot"))
                            reco_tuned_typesdict[bkgtype] = tmp_tuned_histdict[itype].Clone(tmp_tuned_histdict[itype].GetName().replace(bkg,"qelikenot"))
                            continue
                        reco_untuned_typesdict[bkgtype].Add(tmp_untuned_histdict[itype])
                        reco_tuned_typesdict[bkgtype].Add(tmp_tuned_histdict[itype])

            # Now make the titles for the plot
            var_units = "unit"
            xvar_name = ""
            xvar_units = "xunits"
            yvar_name = ""
            yvar_units = "yunits"
            tmp_xvar_bins = []
            tmp_yvar_bins = []
            if len(c_var.split("_")) == 2:
                for var in c_var.split("_"):
                    if var not in vars_info:
                        vars_info[var] = {"title": var, "units": unit, "bins":[]}
                        print("ERROR: variable not in varsinfo: %s"%(var))
                        continue
                xvar_name = vars_info[c_var.split("_")[0]]["title"]
                xvar_units = vars_info[c_var.split("_")[0]]["units"]
                yvar_name = vars_info[c_var.split("_")[1]]["title"]
                yvar_units = vars_info[c_var.split("_")[1]]["units"]
                tmp_xvar_bins = vars_info[c_var.split("_")[0]]["bins"]
                tmp_yvar_bins = vars_info[c_var.split("_")[1]]["bins"]
            else:
                if c_var not in vars_info:
                    vars_info[c_var] = {"title": var, "units": unit, "bins":[]}
                xvar_name = vars_info[c_var]["title"]
                xvar_units = vars_info[c_var]["units"]
                tmp_xvar_bins = vars_info[c_var]["bins"]
            tmp_xvar_title = "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(xvar_name,xvar_units)
            tmp_yvar_title = "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(yvar_name, yvar_units)
            tmp_counts_ztitle = "Counts / (%s) / (%s)"%(xvar_units, yvar_units)
            tmp_counts_ytitle_1d = "Counts / (%s) "%(xvar_units)
            
            # Now setup the master canvas
            tmp_canvas_basename = "%s_%s_%s"%(modelname, b_sample, c_var)
            dimtag = ""
            if a_hist=="h":
                dimtag = "1D"
            if a_hist=="h2D":
                dimtag = "2D"
            pdf_canvas_name = tmp_canvas_basename+"_recoplots_"+ dimtag
            var_outdir = os.path.join(outdirname,c_var)
            if not os.path.exists(var_outdir):
                print( var_outdir)
                os.mkdir(var_outdir)
                os.mkdir(os.path.join(var_outdir,"source"))
            dummy_canvas = ROOT.TCanvas(pdf_canvas_name,pdf_canvas_name,_xsize,_ysize)
            dummy_canvas.Draw()
            dummy_canvas.Print(os.path.join(var_outdir,pdf_canvas_name+".pdf")+"[","pdf")
            dummy_canvas.Print(os.path.join(var_outdir,pdf_canvas_name+".pdf"),"pdf")

            tmp_canvas_basetitle = "%s %s %s"%(modelname, b_sample, c_var)

            if a_hist == "h":
                # print("here")
                DrawDataMCPlot1D_new(
                    reco_data, 
                    reco_mctot_untuned, reco_untuned_dict, 
                    tmp_xvar_title, 
                    tmp_counts_ytitle_1d, 
                    var_outdir, 
                    pdf_canvas_name,
                    "Event Selection Untuned",
                    # "Final States Untuned",
                    "FinalStates_Untuned", 
                    do_stack = True, do_nostack = True
                )
                DrawDataMCPlot1D_new(
                    reco_data, 
                    reco_mctot_untuned, reco_untuned_typesdict, 
                    tmp_xvar_title, 
                    tmp_counts_ytitle_1d, 
                    var_outdir, 
                    pdf_canvas_name,
                    "Event Selection Untuned",
                    # "Types Untuned",
                    "Types_Untuned", 
                    do_stack = True, do_nostack = True
                )
                tmp_mctot_name = catsnames[0] + " (w/ tune)"
                catsnames[0] = tmp_mctot_name
                DrawDataMCPlot1D_new(
                    reco_data, 
                    reco_mctot_tuned, reco_tuned_dict, 
                    tmp_xvar_title, 
                    tmp_counts_ytitle_1d, 
                    var_outdir, 
                    pdf_canvas_name,
                    "Event Selection Tuned",
                    # "Final States Tuned",
                    "FinalStates_Tuned", 
                    do_stack = True, do_nostack = True
                )
                DrawDataMCPlot1D_new(
                    reco_data, 
                    reco_mctot_tuned, reco_tuned_typesdict, 
                    tmp_xvar_title, 
                    tmp_counts_ytitle_1d, 
                    var_outdir, 
                    pdf_canvas_name,
                    "Event Selection Tuned",
                    # "Types Tuned",
                    "Types_Tuned", 
                    do_stack = True, do_nostack = True
                )
                catsnames[0] = catsnames[0].replace(" (w/ tune)","")
            else:
                reco_data.Print()
                DrawDataMCPlot2D_new(
                    reco_data, 
                    reco_mctot_untuned, reco_untuned_dict, 
                    xvar_name, xvar_units, tmp_xvar_bins, 
                    yvar_name, yvar_units, tmp_yvar_bins,
                    tmp_counts_ztitle, 
                    var_outdir, 
                    pdf_canvas_name, 
                    "Event Selection Untuned",
                    # "Final States Untuned",
                    "_FinalStates_Untuned",
                    i_multipliers = [],
                    do_stack = True, do_nostack = True, do_error_summary = False,
                    i_comp_data_hist = False,
                )
                DrawDataMCPlot2D_new(
                    reco_data, 
                    reco_mctot_untuned, reco_untuned_typesdict, 
                    xvar_name, xvar_units, tmp_xvar_bins, 
                    yvar_name, yvar_units, tmp_yvar_bins,
                    tmp_counts_ztitle, 
                    var_outdir, 
                    pdf_canvas_name, 
                    "Event Selection",
                    # "Types Untuned",
                    "Types_Untuned", 
                    i_multipliers = [],
                    do_stack = True, do_nostack = True, do_error_summary = False,
                    i_comp_data_hist = False,
                )
                tmp_mctot_name = catsnames[0] + " (w/ tune)"
                catsnames[0] = tmp_mctot_name
                DrawDataMCPlot2D_new(
                    reco_data, 
                    reco_mctot_tuned, reco_tuned_dict, 
                    xvar_name, xvar_units, tmp_xvar_bins, 
                    yvar_name, yvar_units, tmp_yvar_bins,
                    tmp_counts_ztitle, 
                    var_outdir, 
                    pdf_canvas_name, 
                    "Event Selection Tuned",
                    # "Final States Tuned",
                    "FinalStates_Untuned", 
                    i_multipliers = [],
                    do_stack = True, do_nostack = True, do_error_summary = False,
                    i_comp_data_hist = False,
                )
                DrawDataMCPlot2D_new(
                    reco_data, 
                    reco_mctot_tuned, reco_tuned_typesdict, 
                    xvar_name, xvar_units, tmp_xvar_bins, 
                    yvar_name, yvar_units, tmp_yvar_bins,
                    tmp_counts_ztitle, 
                    var_outdir, 
                    pdf_canvas_name, 
                    "Event Selection Tuned",
                    # "Types Tuned",
                    "Types_Tuned", 
                    i_multipliers = [],
                    do_stack = True, do_nostack = True, do_error_summary = False,
                    i_comp_data_hist = False,
                )
                catsnames[0] = catsnames[0].replace(" (w/ tune)","")

            dummy_canvas.Print(os.path.join(var_outdir,pdf_canvas_name+".pdf")+"]","pdf")
print("done with the reconstructed hists")
catsnames["data"] = "Data (stat. + syst.)"

for a_hist in analyze_hists.keys():
    print(a_hist)
    for b_sample in analyze_hists[a_hist].keys():
        for c_var in analyze_hists[a_hist][b_sample].keys():
            if "pzmu" in c_var: continue

            if c_var in skipvar_list:
                continue
            if "pzmu" in c_var: continue
            mnvPlotter = MnvPlotter()
            print(c_var)

            # These are total signal mc hists 
            tmp_mcrecosig_untuned = input_hists[a_hist][b_sample][c_var]["qelike"]["reconstructed"].Clone()
            tmp_mcseltru_untuned = input_hists[a_hist][b_sample][c_var]["qelike"]["selected_truth"].Clone()
            tmp_mcalltru_untuned = input_hists[a_hist][b_sample][c_var]["qelike"]["all_truth"].Clone()

            tmp_mcrecosig_tuned = input_hists[a_hist][b_sample][c_var]["qelike"]["reconstructed_tuned"].Clone()
            tmp_mcseltru_tuned = input_hists[a_hist][b_sample][c_var]["qelike"]["selected_truth_tuned"].Clone()
            tmp_mcalltru_tuned = input_hists[a_hist][b_sample][c_var]["qelike"]["all_truth_tuned"].Clone()

            # These are data hists from analyze
            tmp_bkgsub = analyze_hists[a_hist][b_sample][c_var]["bkgsub"].Clone()
            tmp_bkgsub_tuned = analyze_hists[a_hist][b_sample][c_var]["bkgsub_tuned"].Clone()

            tmp_unfolded = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded"].Clone()
            tmp_unfolded_tuned = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_tuned"].Clone()
            # Make a list for the unfolded by iteration
            tmp_unfoldediter_list = []
            tmp_unfoldediter_tuned_list = []
            for key in analyze_hists[a_hist][b_sample][c_var].keys():
                # print(">>>>>>>unfolded iter check on ", key)
                if "unfolded" not in key: continue
                if "iter" not in key: continue
                if "tuned" in key: 
                    tmp_unfoldediter_tuned_list.append(analyze_hists[a_hist][b_sample][c_var][key].Clone())
                else:
                    tmp_unfoldediter_list.append(analyze_hists[a_hist][b_sample][c_var][key].Clone())
            # want to add the last iter
            tmp_unfoldediter_list.append(tmp_unfolded)
            tmp_unfoldediter_tuned_list.append(tmp_unfolded_tuned)

            # Efficiency related things
            tmp_efficiency = analyze_hists[a_hist][b_sample][c_var]["efficiency"].Clone()
            tmp_efficiency_tuned = analyze_hists[a_hist][b_sample][c_var]["efficiency_tuned"].Clone()

            tmp_effcorr = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_effcorr"].Clone()
            tmp_effcorr_tuned = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_effcorr_tuned"].Clone()

            # Cross sections  
            tmp_sigma = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_effcorr_sigma"].Clone()
            tmp_sigma_tuned = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_effcorr_sigma_tuned"].Clone()
            tmp_sigmamc = analyze_hists[a_hist][b_sample][c_var]["sigmaMC"].Clone()
            tmp_sigmamc_tuned = analyze_hists[a_hist][b_sample][c_var]["sigmaMC_tuned"].Clone()

            found_typessigma = False
            found_typessigmatuned = False
            tmp_typessigma = {}
            tmp_typessigma_tuned = {}
            if a_hist in analyze_typeshists:
                if b_sample in analyze_typeshists[a_hist]:
                    if c_var in analyze_typeshists[a_hist][b_sample]:
                        if "sigmaMC" in analyze_typeshists[a_hist][b_sample][c_var]:
                            print("found types sigmamc")
                            for itype in analyze_typeshists[a_hist][b_sample][c_var]["sigmaMC"]:
                                tmp_typessigma[itype] = analyze_typeshists[a_hist][b_sample][c_var]["sigmaMC"][itype].Clone()
                            found_typessigma = True
                        if "sigmaMC_tuned" in analyze_typeshists[a_hist][b_sample][c_var]:
                            print("found tuned types sigmamc")
                            for itype in analyze_typeshists[a_hist][b_sample][c_var]["sigmaMC_tuned"]:
                                tmp_typessigma_tuned[itype] = analyze_typeshists[a_hist][b_sample][c_var]["sigmaMC_tuned"][itype].Clone()
                            found_typessigmatuned = True

            found_inputtypes = []
            found_inputtypestuned = []
            if a_hist in input_typeshists:
                if b_sample in input_typeshists[a_hist].keys():
                    if c_var in input_typeshists[a_hist][b_sample].keys():
                        print("keys for input typehists: ", input_typeshists[a_hist][b_sample][c_var].keys())
                        for d_types in input_typeshists[a_hist][b_sample][c_var]["qelike"]:
                            print("looking for types for ", d_types)
                            if "tuned" in d_types:
                                if len(list(input_typeshists[a_hist][b_sample][c_var]["qelike"][d_types].keys())) != 0:
                                    # print("found types for ", d_types)
                                    found_inputtypestuned.append(d_types)
                            else:
                                if len(list(input_typeshists[a_hist][b_sample][c_var]["qelike"][d_types].keys())) != 0:
                                    print("found types for ", d_types)
                                    found_inputtypestuned.append(d_types)
            tmp_types_mcreco = []
            tmp_types_mcseltru = []
            tmp_types_mcalltru = []

            tmp_types_mcreco = {}
            tmp_types_mcseltru = {}
            tmp_types_mcalltru = {}
            tmp_types_mcreco_tuned = {}
            tmp_types_mcseltru_tuned = {}
            tmp_types_mcalltru_tuned = {}
            if "reconstructed" in found_inputtypes:
                # tmp_types_mcreco= input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed"]
                for itype in input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed"]:
                    tmp_types_mcreco[itype] = input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed"][itype].Clone()
            if "selected_truth" in found_inputtypes:
                # tmp_types_mcseltru = input_typeshists[a_hist][b_sample][c_var]["qelike"]["selected_truth"]
                for itype in input_typeshists[a_hist][b_sample][c_var]["qelike"]["selected_truth"]:
                    tmp_types_mcseltru[itype] = input_typeshists[a_hist][b_sample][c_var]["qelike"]["selected_truth"][itype].Clone()
            if "all_truth" in found_inputtypes:
                # tmp_types_mcalltru = input_typeshists[a_hist][b_sample][c_var]["qelike"]["all_truth"]
                for itype in input_typeshists[a_hist][b_sample][c_var]["qelike"]["all_truth"]:
                    tmp_types_mcalltru[itype] = input_typeshists[a_hist][b_sample][c_var]["qelike"]["all_truth"][itype].Clone()
            if "reconstructed_tuned" in found_inputtypestuned:
                # tmp_types_mcreco_tuned = input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed_tuned"]
                for itype in input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed_tuned"]:
                    tmp_types_mcreco_tuned[itype] = input_typeshists[a_hist][b_sample][c_var]["qelike"]["reconstructed_tuned"][itype].Clone()
            if "selected_truth_tuned" in found_inputtypestuned:
                # tmp_types_mcseltru_tuned = input_typeshists[a_hist][b_sample][c_var]["qelike"]["selected_truth_tuned"]
                for itype in input_typeshists[a_hist][b_sample][c_var]["qelike"]["selected_truth_tuned"]:
                    tmp_types_mcseltru_tuned[itype] = input_typeshists[a_hist][b_sample][c_var]["qelike"]["selected_truth_tuned"][itype].Clone()
            if "all_truth_tuned" in found_inputtypestuned:
                # tmp_types_mcalltru_tuned = input_typeshists[a_hist][b_sample][c_var]["qelike"]["all_truth_tuned"]
                for itype in input_typeshists[a_hist][b_sample][c_var]["qelike"]["all_truth_tuned"]:
                    tmp_types_mcseltru_tuned[itype] = input_typeshists[a_hist][b_sample][c_var]["qelike"]["all_truth_tuned"][itype].Clone()
            if domodelcomp:
                print(model_hists.keys())
                tmp_model_hists = {}
                for model in modelcomptodo["NUISANCE"]:
                    if a_hist in model_hists[model]:
                        if b_sample in model_hists[model][a_hist]:
                            if c_var in model_hists[model][a_hist][b_sample]:
                                tmp_model_hists[model] = model_hists[model][a_hist][b_sample][c_var]["reweight"].Clone()
            tmp_canvas_basename = "%s_%s_%s"%(modelname, b_sample, c_var)
            # if do_comparison:
            #     tmp_canvas_basename+="_ModelComp"
            if docompdata: 
                tmp_canvas_basename+="_DataComp"
            # tmp_canvas_basetitle = "%s %s %s"%(modelname, b_sample, c_var)
            var_outdir = os.path.join(outdirname,c_var)
            if not os.path.exists(var_outdir):
                print( var_outdir)
                os.mkdir(var_outdir)
                os.mkdir(os.path.join(var_outdir,"source"))
            dimtag = ""
            if a_hist=="h":
                dimtag = "1D"
            if a_hist=="h2D":
                dimtag = "2D"
            pdf_canvas_name = tmp_canvas_basename+"_xsecplots_"+ dimtag
            dummy_canvas = ROOT.TCanvas(pdf_canvas_name,pdf_canvas_name,_xsize,_ysize)
            dummy_canvas.Draw()
            dummy_canvas.Print(os.path.join(var_outdir,pdf_canvas_name+".pdf")+"[","pdf")
            # For some reason the first canvas is always slightly smaller, so do that here instead of in the plotting
            dummy_canvas.Print(os.path.join(var_outdir,pdf_canvas_name+".pdf"),"pdf")

            if a_hist=="h":
                var_title = c_var
                var_units = "unit"
                var_title = vars_info[c_var]["title"]
                var_units = vars_info[c_var]["units"]
                counts_ytitle = "Counts / (%s)"%(var_units)
                # bkg subtracted 
                if "bkgsub" not in skipstage_list:
                    bkgsub_canvas_title = " Background Subtracted"
                    if "reconstructed_tuned" in found_inputtypestuned:
                        print(counts_ytitle)
                        DrawDataMCPlot1D_new(
                            tmp_bkgsub_tuned, 
                            tmp_mcrecosig_tuned, 
                            tmp_types_mcreco_tuned, 
                            "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(var_title,var_units), 
                            counts_ytitle, 
                            var_outdir, 
                            pdf_canvas_name, 
                            bkgsub_canvas_title,
                            "_bkgsub", 
                            True, 
                            True,
                        )
                # unfolded hists
                if "unfolded" not in skipstage_list:
                    unfolded_canvas_title = "Unfolded"
                    if "selected_truth_tuned" in found_inputtypestuned:
                        DrawDataMCPlot1D_new(
                            tmp_unfolded_tuned, 
                            tmp_mcseltru_tuned, 
                            tmp_types_mcseltru_tuned, 
                            "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(var_title,var_units), 
                            counts_ytitle, 
                            var_outdir, 
                            pdf_canvas_name, 
                            unfolded_canvas_title,
                            "_unfolded", 
                            True, 
                            True
                        )
                    if "unfolditers" not in skipstage_list:
                        for i in range(len(tmp_unfoldediter_tuned_list)):
                            tmp_canvas_title = "%s iter %d"%(unfolded_canvas_title, i+1)
                            if "selected_truth_tuned" in found_inputtypestuned:
                                DrawDataMCPlot1D_new(
                                    tmp_unfoldediter_tuned_list[i], 
                                    tmp_mcseltru_tuned, 
                                    tmp_types_mcseltru_tuned, 
                                    "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(var_title,var_units), 
                                    counts_ytitle, 
                                    var_outdir, 
                                    pdf_canvas_name, 
                                    tmp_canvas_title,
                                    "_unfolded_iter%02d"%(i+1), 
                                    True, 
                                    True
                                )
                # effcorr hists
                if "effcorr" not in skipstage_list:
                    # effcorr_canvas_title = tmp_canvas_basename + " Efficiency Corrected"
                    effcorr_canvas_title = " Efficiency Corrected"
                    if "all_truth_tuned" in found_inputtypestuned:
                        DrawDataMCPlot1D_new(
                            tmp_effcorr_tuned, 
                            tmp_mcalltru_tuned, 
                            tmp_types_mcalltru_tuned, 
                            "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(var_title,var_units), 
                            counts_ytitle, 
                            var_outdir, 
                            pdf_canvas_name, 
                            effcorr_canvas_title,
                            "_effcorr", 
                            True, 
                            True
                        )                    
                    if "all_truth_tuned" in found_inputtypestuned and "selected_truth_tuned" in found_inputtypestuned:
                        eff_canvas_title = " Efficiencys"
                        DrawEfficiency1D(
                            tmp_mcseltru_tuned, 
                            tmp_mcalltru_tuned_tuned, 
                            var_title, 
                            var_units,
                            var_outdir, 
                            pdf_canvas_name, 
                            eff_canvas_title
                        )
                if "sigma" not in skipstage_list:
                    # sigma_canvas_title = tmp_canvas_basetitle + " sigma"
                    sigma_canvas_title = "Cross Section"
                    sigma_ytitle = "d#sigma/d%s #lower[0.25]{#scale[0.6(cm^{2}/%s/Nucleon)}}"%(var_title,var_units)
                    if found_typessigma:
                        DrawDataMCPlot1D_new(
                            tmp_sigma_tuned, 
                            tmp_sigmamc, 
                            tmp_typessigma,
                            "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(var_title,var_units), 
                            sigma_ytitle, 
                            var_outdir, 
                            pdf_canvas_name, 
                            sigma_canvas_title,
                            "_sigma", 
                            True, 
                            True
                        )        

            if a_hist == "h2D":
                print(">>>>>> doing 2D")
                # print(found_inputtypes)
                # print(found_inputtypestuned)
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
                    # print(yvar, yvar_bins)
                    
                xvar_title = "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(xvar_name,xvar_units)
                yvar_title = "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(yvar_name, yvar_units)
                counts_ztitle = "Counts / (%s) / (%s)"%(xvar_units, yvar_units)
                tmp_nametag = ""
                tmp_do_stack = True
                tmp_do_nostack = True
                if "bkgsub" not in skipstage_list:
                    multipliers = []
                    bkgsub_canvas_name = pdf_canvas_name
                    bkgsub_canvas_title = "Background Subtracted"
                    if "reconstructed_tuned" in found_inputtypestuned:
                        print(vars_info[xvar])
                        print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Doing bkg sub'd")
                        DrawDataMCPlot2D_new(
                            tmp_bkgsub_tuned, 
                            tmp_mcrecosig_tuned, 
                            tmp_types_mcreco_tuned, 
                            xvar_name, xvar_units, xvar_bins, 
                            yvar_name, yvar_units, yvar_bins, 
                            counts_ztitle, 
                            var_outdir, 
                            pdf_canvas_name, 
                            bkgsub_canvas_title, 
                            "_bkgsub", 
                            multipliers, 
                            tmp_do_stack, 
                            tmp_do_nostack 
                        )
                    if docompdata:
                        datacompbkgsub_canvas_title = "Background Subtracted Data Comparison"

                        # tmp_compbkgsub = companalyze_hists[a_hist][b_sample][c_var]["bkgsub"].Clone()
                        tmp_compbkgsub_tuned = companalyze_hists[a_hist][b_sample][c_var]["bkgsub_tuned"].Clone()
                        DrawDataMCPlot2D_new(
                            tmp_bkgsub_tuned, 
                            tmp_mcrecosig_tuned, 
                            tmp_types_mcreco_tuned, 
                            xvar_name, xvar_units, xvar_bins, 
                            yvar_name, yvar_units, yvar_bins,
                            counts_ztitle, 
                            var_outdir, 
                            pdf_canvas_name, 
                            datacompbkgsub_canvas_title, 
                            "_bkgsub", 
                            multipliers,
                            tmp_do_stack, 
                            tmp_do_nostack,
                            False,
                            companalyze_hists[a_hist][b_sample][c_var]["bkgsub_tuned"].Clone(),
                        )
                # unfolded
                if "unfolded" not in skipstage_list:
                    multipliers = []
                    unfolded_canvas_title = "Unfolded"
                    if "selected_truth_tuned" in found_inputtypestuned:
                        print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Doing unfolded")
                        DrawDataMCPlot2D_new(
                            tmp_unfolded_tuned, 
                            tmp_mcseltru_tuned, 
                            tmp_types_mcseltru_tuned, 
                            xvar_name, xvar_units, xvar_bins, 
                            yvar_name, yvar_units, yvar_bins,
                            counts_ztitle, 
                            var_outdir, 
                            pdf_canvas_name, 
                            unfolded_canvas_title, 
                            "_unfolded", 
                            multipliers,
                            tmp_do_stack, 
                            tmp_do_nostack
                        )
                    if "unfolditers" not in skipstage_list:
                        for i in range(len(tmp_unfoldediter_tuned_list)):
                            tmp_canvas_title = "%s iter %d"%(unfolded_canvas_title, i+1)
                            if "selected_truth_tuned" in found_inputtypestuned:
                                DrawDataMCPlot2D_new(
                                    tmp_unfoldediter_tuned_list[i], 
                                    tmp_mcseltru_tuned, 
                                    tmp_types_mcseltru_tuned, 
                                    xvar_name, xvar_units, xvar_bins, 
                                    yvar_name, yvar_units, yvar_bins,
                                    counts_ztitle, 
                                    var_outdir, 
                                    pdf_canvas_name, 
                                    tmp_canvas_title, 
                                    "_unfolded_iter%02d"%(i+1), 
                                    multipliers,
                                    tmp_do_stack, 
                                    tmp_do_nostack
                                )
                # eff corr
                if "effcorr" not in skipstage_list:
                    mutlipliers = []
                    effcorr_canvas_title = "Efficiency Corrected"
                    if "all_truth_tuned" in found_inputtypestuned:
                        print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Doing Efficiency")
                        DrawDataMCPlot2D_new(
                            tmp_effcorr_tuned, 
                            tmp_mcalltru_tuned, 
                            tmp_types_mcalltru_tuned, 
                            xvar_name, xvar_units, xvar_bins, 
                            yvar_name, yvar_units, yvar_bins,
                            counts_ztitle, 
                            var_outdir, 
                            pdf_canvas_name, 
                            effcorr_canvas_title, 
                            "_effcorr", 
                            mutlipliers,
                            tmp_do_stack, 
                            tmp_do_nostack
                        )
                        if "selected_truth_tuned" in found_inputtypestuned:
                            eff_canvas_title = "Efficiency"
                            DrawEfficiency2D(
                                tmp_mcseltru_tuned, 
                                tmp_mcalltru_tuned, 
                                tmp_types_mcseltru, 
                                tmp_types_mcalltru,
                                xvar_name, xvar_units, xvar_bins, 
                                yvar_name, yvar_units, yvar_bins,
                                var_outdir, 
                                pdf_canvas_name, 
                                eff_canvas_title
                            )
                eavail_mutlipliers = []
                #     1.0,
                #     12.0,
                #     18.0,
                #     26.0,
                #     41.0,
                #     82.0,
                #     200.0,
                # ]
                # cross section
                if "sigma" not in skipstage_list:
                    #lower[-0.25]{#scale[0.6]{(%s)}}
                    # sigma_ztitle = "d^{2}#sigma/d%sd%s (cm^{2}/%s/%s/Nucleon)"%(xvar_name, yvar_name, xvar_units, yvar_units)
                    sigma_ztitle = "d^{2}#it{#sigma}/^{}d#it{%s}d#it{%s}#lower[-0.15]{#scale[0.7]{ (cm^{2}/(%s)/(%s)/Nucleon)}}"%(xvar_name, yvar_name, xvar_units, yvar_units)
                    sigma_canvas_title = "Cross section"
                    if found_typessigma:
                        print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Doing cross section")


                        print(eavail_mutlipliers)
                        DrawDataMCPlot2D_new(
                            tmp_sigma_tuned, 
                            tmp_sigmamc, 
                            tmp_typessigma, 
                            xvar_name, xvar_units, xvar_bins, 
                            yvar_name, yvar_units, yvar_bins,
                            sigma_ztitle, 
                            var_outdir, 
                            pdf_canvas_name, 
                            sigma_canvas_title, 
                            "_sigma",
                            eavail_mutlipliers,
                            tmp_do_stack, 
                            tmp_do_nostack
                        )
                if domodelcomp and "modelcomp" not in skipstage_list:
                    sigma_ztitle = "d^{2}#it{#sigma}/^{}d#it{%s}d#it{%s}#lower[-0.15]{#scale[0.7]{ (cm^{2}/(%s)/(%s)/Nucleon)}}"%(xvar_name, yvar_name, xvar_units, yvar_units)
                    modelcomp_canvas_title = "Cross section Model Comparison"
                    DrawDataMCPlot2D_new(
                        tmp_sigma_tuned, 
                        tmp_sigmamc, 
                        tmp_model_hists, 
                        xvar_name, xvar_units, xvar_bins, 
                        yvar_name, yvar_units, yvar_bins,
                        sigma_ztitle, 
                        var_outdir, 
                        pdf_canvas_name, 
                        modelcomp_canvas_title, 
                        "_sigmaModelComp",
                        eavail_mutlipliers,
                        do_stack = False, 
                        do_nostack = True, 
                        do_error_summary = False
                    )
                if docompdata and "compdata" not in skipstage_list:

                    tmp_compsigma = companalyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_effcorr_sigma"].Clone()
                    tmp_compsigma_tuned = companalyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_effcorr_sigma_tuned"].Clone()

                    sigma_ztitle = "d^{2}#it{#sigma}/^{}d#it{%s}d#it{%s}#lower[-0.15]{#scale[0.7]{ (cm^{2}/(%s)/(%s)/Nucleon)}}"%(xvar_name, yvar_name, xvar_units, yvar_units)
                    modelcomp_canvas_title = "Cross section Data Comparison"
                    DrawDataMCPlot2D_new(
                        tmp_sigma_tuned, 
                        tmp_sigmamc, 
                        tmp_typessigma, 
                        xvar_name, xvar_units, xvar_bins, 
                        yvar_name, yvar_units, yvar_bins,
                        sigma_ztitle, 
                        var_outdir, 
                        pdf_canvas_name, 
                        modelcomp_canvas_title, 
                        "_sigmaDataComp",
                        eavail_mutlipliers,
                        do_stack = True, 
                        do_nostack = True, 
                        do_error_summary = False,
                        i_comp_data_hist = tmp_compsigma_tuned,
                    )
                # close if sigma
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> bkg sub")    
                PrintSelectionBreakDown(tmp_bkgsub_tuned, tmp_mcrecosig_tuned, tmp_types_mcreco_tuned)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> sigma")    
                PrintSelectionBreakDown(tmp_sigma_tuned, tmp_sigmamc, tmp_typessigma)
            # Close if h2d
            dummy_canvas.Print(os.path.join(var_outdir,pdf_canvas_name+".pdf")+"]","pdf")
        # close c_var loop
    # close b_sample loop
# close a_hist loop


sys.exit(1)
