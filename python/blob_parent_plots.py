# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023


from re import L
import sys,os
import ROOT
from ROOT import gROOT,gStyle, TFile,THStack,TH1D,TCanvas, TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex, TString

TEST=False
noData=True  # use this to plot MC only types
sigtop=True # use this to place signal on top of background
dotypes=True
dotuned=False
ROOT.TH1.AddDirectory(ROOT.kFALSE)

legendfontsize = 0.042


def CCQECanvas(name,title,xsize=1100,ysize=720):
    c2 = ROOT.TCanvas(name,title)

    # c2 = ROOT.TCanvas(name,title,xsize,ysize)
    # # c2.SetLeftMargin(0.1)
    # c2.SetRightMargin(0.04)
    # c2.SetLeftMargin(0.13)
    # c2.SetTopMargin(0.04)
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

catstodo = [
    # "data",
    "qelike",
    "qelikenot",
    # "chargedpion",
    # "neutralpion",
    # "multipion",
    # "other"
]

catsnames = {
    # "data":"data", 
    "qelike":"QElike",
    "qelikenot":"QElikeNot"
    # "chargedpion":"1#pi^{#pm}",
    # "neutralpion":"1#pi^{0}",
    # "multipion":"N#pi",
    # "other":"Other"
}

catscolors = {
    # "data":ROOT.kBlack,
    "qelike": ROOT.kBlue - 6,
    "qelikenot": ROOT.kRed - 6,
    "chargedpion": ROOT.kMagenta - 6,
    "neutralpion": ROOT.kRed - 6,
    "multipion": ROOT.kGreen - 6,
    "other": ROOT.kYellow - 6,
}

#  These are the vars that fill into bins
varstodo= [
    "NeutCandMCPID",
    # "NeutCandTopMCPID"
    "LeadingIsoBlobsPrimaryMCPID"
]
samplestodo= [
    "QElike",
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
    10: "Other"
}
process=["data","QE","RES","DIS","COH","","","","2p2h",""]
whichcats = ["data","qelike","qelikenot"]
nproc = len(process)
for x in range(0,nproc+1):
    process.append(process[x]+"-not")
colors = {
0:ROOT.kBlack,
1:ROOT.kBlue-6,
2:ROOT.kMagenta-6,
3:ROOT.kRed-6,
4:ROOT.kYellow-6,
5:ROOT.kWhite,
6:ROOT.kWhite,
7:ROOT.kWhite,
8:ROOT.kGreen-6,
9:ROOT.kTeal-6,
10:ROOT.kBlue-1,
11:ROOT.kBlue-10,
12:ROOT.kMagenta-10,
13:ROOT.kRed-10,
14:ROOT.kYellow-10,
15:ROOT.kGray,
16:ROOT.kBlack,
17:ROOT.kBlack,
18:ROOT.kGreen-6,
19:ROOT.kTeal-6}

samplenames = {
    "QElike": "QElike Signal Sample",
    "QElike0Blob": "QElike Signal w/o Blobs",
    "QElike1Blob": "QElike Signal w/ 1 Blob",
    "QElike2Blob": "QElike Signal w/ 2 Blobs",
    "QElikeOld": "2D Era QElike Signal Sample",
    # "BlobSideband": "1 #pi^{0} Sideband",
    "BlobSideband": "Blob Sideband",
    "MultipBlobSideband": "Multiple #pi Sideband",
    "HiPionThetaSideband": "Backward #pi^{#pm} Sideband",
    "LoPionThetaSideband": "Forward #pi^{#pm} Sideband",
    "TrackSideband": "Track Sideband"
}
if len(sys.argv) == 1:
    print ("enter root file name and optional 2nd argument to get tuned version")
flag = "types_"
filename = sys.argv[1]
if len(sys.argv)> 2:
    flag = "tuned_type_"


f = TFile.Open(filename,"READONLY")
dirname = filename.replace(".root","_FinalStates")
plotdir = "/Users/nova/git/plots/Winter2025MinervaCollab"
outdirname = os.path.join(plotdir,"dirname")
if not os.path.exists(outdirname): os.mkdir(outdirname)

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
    #print (parse)
    # names look like : hist___Sample___category__variable___types_0;
    # if not flag in parse[4] and not "data" in parse[2]: continue
    if "reconstructed" not in parse[4]: continue
    hist = parse[0]
    sample = parse[1]
    cat = parse[2]
    variable = parse[3]
    if "types" in parse[4] and not dotypes:
        continue
    if "simulfit" in parse[4]:
        continue
    # reorder so category is last
    if hist == "h2D": continue
    # if cat == "qelikenot": continue
    if cat not in catstodo: continue
    if variable not in varstodo:
        continue
    if sample not in samplestodo: continue
    
    if hist not in groups.keys():
        groups[hist] = {}
        #legs[parse[0]] = {}
    if sample not in groups[hist].keys():
        groups[hist][sample] = {}
        
    if variable not in groups[hist][sample].keys():
        groups[hist][sample][variable] = {}
        
    if cat not in groups[hist][sample][variable].keys():
        groups[hist][sample][variable][cat] = {}

# now that the structure is created, stuff histograms into it after scaling for POT
for k in keys:
    name = k.GetName()
    if "___" not in name:
        continue
    parse = name.split("___")
    # if len(parse) < 5: continue
    hist = parse[0]
    if hist == "h2D": continue # only 1d
    sample = parse[1]
    cat = parse[2]
    variable = parse[3]

    # if cat == "qelikenot": continue
    if cat not in catstodo: continue
    if variable not in varstodo: continue
    if sample not in samplestodo: continue
    if not dotypes:
        if "types" in parse[4]:
            continue
        if "reconstructed" not in parse[4]: continue
    else:
        if "types" not in parse[4]:
            continue
    
    if "simulfit" in parse[4]:
        continue
    if "tuned" not in parse[4] and dotuned and cat!="data":
        continue
    if "tuned" in parse[4] and not dotuned:
        continue
    # these are stacked histos
    h = f.Get(name).Clone()
    if h.GetEntries() <= 0: continue
    if not dotypes:
        print("here")
        h.SetFillColor(catscolors[cat])
        h.SetLineColor(catscolors[cat]+1)
        if "data" in cat:
            index = 0
            h = f.Get(name)
            if h.GetEntries() <= 0: continue
            # h.Scale(1.,"width")
            h.Scale(0.001,"width")
            h.SetMarkerStyle(20)
            h.SetMarkerSize(1.5)
        if "data" not in cat:
            print("scaling hist ",h.GetName())
            # print("POTscale: ", POTScale)
            h.Scale(POTScale*0.001,"width") #scale to data
            # h.Scale(POTScale,"width") #scale to data
        # if cat in ["chargedpion", "neutralpion", "multipion", "other"]:
        #     h.SetFillStyle(3244)
        groups[hist][sample][variable][cat]=h

    else: # if dotypes:
        if "types_" in parse[4]:
            index = int(parse[4].replace("types_",""))
            h.SetFillColor(colors[index])
            if cat == "qelikenot":
                index += 10
                h.SetFillStyle(3244)
            h.Scale(0.0001)
            groups[hist][sample][variable][cat][index]=h
            h.Print()

            print("here")


        # print ("data",groups[hist][sample][variable][c])

# "h___MultiplicitySideband___qelike___pzmu___reconstructed"
# h___MultipBlobSideband___other___pzmu___reconstructed
# do the plotting


# build an order which puts backgrounds below signal (assumes signal is first in list)
bestorder = []

ROOT.gStyle.SetOptStat(0)
template = "%s___%s___%s___%s"

for a_hist in groups.keys():
    if a_hist != "h": continue # no 2D
    # print ("a is",a)
    for b_sample in groups[a_hist].keys():
        for c_var in groups[a_hist][b_sample].keys():

            first = 0
            leg = CCQELegend(0.5,0.55,0.9,0.75)
            leg.SetNColumns(2)
            thename = "%s_%s"%(b_sample,c_var)
            thetitle = "%s %s"%(b_sample,c_var)

            cc = CCQECanvas(thename, thename)

            # do the data first
            # if c_var in scaleX:
            #     cc.SetLogx()
            # if c_var in scaleY:
            #     cc.SetLogy()

            # hist = TH1D(groups[a_hist][b_sample][c_var]["qelike"])

            # data = TH1D()
            # if len(groups[a_hist][b_sample][c_var]["data"]) < 1:
            #     print (" no data",a_hist,b_sample,c_var)
            #     continue

            # data = TH1D(groups[a_hist][b_sample][c_var]["data"])
            plottitle=samplenames[b_sample]
            if dotuned:
                plottitle = "Tuned "+plottitle
            # # data.SetTitle(plottitle)
            # data.SetTitle("")
            # # data.GetYaxis().SetTitle("Counts/unit (bin width normalized)")
            # # data.GetYaxis().SetTitle("Counts/unit")
            # data.GetYaxis().SetTitle("Counts #times 10^{3}/GeV^{2}")
            # data.GetYaxis().CenterTitle()
            # data.GetYaxis().SetTitleSize(0.05)
            # data.GetYaxis().SetLabelSize(0.04)

            # # data.GetXaxis().SetTitle("Recoil in GeV")
            # data.GetXaxis().CenterTitle()
            # data.GetXaxis().SetTitleSize(0.05)
            # data.GetXaxis().SetLabelSize(0.04)

            # dmax = data.GetMaximum()
            # if noData:
            #     dmax = 0.0
            # #data.Draw("PE")
            # if not noData: leg.AddEntry(data,"data","pe")

            # data.Print()

            if not dotypes:
                bestorder = list([
                    "other",
                    # "multipion",
                    "neutralpion",
                    "chargedpion",
                    "qelike"
                ])
                for d_cat in bestorder:
                    if d_cat == "data": continue
                    if first == 0: # make a stack
                        stack = THStack(name.replace("reconstructed","stack"),"")
                    first+=1
                    h = groups[a_hist][b_sample][c_var][d_cat]
                    stack.Add(h)
                    leg.AddEntry(h,catsnames[d_cat],"f")
            else:
                # bestorder = list(groups[a_hist][b_sample][c_var].keys()).copy()
                bestorder = list(["qelikenot","qelike"]).copy()
                # signal = bestorder[1]
                # bestorder = bestorder[2:]
                # bestorder.append(signal)
                for d_type in bestorder:
                    if first==0:
                        stack = THStack(name.replace("types","stack"),"")
                        first+=1
                    for index in groups[a_hist][b_sample][c_var][d_type].keys(): #fill the stack
                        if index == 0:
                            continue
                        if index not in groups[a_hist][b_sample][c_var][d_type]:
                            continue

                        h = groups[a_hist][b_sample][c_var][d_type][index]
                        stack.Add(h)
                        leg.AddEntry(h,process[index],'f')
            smax = stack.GetMaximum()
            # print ("max",smax,dmax)
            max_multiplier = 1.4

            stack.SetTitle("")
            stack.Draw("")

            stack.GetYaxis().SetTitle("Counts #times 10^{3}")
            stack.GetYaxis().CenterTitle()
            stack.GetYaxis().SetTitleSize(0.05)
            stack.GetYaxis().SetLabelSize(0.05)

            for bin in bin_pid.keys():
                stack.GetXaxis().SetBinLabel(bin, bin_pid[bin])
            stack.GetXaxis().SetTitle("PID of particle reconstructed as blob")
            stack.GetXaxis().CenterTitle()
            stack.GetXaxis().SetTitleSize(0.05)
            stack.GetXaxis().SetLabelSize(0.05)
            # if c_var in scaleY:
            #     max_multiplier = 2.0
            #     data.SetMinimum(500.)
            #     data.GetXaxis().SetRangeUser(0.0,0.5)
            # if smax > dmax:
            #     data.SetMaximum(smax*max_multiplier)
            #     stack.SetMaximum(smax*max_multiplier)
            # else:
            #     data.SetMaximum(dmax*max_multiplier)
            #     stack.SetMaximum(dmax*max_multiplier)
            # if not noData:
            #     data.Draw("PE")
            #     stack.Draw("hist same")
            # else:
            #     data.Reset()
            #     data.Draw("hist")  # need to this to get the axis titles from data
            #     stack.Draw("hist same")
            #     data.Draw("AXIS same")
            # if not noData:
            #     data.Draw("AXIS same")
            #     data.Draw("PE same")
            stack.Draw("hist")

            leg.Draw()
            prelim = AddPreliminary()
            prelim.DrawLatex(0.5,0.52,"MINER#nuA Work In Progress")
            titleonplot = MakeTitleOnPlot()
            titleonplot.DrawLatex(0.37,0.85,plottitle)
            cc.Draw()
            canvas_name=thename+"_FinalStates"
            if dotuned:
                canvas_name = thename+"_FinalStates_tuned"
            cc.Print(os.path.join(outdirname,canvas_name+".png"))


