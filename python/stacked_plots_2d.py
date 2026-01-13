# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023


# from re import L
import sys,os
import ROOT
from ROOT import gROOT,gStyle, TFile,THStack,TH1D,TCanvas, TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex, TString
from PlotUtils import MnvH1D, MnvH2D, HyperDimLinearizer, GridCanvas

import json, re
import math
import datetime
mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")

TEST=False
global_noData=False  # use this to plot MC only types
sigtop = True # use this to place signal on top of background
dotuned= True
dowarp = False
dopanelwidth = True

doareanorm = False

ROOT.TH1.AddDirectory(ROOT.kFALSE)
legendfontsize = 0.042

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


def CCQECanvas(name,title,xsize=1100,ysize=720):
    c2 = ROOT.TCanvas(name,title,xsize,ysize)
    # c2.SetLeftMargin(0.1)
    c2.SetRightMargin(0.04)
    c2.SetLeftMargin(0.1)
    c2.SetTopMargin(0.04)
    c2.SetBottomMargin(0.1)
    return c2

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

    print("PanelCanvas: Making a grid canvas named "+name+" with a grid of ",n_xbins,"    ",n_ybins,"    ",grid_x,"    ",grid_y)

    # gc2 = PlotUtils.GridCanvas(name, grid_x, grid_y, x_size, y_size)
    # gc2 = GridCanvas(name, grid_x, grid_y, x_size, y_size)
    gc2 = GridCanvas(name, grid_x, grid_y, x_size, y_size)
    # gc2.SetRightMargin(0.05)
    # gc2.SetLeftMargin(0.05)
    gc2.ResetPads()

    return gc2


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
    "data",
    "qelike",
    "chargedpion",
    "neutralpion",
    # "multipion",
    "other"
]
catsnames = {
"data":"data", 
"qelike":"QElike",
"chargedpion":"1#pi^{#pm}",
"neutralpion":"1#pi^{0}",
"multipion":"N#pi",
"other":"Other"
}

catscolors = {
"data":ROOT.kBlack, 
"qelike":ROOT.kBlue-6,
"chargedpion":ROOT.kMagenta-6,
"neutralpion":ROOT.kRed-6,
"multipion":ROOT.kGreen-6,
"other":ROOT.kYellow-6
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

var_short_names = {
    "ERemoved": "E_{Removed}",
    "EAvail": "E_{Avail}",
    "EExcess": "E_{Excess}",
    "EAvailFromTruthBlobs": "E_{Avail}^{TruthBlobs}",
    "VisEMissing": "Vis E_{Missing}",
    "InvisEMissing": "Invis E_{Missing}",
    "recoil": "recoil",
}

if len(sys.argv) == 1:
    print ("enter root file name and optional 2nd argument to get tuned version")
flag = "types_"
filename = sys.argv[1]
if len(sys.argv)> 2:
    flag = "tuned_type_"


f = TFile.Open(filename,"READONLY")

plotdirbase = os.getenv("OUTPUTLOC")

plotdir = MakePlotDir("Dists2D")
dirname = filename.replace(".root", "_Dists2D")
# outfilename=filebasename1.replace(".root","_2DPlots")
outdirname = os.path.join(plotdir, dirname)
if not os.path.exists(outdirname):
    print(outdirname)
    os.mkdir(outdirname)
keys = f.GetListOfKeys()

h_pot = f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(2)
POTScale = dataPOT / mcPOTprescaled
print("POTScale: ",POTScale)

if "varsFile" not in keys:
    bigvarconfig_string = f.Get("varsFile_5A").GetTitle()
else:
    bigvarconfig_string = f.Get("varsFile").GetTitle()
bigvarconfig_dict = json.loads(re.sub("//.*", "", bigvarconfig_string, flags = re.MULTILINE))


groups = {}
scaleX = [
    "ERemoved", 
    "EExcess",
    # "InvisEMissing",
    "VisEMissing", 
    "ERemovedFromTruthBlobs",
]

scaleY = []#"recoil","EAvail"]


# find all the valid histogram and group by keywords
ncats = 5
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
    if "types" in parse[4]:
        continue
    if "simulfit" in parse[4]:
        continue
    # reorder so category is last
    if hist != "h2D": continue
    # if cat == "qelikenot": continue
    if cat not in catstodo: continue
    if sample not in groups.keys():
        groups[sample] = {}
        
    if variable not in groups[sample].keys():
        groups[sample][variable] = {}
        
    if cat not in groups[sample][variable].keys():
        groups[sample][variable][cat] = {}


# now that the structure is created, stuff histograms into it after scaling for POT
for k in keys:
    name = k.GetName()
    parse = name.split("___")
    if len(parse) < 5: continue
    hist = parse[0]
    if hist != "h2D": continue # only 1d
    sample = parse[1]
    cat = parse[2]
    # if cat == "qelikenot": continue
    if cat not in catstodo: continue
    variable = parse[3]
    if "reconstructed" not in parse[4]: continue
    if "types" in parse[4]:
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
    # h.SetFillColor(catscolors[cat])
    # h.SetLineColor(ROOT.kBlack)
    
    if "data" in cat:
        index = 0
        h = f.Get(name)
        if h.GetEntries() <= 0: continue
        # h.Scale(1.,"width")
        # h.Scale(0.001,"width")
        # h.SetMarkerStyle(20)
        # h.SetMarkerSize(1.5)
    if "data" not in cat:
        print("scaling hist ",h.GetName())
        # print("POTscale: ", POTScale)
        # h.Scale(POTScale*0.001,"width") #scale to data
        h.Scale(POTScale) #scale to data
        # h.Scale(POTScale,"width") #scale to data
    # if cat in ["chargedpion", "neutralpion", "multipion", "other"]:
    #     h.SetFillStyle(3244)
    groups[sample][variable][cat]=h
    if "bins" not in groups[sample][variable].keys():
        bins = []
        for var in variable.split("_"):
            varconfig = bigvarconfig_dict["1D"][var]
            if "bins" in varconfig.keys():
                bins1D = [float(tmpbin) for tmpbin in varconfig["bins"]]
                bins.append(bins1D)

                continue
            elif "nbins" in varconfig.keys():
                mini = varconfig["min"]
                maxi = varconfig["max"]
                width = (maxi - mini)/varconfig["nbins"]
                bins1D = [mini + tmpbin * width for tmpbin in range(0,varconfig["nbins"]+1)]
                # print(bins1D)
                bins.append(bins1D)
        print(bins)
        groups[sample][variable]["bins"] = bins

        #print ("data",groups[hist][sample][variable][c])

# "h___MultiplicitySideband___qelike___pzmu___reconstructed"
# h___MultipBlobSideband___other___pzmu___reconstructed
# do the plotting


# build an order which puts backgrounds below signal (assumes signal is first in list)
bestorder = []
cat_order = list([
    "other",
    # "multipion",
    "neutralpion",
    "chargedpion",
    "qelike",
    "data"
])
ROOT.gStyle.SetOptStat(0)
template = "%s___%s___%s___%s"
print("here")
for a_sample in groups.keys():

    datasample = a_sample
    if a_sample == "QElike_warped":
        datasample = "QElike"
    if a_sample == "QElike" and dowarp: continue

    for b_var in groups[a_sample].keys():
        print("starting on ", a_sample,b_var)
        histskeys = groups[a_sample][b_var].keys()
        n_xbins = groups[a_sample][b_var]["qelike"].GetNbinsX()
        n_ybins = groups[a_sample][b_var]["qelike"].GetNbinsY()
        
        # print("histskeys ", histskeys)
        noData = global_noData
        if "data" not in histskeys:
            print("switched to nodata")
            noData = True
        
        for projY in [True, False]:
            proj_bin_range = []
            n_projbins_raw = 0

            if projY:
                n_projbins_raw = n_xbins
            else:
                n_projbins_raw = n_ybins
            proj_bin_range = range(1, n_projbins_raw+1) # TODO check upper bound on this
            grid_dict = {}
            for projbin in proj_bin_range:
                if projbin not in grid_dict.keys():
                    grid_dict[projbin] = {}
                firstmc = True
                for c_cat in cat_order:
                    if c_cat == "data" and noData: continue
                    if c_cat not in grid_dict[projbin].keys():
                        grid_dict[projbin][c_cat] = {}
                    tmp_hist2D = MnvH2D(groups[a_sample][b_var][c_cat].Clone())
                    width = 1.0
                    if projY:
                        tmp_proj_name ="projY_%0.3d"%projbin
                        width = tmp_hist2D.GetXaxis().GetBinWidth(projbin)
                        tmp_proj = tmp_hist2D.ProjectionY(tmp_proj_name, projbin, projbin)
                    else:
                        tmp_proj_name ="projX_%0.3d"%projbin
                        width = tmp_hist2D.GetYaxis().GetBinWidth(projbin)
                        tmp_proj = tmp_hist2D.ProjectionX(tmp_proj_name, projbin, projbin)
                    if dopanelwidth:
                        tmp_proj.Scale(1./width,"width")
                    else:
                        tmp_proj.Scale(1.,"width")
                    if c_cat == "data":
                        tmp_proj.SetMarkerStyle(20)
                        tmp_proj.SetMarkerColor(ROOT.kBlack)
                        tmp_proj.SetLineColor(ROOT.kBlack)
                    else:
                        tmp_proj.SetFillColor(catscolors[c_cat])
                        tmp_proj.SetLineColor(catscolors[c_cat])
                        # if c_cat in backgrounds: #TODO backgrounds
                        #     tmp_proj.SetFillStyle(3244)
                    
                    grid_dict[projbin][c_cat] = tmp_proj
                    if c_cat!="data":
                        if firstmc:
                            tmp_mctot = tmp_proj.Clone()
                            firstmc = False
                        else:
                            tmp_mctot.Add(tmp_proj)
                grid_dict[projbin]["mctot"] = tmp_mctot

            global_max = 0.0
            tmpglobal_max = 0.0
            if doareanorm and not noData:
                for projbin in grid_dict.keys():
                    tmp_mcarea_scale = 1.0
                    tmp_mcarea = grid_dict[projbin]["mctot"].Integral(1,grid_dict[projbin]["mctot"].GetNbinsX())
                    tmp_dataarea = grid_dict[projbin]["data"].Integral(1,grid_dict[projbin]["data"].GetNbinsX())
                    if tmp_mcarea != 0.0 and tmp_dataarea != 0.0:
                        tmp_mcarea_scale = tmp_dataarea/tmp_mcarea
                        # print("tmp_mcarea_scale",tmp_mcarea_scale, tmp_dataarea, tmp_mcarea)
                    for cat in grid_dict[projbin].keys():
                        if cat in ["data", "stack", "multiplier","dataratio","mcratio"]: continue
                        grid_dict[projbin][cat].Scale(tmp_mcarea_scale)
            if not noData:
                for projbin in grid_dict.keys():
                    tmp_data = grid_dict[projbin]["data"].Clone()
                    tmp_mctot = grid_dict[projbin]["mctot"].Clone()
                    data_ratio = tmp_data.Clone("datamcratio")
                    data_ratio.Divide(tmp_data, tmp_mctot)
                    data_ratio.SetMinimum(0.5)
                    data_ratio.SetMaximum(1.5)
                    data_ratio.SetTitle("")
                    data_ratio.GetYaxis().SetTitle("Data / MC")
                    data_ratio.GetYaxis().CenterTitle()

                    grid_dict[projbin]["dataratio"] = data_ratio

                    mcratio = TH1D(tmp_mctot.GetTotalError(False, True, False))
                    for ibin in range(1, mcratio.GetXaxis().GetNbins() + 1):
                        mcratio.SetBinError(ibin, max(mcratio.GetBinContent(ibin), 1.0e-9))
                        mcratio.SetBinContent(ibin, 1.0)
                    mcratio.SetLineColor(ROOT.kRed)
                    mcratio.SetLineWidth(3)
                    mcratio.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
                    grid_dict[projbin]["mcratio"] = mcratio

                    straightline = grid_dict[projbin]["mcratio"].Clone("mcline")
                    straightline.SetFillStyle(0)
                    straightline.SetFillColorAlpha(ROOT.kPink + 1, 0.0)
                    grid_dict[projbin]["mcline"] = mcratio


            for projbin in grid_dict.keys():
                smax = 1.2*grid_dict[projbin]["mctot"].GetMaximum()
                # print("smax", smax)
                if not noData:
                    dmax = 1.2*grid_dict[projbin]["data"].GetMaximum()
                    # print("dmax", dmax)
                    tmpglobal_max = max(smax, dmax, global_max)
                else:
                    tmpglobal_max = max(smax, global_max)  
                global_max = tmpglobal_max
            print("global max", global_max)
            bin_scales = []
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
                if not noData:
                    grid_dict[projbin]["data"].Scale(tmp_pad_scale)
                tmp_stack = THStack("stack","")
                for c_cat in cat_order:
                    if c_cat in ["data","mctot","stack","multiplier","dataratio","mcratio","mcline"]: continue
                    tmp_hist = TH1D(grid_dict[projbin][c_cat].Clone())
                    tmp_hist.Scale(tmp_pad_scale)
                    tmp_stack.Add(tmp_hist)
                grid_dict[projbin]["stack"] = tmp_stack
            
            gridname = "%s_%s" % (a_sample, b_var)
            if projY:
                n_xcanvasbins = n_ybins
                n_ycanvasbins = n_xbins
                gridname += "_projY"
            else:
                n_xcanvasbins = n_xbins
                n_ycanvasbins = n_ybins
                gridname += "_projX"
            
            gc2 = PanelCanvas(gridname, n_xcanvasbins, n_ycanvasbins)
            gc2.SetYTitle("Counts/unit")
            raw_x_title = b_var.split("_")[0]
            raw_y_title = b_var.split("_")[1]
            if projY:
                x_title = raw_y_title
                y_title = raw_x_title

            else:
                x_title = raw_x_title
                y_title = raw_y_title

            if x_title in var_short_names.keys():
                x_title = var_short_names[x_title]

            gc2.SetXTitle(x_title)
            gc2.Draw()

            pad_index = 1
            for projbin in grid_dict.keys():
                pad = gc2.cd(pad_index)
                pad_index += 1
                if not noData:
                    # dmax = grid_dict[projbin]["data"].GetMaximum()
                    grid_dict[projbin]["data"].SetMaximum(global_max)
                    grid_dict[projbin]["data"].SetMinimum(0)
                    grid_dict[projbin]["data"].GetXaxis().SetNdivisions(505)
                    grid_dict[projbin]["data"].GetYaxis().SetNdivisions(505)
                    grid_dict[projbin]["data"].Draw("")
                    grid_dict[projbin]["stack"].Draw("hist, same")
                    grid_dict[projbin]["data"].Draw("PE, same")
                    grid_dict[projbin]["data"].Draw("Axis, same")
                else:
                    # grid_dict[projbin]["stack"].Draw("")
                    grid_dict[projbin]["mctot"].SetTitle(b_var)

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
                multip_latex.SetTextSize(0.028)
                multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.1),"#times {:g}".format(float('{:.{p}g}'.format(multip, p=2))))

                if projY:
                    tmp_projaxis_bins = groups[a_sample][b_var]["bins"][0]
                    tmp_var = b_var.split("_")[0]
                else: 
                    tmp_projaxis_bins = groups[a_sample][b_var]["bins"][1]
                    tmp_var = b_var.split("_")[1]
                if tmp_var not in var_short_names.keys():
                    tmp_varshort = "var"
                else:
                    tmp_varshort = var_short_names[tmp_var]
                # print(tmp_projaxis_bins)
                loedge = tmp_projaxis_bins[projbin-1]
                hiedge = tmp_projaxis_bins[projbin]

                range_string = "{mini} < {var} < {maxi}".format(mini = round(loedge,3), var = tmp_varshort, maxi = round(hiedge,3))

                binrange_latex = ROOT.TLatex()
                binrange_latex.SetTextAlign(33) # top right
                binrange_latex.SetNDC()
                binrange_latex.SetTextFont(42)
                binrange_latex.SetTextSize(0.025)
                binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)
                if projY and b_var.split("_")[1] in scaleX:
                    pad.SetLogx()
                if not projY and b_var.split("_")[0] in scaleX:
                    pad.SetLogx()

            gc2.SetHistTexts()
            gc2.Draw()
            # gc2.SetXTitle(x_title)

            canvas_name = gridname + "_FinalStates"
            if dotuned:
                canvas_name = gridname + "_FinalStates_tuned"
            gc2.Print(os.path.join(outdirname, canvas_name + ".png"))
            gc2.Print(os.path.join(outdirname, "source", canvas_name + ".C"))

            if noData:
                del gc2
                continue

            # gc2_ratio = PanelCanvas(gridname + "_ratio", n_xcanvasbins, n_ycanvasbins)
            # gc2_ratio.cd()
            gc2.cd()
            gc2.ResetPads()
            gc2.SetYTitle("Data/MC")
            gc2.Modified()
            gc2.Update()

            ratio_pad_index = 1
            for projbin in grid_dict.keys():
                # ratio_pad = gc2_ratio.cd(ratio_pad_index)
                ratio_pad = gc2.cd(ratio_pad_index)
                # ratio_pad.cd()
                
                # tmp_data = grid_dict[projbin]["data"].Clone()
                # tmp_mctot = grid_dict[projbin]["mctot"].Clone()
                # data_ratio = tmp_data.Clone("datamcratio")
                # data_ratio.Divide(tmp_data, tmp_mctot)
                # data_ratio.SetMinimum(0.5)
                # data_ratio.SetMaximum(1.5)
                # data_ratio.SetTitle("")
                # data_ratio.GetYaxis().SetTitle("Data / MC")
                # data_ratio.GetYaxis().CenterTitle()
                # data_ratio.Print()

                # mcratio = TH1D(tmp_mctot.GetTotalError(False, True, False))
                # for ibin in range(1, mcratio.GetXaxis().GetNbins() + 1):
                #     mcratio.SetBinError(ibin, max(mcratio.GetBinContent(ibin), 1.0e-9))
                #     mcratio.SetBinContent(ibin, 1.0)
                # mcratio.SetLineColor(ROOT.kRed)
                # mcratio.SetLineWidth(3)
                # mcratio.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
                # mcratio.Print()

                # straightline = mcratio.Clone()
                # straightline.SetFillStyle(0)


                # data_ratio.Draw("PE")
                # # mcratio.Draw("E2 same")
                # mcratio.Draw("E2 same")
                # straightline.Draw("hist same")
                # data_ratio.Draw("PE same")

                grid_dict[projbin]["dataratio"].Draw()
                grid_dict[projbin]["mcratio"].Draw("same E2")
                grid_dict[projbin]["mcline"].Draw("hist same")
                grid_dict[projbin]["dataratio"].Draw("same")


                if projY and b_var.split("_")[1] in scaleX:
                    ratio_pad.SetLogx()
                if not projY and b_var.split("_")[0] in scaleX:
                    ratio_pad.SetLogx()
                ratio_pad.Draw()
                # ratio_pad.Modified()
                # ratio_pad.Update()
                ratio_pad_index += 1
            
            # gc2_ratio.Draw()
            gc2.SetHistTexts()

            gc2.Draw()
            raio_canvas_name = gridname + "_FinalStates_Ratio"
            if dotuned:
                raio_canvas_name = gridname + "_FinalStates_Ratio_tuned"
            # gc2_ratio.Print(os.path.join(outdirname, raio_canvas_name + ".png"))
            gc2.Print(os.path.join(outdirname, raio_canvas_name + ".png"))
            gc2.Print(os.path.join(outdirname, "source", raio_canvas_name + ".C"))

            # del gc2_ratio
            del gc2

