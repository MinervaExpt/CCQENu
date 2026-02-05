# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023


from re import L
import sys,os
import ROOT
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
from PlotUtils import MnvH1D, MnvPlotter, HyperDimLinearizer, GridCanvas
import datetime
import ctypes
import math
import json, re

mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")

TEST=False
global_noData=False  # use this to plot MC only types
sigtop=True # use this to place signal on top of background
dotuned=False
dowarp = False
doratio = True
dotypes = False

ROOT.TH1.AddDirectory(ROOT.kFALSE)
_xsize = 1200.0
_ysize = 900.0

latex_x = 0.55
latex_y = 0.43

pad_lmarg = 0.10
pad_rmarg = 0.04
topmarg = 0.05
bottommarg = 0.3

legendfontsize = 0.05
legx1 = 0.7
legx2 = 1.0
legy1 = 0.65
legy2 = 0.95

lat_xoffset = 0.06
lat_yoffset = 0.04

scaleX = ["Q2QE"]
scaleY = ["EAvail","E_{Avail}"]#"recoil","EAvail"]

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

def GetInputHistDict(f, input_dict={}):
    keys = f.GetListOfKeys()
    print("Making dict of source hists in file %s..."%(f.GetName()))
    for k in keys:
        name = k.GetName()
        if "___" not in name:
            continue
        parse = name.split("___")
        if len(parse) < 5: continue
        #print (parse)
        # names look like : hist___Sample___category__variable___types_0;
        # if not flag in parse[4] and not "data" in parse[2]: continue
        hist = parse[0]
        sample = parse[1]
        cat = parse[2]
        variable = parse[3]
        recotrutype = parse[4]
        if "types" in recotrutype:
            print("WARNING: types not set up yet")
            continue
        if "simulfit" in recotrutype:
            continue
        if cat not in catstodo: continue
        # if "reconstructed" not in recotrutype:
        #     continue
        if "tuned" in recotrutype:
            sample += "_Tuned"
            recotrutype.replace("_tuned","")

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
            print("WARNING: hist ", name, " is empty. Skipping...")
            continue
        h.SetFillColor(catscolors[cat])
        h.SetLineColor(ROOT.kBlack)
        if "data" in cat:
            # h.Scale(1.0, "width")
            # h.Scale(1.0)
            h.SetMarkerStyle(20)
            h.SetMarkerSize(1.5)
        # else:
            # print("scaling hist ", name)
            # h.Scale(1.0, "width")
            # h.Scale(POTScale)
        input_dict[hist][sample][variable][cat][recotrutype] = h
    return input_dict

def GetAnalyzeHistDict(f, tuned=False, analyze_dict = {}):
    keys = f.GetListOfKeys()
    for k in keys:
        name = k.GetName()
        if "___" in name:
            continue
        if "_" not in name or name=="flux_dewidthed":
            continue
        print("found key", name)
        parse = name.split("_")
        hist = parse[0]
        sample = parse[1]
        var = parse[2]
        shift = 0
        if hist=="h2D":
            var+="_"+parse[3]
            shift = 1
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
            print("WARNING: hist ", name, " is empty. Skipping...")
            continue
        # TODO width normalize?
        h.Scale(1.0, "width")
        analyze_dict[hist][sample][var][stage] = h
    return analyze_dict



def MakeDataMCRatio(i_data, i_mctot):
    mcratio = i_data.Clone(str(i_data.GetName().replace("data", "datamcratio")))
    mcratio.Divide(i_data, i_mctot)
    return mcratio

# def GetChi2NDF(i_data, i_mctot):
#     chi2 = -9999.
#     if i_data.GetNbinsX() != i_mctot.GetNbinsX(): return chi2
#     nbins = i_data.GetNbinsX()
#     for i in range(1,nbins+1):
#         datacont = i_data.GetBinContent(i)
#         mccont = i_mctot.GetBinContnent(i)
#         if data

def DrawDataMCPlot1D(i_data_hist, i_mc_hist, x_title, y_title,outdirname):
    thename = "%s_%s_%s"%(b_sample,c_var,"sigma")
    thetitle = "%s %s %s"%(b_sample,c_var,"sigma")
    ysize = _ysize
    xsize = _xsize
    cc = ROOT.TCanvas(thename, thetitle, round(xsize), round(ysize))
    cc.SetLeftMargin(0.25)
    cc.SetRightMargin(0.15)
    cc.SetBottomMargin(0.15)
    cc.SetFrameLineWidth(1)

    mnv_data = i_data_hist.Clone()
    mnv_mc = i_mc_hist.Clone()
    
    print("here I am >>>>>>>>")
    mnv_data.Print()

    mnv_data.SetMarkerStyle(20)
    mnv_data.SetMarkerColor(ROOT.kBlack)
    mnv_data.SetLineWidth(2)
    mnv_data.SetLineColor(ROOT.kBlack)
    mnv_data.SetLineStyle(1)
    mnv_data.SetMarkerSize(1.5)

    data_hist = mnv_data.GetCVHistoWithError(True,False)
    data_stat = mnv_data.GetCVHistoWithStatError()

    data_hist.GetYaxis().SetTitle(sigma_ytitle)
    data_hist.GetYaxis().CenterTitle()
    data_hist.GetYaxis().SetTitleOffset(0.9)
    data_hist.GetYaxis().SetTitleSize(0.05)
    data_hist.GetYaxis().SetLabelSize(0.05)

    data_hist.SetMaximum(1.2* max(mnv_data.GetMaximum(),mnv_mc.GetMaximum()))

    mc_band = mnv_mc.GetCVHistoWithError(True,False)
    mc_band.SetFillColor(ROOT.kRed-10)
    mc_band.SetFillStyle(1001)
    mc_band.SetLineColor(ROOT.kRed)
    mc_band.SetMarkerStyle(0)

    mc_hist = mnv_mc.GetCVHistoWithError(True,False)
    mc_hist.SetFillColor(0)
    mc_hist.SetLineColor(2)
    mc_hist.SetLineStyle(1)
    mc_hist.SetLineWidth(3)

    # if doratio:
    top = TPad("hist", "hist", 0, 0.278, 1, 1)
    top.SetRightMargin(pad_rmarg)
    top.SetLeftMargin(pad_lmarg)
    top.SetTopMargin(topmarg)
    top.SetBottomMargin(0)
    top.SetFrameLineWidth(1)

    bottom = TPad("Ratio", "Ratio", 0, 0, 1, 0.278)
    bottom.SetRightMargin(pad_rmarg)
    bottom.SetLeftMargin(pad_lmarg)
    bottom.SetBottomMargin(bottommarg)
    bottom.SetTopMargin(0)
    bottom.SetFrameLineWidth(1)

    top.Draw()
    bottom.Draw()

    bottomArea = bottom.GetWNDC() * bottom.GetHNDC()
    topArea = top.GetWNDC() * top.GetHNDC()
    areaScale = topArea / bottomArea
    # Move to top pad for hists
    top.cd()
    if c_var in scaleY:
        top.SetLogy()
    leg_pos = "TR"

    data_hist.Draw("E1 X0")
    
    # if not issmooth:
    mc_band.Draw("SAME E2")
    mc_hist.Draw("SAME HIST")

    data_stat.Draw("SAME E1 X0")
    data_hist.Draw("Same E1 X0")

    titlewidth = mnvPlotter.GetLegendWidthInLetters(["Data","Simulation"])
    # print(titlewidth)
    x1 = ctypes.c_double(0)
    y1 = ctypes.c_double(0)
    x2 = ctypes.c_double(0)
    y2 = ctypes.c_double(0)
    mnvPlotter.DecodeLegendPosition(x1,y1,x2,y2, leg_pos, 2, titlewidth, 0.042)

    leg = TLegend(x1,y1,x2,y2)
    leg.SetNColumns(1)
    leg.SetBorderSize(0)
    leg.SetFillColor(-1)
    leg.AddEntry(data_hist, "Data","p")
    leg.AddEntry(mc_band, "MC","fl")

    leg.Draw()
    
    # if doratio:
    bottom.cd()

    # ratio = MnvH1D()
    ratio = MakeDataMCRatio(data_hist,mc_band)
    ratio.SetFillStyle(1001)
    ratio.SetMinimum(0.5)
    ratio.SetMaximum(1.5)

    ratio.SetLineColor(ROOT.kBlack)

    ratio.SetTitle("")            
    ratio.GetYaxis().SetTitle("Data / MC")
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetTitleSize(0.05 * areaScale)
    ratio.GetYaxis().SetTitleOffset(0.9 / areaScale)
    ratio.GetYaxis().SetLabelSize(0.05 * areaScale)
    ratio.GetYaxis().SetNdivisions(205)

    ratio.GetXaxis().SetTitle(vars_info[c_var]["title"])
    ratio.GetXaxis().CenterTitle()
    ratio.GetXaxis().SetTitleSize(0.05 * areaScale)
    ratio.GetXaxis().SetLabelSize(ratio.GetXaxis().GetLabelSize() * areaScale*1.5)
    ratio.SetLineWidth(round(2 / areaScale))
    ratio.Draw()

    # Now do mc uncertainties
    mcerror = TH1D()
    mnv_mc.SetFillStyle(1001)
    mcerror = TH1D(mnv_mc.GetTotalError(False, True, False))
    for bin in range(1, mcerror.GetXaxis().GetNbins() + 1):
        mcerror.SetBinError(bin, max(mcerror.GetBinContent(bin), 1.0e-9))
        mcerror.SetBinContent(bin, 1.0)
    mcerror.SetLineColor(ROOT.kRed)
    mcerror.SetLineWidth(3)
    # mcerror.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
    mcerror.SetFillColor(ROOT.kRed-10)
    mcerror.Draw("same E2")

    # Now do a line at 1
    straightline = TH1D()
    straightline = mcerror.Clone()
    straightline.SetFillStyle(0)
    straightline.Draw("hist same")

    ratio.Draw("same")
    top.cd()
    prelim = AddPreliminary()
    # titleonplot = MakeTitleOnPlot()
    prelim.DrawLatex(x1.value-lat_xoffset, y1.value-2*lat_yoffset-0.01, "MINER#nuA Work In Progress")
    # titleonplot.DrawLatex(0.37, 0.9, plottitle)

    canvas_name = thename + "_FinalStates"

    if dotypes:
        canvas_name = thename + "Types"
    if dotuned:
        canvas_name += "_tuned" 


    cc.Print(os.path.join(outdirname, canvas_name + ".png"))
    cc.Print(os.path.join(outdirname, "source", canvas_name + ".C"))
    del cc

def DrawErrorSummary1D():

    return 0

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
    
    print("PanelCanvas: Making a grid canvas named "+name+" with a grid of ",n_xbins,"    ",n_ybins,"    ",grid_x,"    ",grid_y)

    # gc2 = PlotUtils.GridCanvas(name, grid_x, grid_y, x_size, y_size)
    gc2 = GridCanvas(name, grid_x, grid_y, x_size, y_size)
    # gc2.SetRightMargin(0.01)
    # gc2.SetLeftMargin(0.1)
    gc2.ResetPads()

    return gc2

def MakeProjHistList(i_hist, projaxis="x"):
    ret_list = []
    hist = i_hist.Clone()
    n_projbins = 0
    if projaxis=="x":
        n_projbins = hist.GetNbinsY()
        proj_nametail = "_projybin"
    elif projaxis == "y":
        n_projbins = hist.GetNbinsX()
        proj_nametail = "_projxbin"
    else:
        print("ERROR: invalid projaxis %s, exiting"%(projaxis))
        sys.exit(1)

    for i in range(n_projbins):
        tmp_proj_name = hist.GetName() + proj_nametail + str(i)
        if projaxis == "x":
            tmp_proj = hist.ProjectionX(tmp_proj_name,i+1,i+1)
            ret_list.append(tmp_proj)
            continue
        else: # if projaxis == "y"
            tmp_proj = hist.ProjectionY(tmp_proj_name,i+1,i+1)
            ret_list.append(tmp_proj)
            continue
    return ret_list    

def GetDataHistsForPlot(mnv_datahist):
    mnvh = mnv_datahist.Clone()

    mnvh.SetMarkerStyle(20)
    mnvh.SetMarkerColor(ROOT.kBlack)
    mnvh.SetLineWidth(2)
    mnvh.SetLineColor(ROOT.kBlack)
    mnvh.SetLineStyle(1)
    mnvh.SetMarkerSize(1.5)

    hist = mnvh.GetCVHistoWithError(True,False)
    stat = mnvh.GetCVHistoWithStatError()

    return hist, stat

def GetMCHistsForPlot(mnv_mchist):
    mnvh = mnv_mchist.Clone()

    band = mnvh.GetCVHistoWithError(True,False)
    band.SetFillColor(ROOT.kRed - 10)
    band.SetFillStyle(1001)
    band.SetLineColor(ROOT.kRed)
    band.SetMarkerStyle(0)

    hist = mnvh.GetCVHistoWithError(True,False)
    hist.SetFillColor(0)
    hist.SetLineColor(2)
    hist.SetLineStyle(1)
    hist.SetLineWidth(3)

    return hist, band
    


def DrawDataMCPlot2D(i_data_hist, i_mc_hist, x_title, x_bins, y_title, y_bins, z_title, outdirname, do_ratio = False):
    data_mnv2d = i_data_hist.Clone()
    mc_mnv2d = i_mc_hist.Clone()
    n_xbins = data_mnv2d.GetNbinsX()
    n_ybins = data_mnv2d.GetNbinsY()
    print("hist n x bins: ",n_xbins,",\t hist n y bins: ",n_ybins)

    for projaxis in ["x","y"]:
        data_mnvproj_list = MakeProjHistList(data_mnv2d,projaxis)
        mc_mnvproj_list = MakeProjHistList(mc_mnv2d,projaxis)

        thename = "%s_%s_%s_proj%s"%(b_sample,c_var,"sigma",projaxis)
        thetitle = "%s %s %s proj%s"%(b_sample,c_var,"sigma",projaxis)
        ysize = _ysize
        xsize = _xsize
        canvas_nxbins = n_xbins
        canvas_nybins = n_ybins
        # these are the bin edges for each panel, printed on each panel
        plot_bins = y_bins

        proj_xtitle = x_title
        proj_ytitle = y_title
        if projaxis == "y":
            canvas_nxbins = n_ybins
            canvas_nybins = n_xbins
            plot_bins = x_bins 
            proj_xtitle = y_title
            proj_ytitle = x_title


        print("canvas n x bins: ",canvas_nxbins,",\t canvas n y bins: ",canvas_nybins)

        gc = PanelCanvas(thename, canvas_nxbins, canvas_nybins, round(xsize), round(ysize))
        # gc.SetLeftMargin(0.25)
        # gc.SetRightMargin(0.15)
        # gc.SetBottomMargin(0.15)
        # gc.SetFrameLineWidth(1)
        gc.SetXTitle(proj_xtitle)
        gc.SetYTitle(z_title)
        gc.Draw()
        n_pads = len(data_mnvproj_list)
        print(n_pads)
        data_hist_list = []
        data_stat_list = []

        mc_hist_list = []
        mc_band_list = []

        for hist in data_mnvproj_list:
            data_hist, data_stat = GetDataHistsForPlot(hist)
            data_hist_list.append(data_hist)
            data_stat_list.append(data_stat)
        for hist in mc_mnvproj_list:
            mc_hist, mc_band = GetMCHistsForPlot(hist)
            mc_hist_list.append(mc_hist)
            mc_band_list.append(mc_band)
        maxlist = [hist.GetMaximum() for hist in data_hist_list] + [hist.GetMaximum() for hist in mc_hist_list]
        global_max = max(maxlist)

        for i in range(n_pads):
            pad = gc.cd(i+1)
            pad.Draw()
            tmp_pad_max = 0.0
            tmp_pad_scale = 1.0

            tmp_pad_max = max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum())
            if tmp_pad_max == 0:
                tmp_pad_max = 1.0

            tmp_pad_scale = eval('{:.{p}g}'.format(global_max / tmp_pad_max, p=3))

            data_hist_list[i].Scale(tmp_pad_scale)
            data_stat_list[i].Scale(tmp_pad_scale)
            mc_hist_list[i].Scale(tmp_pad_scale)
            mc_band_list[i].Scale(tmp_pad_scale)

            data_hist_list[i].SetMaximum(1.2 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
            data_hist_list[i].SetMinimum(0)
            if proj_xtitle.split(" (")[0] in scaleY:
                pad.SetLogy()
                data_hist_list[i].SetMaximum(1.5 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
                data_hist_list[i].SetMinimum(data_hist_list[i].GetMaximum()/1000)
            
            data_hist_list[i].GetXaxis().SetNdivisions(207)
            data_hist_list[i].GetYaxis().SetNdivisions(205)


            data_hist_list[i].Draw("axis")
            mc_band_list[i].Draw("SAME E2")
            mc_hist_list[i].Draw("SAME HIST")

            data_stat_list[i].Draw("SAME E1 X0")
            data_hist_list[i].Draw("SAME E1 X0")

            range_string = "{loedge} < {var} < {hiedge}".format(loedge = round(plot_bins[i], 3), var =proj_ytitle.split(" (")[0], hiedge = round(plot_bins[i+1], 3))
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.025)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)

            multip_string = "#times {:g}".format(float('{:.{p}g}'.format(tmp_pad_scale, p=2)))
            multip_latex = ROOT.TLatex()
            multip_latex.SetTextAlign(32)
            multip_latex.SetNDC()
            multip_latex.SetTextFont(42)
            multip_latex.SetTextSize(0.028)
            multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.05),multip_string)
            pad.Modified()

        gc.SetHistTexts()
        gc.Draw()
        canvas_name = thename + "XSec_Proj" + projaxis

        gc.Print(os.path.join(outdirname, canvas_name + ".png"))
        gc.Print(os.path.join(outdirname,"source", canvas_name + ".C"))
        # del gc

        gc.cd()
        gc.ResetPads()
        gc.SetYTitle("Data / MC")
        gc.Modified()
        gc.Update()

        ratio_list = []
        mcerror_list = []
        straightline_list = []
        for i in range(n_pads):
            ratio = MakeDataMCRatio(data_hist_list[i],mc_band_list[i])
            ratio = MakeDataMCRatio(data_hist_list[i],mc_band_list[i])
            ratio.SetMinimum(0.1)
            ratio.SetMaximum(2)

            ratio.SetFillStyle(1001)
            ratio.SetLineColor(ROOT.kBlack)
            ratio.SetLineWidth(2)
            # ratio.SetTitle("")
            ratio.GetYaxis().SetNdivisions(205)
            ratio_list.append(ratio)

            mcerror = TH1D()
            mc_mnvproj_list[i].SetFillStyle(1001)
            mcerror = TH1D(mc_mnvproj_list[i].GetTotalError(False,True,False))
            for bin in range(1,mcerror.GetXaxis().GetNbins() + 1):
                mcerror.SetBinError(bin,max(mcerror.GetBinContent(bin),1.0E-9))
                mcerror.SetBinContent(bin, 1.0)
            mcerror.SetLineColor(ROOT.kRed)
            mcerror.SetLineWidth(3)
            mcerror.SetFillColor(ROOT.kRed - 10)

            mcerror_list.append(mcerror)

            straightline = TH1D()
            straightline = mcerror.Clone()
            straightline.SetFillStyle(0)
            straightline_list.append(straightline)


        for i in range(n_pads):
            pad = gc.cd(i+1)
            pad.SetLogy(0)

            pad.Draw()
            ratio_list[i].Draw("E1")
            mcerror_list[i].Draw("same E2")
            straightline_list[i].Draw("hist same")
            ratio_list[i].Draw("same")

            range_string = "{loedge} < {var} < {hiedge}".format(loedge = round(plot_bins[i], 3), var =proj_ytitle.split(" (")[0], hiedge = round(plot_bins[i+1], 3))
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.025)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)

        
        gc.SetHistTexts()
        gc.Draw()
        canvas_name += "_ratio"

        gc.Print(os.path.join(outdirname, canvas_name + ".png"))
        gc.Print(os.path.join(outdirname,"source", canvas_name + ".C"))


        del gc

    # return 0

def DrawErrorSumary2D():
    return 0





def CCQECanvas(name,title,xsize=1100,ysize=720):
    c2 = ROOT.TCanvas(name, title, round(xsize), round(ysize))
    # c2 = ROOT.TCanvas(name, title)
    # c2.SetLeftMargin(0.1)
    # c2.SetRightMargin(0.04)
    # c2.SetLeftMargin(0.1)
    # c2.SetTopMargin(0.04)
    # c2.SetBottomMargin(0.1)
    return c2

def CCQELegend(xlow,ylow,xhigh,yhigh):
    leg = ROOT.TLegend(xlow,ylow,xhigh,yhigh)
    # leg = ROOT.TLegend(abs(xlow-xhigh),abs(ylow-yhigh))
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(legendfontsize)
    return leg


def AddPreliminary():
    font = 112
    color = ROOT.kRed +1
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(legendfontsize*0.9)
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

bkgcats = [
    "chargedpion",
    "neutralpion",
    # "multipion",
    "other",
]

catstodo = [
    "data",
    "qelike",
    "chargedpion",
    "neutralpion",
    # "multipion",
    "other",
]

catsnames = {
    "data":"data", 
    "qelike":"QElike",
    "chargedpion":"1#pi^{#pm}",
    "neutralpion":"1#pi^{0}",
    "multipion":"N#pi",
    "other":"Other",
}

catscolors = {
    "data":ROOT.kBlack, 
    "qelike":ROOT.kBlue-6,
    "chargedpion":ROOT.kMagenta-6,
    "neutralpion":ROOT.kRed-6,
    "multipion":ROOT.kGreen-6,
    "other":ROOT.kYellow-6,
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

vars_info = {
    "EAvail": {
        "title": "E_{Avail}",
        "units": "GeV",
        "bins": [],
    },
    "ptmu": {
        "title": "p_{T}",
        "units": "GeV/c",
        "bins": [],

    },
    "pzmu" : {
        "title": "p_{||}",
        "units": "GeV/c",
        "bins": [],

    }
}

if len(sys.argv) == 1:
    print ("enter root file name and optional 2nd argument to get tuned version")
flag = "types_"
raw_filename = sys.argv[1]
if len(sys.argv)> 2:
    flag = "tuned_type_"

if "_tuned_analyzev9" in raw_filename:
    tuned_filename = raw_filename
    untuned_filename = raw_filename.replace("_tuned_","_untuned_")
elif "_untuned_analyzev9":
    untuned_filename = raw_filename
    tuned_filename = raw_filename.replace("_untuned_","_tuned_")

tuned_f = TFile.Open(tuned_filename,"READONLY")
untuned_f = TFile.Open(untuned_filename,"READONLY")

plotdirbase = os.getenv("OUTPUTLOC")

plotdir = MakePlotDir("XSec1D")
dirname = untuned_filename.replace("_untuned_analyzev9.root", "_XSec1D")

# outfilename=filebasename1.replace(".root","_2DPlots")
outdirname = os.path.join(plotdir, dirname)
if not os.path.exists(outdirname):
    print(outdirname)
    os.mkdir(outdirname)

source_outdirname = os.path.join(outdirname, "source")
if not os.path.exists(source_outdirname):
    print(source_outdirname)
    os.mkdir(source_outdirname)


# keys = f.GetListOfKeys()

# h_pot = f.Get("POT_summary")
# dataPOT = h_pot.GetBinContent(1)
# mcPOTprescaled = h_pot.GetBinContent(2)
# POTScale = dataPOT / mcPOTprescaled
# print("POTScale: ",POTScale)


# find all the valid histogram and group by keywords
print("Making dict of source hists...")
print("\tLooking at untuned...")
input_hists = GetInputHistDict(untuned_f)
print("\tLooking at tuned...")
input_hists = GetInputHistDict(tuned_f, input_hists)

# print(input_hists)

analyze_stage_list = [
    "mc_tot",
    "mc_bkg_tot",
    "signalfraction",
    "bkgfraction",
    "bkgsub",
    "bkgsub_unfolded",
    "bkgsub_unfolded_effcorr",
    "efficiency",
    "bkgsub_unfolded_effcorr_sigma",
    "sigmaMC"
]


print("Making dict of analyze hists...")
print("\tLooking at untuned...")
analyze_hists = GetAnalyzeHistDict(untuned_f, False)
print("\tLooking at tuned...")
analyze_hists = GetAnalyzeHistDict(tuned_f, True, analyze_hists)

keys = tuned_f.GetListOfKeys()
if "varsFile" not in keys:
    bigvarconfig_string = tuned_f.Get("varsFile_5A").GetTitle()
else:
    bigvarconfig_string = tuned_f.Get("varsFile").GetTitle()
bigvarconfig_dict = json.loads(re.sub("//.*", "", bigvarconfig_string, flags = re.MULTILINE))


# print(analyze_hists)
# analyze_dict[hist][sample][var][stage] = hist
ROOT.gStyle.SetOptStat(0)
for a_hist in analyze_hists.keys():
    # if a_hist == "h2D":
    #     print("2d not set up, skipping")
    #     continue
    print(a_hist)
    for b_sample in analyze_hists[a_hist].keys():
        datasample = b_sample
        plottitle = ""
        print(b_sample)
        if "_Tuned" in b_sample:
            dotuned = True
            datasample = datasample.replace("_Tuned","")
            plottitle += "Tuned "
        
        for c_var in analyze_hists[a_hist][b_sample].keys():
            mnvPlotter = MnvPlotter()
            print(c_var)
            # Plot total MC vs data + ratio

            # Plot bkg fraction and signal fraction?
            
            # Plot bkgsub data vs mcreco sig (tuned) + ratio + errorsum

            # Plot bkgsub_unfolded vs selected truth (tuned, untuned?) + ratio + errorsum

            # Plot efficiency + errorsum

            # Plot bkgsub_unfolded_effcorr_sigma vs alltruth (untuned) + ratio + error sum
            # print(analyze_hists[a_hist][b_sample][c_var].keys())

                        
            tmp_sigma = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_effcorr_sigma"]
            tmp_sigma_tuned = analyze_hists[a_hist][b_sample][c_var]["bkgsub_unfolded_effcorr_sigma_tuned"]
            tmp_sigmamc = analyze_hists[a_hist][b_sample][c_var]["sigmaMC"]
            tmp_sigmamc_tuned = analyze_hists[a_hist][b_sample][c_var]["sigmaMC_tuned"]
            if a_hist=="h":
                var_title = c_var
                var_units = "unit"
                if c_var in vars_info:
                    var_title = vars_info[c_var]["title"]
                    var_units = vars_info[c_var]["units"]
                    if len(vars_info[c_var]["bins"]) == 0:
                        print("making bins")
                        varconfig = bigvarconfig_dict["1D"][c_var]
                        if "bins" in varconfig.keys():
                            bins1D = [float(tmpbin) for tmpbin in varconfig["bins"]]
                            vars_info[c_var]["bins"] = bins1D
                        elif "nbins" in varconfig.keys():
                            mini = varconfig["min"]
                            maxi = varconfig["max"]
                            width = (maxi - mini)/varconfig["nbins"]
                            bins1D = [mini + tmpbin * width for tmpbin in range(0,varconfig["nbins"]+1)]
                            # print(bins1D)
                            vars_info[c_var]["bins"] = bins1D
                sigma_ytitle = "d#sigma/d%s (cm^{2}/%s/Nucleon)"%(var_title,var_units)

                DrawDataMCPlot1D(tmp_sigma_tuned,tmp_sigmamc, "%s (%s)"%(var_title,var_units), sigma_ytitle, outdirname)

                # DrawErrorSummary1D(tmp_sigma)
            if a_hist == "h2D":
                print(">>>>>> doing 2D")
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
                    print(yvar, yvar_bins)
                    
                xvar_title = "%s (%s)"%(xvar_name,xvar_units)
                yvar_title = "%s (%s)"%(yvar_name, yvar_units)
                sigma_ztitle = "d^{2}#sigma/d%sd%s (cm^{2}/%s/%s/Nucleon)"%(xvar_title,yvar_title,xvar_units,yvar_units)

                DrawDataMCPlot2D(tmp_sigma_tuned, tmp_sigmamc, xvar_title, xvar_bins, yvar_title, yvar_bins, sigma_ztitle, outdirname)
                # DrawErrorSummary2D()


                
            

sys.exit(1)
            

ROOT.gStyle.SetOptStat(0)
for a_sample in groups.keys():
    datasample = a_sample
    plottitle = ""
    if "warped" in a_sample:
        datasample = datasample.replace("_warped","")
        plottitle += "Warped "
    if "_Tuned" in a_sample:
        dotuned = True
        datasample = datasample.replace("_Tuned","")
        plottitle += "Tuned "
    else:
        dotuned = False
    plottitle +=  samplenames[datasample]

    for b_var in groups[a_sample].keys():
        noData = global_noData
        if "data" not in groups[datasample][b_var].keys():
            noData = True
        # Figure out what order to put the mc in for stack plots (backgrounds first, then signal)
        mc_order = list([
            "qelikenot",
            "qelike"
            ])
        if "qelikenot" not in groups[a_sample][b_var].keys():
            mc_order = list([
                "other",
                "neutralpion",
                "chargedpion",
                "qelike"
                ])
        
        # Set up the legend
        leg = CCQELegend(legx1,legy1,legx2,legy2)
        leg = CCQELegend(legx1,legy1,legx2,legy2)
        # leg.SetNColumns(2)

        # Make a dummy data hist and put the data in it if needed
        data = MnvH1D()
        if not noData:
            data = groups[datasample][b_var]["data"]

        # Now make the stack for the plot, and total mc for the ratio and the chi2
        stack = THStack("stack","")
        mctot = MnvH1D()
        firstmc = True
        for c_cat in mc_order:
        # for c_cat in groups[a_sample][b_var].keys():
            if c_cat not in groups[a_sample][b_var].keys():
                print("WARNING: cat ", c_cat, "in mc_order but not in hists")
                continue
            if c_cat in ["data","mctot","stack"]:
                continue
            if firstmc:
                mctot = groups[a_sample][b_var][c_cat].Clone("mctot")
                firstmc = False
            else:
                mctot.Add(groups[a_sample][b_var][c_cat])
            stack.Add(groups[a_sample][b_var][c_cat])
            # leg.AddEntry(groups[a_sample][b_var][c_cat],catsnames[c_cat],"f")
        for c_cat in mc_order[::-1]:
            leg.AddEntry(groups[a_sample][b_var][c_cat],catsnames[c_cat],"f")
            if c_cat not in groups[a_sample][b_var].keys():
                continue
            if c_cat in ["data","mctot","stack"]:
                continue
        if not noData:
            leg.AddEntry(data,"data","pe") # TODO need to figure out how to order this properly



        # Make the canvas
        thename = "%s_%s"%(a_sample,b_var)
        thetitle = "%s %s"%(a_sample,b_var)
        ysize = _ysize
        xsize = _xsize
        # if doratio and not noData:
        #     ysize = 1.2 * _ysize
        # cc = CCQECanvas(thename, thetitle, xsize, ysize)
        cc = ROOT.TCanvas(thename, thetitle, round(xsize), round(ysize))
        cc.SetLeftMargin(0.15)
        cc.SetRightMargin(0.15)
        cc.SetBottomMargin(0.15)
        cc.SetFrameLineWidth(1)

        # If do ratio, set up the top and bottom pads for the hists
        if doratio and not noData:
            top = TPad("hist", "hist", 0, 0.278, 1, 1)
            top.SetRightMargin(pad_rmarg)
            top.SetLeftMargin(pad_lmarg)
            top.SetTopMargin(topmarg)
            top.SetBottomMargin(0)
            top.SetFrameLineWidth(1)

            bottom = TPad("Ratio", "Ratio", 0, 0, 1, 0.278)
            bottom.SetRightMargin(pad_rmarg)
            bottom.SetLeftMargin(pad_lmarg)
            bottom.SetBottomMargin(bottommarg)
            bottom.SetTopMargin(0)
            bottom.SetFrameLineWidth(1)

            top.Draw()
            bottom.Draw()

            bottomArea = bottom.GetWNDC() * bottom.GetHNDC()
            topArea = top.GetWNDC() * top.GetHNDC()
            areaScale = topArea / bottomArea
            # Move to top pad for hists
            top.cd()
        
        # Do stack first
        stack.Draw()

        # set up its y axis
        stack.GetYaxis().SetTitle("Counts/unit")
        stack.GetYaxis().CenterTitle()
        stack.GetYaxis().SetTitleOffset(0.6)
        stack.GetYaxis().SetTitleSize(0.05)
        stack.GetYaxis().SetLabelSize(0.05)

        # set up its x axis if relevant
        x_title = ""
        if not noData:
            x_title = data.GetXaxis().GetTitle()
        else:
            x_title = groups[a_sample][b_var][mc_order[0]].GetXaxis().GetTitle()
        if not doratio or noData:
            stack.GetXaxis().SetTitle(x_title)
            stack.GetXaxis().CenterTitle()
            stack.GetXaxis().SetTitleSize(0.05)

        # figure out the maximums
        if not noData:
            stack.SetMaximum(1.2 * max(data.GetMaximum(), stack.GetMaximum()))
        else:
            stack.SetMaximum(1.2 * stack.GetMaximum())
        
        stack.Draw("hist")
        if not noData:
            data.Draw("PE same")
        leg.Draw()

        if doratio and not noData:
            bottom.cd()

            # make the ratio and make it pretty
            mctot.SetFillStyle(1001)
            ratio = MnvH1D()
            ratio = MakeDataMCRatio(data, mctot)
            ratio.SetMinimum(0.5)
            ratio.SetMaximum(1.5)

            ratio.SetLineColor(ROOT.kBlack)
            ratio.SetLineWidth(3)

            ratio.SetTitle("")            
            ratio.GetYaxis().SetTitle("Data / MC")
            ratio.GetYaxis().CenterTitle()
            ratio.GetYaxis().SetTitleSize(0.05 * areaScale)
            ratio.GetYaxis().SetTitleOffset(0.6 / areaScale)
            ratio.GetYaxis().SetLabelSize(0.05 * areaScale)
            ratio.GetYaxis().SetNdivisions(205)

            ratio.GetXaxis().SetTitle(x_title)
            ratio.GetXaxis().CenterTitle()
            ratio.GetXaxis().SetTitleSize(0.05 * areaScale)
            ratio.GetXaxis().SetLabelSize(ratio.GetXaxis().GetLabelSize() * areaScale*1.5)

            ratio.Draw()

            # Now do mc uncertainties
            mcerror = TH1D()
            mcerror = TH1D(mctot.GetTotalError(False, True, False))
            for bin in range(1, mcerror.GetXaxis().GetNbins() + 1):
                mcerror.SetBinError(bin, max(mcerror.GetBinContent(bin), 1.0e-9))
                mcerror.SetBinContent(bin, 1.0)
            mcerror.SetLineColor(ROOT.kRed)
            mcerror.SetLineWidth(3)
            mcerror.SetFillColorAlpha(ROOT.kPink + 1, 0.4)
            mcerror.Draw("same E2")

            # Now do a line at 1
            straightline = TH1D()
            straightline = mcerror.Clone()
            straightline.SetFillStyle(0)
            straightline.Draw("hist same")

            ratio.Draw("same")

            # Go back to the top pad 
            top.cd()
        # Dress plot with text
        prelim = AddPreliminary()
        titleonplot = MakeTitleOnPlot()
        # prelim.DrawLatex(latex_x, latex_y, "MINER#nuA Work In Progress")
        prelim.DrawLatex(legx1-lat_xoffset, legy1-2*lat_yoffset-0.01, "MINER#nuA Work In Progress")
        titleonplot.DrawLatex(0.37, 0.9, plottitle)
        # calculate chi2 and do that too
        if not noData:
            plotter = MnvPlotter()
            chi2 = plotter.Chi2DataMC(data,mctot)
            chi2_latex = ROOT.TLatex()
            chi2_latex.SetNDC()
            chi2_latex.SetTextSize(legendfontsize*0.9)
            chi2_latex.SetTextAlign(11)
            chi2_latex.DrawLatex(legx1-lat_xoffset,legy1-lat_yoffset, "#chi^{2} = "+ "{:g}".format(float('{:.{p}g}'.format(chi2, p=5))))
            # chi2_latex.DrawLatex(0.6,0.69, "#chi^{2} = "+str(chi2))
            del plotter
        canvas_name = thename + "_FinalStates"
        if dotypes:
            canvas_name = thename + "Types"
        if dotuned:
            canvas_name += "_tuned"
        cc.cd()
        cc.Print(os.path.join(outdirname, canvas_name + ".png"))
        cc.Print(os.path.join(outdirname,"source", canvas_name + ".C"))

        del cc, stack, mctot
        if doratio and not noData:
            print("deleting data stuff")
            del top, bottom, ratio, straightline, mcerror

# # now that the structure is created, stuff histograms into it after scaling for POT
# for k in keys:
#     name = k.GetName()
#     parse = name.split("___")
#     if len(parse) < 5: continue
#     hist = parse[0]
#     if hist == "h2D": continue # only 1d
#     sample = parse[1]
#     cat = parse[2]
#     # if cat == "qelikenot": continue
#     if cat not in catstodo: continue
#     variable = parse[3]
#     if "reconstructed" not in parse[4]: continue
#     if "types" in parse[4]:
#         continue
#     if "simulfit" in parse[4]:
#         continue
#     if "tuned" not in parse[4] and dotuned and cat!="data":
#         continue
#     if "tuned" in parse[4] and not dotuned:
#         continue
#     # these are stacked histos
#     h = f.Get(name).Clone()
#     if h.GetEntries() <= 0: continue
#     h.SetFillColor(catscolors[cat])
#     h.SetLineColor(ROOT.kBlack)
    
#     if "data" in cat:
#         index = 0
#         h = f.Get(name)
#         if h.GetEntries() <= 0: continue
#         # h.Scale(1.,"width")
#         h.Scale(0.001,"width")
#         h.SetMarkerStyle(20)
#         h.SetMarkerSize(1.5)
#     if "data" not in cat:
#         print("scaling hist ",h.GetName())
#         # print("POTscale: ", POTScale)
#         h.Scale(POTScale*0.001,"width") #scale to data
#         # h.Scale(POTScale,"width") #scale to data
#     # if cat in ["chargedpion", "neutralpion", "multipion", "other"]:
#     #     h.SetFillStyle(3244)
#     groups[hist][sample][variable][cat]=h

#         #print ("data",groups[hist][sample][variable][c])

# for a_hist in groups.keys():
#     if a_hist != "h": continue # no 2D
#     #print ("a is",a)
#     for b_sample in groups[a_hist].keys():

#         datasample = b_sample
#         if b_sample == "QElike_warped":
#             datasample = "QElike"
#         if b_sample == "QElike" and dowarp: continue

#         for c_var in groups[a_hist][b_sample].keys():
#             firstmc = True
#             for d_cat in groups[a_hist][b_sample][c_var].keys():
#                 if d_cat in ["data","mctot"]:
#                     continue
#                 if firstmc:
#                     mctot = groups[a_hist][b_sample][c_var][d_cat].Clone("mctot")
#                     firstmc = False
#                 else:
#                     mctot.Add(groups[a_hist][b_sample][c_var][d_cat])
#             groups[a_hist][b_sample][c_var]["mctot"] = mctot
                
            


# # "h___MultiplicitySideband___qelike___pzmu___reconstructed"
# # h___MultipBlobSideband___other___pzmu___reconstructed
# # do the plotting


# # build an order which puts backgrounds below signal (assumes signal is first in list)
# bestorder = []

# ROOT.gStyle.SetOptStat(0)
# template = "%s___%s___%s___%s"
# print("here")
# for a_hist in groups.keys():
#     if a_hist != "h": continue # no 2D
#     #print ("a is",a)
#     for b_sample in groups[a_hist].keys():

#         datasample = b_sample
#         if b_sample == "QElike_warped":
#             datasample = "QElike"
#         if b_sample == "QElike" and dowarp: continue

#         for c_var in groups[a_hist][b_sample].keys():
#             noData = global_noData
#             if "data" not in groups[a_hist][b_sample][c_var].keys():
#                 noData = False
#             print("here")

#             first = 0
#             leg = CCQELegend(0.6,0.75,1.,0.95)
#             leg.SetNColumns(2)
#             thename = "%s_%s"%(b_sample,c_var)
#             thetitle = "%s %s"%(b_sample,c_var)
#             # do the data first
#             cc = CCQECanvas(name,name)
#             if c_var in scaleX:
#                 cc.SetLogx()
#             # if c_var in scaleY:
#             cc.SetLogy()
            
#             data = TH1D()
#             # if len(groups[a_hist][datasample][c_var]["data"]) < 1:
#             #     print (" no data",a_hist,b_sample,c_var)
#             #     continue
            
#             data = TH1D(groups[a_hist][datasample][c_var]["data"])
#             plottitle=samplenames[b_sample]
#             if dotuned:
#                 plottitle = "Tuned "+plottitle
#             # data.SetTitle(plottitle)
#             data.SetTitle("")
#             # data.GetYaxis().SetTitle("Counts/unit (bin width normalized)")
#             # data.GetYaxis().SetTitle("Counts/unit")
#             data.GetYaxis().SetTitle("Counts #times 10^{3}/GeV^{2}")
#             data.GetYaxis().CenterTitle()
#             data.GetYaxis().SetTitleSize(0.05)
#             data.GetYaxis().SetLabelSize(0.04)

#             # data.GetXaxis().SetTitle("Recoil in GeV")
#             data.GetXaxis().CenterTitle()
#             data.GetXaxis().SetTitleSize(0.05)    
#             data.GetXaxis().SetLabelSize(0.04)

#             dmax = data.GetMaximum()
#             if noData:
#                 dmax = 0.0
#             #data.Draw("PE")
#             if not noData: leg.AddEntry(data,"data","pe")
            
#             data.Print()
            
#             bestorder = list([
#                 "other",
#                 # "multipion",
#                 "neutralpion",
#                 "chargedpion",
#                 "qelike"
#             ])

#             for d_cat in bestorder:
#                 if d_cat == "data": continue
#                 if first == 0: # make a stack
#                     stack = THStack(name.replace("reconstructed","stack"),"")
#                 first+=1
#                 h = groups[a_hist][b_sample][c_var][d_cat]
#                 stack.Add(h)
#                 leg.AddEntry(h,catsnames[d_cat],"f")
#             smax = stack.GetMaximum()
#             #print ("max",smax,dmax)
#             max_multiplier = 1.4

#             if c_var in scaleY:
#                 max_multiplier = 2.0
#                 data.SetMinimum(0.)
#                 data.GetXaxis().SetRangeUser(0.0,0.5)
#             if smax > dmax:
#                 data.SetMaximum(smax*max_multiplier)
#                 stack.SetMaximum(smax*max_multiplier)
#             else:
#                 data.SetMaximum(dmax*max_multiplier)
#                 stack.SetMaximum(dmax*max_multiplier)
#             if not noData: 
#                 data.Draw("PE")
#                 stack.Draw("hist same")
#             else:
#                 data.Reset()
#                 data.Draw("hist")  # need to this to get the axis titles from data
#                 stack.Draw("hist same")
#                 data.Draw("AXIS same")
#             if not noData: 
#                 data.Draw("AXIS same")
#                 data.Draw("PE same")
#             leg.Draw()
#             prelim = AddPreliminary()
#             prelim.DrawLatex(0.6,0.72,"MINER#nuA Work In Progress")

#             chi2 = groups[a_hist][b_sample][c_var]["data"].Chi2Test(groups[a_hist][b_sample][c_var]["mctot"], "CHI2/NDF")
#             chi2_latex = ROOT.TLatex()
#             chi2_latex.SetNDC()
#             chi2_latex.SetTextSize(legendfontsize-0.004)
#             chi2_latex.SetTextAlign(11)
#             chi2_latex.DrawLatex(0.6,0.69,"#chi^{2} = %d"%chi2)

#             titleonplot = MakeTitleOnPlot()
#             titleonplot.DrawLatex(0.37,0.85,plottitle)
#             cc.Draw()

#             canvas_name=thename+"_FinalStates"
#             if dotuned:
#                 canvas_name = thename+"_FinalStates_tuned"
#             cc.Print(dirname+"/"+canvas_name+".png")
#             cc.Print(dirname+"/"+canvas_name+".C")

#             del cc
