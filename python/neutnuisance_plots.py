# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023


from re import L
import sys, os
import ROOT
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

global_noData = False  # use this to plot MC only types
noData = global_noData  # dummy bc dumb
dotypes = False  # use this if ou want to do by types
# dotuned=False  # use this if you have tuned hists
doratio = True  # use this if you want to include a data/mc ratio
ROOT.TH1.AddDirectory(ROOT.kFALSE)

legendfontsize = 0.042

_xsize = 1100.0
_ysize = 720.0

latex_x = 0.72
latex_y = 0.53


def CCQECanvas(name, title, xsize=1100, ysize=720):
    # c2 = ROOT.TCanvas(name,title)

    c2 = ROOT.TCanvas(name, title, round(xsize), round(ysize))
    # c2.SetLeftMargin(0.2)
    c2.SetRightMargin(0.04)
    # c2.SetLeftMargin(0.13)
    c2.SetTopMargin(0.04)

    # c2.SetBottomMargin(0.14)
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
# cat_order = list(
#     [
#         "qelikenot",
#         "qelike",
#         "data",
#     ]
# )
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
signal = ["data", "qelike", "qelike_old"]

backgrounds = [cat for cat in cat_order if cat not in signal]
# print(backgrounds)

catstodo = cat_order
# catstodo = [
#     # "data",
#     "qelike",
#     "qelikenot",
#     # "chargedpion",
#     # "neutralpion",
#     # "multipion",
#     # "other"
# ]


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
# vars1Dtodo = [
#     "LeadingNeutCandvtxBoxDist",
#     "SecNeutCandvtxBoxDist",
#     "ThirdNeutCandvtxBoxDist",
#     "LeadingNeutCandvtxZDist",
#     "SecNeutCandvtxZDist",
#     "ThirdNeutCandvtxZDist",
#     "LeadingNeutCandvtxSphereDist",
#     "SecNeutCandvtxSphereDist",
#     "ThirdNeutCandvtxSphereDist",
#     "LeadingNeutCandEdep",
#     "SecNeutCandEdep",
#     "ThirdNeutCandEdep",
#     "LeadingNeutCandMuonDist",
#     "SecNeutCandMuonDist",
#     "ThirdNeutCandMuonDist",
#     "LeadingNeutCandMuonAngle",
#     "SecNeutCandMuonAngle",
#     "ThirdNeutCandMuonAngle",
#     "LeadingNeutCandClusterMaxE",
#     "SecNeutCandClusterMaxE",
#     "ThirdNeutCandClusterMaxE",
# ]
#  These are the vars that fill into bins
# varstodo = [
#     "LeadingNeutCandvtxBoxDist_LeadingNeutCandTopMCPID",
#     "SecNeutCandvtxBoxDist_SecNeutCandTopMCPID",
#     "ThirdNeutCandvtxBoxDist_ThirdNeutCandTopMCPID",
#     "LeadingNeutCandvtxZDist_LeadingNeutCandTopMCPID",
#     "SecNeutCandvtxZDist_SecNeutCandTopMCPID",
#     "ThirdNeutCandvtxZDist_ThirdNeutCandTopMCPID",
#     "LeadingNeutCandvtxSphereDist_LeadingNeutCandTopMCPID",
#     "SecNeutCandvtxSphereDist_SecNeutCandTopMCPID",
#     "ThirdNeutCandvtxSphereDist_ThirdNeutCandTopMCPID",
#     "LeadingNeutCandEdep_LeadingNeutCandTopMCPID",
#     "SecNeutCandEdep_SecNeutCandTopMCPID",
#     "ThirdNeutCandEdep_ThirdNeutCandTopMCPID",
#     "LeadingNeutCandMuonDist_LeadingNeutCandTopMCPID",
#     "SecNeutCandMuonDist_SecNeutCandTopMCPID",
#     "ThirdNeutCandMuonDist_ThirdNeutCandTopMCPID",
#     "LeadingNeutCandMuonAngle_LeadingNeutCandTopMCPID",
#     "SecNeutCandMuonAngle_SecNeutCandTopMCPID",
#     "ThirdNeutCandMuonAngle_ThirdNeutCandTopMCPID",
#     "LeadingNeutCandClusterMaxE_LeadingNeutCandTopMCPID",
#     "SecNeutCandClusterMaxE_SecNeutCandTopMCPID",
#     "ThirdNeutCandClusterMaxE_ThirdNeutCandTopMCPID",
# ]

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
    10: ROOT.kP10Gray,
}

# bin_pid_order = list([10, 7, 6, 5, 4, 3, 8, 2, 1])
# decided to combine pi+ (4) with pi- (5)
bin_pid_order = list([10, 7, 6, 5, 3, 8, 2, 1]) 

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

plotdir = os.path.join(plotdirbase, "mad-blob-studies", "neutnuisance")
if not os.path.exists(plotdir):
    print(plotdir)
    os.mkdir(plotdir)

dirname = filename.replace(".root", "_neutnuisanceplots")
for cat in catstodo:
    dirname += "_" + cat
outdirname = os.path.join(plotdir, dirname)
print(outdirname)
if not os.path.exists(outdirname):
    print(outdirname)
    os.mkdir(outdirname)

keys = f.GetListOfKeys()

h_pot = f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(2)
POTScale = dataPOT / mcPOTprescaled
print("POTScale: ", POTScale)

groups = {}
scaleX = ["Q2QE"]
scaleY = ["recoil", "EAvail"]

# find all the valid histogram and group by keywords
for k in keys:
    name = k.GetName()
    if "___" not in name:
        continue
    parse = name.split("___")
    if len(parse) < 5:
        continue
    # print (parse)
    # names look like : hist___Sample___category__variable___types_0;
    # if not flag in parse[4] and not "data" in parse[2]: continue
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
    # if parse[4].find("tuned") != -1 and not dotuned:
    # if ("tuned" in parse[4]) and not dotuned:
    #     continue
    # # if dotuned and parse[4].find("tuned") == -1 and cat != "data":
    # if dotuned and ("tuned" not in parse[4]) and (cat != "data"):
    #     continue
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

    if "tuned" in parse[4]:
        sample += "_Tuned"
    if hist == "h2D":
        if "_" in variable:
            # Skip 2D vars that don't have the PID as a y axis
            if variable.split("_")[1].find("NeutCandTopMCPID") == -1:
                print("Missing NeutCandTopMCPID in ", variable)
                continue
            # Add to list to loop over later
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

    # print("\t",sample, variable, cat)
    h = f.Get(name).Clone()
    if h.GetEntries() <= 0:
        print("hist ", name, " has no entries, skipping...")
        continue
    h.SetFillColor(catscolors[cat])
    h.SetLineColor(catscolors[cat] + 1)
    if "data" in cat:
        if h.GetEntries() <= 0:
            continue
        # h.Scale(1.,"width")
        # h.Scale(0.001, "width")
        h.Scale(0.001)
        h.SetMarkerStyle(20)
        h.SetMarkerSize(1.5)
    if "data" not in cat:
        # h.Scale(POTScale * 0.001, "width")  # scale to data
        # h.Scale(0.001, "width")  # scale to data
        h.Scale(POTScale * 0.001)  # scale to data
        # h.Scale(POTScale)  # scale to data
    if cat in backgrounds:
        h.SetFillStyle(3244)
    groups[sample][variable][cat] = h
# do the plotting

if "qelikenot" not in backgrounds:
    backgrounds.append("qelikenot")
    print("Combining backgrounds to make a background total")
    for a_sample in groups.keys():
        for b_var in groups[a_sample].keys():
            if "_" not in b_var:
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

if not noData:
    cat_order = list(["qelikenot", "qelike", "data"])
# if doratio and not noData:
#     for a_sample in groups.keys():
#         print(a_sample)
#         data_sample_name = a_sample
#         if "_Tuned" in a_sample:
#             data_sample_name = a_sample.replace("_Tuned","")
#         for b_var in varstodo:
#             if "mctot" in groups[a_sample][b_var].keys():
#                 continue
#             var1d = b_var.split("_")[0]
#             if var1d not in groups[data_sample_name].keys():
#                 continue
#             groups[a_sample][b_var]["mctot"] = {}
#             mctot2d = MakeMCtot(
#                 [
#                     groups[a_sample][b_var]["qelike"],
#                     groups[a_sample][b_var]["qelikenot"],
#                 ]
#             )
#             print("making mctot hist ", str(mctot2d.GetName().replace(b_var, var1d)))
#             mctot = mctot2d.ProjectionX(
#                 str(mctot2d.GetName().replace(b_var, var1d)), 0, -1
#             )
#             if var1d not in groups[a_sample].keys():
#                 # print(a_sample, var1d)
#                 groups[a_sample][var1d] = {}
#             groups[a_sample][var1d]["mctot"] = mctot


# build an order which puts backgrounds below signal (assumes signal is first in list)
bestorder = []

ROOT.gStyle.SetOptStat(0)
template = "%s___%s___%s___%s"

for a_sample in groups.keys():
    # for b_var in groups[a_sample].keys():
    if "_Tuned" in a_sample:
        dotuned = True
        tunedname = a_sample.replace("_Tuned", "")
    else:
        dotuned = False
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

        stack_first = 0
        if stack_first == 0:
            print("starting with var ", b_var)

        thename = "%s_%s" % (a_sample.replace("_Tuned",""), data_var)
        thetitle = "%s %s" % (a_sample, data_var)

        # if doratio and not noData:
        #     leg = CCQELegend(0.65, 0.45, 0.95, 0.85)
        # else:
        #     leg = CCQELegend(0.65, 0.65, 0.95, 0.95)
        leg = CCQELegend(0.75, 0.55, 0.98, 0.95)
        leg.SetNColumns(2)

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
        for c_cat in cat_order:
            if c_cat not in groups[a_sample][b_var].keys():
                print("skipping cat not found in groups: ", c_cat)
                continue

            hist = groups[a_sample][b_var][c_cat]
            first_pipm = True
            for pid in bin_pid_order:
                lobin = pid
                hibin = pid
                if pid in [4,5]:
                    if first_pipm:
                        lobin = 4
                        hibin = 5
                        first_pipm = False
                    else:
                        continue
                tmp_h_pid = hist.ProjectionX(
                    str(hist.GetName().replace("h2D", "h") + "_" + bin_pid[pid]),
                    lobin,
                    hibin,
                )
                # if pid == 3:
                #     tmp_h_pid.Scale(3.0)
                tmp_h_pid.SetFillColor(bin_pid_colors[pid])
                tmp_h_pid.SetLineColor(bin_pid_colors[pid])
                if c_cat in backgrounds:
                    tmp_h_pid.SetFillStyle(3244)
                stack.Add(tmp_h_pid)
                if firstpid:
                    mctot = tmp_h_pid.Clone()
                    firstpid = False
                else:
                    mctot.Add(tmp_h_pid)
        # Jank to get legend order correct
        firstpis = {}
        for c_cat in cat_order:
            firstpis[c_cat] = True
        for pid in reversed(bin_pid_order):
            for c_cat in reversed(cat_order):  
                if c_cat not in groups[a_sample][b_var].keys():
                    continue
                hist = groups[a_sample][b_var][c_cat]
                lobin = pid
                hibin = pid
                if pid in [4,5]:
                    if firstpis[c_cat]:
                        lobin = 4
                        hibin = 5
                        first_pipm = False
                    else:
                        continue
                tmp_h_pid = hist.ProjectionX(
                    str(hist.GetName().replace("h2D", "h") + "_" + bin_pid[pid]),
                    lobin,
                    hibin,
                )
                tmp_h_pid.SetFillColor(bin_pid_colors[pid])
                tmp_h_pid.SetLineColor(bin_pid_colors[pid])
                if c_cat in backgrounds:
                    tmp_h_pid.SetFillStyle(3244)
                if c_cat in backgrounds:
                    leg.AddEntry(tmp_h_pid, bin_pid[pid] + "-not", "f")
                else:
                    leg.AddEntry(tmp_h_pid, bin_pid[pid], "f")

        if not noData:
            leg.AddEntry(data, "Data", "p")

        ysize = _ysize
        if doratio and not noData:
            ysize = 1.2 * _ysize
        cc = CCQECanvas(thename, thetitle, _xsize, ysize)
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

            top.cd()
        
        # Now draw everything
        stack.Draw("")
        stack.GetYaxis().SetTitle("Counts #times 10^{3}")
        # stack.GetYaxis().SetTitle("Counts")
        stack.GetYaxis().CenterTitle()
        stack.GetYaxis().SetTitleOffset(0.6)
        stack.GetYaxis().SetTitleSize(0.05)
        stack.GetYaxis().SetLabelSize(stack.GetYaxis().GetLabelSize() * 1.2)
        title = ""
        if b_var not in titles.keys():
            title = b_var.split("_")[0]
        else:
            title = titles[b_var]
        if not doratio or noData:
            stack.GetXaxis().SetTitle(title)
            stack.GetXaxis().CenterTitle()
            stack.GetXaxis().SetTitleSize(0.05)
        stack.Draw("hist")
        if not noData:
            data.Draw("PE same")
        leg.Draw()
        if doratio and not noData:
            bottom.cd()
            bottom.SetBottomMargin(0.3)
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
            # ratio.GetYaxis().SetTitleOffset(0.8)
            ratio.GetYaxis().SetLabelSize(ratio.GetYaxis().GetLabelSize() * areaScale*1.2)
            ratio.GetYaxis().SetNdivisions(-505)

            ratio.GetXaxis().SetTitle(title)
            ratio.GetXaxis().CenterTitle()
            ratio.GetXaxis().SetTitleSize(0.05 * areaScale)
            ratio.GetXaxis().SetLabelSize(ratio.GetXaxis().GetLabelSize() * areaScale*1.2)

            ratio.Draw()

            mcratio = TH1D(
                # groups[a_sample][data_var]["mctot"].GetTotalError(False, True, False)
                mctot.GetTotalError(False, True, False)
            )
            for bin in range(1, mcratio.GetXaxis().GetNbins() + 1):
                mcratio.SetBinError(bin, max(mcratio.GetBinContent(bin), 1.0e-9))
                mcratio.SetBinContent(bin, 1.0)
            mcratio.SetLineColor(ROOT.kRed)
            mcratio.SetLineWidth(3)
            mcratio.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
            mcratio.Draw("same E2")

            straightline = mcratio.Clone()
            straightline.SetFillStyle(0)
            straightline.Draw("hist same")

            ratio.Draw("same")

            # cc.Update()
            top.cd()
            # titleonplot.DrawLatex(0.37, 0.85, plottitle)
            # prelim.DrawLatex(0.62, 0.62, "MINER#nuA Work In Progress")
        prelim = AddPreliminary()
        titleonplot = MakeTitleOnPlot()
        # else:
        prelim.DrawLatex(latex_x, latex_y, "MINER#nuA Work In Progress")
        titleonplot.DrawLatex(0.37, 0.9, plottitle)

        # cc.Draw()
        # cc.SetLogy()
        canvas_name = thename + "_FinalStates"
        if dotuned:
            canvas_name = thename + "_FinalStates_tuned"
        cc.Print(os.path.join(outdirname, canvas_name + ".png"))
