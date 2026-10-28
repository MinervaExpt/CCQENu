# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023


# from re import L
import sys, os
import ROOT
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
    TFractionFitter,
    TLegend,
    TLatex,
    TString,
    TPad,
)
from PlotUtils import MnvH1D, MnvH2D, HyperDimLinearizer, GridCanvas
import math
# import json5 as json
import json, re
import datetime
mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")

IncludeSysBool = False
global_noData = True  # use this to plot MC only types
noData = global_noData  # dummy bc dumb
dotypes = False  # use this if ou want to do by types
dotuned=False  # use this if you have tuned hists
doratio = True  # use this if you want to include a data/mc ratio
projY = False

ROOT.TH1.AddDirectory(ROOT.kFALSE)

legendfontsize = 0.042

_xsize = 1100.0
_ysize = 720.0

latex_x = 0.72
latex_y = 0.53

data_marker_size = 0.5

def GetHistDict(i_file,POTScale):
    groups = {}
    keys = i_file.GetListOfKeys()
    for k in keys:
        name = k.GetName()
        if "___" not in name: continue
        parse = name.split("___")
        if len(parse) < 5: continue
        hist = parse[0]
        sample = parse[1]
        cat = parse[2]
        variable = parse[3]
        recotrutype = parse[4]
        # print("looking at %s"%name)

        if "types" in recotrutype and not dotypes:
            continue
        if "types" not in recotrutype and dotypes:
            continue
        if "reconstructed" not in recotrutype:
            continue
        if cat != "data":
            if "tuned" not in recotrutype and dotuned:
                continue
            if "tuned" in recotrutype and not dotuned:
                continue
        if cat not in catstodo:
            continue
        if sample not in samplestodo:
            continue

        h = i_file.Get(name).Clone()
        if h.GetEntries() <= 0:
            print("hist %s has no entries. Skipping..."%name)
            continue
        if "data" in cat:
            h.SetMarkerColor(ROOT.kBlack)
            h.SetLineColor(ROOT.kBlack)
            h.SetMarkerSize(data_marker_size)
            h.SetMarkerStyle(20)
            h.SetLineWidth(1)
            h.Scale(1.0,"width")
        else:
            if POTScale >= 0:
                h.Scale(POTScale)

        if hist not in groups.keys():
            groups[hist] = {}
        if sample not in groups[hist].keys():
            groups[hist][sample] = {}
        if variable not in groups[hist][sample]:
            groups[hist][sample][variable] = {}
        if cat not in groups[hist][sample][variable]:
            groups[hist][sample][variable][cat] = {}
        # if "qelikenot" not in groups[hist][sample][variable]:
        #     groups[hist][sample][variable]["qelikenot"] = {}
        # if "mctot" not in groups[hist][sample][variable]:
        #     groups[hist][sample][variable]["mctot"] = {}
        groups[hist][sample][variable][cat] = h
    # check if mctot and qelikenot in there
    for a_hist in groups:
        for b_sample in groups[a_hist]:
            for c_var in groups[a_hist][b_sample]:
                missing_bkg = False
                for bkgcat in backgrounds:
                    if bkgcat not in groups[a_hist][b_sample][c_var]:
                        missing_bkg = True
                        break
                if missing_bkg or "qelike" not in groups[a_hist][b_sample][c_var]:
                    continue
                tmp_qelikenot_hist = groups[a_hist][b_sample][c_var][backgrounds[0]].Clone(
                    groups[a_hist][b_sample][c_var][backgrounds[0]].GetName().replace(backgrounds[0],"qelikenot")
                )
                tmp_mctot_hist = groups[a_hist][b_sample][c_var]["qelike"].Clone(
                    groups[a_hist][b_sample][c_var]["qelike"].GetName().replace(backgrounds[0],"mctot")
                )
                for bkgcat in backgrounds:
                    tmp_qelikenot_hist.Add(groups[a_hist][b_sample][c_var][bkgcat])
                    tmp_mctot_hist.Add(groups[a_hist][b_sample][c_var][bkgcat])
                if "qelikenot" not in groups[a_hist][b_sample][c_var]:
                    groups[a_hist][b_sample][c_var]["qelikenot"] = tmp_qelikenot_hist
                if "mctot" not in groups[a_hist][b_sample][c_var]:
                    groups[a_hist][b_sample][c_var]["mctot"] = tmp_mctot_hist
    return groups
    
        



def GetHistHDDict(i_file, POTScale):
    groups = {}
    keys = i_file.GetListOfKeys()

    # find all the valid histogram and group by keywords
    for k in keys:
        name = k.GetName()
        if "___" not in name:
            continue
        parse = name.split("___")
        if len(parse) < 5:
            continue

        hist = parse[0]
        sample = parse[1]
        cat = parse[2]
        variable = parse[3]
        # print("checking hist ", name)
        if "reconstructed" not in parse[4]:
            continue
        if ("types" in parse[4]) and (not dotypes):
            continue
        if ("types" not in parse[4]) and dotypes:
            continue
        if "simulfit" in parse[4]:
            continue
        if hist == "h":
            continue
        if hist != "hHD" and cat != "data":
            continue
        if cat == "data" and hist != "h2D":
            continue
        if cat not in catstodo:
            continue
        # if variable not in varsHDtodo+vars2Dtodo:
        #     continue
        if sample not in samplestodo:
            continue

        if "tuned" in parse[4]:
            sample += "_Tuned"
        if hist == "hHD":
            if "_" in variable:
                if len(variable.split("_")) == 3:
                    # Skip 2D vars that don't have the PID as a y axis
                    if (
                        variable.split("_")[2].find("ProtonCandMCPID") == -1
                        and variable.split("_")[2].find("ProtonCandsMCPID") == -1
                    ):
                        print("Missing ProtonCandMCPID in ", variable)
                        continue
                    # Add to list to loop over later
                    if variable not in varsHDtodo:
                        varsHDtodo.append(variable)
                    # Add to list to check later if there's a 1D data that exists
                    if (
                        variable.split("_")[0] + "_" + variable.split("_")[1]
                        not in vars2Dtodo
                    ):
                        vars2Dtodo.append(
                            variable.split("_")[0] + "_" + variable.split("_")[1]
                        )
                else:
                    print("Skipping variable that isn't formatted properly: ", variable)
                    continue
            else:
                print("Skipping variable that isn't formatted properly: ", variable)
                continue

        print("adding hist to the list ", name)
        if sample not in groups.keys():
            groups[sample] = {}
        if variable not in groups[sample].keys():
            groups[sample][variable] = {}
        if cat not in groups[sample][variable].keys():
            groups[sample][variable][cat] = {}

        # print("\t",sample, variable, cat)
        h = i_file.Get(name).Clone()
        if h.GetEntries() <= 0:
            print("hist ", name, " has no entries, skipping...")
            continue
        h.SetFillColor(catscolors[cat])
        # h.SetLineColor(catscolors[cat] + 1)
        h.SetLineColor(ROOT.TColor.GetColorDark(catscolors[cat]))
        if "data" in cat:
            if h.GetEntries() <= 0:
                continue
            # h.SetMarkerStyle(20)
            # h.SetMarkerSize(1.5)
        else:
            h.Scale(POTScale)
        # if cat in backgrounds:
        #     h.SetFillStyle(3244)

        groups[sample][variable][cat] = h
    # do the plotting
    if "qelikenot" not in backgrounds:
        backgrounds.append("qelikenot")
        print("Combining backgrounds to make a background total")
        for a_sample in groups.keys():
            for b_var in groups[a_sample].keys():
                if "_" not in b_var:
                    continue
                if len(b_var.split("_"))!=3:
                    continue
                if "qelikenot" in groups[a_sample][b_var].keys():
                    continue
                groups[a_sample][b_var]["qelikenot"] = {}
                first_cat = True
                for c_cat in backgrounds:
                    if c_cat == "qelikenot":
                        continue
                    tmp_hist = groups[a_sample][b_var][c_cat].Clone()
                    if first_cat:
                        groups[a_sample][b_var]["qelikenot"] = tmp_hist.Clone(
                            tmp_hist.GetName().replace(c_cat, "qelikenot")
                        )
                        first_cat = False
                        continue
                    groups[a_sample][b_var]["qelikenot"].Add(tmp_hist)

    return groups

def GetHist2DDict(i_file, POTScale):
    groups = {}
    keys = i_file.GetListOfKeys()

    # find all the valid histogram and group by keywords
    for k in keys:
        name = k.GetName()
        if "___" not in name:
            continue
        parse = name.split("___")
        if len(parse) < 5:
            continue

        hist = parse[0]
        sample = parse[1]
        cat = parse[2]
        variable = parse[3]
        # print("checking hist ", name)
        if "reconstructed" not in parse[4]:
            continue
        if ("types" in parse[4]) and (not dotypes):
            continue
        if ("types" not in parse[4]) and dotypes:
            continue
        if "simulfit" in parse[4]:
            continue
        if hist == "hHD":
            continue
        if cat == "data" and hist != "h":
            continue
        if cat not in catstodo:
            continue
        # if variable not in varsHDtodo+vars2Dtodo:
        #     continue
        if sample not in samplestodo:
            continue

        if "tuned" in parse[4]:
            sample += "_Tuned"
        if hist == "h2D":
            if "_" in variable:
                if len(variable.split("_")) == 2:
                    # Skip 2D vars that don't have the PID as a y axis
                    if variable.split("_")[1] != "PlotPrimaryProtonCandMCPID":
                        print("this hist %s does not have PlotPrimaryProtonCandMCPID, skipping"%(name))
                        continue
                    # Add to list to loop over later
                    if variable not in vars2Dtodo:
                        vars2Dtodo.append(variable)
                    # Add to list to check later if there's a 1D data that exists
                    if variable.split("_")[0] not in vars1Dtodo:
                        vars1Dtodo.append(variable.split("_")[0])
                else:
                    print("Skipping variable that isn't formatted properly: ", variable)
                    continue
            else:
                print("Skipping variable that isn't formatted properly: ", variable)
                continue

        print("adding hist to the list ", name)
        if sample not in groups.keys():
            groups[sample] = {}
        if variable not in groups[sample].keys():
            groups[sample][variable] = {}
        if cat not in groups[sample][variable].keys():
            groups[sample][variable][cat] = {}

        # print("\t",sample, variable, cat)
        h = i_file.Get(name).Clone()
        if h.GetEntries() <= 0:
            print("hist ", name, " has no entries, skipping...")
            continue
        h.SetFillColor(catscolors[cat])
        # h.SetLineColor(catscolors[cat] + 1)
        h.SetLineColor(ROOT.TColor.GetColorDark(catscolors[cat]))
        # if "data" in cat:
        #     if h.GetEntries() <= 0:
        #         continue
        #     # h.SetMarkerStyle(20)
        #     # h.SetMarkerSize(1.5)
        # else:
        #     h.Scale(POTScale)
        # # if cat in backgrounds:
        # #     h.SetFillStyle(3244)

        groups[sample][variable][cat] = h
    # do the plotting
    if "qelikenot" not in backgrounds:
        backgrounds.append("qelikenot")
        print("Combining backgrounds to make a background total")
        for a_sample in groups.keys():
            for b_var in groups[a_sample].keys():
                if "_" not in b_var:
                    continue
                if len(b_var.split("_"))!=3:
                    continue
                if "qelikenot" in groups[a_sample][b_var].keys():
                    continue
                groups[a_sample][b_var]["qelikenot"] = {}
                first_cat = True
                for c_cat in backgrounds:
                    if c_cat == "qelikenot":
                        continue
                    tmp_hist = groups[a_sample][b_var][c_cat].Clone()
                    if first_cat:
                        groups[a_sample][b_var]["qelikenot"] = tmp_hist.Clone(
                            tmp_hist.GetName().replace(c_cat, "qelikenot")
                        )
                        first_cat = False
                        continue
                    groups[a_sample][b_var]["qelikenot"].Add(tmp_hist)

    return groups

def GetHDBinning(i_file, varHD_name):
    bins = []

    bigvarconfig_string = i_file.Get("varsFile_5A").GetTitle()
    # print(bigvarconfig_string)
    bigvarconfig_dict = json.loads(re.sub("//.*","",bigvarconfig_string,flags=re.MULTILINE))
    if varHD_name in bigvarconfig_dict["HyperD"].keys():
        varHDconfig = bigvarconfig_dict["HyperD"][varHD_name]
        axisvars = varHDconfig["vars"]
    else:
        axisvars = varHD_name.split("_")
    vars1Dconfig = bigvarconfig_dict["1D"]
    for var in axisvars:
        varconfig = vars1Dconfig[var]
        if "bins" in varconfig.keys():
            bins1D = [float(bin) for bin in varconfig["bins"]]
            bins.append(bins1D)
            continue
        elif "nbins" in varconfig.keys():
            min = varconfig["min"]
            max = varconfig["max"]
            width = (max - min)/varconfig["nbins"]
            bins1D = [min + bin*width for bin in range(0,varconfig["nbins"]+1)]
            # print(bins1D)
            bins.append(bins1D)
    # print(bins)
    return bins

def GetHDAnalysisType(i_file,varHD_name):
    bigvarconfig_string = i_file.Get("varsFile_5A").GetTitle()
    # print(bigvarconfig_string)
    bigvarconfig_dict = json.loads(re.sub("//.*","",bigvarconfig_string,flags=re.MULTILINE))
    if varHD_name not in bigvarconfig_dict["HyperD"].keys():
        return 1
    varHDconfig = bigvarconfig_dict["HyperD"][varHD_name]
    if "analysistype" in varHDconfig.keys():
        return varHDconfig["analysistype"]
    print("Couldn't find analysis type. Trying k1D...")
    return 1

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


def CCQECanvas(name, title, xsize=1000, ysize=1800):
    c2 = ROOT.TCanvas(name, title, xsize, ysize)
    # c2.SetLeftMargin(0.1)
    c2.SetRightMargin(0.15)
    c2.SetLeftMargin(0.11)
    c2.SetTopMargin(0.1)
    c2.SetBottomMargin(0.1)
    return c2


def MakeHistPretty(hist,pid,cat,projwidth=1.):
    """
    hist is the projected 1D hist you are looking at
    pid is the zbin/particle hist you are looking at
    cat is the category (qelike, qelikenot, data, etc.)
    projwidth is the width of the bin this hist is a projection of
    """
    hist.Scale(1./projwidth,"width")
    if cat == "data":
        hist.SetMarkerStyle(20)
        # hist.SetMarkerSize(1.5)
        hist.SetMarkerColor(ROOT.kBlack)
        hist.SetLineColor(ROOT.kBlack)
    else:
        if pid == -1:
            print("something wrong with ", hist.GetName())
        hist.SetFillColor(bin_pid_colors[pid])
        hist.SetLineColor(bin_pid_colors[pid])
        if cat in backgrounds:
            hist.SetFillStyle(3244)
    return hist

def CCQELegend(xlow, ylow, xhigh, yhigh):
    leg = ROOT.TLegend(xlow, ylow, xhigh, yhigh)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(legendfontsize)
    return leg


def AddPreliminary():
    font = 112
    color = ROOT.kRed + 1
    latex = ROOT.TLatex()
    latex.SetNDC()
    # latex.SetTextSize(legendfontsize - 0.004)
    latex.SetTextSize(legendfontsize - 0.01)
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


def MakeMCtot(i_mchists):
    name = i_mchists[0].GetName()
    split = name.split("___")
    mctot = i_mchists[0].Clone(str(name.replace(split[2], "mctot")))
    for i in range(1, len(i_mchists)):
        mctot.Add(i_mchists[i].Clone())
    return mctot


# TODO check uncertainty stuff options for systematics etc a la MnvPlotter
def MakeDataMCRatio(i_data, i_mctot):
    mcratio = i_data.Clone(str(i_data.GetName().replace("data", "datamcratio")))
    mcratio.Divide(i_data, i_mctot)
    return mcratio


cat_order = list(
    [
        "other",
        "neutralpion",
        "chargedpion",
        "qelike",
        # "qelikenot",
        "data",
    ]
)

# if noData:
#     cat_order = list(
#         [
#             # "other",
#             # # "multipion",
#             # "neutralpion",
#             # "chargedpion",
#             # "qelikenot",
#             "qelike_old",
#             "qelike",
#         ]
#     )
signal = ["data", "qelike", "qelike_old"]

backgrounds = [cat for cat in cat_order if cat not in signal]
# print(backgrounds)

catstodo = cat_order


catscolors = {
    "data": ROOT.kBlack,
    "qelike": ROOT.kBlue - 6,
    "qelikenot": ROOT.kRed - 6,
    "qelike_old": ROOT.kBlue - 6,
    "qelikenot_old": ROOT.kRed - 6,
    "chargedpion": ROOT.kMagenta - 6,
    "neutralpion": ROOT.kRed - 6,
    "multipion": ROOT.kGreen - 6,
    "other": ROOT.kYellow - 6,
}

vars2Dtodo = []
varsHDtodo = []

titles = {
    "LeadingNeutCandvtxBoxDist_LeadingNeutCandTopMCPID": "Leading blob box dist from vtx",
    "SecNeutCandvtxBoxDist_SecNeutCandTopMCPID": "Second blob box dist from vtx",
    "ThirdNeutCandvtxBoxDist_ThirdNeutCandTopMCPID": "Third blob box dist from vtx",
    "LeadingNeutCandvtxZDist_LeadingNeutCandTopMCPID": "Leading Blob zdist from vtx",
    "LeadingNeutCandvtxSphereDist_LeadingNeutCandTopMCPID": "Leading Blob spherical dist from vtx",
    "LeadingNeutCandEdep_LeadingNeutCandTopMCPID": "Leading Blob TotalE",
    "SecNeutCandvtxZDist_SecNeutCandTopMCPID": "Second Blob zdist from vtx",
    "SecNeutCandvtxSphereDist_SecNeutCandTopMCPID": "Second Blob spherical dist from vtx",
    "SecNeutCandEdep_SecNeutCandTopMCPID": "Second Blob TotalE",
    "ThirdNeutCandvtxZDist_ThirdNeutCandTopMCPID": "Third Blob zdist from vtx",
    "ThirdNeutCandvtxSphereDist_ThirdNeutCandTopMCPID": "Third Blob spherical dist from vtx",
    "ThirdNeutCandEdep_ThirdNeutCandTopMCPID": "Third Blob TotalE",
    "LeadingNeutCandMuonDist_LeadingNeutCandTopMCPID": "Leading blob dist from #mu track",
    "SecNeutCandMuonDist_SecNeutCandTopMCPID": "Second blob dist from #mu track",
    "ThirdNeutCandMuonDist_ThirdNeutCandTopMCPID": "Third blob dist from #mu track",
    "LeadingNeutCandMuonAngle_LeadingNeutCandTopMCPID": "Leading blob angle from #mu track",
    "SecNeutCandMuonAngle_SecNeutCandTopMCPID": "Second blob dist angle #mu track",
    "ThirdNeutCandMuonAngle_ThirdNeutCandTopMCPID": "Third blob angle from #mu track",
    "LeadingNeutCandClusterMaxE_LeadingNeutCandTopMCPID": "Leading max cluster E",
    "SecNeutCandClusterMaxE_SecNeutCandTopMCPID": "Second blob max cluster E",
    "ThirdNeutCandClusterMaxE_ThirdNeutCandTopMCPID": "Third blob max cluster E",
}

var_short_names = {
    "LeadingNeutCandEdep": "E_{dep}",
    "NeutCandsEdep": "E_{dep}",
    "LeadingNeutCandvtxSphereDist": "d_{vtx}",
    "NeutCandsvtxSphereDist": "d_{vtx}",
    "NeutCandsMuonCosTheta": "cos d#theta_{#mu}",
    "NeutCandsTrackEndDist": "d_{track}",
    "ptmu": "p_{T}",
    "EAvail": "E_{Avail}",
    "recoil": "recoil",
    "pzmu": "p_{||}",
    "Q2QE": "Q^{2}_{QE}",
    "PrimaryProtonScore": "Primary Proton Score",
    "ProtonScores": "All Proton Scores",
    "ProtonTfromdEdx": "Proton T"
}


samplestodo = [
    "QElike",
    "QElike2trackNoPID",
    "TrackSideband",
    "BlobSideband",
    # "QElike_old"
    # "QElike0Blob",
    # "QElike1Blob",
    # "QElike2Blob"
]

# Used to make the labels. See CVUniverse and variables config for binnning
bin_pid = {
    1: "n",
    2: "p",
    3: "#pi^{0}",
    # 4: "#pi^{+}", # decided to combine pi+ (4) with pi- (5)
    # 5: "#pi^{-}",
    4: "#pi^{#pm}",
    5: "#pi^{#pm}",
    6: "#gamma",
    7: "e^{#pm}",
    8: "#mu^{#pm}",
    9: "No Top",
    10: "Other",
}

bin_pid_colors = {
    1: ROOT.kP10Blue,
    2: ROOT.kP10Yellow,
    3: ROOT.kP10Green,
    # 4: ROOT.kP10Ash, # decided to combine pi+ (4) with pi- (5)
    # 4: ROOT.kP10Orange,
    # 5: ROOT.kP10Orange,
    4: ROOT.kP10Blue,
    5: ROOT.kP10Blue,
    6: ROOT.kP10Violet,
    7: ROOT.kP10Cyan,
    8: ROOT.kP10Red,
    9: ROOT.kP10Brown,
    10: ROOT.kP10Gray,
}

# bin_pid_order = list([10, 7, 6, 5, 4, 3, 8, 2, 1])
# decided to combine pi+ (4) with pi- (5)
bin_pid_order = list([10, 9, 7, 6, 5, 3, 8, 2, 1]) 

bin_pid_order = [
    10, 
    9, 
    7, 
    6, 
    5, 
    3, 
    8, 
    1,
    2, 
] 

process = ["data", "QE", "RES", "DIS", "COH", "", "", "", "2p2h", ""]
whichcats = ["data", "qelike", "qelikenot"]
nproc = len(process)
for x in range(0, nproc + 1):
    process.append(process[x] + "-not")
type_colors = {
    0: ROOT.kBlack,
    1: ROOT.kBlue - 6,
    2: ROOT.kMagenta - 6,
    3: ROOT.kRed - 6,
    4: ROOT.kYellow - 6,
    5: ROOT.kWhite,
    6: ROOT.kWhite,
    7: ROOT.kWhite,
    8: ROOT.kGreen - 6,
    9: ROOT.kTeal - 6,
    10: ROOT.kBlue - 1,
    11: ROOT.kBlue - 10,
    12: ROOT.kMagenta - 10,
    13: ROOT.kRed - 10,
    14: ROOT.kYellow - 10,
    15: ROOT.kGray,
    16: ROOT.kBlack,
    17: ROOT.kBlack,
    18: ROOT.kGreen - 6,
    19: ROOT.kTeal - 6,
}


samplenames = {
    "QElike": "QElike Signal Sample",
    "QElike_old": "QElike 120MeV Protons Signal Sample",
    "QElike0Blob": "QElike Signal w/o Blobs",
    "QElike1Blob": "QElike Signal w/ 1 Blob",
    "QElike2Blob": "QElike Signal w/ 2 Blobs",
    "QElikeOld": "2D Era QElike Signal Sample",
    # "BlobSideband": "1 #pi^{0} Sideband",
    "BlobSideband": "Blob Sideband",
    "MultipBlobSideband": "Multiple #pi Sideband",
    "HiPionThetaSideband": "Backward #pi^{#pm} Sideband",
    "LoPionThetaSideband": "Forward #pi^{#pm} Sideband",
    "TrackSideband": "Track Sideband",
}

if len(sys.argv) == 1:
    print("enter root file name and optional 2nd argument to get tuned version")
flag = "types_"
filename = sys.argv[1]
if len(sys.argv) > 2:
    flag = "tuned_type_"

f = TFile.Open(filename, "READONLY")
plotdirbase = os.getenv("OUTPUTLOC")

plotdir = MakePlotDir("ProtonScorePlotsHD")
dirname = filename.replace(".root", "_protonscore")
for cat in catstodo:
    dirname += "_" + cat
# outfilename=filebasename1.replace(".root","_2DPlots")
outdirname = os.path.join(plotdir, dirname)
if not os.path.exists(outdirname):
    print(outdirname)
    os.mkdir(outdirname)


# h_pot = f.Get("POT_summary")
# dataPOT = h_pot.GetBinContent(1)
# mcPOTprescaled = h_pot.GetBinContent(2)
# POTScale = dataPOT / mcPOTprescaled
# print("POTScale: ", POTScale)
POTScale = -1

# groupsHD = {}
# logvars = ["Q2QE"]
# groupsHD = GetHistHDDict(f, POTScale)

# if not noData:
#     cat_order = list(["qelikenot", "qelike", "data"])
# else:
#     cat_order = list(["qelikenot","qelike"])

# ROOT.gStyle.SetOptStat(0)
# # template = "%s___%s___%s___%s"

# for a_sample in groupsHD.keys():
#     # for b_var in groupsHD[a_sample].keys():
#     if "_Tuned" in a_sample:
#         dotuned = True
#         tunedname = a_sample.replace("_Tuned", "")
#     else:
#         dotuned = False
#     data_sample_name = a_sample
#     for b_var in varsHDtodo:
#         if b_var not in groupsHD[a_sample].keys():
#             continue
#         xvar = b_var.split("_")[0]
#         yvar = b_var.split("_")[1]
#         noData = global_noData
#         data_var = b_var.split("_")[0]+"_"+b_var.split("_")[1]
#         if data_var not in vars2Dtodo:
#             print("bad data_var", data_var, " skipping data for HD var ", b_var)
#             noData = True
#         if not noData:
#             # data_sample_name = a_sample
#             if dotuned:
#                 data_sample_name = tunedname
#             if data_var not in groupsHD[data_sample_name].keys():
#                 print("Couldn't find data_var. Skipping", b_var)
#                 # noData = True
#                 continue
#             else:
#                 data = groupsHD[data_sample_name][data_var]["data"].Clone()
#                 data.SetMarkerColor(ROOT.kBlack)
#                 data.SetLineColor(ROOT.kBlack)

#         bins = GetHDBinning(f,b_var)
#         analysistype = GetHDAnalysisType(f,b_var)
#         flowadjust = 1
#         new_bin_pid_order = bin_pid_order
#         if analysistype in [0,1]:
#             flowadjust = 1
#         elif analysistype in [2,3]:
#             flowadjust = -1
#             new_bin_pid_order = [pid-1 for pid in bin_pid_order]
#         print(analysistype)
#         print(bins)
#         myhyperdim = HyperDimLinearizer(bins, analysistype)

#         n_xbins = len(bins[0]) + flowadjust
#         n_ybins = len(bins[1]) + flowadjust
#         n_zbins = len(bins[2]) + flowadjust
#         h2D_dict = {}
#         for c_cat in cat_order:
#             tmp_h2D_list = []
#             if c_cat == "data":
#                 if noData:
#                     continue
#                 print(data_sample_name, data_var, c_cat)
#                 # print(groupsHD[data_sample_name].keys())
#                 data = groupsHD[data_sample_name][data_var][c_cat].Clone()
#                 if -1 not in h2D_dict.keys():
#                     h2D_dict[-1] = {}
#                 # h2D_dict[-1] = {"data":data}
#                 h2D_dict[-1] = {"data":data}
#                 continue
#             hHD = groupsHD[a_sample][b_var][c_cat].Clone()
#             tmp_h2D_list = myhyperdim.Get2DHistos(hHD,IncludeSysBool)
#             if n_zbins!= len(tmp_h2D_list):
#                 print("bins are wrong!!! You calculated ", n_zbins," zbins but there are ", len(tmp_h2D_list))
#                 sys.exit(1)
#             # n_zbins = len(tmp_h2D_list)
#             for zbin in new_bin_pid_order:
#                 # print ("adjusted pid ", zbin)
#                 if zbin not in h2D_dict.keys():
#                     h2D_dict[zbin] = {}
#                 if c_cat not in h2D_dict[zbin].keys():
#                     h2D_dict[zbin][c_cat] = {}

#                 h2D_dict[zbin][c_cat] = tmp_h2D_list[zbin]
#                 if analysistype in [0,1] and zbin == 5:
#                     h2D_dict[zbin][c_cat].Add(tmp_h2D_list[zbin-1])
#                 if analysistype in [2,3] and zbin == 4:
#                     h2D_dict[zbin][c_cat].Add(tmp_h2D_list[zbin-1])

#         pionproton_h2d_dict = {"pi":TH2D(), "proton":TH2D(),"total":TH2D()}
#         firstcat = True
#         for c_cat in cat_order:
#             if analysistype in [0,1]:
#                 if firstcat:
#                     pionproton_h2d_dict["pi"] = h2D_dict[5][c_cat].Clone()
#                     pionproton_h2d_dict["proton"] = h2D_dict[2][c_cat].Clone()
#                     firstcat = False
#                 else:
#                     pionproton_h2d_dict["pi"].Add(h2D_dict[5][c_cat])
#                     pionproton_h2d_dict["proton"].Add(h2D_dict[2][c_cat])
#             else:
#                 if firstcat:
#                     pionproton_h2d_dict["pi"] = h2D_dict[4][c_cat].Clone()
#                     pionproton_h2d_dict["proton"] = h2D_dict[1][c_cat].Clone()
#                     firstcat = False
#                 else:
#                     pionproton_h2d_dict["pi"].Add(h2D_dict[4][c_cat])
#                     pionproton_h2d_dict["proton"].Add(h2D_dict[1][c_cat])
#         # TODO make naming smarter
#         xvarname = var_short_names[xvar]
#         yvarname = var_short_names[yvar]
#         pionproton_h2d_dict["pi"].Scale(1.0,"width")
#         pionproton_h2d_dict["proton"].Scale(1.0, "width")
#         pionproton_h2d_dict["pi"].SetLineColor(ROOT.kRed+1)
#         pionproton_h2d_dict["proton"].SetLineColor(ROOT.kBlue + 2)
#         pionproton_h2d_dict["proton"].GetXaxis().SetTitle(xvarname)
#         pionproton_h2d_dict["proton"].GetYaxis().SetTitle(yvarname)
#         pionproton_h2d_dict["proton"].GetXaxis().CenterTitle()
#         pionproton_h2d_dict["proton"].GetYaxis().CenterTitle()

#         pionproton_h2d_dict["total"] = pionproton_h2d_dict["proton"].Clone("total")
#         pionproton_h2d_dict["total"].Add(pionproton_h2d_dict["pi"])

#         pionproton_h2d_dict["protonratio"] = pionproton_h2d_dict["proton"].Clone(
#             "protonratio"
#         )
#         pionproton_h2d_dict["protonratio"].Divide(pionproton_h2d_dict["protonratio"], pionproton_h2d_dict["total"] , 1.,1.)

#         pionproton_h2d_dict["piratio"] = pionproton_h2d_dict["pi"].Clone(
#             "piratio"
#         )
#         pionproton_h2d_dict["piratio"].Divide(pionproton_h2d_dict["piratio"], pionproton_h2d_dict["total"], 1.,1.)

#         leg = CCQELegend(0.85,0.57,0.97,0.43)

#         pionproton_h2d_dict["proton"].SetTitle("Raw %s vs. %s in %s"%(yvarname,xvarname,a_sample))
#         pionproton_h2d_dict["protonratio"].SetTitle(
#             "Ratio %s vs. %s in %s" % (yvarname, xvarname, a_sample)
#         )

#         dummyproton = pionproton_h2d_dict["proton"].Clone()
#         dummyproton.SetFillColor(ROOT.kBlue+2)
#         leg.AddEntry(dummyproton,"Proton","f")
#         dummypion = pionproton_h2d_dict["pi"].Clone()
#         dummypion.SetFillColor(ROOT.kRed + 1)
#         leg.AddEntry(dummypion, "#pi^{#pm}", "f")

#         rawcanvas = CCQECanvas(
#             "Raw_%s_%s_%s"% (a_sample, xvar, yvar), "%s vs. %s in %s" % (yvarname, xvarname, a_sample)
#         )
#         if xvar in ["Q2QE"]:
#             rawcanvas.SetLogx()
#         pionproton_h2d_dict["proton"].Draw("BOX")
#         pionproton_h2d_dict["pi"].Draw("BOX same")
#         leg.Draw()
#         thename = "%s_%s_%s_%s" % ("raw",a_sample, xvar, yvar)

#         canvas_name = thename + "_FinalStates"
#         if dotuned:
#             canvas_name = thename + "_FinalStates_tuned"
#         rawcanvas.Print(os.path.join(outdirname, canvas_name + ".png"))

#         if dotuned:
#             canvas_name = thename + "_FinalStates_tuned"
#         rawcanvas.Print(os.path.join(outdirname, canvas_name + ".png"))

#         del rawcanvas

#         ratiocanvas = CCQECanvas(
#             "Ratio_%s_%s_%s" % (a_sample, xvar, yvar),
#             "Raio %s vs. %s in %s" % (yvarname, xvarname, a_sample),
#         )
#         if xvar in ["Q2QE"]:
#             ratiocanvas.SetLogx()
#         pionproton_h2d_dict["protonratio"].Draw("BOX")
#         pionproton_h2d_dict["piratio"].Draw("BOX same")
#         leg.Draw()
#         thename = "%s_%s_%s" % (a_sample, yvarname, xvarname)

#         canvas_name = thename + "_FinalStates"
#         if dotuned:
#             canvas_name = thename + "_FinalStates_tuned"
#         ratiocanvas.Print(os.path.join(outdirname, canvas_name + ".png"))

#         if dotuned:
#             canvas_name = thename + "_FinalStates_tuned"
#         ratiocanvas.Print(os.path.join(outdirname, canvas_name + ".png"))

#         del ratiocanvas

groups = {}
logvars = ["Q2QE"]
groups = GetHistDict(f, POTScale)
bin_pid_particle = {
    1: "neutron",
    2: "proton",
    3: "pizero",
    4: "piplus", # decided to combine pi+ (4) with pi- (5)
    5: "piminus",
    # 4: "#pi^{#pm}",
    # 5: "#pi^{#pm}",
    6: "gamma",
    7: "electron",
    8: "muon",
    9: "notop",
    10: "other",
}
part_colors = {
    "data": ROOT.kBlack,
    "neutron": ROOT.kP10Blue,
    "proton": ROOT.kP10Yellow,
    "pizero": ROOT.kP10Green,
    # 4: ROOT.kP10Ash, # decided to combine pi+ (4) with pi- (5)
    # 4: ROOT.kP10Orange,
    # 5: ROOT.kP10Orange,
    "piplus": ROOT.kP10Blue,
    "piminus": ROOT.kP10Blue,
    "pipm": ROOT.kP10Blue,
    "gamma": ROOT.kP10Violet,
    "electron": ROOT.kP10Cyan,
    "muon": ROOT.kP10Red,
    "notop": ROOT.kP10Brown,
    "other": ROOT.kP10Gray,
}
particle_names = {   
    "neutron": "#it{n}",
    "proton": "#it{p}",
    "pizero": "#it{#pi^{0}}",
    "piplus": "#it{#pi^{+}}",
    "piminus": "#it{#pi^{-}}",
    "pipm": "#it{#pi^{#pm}}",
    "gamma": "#it{#gamma}",
    "electron": "#it{e^{#pm}}",
    "muon": "#it{#mu^{#pm}}",
    "notop": "Non-GENIE",
    "other": "Other",
}
tunedtag = "Untuned"
if dotuned:
    tunedtag = "Tuned"
# print(groups)
ROOT.gStyle.SetErrorX(0) # This turns off the horizontal error bars
ROOT.gStyle.SetOptStat(0)

plotsubdir = os.path.join("plots","protonscore")
thesisplotdir = MakeThesisPlotDir(plotsubdir)

for a_hist in groups.keys():
    if a_hist in ["hHD", "h2D"]: continue
    for b_sample in groups[a_hist]:
        for c_var in groups[a_hist][b_sample]:
            print("looking at %s %s %s"%(a_hist, b_sample, c_var))
            pidvarname = c_var + "_PlotPrimaryProtonCandMCPID"
            if pidvarname not in groups["h2D"][b_sample]:
                print("Couldn't find the mcpid hist to match hist %s. Skipping..."%c_var)
                continue
            if "mctot" not in groups["h2D"][b_sample][pidvarname]: continue
            data = groups[a_hist][b_sample][c_var]["data"].Clone()
            pid2d_mctot = groups["h2D"][b_sample][pidvarname]["mctot"].Clone()
            
            pid_histdict = {}
            for i in range(1,11):
                tmp_projname = "%s_%s"%(pid2d_mctot.GetName().replace("h2D", "h"), bin_pid_particle[i]) 
                tmp_h_pid = pid2d_mctot.ProjectionX(tmp_projname, i, i)
                tmp_h_pid.Scale(1., "width")
                tmp_h_pid.SetFillColor(bin_pid_colors[i])
                tmp_h_pid.SetLineColor(ROOT.TColor.GetColorDark(bin_pid_colors[i]))
                pid_histdict[bin_pid_particle[i]] = tmp_h_pid
            plot_histdict = {
                "proton": pid_histdict["proton"].Clone()
            }
            plot_histdict["pipm"] = pid_histdict["piplus"].Clone("%s_%s"%(pid2d_mctot.GetName().replace("h2D", "h"), "pipm"))
            plot_histdict["pipm"].Add(pid_histdict["piminus"])
            plot_histdict["other"] = pid_histdict["other"].Clone()
            for part in pid_histdict:
                if part in ["pipm", "piminus", "piplus","proton", "other"]:
                    continue
                plot_histdict["other"].Add(pid_histdict[part])
            stack = THStack("stack_%s%s%s"%(a_hist,b_sample,c_var),"Proton Score")
            stack.Add(plot_histdict["other"])
            stack.Add(plot_histdict["pipm"])
            stack.Add(plot_histdict["proton"])

            leg = ROOT.TLegend(0.7,0.6,0.9,0.9)
            leg.SetFillColor(-1)
            leg.SetFillStyle(0)
            leg.AddEntry(data,"Data", "pe")
            leg.AddEntry(plot_histdict["proton"],"Proton", "fl")
            leg.AddEntry(plot_histdict["pipm"],"#pi^{#pm}", "fl")
            leg.AddEntry(plot_histdict["other"],"Other", "fl")
            leg.SetBorderSize(0)

            # stack.GetXaxis().SetNdivisions(505)
            # stack.GetYaxis().SetNdivisions(505)
            data.GetXaxis().SetNdivisions(505)
            data.GetYaxis().SetNdivisions(505)
            data.GetXaxis().SetTitle("Proton score")
            data.GetYaxis().SetTitle("N_{events} (bin width normalized)")
            data.GetXaxis().CenterTitle()
            data.GetYaxis().CenterTitle()
            data.SetTitle("Proton Score for Signal sample w/o Track PID")
            canvas_name = "canvas_%s_%s_%s"%(b_sample, c_var, tunedtag)
            canvas = ROOT.TCanvas(canvas_name)
            # canvas.Draw()

            plotmax = 1.2*max(data.GetMaximum(), stack.GetMaximum())
            data.SetMaximum(plotmax)
            stack.SetMaximum(plotmax)
            # stack.Draw("hist")
            # data.Draw("axis")
            data.Draw("E1 X0")

            stack.Draw("HIST same")
            data.Draw("E1 X0 same")
            data.Draw("axis same")
            leg.Draw()
            stackedplot_outfilename = os.path.join(outdirname,"protonscore1D_%s_%s_%s.pdf"%(b_sample,c_var,tunedtag))
            canvas.Print(stackedplot_outfilename)
            if thesisplotdir != "":
                thesis_stackedplot_outfilename = os.path.join(thesisplotdir,"protonscore1D_%s_%s_%s.pdf"%(b_sample,c_var,tunedtag))
                canvas.Print(thesis_stackedplot_outfilename)

            # Now make a cumulative plot
            proton_cumul = plot_histdict["proton"].GetCumulative(False)
            pipm_cumul = plot_histdict["pipm"].GetCumulative(False)

            
            proton_cumul.SetFillStyle(0)
            pipm_cumul.SetFillStyle(0)

            proton_cumul.SetLineWidth(3)
            pipm_cumul.SetLineWidth(3)
            
            sum_cumul = proton_cumul.Clone("cumul_ratio")
            sum_cumul.Add(pipm_cumul.Clone())
            
            proton_ratio_cumul = proton_cumul.Clone("proton_cumul_ratio")
            proton_ratio_cumul.Divide(proton_ratio_cumul,sum_cumul.Clone(), 1.,1.)            
        
            pipm_ratio_cumul = pipm_cumul.Clone("pipm_cumul_ratio")
            pipm_ratio_cumul.Divide(pipm_ratio_cumul,sum_cumul.Clone(), 1.,1.)
            proton_ratio_cumul.SetMinimum(0.0)
            proton_ratio_cumul.Draw("HIST")
            pipm_ratio_cumul.Draw("HIST same")
            # proton_cumul.Draw("HIST")
            # pipm_cumul.Draw("HIST same")
            leg.Draw()
            cumul_outname = "cumul_protonscore1D_%s_%s_%s.pdf"%(b_sample,c_var,tunedtag)
            canvas.Print(os.path.join(outdirname,cumul_outname))
            canvas.Print(os.path.join(thesisplotdir,cumul_outname))


print("Now doing hyperdim ones")
for a_hist in groups.keys():
    if a_hist in ["h","hHD"]: continue
    for b_sample in groups[a_hist]:
        for c_var in groups[a_hist][b_sample]:
            print("looking at %s %s %s"%(a_hist, b_sample, c_var))
            if "PlotPrimaryProtonCandMCPID" in c_var: continue
            pidvarname = c_var + "_PlotPrimaryProtonCandMCPID"
            if pidvarname not in groups["hHD"][b_sample]:
                print("Couldn't find the mcpid hist to match hist %s. Skipping..."%c_var)
                continue
            if "mctot" not in groups["hHD"][b_sample][pidvarname]: continue
            data = groups[a_hist][b_sample][c_var]["data"].Clone()
            pidhd_mctot = groups["hHD"][b_sample][pidvarname]["mctot"].Clone()

            x_var = c_var.split("_")[0]
            y_var = c_var.split("_")[1]

            bins = GetHDBinning(f,pidvarname)
            analysistype = GetHDAnalysisType(f,pidvarname)
            flowadjust = 1
            new_bin_pid_order = bin_pid_order
            if analysistype in [0,1]:
                flowadjust = 1
            elif analysistype in [2,3]:
                flowadjust = -1
                new_bin_pid_order = [pid-1 for pid in bin_pid_order]
            print(analysistype)
            print(bins)
            myhyperdim = HyperDimLinearizer(bins, analysistype)

            n_xbins = len(bins[0]) + flowadjust
            n_ybins = len(bins[1]) + flowadjust
            n_zbins = len(bins[2]) + flowadjust
            h2D_dict = {}
            
            tmp_h2D_list = myhyperdim.Get2DHistos(pidhd_mctot.Clone(),False)
            pid_histdict = {}

            for i in range(1,11):
                tmp_hist = tmp_h2D_list[i].Clone()
                tmp_hist.Scale(1.0,"width")
                # tmp_hist.RebinY(2)
                # tmp_hist.SetFillColor(bin_pid_colors[i])
                # tmp_hist.SetLineColor(ROOT.TColor.GetColorDark(bin_pid_colors[i]))
                pid_histdict[bin_pid_particle[i]] = tmp_hist
            # data.RebinY(2)
            plot_histdict = {
                "data": data.Clone(),
                "proton": pid_histdict["proton"].Clone(),
            }
            plot_histdict["pipm"] = pid_histdict["piplus"].Clone("%s_%s"%(pid2d_mctot.GetName().replace("h2D", "h"), "pipm"))
            plot_histdict["pipm"].Add(pid_histdict["piminus"])
            plot_histdict["pipm"].Add(pid_histdict["pizero"])
            plot_histdict["other"] = pid_histdict["other"].Clone()
            for part in pid_histdict:
                if part in ["pipm", "piminus", "piplus","proton","pizero", "other","data"]:
                    continue
                plot_histdict["other"].Add(pid_histdict[part])
            plot_histdict["proton"].GetXaxis().SetNdivisions(505)
            plot_histdict["proton"].GetXaxis().SetNdivisions(505)
            plot_histdict["proton"].GetXaxis().SetTitle("Q^{2}_{QE} [(GeV/c)^{2}]")
            plot_histdict["proton"].GetYaxis().SetTitle("Proton score")
            plot_histdict["proton"].GetXaxis().CenterTitle()
            plot_histdict["proton"].GetYaxis().CenterTitle()
            plot_histdict["proton"].SetLineColor(ROOT.kBlue)
            plot_histdict["pipm"].SetLineColor(ROOT.kRed)

            tot = plot_histdict["proton"].Clone(plot_histdict["proton"].GetName().replace("proton","total"))
            tot.Add(plot_histdict["pipm"])

            proton_ratio = plot_histdict["proton"].Clone(plot_histdict["proton"].GetName()+"_ratio")
            proton_ratio.Divide(proton_ratio,tot, 1., 1.)

            pipm_ratio = plot_histdict["pipm"].Clone(plot_histdict["pipm"].GetName()+"_ratio")
            pipm_ratio.Divide(pipm_ratio,tot, 1., 1.)

            proton_ratio.SetTitle("Ratio of proton and pion event rates")

            canvas_name = "canvas_%s_%s_%s"%(b_sample, c_var, tunedtag)
            canvas2d = ROOT.TCanvas(canvas_name, canvas_name, 900,3200)
            if x_var in ["Q2QE"]: canvas2d.SetLogx()
            if y_var in ["Q2QE"]: canvas2d.SetLogy()
            plotmax = 1.05*max(proton_ratio.GetMaximum(), pipm_ratio.GetMaximum())
            # print(plotmax)
            proton_ratio.SetMaximum(1.0)

            ROOT.gStyle.SetPaintTextFormat("0.2f")
            proton_ratio.SetMarkerSize(0.75)
            proton_ratio.Draw("Colz text")
            # pipm_ratio.Draw("Box same")
            # proton_ratio.Draw("axis same")

            plot_outfilename = "protonscore2D_%s_%s_%s.pdf"%(b_sample,c_var,tunedtag)
            canvas2d.Print(os.path.join(outdirname,plot_outfilename))
            if thesisplotdir != "":
                canvas2d.Print(os.path.join(thesisplotdir,plot_outfilename))
            canvas2d.SetLogx(0)
            canvas2d.SetLogy(0)

            # Now do the 2D cumulative hist
            n_xbins = plot_histdict["proton"].GetNbinsX()
            n_ybins = plot_histdict["proton"].GetNbinsY()
            projdict = {}
            cumuldict = {}
            global_max = 0.0


            gc2 = PanelCanvas("gridcanvas_%s_%s_cumul"%(b_sample,c_var), n_ybins, n_xbins)
            gc2.Draw()
            for projbin in range(1, n_xbins+1):
                projdict[projbin] = {}
                cumuldict[projbin] = {}

                loedge = plot_histdict["proton"].GetXaxis().GetBinLowEdge(projbin)
                upedge = plot_histdict["proton"].GetXaxis().GetBinUpEdge(projbin)
                range_string = "{min} < {var} < {max}".format(
                    min = round(loedge,4), 
                    var = "Q^{2}_{QE} #lower[-0.25]{#scale[0.6]{[(GeV/c)^{2}]}}", 
                    max = round(upedge,4)
                )
                projdict[projbin]["mctot"] = {}
                first_part = True
                for part in ["other", "pipm", "proton","data"]:
                    projname = "%s_projY%s"%(plot_histdict[part].GetName(), str(projbin))
                    tmp_proj = plot_histdict[part].ProjectionY(projname, projbin, projbin)
                    tmp_proj.Scale(1/(upedge - loedge))

                    # tmp_proj.SetFillStyle(0)
                    projdict[projbin][part] = tmp_proj
                    
                    if part == "data": 
                        tmp_proj.SetMarkerStyle(20)
                        tmp_proj.SetMarkerSize(data_marker_size)
                        tmp_proj.SetLineColor(ROOT.kBlack)
                        tmp_proj.SetMarkerColor(ROOT.kBlack)
                        if tmp_proj.GetMaximum()>global_max: 
                            global_max = tmp_proj.GetMaximum()
                        continue
                    tmp_proj.SetLineColor(ROOT.TColor.GetColorDark(part_colors[part]))
                    tmp_proj.SetFillColor(part_colors[part])
                    tmp_proj.SetLineWidth(2)
                    if first_part:
                        projdict[projbin]["mctot"] = tmp_proj.Clone("%s_%s"%(tmp_proj.GetName(),"mctot"))
                        first_part = False
                        # projdict[projbin]["stack"].Add(tmp_proj)        
                    else:
                        projdict[projbin]["mctot"].Add(tmp_proj)

                    tmp_cumul = tmp_proj.GetCumulative(False)
                    tmp_cumul.SetLineColor(part_colors[part])
                    tmp_cumul.SetLineWidth(2)
                    tmp_cumul.SetFillStyle(0)
                    cumuldict[projbin][part] = tmp_cumul
                if projdict[projbin]["mctot"].GetMaximum() > global_max: 
                    global_max = projdict[projbin]["stack"].GetMaximum()
                # cumuldict[projbin]["pipm"].Add(cumuldict[projbin]["other"])
                cumul_sum = cumuldict[projbin]["proton"].Clone()
                cumul_sum.Add(cumuldict[projbin]["pipm"])
                # cumul_sum.Add(cumuldict[projbin]["other"])
                
                for part in cumuldict[projbin]:
                    # cumuldict[projbin][part].Divide(cumuldict[projbin][part], cumul_sum, 1.0, 1.0)
                    cumuldict[projbin][part].Scale(1.0/cumuldict[projbin][part].GetBinContent(1))
                cumul_integral = cumul_sum.GetBinContent(1)
                cumul_sum.Scale(1.0/cumul_integral)
                cumul_sum.SetLineColor(ROOT.kP10Gray)

                cumuldict[projbin]["total"] = cumul_sum
                cumuldict[projbin]["pipm"].GetXaxis().SetTitle("Proton Score")
                cumuldict[projbin]["pipm"].GetXaxis().SetTitle("Cumulative")
                cumuldict[projbin]["pipm"].SetMaximum(1.2)
                cumuldict[projbin]["pipm"].SetMinimum(0.0)
                cumuldict[projbin]["pipm"].GetXaxis().SetNdivisions(505)
                cumuldict[projbin]["pipm"].GetYaxis().SetNdivisions(507)

                pad = gc2.cd(projbin)
                pad.SetGrid()
                pad.Draw()
                cumuldict[projbin]["pipm"].Draw("AXIS")
                cumuldict[projbin]["pipm"].Draw("AXIG same")
                # cumuldict[projbin]["other"].Draw("HIST same")
                cumul_sum.Draw("HIST same")
                cumuldict[projbin]["pipm"].Draw("HIST same")
                cumuldict[projbin]["proton"].Draw("HIST same")
                # cumuldict[projbin]["pipm"].Draw("AXIG same")

                binrange_latex = ROOT.TLatex()
                binrange_latex.SetTextAlign(33) # top right
                binrange_latex.SetNDC()
                binrange_latex.SetTextFont(42)
                binrange_latex.SetTextSize(0.02)
                binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)

            gc2.SetYTitle("Cumultive fraction")
            gc2.SetXTitle("Proton Score")
            gc2.SetHistTexts()
            gc2.Draw()

            cumul_outfilename = "cumulativepanel_"+plot_outfilename
            gc2.Print(os.path.join(outdirname,cumul_outfilename))
            if thesisplotdir != "":
                gc2.Print(os.path.join(thesisplotdir,cumul_outfilename))

            # Now make the non cumulative stacked panel plot:
            gc2.ResetPads()
            gc2.Modified()
            gc2.Update()

            # gc3 = PanelCanvas("gridcanvas_%s_%s_panel"%(b_sample,c_var), n_ybins, n_xbins)
            # gc3.Draw()
            for projbin in projdict:
                pad = gc2.cd(projbin)
                pad.Draw()
                loedge = plot_histdict["proton"].GetXaxis().GetBinLowEdge(projbin)
                upedge = plot_histdict["proton"].GetXaxis().GetBinUpEdge(projbin)

                projdict[projbin]["data"].GetXaxis().SetNdivisions(505)
                projdict[projbin]["data"].GetYaxis().SetNdivisions(505)
                projdict[projbin]["data"].SetMinimum(0.0)

                tmp_pad_scale = 1.0
                tmp_pad_max = max(projdict[projbin]["data"].GetMaximum(), projdict[projbin]["mctot"].GetMaximum())
                if global_max != 0.0:
                    if tmp_pad_max < global_max and tmp_pad_max > 0.0:
                        tmp_pad_scale = round(global_max / tmp_pad_max, 3)
                        print(tmp_pad_max, tmp_pad_scale)
                for part in projdict[projbin]:
                    projdict[projbin][part].Scale(tmp_pad_scale)
                projdict[projbin]["stack"] = THStack()
                for part in ["other","pipm","proton"]:
                    projdict[projbin]["stack"].Add(projdict[projbin][part])
                
                projdict[projbin]["data"].SetMaximum(
                    1.2*max(projdict[projbin]["data"].GetMaximum(), projdict[projbin]["stack"].GetMaximum())
                )
                
                range_string = "{min} < {var} < {max}".format(
                    min = round(loedge,4), 
                    var = "Q^{2}_{QE} #lower[-0.25]{#scale[0.6]{[(GeV/c)^{2}]}}", 
                    max = round(upedge,4)
                )
                projdict[projbin]["rangestring"] = range_string

                projdict[projbin]["scalestring"] = "#times {:g}".format(float('{:.{p}g}'.format(tmp_pad_scale, p=2)))


            for projbin in projdict:
                pad = gc2.cd(projbin)
                pad.Draw()

                projdict[projbin]["data"].Draw("axis")
                projdict[projbin]["stack"].Draw("HIST same")
                projdict[projbin]["data"].Draw("E1 E0 X0 same")


                binrange_latex = ROOT.TLatex()
                binrange_latex.SetTextAlign(33) # top right
                binrange_latex.SetNDC()
                binrange_latex.SetTextFont(42)
                binrange_latex.SetTextSize(0.02)
                binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),projdict[projbin]["rangestring"])

                multip_latex = ROOT.TLatex()
                multip_latex.SetTextAlign(32)
                multip_latex.SetNDC()
                multip_latex.SetTextFont(52)
                multip_latex.SetTextSize(0.03)
                multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.052),projdict[projbin]["scalestring"])


            gc2.SetYTitle("N_{events} / (GeV/c)^{2} / Score")
            gc2.SetXTitle("Proton Score")

            gc2.SetHistTexts()
            gc2.Draw()

            panel_outfilename = "panel_"+plot_outfilename
            gc2.Print(os.path.join(outdirname,panel_outfilename))
            if thesisplotdir != "":
                gc2.Print(os.path.join(thesisplotdir,panel_outfilename))


                

                










                

        
