# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023


import sys,os
import ROOT
from ROOT import gROOT,gStyle, TFile,THStack,TH1D,TCanvas, TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex, TString
import datetime

mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")


TEST=False
noData=False  # use this to plot MC only types
sigtop=True # use this to place signal on top of background
manualrange = False
dowarp = True

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


def CCQECanvas(name,title,xsize=1000,ysize=1500):
    c2 = ROOT.TCanvas(name,title,xsize,ysize)
    # c2.SetLeftMargin(0.10)
    # c2.SetRightMargin(0.05)
    # c2.SetBottomMargin(0.15)
    return c2

def CCQELegend(xlow,ylow,xhigh,yhigh):
    leg = ROOT.TLegend(xlow,ylow,xhigh,yhigh)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    return leg

# def AddPreliminary(x,y):
#     text = "MINER#nuA Work In Progress"
#     font = 112
#     color = ROOT.kRed +1
#     latex = ROOT.TLatex(x,y,text)
#     latex.SetNDC()
#     latex.SetTextSize(12)
#     latex.SetTextColor(color)
#     latex.SetTextFont(font)
#     latex.SetTextAlign(22)
#     return latex

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

samplenames = {
    "QElike": "QElike",
    "QElike_warped": "no 2p2h tune",
    "QElike_2track": "QElike 2track Sample",
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

if len(sys.argv) == 1:
    print ("enter root file name and optional 2nd argument to get tuned version")
flag = "types_"
filename = sys.argv[1]
if len(sys.argv)> 2:
    flag = "tuned_type_"


f = TFile.Open(filename,"READONLY")

dirname = filename.replace(".root","_types")
plotdir = MakePlotDir("typePlots1D")
outdirname = os.path.join(plotdir, dirname)
if not os.path.exists(outdirname): 
    print(outdirname)
    os.mkdir(outdirname)

keys = f.GetListOfKeys()

h_pot = f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(2)
POTScale = dataPOT / mcPOTprescaled

groups = {}
scaleX = ["Q2QE"]
scaleY = [
    # "EAvail",
    # "recoil"#, 
    # "CosMuonPionAngle"
]
prettyvarnames = {
    "EAvail": "E_{Avail}",
    "recoil": "recoil"
}

# find all the valid histogram and group by keywords
ncats = 0
for k in keys:
    name = k.GetName()
    if "___" not in name:
        continue
    parse = name.split("___")
    if len(parse) < 5: continue
    #print (parse)
    # names look like : hist___Sample___category__variable___types_0;
    if not flag in parse[4] and not "data" in parse[2]: continue
    hist = parse[0]
    sample = parse[1]
    cat = parse[2]
    variable = parse[3]
    # reorder so category is last
    if hist == "h2D": continue
    if cat not in whichcats:
        continue
    if hist not in groups.keys():
        groups[hist] = {}
        #legs[parse[0]] = {}
    if sample not in groups[hist].keys():
        groups[hist][sample] = {}
        
    if variable not in groups[hist][sample].keys():
        groups[hist][sample][variable] = {}
        
    if cat not in groups[hist][sample][variable].keys():
        groups[hist][sample][variable][cat] = {}
    # neehist to know the #of categories later
    #print ("cats",groups[d][s][variable].keys())
    if len(groups[hist][sample][variable].keys())-1 > ncats:
        ncats = len(groups[hist][sample][variable].keys())-1

# now that the structure is created, stuff histograms into it after scaling for POT
for k in keys:
    name = k.GetName()
    parse = name.split("___")
    if len(parse) < 5: continue
    hist = parse[0]
    if hist == "h2D": continue # only 1d
    sample = parse[1]
    cat = parse[2]
    variable = parse[3]
    # these are stacked histos
    if cat not in whichcats:
        continue
    if flag in parse[4]:
        index = int(parse[4].replace(flag,""))
        #print ("check",index,name)
        h = f.Get(name)
        if h.GetEntries() <= 0: continue
        if TEST: h.Scale(2)
        h.Scale(POTScale,"width") #scale to data
        
        h.SetFillColor(colors[index])
        # h.SetLineColor(colors[index]+2)
        if cat == "qelikenot":  # make a better way to do this, maybe code in the input file?
            index += 10
            h.SetFillStyle(3244)
        groups[hist][sample][variable][cat][index]=h
        
        #print ("mc",groups[hist][sample][variable][cat])
    # this is data
    if "data" in cat:
        index = 0
        h = f.Get(name)
        
        if h.GetEntries() <= 0: continue
        h.Scale(1.,"width")
        h.SetMarkerStyle(20)
        groups[hist][sample][variable][cat][index]=h
    print(" got hist ", name) 
        #print ("data",groups[hist][sample][variable][c])


# do the plotting


# build an order which puts backgrounds below signal (assumes signal is first in list)
bestorder = []

ROOT.gStyle.SetOptStat(0)
template = "%s___%s___%s___%s"

for a_hist in groups.keys():
    if a_hist != "h": continue # no 2D
    # print ("a is",a)
    for b_sample in groups[a_hist].keys():
        datasample = b_sample
        if b_sample == "QElike_warped":
            datasample = "QElike"
        if dowarp and b_sample == "QElike":
            continue
        for c_var in groups[a_hist][b_sample].keys():

            first = 0
            leg = CCQELegend(0.5,0.7,0.9,0.9)
            leg.SetNColumns(2)
            thename = "%s_%s"%(b_sample,c_var)
            thetitle = "%s %s"%(b_sample,c_var)
            # do the data first
            cc = CCQECanvas(name,name)
            if c_var in scaleX:
                cc.SetLogx()
            if c_var in scaleY:
                cc.SetLogy()

            data = TH1D()
            # if len(groups[a_hist][b_sample][c_var]["data"]) < 1:
            #     print (" no data",a_hist,b_sample,c_var)
            #     continue

            if noData:
                dmax = 0.0
            # data.Draw("PE")
            if not noData: 
                data = TH1D(groups[a_hist][datasample][c_var]["data"][0])
                data.SetTitle("%s %s"%(samplenames[b_sample],prettyvarnames[c_var]))
                data.GetYaxis().SetTitle("Counts/unit (bin width normalized)")
                dmax = data.GetMaximum()
                leg.AddEntry(data,"data","pe")

                data.Print()

            # do the MC
            # move the first category to the top of the plot

            # if "QElike" not in b_sample:
            #     sigtop = False
            # else:
            #     sigtop = True
            if sigtop:
                bestorder = list(groups[a_hist][b_sample][c_var].keys()).copy()
                # assume data = type 0, signal is type 1, rest are after that
                print ("pre-bestorder",bestorder)
                
                if not noData:
                    if not dowarp:
                        signal = bestorder[1]
                        bestorder = bestorder[2:]
                        bestorder.append(signal)
                    else:
                        bestorder = ["qelikenot", "qelike"]
                else:
                    signal = bestorder[0]
                    bestorder = bestorder[1:]
                    bestorder.append(signal)
            else:
                bestorder = list(groups[a_hist][b_sample][c_var].keys()).copy()
            print ("bestorder",bestorder)
            for d_type in bestorder:
                print("d_type", d_type)
                if d_type == "data": 
                    continue
                if first == 0: # make a stack
                    stack = THStack(name.replace(flag,"stack"),"")
                first+=1
                for index in groups[a_hist][b_sample][c_var][d_type].keys(): #fill the stack
                    # print("index",index,bestorder,groups[a_hist][b_sample][c][d])
                    if index == 0: continue
                    if index not in groups[a_hist][b_sample][c_var][d_type]: continue
                    # print ("do this one ",  index,bestorder)
                    h = groups[a_hist][b_sample][c_var][d_type][index]
                    stack.Add(h)
                    leg.AddEntry(h,process[index],'f')
            smax = stack.GetMaximum()
            if c_var=="PionAngle":
                if b_sample == "LoPionThetaSideband":
                    data.GetXaxis().SetRangeUser(0.,90.)            
                elif b_sample == "HiPionThetaSideband":
                    data.GetXaxis().SetRangeUser(90.,180.)
            # print ("max",smax,dmax)

            if not noData:
                if smax > dmax:
                    data.SetMaximum(smax*1.2)
                    stack.SetMaximum(smax*1.2)
                else:
                    data.SetMaximum(dmax*1.2)
                    stack.SetMaximum(dmax*1.2)
                if c_var=="CosMuonPionAngle":
                    data.SetMaximum(8000)
                    data.SetMinimum(0)
                    data.GetXaxis().SetRangeUser(-1.0,-0.5)
                if c_var in ["recoil","EAvail"]:
                    if c_var not in scaleY:
                        data.SetMinimum(0)
                        stack.SetMinimum(0)
                        data.SetMaximum(1800000)
                        stack.SetMaximum(1800000)
                    else:
                        # stack.Divide(data,1.)
                        data.SetMinimum(50)
                        stack.SetMinimum(50)
                        # data.SetMaximum(1000000)
                        # stack.SetMinimum(1000000)

                if not noData: 
                    data.Draw("PE")
                    stack.Draw("hist same")
                else:
                    data.Reset()
                    data.Draw("hist")  # need to this to get the axis titles from data
                    stack.Draw("hist same")
                if not noData: 
                    data.Draw("PE same")
            else: 
                stack.Draw("")
                if "IsoBlobsPrimaryMCPID" in c_var:
                    for bin in bin_pid.keys():
                        stack.GetXaxis().SetBinLabel(bin, bin_pid[bin])
                    stack.GetXaxis().SetLabelSize(0.07)
                    stack.GetXaxis().SetTitle("PID of parent of particle reconstructed as blob")
                    stack.GetXaxis().CenterTitle()
                stack.GetYaxis().SetTitle("Counts/unit")
                # stack.SetMaximum(smax*1.5)
                # stack.SetMinimum(0.0)

                stack.Draw("hist")

            leg.Draw()
            # prelim = AddPreliminary(0.1,0.9)
            # prelim.DrawLatexNDC(0.1,0.9,"MINER#nuA Work In Progress")
            # cc.Modified()
            cc.Update()
            cc.RedrawAxis()
            # if c_var in scaleX:
            #     cc.SetLogx()
            # if c_var in scaleY:
            #     cc.SetLogy()
            cc.Draw()
            outname = os.path.join(outdirname,thename+"_"+flag+".png")
            if manualrange: 
                outname = os.path.join(outdirname,thename+"_"+flag+"_manualxrange.png")
            cc.Print(outname)
            del cc
