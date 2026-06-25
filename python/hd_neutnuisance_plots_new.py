# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023


# from re import L
import sys, os
import ROOT
ROOT.gROOT.SetBatch(True) # Run in batch mode
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
global_noData = True    # use this to plot MC only types
noData = global_noData  # dummy bc dumb
dotypes = True          # use this if ou want to do by types
dotuned= False           # use this if you have tuned hists
doratio = True          # use this if you want to include a data/mc ratio
# projY = True
sig_only = True
do_data = False

ROOT.TH1.AddDirectory(ROOT.kFALSE)

legendfontsize = 0.042

# _xsize = 1100.0
# _ysize = 720.0
_xsize = 2000
_ysize = 1500

latex_x = 0.72
latex_y = 0.53


data_marker_style = 20
data_marker_size = 2.0
data_marker_size2d = 1.5
end_error_size = 10.0
typeslinewidth = 1
typeslinewidth1D = 1
bkgfillstyle = 3244

ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer


def GetHistDict(i_file, POTScale):
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
        types = parse[4]
        if sample not in samplestodo:
            print("skipping hist not in samplestodo %s"%name)
            continue
        if "reconstructed" not in types:
            continue
        if "simulfit" in types:
            continue
        if "tuned" not in types and dotuned and cat!="data":
            continue
        if "tuned" in types and not dotuned:
            continue
        if cat not in catstodo: 
            continue
        if hist == "h":
            continue
        if hist != "hHD" and cat != "data": # and (not dotypes):
            continue
        # if hist != "h2D": # and dotypes:
        #     continue
        if cat == "data" and hist != "h2D":
            continue
        flag = "reconstructed_types_"
        if "tuned" in types:
            flag = "reconstructed_tuned_types_"
        index = 0
        if "types" in types:
            if not dotypes:
                continue
            tmp_index = int(parse[4].replace(flag,""))
            if tmp_index == 0:
                print("Skipping hist of types0 %s"%name)
                continue
            index = tmp_index
        if hist == "hHD":
            if len(variable.split("_")) == 3:
                tmp_xvar = variable.split("_")[0]
                tmp_yvar = variable.split("_")[1]
                tmp_zvar = variable.split("_")[2]
                if tmp_zvar != "NeutCandsTopMCPID" and "NeutCandTopMCPID" not in tmp_zvar:
                    continue
                # Add to list to loop over later
                if variable not in varsHDtodo:
                    varsHDtodo.append(variable)
                # Add to list to check later if there's a 1D data that exists
                if "%s_%s"%(tmp_xvar,tmp_yvar) not in vars2Dtodo:
                    vars2Dtodo.append("%s_%s"%(tmp_xvar,tmp_yvar))
            else:
                print("Skipping variable that isn't formatted properly: ", variable)
                continue
        if hist == "h2D":# and dotypes:
            if len(variable.split("_")) == 2:
                if variable not in vars2Dtodo:
                    vars2Dtodo.append(variable)
            else:
                print("Skipping variable that isn't formatted properly: ", variable)
                continue
        
        h = f.Get(name).Clone()
        if h.GetEntries() <= 0 and index not in [1,2,3,4,8]: 
        # if h.GetEntries() <= 0 and index not in [1,2,3,8]: 
            print("Skipping hist %s because it has no entries"%name)
            # h.Print()
            continue
        if cat in backgrounds and index != 0:
            index += 10
        if sample not in groups.keys():
            groups[sample] = {}
        if variable not in groups[sample].keys():
            groups[sample][variable] = {}
        if cat not in groups[sample][variable].keys():
            groups[sample][variable][cat] = {}
        if index not in groups[sample][variable][cat]:
            groups[sample][variable][cat][index] = {}
        print("%s %s %s"%(sample, variable, cat))
        if "data" in cat:
            h.SetMarkerColor(ROOT.kBlack)
            h.SetLineColor(ROOT.kBlack)
            h.SetMarkerStyle(data_marker_style)
            h.SetMarkerSize(data_marker_size)
        else:
            # print("scaling MC hist %s with potscale of "%name, POTScale)
            h.Scale(POTScale)
            h.SetFillColor(catscolors[cat])
            if index != 0:
                h.SetFillColor(catscolors[index])
            h.SetLineColor(ROOT.kBlack)
            h.SetLineWidth(typeslinewidth)
            if cat in backgrounds:
                h.SetFillStyle(bkgfillstyle)
        # print("Found and using hist %s"%name)
        groups[sample][variable][cat][index] = h

    # print("Making total MC and total background now")
    if "qelikenot" not in backgrounds:
        print("Combining backgrounds for a total background")
        for a_sample in groups:
            for b_var in groups[a_sample]:
                if len(b_var.split("_")) != 3: continue
                if "qelikenot" in groups[a_sample][b_var]:
                    print("Found a qelikenot already")
                    continue
                groups[a_sample][b_var]["qelikenot"] = {}
                for itype in groups[a_sample][b_var][backgrounds[0]]:
                    tmp_qelikenot_name = groups[a_sample][b_var][backgrounds[0]][itype].GetName().replace(backgrounds[0],"qelikenot")
                    tmp_qelikenot_hist = groups[a_sample][b_var][backgrounds[0]][itype].Clone(tmp_qelikenot_name)
                    # print(backgrounds[0])
                    for c_cat in backgrounds[1:]:
                        if c_cat in ["data","mctot","qelike","qelikenot"]: continue
                        if c_cat not in catstodo: continue
                        # print(c_cat)
                        tmp_qelikenot_hist.Add(groups[a_sample][b_var][c_cat][itype])
                    groups[a_sample][b_var]["qelikenot"][itype] = tmp_qelikenot_hist.Clone()
        backgrounds.append("qelikenot")
    print("Making a total MC histogram")
    for a_sample in groups:
        for b_var in groups[a_sample]:
            if len(b_var.split("_")) != 3: continue
            if "mctot" in groups[a_sample][b_var]:
                print("Found a mctot already")
                continue
            groups[a_sample][b_var]["mctot"] = {}
            mctot_name = groups[a_sample][b_var]["qelike"][0].GetName().replace("qelike","mctot")
            tmp_mctot_hist = groups[a_sample][b_var]["qelike"][0].Clone(mctot_name)
            for cat in groups[a_sample][b_var]:
                if cat in ["data","qelike","qelikenot","mctot",]:
                    continue
                tmp_mctot_hist.Add(groups[a_sample][b_var][cat][0])
            groups[a_sample][b_var]["mctot"][0] = tmp_mctot_hist.Clone()

    print("Finished making hist dict")
    return groups        


def GetHDBinning(i_file, varHD_name):
    bins = []
    if "varsFile" in i_file.GetListOfKeys():
        bigvarconfig_string = i_file.Get("varsFile").GetTitle()
    else:
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
    if "varsFile" in i_file.GetListOfKeys():
        bigvarconfig_string = i_file.Get("varsFile").GetTitle()
    else:
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
        os.mkdir(plotdir)
    if subdir == "":
        return plotdir
    if not os.path.exists(os.path.join(plotdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(plotdir, subdir))
        os.mkdir(os.path.join(plotdir, subdir))
    return os.path.join(plotdir, subdir)

def PanelCanvas(name, n_xbins, n_ybins, x_size=2000, y_size=1500):
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
        print("I'm doing it mr krabs")
    print("HyperDPanelCanvas: Making a grid canvas named "+name+" with a grid of ",n_xbins,"    ",n_ybins,"    ",grid_x,"    ",grid_y)

    # gc2 = PlotUtils.GridCanvas(name, grid_x, grid_y, x_size, y_size)
    # gc2 = GridCanvas(name, grid_x, grid_y, x_size, y_size)
    gc2 = GridCanvas(name, grid_x, grid_y, x_size, y_size)
    # gc2.SetRightMargin(0.05)
    # gc2.SetLeftMargin(0.05)
    gc2.SetInterpadSpace(0.0)
    gc2.ResetPads()

    return gc2


def CCQECanvas(name, title, xsize=1800, ysize=1200):
    c2 = ROOT.TCanvas(name, title, xsize, ysize)
    # c2.SetLeftMargin(0.1)
    c2.SetRightMargin(0.15)
    c2.SetLeftMargin(0.11)
    c2.SetTopMargin(0.1)
    c2.SetBottomMargin(0.1)
    return c2

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

catstodo = [
    "data",
    "qelike",
    "chargedpion",
    "neutralpion",
    "other",
    # "multipion",
    # "other_np",
]


catscolors = {
    "data": ROOT.kBlack,
    # "qelike": ROOT.kBlue - 6,
    # "qelikenot": ROOT.kRed - 6,
    # "qelike_old": ROOT.kBlue - 6,
    # "qelikenot_old": ROOT.kRed - 6,
    # "chargedpion": ROOT.kMagenta - 6,
    # "neutralpion": ROOT.kRed - 6,
    # "multipion": ROOT.kGreen - 6,
    # "other": ROOT.kYellow - 6,
    "qelike":       ROOT.kP10Blue,
    "chargedpion":  ROOT.kP10Yellow,
    "neutralpion":  ROOT.kP10Orange,
    "multipion":    ROOT.kP10Violet,
    "other":        ROOT.kP10Ash,
    "other_np":     ROOT.kP10Ash,
    "mctot":        ROOT.kP10Red,
    0:              ROOT.kP8Red,     # total mc
    1:              ROOT.kP8Blue,    # QE
    2:              ROOT.kP8Orange,  # RES
    3:              ROOT.kP8Pink,    # DIS
    4:              ROOT.kP8Green,   # COH
    8:              ROOT.kP8Azure,   # 2p2h
    11:             ROOT.kP8Blue,    # "Bkg QE"
    12:             ROOT.kP8Orange,  # "Bkg RES",
    13:             ROOT.kP8Pink,    # "Bkg DIS",
    14:             ROOT.kP8Green,   # "Bkg COH",
    18:             ROOT.kP8Azure,   # "Bkg 2p2h",
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
    "NeutCandsMuonCosTheta": "cos #Delta #theta_{#mu}",
    "NeutCandsTrackEndDist": "d_{track}",
    "ptmu": "p_{T}",
    "EAvail": "E_{Avail}",
    "recoil": "recoil",
    "pzmu": "p_{||}",
}


samplestodo = [
    "QElike",
    "TrackSideband",
    "BlobSideband",
    # "QElike_old"
    # "QElike0Blob",
    # "QElike1Blob",
    # "QElike2Blob"
]
vars_info = {
    "NeutCandsEdep": {
        "title": "Cluster E_{dep}",
        "shortname": "E_{dep}",
        "units": "MeV",
        "bins": [],
    },
    "NeutCandsMuonCosTheta": {
        "title": "Cluster cos(#Delta#theta_{#mu})",
        "shortname": "cos(#Delta#theta_{#mu})",
        "units": "",
        "bins": [],
    },
    "NeutCandsvtxSphereDist" : {
        "title": "Cluster d_{vtx}",
        "shortname": "d_{vtx}",
        "units": "mm",
        "bins": [],
    },
    "NeutCandsTrackEndDist": {
        "title": "Cluster d_{track end}",
        "shortname": "d_{track}",
        "units": "mm",
        "bins": [],
    },
    "recoil": {
        "title": "recoil",
        "units": "GeV",
        "bins": [],
    },
}
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
    9: "Non-GENIE", # "No Top",
    10: "Other",
}
bin_pid_mechname = {
    1: "neutron",
    2: "proton",
    3: "pizero",
    # 4: "piplus",
    # 5: "piminus",
    4: "pipm",
    5: "pipm",
    6: "gamma",
    7: "electron",
    8: "muon",
    9: "notop",
    10: "other",
}

10
bin_pid_names = {   
    "neutron": "n",
    "proton": "p",
    "pizero": "#pi^{0}",
    "piplus": "#pi^{+}",
    "piminus": "#pi^{-}",
    "pipm": "#pi^{#pm}",
    "gamma": "#gamma",
    "electron": "e^{#pm}",
    "muon": "#mu^{#pm}",
    "notop": "Non-GENIE",
    "other": "Other",
}
bin_pid_colors = {
    1: ROOT.kP10Blue,
    2: ROOT.kP10Yellow,
    3: ROOT.kP10Green,
    # 4: ROOT.kP10Ash, # decided to combine pi+ (4) with pi- (5)
    4: ROOT.kP10Orange,
    5: ROOT.kP10Orange,
    6: ROOT.kP10Violet,
    7: ROOT.kP10Cyan,
    8: ROOT.kP10Red,
    9: ROOT.kP10Brown,
    10: ROOT.kP10Gray,
}

# bin_pid_order = list([10, 7, 6, 5, 4, 3, 8, 2, 1])
# decided to combine pi+ (4) with pi- (5)
bin_pid_order = [
    10, 
    9, 
    7, 
    6, 
    5, 
    3, 
    8, 
    2, 
    1
]

sigremoval = [7,6,5,4,3]

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

plotdir = MakePlotDir("neutnuisancePlotsHD")
dirname = filename.replace(".root", "_neutnuisanceplots")
for cat in catstodo:
    dirname += "_" + cat
# outfilename=filebasename1.replace(".root","_2DPlots")
outdirname = os.path.join(plotdir, dirname)
if not os.path.exists(outdirname):
    print(outdirname)
    os.mkdir(outdirname)

if ("potscaled_combined_" in filename):
    POTScale = 1.0
else:
    h_pot = f.Get("POT_summary")
    dataPOT = h_pot.GetBinContent(1)
    mcPOTprescaled = h_pot.GetBinContent(2)
    POTScale = dataPOT / mcPOTprescaled
print("POTScale: ", POTScale)

groups = {}
scaleX = ["Q2QE","NeutCandsEdep"]
groups = GetHistDict(f, POTScale)

if not noData:
    cat_order = list(["qelikenot", "qelike", "data"])
else:
    cat_order = list(["qelikenot","qelike"])

ROOT.gStyle.SetOptStat(0)
# template = "%s___%s___%s___%s"

for a_sample in groups.keys():
    # # for b_var in groups[a_sample].keys():
    # if "_Tuned" in a_sample:
    #     dotuned = True
    #     tunedname = a_sample.replace("_Tuned", "")
    # else:
    #     dotuned = False
    # data_sample_name = a_sample
    tmp_canvas_basename = "%s"%(a_sample)
    # tmp_canvas_basetitle = "%s %s %s"%()
    pdf_canvas_name = "gl_"+tmp_canvas_basename+"_neuthd"
    dummy_canvas = ROOT.TCanvas(pdf_canvas_name,pdf_canvas_name,_xsize,_ysize)
    dummy_canvas.SetCanvasSize(_xsize,_ysize)
    dummy_canvas.Print(os.path.join(outdirname,pdf_canvas_name+".pdf")+"[","pdf")
    for b_var in varsHDtodo:
        if b_var not in groups[a_sample].keys():
            continue
        noData = global_noData
        data_var = b_var.replace("_%s"% b_var.split("_")[2], "")
        print(data_var)
        if data_var not in vars2Dtodo:
            print("bad data_var", data_var, " skipping data for HD var ", b_var)
            noData = True
        
        if data_var not in groups[a_sample].keys() and not noData:
            print("Couldn't find data_var. Skipping", b_var)
            continue        
        
        # if not noData:
        #     if dotuned:
        #         data_sample_name = tunedname
        #     if data_var not in groups[data_sample_name].keys():
        #         print("Couldn't find data_var. Skipping", b_var)
        #         # noData = True
        #         continue
        #     else:
        #         data = groups[data_sample_name][data_var]["data"].Clone()
        #         data.SetMarkerColor(ROOT.kBlack)
        #         data.SetLineColor(ROOT.kBlack)

        bins = GetHDBinning(f,b_var)
        analysistype = GetHDAnalysisType(f,b_var)
        flowadjust = 1
        new_bin_pid_order = bin_pid_order
        new_sigremoval = sigremoval
        if sig_only:
            new_bin_pid_order = []
            for pid in bin_pid_order:
                if pid not in sigremoval: new_bin_pid_order.append(pid)
                # [pid in bin_pid_order if pid not in sigremoval]

        if analysistype in [0,1]:
            flowadjust = 1
        elif analysistype in [2,3]:
            flowadjust = -1
            new_bin_pid_order = [pid-1 for pid in bin_pid_order]
            new_sigremoval = [pid -1 for pid in sigremoval]
        print(analysistype)
        print(bins)
        myhyperdim = HyperDimLinearizer(bins, analysistype)

        n_xbins = len(bins[0]) + flowadjust
        n_ybins = len(bins[1]) + flowadjust
        n_zbins = len(bins[2]) + flowadjust

        tmp_data = groups[a_sample][data_var]["data"][0].Clone()
        h2D_dict = {"data":{"data":tmp_data}}

        for c_cat in ["qelike", "qelikenot","mctot"]:
            print(c_cat)
            # print(groups[a_sample][b_var][c_cat][0])
            tmp_hHD = groups[a_sample][b_var][c_cat][0].Clone()
            tmp_h2D_list = myhyperdim.Get2DHistos(tmp_hHD,IncludeSysBool)
            if n_zbins != len(tmp_h2D_list):
                print("ERROR: number of bins counted does not match those given by hyperdimlin")
                print("\t nz_bins %f\t len(tmp_h2D_list) %f"%(nz_bins,len(tmp_h2D_list)))
                tmp_hHD.Print()
                sys.error(1)
            for zbin in new_bin_pid_order:
                partname = bin_pid_mechname[zbin]
                if c_cat not in h2D_dict:
                    h2D_dict[c_cat] = {}
                if partname not in h2D_dict[c_cat].keys():
                    h2D_dict[c_cat][partname] = {}
                if sig_only and zbin in new_sigremoval:
                    tmp_h2D_list[10].Add(tmp_h2D_list[zbin])
                    continue
                if zbin == 5:
                    tmp_h2D_list[zbin].Add(tmp_h2D_list[4])                    
                tmp_h2D_list[zbin].SetFillColor(bin_pid_colors[zbin])
                tmp_h2D_list[zbin].SetLineColor(ROOT.kBlack)
                tmp_h2D_list[zbin].SetLineWidth(typeslinewidth)
                if c_cat == "qelikenot":
                    tmp_h2D_list[zbin].SetFillStyle(3244)
                else:
                    tmp_h2D_list[zbin].SetFillStyle(1001)
                h2D_dict[c_cat][partname] = tmp_h2D_list[zbin].Clone("%s_%s"%(tmp_h2D_list[zbin].GetName(),partname))
        first = True
        tmp_mctot = MnvH1D()
        for part in h2D_dict["mctot"]:
            if first:
                tmp_mctot = h2D_dict["mctot"][part].Clone()
                first = False
                continue
            tmp_mctot.Add(h2D_dict["mctot"][part])
        h2D_dict["mctot"]["mctot"] = tmp_mctot.Clone()
        tmp_qeliketot = MnvH1D()
        first = True
        for part in h2D_dict["qelike"]:
            if first:
                tmp_qeliketot = h2D_dict["qelike"][part].Clone()
                first = False
                continue
            tmp_qeliketot.Add(h2D_dict["qelike"][part])
        h2D_dict["qelike"]["qeliketot"] = tmp_qeliketot.Clone()
        
        for proj in ["projX", "projY"]:
            proj_bin_range = []
            n_projbins_raw = 0
            if proj == "projY":
                n_projbins_raw = n_xbins
                tmp_projaxis_bins = bins[0]
                tmp_projvar = b_var.split("_")[0]
                tmp_axisvar = b_var.split("_")[1]
            else:
                n_projbins_raw = n_ybins
                tmp_projaxis_bins = bins[1]
                tmp_projvar = b_var.split("_")[1]
                tmp_axisvar = b_var.split("_")[0]
            
            tmp_projvar_shortname = vars_info[tmp_projvar]["shortname"]
            tmp_axisvar_shortname = vars_info[tmp_axisvar]["shortname"]
            tmp_axisvar_units = vars_info[tmp_axisvar]["units"]
            proj_bin_range = range(1,n_projbins_raw-1)

            grid_dict = {}
            for projbin in proj_bin_range:
                if projbin not in grid_dict:
                    grid_dict[projbin] = {}
                for cat in h2D_dict:
                    if cat not in grid_dict[projbin]:
                        grid_dict[projbin][cat] = {}
                    for part in h2D_dict[cat]:
                        if part not in grid_dict[projbin][cat]:
                            grid_dict[projbin][cat][part] = {}
                        tmp_hist2D = h2D_dict[cat][part].Clone()
                        tmp_proj = MnvH1D()
                        if proj == "projY":
                            tmp_proj_name ="%s_projY_%0.3d"%(tmp_hist2D.GetName().replace("hHD","h"),projbin)
                            width = tmp_hist2D.GetXaxis().GetBinWidth(projbin)
                            tmp_proj = tmp_hist2D.ProjectionY(tmp_proj_name, projbin, projbin)
                        if proj == "projX":
                            tmp_proj_name ="%s_projX_%0.3d"%(tmp_hist2D.GetName().replace("hHD","h"),projbin)
                            width = tmp_hist2D.GetYaxis().GetBinWidth(projbin)
                            tmp_proj = tmp_hist2D.ProjectionX(tmp_proj_name, projbin, projbin)
                        # tmp_proj.Scale(1./width,"width")
                        tmp_proj.Scale(1.,"width")
                        if cat != "qelike":
                            tmp_proj.SetFillStyle(bkgfillstyle)
                        grid_dict[projbin][cat][part] = tmp_proj.Clone()

            global_max = 0.0
            datamax = 0.0
            print(grid_dict[projbin]["qelike"]["qeliketot"])
            mcmax = max([grid_dict[projbin]["qelike"]["qeliketot"].GetMaximum() for projbin in grid_dict])
            if not sig_only:
                if do_data:
                    datamax = max([grid_dict[projbin]["data"]["data"].GetMaximum() for projbin in grid_dict])
                mcmax = max([grid_dict[projbin]["mctot"]["mctot"].GetMaximum() for projbin in grid_dict])
            global_max = max(datamax, mcmax)
            multipliers = []
            for projbin in grid_dict:
                tmp_pad_max = 0.0
                tmp_pad_scale = 1.0
                if do_data:
                    tmp_datamax = grid_dict[projbin]["data"]["data"].GetMaximum()
                    tmp_mcmax = grid_dict[projbin]["mctot"]["mctot"].GetMaximum()
                    tmp_pad_max = max(tmp_datamax,tmp_mcmax)
                if sig_only:
                    tmp_pad_max = grid_dict[projbin]["qelike"]["qeliketot"].GetMaximum()
                if tmp_pad_max == 0.0:
                    tmp_pad_max = global_max
                tmp_pad_scale = eval('{:.{p}g}'.format(round(global_max / tmp_pad_max), p=2))
                multipliers.append(tmp_pad_scale)

                for cat in grid_dict[projbin]:
                    for part in grid_dict[projbin][cat]:
                        grid_dict[projbin][cat][part].Scale(tmp_pad_scale)
                        # grid_dict[projbin][cat][part].SetMaximum(1.2 * global_max)
                grid_dict[projbin]["data"]["data"].SetMaximum(1.4 * global_max)
                grid_dict[projbin]["data"]["data"].SetMinimum(0)
                grid_dict[projbin]["data"]["data"].GetXaxis().SetNdivisions(505)
                grid_dict[projbin]["data"]["data"].GetYaxis().SetNdivisions(505)
                
                tmp_stack = THStack("stack","")

                for cat in ["qelikenot", "qelike"]:
                    for pid in new_bin_pid_order:
                        tmp_hist = grid_dict[projbin][cat][bin_pid_mechname[pid]].Clone()
                        if cat != "qelike":
                            if sig_only: continue
                            tmp_hist.SetFillStyle(bkgfillstyle)
                        tmp_stack.Add(tmp_hist)
                grid_dict[projbin]["stack"] = tmp_stack
            
            proj_nxbins = n_xbins - 2 
            proj_nybins = n_ybins - 2 
            if proj == "projY":
                proj_nxbins = n_ybins - 2 
                proj_nybins = n_xbins - 2 
            
            tmp_canvas_name = "%s_%s_%s_%s"%(a_sample, b_var, data_var, proj)
            tmp_canvas_title = "%s %s"%(data_var, proj)
            gc2 = PanelCanvas(tmp_canvas_name, proj_nxbins,proj_nybins)
            gc2.SetLeftMargin(0.1)
            gc2.SetRightMargin(0.05)
            gc2.SetBottomMargin(0.1)
            # gc2.SetFrameLineWidth(1)
            gc2.SetXTitle(tmp_axisvar_shortname)
            gc2.SetYTitle("Counts/%s"%(tmp_axisvar_units))
            gc2.SetTitleSize(1500*0.05)

            gc2.Draw()

            
            for i in proj_bin_range:
                pad = gc2.cd(i)
                pad.SetFrameLineWidth(1)
                pad.Draw()
                grid_dict[i]["data"]["data"].Draw("AXIS")
            for i in proj_bin_range:
                pad = gc2.cd(i)
                pad.Draw()
                grid_dict[i]["stack"].Draw("HIST same")
                if do_data:
                    grid_dict[i]["data"]["data"].Draw("E1 X0 SAME")
                    
                    # grid_dict[i]["data"]["data"].Draw("E1 X0 SAME")
                grid_dict[i]["data"]["data"].Draw("AXIS same")
            
                if data_var.split("_")[0] in scaleX and proj=="projX":
                    pad.SetLogx()
                if data_var.split("_")[1] in scaleX and proj=="projY":
                    pad.SetLogx()         

                mutlip_string = "#times {:g}".format(float('{:.{p}g}'.format(multipliers[i-1], p=2)))
                multip_latex = ROOT.TLatex()
                multip_latex.SetTextAlign(32)
                multip_latex.SetNDC()
                multip_latex.SetTextFont(52)
                multip_latex.SetTextSize(0.028)
                multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.05),mutlip_string)

                loedge = tmp_projaxis_bins[i-1]
                hiedge = tmp_projaxis_bins[i]
                tmp_projvar_shortname
                range_string = "{min} < {var} < {max}".format(min = round(loedge,2), var = tmp_projvar_shortname, max = round(hiedge,2))
                binrange_latex = ROOT.TLatex()
                binrange_latex.SetTextAlign(33) # top right
                binrange_latex.SetNDC()
                binrange_latex.SetTextFont(42)
                binrange_latex.SetTextSize(0.025)
                binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)
                pad.Modified()
                pad.Update()
            pad = gc2.cd(n_projbins_raw)
            pad.Draw()

            padwidth = 1 - pad.GetLeftMargin() - pad.GetRightMargin()
            x1 = pad.GetLeftMargin()+padwidth/20.0
            y1 = 1.-(pad.GetTopMargin())-0.01
            x2 = 1 - pad.GetRightMargin() + padwidth/20
            y2 = pad.GetBottomMargin()+0.01

            leg = TLegend(x1, y1, x2, y2)
            leg.SetBorderSize(0)
            leg.SetFillColor(-1)
            leg.SetTextSize(round(legendfontsize/3))
            leg.SetNColumns(2)

            if do_data:
                leg.AddEntry(grid_dict[1]["data"]["data"], "Data", "pe")
            if not sig_only:
                leg.AddEntry(0, "", "")
            for part in reversed(list(grid_dict[1]["qelike"])):
                if part == "qeliketot": continue
                leg.AddEntry(grid_dict[1]["qelike"][part], bin_pid_names[part], "fl")
                if sig_only: 
                    # leg.SetNColumns(1)
                    continue
                leg.AddEntry(grid_dict[1]["qelikenot"][part], "Bkg "+bin_pid_names[part], "fl")
            leg.Draw()
            pad.Modified()

            gc2.SetHistTexts()
            gc2.Draw()
            gc2.Print(os.path.join(outdirname,pdf_canvas_name+".pdf"),"Title:%s %s"%(tmp_canvas_title," Final States"))
            gc2.ResetPads()
            gc2.Modified()
            gc2.Update()
            del gc2

            


        # sys.exit(1)
        continue
        h2D_dict = {}
        for c_cat in cat_order:
            tmp_h2D_list = []
            if c_cat == "data":
                if noData:
                    continue
                print(data_sample_name, data_var, c_cat)
                # print(groups[data_sample_name].keys())
                data = groups[data_sample_name][data_var][c_cat].Clone()
                if -1 not in h2D_dict.keys():
                    h2D_dict[-1] = {}
                # h2D_dict[-1] = {"data":data}
                h2D_dict[-1] = {"data":data}
                continue
            hHD = groups[a_sample][b_var][c_cat].Clone()
            tmp_h2D_list = myhyperdim.Get2DHistos(hHD,IncludeSysBool)
            if n_zbins!= len(tmp_h2D_list):
                print("bins are wrong!!! You calculated ", n_zbins," zbins but there are ", len(tmp_h2D_list))
                sys.exit(1)
            # n_zbins = len(tmp_h2D_list)
            for zbin in new_bin_pid_order:
                # print ("adjusted pid ", zbin)
                if zbin not in h2D_dict.keys():
                    h2D_dict[zbin] = {}
                if c_cat not in h2D_dict[zbin].keys():
                    h2D_dict[zbin][c_cat] = {}

                h2D_dict[zbin][c_cat] = tmp_h2D_list[zbin]
                if analysistype in [0,1] and zbin == 5:
                    h2D_dict[zbin][c_cat].Add(tmp_h2D_list[zbin-1])
                if analysistype in [2,3] and zbin == 4:
                    h2D_dict[zbin][c_cat].Add(tmp_h2D_list[zbin-1])

        # h2D dict now has the 2D reco hists of the vars of interest for each pid

        proton_neutron_dict = {
            "proton": TH2D(),
            "muneut": TH2D(),
            "tot": TH2D(),
            "protonratio": TH2D(),
            "muneutratio": TH2D(),
        }
        firstcat = True
        for c_cat in cat_order:
            if c_cat == "data":
                continue
            if analysistype in [0,1]:
                if firstcat:
                    proton_neutron_dict["proton"] = h2D_dict[2][c_cat].Clone()
                    proton_neutron_dict["muneut"] = h2D_dict[1][c_cat].Clone()
                    proton_neutron_dict["muneut"].Add(h2D_dict[8][c_cat])
                    firstcat = False
                else:
                    proton_neutron_dict["proton"].Add(h2D_dict[2][c_cat])
                    proton_neutron_dict["muneut"].Add(h2D_dict[1][c_cat])
                    proton_neutron_dict["muneut"].Add(h2D_dict[8][c_cat])
            else:
                if firstcat:
                    proton_neutron_dict["proton"] = h2D_dict[1][c_cat].Clone()
                    proton_neutron_dict["muneut"] = h2D_dict[0][c_cat].Clone()
                    proton_neutron_dict["muneut"].Add(h2D_dict[7][c_cat])
                    firstcat = False
                else:
                    proton_neutron_dict["proton"].Add(h2D_dict[1][c_cat])
                    proton_neutron_dict["muneut"].Add(h2D_dict[0][c_cat])
                    proton_neutron_dict["muneut"].Add(h2D_dict[7][c_cat])
        # TODO figure out var names
        proton_neutron_dict["proton"].Scale(1.0, "width")
        proton_neutron_dict["muneut"].Scale(1.0, "width")
        xvar = b_var.split("_")[0]
        yvar = b_var.split("_")[1]
        xvarname = var_short_names[xvar]
        yvarname = var_short_names[yvar]
        proton_neutron_dict["proton"].SetLineColor(ROOT.kRed + 1)
        proton_neutron_dict["muneut"].SetLineColor(ROOT.kBlue + 2)
        proton_neutron_dict["proton"].GetXaxis().SetTitle(xvarname)
        proton_neutron_dict["muneut"].GetYaxis().SetTitle(yvarname)
        proton_neutron_dict["proton"].GetXaxis().CenterTitle()
        proton_neutron_dict["muneut"].GetYaxis().CenterTitle()

        proton_neutron_dict["total"] = proton_neutron_dict["proton"].Clone("total")
        proton_neutron_dict["total"].Add(proton_neutron_dict["muneut"])

        proton_neutron_dict["protonratio"] = proton_neutron_dict["proton"].Clone()
        proton_neutron_dict["protonratio"].Divide(
            proton_neutron_dict["protonratio"], proton_neutron_dict["total"],1.0,1.0
        )
        proton_neutron_dict["muneutratio"] = proton_neutron_dict["muneut"].Clone()
        proton_neutron_dict["muneutratio"].Divide(
            proton_neutron_dict["muneutratio"], proton_neutron_dict["total"], 1.0, 1.0
        )
        boxleg = CCQELegend(0.85,0.57,0.97,0.43)

        proton_neutron_dict["proton"].SetTitle(
            "Raw %s vs. %s in %s" % (yvarname, xvarname, a_sample)
        )
        proton_neutron_dict["protonratio"].SetTitle(
            "Ratio %s vs. %s in %s" % (yvarname, xvarname, a_sample)
        )

        dummyproton = proton_neutron_dict["proton"].Clone()
        dummyproton.SetFillColor(ROOT.kRed + 1)
        boxleg.AddEntry(dummyproton, "Proton", "f")
        dummymuneut = proton_neutron_dict["muneut"].Clone()
        dummymuneut.SetFillColor(ROOT.kBlue+2)
        boxleg.AddEntry(dummymuneut, "n, #mu", "f")

        rawcanvas = CCQECanvas(
            "BoxRaw_%s_%s_%s" % (a_sample, xvar, yvar),
            "%s vs. %s in %s" % (yvarname, xvarname, a_sample),
        )
        if xvar in ["NeutCandEdep", "NeutCandsEdep"]:
            rawcanvas.SetLogx()
        if yvar in ["NeutCandEdep", "NeutCandsEdep"]:
            rawcanvas.SetLogy()
        proton_neutron_dict["proton"].Draw("BOX")
        proton_neutron_dict["muneut"].Draw("BOX same")
        boxleg.Draw()
        thename = "BoxRaw_%s_%s_%s_%s" % ("raw", a_sample, xvar, yvar)

        canvas_name = thename + "_FinalStates"
        if dotuned:
            canvas_name = thename + "_FinalStates_tuned"
        rawcanvas.Print(os.path.join(outdirname, canvas_name + ".png"))

        if dotuned:
            canvas_name = thename + "_FinalStates_tuned"
        rawcanvas.Print(os.path.join(outdirname, canvas_name + ".png"))

        del rawcanvas

        ratiocanvas = CCQECanvas(
            "BoxRatio_%s_%s_%s" % (a_sample, xvar, yvar),
            "Ratio %s vs. %s in %s" % (yvarname, xvarname, a_sample),
        )
        if xvar in ["NeutCandEdep", "NeutCandsEdep"]:
            ratiocanvas.SetLogx()
        if yvar in ["NeutCandEdep", "NeutCandsEdep"]:
            ratiocanvas.SetLogy()
        proton_neutron_dict["protonratio"].Draw("BOX")
        proton_neutron_dict["muneutratio"].Draw("BOX same")
        boxleg.Draw()
        thename = "BoxRatio_%s_%s_%s" % (a_sample, yvarname, xvarname)

        canvas_name = thename + "_FinalStates"
        if dotuned:
            canvas_name = thename + "_FinalStates_tuned"
        ratiocanvas.Print(os.path.join(outdirname, canvas_name + ".png"))

        if dotuned:
            canvas_name = thename + "_FinalStates_tuned"
        ratiocanvas.Print(os.path.join(outdirname, canvas_name + ".png"))

        del ratiocanvas
    dummy_canvas.Print(os.path.join(outdirname,pdf_canvas_name+".pdf")+"]","pdf")


        
