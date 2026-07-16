# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023


# from re import L
import sys,os
import ROOT
ROOT.gROOT.SetBatch(True) # Run in batch mode
from ROOT import gROOT,gStyle, TFile,THStack,TH1D,TCanvas, TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex, TString
from PlotUtils import MnvH1D, MnvH2D, HyperDimLinearizer, GridCanvas, MnvPlotter
import ctypes

import json, re
import math
import datetime


mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")

TEST=False
global_noData=False  # use this to plot MC only types
dotypes = True
sigtop = True # use this to place signal on top of background
dotuned = True
dowarp = False

doareanorm = False

ratio_frac = 0.3 #0.278

staterror_drawopt = "E1 X0"


legendfontsize = 0.042
axistitle_font = 42 # helvetica
# Defines the size of the canvas you're making
_xsize = 3200
_ysize = 2400
# _xsize = 2000.0
# _ysize = 1500.0

latex_x = 0.55
latex_y = 0.43

pad_lmarg = 0.10
pad_rmarg = 0.04
topmarg = 0.05
bottommarg = 0.3

pad_lmarg = 0.10
pad_rmarg = 0.02
topmarg = 0.05
bottommarg = 0.3
lat_xoffset = 0.0
lat_yoffset = 0.04

scaleY = [
    "EAvail",
    "Eavail",
    "E_{Avail}",
]#"recoil","EAvail"]


# For things around the data points
data_marker_style = 20
data_marker_size = 3.0
data_marker_size2d = 2.0
end_error_size = 15.0
typeslinewidth = 1
typeslinewidth1D = 2
typeslinedarker = True
# bkgfillstyle = 3244
do_pinkstat = False

prelim_string = "MINER#it{^{}#nu}A Work In Progress"
datapot_string1 = "#it{POT Normalized}"
datapot_string2 =  "#it{Data POT}: 1.12 #times 10^{21}"
do_titleonplot = True
do_chi2onplot = True

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

def GetPadMax(i_data_hist, i_mctot_hist, including_errors = True):
    data_max = i_data_hist.GetBinContent(i_data_hist.GetMaximumBin())
    mc_max = i_mctot_hist.GetBinContent(i_mctot_hist.GetMaximumBin())
    tmp_max = max(data_max, mc_max)
    if including_errors:
        tmp_data = i_data_hist.Clone()
        if type(i_data_hist)==type(MnvH1D()):
            tmp_data = i_data_hist.GetCVHistoWithError().Clone()
        for i in range(1,tmp_data.GetNbinsX()+1):
            # print("\t%s\t%s"%(tmp_data.GetBinContent(i),tmp_data.GetBinError(i)))
            cont_and_err = tmp_data.GetBinContent(i) + tmp_data.GetBinError(i)
            if cont_and_err > tmp_max:
                # print("\tcont_and_err:", cont_and_err, "\ttmp_max", tmp_max)
                tmp_max = cont_and_err
                # return cont_and_err
    # print("\tGoing with tmp max cont_and_err:", cont_and_err, "\ttmp_max:", tmp_max)
    return tmp_max


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
    gc2.SetInterpadSpace(0.0)
    gc2.ResetPads()
    gc2.SetCanvasSize(_xsize,_ysize)
    return gc2


def SetupErrorSummary(mnvPlotter):
    mnvPlotter.axis_minimum = 0.0
    mnvPlotter.axis_maximum = 0.6
    mnvPlotter.error_color_map["Flux"] = ROOT.kViolet + 6
    mnvPlotter.error_color_map["Recoil Reconstruction"] = ROOT.kOrange + 2
    mnvPlotter.error_color_map["Cross Section Models"] = ROOT.kMagenta
    mnvPlotter.error_color_map["FSI Model"] = ROOT.kRed
    mnvPlotter.error_color_map["Muon Reconstruction"] = ROOT.kGreen
    mnvPlotter.error_color_map["Muon Energy"] = ROOT.kGreen + 3
    mnvPlotter.error_color_map["Muon_Energy_MINERvA"] = ROOT.kRed - 3
    mnvPlotter.error_color_map["Muon_Energy_MINOS"] = ROOT.kViolet - 3
    mnvPlotter.error_color_map["Other"] = ROOT.kGreen + 3
    mnvPlotter.error_color_map["Low Recoil Fits"] = ROOT.kRed + 3
    mnvPlotter.error_color_map["GEANT4"] = ROOT.kBlue
    mnvPlotter.error_color_map["Background Subtraction"] = ROOT.kGreen
    mnvPlotter.error_color_map["Tune"] = ROOT.kOrange + 2

    mnvPlotter.error_summary_group_map.clear()
    FSI_Model_list = [
        "GENIE_FrAbs_N",
        "GENIE_FrAbs_pi",
        "GENIE_FrCEx_N",
        "GENIE_FrCEx_pi",
        "GENIE_FrElas_N",
        "GENIE_FrElas_pi",
        "GENIE_FrInel_N",
        "GENIE_FrInel_pi",
        "GENIE_FrPiProd_N",
        "GENIE_FrPiProd_pi",
        "GENIE_MFP_N",
        "GENIE_MFP_pi",
    ]
    mnvPlotter.error_summary_group_map["FSI Model"] = FSI_Model_list

    Genie_Interaction_Model_list = [
        "GENIE_AGKYxF1pi",
        "GENIE_AhtBY",
        "GENIE_BhtBY",
        "GENIE_CCQEPauliSupViaKF",
        "GENIE_CV1uBY",
        "GENIE_CV2uBY",
        "GENIE_EtaNCEL",
        "GENIE_MaCCQE",
        "GENIE_MaCCQEshape",
        "GENIE_MaNCEL",
        "GENIE_MaRES",
        "GENIE_MvRES",
        "GENIE_NormCCQE",
        "GENIE_NormCCRES",
        "GENIE_NormDISCC",
        "GENIE_NormNCRES",
        "GENIE_RDecBR1gamma",
        "GENIE_Rvn1pi",
        "GENIE_Rvn2pi",
        "GENIE_Rvn3pi",
        "GENIE_Rvp1pi",
        "GENIE_Rvp2pi",
        "GENIE_Theta_Delta2Npi",
        "GENIE_VecFFCCQEshape",
    ]
    mnvPlotter.error_summary_group_map["Genie Interaction Model"] = Genie_Interaction_Model_list

    Tune_list = [
        "RPA_LowQ2",
        "RPA_HighQ2",
        "NonResPi",
        "2p2h",
        "LowQ2Pi",
        "Low_Recoil_2p2h_Tune",
    ]
    mnvPlotter.error_summary_group_map["Tune"] = Tune_list

    Response_list = [    
        "response_em",
        "response_proton",
        "response_pion",
        "response_meson",
        "response_other",
        "response_low_neutron",
        "response_mid_neutron",
        "response_high_neutron",
    ]
    mnvPlotter.error_summary_group_map["Response"] = Response_list

    Geant_list = [
        "GEANT_Neutron",
        "GEANT_Proton",
        "GEANT_Pion",
    ]
    mnvPlotter.error_summary_group_map["Geant"] = Geant_list

    Muon_list = [
        "Muon_Energy_MINOS",
        "Muon_Energy_MINERvA",
        "MINOS_Reconstruction_Efficiency",
        "Muon_Energy_Resolution",
        "BeamAngleX",
        "BeamAngleY",
    ]
    mnvPlotter.error_summary_group_map["Muon"] = Muon_list


    return mnvPlotter

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

def AddDataPOTInfo():
    font = 42
    # color = ROOT.kBlack
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(legendfontsize*0.85)
    # latex.SetTextColor(color)
    latex.SetTextFont(font)
    # latex.SetTextAlign(11)
    return latex

def AddChi2Info():
    font = 42
    # color = ROOT.kBlack
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(legendfontsize*0.85)
    # latex.SetTextColor(color)
    latex.SetTextFont(font)
    # latex.SetTextAlign(11)
    return latex
    
# def MakeProjHistList(i_hist, projaxis="x"):
#     ret_list = []
#     hist = i_hist.Clone()
#     n_projbins = 0
#     if projaxis=="x":
#         n_projbins = hist.GetNbinsY()
#         proj_nametail = "_projybin"
#     elif projaxis == "y":
#         n_projbins = hist.GetNbinsX()
#         proj_nametail = "_projxbin"
#     else:
#         print("ERROR: invalid projaxis %s, exiting"%(projaxis))
#         sys.exit(1)

#     for i in range(n_projbins):
#         tmp_proj_name = hist.GetName() + proj_nametail + str(i)
#         if projaxis == "x":
#             tmp_proj = hist.ProjectionX(tmp_proj_name,i+1,i+1)#, "width")
#             tmp_proj.SetMarkerSize(data_marker_size2d)
#             ret_list.append(tmp_proj)
#             continue
#         else: # if projaxis == "y"
#             tmp_proj = hist.ProjectionY(tmp_proj_name,i+1,i+1)#, "width")
#             tmp_proj.SetMarkerSize(data_marker_size2d)
#             ret_list.append(tmp_proj)
#             continue
#     return ret_list  

def MakeProjHistList(i_hist, projaxis="x", n_projbins = 0):
    ret_list = []
    hist = i_hist.Clone()
    if projaxis=="x":
        if n_projbins == 0: n_projbins = hist.GetNbinsY()
        proj_nametail = "_projybin"
    elif projaxis == "y":
        if n_projbins == 0: n_projbins = hist.GetNbinsX()
        proj_nametail = "_projxbin"
    else:
        print("ERROR: invalid projaxis %s, exiting"%(projaxis))
        sys.exit(1)

    linecolor = hist.GetLineColor()
    fillcolor = hist.GetFillColor()
    linewidth = hist.GetLineWidth()
    markercolor = hist.GetMarkerColor()
    markerstyle = hist.GetMarkerStyle()
    markersize = hist.GetMarkerSize()
    fillstyle = hist.GetFillStyle()
    for i in range(n_projbins):
        tmp_proj_name = hist.GetName() + proj_nametail + str(i)

        if projaxis == "x":
            tmp_proj = hist.ProjectionX(tmp_proj_name,i+1,i+1)#, "width")
            # ret_list.append(tmp_proj)
            # continue
        else: # if projaxis == "y"
            tmp_proj = hist.ProjectionY(tmp_proj_name,i+1,i+1)#, "width")
            # ret_list.append(tmp_proj)
            # continue
        tmp_proj.SetLineColor(linecolor)
        tmp_proj.SetLineWidth(linewidth)
        tmp_proj.SetFillColor(fillcolor)
        tmp_proj.SetMarkerColor(markercolor)
        tmp_proj.SetMarkerStyle(markerstyle)
        tmp_proj.SetMarkerSize(markersize)
        tmp_proj.SetFillStyle(fillstyle)

        ret_list.append(tmp_proj)

    return ret_list    


# def GetDataHistsForPlot(mnv_datahist):
#     mnvh = mnv_datahist.Clone()

#     hist = mnvh.GetCVHistoWithError(True,False)
#     hist.SetMarkerStyle(data_marker_style)
#     hist.SetMarkerColor(ROOT.kBlack)
#     hist.SetLineWidth(2)
#     hist.SetLineColor(ROOT.kBlack)
#     hist.SetLineStyle(1)
#     hist.SetMarkerSize(data_marker_size)

#     stat = mnvh.GetCVHistoWithStatError()
#     stat.SetMarkerStyle(1)
#     stat.SetMarkerColor(ROOT.kBlack)
#     stat.SetLineWidth(2)
#     stat.SetLineColor(ROOT.kBlack)
#     stat.SetFillColorAlpha(ROOT.kPink, 0.3)
#     stat.SetLineStyle(1)
#     stat.SetMarkerSize(1)

#     return hist, stat


def GetDataHistsForPlot(mnv_datahist):
    mnvh = mnv_datahist.Clone()

    hist = mnvh.GetCVHistoWithError(True,False)
    hist.SetMarkerColor(mnvh.GetMarkerColor())
    hist.SetLineWidth(mnvh.GetLineWidth())
    hist.SetLineColor(mnvh.GetLineColor())
    hist.SetMarkerSize(data_marker_size2d)
    hist.SetMarkerStyle(mnvh.GetMarkerStyle())
    # hist.SetLineStyle(1)

    stat = mnvh.GetCVHistoWithStatError()
    stat.SetMarkerColor(mnvh.GetMarkerColor())
    # end_error_size
    stat.SetLineWidth(mnvh.GetLineWidth())
    stat.SetLineColor(mnvh.GetLineColor())
    if do_pinkstat:
        stat.SetLineWidth(4)
        stat.SetLineColorAlpha(ROOT.kPink, 0.3) #mnvh.GetLineColor())
        stat.SetFillColorAlpha(ROOT.kPink, 0.3)
    stat.SetMarkerSize(0)
    stat.SetMarkerStyle(1)
    # stat.SetLineStyle(1)

    return hist, stat

# def GetMCHistsForPlot(mnv_mchist):
#     mnvh = mnv_mchist.Clone()

#     band = mnvh.GetCVHistoWithError(True,False)
#     band.SetFillColor(catscolors["mctot"])
#     band.SetFillColorAlpha(catscolors["mctot"],0.4)
#     band.SetLineColor(catscolors["mctot"])

#     # band.SetFillColor(ROOT.kRed - 10)
#     # band.SetFillStyle(1001)
#     # band.SetLineColor(ROOT.kRed)
#     band.SetMarkerStyle(0)

#     hist = mnvh.GetCVHistoWithError(True,False)
#     hist.SetFillColor(0)
#     hist.SetLineColor(catscolors["mctot"])
#     # hist.SetLineColor(2)
#     # hist.SetLineColor(typescolors[0])
#     hist.SetLineStyle(1)
#     # hist.SetLineWidth(3)

#     return hist, band

def GetMCHistsForPlot(mnv_mchist):
    mnvh = mnv_mchist.Clone()

    hist = mnvh.GetCVHistoWithError(True,False)
    hist.SetFillColor(0)
    hist.SetLineColor(catscolors[0])
    hist.SetLineWidth(typeslinewidth+1)
    # hist.SetLineStyle(1)

    band = mnvh.GetCVHistoWithError(True,False)
    band.SetFillStyle(1001)
    # band.SetFillColorAlpha(typescolors[0], 0.3)
    # band.SetFillColor(ROOT.kRed - 10)
    band.SetFillColorAlpha(catscolors[0], 0.3)
    band.SetLineColor(catscolors[0])
    band.SetLineWidth(typeslinewidth+1)
    band.SetMarkerStyle(0)

    return hist, band

def MakeDataMCRatio(i_data, i_mctot):
    mcratio = i_data.Clone(str(i_data.GetName().replace("data", "datamcratio")))
    mcratio.Divide(i_data, i_mctot,1.0,1.0, "B")
    return mcratio

# def MakeDataMCRatioForPlot(i_data, i_mctot):
#     ratio = i_data.Clone(str(i_data.GetName().replace("data", "datamcratio")))
#     mctot = i_mctot.Clone()
#     mctot.ClearAllErrorBands()
#     mctot.AddMissingErrorBandsAndFillWithCV(i_mctot)
#     ratio.Divide(ratio,mctot,1.0,1.0)
#     return ratio

def MakeDataMCRatioForPlot(i_data, i_mctot):
    ratio = i_data.Clone(str(i_data.GetName().replace("data", "datamcratio")))
    mctot = i_mctot.Clone()
    mctot.ClearAllErrorBands()
    mctot.AddMissingErrorBandsAndFillWithCV(i_mctot)
    ratio.Divide(ratio,mctot,1.0,1.0)
    
    ratio.SetLineColor(i_data.GetLineColor())
    ratio.SetLineWidth(i_data.GetLineWidth())
    ratio.SetMarkerColor(i_data.GetMarkerColor())
    ratio.SetMarkerStyle(i_data.GetMarkerStyle())
    ratio.SetMarkerSize(i_data.GetMarkerSize())
    
    return ratio
def DrawDataMCPlot1D(i_data_hist, i_mc_hist, i_mc_typeshistdict, x_title, y_title, outdirname, canvas_name, canvas_title,nametag = ""):
    # mnvPlotter = SetupErrorSummary(MnvPlotter(8))
    mnvPlotter = MnvPlotter(8)
    
    mnv_data = i_data_hist.Clone()
    mnv_mc = i_mc_hist.Clone()
    mnv_data.Scale(1.0, "width")
    mnv_mc.Scale(1.0, "width")

    my_catstodo = catstodo
    tmp_dotypes = False
    for key in i_mc_typeshistdict.keys():
        if key not in catstodo:
            my_catstodo = typestodo
            tmp_dotypes = True
            break

    my_catscolors = catscolors
    my_catsnames  = catsnames
    mc_typehistdict = {}
    stack = THStack("stack","")
    for cat in reversed(my_catstodo[1:]):
        hist = i_mc_typeshistdict[cat].Clone()
        hist.Scale(1.0, "width")
        hist.SetLineColor(ROOT.kBlack)
        if typeslinedarker:
            hist.SetLineColor(ROOT.TColor.GetColorDark(my_catscolors[cat]))
        hist.SetFillColor(my_catscolors[cat])
        hist.SetLineWidth(typeslinewidth1D+1)
        # if cat in bkgcats:
        #     hist.SetFillStyle(bkgfillstyle[cat]+100)
            # hist.SetFillColor(ROOT.TColor.GetColorDark(my_catscolors[cat]))
        if type(cat) == int:
            hist.SetLineColor(ROOT.kBlack)
            if cat >= 10: 
                hist.SetFillStyle(bkgfillstyle[cat]+100)
                # hist.SetFillColor(ROOT.TColor.GetColorDark(my_catscolors[cat]))
        stack.Add(hist)
        mc_typehistdict[cat] = hist.Clone()

    thename = canvas_name + nametag
    thetitle = canvas_title 
    if tmp_dotypes:
        thetitle += " Types"
    else: 
        thetitle += " Final States"

    ysize = _ysize
    xsize = _xsize

    mnv_data.SetMarkerStyle(data_marker_style)
    mnv_data.SetMarkerColor(ROOT.kBlack)
    mnv_data.SetLineWidth(2)
    mnv_data.SetLineColor(ROOT.kBlack)
    mnv_data.SetLineStyle(1)
    mnv_data.SetMarkerSize(data_marker_size)

    # data_hist = mnv_data.GetCVHistoWithError(True,False).Clone()
    # data_stat = mnv_data.GetCVHistoWithStatError().Clone()
    # data_stat.SetMarkerStyle(1)
    # data_stat.SetMarkerSize(1)
    data_hist, data_stat = GetDataHistsForPlot(mnv_data)
    # data_hist.GetYaxis().SetTitle(y_title)
    # data_hist.GetYaxis().CenterTitle()
    # data_hist.GetYaxis().SetTitleOffset(0.9)
    # data_hist.GetYaxis().SetTitleSize(0.05)
    # data_hist.GetYaxis().SetLabelSize(0.05)

    # data_hist.SetMaximum(1.2* max(mnv_data.GetMaximum(),mnv_mc.GetMaximum()))

    # Stuff for doing the ratios
    mc_hist = mnv_mc.GetCVHistoWithError(True,False)
    mc_hist.SetFillColor(0)
    mc_hist.SetLineColor(my_catscolors["mctot"])
    mc_hist.SetLineStyle(1)
    mc_hist.SetLineWidth(typeslinewidth1D+1)
    mnv_ratio = MakeDataMCRatioForPlot(mnv_data, mnv_mc)
    ratio, ratio_stat = GetDataHistsForPlot(mnv_ratio)

    ratio.SetFillStyle(0)
    ratio.SetMinimum(0.0001)
    ratio.SetMaximum(1.999)

    ratio.SetLineColor(ROOT.kBlack)
    ratio.SetLineWidth(2)
    ratio_stat.SetLineColor(ROOT.kBlack)
    ratio_stat.SetMarkerStyle(1)
    ratio_stat.SetMarkerSize(1)

    typesratio_dict = {}
    for key in my_catstodo[1:]:
        # tmp_typesratio = MakeDataMCRatio(mc_typehistdict[key], mnv_mc)
        tmp_typesratio = mc_typehistdict[key].Clone()
        tmp_typesratio.Divide(tmp_typesratio, mnv_mc,1.0,1.0)
        tmp_typesratio.SetLineWidth(typeslinewidth1D + 1)
        tmp_typesratio.SetFillStyle(0)
        tmp_typesratio.SetFillColor(0)
        tmp_typesratio.SetLineColor(catscolors[key])
        if tmp_dotypes:
            if key > 10:
                tmp_typesratio.SetLineStyle(2)
            else:
                if typeslinedarker:
                    tmp_typesratio.SetLineColor(ROOT.TColor.GetColorDark(catscolors[key]))

        typesratio_dict[key] = tmp_typesratio
    typesratio_stack_dict = {}
    if tmp_dotypes:
        for key in typestodo_leg:
            if key > 10:
                tmp_hist = typesratio_dict[key].Clone()
                tmp_hist.SetLineStyle(7)
                tmp_hist.SetLineWidth(typeslinewidth1D + 1)
                print(key)
                tmp_hist.Print()
                tmp_stack = THStack()
                tmp_stack.Add(tmp_hist)
                typesratio_stack_dict[key-10] = tmp_stack
        for key in typestodo_leg:
            if key <= 10:
                tmp_hist = typesratio_dict[key].Clone()
                tmp_hist.SetLineWidth(typeslinewidth1D + 1)
                tmp_hist.Print()
                if tmp_hist.GetEntries() == 0: continue
                typesratio_stack_dict[key].Add(tmp_hist)
                # typesratio_stack_dict[key].SetFillStyle(0)
                # typesratio_stack_dict[key].SetFillColor(0)
        # sys.exit(1)

    tmp_mnvmc_band = mnv_mc.Clone()
    tmp_mnvmc_band.ClearAllErrorBands()
    tmp_mnvmc_band.AddMissingErrorBandsAndFillWithCV(mnv_mc)
    tmp_mnvmc_band.Divide(tmp_mnvmc_band,mnv_mc,1.0,1.0)
    tmp_mnvmc_band.SetFillColor(my_catscolors["mctot"])
    tmp_mnvmc_band.SetFillColorAlpha(catscolors["mctot"],0.4)
    tmp_mnvmc_band.SetLineColor(catscolors["mctot"])
    tmp_mnvmc_band.SetLineWidth(typeslinewidth1D + 1)
    tmp_mnvmc_band.SetMarkerStyle(0)
    tmp_band = tmp_mnvmc_band.GetCVHistoWithError().Clone()
    
    straightline = tmp_band.Clone()
    straightline.SetFillStyle(0)
    straightline.SetFillColor(0)
    # ROOT.gStyle.SetErrorX(0) # This turns off the horizontal error bars
    ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer

    # Now set up the canvas
    cc = ROOT.TCanvas(thename, thetitle, round(xsize), round(ysize))
    cc.SetCanvasSize(_xsize,_ysize)
    cc.SetLeftMargin(0.25)
    cc.SetRightMargin(0.15)
    cc.SetBottomMargin(0.1)
    cc.SetFrameLineWidth(1)

    top = ROOT.TPad("hist", "hist", 0, ratio_frac, 1.0, 1.0)
    top.SetRightMargin(pad_rmarg)
    top.SetLeftMargin(pad_lmarg)
    top.SetTopMargin(topmarg)
    top.SetBottomMargin(0)
    top.SetFrameLineWidth(1)

    bottom = ROOT.TPad("Ratio", "Ratio", 0, 0, 1.0, ratio_frac)
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
    if x_title.split(" (")[0] in scaleY:
        top.SetLogy()

    # top.SetLogy()
    # # E1 draws a point with error bars, X0 turns off horizontal error bars
    # data_hist.Draw("9 E1 X0")

    stack.Draw()

    stack.GetYaxis().SetTitle(y_title)
    stack.GetYaxis().SetTitleFont(axistitle_font)
    stack.GetYaxis().CenterTitle()
    stack.GetYaxis().SetTitleOffset(0.6)
    stack.GetYaxis().SetTitleSize(0.07)
    stack.GetYaxis().SetLabelSize(0.05)

    stack.SetMaximum(1.2* max(mnv_data.GetMaximum(),mnv_mc.GetMaximum()))
    stack.SetMinimum(stack.GetMaximum()*0.001)
    stack.Draw("hist ][ 9")

    data_hist.Draw("PE1 X0 same 9")

    # stack.Draw("9 HIST same")    
    data_stat.Draw("9 SAME %s"%staterror_drawopt)
    data_hist.Draw("9 Same PE1 X0")

    padwidth = 1 - cc.GetLeftMargin() - cc.GetRightMargin()
    padheight = 1 - cc.GetTopMargin() - cc.GetBottomMargin()
    x1 = cc.GetLeftMargin() + 0.7 * padwidth
    if tmp_dotypes:
        x1 = cc.GetLeftMargin() + 0.5 * padwidth
    y1 = 1. - cc.GetTopMargin() - 0.01
    x2 = 1.-  padwidth/10 
    y2 = cc.GetBottomMargin() + 0.4 * padheight
    leg = TLegend(x1,y1,x2,y2)
    leg.SetTextSize(legendfontsize * 1.05)
    leg.SetNColumns(1)
    leg.SetBorderSize(0)
    leg.SetFillColor(-1)
    ROOT.gStyle.SetLegendFont(42)
    leg.AddEntry(data_hist, "Data","pe")
    leg.AddEntry(tmp_band, my_catsnames["mctot"],"fl")
    # leg.AddEntry(mc_hist, my_catsnames["mctot"],"fl")
    if tmp_dotypes:
        for cat in typestodo_leg:
            leg.AddEntry(mc_typehistdict[cat],my_catsnames[cat], "f")
        leg.SetNColumns(2)

    else:
        for cat in my_catstodo[1:]:
            leg.AddEntry(mc_typehistdict[cat],my_catsnames[cat], "f")
    
    leg.Draw()
    top.Modified()
    top.Update()

    bottom.cd()

    ratio.SetTitle("")            
    ratio.GetYaxis().SetTitle("Data / MC")
    ratio.GetYaxis().SetTitleFont(axistitle_font)
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetTitleSize(0.07 * areaScale)
    ratio.GetYaxis().SetTitleOffset(0.6 / areaScale)
    ratio.GetYaxis().SetLabelSize(0.05 * areaScale)
    ratio.GetYaxis().SetNdivisions(505)

    # ratio.GetXaxis().SetTitle(vars_info[c_var]["title"])
    ratio.GetXaxis().SetTitle(x_title)
    ratio.GetXaxis().CenterTitle()
    ratio.GetXaxis().SetTitleSize(0.05 * areaScale)
    ratio.GetXaxis().SetLabelSize(ratio.GetXaxis().GetLabelSize() * areaScale*1.5)
    
    ratio.Draw("9 E1 X0")

    # Now do mc uncertainties
    tmp_band.Draw("9 E2 same ][")
    straightline.Draw("9 Hist same, ][")

    if tmp_dotypes:
        for cat in reversed(typestodo_leg):
            if cat > 10: continue
            typesratio_stack_dict[cat].Draw("9 HIST NOCLEAR SAME")
    else:
        for cat in reversed(my_catstodo):
            if cat == "data": continue
            typesratio_dict[cat].Draw("9 HIST SAME")

    ratio_stat.Draw("9 %s SAME"%staterror_drawopt)
    ratio.Draw("9 same E1 X0")
    ratio.Draw("9 same axis")
    bottom.Modified()
    bottom.Update()

    top.cd()
    prelim = AddPreliminary()

    # prelim.DrawLatex(x1.value-lat_xoffset, y1.value-2*lat_yoffset-0.01, "MINER#it{#nu}A Work In Progress")
    prelim.DrawLatex(x1-lat_xoffset, y2-2*lat_yoffset-0.01, "MINER#it{#nu}A Work In Progress")
    thename += "_Types"
    top.Modified()
    top.Update()
    if x_title.split(" (")[0] in scaleX:
        top.SetLogx()
        bottom.SetLogx()
        top.Modified()
        top.Update()
        bottom.Modified()
        bottom.Update()
    # top.cd()
    # top.Draw()

    # cc.Draw()
    # cc.Print(os.path.join(outdirname, thename + ".png"))
    # cc.Print(os.path.join(outdirname, "source", thename + ".C"))
    cc.Print(os.path.join(outdirname, canvas_name + ".pdf"),"Title:%s Types"%(thetitle))

    cc.cd()
    cc.Clear()
    cc.Modified()
    cc.Update()

    
    # Now do the unstacked hist
    mc_band = mc_hist.Clone()
    mc_band.SetFillColor(my_catscolors["mctot"])
    mc_band.SetFillColorAlpha(catscolors["mctot"],0.4)
    mc_band.SetLineColor(catscolors["mctot"])
    mc_band.SetLineWidth(typeslinewidth1D + 1)
    mc_band.SetMarkerStyle(0)
    mc_line = mc_band.Clone()
    mc_line.SetFillStyle(0)
    mc_line.SetFillColor(0)
    top = ROOT.TPad("hist", "hist", 0, ratio_frac, 1.0, 1.0)
    top.SetRightMargin(pad_rmarg)
    top.SetLeftMargin(pad_lmarg)
    top.SetTopMargin(topmarg)
    top.SetBottomMargin(0)
    top.SetFrameLineWidth(1)

    bottom = ROOT.TPad("Ratio", "Ratio", 0, 0, 1.0, ratio_frac)
    bottom.SetRightMargin(pad_rmarg)
    bottom.SetLeftMargin(pad_lmarg)
    bottom.SetBottomMargin(bottommarg)
    bottom.SetTopMargin(0)
    bottom.SetFrameLineWidth(1)

    top.Draw()    
    bottom.Draw()

    top.cd()
    top.Draw()
    if tmp_dotypes:
        leg.Clear()
        leg.SetNColumns(1)
        leg.AddEntry(data_hist, "Data", "fl")
        leg.AddEntry(tmp_band, my_catsnames["mctot"],"fl")

    if x_title.split(" (")[0] in scaleY:
        top.SetLogy()
    
    for hist in stack.GetHists():
        hist.SetFillStyle(0)
        if tmp_dotypes:
            hist.SetLineWidth(0)
            continue
        hist.SetLineWidth(typeslinewidth1D+1)
        
    stack.Draw("9 axis")
    stack.Draw("9 nostack, hist same")
    mc_band.Draw("9 E2 ][ same")
    stack.Draw("9 nostack, hist same")
    mc_line.Draw("9 hist same")
    data_hist.Draw("9 E1 X0, same")
    data_stat.Draw("9 SAME %s"%staterror_drawopt)
    leg.Draw()
    top.Modified()
    top.Update()
    
    bottom.cd()
    bottom.Draw()
    if x_title.split(" (")[0] in scaleY:
        bottom.SetLogy()
    ratio.Draw("9 E1 X0")

    # Now do mc uncertainties
    tmp_band.Draw("9 E2 same ][")
    straightline.Draw("9 Hist same, ][")

    # if tmp_dotypes:
    #     for cat in reversed(typestodo_leg):
    #         if cat > 10: continue
    #         typesratio_stack_dict[cat].Draw("9 HIST NOCLEAR SAME")
    # else:
    if not tmp_dotypes:
        for cat in reversed(my_catstodo):
            if cat == "data": continue
            typesratio_dict[cat].Draw("9 HIST SAME")

    ratio_stat.Draw("9 %s SAME"%staterror_drawopt)
    ratio.Draw("9 same E1 X0")
    ratio.Draw("9 same axis")
    bottom.Modified()
    bottom.Update()

    top.cd()
    prelim.DrawLatex(x1-lat_xoffset, y2-2*lat_yoffset-0.01, "MINER#it{#nu}A Work In Progress")
    thename += "_Types_unstack"
    top.Modified()
    top.Update()

    if x_title.split(" (")[0] in scaleX:
        top.SetLogx()
        bottom.SetLogx()
        top.Modified()
        top.Update()
        bottom.Modified()
        bottom.Update()

    top.cd()
    top.Draw()
    cc.Draw()
    # cc.Print(os.path.join(outdirname, thename + ".png"))
    # cc.Print(os.path.join(outdirname, "source", thename + ".C"))
    cc.Print(os.path.join(outdirname, canvas_name + ".pdf"),"Title: %s NoStack"%(thetitle))

    cc.cd()
    cc.Clear()
    cc.Modified()
    cc.Update()

    # del stack
    # del cc


def DrawDataMCPlot2D(i_data_hist, i_mc_hist, i_mc_typeshistdict, x_title, x_bins, y_title, y_bins, z_title, outdirname, canvas_name, canvas_title, nametag,i_multipliers = []):
    data_mnv2d = i_data_hist.Clone()
    mc_mnv2d = i_mc_hist.Clone()
    data_mnv2d.Scale(1.0, "width")
    mc_mnv2d.Scale(1.0, "width")

    # These don't get bin width normalized before they get used for the total 1D projection hists
    data_mnv2d_unscaled = i_data_hist.Clone()
    mc_mnv2d_unscaled = i_mc_hist.Clone()

    mc_typehistdict = {}
    mc_typehistdict_unscaled = {}
    for key in i_mc_typeshistdict:
        tmphist = i_mc_typeshistdict[key].Clone()
        tmphist_unscaled = i_mc_typeshistdict[key].Clone()
        tmphist.Scale(1.0,"width")
        mc_typehistdict[key] = tmphist
        mc_typehistdict_unscaled[key] = tmphist_unscaled

    n_xbins = data_mnv2d.GetNbinsX()
    n_ybins = data_mnv2d.GetNbinsY()
    print("hist n x bins: ",n_xbins,",\t hist n y bins: ",n_ybins)
    # my_catstodo = catstodo[1:]
    my_catstodo = [cat for cat in catstodo[1:]]
    tmp_dotypes = False
    for key in i_mc_typeshistdict.keys():
        if key not in my_catstodo:
            # my_catstodo = typestodo[1:]
            my_catstodo = [cat for cat in typestodo[1:]]
            tmp_dotypes = True
            break

    for projaxis in ["x","y"]:

        # thetitle = "%s %s %s proj%s"%(b_sample,c_var,"sigma",projaxis)
        thename = "%s_%s_proj%s"%(canvas_name, nametag, projaxis)
        thetitle = "%s%s proj%s"%(canvas_title,nametag.replace("_"," "),projaxis)
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
        
        # Make the projections
        data_mnvproj_list = MakeProjHistList(data_mnv2d,projaxis)
        mc_mnvproj_list = MakeProjHistList(mc_mnv2d,projaxis)

        mc_typesproj_listdict = {}

        for key in mc_typehistdict:
            if key not in mc_typesproj_listdict:
                mc_typesproj_listdict[key] = []
            tmp_list = MakeProjHistList(mc_typehistdict[key],projaxis)
            for hist in tmp_list:
                tmp_hist = hist.Clone()
                tmp_hist.SetFillColor(catscolors[key])
                # if key in bkgcats:
                #     # tmp_hist.SetFillStyle(bkgfillstyle)
                #     tmp_hist.SetFillStyle(bkgfillstyle[key])
                if tmp_dotypes:
                    # if key >= 10: tmp_hist.SetFillStyle(bkgfillstyle)
                    if key >= 10: 
                        tmp_hist.SetFillStyle(bkgfillstyle[key])
                    tmp_hist.SetLineColor(ROOT.kBlack)
                    mc_typesproj_listdict[key].append(tmp_hist.Clone())
                    continue

                tmp_hist.SetLineColor(ROOT.TColor.GetColorDark(catscolors[key]))
                mc_typesproj_listdict[key].append(tmp_hist.GetCVHistoWithStatError())

        # TODO: the 1D total projections
        # total projection to 1D
        data_mnvprojtot = MnvH1D()
        mc_mnvprojtot = MnvH1D()
        mc_typestotproj_dict = {}
        if projaxis == "x":
            data_mnvprojtot = data_mnv2d_unscaled.ProjectionX("%s_proj%s"%(data_mnv2d_unscaled.GetName(),projaxis), 0, data_mnv2d_unscaled.GetNbinsY()+2)#, "width e")
            mc_mnvprojtot = mc_mnv2d_unscaled.ProjectionX("%s_proj%s"%(mc_mnv2d_unscaled.GetName(),projaxis), 0, mc_mnv2d_unscaled.GetNbinsY()+2)#, "width e")
            for key in mc_typehistdict:
                tmp_totproj = mc_typehistdict_unscaled[key].ProjectionX("%s_proj%s"%(mc_typehistdict_unscaled[key].GetName(),projaxis), 0, mc_typehistdict_unscaled[key].GetNbinsY()+2)#, "width e")
                mc_typestotproj_dict[key] = tmp_totproj
        if projaxis == "y":
            data_mnvprojtot = data_mnv2d_unscaled.ProjectionY("%s_proj%s"%(data_mnv2d_unscaled.GetName(),projaxis), 0, data_mnv2d_unscaled.GetNbinsX()+2)#, "width e")
            mc_mnvprojtot = mc_mnv2d_unscaled.ProjectionY("%s_proj%s"%(mc_mnv2d_unscaled.GetName(),projaxis), 0, mc_mnv2d_unscaled.GetNbinsX()+2)#, "width e")
            for key in mc_typehistdict:
                tmp_totproj = mc_typehistdict_unscaled[key].ProjectionY("%s_proj%s"%(mc_typehistdict_unscaled[key].GetName(),projaxis), 0, mc_typehistdict_unscaled[key].GetNbinsY()+2)#, "width e")
                mc_typestotproj_dict[key] = tmp_totproj
        proj_y_title = z_title
        if projaxis == "x":
            tmp_units = "(%s"%x_title.split(" (") [1]
            proj_y_title = "Counts / %s"%tmp_units
        if projaxis == "y":
            tmp_units = "(%s"%y_title.split(" (") [1]
            proj_y_title = "Counts / %s"%tmp_units
        DrawDataMCPlot1D(data_mnvprojtot, mc_mnvprojtot, mc_typestotproj_dict, proj_xtitle, proj_y_title, outdirname, canvas_name, thetitle,"_totalproj%s"%(projaxis))
        # if "E_{Avail}" in proj_xtitle and not do_comparison:
        # if "E_{Avail}" in proj_xtitle:
        #     DrawDataMCTypesPlot1D_AxisChange(data_mnvprojtot, mc_mnvprojtot, mc_typestotproj_dict, proj_xtitle, z_title, outdirname, canvas_name, canvas_title+" total proj")
 
        # ROOT.gStyle.SetErrorX(0.) # This turns off the horizontal error bars
        ROOT.gStyle.SetEndErrorSize(end_error_size/2) # This makes the ticks at the end of the error bars longer


        n_pads = len(data_mnvproj_list)
        print(n_pads)

        # These are the hists w/ total error
        data_hist_list = []
        # These are the hists w/ just stat error
        data_stat_list = []
        # These are just used for the CV
        mc_hist_list = []
        # # These are used for the errors, to make a band around MC
        mc_band_list = []

        for hist in data_mnvproj_list:
            data_hist, data_stat = GetDataHistsForPlot(hist)
            data_hist.SetMarkerSize(data_marker_size2d)
            data_stat.SetMarkerSize(data_marker_size2d)
            data_hist_list.append(data_hist)
            data_stat_list.append(data_stat)
        # TODO: do I actually use these?
        for hist in mc_mnvproj_list:
            mc_hist, mc_band = GetMCHistsForPlot(hist)
            mc_hist_list.append(mc_hist)
            mc_band_list.append(mc_band)
        maxlist = [hist.GetMaximum() for hist in data_hist_list] + [hist.GetMaximum() for hist in mc_hist_list]
        global_max = max(maxlist)

        calc_tmp_pad_scale = True
        multipliers = []
        if len(i_multipliers) == n_pads:
            calc_tmp_pad_scale = False
            multipliers = i_multipliers
            # global_max = 4.0E-37
        stack_list = []
        for i in range(n_pads):
            stack_list.append(THStack("%s_%0.3d"%(key,i),"%s_%0.3d"%(key,i)))
        for i in range(n_pads):
            tmp_pad_scale = 1.0
            if calc_tmp_pad_scale:
                tmp_pad_max = 0.0
                tmp_pad_max = max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum())
                if tmp_pad_max == 0:
                    tmp_pad_max = 1.0
                tmp_pad_scale = eval('{:.{p}g}'.format(global_max / tmp_pad_max, p=3))
                multipliers.append(tmp_pad_scale)
            else:
                tmp_pad_scale = multipliers[i]
            
            data_hist_list[i].Scale(tmp_pad_scale)
            data_stat_list[i].Scale(tmp_pad_scale)
            mc_hist_list[i].Scale(tmp_pad_scale)
            mc_band_list[i].Scale(tmp_pad_scale)
            mc_hist_list[i].SetLineWidth(typeslinewidth)
            mc_band_list[i].SetLineWidth(typeslinewidth)
            # tmp_stack = THStack()
            # for key in mc_typesproj_listdict:
            for cat in reversed(my_catstodo):
                # if cat == "data": continue
                mc_typesproj_listdict[cat][i].Scale(tmp_pad_scale)
                tmp_type_hist = mc_typesproj_listdict[cat][i].Clone()
                # tmp_type_hist.Scale(tmp_pad_scale)
                # if cat in bkgcats:
                #     tmp_type_hist.SetFillStyle(bkgfillstyle[cat])
                if type(cat) == int:
                    hist.SetLineColor(ROOT.kBlack)
                    if cat >= 10: 
                        hist.SetFillStyle(bkgfillstyle[cat])
                else:
                    hist.SetLineColor(ROOT.TColor.GetColorDark(catscolors[cat]))

                tmp_type_hist.SetLineWidth(typeslinewidth)
                stack_list[i].Add(tmp_type_hist)

            data_hist_list[i].SetMaximum(1.2 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
            data_hist_list[i].SetMinimum(0.001*data_hist_list[i].GetMaximum())

            if proj_xtitle.split(" (")[0] in scaleY:
                pad.SetLogy()
                data_hist_list[i].SetMaximum(1.5 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
                # data_hist_list[i].SetMinimum(data_hist_list[i].GetMaximum()*1000)
            
            data_hist_list[i].GetXaxis().SetNdivisions(505)
            data_hist_list[i].GetYaxis().SetNdivisions(505)
            data_hist_list[i].GetYaxis().SetLabelSize(data_hist_list[i].GetXaxis().GetLabelSize())
        
        gc = PanelCanvas(thename, canvas_nxbins, canvas_nybins, round(xsize), round(ysize))
        gc.SetTopMargin(0.05)
        gc.SetLeftMargin(0.08)
        gc.SetRightMargin(0.05)
        gc.SetBottomMargin(0.1)
        # gc.SetFrameLineWidth(1)
        gc.SetXTitle(proj_xtitle)
        gc.SetYTitle(z_title)
        gc.SetTitleSize(_xsize*0.03)

        gc.Draw()
        for stackopt in ["stack", "nostack"]:
            
            for i in range(n_pads):
                pad = gc.cd(i+1)
                pad.SetFrameLineWidth(2)
                pad.Draw()
                data_hist_list[i].Draw("9 axis")
            for i in range(n_pads):
                pad = gc.cd(i+1)
                pad.Draw()

                if stackopt == "nostack":
                    for tmp_hist in stack_list[i].GetHists():
                        tmp_hist.SetFillStyle(0)
                        if tmp_dotypes:
                            tmp_hist.SetLineWidth(0)
                            continue
                        tmp_hist.SetLineWidth(typeslinewidth+1)
                    mc_hist_list[i].SetLineWidth(typeslinewidth+1)
                    mc_band_list[i].SetLineWidth(typeslinewidth+1)

                    mc_band_list[i].Draw("9 E2 ][ same")
                    stack_list[i].Draw("9 nostack hist same")
                    mc_hist_list[i].Draw("9 HIST SAME")
                else:
                    stack_list[i].Draw("9 HIST same")
            

                data_stat_list[i].Draw("9 SAME %s"%staterror_drawopt)
                data_hist_list[i].Draw("9 SAME E1 X0")
                data_hist_list[i].Draw("9 SAME axis")

                range_string = "{loedge} < {var} < {hiedge}".format(loedge = round(plot_bins[i], 3), var =proj_ytitle.split(" (")[0], hiedge = round(plot_bins[i+1], 3))
                binrange_latex = ROOT.TLatex()
                binrange_latex.SetTextAlign(33) # top right
                binrange_latex.SetNDC()
                binrange_latex.SetTextFont(42)
                binrange_latex.SetTextSize(0.025)
                binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)

                multip_string = "#times {:g}".format(float('{:.{p}g}'.format(multipliers[i], p=2)))
                multip_latex = ROOT.TLatex()
                multip_latex.SetTextAlign(32)
                multip_latex.SetNDC()
                multip_latex.SetTextFont(42)
                multip_latex.SetTextSize(0.028)
                multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.05),multip_string)
                pad.Modified()
                pad.Update()
            pad = gc.cd(n_pads+1)
            pad.Draw()

            padwidth = 1 - pad.GetLeftMargin() - pad.GetRightMargin()
            leg = TLegend(pad.GetLeftMargin()+padwidth/20,(1.-(pad.GetTopMargin())-0.01), 1 - (pad.GetRightMargin() + padwidth/20),(pad.GetBottomMargin()+0.01))
            leg.SetBorderSize(0)
            leg.SetFillColor(-1)
            leg.SetTextSize(round(legendfontsize/3))
            leg.AddEntry(data_hist_list[0], catsnames["data"],"pe")
            if tmp_dotypes:
                if stackopt == "nostack":
                    leg.AddEntry(mc_band_list[i], catsnames["mctot"],"fl")
                    leg.SetNColumns(1)
                else:
                    leg.AddEntry(0, "", "")
                    for cat in typestodo_leg:
                        leg.AddEntry(mc_typesproj_listdict[cat][0],catsnames[cat],"fl")
                    leg.SetNColumns(2)  
            else:
                for cat in my_catstodo:
                    leg.AddEntry(mc_typesproj_listdict[cat][0],catsnames[cat],"fl")
            leg.Draw()
            pad.Modified()

            gc.SetHistTexts()
            gc.Draw()
            sigma_canvas_name = thename + "_Types"
            # gc.Print(os.path.join(outdirname, sigma_canvas_name + ".png"))
            # gc.Print(os.path.join(outdirname,"source", sigma_canvas_name + ".C"))
            gc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s"%(thetitle," Types"))


        gc.cd()
        gc.ResetPads()
        gc.SetYTitle("Data / Simulation")
        gc.SetXTitle(proj_xtitle)
        gc.Modified()
        gc.Update()
        leg.Clear()
        ratio_list = []
        ratio_stat_list = []
        straightline_list = []
        mcerror_list = []
        typesratio_listdict = {}
        typesratiostack_listdict = {}
        for i in range(n_pads):
            ratio_mnvh = MakeDataMCRatioForPlot(data_mnvproj_list[i],mc_mnvproj_list[i])
            ratio_hist, ratio_stat = GetDataHistsForPlot(ratio_mnvh)

            # ratio_hist.SetMinimum(0.001)
            # ratio_hist.SetMaximum(2.999)
            ratio_hist.SetMinimum(0.0001)
            ratio_hist.SetMaximum(1.9999)
            ratio_hist.SetFillStyle(1001)
            ratio_hist.SetLineColor(ROOT.kBlack)
            ratio_hist.SetLineWidth(1)
            ratio_hist.SetMarkerSize(data_marker_size2d)

            ratio_hist.GetXaxis().SetNdivisions(505)
            ratio_hist.GetYaxis().SetNdivisions(505)
            ratio_hist.GetYaxis().SetLabelSize(ratio_hist.GetXaxis().GetLabelSize())
            ratio_list.append(ratio_hist)
            ratio_stat.SetLineWidth(1)
            ratio_stat.SetFillStyle(1001)
            ratio_stat.SetMarkerSize(data_marker_size2d)
            ratio_stat.SetLineColor(ROOT.kBlack)
            ratio_stat_list.append(ratio_stat)

            # typesratio_dict = {}
            # for key in mc_typesproj_listdict:
            for key in reversed(my_catstodo):
                # tmp_typesratio = MakeDataMCRatio(mc_typesproj_listdict[key][i],mc_hist_list[i])
                tmp_typesratio = mc_typesproj_listdict[key][i].Clone()
                tmp_typesratio.Divide(tmp_typesratio,mc_hist_list[i],1.0,1.0)
                tmp_typesratio.SetLineWidth(typeslinewidth+1)
                tmp_typesratio.SetFillColor(0)
                tmp_typesratio.SetLineColor(catscolors[key])
                # tmp_typesratio.SetLineColor(catscolors[key])
                if tmp_dotypes:
                    if key > 10:
                        tmp_typesratio.SetLineStyle(2)
                    else:
                        if typeslinedarker:
                            tmp_typesratio.SetLineColor(ROOT.TColor.GetColorDark(catscolors[key]))
                if key not in typesratio_listdict.keys():
                    typesratio_listdict[key] = []
                typesratio_listdict[key].append(tmp_typesratio)
                # typesratio_dict[key] = tmp_typesratio
            if tmp_dotypes:
                for key in reversed(typestodo_leg):
                    if key > 10 or key in typesratiostack_listdict: continue
                    typesratiostack_listdict[key] = []
                for key in reversed(typestodo_leg):
                    if key > 10:
                        tmp_stack = THStack()
                        tmp_hist = typesratio_listdict[key][i].Clone()
                        tmp_hist.SetLineStyle(7)
                        tmp_stack.Add(tmp_hist)
                        typesratiostack_listdict[key-10].append(tmp_stack)
                for key in reversed(typestodo_leg):
                    if key <= 10:
                        tmp_hist = typesratio_listdict[key][i].Clone()
                        if tmp_hist.GetEntries() == 0: continue
                        typesratiostack_listdict[key][i].Add(tmp_hist)

            straightline = TH1D()
            # straightline = fmcerror.Clone()
            straightline = mc_hist_list[i].Clone()
            # for bin in range(1,mc_hist_list[i].GetXaxis().GetNbins() + 1):
            for j in range(1,mc_hist_list[i].GetXaxis().GetNbins() + 1):
                straightline.SetBinContent(j,1.0)
            # straightline.SetLineColor(ROOT.kRed)
            straightline.SetLineColor(catscolors["mctot"])
            straightline.SetLineWidth(3)
            straightline.SetFillStyle(0)
            straightline_list.append(straightline)

            tmp_mnvh_mc = mc_mnvproj_list[i].Clone()
            tmp_mnvh_mc.ClearAllErrorBands()
            tmp_mnvh_mc.AddMissingErrorBandsAndFillWithCV(mc_mnvproj_list[i])
            tmp_mnvh_mc.Divide(tmp_mnvh_mc,mc_mnvproj_list[i],1.0,1.0)
            # tmp_mnvh_mc.SetFillColor(ROOT.kRed-10)
            # tmp_mnvh_mc.SetFillColorAlpha(ROOT.kRed-10,0.7)
            # tmp_mnvh_mc.SetLineColor(ROOT.kRed)
            tmp_mnvh_mc.SetFillColor(catscolors["mctot"])
            tmp_mnvh_mc.SetFillColorAlpha(catscolors["mctot"],0.4)
            tmp_mnvh_mc.SetLineColor(catscolors["mctot"])
            tmp_mnvh_mc.SetLineWidth(3)
            tmp_mnvh_mc.SetMarkerStyle(0)
            tmp_mnvh_mc.SetFillStyle(1001)
            mcerror_list.append(tmp_mnvh_mc.GetCVHistoWithError())
            

        for i in range(n_pads):
            pad = gc.cd(i+1)
            pad.SetLogy(0)

            pad.Draw()
            ratio_list[i].Draw("9 axis")
            mcerror_list[i].Draw("9 E2 same ][")
            straightline_list[i].Draw("9 hist same X0 ][")
            if tmp_dotypes:
                # for cat in reversed(typestodo_leg):
                for cat in typestodo_leg:
                    if cat > 10: continue
                    typesratiostack_listdict[cat][i].Draw("9 HIST NOCLEAR SAME ][")
            else:
                for cat in typesratio_listdict:
                    typesratio_listdict[cat][i].Draw("9 HIST SAME ][")
            ratio_stat_list[i].Draw("9 same %s"%staterror_drawopt)
            ratio_list[i].Draw("9 same E1 X0")
            ratio_list[i].Draw("9 same axis")

            range_string = "{loedge} < {var} < {hiedge}".format(loedge = round(plot_bins[i], 3), var =proj_ytitle.split(" (")[0], hiedge = round(plot_bins[i+1], 3))
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.03)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),range_string)
            pad.Modified()
            pad.Update()
        pad = gc.cd(n_pads+1)
        pad.Draw()

        leg.AddEntry(ratio_list[0], catsnames["data"],"pe")
        leg.AddEntry(mcerror_list[0], "MnvTune v2.0.1", "fl")
        leg.SetNColumns(2)
        if tmp_dotypes:
            for cat in typestodo_leg:
                leg.AddEntry(typesratio_listdict[cat][0],catsnames[cat],"fl")
        else:
            for cat in my_catstodo:
                leg.AddEntry(typesratio_listdict[cat][0],catsnames[cat],"fl")
        leg.Draw()
        pad.Modified()
        gc.SetHistTexts()
        gc.Draw()
        # gc.Print(os.path.join(outdirname, thename + "_Types_ratio.png"))
        # gc.Print(os.path.join(outdirname,"source", thename + "_Types_ratio.C"))
        gc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s"%(canvas_title," Types Ratio"))
        gc.cd()
        gc.ResetPads()
        gc.Modified()
        gc.Update()
        

        del gc
    # return 0

def DrawDataMCPlot1D_new(i_data_hist, i_mc_hist, i_mc_typeshistdict, x_title, y_title, outdirname, canvas_name, canvas_title,nametag = "", do_stack = True, do_nostack = True):
    # mnvPlotter = SetupErrorSummary(MnvPlotter(8))
    mnvPlotter = MnvPlotter(8)
    SetupErrorSummary(mnvPlotter)
    
    mnv_data = i_data_hist.Clone()
    mnv_mc = i_mc_hist.Clone()
    mnv_data.Scale(1.0, "width")
    mnv_mc.Scale(1.0, "width")

    my_catstodo = [cat for cat in catstodo[1:]]
    bad_keys = []
    for key in my_catstodo:
        if key not in i_mc_typeshistdict: 
            bad_keys.append(key)
            continue
    for key in bad_keys:
        my_catstodo.remove(key)

    mc_typeshistdict = {}
    stack = THStack("stack","")
    for key in reversed(my_catstodo):
        if key not in i_mc_typeshistdict: continue
        hist = i_mc_typeshistdict[key].Clone()
        hist.Scale(1.0, "width")
        hist.SetLineWidth(typeslinewidth1D)
        hist.SetFillColor(catscolors[key])
        if key in bkgcats:
            # hist.SetFillStyle(bkgfillstyle[key]+100)
            # hist.SetFillColor(TColor.GetColorDark(hist.GetFillColor()))
            hist.SetFillStyle(3244)
            if type(key) == int:
                hist.SetLineStyle(7)
        stack.Add(hist)
        mc_typeshistdict[key] = hist.Clone()

    thename = canvas_name + nametag
    thetitle = canvas_title 

    ysize = _ysize
    xsize = _xsize

        
    plottitle_string = "%s - %s"%(canvas_title, x_title.split(" (")[0])

    mnv_data.SetLineWidth(typeslinewidth1D)
    data_hist, data_stat = GetDataHistsForPlot(mnv_data)
    data_hist.SetMarkerSize(data_marker_size)
    data_stat.SetMarkerSize(data_marker_size)
    data_hist.GetYaxis().SetTitle(y_title)
    data_hist.GetYaxis().SetTitleFont(42)
    data_hist.GetYaxis().CenterTitle()
    data_hist.GetYaxis().SetTitleOffset(0.6)
    data_hist.GetYaxis().SetTitleSize(0.07)
    data_hist.GetYaxis().SetLabelSize(0.05)

    mc_hist, mc_band = GetMCHistsForPlot(mnv_mc)
    mc_hist.SetLineWidth(typeslinewidth1D)
    mc_band.SetLineWidth(typeslinewidth1D)

    mnv_ratio = MakeDataMCRatioForPlot(mnv_data, mnv_mc)
    ratio, ratio_stat = GetDataHistsForPlot(mnv_ratio)
    ratio.SetMarkerSize(data_marker_size)
    ratio.SetLineWidth(typeslinewidth1D)
    ratio_stat.SetMarkerSize(data_marker_size)
    ratio_stat.SetLineWidth(typeslinewidth1D)

    ratio.SetFillStyle(0)
    ratio.SetMinimum(0.0001)
    ratio.SetMaximum(1.999)

    typesratio_dict = {}
    for key in my_catstodo:
        if key not in mc_typeshistdict: continue
        tmp_typesratio = mc_typeshistdict[key].Clone()
        tmp_typesratio.Divide(tmp_typesratio, mnv_mc,1.0,1.0)
        tmp_typesratio.SetLineWidth(typeslinewidth1D)
        tmp_typesratio.SetFillStyle(0)
        tmp_typesratio.SetFillColor(0)
        tmp_typesratio.SetLineColor(mc_typeshistdict[key].GetFillColor())
        if type(key) == int:
            if key > 10:
                tmp_typesratio.SetLineStyle(2)

        typesratio_dict[key] = tmp_typesratio
    typesratio_stack_dict = {}
    if 11 in my_catstodo:
        for key in reversed(my_catstodo):
            if key not in typesratio_dict: continue
            if key > 10: continue
            if key not in typesratio_stack_dict:
                typesratio_stack_dict[key] = {}
            tmp_hist = typesratio_dict[key].Clone()
            tmp_stack = THStack("tmpstack, i", "")
            if key + 10 not in my_catstodo:
                typesratio_stack_dict[key] = tmp_hist
                continue
            tmp_hist_bkg = typesratio_dict[key+10].Clone()
            tmp_hist_bkg.SetLineStyle(7)
            tmp_stack.Add(tmp_hist_bkg)
            typesratio_stack_dict[key] = tmp_stack
            if tmp_hist.GetEntries() == 0: continue
            typesratio_stack_dict[key].Add(tmp_hist)            
    ratio_mnvmc_band = mnv_mc.Clone()
    ratio_mnvmc_band.ClearAllErrorBands()
    ratio_mnvmc_band.AddMissingErrorBandsAndFillWithCV(mnv_mc)
    ratio_mnvmc_band.Divide(ratio_mnvmc_band,mnv_mc,1.0,1.0)
    straightline, band_ratio = GetMCHistsForPlot(ratio_mnvmc_band) 
    straightline.SetLineWidth(typeslinewidth1D)
    band_ratio.SetLineWidth(typeslinewidth1D)
    
    ROOT.gStyle.SetEndErrorSize(round(end_error_size*1.5)) # This makes the ticks at the end of the error bars longer

    pad_max = GetPadMax(mnv_data,mnv_mc,True)


    # mc_band.SetMaximum(1.2 * pad_max)
    # mc_band.SetMinimum(data_hist.GetMaximum()*0.001)

    # Now set up the canvas
    cc = ROOT.TCanvas(thename, thetitle,_xsize, _ysize)
    cc.SetCanvasSize(_xsize,_ysize)
    cc.SetLeftMargin(0.25)
    cc.SetRightMargin(0.15)
    cc.SetBottomMargin(0.1)
    if do_titleonplot:
        cc.SetTopMargin(0.1)
        tmp_topmarj = topmarg + 0.06
    cc.SetFrameLineWidth(1)
    cc.cd()
    cc.Draw()

    plottitle = ROOT.TLatex(pad_lmarg+((1-pad_rmarg -pad_lmarg)/2), 0.96,plottitle_string)
    plottitle.SetTextAlign(22)
    plottitle.SetTextFont(52)
    plottitle.SetTextSize(0.058)

    top = ROOT.TPad("hist", "hist", 0, ratio_frac, 1.0, 1.0)
    top.SetRightMargin(pad_rmarg)
    top.SetLeftMargin(pad_lmarg)
    top.SetTopMargin(tmp_topmarj)
    top.SetBottomMargin(0)
    top.SetFrameLineWidth(1)

    bottom = ROOT.TPad("Ratio", "Ratio", 0, 0, 1.0, ratio_frac)
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

    padwidth = 1 - pad_lmarg - pad_rmarg
    padheight = 1 - tmp_topmarj - bottommarg

    x2 = 1. - pad_rmarg - (0.02 * padwidth)
    x1 = x2 - 0.3 # padwidth * 0.17
    y2 = 1 - tmp_topmarj - (0.02 * padheight)
    y1 = y2 - 0.45 # * padheight
    tmp_latex_x = x2
    tmp_latex_y = y1 - 0.05
    leg = TLegend(x1, y1, x2, y2)
    leg.SetBorderSize(0)
    leg.SetFillColor(-1)
    leg.SetFillStyle(0)
    # leg.SetTextSize(legendfontsize)
    # leg.SetNColumns(2)
    leg.SetTextFont(42)
    if 11 in my_catstodo:
        leg.SetNColumns(2)
    
    stack_unstack = []
    # This will plot the histograms stacked on top of each other
    if do_stack:
        stack_unstack.append("stack")
    # This will plot the histograms unstacked
    if do_nostack:
        stack_unstack.append("nostack")
    # This will just plot data and total mc
    stack_unstack.append("nobreakdown")
    npasses = 0
    for whichstack in stack_unstack:

        top.cd()
        data_hist.SetMaximum(1.2 * pad_max)
        data_hist.SetMinimum(data_hist.GetMaximum()*0.001)
        if x_title.split(" (")[0] in scaleY:
            data_hist.SetMaximum(4.0 * pad_max)
            data_hist.SetMinimum(data_hist.GetMaximum()*0.0005)
            top.SetLogy()

        top.Modified()
        top.Update()
        # leg.Clear()
        data_hist.Draw("E1 E0 X0 9")
        if whichstack == "stack":
            tmp_stack = stack.Clone()
            for hist in tmp_stack.GetHists():
                hist.SetLineStyle(1)
            tmp_stack.Draw("hist  9 same")
        elif whichstack == "nostack":
            mc_band.Draw("9 E2 E0 ][ same")
            tmp_stack = stack.Clone()
            for hist in tmp_stack.GetHists():
                hist.SetFillStyle(0)
                hist.SetLineColor(hist.GetFillColor())
                hist.SetLineWidth(typeslinewidth1D)
            tmp_stack.Draw("hist nostack noclear 9 same")
            mc_hist.Draw("9 hist same")
        else:
            mc_band.Draw("9 E2 E0 ][ same")
            mc_hist.Draw("9 hist same")

        data_hist.Draw("PE1 E0 X0 same 9")
        
        if do_pinkstat:
            ROOT.gStyle.SetEndErrorSize(0) # This makes the ticks at the end of the error bars longer
            data_stat.Draw("9 SAME X0 %s E0"%staterror_drawopt)
            ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer
        else:
            data_stat.Draw("9 SAME X0 %s E0"%staterror_drawopt)

        data_hist.Draw("9 Same PE1 E0 X0")
        leg.Draw()

        prelim = AddPreliminary()
        prelim.SetTextAlign(11)
        prelim.DrawLatex(x1, y1 - 0.145, prelim_string)

        datapottext = AddDataPOTInfo()
        datapottext.SetTextAlign(11)
        datapottext.DrawLatex(x1, y1 - 0.045, datapot_string1)
        datapottext.DrawLatex(x1, y1 - 0.100, datapot_string2)

        chi2 = mnvPlotter.Chi2DataMC(mnv_data,mnv_mc,mnv_data.GetNbinsX()-1)
        chi2text = AddChi2Info()
        # chi2text.SetTextAlign(11)
        # chi2text.DrawLatex(x1, y1 - 0.205, "#it{#chi^{2}} = %.02f"%chi2)
        # chi2text.DrawLatex(x1, y1 - 0.255, "#it{ndf} = %d"%mnv_data.GetNbinsX())
        chi2text.SetTextAlign(31)
        if do_chi2onplot:
            chi2text.DrawLatex(x2, y1 - 0.045, "#it{#chi^{2}} = %.02f"%chi2)
            chi2text.DrawLatex(x2, y1 - 0.100, "#it{ndf} = %d"%mnv_data.GetNbinsX())
        top.Modified()
        top.Update()

        bottom.cd()

        ratio.SetTitle("")            
        ratio.GetYaxis().SetTitle("Data / MC")
        ratio.GetYaxis().SetTitleFont(42)
        ratio.GetYaxis().CenterTitle()
        ratio.GetYaxis().SetTitleSize(0.06 * areaScale)
        ratio.GetYaxis().SetTitleOffset(0.6 / areaScale)
        ratio.GetYaxis().SetLabelSize(0.04 * areaScale)
        ratio.GetYaxis().SetNdivisions(505)

        # ratio.GetXaxis().SetTitle(vars_info[c_var]["title"])
        ratio.GetXaxis().SetTitle(x_title)
        ratio.GetXaxis().CenterTitle()
        ratio.GetXaxis().SetTitleOffset(0.8)
        ratio.GetXaxis().SetTitleSize(0.06 * areaScale)
        ratio.GetXaxis().SetLabelSize(0.04 * areaScale)
        
        ratio.Draw("9 E1 E0 X0")

        # Now do mc uncertainties
        band_ratio.Draw("9 E2 same ][")
        straightline.Draw("9 Hist same, ][")
        if 11 in my_catstodo:
            for key in reversed(typestodo_leg):
                if key > 10: continue
                typesratio_stack_dict[key].Draw("9 HIST NOCLEAR SAME")
        elif whichstack!="nobreakdown":
            for key in reversed(my_catstodo):
                if key not in typesratio_dict: continue
                if key == "data": continue
                typesratio_dict[key].SetLineColor(catscolors[key])
                typesratio_dict[key].Draw("9 HIST SAME")
        
        if do_pinkstat:
            ROOT.gStyle.SetEndErrorSize(0) # This makes the ticks at the end of the error bars longer
            ratio_stat.Draw("9 SAME X0 %s E0"%staterror_drawopt)
            ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer
        else:
            ratio_stat.Draw("9 SAME X0 %s E0"%staterror_drawopt)
        ratio.Draw("9 same E1 E0 X0")
        ratio.Draw("9 same axis")
        bottom.Modified()
        bottom.Update()

        leg.AddEntry(data_hist, "Data","pe")
        leg.AddEntry(band_ratio, catsnames[0],"fl")
        if whichstack == "stack":
            for cat in my_catstodo:
                if cat not in mc_typeshistdict: continue
                if 11 in mc_typeshistdict:
                    if cat > 10: continue
                leg.AddEntry(mc_typeshistdict[cat],catsnames[cat], "fl")
                if 11 in mc_typeshistdict:
                    leg.AddEntry(mc_typeshistdict[cat+10],catsnames[cat+10], "fl")
        elif whichstack == "nostack":
            for cat in my_catstodo:
                if cat not in mc_typeshistdict: continue
                mc_typeshistdict[cat].SetLineColor(mc_typeshistdict[cat].GetFillColor())
                if 11 in mc_typeshistdict:
                    if cat > 10: continue
                leg.AddEntry(mc_typeshistdict[cat],catsnames[cat], "l")
                if 11 in mc_typeshistdict:
                    mc_typeshistdict[cat+10].SetLineStyle(7)
                    leg.AddEntry(mc_typeshistdict[cat+10],catsnames[cat+10], "l")
        if x_title.split(" (")[0] in scaleX:
            top.SetLogx()
            bottom.SetLogx()
            top.Modified()
            top.Update()
            bottom.Modified()
            bottom.Update()
        cc.cd()
        if do_titleonplot:
            plottitle.Draw()
        cc.Modified()
        cc.Update
        cc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s %s"%(thetitle," Types1D", whichstack))
        leg.Clear()
        top.Clear()
        bottom.Clear()
        top.Modified()
        top.Update()
        bottom.Modified()
        bottom.Update()
        cc.Modified()
        cc.Update()

    cc.cd()
    cc.Clear()
    cc.Modified()
    cc.Update()

def DrawDataMCPlot2D_new(i_data_hist, i_mc_hist, i_mc_typeshistdict, x_varname, x_units, x_bins, y_varname, y_units, y_bins, z_title, outdirname, canvas_name, canvas_title, nametag,i_multipliers = [], do_stack = True, do_nostack = True, do_error_summary = False):
    mnvPlotter = MnvPlotter(8)
    SetupErrorSummary(mnvPlotter)

    data_mnv2d = i_data_hist.Clone()
    mc_mnv2d = i_mc_hist.Clone()
    data_mnv2d.Scale(1.0, "width")
    mc_mnv2d.Scale(1.0, "width")

    # These don't get bin width normalized before they get used for the total 1D projection hists
    data_mnv2d_unscaled = i_data_hist.Clone()
    mc_mnv2d_unscaled = i_mc_hist.Clone()

    mc_typeshistdict = {}
    mc_typeshistdict_unscaled = {}
    for key in i_mc_typeshistdict:
        tmphist = i_mc_typeshistdict[key].Clone()
        tmphist_unscaled = i_mc_typeshistdict[key].Clone()
        tmphist.Scale(1.0,"width")
        mc_typeshistdict[key] = tmphist
        mc_typeshistdict_unscaled[key] = tmphist_unscaled
    # n_xbins = data_mnv2d.GetNbinsX()
    # n_ybins = data_mnv2d.GetNbinsY()
    n_xbins = len(x_bins) - 1 
    n_ybins = len(y_bins) - 1
    print("hist n x bins: ",n_xbins,",\t hist n y bins: ", n_ybins)
    # my_catstodo = catstodo[1:]
    my_catstodo = [cat for cat in catstodo[1:]]
    bad_keys = []
    for key in my_catstodo:
        if key not in mc_typeshistdict: 
            bad_keys.append(key)
            continue
    for key in bad_keys:
        my_catstodo.remove(key)

    x_title = "%s (%s)"%(x_varname, x_units)
    y_title = "%s (%s)"%(y_varname, y_units)
    prelim = AddPreliminary()
    prelim.SetTextAlign(31)
    datapottext = AddDataPOTInfo()
    datapottext.SetTextAlign(31)
    chi2 = mnvPlotter.Chi2DataMC(data_mnv2d,mc_mnv2d,n_xbins*n_ybins)
    chi2text = AddChi2Info()
    # chi2text.SetTextAlign(11)
    # chi2text.DrawLatex(x1, y1 - 0.205, "#it{#chi^{2}} = %.02f"%chi2)
    # chi2text.DrawLatex(x1, y1 - 0.255, "#it{ndf} = %d"%mnv_data.GetNbinsX())
    chi2text.SetTextAlign(31)
    chi2_string = "#it{#chi^{2}} = %.02f"%chi2
    
    ndf_string = "#it{ndf} = %d"%(n_xbins*n_ybins)

    for projaxis in ["x","y"]:
        plottitle_string = "%s - %s , %s"%(canvas_title, x_varname, y_varname)
        # Info needed for the canvas
        thename = "%s_%s_proj%s"%(canvas_name, nametag, projaxis)
        thetitle = "%s%s proj%s"%(canvas_title,nametag.replace("_"," "),projaxis)
        ysize = _ysize
        xsize = _xsize
        canvas_nxbins = n_xbins
        canvas_nybins = n_ybins

        # Info needed for panels
        # This is the bin ranges for the panels
        plot_bins = y_bins

        projtot1d_y_title = z_title
        proj_x_varname = x_varname
        proj_x_units = x_units
        proj_y_varname = y_varname
        proj_y_units = y_units

        if projaxis == "y":
            canvas_nxbins = n_ybins
            canvas_nybins = n_xbins
            plot_bins = x_bins
            proj_x_varname = y_varname
            proj_x_units = y_units
            proj_y_varname = x_varname
            proj_y_units = x_units
        proj_xtitle = "%s (%s)"%(proj_x_varname, proj_x_units)
        if "#sigma" in z_title:
            projtot1d_y_title = "d#sigma /^{} d%s (cm^{2}/^{}%s/^{}Nucleon)"%(proj_x_varname,proj_x_units)
        else:
            projtot1d_y_title = "Counts / (%s)"%proj_x_units
        binrange_list = []
        for i in range(len(plot_bins)-1):
            range_string = "{loedge} < {var} < {hiedge}".format(
                loedge = round(plot_bins[i], 3), 
                var = "%s #lower[-0.25]{#scale[0.6]{(%s)}}"%(proj_y_varname, proj_y_units), 
                hiedge = round(plot_bins[i+1], 3)
            )
            binrange_list.append(range_string)

        # Make the projections
        data_mnvproj_list = MakeProjHistList(data_mnv2d, projaxis, canvas_nybins)
        mc_mnvproj_list = MakeProjHistList(mc_mnv2d, projaxis, canvas_nybins)
        mc_typesproj_listdict = {}
        for key in mc_typeshistdict:
            if key not in mc_typesproj_listdict:
                mc_typesproj_listdict[key] = []
            tmp_list = MakeProjHistList(mc_typeshistdict[key],projaxis, canvas_nybins)
            for hist in tmp_list:
                tmp_hist = hist.Clone()
                tmp_hist.SetFillColor(catscolors[key])
                if key in bkgcats:
                    tmp_hist.SetFillStyle(3244)
                mc_typesproj_listdict[key].append(tmp_hist.Clone())
                # mc_typesproj_listdict[key].append(tmp_hist.GetCVHistoWithStatError())

        # 1D total projections
        data_mnvprojtot = MnvH1D()
        mc_mnvprojtot = MnvH1D()
        mc_typestotproj_dict = {}
        if projaxis == "x":
            data_mnvprojtot = data_mnv2d_unscaled.ProjectionX("%s_proj%s"%(data_mnv2d_unscaled.GetName(),projaxis), 0, data_mnv2d_unscaled.GetNbinsY()+2)#, "width e")
            mc_mnvprojtot = mc_mnv2d_unscaled.ProjectionX("%s_proj%s"%(mc_mnv2d_unscaled.GetName(),projaxis), 0, mc_mnv2d_unscaled.GetNbinsY()+2)#, "width e")
            for key in mc_typeshistdict:
                tmp_totproj = mc_typeshistdict_unscaled[key].ProjectionX("%s_proj%s"%(mc_typeshistdict_unscaled[key].GetName(),projaxis), 0, mc_typeshistdict_unscaled[key].GetNbinsY()+2)#, "width e")
                mc_typestotproj_dict[key] = tmp_totproj
        if projaxis == "y":
            data_mnvprojtot = data_mnv2d_unscaled.ProjectionY("%s_proj%s"%(data_mnv2d_unscaled.GetName(),projaxis), 0, data_mnv2d_unscaled.GetNbinsX()+2)#, "width e")
            mc_mnvprojtot = mc_mnv2d_unscaled.ProjectionY("%s_proj%s"%(mc_mnv2d_unscaled.GetName(),projaxis), 0, mc_mnv2d_unscaled.GetNbinsX()+2)#, "width e")
            for key in mc_typeshistdict:
                tmp_totproj = mc_typeshistdict_unscaled[key].ProjectionY("%s_proj%s"%(mc_typeshistdict_unscaled[key].GetName(),projaxis), 0, mc_typeshistdict_unscaled[key].GetNbinsY()+2)#, "width e")
                mc_typestotproj_dict[key] = tmp_totproj
        data_mnvprojtot.SetLineColor(data_mnv2d_unscaled.GetLineColor())
        data_mnvprojtot.SetLineWidth(data_mnv2d_unscaled.GetLineWidth())
        data_mnvprojtot.SetMarkerStyle(data_mnv2d_unscaled.GetMarkerStyle())
        data_mnvprojtot.SetMarkerColor(data_mnv2d_unscaled.GetMarkerColor())

        mc_mnvprojtot.SetLineWidth(mc_mnvprojtot.GetLineWidth())
        mc_mnvprojtot.SetLineColor(mc_mnvprojtot.GetLineColor())
        mc_mnvprojtot.SetFillColor(mc_mnvprojtot.GetFillColor())
        for key in mc_typestotproj_dict:
            mc_typestotproj_dict[key].SetLineWidth(mc_typestotproj_dict[key].GetLineWidth())
            mc_typestotproj_dict[key].SetLineColor(mc_typestotproj_dict[key].GetLineColor())
            mc_typestotproj_dict[key].SetFillColor(mc_typestotproj_dict[key].GetFillColor())

        # TODO
        DrawDataMCPlot1D_new(
            data_mnvprojtot, mc_mnvprojtot, mc_typestotproj_dict, 
            proj_xtitle, 
            projtot1d_y_title, outdirname, 
            canvas_name, canvas_title,
            "_totalproj%s"%(projaxis), 
            do_stack, do_nostack
        )
        # if "E_{Avail}" in proj_xtitle and not do_comparison:
        # if "E_{Avail}" in proj_xtitle:
        #     DrawDataMCTypesPlot1D_AxisChange(data_mnvprojtot, mc_mnvprojtot, mc_typestotproj_dict, proj_xtitle, z_title, outdirname, canvas_name, canvas_title+" total proj")

        ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer


        n_pads = len(data_mnvproj_list)

        # These are the hists w/ total error
        data_hist_list = []
        # These are the hists w/ just stat error
        data_stat_list = []
        # These are just used for the CV
        mc_hist_list = []
        # These are used for the errors, to make a band around MC
        mc_band_list = []

        for hist in data_mnvproj_list:
            data_hist, data_stat = GetDataHistsForPlot(hist)
            data_hist_list.append(data_hist)
            data_stat_list.append(data_stat)

        # TODO: do I actually use these?
        for hist in mc_mnvproj_list:
            mc_hist, mc_band = GetMCHistsForPlot(hist)
            mc_hist_list.append(mc_hist)
            mc_band_list.append(mc_band)
        maxlist = [GetPadMax(data_hist_list[i],mc_hist_list[i], True) for i in range(len(data_hist_list))]
        global_max = max(maxlist)

        calc_tmp_pad_scale = True
        multipliers = []
        if len(i_multipliers) == n_pads:
            calc_tmp_pad_scale = False
            multipliers = i_multipliers
            if "#sigma" in z_title:
                global_max = 4.0E-37
        # Get the stacks ready
        stack_list = []
        for i in range(n_pads):
            stack_list.append(THStack("%s_%0.3d"%(key,i),"%s_%0.3d"%(key,i)))
        for i in range(n_pads):
            tmp_pad_scale = 1.0
            if calc_tmp_pad_scale:
                tmp_pad_max = 0.0
                tmp_pad_max = GetPadMax(data_hist_list[i],mc_hist_list[i], True)
                if tmp_pad_max == 0:
                    tmp_pad_max = 1.0
                tmp_pad_scale = eval('{:.{p}g}'.format(global_max / tmp_pad_max, p=3))
                multipliers.append(tmp_pad_scale)
            else:
                tmp_pad_scale = multipliers[i]
            
            data_hist_list[i].Scale(tmp_pad_scale)
            data_stat_list[i].Scale(tmp_pad_scale)
            mc_hist_list[i].Scale(tmp_pad_scale)
            mc_band_list[i].Scale(tmp_pad_scale)
            for cat in reversed(my_catstodo):
                # if cat == "data": continue
                if cat not in mc_typesproj_listdict: continue
                mc_typesproj_listdict[cat][i].Scale(tmp_pad_scale)
                tmp_type_hist = mc_typesproj_listdict[cat][i].Clone()
                tmp_type_hist.SetLineWidth(typeslinewidth)
                stack_list[i].Add(tmp_type_hist)

            data_hist_list[i].SetMaximum(1.2 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
            data_hist_list[i].SetMinimum(0.0001*data_hist_list[i].GetMaximum())
            
            data_hist_list[i].GetXaxis().SetNdivisions(505)
            data_hist_list[i].GetYaxis().SetNdivisions(505)
            data_hist_list[i].GetYaxis().SetLabelSize(data_hist_list[i].GetXaxis().GetLabelSize())

            if proj_xtitle.split(" (")[0] in scaleY:
                data_hist_list[i].SetMaximum(2.5 * global_max) #max(data_hist_list[i].GetMaximum(),mc_hist_list[i].GetMaximum()))
                data_hist_list[i].SetMinimum(0.0001*data_hist_list[i].GetMaximum())
                data_hist_list[i].GetYaxis().SetLabelSize(data_hist_list[i].GetXaxis().GetLabelSize()*0.67)

        # print(multipliers)
        # if projaxis == "y":
        #     sys.exit(1)
        gc = PanelCanvas(thename, canvas_nxbins, canvas_nybins, round(xsize), round(ysize))
        my_topmarg = 0.03
        if do_titleonplot: my_topmarg += 0.05
        my_bottommarg = 0.1
        my_rightmarg = 0.01
        my_leftmarg = 0.08
        
        gc.SetTopMargin(my_topmarg)
        gc.SetBottomMargin(my_bottommarg)
        gc.SetRightMargin(my_rightmarg)
        gc.SetLeftMargin(my_leftmarg)
        # if proj_x_varname in scaleY:
        #     # gc.SetLeftMargin(0.11)
        
        # gc.SetFrameLineWidth(1)
        gc.SetXTitle(proj_xtitle)
        gc.SetYTitle(z_title)
        gc.SetTitleSize(_xsize*0.03)

        plottitle = ROOT.TLatex(my_leftmarg+((1-my_rightmarg-my_leftmarg)/2), 0.96,plottitle_string)
        plottitle.SetTextAlign(22)
        plottitle.SetTextFont(52)
        plottitle.SetTextSize(0.058)

        gc.Draw()
        stack_unstack = []
        # This will plot the histograms stacked on top of each other
        if do_stack:
            stack_unstack.append("stack")
        # This will plot the histograms unstacked
        if do_nostack:
            stack_unstack.append("nostack")
        # This will just plot data and total mc
        stack_unstack.append("nobreakdown")
        for whichstack in stack_unstack:
            print("doing 2D for %s"%whichstack)
            for i in range(n_pads):
                pad = gc.cd(i+1)
                if proj_x_varname in scaleY:
                    pad.SetLogy()
                pad.SetFrameLineWidth(2)
                pad.Draw()
                data_hist_list[i].Draw("9 axis")

            for i in range(n_pads):
                pad = gc.cd(i+1)
                pad.Draw()
                tmp_stack_drawopts = ""
                if not pad.GetLogy():
                    tmp_stack_drawopts += " ]["
                if whichstack == "stack":
                    stack_list[i].Draw("9 HIST same%s"%tmp_stack_drawopts)
                elif whichstack == "nobreakdown":
                    mc_band_list[i].Draw("9 E2 ][ same")
                    mc_hist_list[i].Draw("9 HIST ][ SAME")
                else: # if whichstack == "nostack":
                    tmp_stack = stack_list[i].Clone()
                    for tmp_hist in tmp_stack.GetHists():
                        tmp_hist.SetLineWidth(typeslinewidth+1)
                        tmp_hist.SetLineColor(tmp_hist.GetFillColor())
                        # # Make the bkgs dotted
                        if tmp_hist.GetFillStyle() not in [0,1001]:
                            tmp_hist.SetLineStyle(7)
                        tmp_hist.SetFillStyle(0)
                    # sys.exit(1)
                    mc_band_list[i].Draw("9 E2 ][ same")
                    tmp_stack.Draw("9 nostack noclear hist same")
                    mc_hist_list[i].Draw("9 HIST ][ SAME")
                if do_pinkstat:
                    ROOT.gStyle.SetEndErrorSize(0) # This makes the ticks at the end of the error bars longer
                    data_stat_list[i].Draw("9 SAME %s E0"%staterror_drawopt)
                    ROOT.gStyle.SetEndErrorSize(end_error_size) # This makes the ticks at the end of the error bars longer
                else:
                    data_stat_list[i].Draw("9 SAME %s E0"%staterror_drawopt)
                data_hist_list[i].Draw("9 SAME E1 E0 X0")
                data_hist_list[i].Draw("9 SAME axis")

                tmp_range_string = binrange_list[i]
                binrange_latex = ROOT.TLatex()
                binrange_latex.SetTextAlign(33) # top right
                binrange_latex.SetNDC()
                binrange_latex.SetTextFont(42)
                binrange_latex.SetTextSize(0.025)
                binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),tmp_range_string)

                multip_string = "#times {:g}".format(float('{:.{p}g}'.format(multipliers[i], p=2)))
                multip_latex = ROOT.TLatex()
                multip_latex.SetTextAlign(32)
                multip_latex.SetNDC()
                multip_latex.SetTextFont(52)
                multip_latex.SetTextSize(0.028)
                multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.05),multip_string)

                
                pad.Modified()
                pad.Update()
            pad = gc.cd(n_pads+1)
            pad.Draw()

            padwidth = 1 - pad.GetLeftMargin() - pad.GetRightMargin()
            padheight = 1 - pad.GetTopMargin() - pad.GetBottomMargin()
            x1 = pad.GetLeftMargin() #+padwidth*.05
            y1 = (1.-(pad.GetTopMargin())-0.01)
            x2 =  1 - (pad.GetRightMargin())# + padwidth*.05)
            y2 =  (pad.GetBottomMargin())
            if 11 in my_catstodo:
            # if whichstack in ["nostack", "stack"]:
                x2 += padwidth * 0.6
            leg = TLegend(x1+0.01, y1, x2-0.01, y2)
            # leg.SetTextSize(legendfontsize*0.6)
            leg.SetBorderSize(0)
            leg.SetFillColorAlpha(0,0.0)
            leg.SetFillStyle(0)
            leg.AddEntry(data_hist_list[0], catsnames["data"],"pe")
            leg.SetNColumns(1) #TODO is this right?
            if whichstack == "nobreakdown":
                leg.AddEntry(mc_band_list[i], catsnames[0],"fl")
            elif whichstack == "nostack":
                leg.AddEntry(mc_band_list[i], catsnames[0],"fl")
                # leg.SetNColumns(2)
                for key in my_catstodo:
                    mc_typesproj_listdict[key][0].SetLineWidth(typeslinewidth+2)
                    mc_typesproj_listdict[key][0].SetLineColor(mc_typesproj_listdict[key][0].GetFillColor())
                if 11 in my_catstodo:
                    leg.SetNColumns(2)
                    for key in my_catstodo:
                        if key > 10: continue
                        leg.AddEntry(mc_typesproj_listdict[key][0],catsnames[key],"l")
                        mc_typesproj_listdict[key+10][0].SetLineStyle(7)
                        leg.AddEntry(mc_typesproj_listdict[key+10][0],catsnames[key+10],"l")
                else:
                    for key in my_catstodo:
                        leg.AddEntry(mc_typesproj_listdict[key][0],catsnames[key],"l")
            else: # if "stack":
                # leg.AddEntry(0,"","")
                # leg.SetNColumns(2)
                for key in my_catstodo:
                    mc_typesproj_listdict[key][0].SetLineWidth(typeslinewidth+2)
                if 11 in my_catstodo:
                    leg.AddEntry(0,"","")
                    leg.SetNColumns(2)
                    for key in my_catstodo:
                        if key > 10: continue
                        leg.AddEntry(mc_typesproj_listdict[key][0],catsnames[key],"fl")
                        leg.AddEntry(mc_typesproj_listdict[key+10][0],catsnames[key+10],"fl")
                else:
                    for key in my_catstodo:
                        # if key not in mc_typesproj_listdict: continue
                        leg.AddEntry(mc_typesproj_listdict[key][0],catsnames[key],"fl")
            leg.Draw()

            pad.Modified()
            pad = gc.cd(n_pads+2)
            latex_x = 1.0 - gc.GetRightMargin() - 0.01
            latex_y = (1.-(pad.GetTopMargin())) - 0.17*padheight
            prelim.SetTextSize(legendfontsize*0.57)
            datapottext.SetTextSize(legendfontsize*0.7)
            # prelim.DrawLatex(latex_x, latex_y, "MINER#it{^{}#nu}A Work In Progress")
            # datapottext.DrawLatex(latex_x, latex_y-0.05, "Data POT: 1.12 #times 10^{21}")
            datapottext.DrawLatex(latex_x, latex_y, datapot_string1)
            datapottext.DrawLatex(latex_x, latex_y-0.04, datapot_string2)
            prelim.DrawLatex(latex_x, latex_y-0.073, prelim_string)
            chi2text.SetTextSize(legendfontsize*0.6)
            if do_chi2onplot:
                chi2text.DrawLatex(latex_x, latex_y - 0.106, "%s, %s"%(chi2_string, ndf_string))
                # chi2text.DrawLatex(latex_x, latex_y - 0.146, ndf_string)
            if do_titleonplot:
                plottitle.Draw()
            gc.SetHistTexts()
            gc.Draw()
            sigma_canvas_name = "%s_Types_%s"%(thename, whichstack)
            gc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s %s"%(thetitle," Types2D", whichstack))
            for key in my_catstodo:
                if key not in mc_typesproj_listdict: continue
                mc_typesproj_listdict[key][0].SetLineWidth(typeslinewidth)
                mc_typesproj_listdict[key][0].SetLineColor(ROOT.TColor.GetColorDark((catscolors[key])))

       
            gc.cd()
            gc.ResetPads()
            gc.Modified()
            gc.Update()
        
        gc.SetYTitle("Ratio to %s"%catsnames[0])
        gc.SetXTitle(proj_xtitle)
        gc.SetLeftMargin(my_leftmarg)
        gc.Modified()
        gc.Update()

        leg.Clear()
        ratio_list = []
        ratio_stat_list = []
        straightline_list = []
        mcerror_list = []
        typesratio_listdict = {}
        typesratiostack_listdict = {}
        for i in range(n_pads):
            ratio_mnvh = MakeDataMCRatioForPlot(data_mnvproj_list[i],mc_mnvproj_list[i])
            ratio_hist, ratio_stat = GetDataHistsForPlot(ratio_mnvh)

            ratio_hist.SetMaximum(1.9999)
            ratio_hist.SetMinimum(0.0001)
# 
            ratio_hist.GetXaxis().SetNdivisions(505)
            ratio_hist.GetYaxis().SetNdivisions(505)
            ratio_hist.GetYaxis().SetLabelSize(ratio_hist.GetXaxis().GetLabelSize())
            ratio_list.append(ratio_hist)
            ratio_stat_list.append(ratio_stat)
            for key in reversed(my_catstodo):
                if key not in mc_typesproj_listdict: continue
                tmp_typesratio = TH1D(mc_typesproj_listdict[key][i].Clone())
                tmp_typesratio.Divide(tmp_typesratio,mc_hist_list[i],1.0,1.0)
                tmp_typesratio.SetLineWidth(typeslinewidth+1)
                tmp_typesratio.SetFillColor(0)
                tmp_typesratio.SetLineColor(mc_typesproj_listdict[key][i].GetFillColor())
                # if type(key) == int:
                #     if key >= 10: tmp_typesratio.SetLineStyle(2)
                if key not in typesratio_listdict.keys():
                    typesratio_listdict[key] = []
                typesratio_listdict[key].append(tmp_typesratio)
            if 11 in mc_typesproj_listdict:
                print(mc_typesproj_listdict.keys())
                # sys.exit(1)
                for key in reversed(my_catstodo):
                    if key not in mc_typesproj_listdict: continue
                    if key > 10: continue
                    if key not in typesratiostack_listdict: 
                        typesratiostack_listdict[key] = []
                    tmp_hist = typesratio_listdict[key][i].Clone()
                    tmp_stack = THStack()
                    if key + 10 not in my_catstodo[1:]:
                        # tmp_stack.Add(tmp_hist)
                        typesratiostack_listdict[key].append(tmp_hist)
                        continue
                    typesratiostack_listdict[key].append(tmp_stack)
                    tmp_hist_bkg = typesratio_listdict[key+10][i].Clone()
                    tmp_hist_bkg.SetLineStyle(7)
                    typesratiostack_listdict[key][i].Add(tmp_hist_bkg)
                    if tmp_hist.GetEntries() == 0: continue
                    typesratiostack_listdict[key][i].Add(tmp_hist)

            straightline = TH1D()
            straightline = mc_hist_list[i].Clone()
            for j in range(1,mc_hist_list[i].GetXaxis().GetNbins() + 1):
                straightline.SetBinContent(j,1.0)
            straightline.SetLineColor(catscolors[0])
            straightline.SetLineWidth(typeslinewidth+1)
            straightline.SetFillStyle(0)
            straightline_list.append(straightline)

            
            tmp_mnvh_mc = mc_mnvproj_list[i].Clone()
            tmp_mnvh_mc.ClearAllErrorBands()
            tmp_mnvh_mc.AddMissingErrorBandsAndFillWithCV(mc_mnvproj_list[i])
            tmp_mnvh_mc.Divide(tmp_mnvh_mc,mc_mnvproj_list[i],1.0,1.0)
            tmp_mnvh_mc.SetFillColor(catscolors[0])
            tmp_mnvh_mc.SetFillColorAlpha(catscolors[0],0.3)
            tmp_mnvh_mc.SetLineColor(catscolors[0])
            tmp_mnvh_mc.SetLineWidth(typeslinewidth)
            tmp_mnvh_mc.SetMarkerStyle(0)
            tmp_mnvh_mc.SetFillStyle(1001)
            mcerror_list.append(tmp_mnvh_mc.GetCVHistoWithError())
            
        ratio_maxlist = [GetPadMax(ratio_list[i],mcerror_list[i], True) for i in range(len(ratio_list))]
        ratio_global_max = max(ratio_maxlist)
        if ratio_global_max > 3.:
            for hist in ratio_list:
                hist.SetMaximum(int(ratio_global_max * 2 + 1)*0.5-0.0001)

        for i in range(n_pads):
            pad = gc.cd(i+1)
            pad.SetLogy(0)

            pad.Draw()
            ratio_list[i].Draw("9 E1 E0 axis")
            mcerror_list[i].Draw("9 E2 E0 same ][")
            straightline_list[i].Draw("9 hist same X0 ][")
            if 11 in mc_typesproj_listdict:
                print(typesratiostack_listdict.keys())
                for key in typestodo_leg:
                    if key > 10: continue
                    typesratiostack_listdict[key][i].Draw("9 HIST NOCLEAR SAME ][")
            else:
                for key in typesratio_listdict:
                    typesratio_listdict[key][i].Draw("9 HIST SAME ][")
            ratio_stat_list[i].Draw("9 same %s"%staterror_drawopt)
            ratio_list[i].Draw("9 same E1 E0 X0")
            ratio_list[i].Draw("9 same axis")

            tmp_range_string = binrange_list[i]
            multip_latex = ROOT.TLatex()
            multip_latex.SetTextAlign(33) # top right
            multip_latex.SetNDC()
            multip_latex.SetTextFont(42)
            multip_latex.SetTextSize(0.028)
            multip_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),tmp_range_string)
            pad.Modified()
            pad.Update()
        pad = gc.cd(n_pads+1)
        pad.Draw()
        if 11 in my_catstodo:
            leg.SetNColumns(2)

        leg.AddEntry(ratio_list[0], catsnames["data"],"pe")
        leg.AddEntry(mcerror_list[0], catsnames[0], "fl")
        for key in my_catstodo:
            if key not in typesratio_listdict: continue
            if 11 in my_catstodo:
                if key > 10: continue
            leg.AddEntry(typesratio_listdict[key][0],catsnames[key],"fl")
            if 11 in my_catstodo:
                typesratio_listdict[key+10][0].SetLineStyle(7)
                leg.AddEntry(typesratio_listdict[key+10][0],catsnames[key+10],"fl")

        leg.Draw()
        pad.Modified()
        gc.SetHistTexts()
        gc.Draw()
        plottitle.Modify()
        plottitle_string = plottitle_string.replace(canvas_title,canvas_title+" Ratio ")
        plottitle.SetTitle(plottitle_string)
        if do_titleonplot:
            plottitle.Draw()

        tmp_ratio_name = "%s_Typesratio"%(thename)
        gc.Print(os.path.join(outdirname,"source", tmp_ratio_name + ".C"))
        gc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s"%(thetitle," Types Ratio"))
        gc.cd()
        gc.ResetPads()
        gc.Modified()
        gc.Update()
        
        if not do_error_summary:
            del gc 
            continue
        gc.SetYTitle("Fractional Uncertainty")
        gc.SetXTitle(proj_xtitle)
        gc.SetLeftMargin(my_leftmarg)
        gc.SetTitleSize(_xsize*0.03)
        gc.Modified()
        gc.Update()


        include_stat_error = True
        solid_lines_only = False
        ignore_Threshold = 0.00001
        do_cov_area_norm = False
        error_group_name = ""
        do_fractional_uncertainty = True

        leg.Clear()
        padwidth = 1.0 - pad.GetLeftMargin() - pad.GetRightMargin()
        leg = TLegend(x1+0.01, y1, x2-0.01 + 0.4* padwidth, y2- pad.GetBottomMargin()*0.2)
        leg.SetBorderSize(0)
        leg.SetFillColorAlpha(0,0.0)
        # leg.SetFillColor(-1)
        # leg.SetNColumns(2)
        global_max = 0.0
        for i in range(n_pads):
            tmp_data_mnvh = data_mnvproj_list[i].Clone()
            total_error = tmp_data_mnvh.GetTotalError(include_stat_error, do_fractional_uncertainty, do_cov_area_norm).Clone()
            pad_max = total_error.GetBinContent(total_error.GetMaximumBin()) #.GetMaximum()
            if pad_max > global_max:
                global_max = pad_max
        if global_max > 1.0:
            global_max = 1.0
        # global_max = 0.5

        for i in range(n_pads):
            pad = gc.cd(i+1)
            tmp_data_mnvh = data_mnvproj_list[i].Clone()
            error_hists = mnvPlotter.GetSysErrorGroupHists(tmp_data_mnvh, do_fractional_uncertainty, do_cov_area_norm, ignore_Threshold)
            # error_hists = GetErrorHistsInGroup(tmp_data_mnvh, "GENIE Int. Model")[:6]
            # error_hists = GetErrorHistsInGroup(tmp_data_mnvh, "Tune")
            # error_hists = GetErrorHistsInGroup(tmp_data_mnvh, "FSI Model")
            # error_hists = GetErrorHistsInGroup(tmp_data_mnvh, "Flux")


            total_error = tmp_data_mnvh.GetTotalError(include_stat_error, do_fractional_uncertainty, do_cov_area_norm).Clone()
            total_error.SetMaximum(global_max * 1.3)
            mnvPlotter.ApplyNextLineStyle(total_error, True, True)
            total_error.SetLineWidth(typeslinewidth + 1)
            total_error.GetXaxis().SetNdivisions(505)
            total_error.GetYaxis().SetNdivisions(505)
            total_error.GetYaxis().SetLabelSize(total_error.GetXaxis().GetLabelSize())
            
            stat_error = tmp_data_mnvh.GetStatError(do_fractional_uncertainty)
            mnvPlotter.ApplyNextLineStyle(stat_error, False, True)
            stat_error.SetLineWidth(typeslinewidth + 1)
            stat_error.SetLineColor(12)
            stat_error.SetLineStyle(2)
            # stat_error.SetLineColor(12)
            if i == 0:
                tmp_total_err = total_error.Clone()
                tmp_total_err.SetLineWidth(total_error.GetLineWidth()+1)
                tmp_stat_error = stat_error.Clone()
                tmp_stat_error.SetLineWidth(stat_error.GetLineWidth()+1)
                leg.AddEntry(tmp_total_err, "Total Unc.", "l")
                # leg.AddEntry(0,"","")
                leg.AddEntry(tmp_stat_error, "Statistical", "l")

            total_error.Draw("9 axis")
            total_error.Draw("9 HIST same")
            stat_error.Draw("9 HIST same")


            # hist_index = 2
            for hist in error_hists:
                mnvPlotter.ApplyNextLineStyle(hist, False, True)
                hist.SetLineColor(mnvPlotter.error_color_map[hist.GetTitle()])
                hist.SetLineWidth(typeslinewidth + 1)
                hist.DrawCopy("9 HIST SAME")
                if i == 0:
                    # # tmp = hist.Clone()
                    # tmp.SetLineStyle(hist.GetLineStyle())
                    # tmp.SetLineColor(hist.GetLineColor())
                    hist.SetLineWidth(typeslinewidth+2)
                    leg.AddEntry(hist, hist.GetTitle(), "l")
            total_error.Draw("9 axis same")

            tmp_range_string = binrange_list[i]
            binrange_latex = ROOT.TLatex()
            binrange_latex.SetTextAlign(33) # top right
            binrange_latex.SetNDC()
            binrange_latex.SetTextFont(42)
            binrange_latex.SetTextSize(0.028)
            binrange_latex.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.01),tmp_range_string)

            pad.Update()
            pad.Modified()

        pad = gc.cd(n_pads+1)
        pad.Draw()
        leg.Draw()
        if do_titleonplot:
            plottitle_string = plottitle_string.replace(canvas_title + " Ratio ",canvas_title+" Error Summary")
            plottitle.SetTitle(plottitle_string)
            plottitle.Draw()
        
        # prelim.Modify()
        # prelim.DrawLatex(latex_x, latex_y, prelim_string)
        # datapottext.Modify()
        # datapottext.DrawLatex(latex_x, latex_y, "")
        

        gc.SetHistTexts()
        # gc.Draw()


        tmp_errror_summary_name = "%s_ErrorSummary"%(thename)
        # gc.Print(os.path.join(outdirname, thename + "_Types_ratio.png"))
        gc.Print(os.path.join(outdirname,"source", tmp_errror_summary_name + ".C"))
        gc.Print(os.path.join(outdirname,canvas_name+".pdf"),"Title:%s %s"%(thetitle," Types Error Summary"))
        gc.cd()
        gc.ResetPads()
        gc.Modified()
        gc.Update()
    
        del gc

def PrintSelectionBreakDown(i_mnv_data, i_mnv_mc, i_mc_typeshistdict):
    mnv_mc = i_mnv_mc.Clone()
    mnv_data = i_mnv_data.Clone()
    mc_typeshistdict = {}
    for key in i_mc_typeshistdict:
        mc_typeshistdict[key] = i_mc_typeshistdict[key].Clone()
    print("=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-Selection breakdown:=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-")
    tot_area = mnv_mc.Integral()#0,mnv_mc.GetNbinsX()+1)
    print("Total data area:\t%f"%mnv_data.Integral())
    print("Total MC area:\t%f"%tot_area)
    for key in mc_typeshistdict:
        type_area = mc_typeshistdict[key].Integral()#0,mnv_mc.GetNbinsX()+1)
        # if 11 in mc_typeshistdict:
        #     if key > 10:
        #         continue
        #     type_area+= mc_typeshistdict[key+10].Integral()#0,mnv_mc.GetNbinsX()+1)
        frac = type_area/tot_area
        print("\t %s:\t\t%.04f\t%f"%(key,frac,type_area))
    if "qelike" not in mc_typeshistdict: 
        print("Types totals: ")    
        for key in mc_typeshistdict:
            type_area = mc_typeshistdict[key].Integral()#0,mnv_mc.GetNbinsX()+1)
            if 11 in mc_typeshistdict:
                if key > 10:
                    continue
                type_area+= mc_typeshistdict[key+10].Integral()#0,mnv_mc.GetNbinsX()+1)
            frac = type_area/tot_area
            print("\t %s:\t\t%.04f\t%f"%(key,frac,type_area))
    print(">>>>>>>>>>>>>>>>>>>> NEntries info <<<<<<<<<<<<<<<<<<<<")
    tot_entries = mnv_mc.GetEntries()
    print("Total entries in data:\t%f"%mnv_data.GetEntries())
    print("Total entries in MC:\t%f"%tot_entries)
    for key in mc_typeshistdict:
        entries = mc_typeshistdict[key].GetEntries()
        frac = entries/tot_entries
        print("\t %s:\t\t%0.4f\t%f"%(key,frac,entries))
    if "qelike" not in mc_typeshistdict: 
        print("Types totals: ")    
        for key in mc_typeshistdict:
            entries = mc_typeshistdict[key].GetEntries()
            if 11 in mc_typeshistdict:
                if key > 10:
                    continue
            entries += mc_typeshistdict[key + 10].GetEntries()
            frac = entries/tot_entries
            print("\t %s:\t\t%0.4f\t%f"%(key,frac,entries))        
    print("=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-")


# def DrawDataMC2D_universal(i_data_hist, i_mc_ref_hist, i_mc_histdict, x_title, x_bins, x_units, y_title, y_bins, y_units, z_title, canvas_name, base_canvas_title, nametag, i_multipliers = [], do_stack = True, do_unstack = True):
#     data_mnv2d = i_data_hist.Clone()
#     mc_mnv2d = i_mc_hist.Clone()
#     data_mnv2d_unscaled = i_data_hist.Clone()
#     mc_mnv2d_unscaled = i_mc_hist.Clone()

#     data_mnv2d.Scale(1.0, "width")
#     mc_mnv2d.Scale(1.0, "width")    

#     mc_typehistdict = {}
#     mc_typehistdict_unscaled = {}
#     for key in i_mc_typeshistdict:
#         tmphist = i_mc_typeshistdict[key].Clone()
#         tmphist_unscaled = i_mc_typeshistdict[key].Clone()
#         tmphist.Scale(1.0,"width")
#         mc_typehistdict[key] = tmphist
#         mc_typehistdict_unscaled[key] = tmphist_unscaled

#     n_xbins = data_mnv2d.GetNbinsX()
#     n_ybins = data_mnv2d.GetNbinsY()
#     print("hist n x bins: ",n_xbins,",\t hist n y bins: ",n_ybins)
    



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
    },
    "EAvailhibin": {
        "title": "E_{Avail}",
        "units": "GeV",
        "bins": [],
    },
    "recoil": {
        "title": "recoil",
        "units": "GeV",
        "bins": [],
    },
}
catstodo = [
    "data",
    "qelike",
    "chargedpion",
    "neutralpion",
    "other",
    # "multipion",
    # "other_np",
    1,  #: "QE",
    8,  #: "2p2h",
    2,  #: "RES",
    3,  #: "DIS",
    4,  #: "COH",
    # 8,  #: "2p2h",
    11, #: "Bkg QE",
    18, #: "Bkg 2p2h",
    12, #: "Bkg RES",
    13, #: "Bkg DIS",
    14, #: "Bkg COH",
]

bkgcats = [
    # "data",
    # "qelike",
    "chargedpion",
    "neutralpion",
    "other",
    "multipion",
    "other_np",
    11,
    12,
    13,
    14,
    18,
]


catsnames = {
    "data": "Data", 
    "qelike":"QElike",
    "chargedpion":"1#pi^{#pm}",
    "neutralpion":"1#pi^{0}",
    "other":"Other",
    "multipion":"N#pi",
    "other_np":"Other",
    "mctot": "MnvTune v2.0.1",  # total mc
    0: "MnvTune v2.0.1",  # total mc
    1: "QE",             # QE
    2: "RES",            # RES
    3: "DIS",            # DIS
    4: "COH",            # COH
    8: "2p2h",           # 2p2h
    11: "Bkg-QE",             # QE
    12: "Bkg-RES",            # RES
    13: "Bkg-DIS",            # DIS
    14: "Bkg-COH",            # COH
    18: "Bkg-2p2h",           # 2p2h
}


typesnames = {
    1: "QE",
    2: "RES",
    3: "DIS",
    4: "COH",
    8: "2p2h",
    11: "Bkg QE",
    12: "Bkg RES",
    13: "Bkg DIS",
    14: "Bkg COH",
    18: "Bkg 2p2h",
}
typestodo = [
    "data",
    1,  #: "QE",
    8,  #: "2p2h",
    2,  #: "RES",
    3,  #: "DIS",
    4,  #: "COH",
    # 8,  #: "2p2h",
    11, #: "Bkg QE",
    18, #: "Bkg 2p2h",
    12, #: "Bkg RES",
    13, #: "Bkg DIS",
    14, #: "Bkg COH",
    # 18, #: "Bkg 2p2h",
]

typestodo_leg = [
    1,  #: "QE",
    11, #: "Bkg QE",
    8,  #: "2p2h",
    18, #: "Bkg 2p2h",
    2,  #: "RES",
    12, #: "Bkg RES",
    3,  #: "DIS",
    13, #: "Bkg DIS",
    4,  #: "COH",
    14, #: "Bkg COH",
]
types_list = [
    "",
    "QE",
    "RES",
    "DIS",
    "COH",
    "",
    "",
    "",
    "2p2h",
    "",
    "",
    "",
    "Bkg QE",
    "Bkg RES",
    "Bkg DIS",
    "Bkg COH",
    "",
    "",
    "",
    "Bkg 2p2h",
    "",
    "",
]


bkgfillstyle = {
    # # "chargedpion":  3212,
    # # "neutralpion":  3206,
    # # "other":        3221,
    # # "multipion":    3204,
    # # "other_np":     3221,
    # # 11:             3212,    # "Bkg QE"
    # # 12:             3206,  # "Bkg RES",
    # # 13:             3221,   # "Bkg DIS",
    # # 14:             3204,    # "Bkg COH",
    # # 18:             3216,  #"Bkg 2p2h",
    # "chargedpion":  3145,
    # "neutralpion":  3154,
    # "other":        3195,
    # "multipion":    3144,
    # "other_np":     3195,
    # 11:             3144,    # "Bkg QE"
    # 12:             3145,  # "Bkg RES",
    # 13:             3154,   # "Bkg DIS",
    # 14:             3195,    # "Bkg COH",
    # 18:             3109,  #"Bkg 2p2h",
    "chargedpion":  1001,
    "neutralpion":  1001,
    "other":        1001,
    "multipion":    1001,
    "other_np":     1000,
    11:             3144,    # "Bkg QE"
    12:             3144,  # "Bkg RES",
    13:             3144,   # "Bkg DIS",
    14:             3144,    # "Bkg COH",
    18:             3144,  #"Bkg 2p2h",

}
catscolors = {
    "data":         ROOT.kBlack, 
    "qelike":       ROOT.kP10Blue,
    "chargedpion":  ROOT.kP10Yellow,
    "neutralpion":  ROOT.kP10Orange,
    "multipion":    ROOT.kP10Violet,
    "other":        ROOT.kP10Ash,
    "other_np":     ROOT.kP10Ash,
    # "mctot":        ROOT.kP10Red,
    "mctot":        ROOT.kP8Red,
    0:              ROOT.kP8Red,     # total mc
    1:              ROOT.kP8Blue,    # QE
    2:              ROOT.kP8Orange,  # RES
    3:              ROOT.kP8Pink,   # DIS
    4:              ROOT.kP8Green,    # COH
    8:              ROOT.TColor.GetColorBright(ROOT.kP8Azure),  # 2p2h
    11:              ROOT.kP8Blue,    # QE
    12:              ROOT.kP8Orange,  # RES
    13:              ROOT.kP8Pink,   # DIS
    14:              ROOT.kP8Green,    # COH
    18:              ROOT.TColor.GetColorBright(ROOT.kP8Azure),  # 2p2h

}


samplenames = {
    "QElike_warped":        "no 2p2h tune",
    "QElike":               "QElike Signal Sample",
    "QElike_2track":        "QElike 2 track Sample",
    "QElike0Blob":          "QElike Signal w/o Blobs",
    "QElike1Blob":          "QElike Signal w/ 1 Blob",
    "QElikeOld":            "2D Era QElike Signal Sample",
    # "BlobSideband":         "1 #pi^{0} Sideband",
    "BlobSideband":         "Blob Sideband",
    "MultipBlobSideband":   "Multiple #pi Sideband",
    "HiPionThetaSideband":  "Backward #pi^{#pm} Sideband",
    "LoPionThetaSideband":  "Forward #pi^{#pm} Sideband",
    "TrackSideband":        "Track Sideband"
}

var_short_names = {
    "ERemoved": "E_{Removed}",
    "EAvail": "E_{Avail}",
    "EExcess": "E_{Excess}",
    "EAvailFromTruthBlobs": "E_{Avail}^{TruthBlobs}",
    "VisEMissing": "Vis E_{Missing}",
    "InvisEMissing": "Invis E_{Missing}",
    "recoil": "recoil",
    "ptmu": "p_{T}"
}
scaleX = [
    "E_{Avail}"
    "ERemoved", 
    "EExcess",
    # "InvisEMissing",
    "VisEMissing", 
    "ERemovedFromTruthBlobs",
]


if len(sys.argv) == 1:
    print ("enter root file name and optional 2nd argument to get tuned version")
flag = "types_"
filename = sys.argv[1]
if len(sys.argv)> 2:
    flag = "tuned_type_"

ROOT.TH1.AddDirectory(ROOT.kFALSE)

f = TFile.Open(filename,"READONLY")

plotdirbase = os.getenv("OUTPUTLOC")

plotdir = MakePlotDir("RawEventRates")
dirname = filename.replace(".root", "_RawEventRates")
# outfilename=filebasename1.replace(".root","_2DPlots")
outdirname = os.path.join(plotdir, dirname)
if not os.path.exists(outdirname):
    print(outdirname)
    os.mkdir(outdirname)
if not os.path.exists(os.path.join(outdirname,"source")):
    print(os.path.join(outdirname,"source"))
    os.mkdir(os.path.join(outdirname,"source"))

keys = f.GetListOfKeys()

# h_pot = f.Get("POT_summary")
# dataPOT = h_pot.GetBinContent(1)
# mcPOTprescaled = h_pot.GetBinContent(2)
# POTScale = dataPOT / mcPOTprescaled
POTScale = 1.0
print("POTScale: ",POTScale)

if "varsFile" not in keys:
    bigvarconfig_string = f.Get("varsFile_5A").GetTitle()
else:
    bigvarconfig_string = f.Get("varsFile").GetTitle()
bigvarconfig_dict = json.loads(re.sub("//.*", "", bigvarconfig_string, flags = re.MULTILINE))


groups = {}



# find all the valid histogram and group by keywords
ncats = 5
flag = "reconstructed_types_"
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
    types = parse[4]

    if "simulfit" in types:
        continue
    if "tuned" not in types and dotuned and cat!="data":
        continue
    if "tuned" in types and not dotuned:
        continue

    # if hist != "h2D": 
    #     continue
    if cat not in catstodo: 
        continue
    if "tuned" in types:
        flag = "reconstructed_tuned_types_"
    index = 0
    if "types" in types:
        if not dotypes:
            continue
        tmp_index = int(parse[4].replace(flag,""))
        if tmp_index == 0:
            continue
        index = tmp_index
    
    h = f.Get(name).Clone()
    if h.GetEntries() <= 0 and index not in [1,2,3,4,8]: 
    # if h.GetEntries() <= 0 and index not in [1,2,3,8]: 
        continue

    if hist not in groups.keys():
        groups[hist] = {}
    if sample not in groups[hist].keys():
        groups[hist][sample] = {}
    if variable not in groups[hist][sample].keys():
        groups[hist][sample][variable] = {}
    if cat not in groups[hist][sample][variable].keys():
        groups[hist][sample][variable][cat] = {}
    if index not in groups[hist][sample][variable][cat]:
        groups[hist][sample][variable][cat][index] = {}

    if "data" in cat:
        h.SetMarkerColor(ROOT.kBlack)
        h.SetLineColor(ROOT.kBlack)
        h.SetMarkerStyle(data_marker_style)
        h.SetMarkerSize(data_marker_size)
    else:
        print("scaling MC hist with potscale of ", POTScale)
        h.Scale(POTScale)
        h.SetFillColor(catscolors[cat])
        h.SetLineColor(ROOT.TColor.GetColorDark(catscolors[cat]))
        if index!= 0:
            h.SetFillColor(catscolors[index])
            h.SetLineColor(ROOT.TColor.GetColorDark(catscolors[index]))
        if cat in bkgcats:# or index > 10:
            h.SetFillStyle(3144)

        h.SetLineWidth(typeslinewidth1D)
        # if cat in bkgcats:
        #     h.SetFillStyle(bkgfillstyle[cat])
            # if typeslinedarker:
            #     h.SetFillColor(ROOT.TColor.GetColorDark(ROOT.kBlack))
            # h.SetFillStyle(3224)
    groups[hist][sample][variable][cat][index] = h

    # Now set up the variable
    if hist!="h2D":
        if variable in vars_info and len(vars_info[variable]["bins"])==0:
            var_title = vars_info[variable]["title"]
            var_units = vars_info[variable]["units"]
            if len(vars_info[variable]["bins"]) == 0:
                print("making bins")
                varconfig = bigvarconfig_dict["1D"][variable]
                if "bins" in varconfig.keys():
                    bins1D = [float(tmpbin) for tmpbin in varconfig["bins"]]
                    vars_info[variable]["bins"] = bins1D
                elif "nbins" in varconfig.keys():
                    mini = varconfig["min"]
                    maxi = varconfig["max"]
                    width = (maxi - mini)/varconfig["nbins"]
                    bins1D = [mini + tmpbin * width for tmpbin in range(0,varconfig["nbins"]+1)]
                    # print(bins1D)
                    vars_info[variable]["bins"] = bins1D
    else:
        for var in variable.split("_"):
            if var in vars_info and len(vars_info[var]["bins"])==0:
                var_title = vars_info[var]["title"]
                var_units = vars_info[var]["units"]
                if len(vars_info[var]["bins"]) == 0:
                    print("making bins")
                    varconfig = bigvarconfig_dict["1D"][var]
                    if "bins" in varconfig.keys():
                        bins1D = [float(tmpbin) for tmpbin in varconfig["bins"]]
                        vars_info[var]["bins"] = bins1D
                    elif "nbins" in varconfig.keys():
                        mini = varconfig["min"]
                        maxi = varconfig["max"]
                        width = (maxi - mini)/varconfig["nbins"]
                        bins1D = [mini + tmpbin * width for tmpbin in range(0,varconfig["nbins"]+1)]
                        # print(bins1D)
                        vars_info[var]["bins"] = bins1D


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
modelname = "MnvTunev2.0.1_FIXME"

for a_hist in groups.keys():

    for a_sample in groups[a_hist].keys():
        if a_hist == "h":
            varlistname = "_".join(list(groups[a_hist][a_sample].keys()))
            tmp_canvas_basename = "%s_%s_%s"%(modelname,a_sample,varlistname)
            tmp_canvas_basetitle = "%s %s %s"%(modelname, a_sample,varlistname)
            pdf_canvas_name = "gl_"+tmp_canvas_basename+"_recoplots1D_FinalStates"
            if dotuned:
                pdf_canvas_name+= "_tuned"
            else:
                pdf_canvas_name+= "_untuned"
            dummy_canvas = ROOT.TCanvas(pdf_canvas_name,pdf_canvas_name,_xsize,_ysize)
            dummy_canvas.SetCanvasSize(_xsize,_ysize)
            dummy_canvas.Print(os.path.join(outdirname,pdf_canvas_name+".pdf")+"[","pdf")

        datasample = a_sample
        if a_sample == "QElike_warped":
            datasample = "QElike"
        if a_sample == "QElike" and dowarp: continue
        first = True

        if a_sample not in ["QElike"]:
            catstodo = reversed(catstodo)
        for b_var in groups[a_hist][a_sample].keys():
            print("starting on ", a_sample,b_var)

            # tmp_canvas_basename = "%s_%s_%s"%(modelname,b_sample,c_var)

            # Get the binning first
            # if it's 2D you'll need to do some other work
            var_units = "unit"
            xvar_name = ""
            xvar_units = "xunits"
            yvar_name = ""
            yvar_units = "yunits"
            tmp_xvar_bins = []
            tmp_yvar_bins = []
            if len(b_var.split("_")) == 2:
                for var in b_var.split("_"):
                    if var not in vars_info:
                        vars_info[var] = {"title": var, "units": unit, "bins":[]}
                        print("ERROR: variable not in varsinfo: %s"%(var))
                        continue
                xvar_name = vars_info[b_var.split("_")[0]]["title"]
                xvar_units = vars_info[b_var.split("_")[0]]["units"]
                yvar_name = vars_info[b_var.split("_")[1]]["title"]
                yvar_units = vars_info[b_var.split("_")[1]]["units"]
                tmp_xvar_bins = vars_info[b_var.split("_")[0]]["bins"]
                tmp_yvar_bins = vars_info[b_var.split("_")[1]]["bins"]
            else:
                if b_var not in vars_info:
                    vars_info[b_var] = {"title": var, "units": unit, "bins":[]}
                xvar_name = vars_info[b_var]["title"]
                xvar_units = vars_info[b_var]["units"]
                tmp_xvar_bins = vars_info[b_var]["bins"]
            
            tmp_xvar_title = "%s (%s)"%(xvar_name,xvar_units)
            tmp_yvar_title = "%s (%s)"%(yvar_name, yvar_units)
            tmp_counts_ztitle = "Counts / (%s) / (%s)"%(xvar_units, yvar_units)
            tmp_counts_ytitle_1d = "Counts / (%s) "%(xvar_units)

            tmp_data_hist = groups[a_hist][a_sample][b_var]["data"][0].Clone()
            if "mctot" not in groups[a_hist][a_sample][b_var]:
                groups[a_hist][a_sample][b_var]["mctot"] = {}
                # for itype in groups[a_hist][a_sample][b_var]["qelike"]:
                tmpmctothist = groups[a_hist][a_sample][b_var]["qelike"][0].Clone()
                # for c_cat in groups[a_hist][a_sample][b_var]:
                for c_cat in catstodo:
                    if type(c_cat) == int: continue
                    # if c_cat in ["data","mctot","qelike","bins"]:
                    if c_cat in ["data","mctot","qelike","qelikenot"]:
                        continue
                    print(c_cat)
                    tmpmctothist.Add(groups[a_hist][a_sample][b_var][c_cat][0])
                groups[a_hist][a_sample][b_var]["mctot"][0] = tmpmctothist.Clone()
            tmp_mctot_hist = groups[a_hist][a_sample][b_var]["mctot"][0].Clone()
            if "qelikenot" not in groups[a_hist][a_sample][b_var]:
                groups[a_hist][a_sample][b_var]["qelikenot"] = {}
                for itype in groups[a_hist][a_sample][b_var][bkgcats[0]]:
                    tmp_qelikenot_hist = groups[a_hist][a_sample][b_var][bkgcats[0]][itype].Clone(groups[a_hist][a_sample][b_var][bkgcats[0]][itype].GetName().replace(bkgcats[0],"qelikenot"))
                    for c_cat in bkgcats[1:]:
                        if c_cat in ["data","mctot","qelike","qelikenot"]:
                            continue
                        if type(c_cat) == int: continue
                        if c_cat not in catstodo:
                            continue
                        print(c_cat)
                        tmp_qelikenot_hist.Add(groups[a_hist][a_sample][b_var][c_cat][itype])
                    tmp_qelikenot_hist
                    groups[a_hist][a_sample][b_var]["qelikenot"][itype] = tmp_qelikenot_hist.Clone()

            tmp_mc_histdict = {}
            for c_cat in groups[a_hist][a_sample][b_var]:
                if c_cat not in ["data","mctot","bins","qelikenot"]:
                    tmp_mc_histdict[c_cat] = groups[a_hist][a_sample][b_var][c_cat][0].Clone()
            tmp_types_dict = {}
            for c_cat in ["qelike", "qelikenot"]:
                for itype in groups[a_hist][a_sample][b_var][c_cat]:
                    if itype not in [1,2,3,4,8]:
                        continue
                    tmp_type = itype
                    if c_cat == "qelikenot":
                        tmp_type += 10
                    tmp_types_dict[tmp_type] = groups[a_hist][a_sample][b_var][c_cat][itype].Clone()
                    tmp_types_dict[tmp_type].SetLineColor(ROOT.TColor.GetColorDark(catscolors[tmp_type]))
                    tmp_types_dict[tmp_type].SetFillColor(catscolors[tmp_type])
                    if tmp_type > 10:
                        tmp_types_dict[tmp_type].SetFillStyle(3244)
            if a_hist != "h":
                tmp_canvas_basename = "%s_%s_%s"%(modelname,a_sample,b_var)
                # tmp_canvas_basetitle = "%s %s %s"%(modelname, a_sample,b_var)
                # tmp_canvas_basetitle = "%s Sample"%(a_sample)
                tmp_canvas_basetitle = ""
                if dotuned:
                    tmp_canvas_basetitle = "Tuned "
                tmp_canvas_basetitle += "Event Selection"
                pdf_canvas_name = "gl_"+tmp_canvas_basename+"_recoplots2D_FinalStates"
                if dotuned:
                    pdf_canvas_name+= "_tuned"
                else:
                    pdf_canvas_name+= "_untuned"
                dummy_canvas = ROOT.TCanvas(pdf_canvas_name,pdf_canvas_name,_xsize,_ysize)
                dummy_canvas.SetCanvasSize(_xsize,_ysize)
                dummy_canvas.Print(os.path.join(outdirname,pdf_canvas_name+".pdf")+"[","pdf")
                # Do the final states ones first
                DrawDataMCPlot2D_new(
                    tmp_data_hist, tmp_mctot_hist, tmp_mc_histdict, 
                    # tmp_xvar_title, tmp_xvar_bins, 
                    # tmp_yvar_title, tmp_yvar_bins, 
                    xvar_name, xvar_units, tmp_xvar_bins, 
                    yvar_name, yvar_units, tmp_yvar_bins, 
                    tmp_counts_ztitle, 
                    outdirname, pdf_canvas_name, 
                    tmp_canvas_basetitle, 
                    "_FinalStates"
                )
                # Now do types
                DrawDataMCPlot2D_new(
                    tmp_data_hist, tmp_mctot_hist, tmp_types_dict, 
                    # tmp_xvar_title, tmp_xvar_bins, 
                    # tmp_yvar_title, tmp_yvar_bins, 
                    xvar_name, xvar_units, tmp_xvar_bins, 
                    yvar_name, yvar_units, tmp_yvar_bins, 
                    tmp_counts_ztitle, 
                    outdirname, 
                    pdf_canvas_name, 
                    tmp_canvas_basetitle, 
                    "_Types"
                )
                dummy_canvas.Print(os.path.join(outdirname,pdf_canvas_name+".pdf")+"]","pdf")
            else:
                # Do the final states ones first
                DrawDataMCPlot1D_new(
                    tmp_data_hist, tmp_mctot_hist, tmp_mc_histdict, 
                    tmp_xvar_title, 
                    tmp_counts_ytitle_1d, 
                    outdirname, pdf_canvas_name, 
                    tmp_canvas_basetitle, 
                    "_1d%s_FinalStates"%(b_var)
                )
                # Now do types
                DrawDataMCPlot1D_new(
                    tmp_data_hist, tmp_mctot_hist, tmp_types_dict, 
                    tmp_xvar_title, 
                    tmp_counts_ytitle_1d, 
                    outdirname, pdf_canvas_name, 
                    tmp_canvas_basetitle, 
                    "_1d%s_Types"%(b_var)
                )

        if a_sample not in ["QElike"]:
            catstodo = reversed(catstodo)
        if a_hist == "h":
            dummy_canvas.Print(os.path.join(outdirname,pdf_canvas_name+".pdf")+"]","pdf")
print("done with final states plots, working on types plots now")
for a_hist in groups.keys():
    for a_sample in groups[a_hist].keys():
        for b_var in groups[a_hist][a_sample].keys():
            tmp_data_hist = groups[a_hist][a_sample][b_var]["data"][0].Clone()
            tmp_mctot_hist = groups[a_hist][a_sample][b_var]["mctot"][0].Clone()
            tmp_mc_histdict = {}
            for c_cat in groups[a_hist][a_sample][b_var]:
                if c_cat not in ["data","mctot","bins","qelikenot"]:
                    tmp_mc_histdict[c_cat] = groups[a_hist][a_sample][b_var][c_cat][0].Clone()
            PrintSelectionBreakDown(tmp_data_hist,tmp_mctot_hist,tmp_mc_histdict)
            tmp_types_dict = {}
            for c_cat in ["qelike", "qelikenot"]:
                for itype in groups[a_hist][a_sample][b_var][c_cat]:
                    if itype not in [1,2,3,4,8]:
                        continue
                    tmp_type = itype
                    if c_cat == "qelikenot":
                        tmp_type += 10
                    tmp_types_dict[tmp_type] = groups[a_hist][a_sample][b_var][c_cat][itype].Clone()
            PrintSelectionBreakDown(tmp_data_hist,tmp_mctot_hist,tmp_types_dict)
            break
        break


# for a_hist in groups:
#     for a_sample in groups[a_hist]:
#         if a_hist == "h":
#             varlistname = "_".join(list(groups[a_hist][a_sample].keys()))
#             tmp_canvas_basename = "%s_%s_%s"%(modelname,a_sample,varlistname)
#             tmp_canvas_basetitle = "%s %s %s"%(modelname, a_sample,varlistname)
#             pdf_canvas_name = "gl_"+tmp_canvas_basename+"_recoplots1D_Types"
#             dummy_canvas = ROOT.TCanvas(pdf_canvas_name,pdf_canvas_name,_xsize,_ysize)
#             dummy_canvas.SetCanvasSize(2000,1500)
#             dummy_canvas.Print(os.path.join(outdirname,pdf_canvas_name+".pdf")+"[","pdf")

#         for b_var in groups[a_hist][a_sample]:


