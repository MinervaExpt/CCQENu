# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023


from re import L
import sys,os
import ROOT
from ROOT import gROOT,gStyle, TFile,THStack,TH1D,TCanvas, TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex, TString

noData=False  # use this to plot MC only types
dotypes=False
dotuned=True
ROOT.TH1.AddDirectory(ROOT.kFALSE)

legendfontsize = 0.042


def CCQECanvas(name,title,xsize=1100,ysize=720):
    # c2 = ROOT.TCanvas(name,title)

    c2 = ROOT.TCanvas(name,title,xsize,ysize)
    # # c2.SetLeftMargin(0.1)
    c2.SetRightMargin(0.04)
    # c2.SetLeftMargin(0.13)
    c2.SetTopMargin(0.04)
    # c2.SetBottomMargin(0.14)
    return c2

def CCQELegend(xlow,ylow,xhigh,yhigh):
    leg = ROOT.TLegend(xlow,ylow,xhigh,yhigh)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(legendfontsize)
    return leg


def AddPreliminary():
    font = 112
    color = ROOT.kRed +1
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(legendfontsize-0.004)
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


cat_order = list(
    [
        "other",
        # "multipion",
        "neutralpion",
        "chargedpion",
        # "qelikenot_old",
        # "qelike_old",
        # "qelikenot",
        "qelike",
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
signal = [
    "data",
    "qelike",
    "qelike_old"
]

backgrounds = [cat for cat in cat_order if cat not in signal]
print(backgrounds)   

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

vars1Dtodo = [
    "LeadingNeutCandvtxBoxDist",
    "SecNeutCandvtxBoxDist",
    "ThirdNeutCandvtxBoxDist",
    "LeadingNeutCandvtxZDist",
    "SecNeutCandvtxZDist",
    "ThirdNeutCandvtxZDist",
    "LeadingNeutCandvtxSphereDist",
    "SecNeutCandvtxSphereDist",
    "ThirdNeutCandvtxSphereDist",
    "LeadingNeutCandEdep",
    "SecNeutCandEdep",
    "ThirdNeutCandEdep",
    "LeadingNeutCandMuonDist",
    "SecNeutCandMuonDist",
    "ThirdNeutCandMuonDist",
    "LeadingNeutCandMuonAngle",
    "SecNeutCandMuonAngle",
    "ThirdNeutCandMuonAngle",
    "LeadingNeutCandClusterMaxE",
    "SecNeutCandClusterMaxE",
    "ThirdNeutCandClusterMaxE",
]
#  These are the vars that fill into bins
varstodo = [
    "LeadingNeutCandvtxBoxDist_LeadingNeutCandTopMCPID",
    "SecNeutCandvtxBoxDist_SecNeutCandTopMCPID",
    "ThirdNeutCandvtxBoxDist_ThirdNeutCandTopMCPID",
    "LeadingNeutCandvtxZDist_LeadingNeutCandTopMCPID",
    "SecNeutCandvtxZDist_SecNeutCandTopMCPID",
    "ThirdNeutCandvtxZDist_ThirdNeutCandTopMCPID",
    "LeadingNeutCandvtxSphereDist_LeadingNeutCandTopMCPID",
    "SecNeutCandvtxSphereDist_SecNeutCandTopMCPID",
    "ThirdNeutCandvtxSphereDist_ThirdNeutCandTopMCPID",
    "LeadingNeutCandEdep_LeadingNeutCandTopMCPID",
    "SecNeutCandEdep_SecNeutCandTopMCPID",
    "ThirdNeutCandEdep_ThirdNeutCandTopMCPID",
    "LeadingNeutCandMuonDist_LeadingNeutCandTopMCPID",
    "SecNeutCandMuonDist_SecNeutCandTopMCPID",
    "ThirdNeutCandMuonDist_ThirdNeutCandTopMCPID",
    "LeadingNeutCandMuonAngle_LeadingNeutCandTopMCPID",
    "SecNeutCandMuonAngle_SecNeutCandTopMCPID",
    "ThirdNeutCandMuonAngle_ThirdNeutCandTopMCPID",
    "LeadingNeutCandClusterMaxE_LeadingNeutCandTopMCPID",
    "SecNeutCandClusterMaxE_SecNeutCandTopMCPID",
    "ThirdNeutCandClusterMaxE_ThirdNeutCandTopMCPID",
]

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

samplestodo= [
    "QElike",
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
    4: "#pi^{+}",
    5: "#pi^{-}",
    6: "#gamma",
    7: "e^{#pm}",
    8: "#mu^{#pm}",
    10: "Other",
}

bin_pid_colors = {
    1: ROOT.kP10Blue,
    2: ROOT.kP10Yellow,
    3: ROOT.kP10Green,
    4: ROOT.kP10Ash,
    5: ROOT.kP10Orange,
    6: ROOT.kP10Violet,
    7: ROOT.kP10Cyan,
    8: ROOT.kP10Red,
    10: ROOT.kP10Gray,
}

bin_pid_order = list([10, 7, 6, 5, 4, 3, 8, 2, 1])

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
    print ("enter root file name and optional 2nd argument to get tuned version")
flag = "types_"
filename = sys.argv[1]
if len(sys.argv)> 2:
    flag = "tuned_type_"


f = TFile.Open(filename,"READONLY")
plotdirbase = os.getenv("OUTPUTLOC")

plotdir = os.path.join(plotdirbase,"mad-blob-studies","neutnuisance")
if not os.path.exists(plotdir):
    print(plotdir)
    os.mkdir(plotdir)

dirname = filename.replace(".root", "_neutnuisanceplots")
for cat in catstodo:
    dirname += "_"+cat
outdirname = os.path.join(plotdir,dirname)
print(outdirname)
if not os.path.exists(outdirname): 
    print(outdirname)
    os.mkdir(outdirname)

keys = f.GetListOfKeys()

h_pot = f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(2)
POTScale = dataPOT / mcPOTprescaled
print("POTScale: ",POTScale)

groups = {}
scaleX = ["Q2QE"]
scaleY = ["recoil","EAvail"]

# find all the valid histogram and group by keywords
for k in keys:
    name = k.GetName()
    if "___" not in name:
        continue
    parse = name.split("___")
    if len(parse) < 5: continue
    # print (parse)
    # names look like : hist___Sample___category__variable___types_0;
    # if not flag in parse[4] and not "data" in parse[2]: continue
    if "reconstructed" not in parse[4]: continue
    hist = parse[0]
    sample = parse[1]
    cat = parse[2]
    variable = parse[3]
    # print("checking hist ", name)

    if "types" in parse[4] and not dotypes:
        continue
    if "types" not in parse[4] and dotypes:
        continue
    if "simulfit" in parse[4]:
        continue
    if "reconstructed" not in parse[4]:
        continue
    if  parse[4].find("tuned") != -1 and not dotuned and cat!="data":
        continue
    if dotuned and parse[4].find("tuned") == -1 and cat != "data":
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

    if hist =="h2D":
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
    print("\t",sample, variable, cat)
    h = f.Get(name).Clone()
    if h.GetEntries() <= 0:
        print("hist ",name," has no entries, skipping...")
        continue

    if not dotypes:
        h.SetFillColor(catscolors[cat])
        h.SetLineColor(catscolors[cat]+1)
        if "data" in cat:
            index = 0
            h = f.Get(name)
            if h.GetEntries() <= 0: continue
            # h.Scale(1.,"width")
            # h.Scale(0.001, "width")
            h.Scale(0.001)
            h.SetMarkerStyle(20)
            h.SetMarkerSize(1.5)
        if "data" not in cat:
            # print("scaling hist ",h.GetName())
            # print("POTscale: ", POTScale)
            # h.Scale(POTScale * 0.001, "width")  # scale to data
            # h.Scale(0.001, "width")  # scale to data
            h.Scale(POTScale * 0.001)  # scale to data
        if cat in backgrounds:
            h.SetFillStyle(3244)
        groups[sample][variable][cat]=h
    else: # if dotypes:
        if "types_" in parse[4]:
            index = int(parse[4].replace("types_",""))
            h.SetFillColor(type_colors[index])
            if cat in backgrounds:
                index += 10
                h.SetFillStyle(3244)
            h.Scale(0.001 * POTScale)
            groups[sample][variable][cat][index] = h
            # h.Print()
# do the plotting

if "qelikenot" not in backgrounds and not dotypes:
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
                print("c_cat", c_cat)
                print("groups[a_sample][b_var].keys()", groups[a_sample][b_var].keys())
                tmp_hist = groups[a_sample][b_var][c_cat].Clone()
                if first_cat:
                    groups[a_sample][b_var]["qelikenot"] = tmp_hist.Clone(
                        tmp_hist.GetName().replace(c_cat, "qelikenot")
                    )
                    first_cat = False
                    continue
                groups[a_sample][b_var]["qelikenot"].Add(
                    groups[a_sample][b_var][c_cat]
                )

    if dotuned:
        cat_order = list([
            "qelikenot",
            "qelike"
        ])


# build an order which puts backgrounds below signal (assumes signal is first in list)
bestorder = []

ROOT.gStyle.SetOptStat(0)
template = "%s___%s___%s___%s"

for a_sample in groups.keys():
    # for b_var in groups[a_sample].keys():
    for b_var in varstodo:
        if b_var not in groups[a_sample].keys(): continue
        data_var = b_var.split('_')[0]
        if data_var not in groups[a_sample].keys() and not noData:
            print("Couldn't find data_var. Skipping ", b_var)
            continue
        first = 0
        if first == 0:
            print("starting with var ", b_var)

        thename = "%s_%s"%(a_sample,b_var)
        thetitle = "%s %s"%(a_sample,b_var)

        cc = CCQECanvas(thename, thename)
        leg = CCQELegend(0.65, 0.65, 0.95, 0.95)
        leg.SetNColumns(2)

        plottitle=samplenames[a_sample]
        if dotuned:
            plottitle = "Tuned "+plottitle
        if not dotypes:
            for c_cat in cat_order:
                # Skips cats that aren't in this sample
                if c_cat not in groups[a_sample][b_var].keys():
                    print("skipping cat not found in groups: ", c_cat)
                    continue
                if c_cat == "data" and not noData:
                    leg.AddEntry(groups[a_sample][data_var]["data"], "Data", "p")
                    continue
                if first == 0:  # make a stack
                    stack = THStack(name.replace("reconstructed","stack"),"")
                    first+=1
                hist = groups[a_sample][b_var][c_cat]
                for pid in bin_pid_order:
                    tmp_h_pid = hist.ProjectionX(
                        str(hist.GetName() + "_" + bin_pid[pid]), pid, pid
                    )
                    tmp_h_pid.SetFillColor(bin_pid_colors[pid])
                    tmp_h_pid.SetLineColor(bin_pid_colors[pid])
                    if c_cat in backgrounds:
                        tmp_h_pid.SetFillStyle(3244)

                    stack.Add(tmp_h_pid)
                # Jank to get legend order correct
                # if not noData:
                #     leg.AddEntry(groups[a_sample][data_var]["data"], "Data", "p")
                for pid in reversed(bin_pid_order):
                    tmp_h_pid = hist.ProjectionX(
                        str(hist.GetName() + "_" + bin_pid[pid]), pid, pid
                    )
                    tmp_h_pid.SetFillColor(bin_pid_colors[pid])
                    tmp_h_pid.SetLineColor(bin_pid_colors[pid])
                    if c_cat in backgrounds:
                        tmp_h_pid.SetFillStyle(3244)

                    # stack.Add(tmp_h_pid)
                    if c_cat in backgrounds:
                        leg.AddEntry(tmp_h_pid, bin_pid[pid] + "-not", "f")
                    else:
                        leg.AddEntry(tmp_h_pid, bin_pid[pid], "f")

        else:
            # bestorder = list(groups[a_sample][b_var].keys()).copy()
            bestorder = list(["qelikenot","qelike"]).copy()
            # signal = bestorder[1]
            # bestorder = bestorder[2:]
            # bestorder.append(signal)
            for c_type in bestorder:
                if first==0:
                    stack = THStack(name.replace("types","stack"),"")
                    first+=1
                for index in groups[a_sample][b_var][c_type].keys(): #fill the stack
                    if index == 0:
                        continue
                    if index not in groups[a_sample][b_var][c_type]:
                        continue

                    h = groups[a_sample][b_var][c_type][index]
                    stack.Add(h)
                    leg.AddEntry(h,process[index],'f')
        # smax = stack.GetMaximum()
        # # print ("max",smax,dmax)
        # max_multiplier = 1.3
        # stack.SetMaximum(1.3 * smax)
        stack.SetTitle("")
        stack.Draw("")

        stack.GetYaxis().SetTitle("Counts #times 10^{3}")
        stack.GetYaxis().CenterTitle()
        stack.GetYaxis().SetTitleSize(0.05)
        # stack.GetYaxis().SetLabelSize(0.05)

        # for bin in bin_pid.keys():
        #     stack.GetXaxis().SetBinLabel(bin, bin_pid[bin])
        if b_var not in titles.keys():
            print(
                "Title missing for ",
                b_var,
                " going with default title ",
                b_var.split("_")[0],
            )
            stack.GetXaxis().SetTitle(b_var.split("_")[0])
        else:
            stack.GetXaxis().SetTitle(titles[b_var])

        stack.GetXaxis().CenterTitle()
        stack.GetXaxis().SetTitleSize(0.05)

        stack.Draw("hist")
        if not noData:
            groups[a_sample][data_var]["data"].Draw("PE same")
        leg.Draw()
        prelim = AddPreliminary()
        prelim.DrawLatex(0.62,0.62,"MINER#nuA Work In Progress")
        titleonplot = MakeTitleOnPlot()
        titleonplot.DrawLatex(0.37,0.90,plottitle)
        cc.Draw()
        # cc.SetLogy()
        canvas_name=thename+"_FinalStates"
        if dotuned:
            canvas_name = thename+"_FinalStates_tuned"
        cc.Print(os.path.join(outdirname,canvas_name+".png"))
