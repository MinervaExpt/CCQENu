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
from PlotUtils import MnvH1D, MnvH2D
import datetime
mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")

sig_only = False


global_noData = False  # use this to plot MC only types
noData = global_noData  # dummy bc dumb
dotypes = False  # use this if ou want to do by types
# dotuned=False  # use this if you have tuned hists
doratio = False  # use this if you want to include a data/mc ratio
ROOT.TH1.AddDirectory(ROOT.kFALSE)
shortenedep = False

legendfontsize = 0.05

# _xsize = 1800.0
# _ysize = 1200.0
_xsize = 3200
# _ysize = 1800
_ysize = 2400

latex_x = 0.55
latex_y = 0.43

rebin_dict = {
    # "NeutCandsEdep": 2,
    "NeutCandsvtxSphereDist": 2,
    "NeutCandsTrackEndDist": 2,
}

topbin_dict = {
    "NeutCandsEdep": [0.0, 100.0,]
    # "NeutCandsvtxSphereDist": 2,
    # "NeutCandsTrackEndDist": 600,

}

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
        if hist != "h2D" and cat != "data":
            continue
        if cat == "data" and hist != "h":
            continue
        if cat not in catstodo:
            continue
        # if variable not in varstodo+vars1Dtodo:
        #     continue
        if sample not in samplestodo:
            continue

        if dotypes and (cat not in ["qelikenot","qelike","data"]):
            continue
        data_var = variable
        if "tuned" in parse[4]:
            sample += "_Tuned"
        if hist == "h2D":
            if "_" in variable:
                # Skip 2D vars that don't have the PID as a y axis
                if (
                    variable.split("_")[1].find("NeutCandTopMCPID") == -1
                    and variable.split("_")[1].find("NeutCandsTopMCPID") == -1
                ):
                    print("Missing NeutCandTopMCPID in ", variable)
                    continue
                # Add to list to loop over later
                data_var = variable.split("_")[0]
                if variable not in varstodo:
                    varstodo.append(variable)
                # Add to list to check later if there's a 1D data that exists
                if variable.split("_")[0] not in vars1Dtodo:
                    vars1Dtodo.append(variable.split("_")[0])
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

        h = i_file.Get(name).Clone()
        if data_var in topbin_dict:
            h.GetXaxis().SetRangeUser(topbin_dict[data_var][0], topbin_dict[data_var][1])

        if h.GetEntries() <= 0:
            print("hist ", name, " has no entries, skipping...")
            continue
        # if not dotypes:
        #     h.SetFillColor(catscolors[cat])
        #     # h.SetLineColor(catscolors[cat] + 1)
        #     h.SetLineColor(ROOT.TColor.GetColorDark(catscolors[cat]))
        if dotypes:
            if "types_" in parse[4]:
                index = int(parse[4].replace("types_",""))
                h.SetFillColor(type_colors[index])
                if cat == "qelikenot":
                    index += 10
                    h.SetFillStyle(3244)
                if index not in groups[sample][variable][cat].keys():
                    groups[sample][variable][cat][index] = {}
        if "data" in cat:
            if h.GetEntries() <= 0:
                continue
            h.Scale(1.0, "width")
            # h.Scale(0.001, "width")
            # h.Scale(0.001)
            h.SetMarkerStyle(20)
            h.SetMarkerSize(2)
            # if shortenedep and variable in ["NeutCandsEdep"]:
            #     h.GetXaxis().SetRangeUser(0.0,150.)
        if "data" not in cat:
            # h.Scale(POTScale * 0.001, "width")  # scale to data
            h.Scale(POTScale, "width")  # scale to data
            # h.Scale(POTScale * 0.001)  # scale to data
            # h.Scale(POTScale)  # scale to data
            h.SetFillColor(catscolors[cat])
            h.SetLineColor(ROOT.TColor.GetColorDark(catscolors[cat]))
            h.SetLineColor(ROOT.kBlack)

        if cat in backgrounds:
            h.SetFillStyle(3244)
        if not dotypes:
            groups[sample][variable][cat] = h
        else:
            if cat=="data":
                groups[sample][variable][cat] = h
            else:
                groups[sample][variable][cat][index] = h

    # do the plotting

    if "qelikenot" not in backgrounds:
        backgrounds.append("qelikenot")
        print("Combining backgrounds to make a background total")
        for a_sample in groups.keys():
            for b_var in groups[a_sample].keys():
                if "_" not in b_var:
                    continue
                if len(b_var.split("_"))!=2:
                    continue
                if "qelikenot" in groups[a_sample][b_var].keys():
                    continue
                groups[a_sample][b_var]["qelikenot"] = {}
                first_cat = True
                for c_cat in backgrounds:
                    if c_cat == "qelikenot":
                        continue
                    # print("c_cat", c_cat)
                    # print("groups[a_sample][b_var].keys()", groups[a_sample][b_var].keys())
                    tmp_hist = groups[a_sample][b_var][c_cat].Clone()
                    if first_cat:
                        groups[a_sample][b_var]["qelikenot"] = tmp_hist.Clone(
                            tmp_hist.GetName().replace(c_cat, "qelikenot")
                        )
                        first_cat = False
                        continue
                    groups[a_sample][b_var]["qelikenot"].Add(tmp_hist)

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
        os.mkdir(plotdir)
    if subdir == "":
        return plotdir
    if not os.path.exists(os.path.join(plotdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(plotdir, subdir))
        os.mkdir(os.path.join(plotdir, subdir))
    return os.path.join(plotdir, subdir)


def CCQECanvas(name, title, xsize=1100, ysize=720):
    # c2 = ROOT.TCanvas(name,title)

    c2 = ROOT.TCanvas(name, title, round(xsize), round(ysize))
    # c2.SetLeftMargin(0.2)
    c2.SetRightMargin(0.04)
    # c2.SetLeftMargin(0.13)
    c2.SetTopMargin(0.04)

    c2.SetBottomMargin(0.17)
    return c2


def CCQELegend(xlow, ylow, xhigh, yhigh):
    leg = ROOT.TLegend(xlow, ylow, xhigh, yhigh)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(legendfontsize)
    return leg

def GetLegendPos(topmargin,bottommargin,leftmargin,rightmargin, n_entries, n_columns, position = "TR"):
    padwidth = 1. - leftmargin - rightmargin
    padheight = 1. - topmargin - bottommargin
    x1 = 0.0
    x2 = 0.0
    y1 = 0.0
    y2 = 0.0
    # position can be TR, TC, TL, BR BC BL, MR, BC, ML

def AddPreliminary():
    font = 112
    color = ROOT.kRed + 1
    latex = ROOT.TLatex()
    latex.SetNDC()
    # latex.SetTextSize(legendfontsize - 0.004)
    latex.SetTextSize(legendfontsize/2)
    latex.SetTextColor(color)
    latex.SetTextFont(font)
    latex.SetTextAlign(31)
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

if noData:
    cat_order = list(
        [
            # "other",
            # # "multipion",
            # "neutralpion",
            # "chargedpion",
            # "qelikenot",
            "qelike_old",
            "qelike",
        ]
    )
if dotypes:
    cat_order = list(
        [
            "qelikenot",
            "qelike",
            "data"
        ]
    )
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

vars1Dtodo = []
varstodo = []

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
        "title": "Cluster d_{track}",
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
    9: "Non-GENIE",
    10: "Other",
}
bin_pid_mechname = {
    1: "neutron",
    2: "proton",
    3: "pizero",
    4: "#piplus", # decided to combine pi+ (4) with pi- (5)
    5: "#piminus",
    # 4: "#pi^{#pm}",
    # 5: "#pi^{#pm}",
    6: "gamma",
    7: "electron",
    8: "muon",
    9: "notop",
    10: "other",
}
bin_pid_names = {   
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
    1,
    2, 
] 

pid_consolidation = [
    7,
    6,
    5,
    4,
    3
]
if len(pid_consolidation)!=0:
    cons_bin_pid_order = []
    for pid in bin_pid_order:
        if pid in pid_consolidation: continue
        cons_bin_pid_order.append(pid)
    # bin_pid_order = tmp_bin_pid_order


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

plotdir = MakePlotDir("neutnuisancePlots")
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
scaleX = ["Q2QE"]
scaleY = ["recoil", "EAvail"]
groups = GetHistDict(f, POTScale)

if not noData:
    cat_order = list(["qelikenot", "qelike", "data"])

ROOT.gStyle.SetOptStat(0)
# template = "%s___%s___%s___%s"

for a_sample in groups.keys():
    # for b_var in groups[a_sample].keys():
    if "_Tuned" in a_sample:
        dotuned = True
        tunedname = a_sample.replace("_Tuned", "")
    else:
        dotuned = False
    tmp_canvas_basename = "%s"%(a_sample)
    pdf_canvas_name = "gl_"+tmp_canvas_basename+"_neut1d"
    dummy_canvas = ROOT.TCanvas(pdf_canvas_name,pdf_canvas_name,_xsize,_ysize)
    dummy_canvas.SetCanvasSize(_xsize,_ysize)
    dummy_canvas.Print(os.path.join(outdirname,pdf_canvas_name+".pdf")+"[","pdf")
    for b_var in varstodo:
        if b_var not in groups[a_sample].keys():
            continue
        noData = global_noData
        data_var = b_var.split("_")[0]
        if not noData:
            data_sample_name = a_sample
            if dotuned:
                data_sample_name = tunedname
            if data_var not in groups[data_sample_name].keys():
                print("Couldn't find data_var. Won't do data stuff for ", b_var)
                noData = True
                # continue
            else:
                data = groups[data_sample_name][data_var]["data"].Clone()
                data.SetMarkerColor(ROOT.kBlack)
                data.SetLineColor(ROOT.kBlack)
                if data_var in topbin_dict:
                    data.GetXaxis().SetRangeUser(topbin_dict[data_var][0], topbin_dict[data_var][1])
                if data_var in rebin_dict:
                    data.Rebin(rebin_dict[data_var])
        tmp_canvas_title = "%s"%(data_var)

        stack_first = 0
        if stack_first == 0:
            print("starting with var ", b_var)

        # thename = "%s_%s" % (a_sample.replace("_Tuned", ""), data_var)
        thename = "%s_%s" % (a_sample, data_var)
        thetitle = "%s %s" % (a_sample, data_var)

        # if doratio and not noData:
        #     leg = CCQELegend(0.65, 0.45, 0.95, 0.85)
        # else:
        #     leg = CCQELegend(0.65, 0.65, 0.95, 0.95)
        # leg = CCQELegend(0.55, 0.45, 0.78, 0.95)
        # leg.SetNColumns(2)

        if a_sample not in samplenames.keys():
            plottitle = a_sample
        else:
            plottitle = samplenames[a_sample]
        if dotuned:
            plottitle = tunedname
            plottitle = "Tuned " + plottitle
        # if stack_first == 0:  # make a stack
        stack = THStack("stack", "")
        # stack_first += 1

        firstpid = True
        mctot = MnvH1D()
        tmp_h_pid_dict = {}
        for c_cat in cat_order:
            if c_cat not in groups[a_sample][b_var].keys():
                print("skipping cat not found in groups: ", c_cat)
                continue
            if c_cat not in tmp_h_pid_dict:
                tmp_h_pid_dict[c_cat] = {}

            if not dotypes:
                hist = groups[a_sample][b_var][c_cat]
                first_pipm = True
                nybins = hist.GetNbinsY()
                for pid in bin_pid_order:
                    tmp_projname = "%s_%s"%(hist.GetName().replace("h2D", "h"),bin_pid_mechname[pid]) 
                    print(tmp_projname)
                    tmp_h_pid = hist.ProjectionX(tmp_projname, pid, pid)
                    if data_var in topbin_dict:
                        tmp_h_pid.GetXaxis().SetRangeUser(topbin_dict[data_var][0], topbin_dict[data_var][1])
                    if data_var in rebin_dict:
                        tmp_h_pid.Rebin(rebin_dict[data_var])
                    tmp_h_pid_dict[c_cat][pid] = tmp_h_pid.Clone()
                for pid in bin_pid_order:
                    if pid in pid_consolidation:
                        tmp_h_pid_dict[c_cat][10].Add(tmp_h_pid_dict[c_cat][pid])
                        continue
                    if pid == 5:
                        tmp_h_pid_dict[c_cat][4].Add(tmp_h_pid_dict[c_cat][5])
                        continue
                for pid in cons_bin_pid_order:
                    if c_cat in backgrounds:
                        if sig_only: continue
                        tmp_h_pid_dict[c_cat][pid].SetFillStyle(3244)
                    if firstpid:
                        mctot =  tmp_h_pid_dict[c_cat][pid].Clone()
                        firstpid = False
                    else:
                        mctot.Add(tmp_h_pid_dict[c_cat][pid])
                    tmp_h_pid_dict[c_cat][pid].SetFillColor(bin_pid_colors[pid])
                    tmp_h_pid_dict[c_cat][pid].SetLineColor(ROOT.kBlack)
                    tmp_h_pid_dict[c_cat][pid].SetLineColor(ROOT.TColor.GetColorDark(bin_pid_colors[pid]))
                    if pid == 6 and tmp_h_pid.GetEntries()>0 and c_cat != "qelikenot":
                        tmp_h_pid_dict[c_cat][pid].Print()
                        sys.exit()
                    stack.Add(tmp_h_pid_dict[c_cat][pid])

                    # print("added pid ", bin_pid[pid])
                    print("added pid ", bin_pid_names[bin_pid_mechname[pid]])
                    tmp_h_pid.Print()

            # else:
            #     if c_cat == "data":
            #         continue
            #     for d_type in groups[a_sample][b_var][c_cat].keys():
            #         hist = groups[a_sample][b_var][c_cat][d_type]
        print("Intgeral of mctot", mctot.Integral())
        ysize = _ysize
        if doratio and not noData:
            ysize = 1.2 * _ysize
        cc = ROOT.TCanvas(thename, thetitle, round(_xsize), round(ysize))
        cc.SetRightMargin(0.02)
        cc.SetTopMargin(0.04)
        cc.SetLeftMargin(0.07)
        # cc.SetRightMargin(0.05)
        cc.SetBottomMargin(0.12)

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
        # else:
        #     cc.SetLeftMargin(0.08)
        #     cc.SetRightMargin(0.05)
        #     cc.SetBottomMargin(0.12)
        pad_rmarg = cc.GetRightMargin()
        pad_lmarg = cc.GetLeftMargin()
        topmarg = cc.GetTopMargin()
        bottommarg = cc.GetBottomMargin()
        # x2 = (1. - cc.GetRightMargin()) - (0.02 * padwidth)
        # x1 = x2 - 0.15 # padwidth * 0.17
        # if not sig_only:
        #     x1 = x2 - 0.25
        # y2 = 1 - cc.GetTopMargin() - (0.02 * padheight)
        # y1 = y2 - 0.35 # * padheight
        # tmp_latex_x = x2
        # if data_var in ["NeutCandsMuonCosTheta","NeutCandsTrackEndDist"]:
        #     x1 = cc.GetLeftMargin() + (0.05 * padwidth)
        #     x2 = x1 + 0.2
        #     tmp_latex_x = x1
        # tmp_latex_y = y1 - 0.04
        # leg = TLegend(x1, y1, x2, y2)
        # leg.SetBorderSize(0)
        # leg.SetFillColor(-1)
        # leg.SetFillStyle(0)
        # # leg.SetTextSize(round(legendfontsize/10))
        # leg.SetNColumns(2)
        # leg.SetTextFont(42)

        padwidth = 1 - pad_lmarg - pad_rmarg
        padheight = 1 - topmarg - bottommarg

        x2 = 1. - pad_rmarg - 0.01
        x1 = x2 - 0.35 # padwidth * 0.17
        y2 = 1 - topmarg - 0.02
        y1 = y2 - 0.4 # * padheight
        tmp_latex_x = x2
        tmp_latex_y = y1 - 0.05
        leg = TLegend(x1, y1, x2, y2)
        leg.SetBorderSize(0)
        leg.SetFillColor(-1)
        leg.SetFillStyle(0)
        # leg.SetTextSize(legendfontsize)
        leg.SetNColumns(2)
        leg.SetTextFont(42)
        if not sig_only and not noData:
            leg.AddEntry(data, "Data", "p")
            leg.AddEntry(0, "", "")
        for pid in reversed(cons_bin_pid_order):
            leg.AddEntry(tmp_h_pid_dict["qelike"][pid], bin_pid_names[bin_pid_mechname[pid]], "fl")
            if sig_only: 
                leg.SetNColumns(1)
                continue
            leg.AddEntry(tmp_h_pid_dict["qelikenot"][pid], "Bkg "+bin_pid_names[bin_pid_mechname[pid]], "fl")

        # Now draw everything
        stack.Draw("")
        stack.GetYaxis().SetMaxDigits(3)
        # stack.GetYaxis().SetTitle("Counts #times 10^{3}")
        ytitle = "Counts/unit"
        if data_var in vars_info.keys():
            if vars_info[data_var]["units"]!= "":
                ytitle = "Counts/(%s)"%(vars_info[data_var]["units"])
            else:
                ytitle = "Counts (width norm'd)"

        stack.GetYaxis().SetTitle(ytitle)
        stack.GetYaxis().CenterTitle()
        stack.GetYaxis().SetTitleOffset(0.6)
        stack.GetYaxis().SetTitleSize(0.05)
        stack.GetYaxis().SetLabelSize(0.04)

        xtitle = ""
        if data_var not in vars_info.keys():
            xtitle = data_var
        else:
            if vars_info[data_var]["units"]!= "":
                xtitle = "%s (%s)"%(vars_info[data_var]["title"],vars_info[data_var]["units"])
            else:
                xtitle = vars_info[data_var]["title"]
        if not doratio or noData:
            stack.GetXaxis().SetTitle(xtitle)
            stack.GetXaxis().CenterTitle()
            stack.GetXaxis().SetTitleSize(0.06)
            stack.GetXaxis().SetLabelSize(0.04)

            stack.GetXaxis().SetTitleOffset(0.9)
        if not noData and not sig_only:
            stack.SetMaximum(1.2 * max(data.GetMaximum(), stack.GetMaximum()))
        else:
            stack.SetMaximum(1.15 * stack.GetMaximum())
        stack.Draw("hist ][")
        if not noData and not sig_only:
            data.Draw("PE same")
        leg.Draw()
        # if doratio and not noData:
        #     bottom.cd()
        #     bottom.SetBottomMargin(0.3)
        #     mctot.SetFillStyle(1001)
        #     ratio = MakeDataMCRatio(data, mctot)
        #     if shortenedep and data_var in ["NeutCandsEdep"]:
        #         print(">>>>>>>>Shortened ratio")
        #         ratio.GetXaxis().SetRangeUser(0.0, 150.0)
        #     if data_var in topbin_dict:
        #         ratio.GetXaxis().SetRangeUser(topbin_dict[data_var][0], topbin_dict[data_var][1])

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
        #     ratio.GetXaxis().SetLabelSize(ratio.GetXaxis().GetLabelSize() * areaScale*1.5)

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
        #     # if shortenedep and data_var in ["NeutCandsEdep"]:
        #     #     mcratio.GetXaxis().SetRangeUser(0.0, 150.0)
        #     mcratio.Draw("same E2")

        #     straightline = mcratio.Clone()
        #     straightline.SetFillStyle(0)
        #     # if shortenedep and data_var in ["NeutCandsEdep"]:
        #     #     straightline.GetXaxis().SetRangeUser(0.0, 150.0)

        #     straightline.Draw("hist ][ same")

        #     ratio.Draw("same")

        #     # cc.Update()
        #     top.cd()
        #     # titleonplot.DrawLatex(0.37, 0.85, plottitle)
        #     # prelim.DrawLatex(0.62, 0.62, "MINER#nuA Work In Progress")
        prelim = AddPreliminary()
        # titleonplot = MakeTitleOnPlot()
        # else:
        if data_var in ["NeutCandsMuonCosTheta","NeutCandsTrackEndDist"]:
            prelim.SetTextAlign(11)
        prelim.DrawLatex(tmp_latex_x, tmp_latex_y, "MINER#it{#bf{#nu}}A Work In Progress")
        # titleonplot.DrawLatex(0.37, 0.9, plottitle)
        # if sig_only:
        #     font = 112
        #     color = ROOT.kRed + 1
        #     latex = ROOT.TLatex()
        #     latex.SetNDC()
        #     # latex.SetTextSize(legendfontsize - 0.004)
        #     latex.SetTextSize(legendfontsize - 0.01)
        #     latex.SetTextColor(color)
        #     latex.SetTextFont(font)
        #     latex.SetTextAlign(31)
        #     return latex
        # cc.Draw()
        # cc.SetLogy()
        canvas_name = thename + "_FinalStates"
        if dotuned:
            canvas_name = thename + "_FinalStates_tuned"
        # cc.Print(os.path.join(outdirname, canvas_name + ".png"))
        cc.Print(os.path.join(outdirname, pdf_canvas_name + ".pdf"),"Title:%s %s"%(tmp_canvas_title,"Final States"))
        
    dummy_canvas.Print(os.path.join(outdirname,pdf_canvas_name+".pdf")+"]","pdf")
