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
# dotuned=False  # use this if you have tuned hists
doratio = True  # use this if you want to include a data/mc ratio
projY = True

ROOT.TH1.AddDirectory(ROOT.kFALSE)

legendfontsize = 0.042

_xsize = 1100.0
_ysize = 720.0

latex_x = 0.72
latex_y = 0.53


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
                        variable.split("_")[2].find("NeutCandTopMCPID") == -1
                        and variable.split("_")[2].find("NeutCandsTopMCPID") == -1
                    ):
                        print("Missing NeutCandTopMCPID in ", variable)
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


def GetHDBinning(i_file, varHD_name):
    bins = []

    bigvarconfig_string = i_file.Get("varsFile").GetTitle()
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
    bigvarconfig_string = i_file.Get("varsFile").GetTitle()
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
bin_pid_order = list([10, 9, 7, 6, 5, 3, 8, 2, 1]) 

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


h_pot = f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(2)
POTScale = dataPOT / mcPOTprescaled
print("POTScale: ", POTScale)

groups = {}
scaleX = ["Q2QE"]
groups = GetHistDict(f, POTScale)

if not noData:
    cat_order = list(["qelikenot", "qelike", "data"])
else:
    cat_order = list(["qelikenot","qelike"])

ROOT.gStyle.SetOptStat(0)
# template = "%s___%s___%s___%s"

for a_sample in groups.keys():

    # for b_var in groups[a_sample].keys():
    if "_Tuned" in a_sample:
        dotuned = True
        tunedname = a_sample.replace("_Tuned", "")
    else:
        dotuned = False
    data_sample_name = a_sample
    for b_var in varsHDtodo:
        if b_var not in groups[a_sample].keys():
            continue
        noData = global_noData
        data_var = b_var.split("_")[0]+"_"+b_var.split("_")[1]
        if data_var not in vars2Dtodo:
            print("bad data_var", data_var, " skipping data for HD var ", b_var)
            noData = True
        if not noData:
            # data_sample_name = a_sample
            if dotuned:
                data_sample_name = tunedname
            if data_var not in groups[data_sample_name].keys():
                print("Couldn't find data_var. Skipping", b_var)
                # noData = True
                continue
            else:
                data = groups[data_sample_name][data_var]["data"].Clone()
                data.SetMarkerColor(ROOT.kBlack)
                data.SetLineColor(ROOT.kBlack)

        bins = GetHDBinning(f,b_var)
        analysistype = GetHDAnalysisType(f,b_var)
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

        new_bin_pid_order = [-1] + new_bin_pid_order
        print("new_bin_pid_order with data", new_bin_pid_order)

        proj_bin_range = []
        n_projbins_raw = 0
        if projY:
            n_projbins_raw = n_xbins
        else:
            n_projbins_raw = n_ybins

        if analysistype in [0,1]:
            proj_bin_range = range(1,n_projbins_raw-1)
        if analysistype in [2,3]:
            proj_bin_range = range(0,n_projbins_raw)

        grid_dict = {}
        # for projbin in range(1,n_xbins):
        for projbin in proj_bin_range:
            if projbin not in grid_dict.keys():
                grid_dict[projbin] = {}
            # ystack = THStack("stack", "")
            tmp_mctot=TH1D()
            firstmc = True
            for c_cat in cat_order:
                for zbin in new_bin_pid_order:
                    if zbin == -1 and noData:
                        continue
                    # print("zbin", zbin)
                    if zbin not in grid_dict[projbin].keys():
                        grid_dict[projbin][zbin] = {}
                    if zbin == -1 and c_cat!="data":
                        continue
                    if zbin != -1 and c_cat == "data":
                        continue
                    tmp_hist2D = TH2D(h2D_dict[zbin][c_cat].Clone())
                    if projY:
                        tmp_proj_name ="projY_%0.3d"%projbin
                        width = tmp_hist2D.GetXaxis().GetBinWidth(projbin)
                        tmp_proj = tmp_hist2D.ProjectionY(tmp_proj_name, projbin, projbin)
                    else:
                        tmp_proj_name ="projX_%0.3d"%projbin
                        width = tmp_hist2D.GetYaxis().GetBinWidth(projbin)
                        tmp_proj = tmp_hist2D.ProjectionX(tmp_proj_name, projbin, projbin)

                    # print("pid", zbin)
                    tmp_proj = MakeHistPretty(tmp_proj,zbin,c_cat, width)
                    if c_cat != "data":
                        if firstmc:
                            tmp_mctot = tmp_proj.Clone()
                            firstmc = False
                        else:
                            tmp_mctot.Add(tmp_proj)
                        grid_dict[projbin][zbin][c_cat] = tmp_proj
                    elif not noData:
                        grid_dict[projbin]["data"] = tmp_proj
            grid_dict[projbin]["mctot"] = tmp_mctot

        # Get the max to get multipliers for these
        global_max = 0.0
        for projbin in grid_dict.keys():
            smax = grid_dict[projbin]["mctot"].GetMaximum()
            if not noData:
                dmax = grid_dict[projbin]["data"].GetMaximum()
                global_max = max(smax*1.2, dmax*1.2, global_max)
            else:
                global_max = max(smax*1.2, global_max)
        print(global_max)
        bin_scales = []
        print(grid_dict.keys())
        for projbin in grid_dict.keys():
            tmp_pad_max = 0.0
            tmp_pad_scale = 1.0
            if not noData:
                dmax = grid_dict[projbin]["data"].GetMaximum()
                mcmax = grid_dict[projbin]["mctot"].GetMaximum()
                tmp_pad_max = 1.2 * max(dmax,mcmax)
            else:
                tmp_pad_max = 1.2 * grid_dict[projbin]["mctot"].GetMaximum()
            if tmp_pad_max == 0:
                tmp_pad_max = 1.0
            tmp_pad_scale = eval('{:.{p}g}'.format(global_max / tmp_pad_max, p=3))

            grid_dict[projbin]["multiplier"] = tmp_pad_scale
            tmp_stack = THStack("stack","")
            if not noData:
                grid_dict[projbin]["data"].Scale(tmp_pad_scale)
            grid_dict[projbin]["mctot"].Scale(tmp_pad_scale)
            for c_cat in cat_order:
                # if c_cat in ["data","mctot","stack","multiplier"]:
                if c_cat in ["data","mctot","stack","multiplier"]:
                    continue
                for zbin in new_bin_pid_order:
                    if zbin == -1:
                        continue
                    # print(c_cat, zbin)
                    tmp_hist = TH1D(grid_dict[projbin][zbin][c_cat].Clone())
                    tmp_hist.Scale(tmp_pad_scale)
                    tmp_stack.Add(tmp_hist)
            # grid_dict[projbin]["stack"] = None
            grid_dict[projbin]["stack"] = tmp_stack

        n_xbins_noflow = n_xbins
        n_ybins_noflow = n_ybins
        if analysistype in [0,1]:
            n_xbins_noflow = n_xbins - 2 
            n_ybins_noflow = n_ybins - 2 

        thename = "%s_%s___%s" % (a_sample, b_var, data_var)
        if projY:
            n_xcanvasbins = n_ybins_noflow
            n_ycanvasbins = n_xbins_noflow
            thename+="_projY"
        else:
            n_xcanvasbins = n_xbins_noflow
            n_ycanvasbins = n_ybins_noflow
            thename+="_projX"

        gc2 = PanelCanvas(thename,n_xcanvasbins,n_ycanvasbins)

        pad_index = 1
        for projbin in grid_dict.keys():
            pad = gc2.cd(pad_index)
            pad_index+=1
            # smax = grid_dict[projbin]["stack"].GetMaximum()
            if not noData:
                # dmax = grid_dict[projbin]["data"].GetMaximum()
                grid_dict[projbin]["data"].SetMaximum(global_max)
                grid_dict[projbin]["data"].SetMinimum(0)
                grid_dict[projbin]["data"].GetXaxis().SetNdivisions(505)
                grid_dict[projbin]["data"].GetYaxis().SetNdivisions(505)
                grid_dict[projbin]["data"].Draw("")

            # if b_var.split("_")[1] in ["LeadingNeutCandEdep","EAvail"] and projY:
            if b_var.split("_")[1] in ["NeutCandEdep","NeutCandsEdep"] and projY:
                pad.SetLogx()
            # if b_var.split("_")[0] in ["LeadingNeutCandEdep","EAvail"] and projY == False:
            if (
                b_var.split("_")[0] in ["NeutCandEdep", "NeutCandsEdep"]
                and projY == False
            ):
                pad.SetLogx()
            if not noData:
                grid_dict[projbin]["stack"].Draw("Hist,same")
                grid_dict[projbin]["data"].Draw("PE,same")
                grid_dict[projbin]["data"].Draw("AXIS,same")
            else:
                # grid_dict[projbin]["stack"].Draw("")
                grid_dict[projbin]["mctot"].SetTitle(data_var)

                grid_dict[projbin]["mctot"].SetMaximum(global_max)
                grid_dict[projbin]["mctot"].SetMinimum(0)
                grid_dict[projbin]["mctot"].GetXaxis().SetNdivisions(505)
                grid_dict[projbin]["mctot"].GetYaxis().SetNdivisions(505)
                grid_dict[projbin]["mctot"].Draw("")

                grid_dict[projbin]["stack"].Draw("Hist,same")
                grid_dict[projbin]["mctot"].Draw("AXIS,same")

            multip = grid_dict[projbin]["multiplier"]
            multip_latex = ROOT.TLatex()
            multip_latex.SetTextAlign(32)
            multip_latex.SetNDC()
            multip_latex.SetTextFont(42)
            multip_latex.SetTextSize(0.03)
            multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.16),"#times {:g}".format(float('{:.{p}g}'.format(multip, p=2))))

            if projY:
                tmp_projaxis_bins = bins[0]
                tmp_var = b_var.split("_")[0]
            else: 
                tmp_projaxis_bins = bins[1]
                tmp_var = b_var.split("_")[1]
            if tmp_var not in var_short_names.keys():
                tmp_varshort = "var"
            else: 
                tmp_varshort = var_short_names[tmp_var]
            if analysistype in [0,1]:
                loedge = tmp_projaxis_bins[projbin-1]
                hiedge = tmp_projaxis_bins[projbin]
            else: 
                loedge = tmp_projaxis_bins[projbin]
                hiedge = tmp_projaxis_bins[projbin+1]
            range_string = "{min} < {var} < {max}".format(min = 0.01*round(loedge*100), var = tmp_varshort, max = 0.01*round(hiedge*100))

            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.028)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)

        if b_var.split("_")[1] in ["NeutCandEdep", "NeutCandsEdep"] and projY:
            gc2.SetLogx()
        if (
            b_var.split("_")[0] in ["NeutCandEdep", "NeutCandsEdep"]
            and projY == False
        ):
            gc2.SetLogx()
        gc2.SetYTitle("Counts/unit")
        gc2.SetXTitle(b_var.split("_")[1])
        gc2.SetHistTexts()
        # gc2.ResetPads()
        gc2.Draw()
        # gc2.ResetPads()
        # gc2.Print("")

        canvas_name = thename + "_FinalStates"
        if dotuned:
            canvas_name = thename + "_FinalStates_tuned"
        gc2.Print(os.path.join(outdirname, canvas_name + ".png"))

        del gc2

        # stack_first = 0
        # if stack_first == 0:
        #     print("starting with var ", b_var)

        # # thename = "%s_%s" % (a_sample.replace("_Tuned", ""), data_var)
        # thename = "%s_%s" % (a_sample, data_var)
        # thetitle = "%s %s" % (a_sample, data_var)

        # # if doratio and not noData:
        # #     leg = CCQELegend(0.65, 0.45, 0.95, 0.85)
        # # else:
        # #     leg = CCQELegend(0.65, 0.65, 0.95, 0.95)
        # leg = CCQELegend(0.75, 0.55, 0.98, 0.95)
        # leg.SetNColumns(2)

        # if a_sample not in samplenames.keys():
        #     plottitle = a_sample
        # else:
        #     plottitle = samplenames[a_sample]
        # if dotuned:
        #     plottitle = tunedname
        #     plottitle = "Tuned " + plottitle
        # # if stack_first == 0:  # make a stack
        # stack = THStack("stack", "")
        # # stack_first += 1

        # firstpid = True
        # mctot = MnvH1D()
        # for c_cat in cat_order:
        #     if c_cat not in groups[a_sample][b_var].keys():
        #         print("skipping cat not found in groups: ", c_cat)
        #         continue

        #     hist = groups[a_sample][b_var][c_cat]
        #     first_pipm = True
        #     for pid in bin_pid_order:
        #         lobin = pid
        #         hibin = pid
        #         if pid in [4,5]:
        #             if first_pipm:
        #                 lobin = 4
        #                 hibin = 5
        #                 first_pipm = False
        #             else:
        #                 continue
        #         tmp_h_pid = hist.ProjectionX(
        #             str(hist.GetName().replace("h2D", "h") + "_" + bin_pid[pid]),
        #             lobin,
        #             hibin,
        #         )
        #         if pid == 9:
        #             tmp_h_pid.Print()
        #         # if pid == 3:
        #         #     tmp_h_pid.Scale(3.0)
        #         tmp_h_pid.SetFillColor(bin_pid_colors[pid])
        #         tmp_h_pid.SetLineColor(bin_pid_colors[pid])
        #         # tmp_h_pid.SetLineColor(ROOT.TColor.GetColorDark(bin_pid_colors[pid]))
        #         if c_cat in backgrounds:
        #             tmp_h_pid.SetFillStyle(3244)
        #         stack.Add(tmp_h_pid)
        #         if firstpid:
        #             mctot = tmp_h_pid.Clone()
        #             firstpid = False
        #         else:
        #             mctot.Add(tmp_h_pid)
        # # Jank to get legend order correct
        # firstpis = {}
        # for c_cat in cat_order:
        #     firstpis[c_cat] = True
        # for pid in reversed(bin_pid_order):
        #     for c_cat in reversed(cat_order):
        #         if c_cat not in groups[a_sample][b_var].keys():
        #             continue
        #         hist = groups[a_sample][b_var][c_cat]
        #         lobin = pid
        #         hibin = pid
        #         if pid in [4,5]:
        #             if firstpis[c_cat]:
        #                 lobin = 4
        #                 hibin = 5
        #                 first_pipm = False
        #             else:
        #                 continue
        #         tmp_h_pid = hist.ProjectionX(
        #             str(hist.GetName().replace("h2D", "h") + "_" + bin_pid[pid]),
        #             lobin,
        #             hibin,
        #         )
        #         tmp_h_pid.SetFillColor(bin_pid_colors[pid])
        #         tmp_h_pid.SetLineColor(bin_pid_colors[pid])
        #         # tmp_h_pid.SetLineColor(ROOT.TColor.GetColorDark(bin_pid_colors[pid]))
        #         if c_cat in backgrounds:
        #             tmp_h_pid.SetFillStyle(3244)
        #         if c_cat in backgrounds:
        #             leg.AddEntry(tmp_h_pid, bin_pid[pid] + "-not", "f")
        #         else:
        #             leg.AddEntry(tmp_h_pid, bin_pid[pid], "f")

        # if not noData:
        #     leg.AddEntry(data, "Data", "p")
        # print("Intgeral of mctot", mctot.Integral())
        # ysize = _ysize
        # if doratio and not noData:
        #     ysize = 1.2 * _ysize
        # cc = CCQECanvas(thename, thetitle, _xsize, ysize)
        # if doratio and not noData:
        #     top = TPad("hist", "hist", 0, 0.278, 1, 1)
        #     top.SetRightMargin(0.04)
        #     top.SetBottomMargin(0)
        #     top.SetTopMargin(0.04)
        #     bottom = TPad("Ratio", "Ratio", 0, 0, 1, 0.278)
        #     bottom.SetRightMargin(0.04)
        #     bottom.SetTopMargin(0)
        #     top.Draw()
        #     bottom.Draw()

        #     bottomArea = bottom.GetWNDC() * bottom.GetHNDC()
        #     topArea = top.GetWNDC() * top.GetHNDC()
        #     areaScale = topArea / bottomArea

        #     top.cd()

        # # Now draw everything
        # stack.Draw("")
        # # stack.GetYaxis().SetTitle("Counts #times 10^{3}")
        # stack.GetYaxis().SetTitle("Counts")
        # stack.GetYaxis().CenterTitle()
        # stack.GetYaxis().SetTitleOffset(0.6)
        # stack.GetYaxis().SetTitleSize(0.05)
        # stack.GetYaxis().SetLabelSize(stack.GetYaxis().GetLabelSize() * 1.2)
        # title = ""
        # if b_var not in titles.keys():
        #     title = b_var.split("_")[0]
        # else:
        #     title = titles[b_var]
        # if not doratio or noData:
        #     stack.GetXaxis().SetTitle(title)
        #     stack.GetXaxis().CenterTitle()
        #     stack.GetXaxis().SetTitleSize(0.05)
        # if not noData:
        #     if data.GetMaximum() > stack.GetMaximum():
        #         stack.SetMaximum(data.GetMaximum())
        # stack.Draw("hist")
        # if not noData:
        #     data.Draw("PE same")
        # leg.Draw()
        # if doratio and not noData:
        #     bottom.cd()
        #     bottom.SetBottomMargin(0.3)
        #     mctot.SetFillStyle(1001)
        #     ratio = MakeDataMCRatio(data, mctot)
        #     ratio.SetMinimum(0.5)
        #     ratio.SetMaximum(1.5)

        #     ratio.SetLineColor(ROOT.kBlack)
        #     ratio.SetLineWidth(3)

        #     ratio.SetTitle("")
        #     ratio.GetYaxis().SetTitle("Data / MC")
        #     ratio.GetYaxis().CenterTitle()
        #     ratio.GetYaxis().SetTitleSize(0.05 * areaScale)
        #     # ratio.GetYaxis().SetTitleOffset(0.8)
        #     ratio.GetYaxis().SetLabelSize(ratio.GetYaxis().GetLabelSize() * areaScale*1.2)
        #     ratio.GetYaxis().SetNdivisions(-505)

        #     ratio.GetXaxis().SetTitle(title)
        #     ratio.GetXaxis().CenterTitle()
        #     ratio.GetXaxis().SetTitleSize(0.05 * areaScale)
        #     ratio.GetXaxis().SetLabelSize(ratio.GetXaxis().GetLabelSize() * areaScale*1.2)

        #     ratio.Draw()

        #     mcratio = TH1D(
        #         # groups[a_sample][data_var]["mctot"].GetTotalError(False, True, False)
        #         mctot.GetTotalError(False, True, False)
        #     )
        #     for bin in range(1, mcratio.GetXaxis().GetNbins() + 1):
        #         mcratio.SetBinError(bin, max(mcratio.GetBinContent(bin), 1.0e-9))
        #         mcratio.SetBinContent(bin, 1.0)
        #     mcratio.SetLineColor(ROOT.kRed)
        #     mcratio.SetLineWidth(3)
        #     mcratio.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
        #     mcratio.Draw("same E2")

        #     straightline = mcratio.Clone()
        #     straightline.SetFillStyle(0)
        #     straightline.Draw("hist same")

        #     ratio.Draw("same")

        #     # cc.Update()
        #     top.cd()
        #     # titleonplot.DrawLatex(0.37, 0.85, plottitle)
        #     # prelim.DrawLatex(0.62, 0.62, "MINER#nuA Work In Progress")
        # prelim = AddPreliminary()
        # titleonplot = MakeTitleOnPlot()
        # # else:
        # prelim.DrawLatex(latex_x, latex_y, "MINER#nuA Work In Progress")
        # titleonplot.DrawLatex(0.37, 0.9, plottitle)

        # # cc.Draw()
        # # cc.SetLogy()
        # canvas_name = thename + "_FinalStates"
        # if dotuned:
        #     canvas_name = thename + "_FinalStates_tuned"
        # cc.Print(os.path.join(outdirname, canvas_name + ".png"))
