import os,sys
import ROOT
from ROOT import TH1D, gPad, TCanvas, TText
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter
#ifndef plotting_functions_H
#define plotting_functions_H
FULLDUMP=False
# #define FULLDUMP  # dumps all syst error subgroups
#include <iostream>
#include <string>
#include <map>
#include <vector>

#include "PlotUtils/HistogramUtils.h"
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "PlotUtils/MnvPlotter.h"
#include "PlotUtils/MnvVertErrorBand.h"
#include "TCanvas.h"
#include "TText.h"

kDefaultStyle     = 0 #!< The Default style
kCompactStyle     = 1 #!< Same as the default style but with less whitespace
kNukeCCStyle      = 2 #!< Similar to compact but with NukeCC-specifics
kNukeCCPrintStyle = 3 
kCCNuPionIncStyle = 4 #!< compact with CCNuPionInc color scheme
kCCCohStyle       = 5 #!< Coherent rocks!!!
kCCQENuStyle      = 6

xmin = 0.
xmax = 20.e3
nbins = 30

do_fractional_uncertainty = True
do_cov_area_norm = False
include_stat_error = True

if do_fractional_uncertainty == "Frac":
    do_fractional_uncertainty_str = True
if do_fractional_uncertainty == "Abs":
    do_fractional_uncertainty_str = False

#do_fractional_uncertainty_str = do_fractional_uncertainty ? ("Frac") : ("Abs")
do_cov_area_norm_str = (do_cov_area_norm == "CovAreaNorm")

def setLogScale(logscale):
    gPad.SetLogy(False)
    gPad.SetLogx(False)
    if (logscale == 0): return
    if (logscale == 2 or logscale == 3): 
        gPad.SetLogy(True)
    
    if (logscale == 1 or logscale == 3): 
        gPad.SetLogx(True)


def resetLogScale():
    gPad.SetLogy(False)
    gPad.SetLogx(False)


#void PlotErrorSummary(PlotUtils.MnvH1D hist, label)
# def PlotErrorSummary(hist, label):  
#     if hist.InheritsFrom("TH2D"):
#     print("no error bands for 2D")

# void PlotVertBand(band, method_str, PlotUtils.MnvH1D hist)
# void PlotLatBand(band, method_str, PlotUtils.MnvH1D hist)
# void PlotVertUniverse(band, unsigned universe, method_str, PlotUtils.MnvH1D hist)
# void PlotLatUniverse(band, unsigned universe, method_str, PlotUtils.MnvH1D hist)
# void PlotCVAndError(PlotUtils.MnvH1D hist, label)
# void PlotTotalError(PlotUtils.MnvH1D hist, method_str)
# void Plot2D(PlotUtils.MnvH2D hist, label)
# void PlotCVAndError(PlotUtils.MnvH2D hist, label)

# integrator(PlotUtils.MnvH1D)
# integrator(PlotUtils.MnvH2D)

def PlotTotalError(hist, method_str): 
    if hist.InheritsFrom("TH2D"):
        print("no error bands for 2D")
        return
    
    hTotalErr = TH1D()
    hTotalErr = hist.GetTotalError(include_stat_error, do_fractional_uncertainty, do_cov_area_norm).Clone("h_total_err_errSum_%d"%(0))
    hTotalErr.SetDirectory(0)
    cF = TCanvas("c4", "c4")
    hTotalErr.SetTitle("Total Uncertainty (%s) %s "%(method_str, hist.GetTitle()))
    hTotalErr.Draw()
    cF.Print("%s_TotalUncertainty_%s_%s_%s.png"%(hist.GetName(), do_fractional_uncertainty_str, do_cov_area_norm_str, method_str))


# def PlotErrorSummary(cE, hist, label, logscale:  
#                      print(" no error summary for 2D" : 

def PlotErrorSummary(cE, hist, label, logscale):
    mnvPlotter = MnvPlotter(kCompactStyle)#PlotUtils.kCCQEAntiNuStyle)
    resetLogScale()
    # TCanvas cE ("c1","c1")
    #  hist.GetXaxis().SetTitle(hist.GetTitle())
    #  xaxis = mc.GetXaxis().GetTitle()
    # mnvPlotter.error_color_map.clear()

    mnvPlotter.axis_maximum = 0.2
    mnvPlotter.axis_minimum = 0.0
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
#ifndef NOGENIE
    # print(" include GENIE" )
    print ("summary_map",mnvPlotter.error_summary_group_map["FSI Model"])
    mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrAbs_N")
    mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrAbs_pi")
    mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrCEx_N")
    mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrCEx_pi")
    mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrElas_N")
    mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrElas_pi")
    mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrInel_N")
    mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrInel_pi")
    mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrPiProd_N")
    mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrPiProd_pi")
    mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_MFP_N")
    mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_MFP_pi")
    #
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_AGKYxF1pi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_AhtBY")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_BhtBY")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_CCQEPauliSupViaKF")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_CV1uBY")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_CV2uBY")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_EtaNCEL")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Mab")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaCCQEshape")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaNCEL")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaRES")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MvRES")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormCCQE")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormCCRES")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormDISCC")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormNCRES")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_RDecBR1gamma")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvn1pi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvn2pi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvn3pi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvp1pi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvp2pi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Theta_Delta2Npi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_VecFFCCQEshape")
#endif
    mnvPlotter.error_summary_group_map["Tune"].push_back("RPA_LowQ2")
    mnvPlotter.error_summary_group_map["Tune"].push_back("RPA_HighQ2")
    mnvPlotter.error_summary_group_map["Tune"].push_back("NonResPi")
    mnvPlotter.error_summary_group_map["Tune"].push_back("2p2h")
    mnvPlotter.error_summary_group_map["Tune"].push_back("LowQ2Pi")
    mnvPlotter.error_summary_group_map["Tune"].push_back("Low_Recoil_2p2h_Tune")

    # mnvPlotter.error_summary_group_map["Angle"].push_back("BeamAngleX")
    #   mnvPlotter.error_summary_group_map["Angle"].push_back("BeamAngleY")

    mnvPlotter.error_summary_group_map["Response"].push_back("response_em")
    mnvPlotter.error_summary_group_map["Response"].push_back("response_proton")
    mnvPlotter.error_summary_group_map["Response"].push_back("response_pion")
    mnvPlotter.error_summary_group_map["Response"].push_back("response_meson")
    mnvPlotter.error_summary_group_map["Response"].push_back("response_other")
    mnvPlotter.error_summary_group_map["Response"].push_back("response_low_neutron")
    mnvPlotter.error_summary_group_map["Response"].push_back("response_mid_neutron")
    mnvPlotter.error_summary_group_map["Response"].push_back("response_high_neutron")

    mnvPlotter.error_summary_group_map["Geant"].push_back("GEANT_Neutron")
    mnvPlotter.error_summary_group_map["Geant"].push_back("GEANT_Proton")
    mnvPlotter.error_summary_group_map["Geant"].push_back("GEANT_Pion")
    #
    mnvPlotter.error_summary_group_map["Muon Energy"].push_back("Muon_Energy_MINOS")
    mnvPlotter.error_summary_group_map["Muon Energy"].push_back("Muon_Energy_MINERvA")
    mnvPlotter.error_summary_group_map["Muon Energy"].push_back("MINOS_Reconstruction_Efficiency")
    mnvPlotter.error_summary_group_map["Muon Energy"].push_back("Muon_Energy_Resolution")
    mnvPlotter.error_summary_group_map["Muon Energy"].push_back("BeamAngleX")
    mnvPlotter.error_summary_group_map["Muon Energy"].push_back("BeamAngleY")
    #  mnvPlotter.error_summary_group_map["Unfolding"].push_back("Unfolding")

    mnvPlotter.DrawErrorSummary(hist, "TR", include_stat_error, False, 0.0, do_cov_area_norm, "", do_fractional_uncertainty)

    plotname = "Title: ErrorSummary_%s_%s_%s"% (hist.GetName(), do_cov_area_norm_str, label)
    t = TText()
    t = TText(.3, .95, label)
    t.SetNDC(1)
    t.SetTextSize(.03)
    setLogScale(logscale)
    #  gPad.SetLogy(False)
    #  gPad.SetLogx(False)
    #  if (logscale== 2 || logscale ==3):
    #    gPad.SetLogy()
    #    hist.SetMinimum(0.001)
    #  
    #  if (logscale== 1 || logscale ==3): gPad.SetLogx():
    t.Draw()
    cE.Print(cE.GetName(), plotname)
    resetLogScale()
    if FULLDUMP:
        for group in mnvPlotter.error_summary_group_map: 
            # print(" error summary for " , group.first :
            mnvPlotter.DrawErrorSummary(hist, "TR", include_stat_error, False, 0.0, do_cov_area_norm, group.first, do_fractional_uncertainty)
            plotname = "Title: ErrorSummary_%s_%s_%s_%s"%(hist.GetName(), group.first, do_cov_area_norm_str, label)
            t = TText(.3, .95, label)
            t.SetNDC(1)
            t.SetTextSize(.03)
            setLogScale(logscale)
            #  gPad.SetLogy(False)
            #  gPad.SetLogx(False)
            #  if (logscale== 2 || logscale ==3):
            #    gPad.SetLogy()
            #    hist.SetMinimum(0.001)
            #  
            #  if (logscale== 1 || logscale ==3): gPad.SetLogx():
            t.Draw()
            cE.Print(cE.GetName(), plotname)
            resetLogScale()
    
#endif

    # mnvPlotter.MultiPrint(&cE, plotname, "pdf")
    #   mnvPlotter.DrawErrorSummary(hist,"TR",include_stat_error,True,0.0, do_cov_area_norm, "Angle",False)
    #   plotname = Form("ResponseErrorSummary_%s_%s_%s", hist.GetName(),do_cov_area_norm_str,label)
    #   mnvPlotter.MultiPrint(&cE, plotname, "png")


def PlotVertBand(band, method_str, hist):
    h1 = TH1D()
    h1 = hist.GetVertErrorBand(band).GetErrorBand(do_fractional_uncertainty, do_cov_area_norm).Clone("%s_%s_%s"%(hist.GetName(), band, method_str))

    if (h1 == 0): 
        print(" no error band " , band )
    
    h1.SetDirectory(0)
    # TH1* h1 = (TH1*)hist.GetVertErrorBand(band)
    cF = TCanvas("c4", "c4")
    h1.SetTitle("%s Uncertainty (%s) Theta_#nu (rad)"%( band, method_str))
    h1.Draw("h")
    cF.Print("%s_%s_band_%s.png"%( hist.GetName(), band, method_str))


def PlotLatBand(band, method_str,  hist) :
    h1 = TH1D()
    h1 = hist.GetLatErrorBand(band).GetErrorBand(do_fractional_uncertainty, do_cov_area_norm).Clone("%s_%s_%s"%( hist.GetName(), band, method_str))
    h1.SetDirectory(0)
    # TH1* h1 = (TH1*)hist.GetLatErrorBand(band)
    cF = TCanvas("c1", "c1")
    h1.SetTitle("%s Uncertainty (%s) E_#nu (MeV)"%( band, method_str))
    h1.Draw("h")
    cF.Print("%s_%s_band_%s.png"%( hist.GetName(), band, method_str))


def PlotVertUniverse(band, universe, method_str, hist): 
    # print("band " , band , " " , hist.GetName() )
    h1 = hist.GetVertErrorBand(band).GetHist(universe)
    h1.SetDirectory(0)
    cF = TCanvas("c1", "c1")
    h1.SetLineColor(ROOT.kBlack)
    h1.SetLineStyle(1)
    h1.Draw("hist")
    cF.Print("%s_%s_band_universe%i_%s.png"%( hist.GetName(), band, universe + 1, method_str))


def PlotLatUniverse(band,universe, method_str,  hist): 
    h1 = hist.GetLatErrorBand(band).GetHist(universe)
    h1.SetDirectory(0)
    cF = TCanvas("c1", "c1")
    h1.SetLineColor(ROOT.kBlack)
    h1.SetLineStyle(1)
    h1.Draw("hist")
    cF.Print("%s_%s_band_universe%i_%s.png"%( hist.GetName(), band, universe + 1, method_str))


def PlotCVAndError(cE, idatahist,  ihist, label, cov_area = do_cov_area_norm, logscale = 0, binwid = True):
    if idatahist.InheritsFrom("TH2D"):
        PlotCVAndError2D(cE, idatahist,  ihist, label, cov_area, logscale, binwid)
    else:
        PlotCVAndError1D(cE, idatahist,  ihist, label, cov_area, logscale, binwid)



def PlotCVAndError1D(cE, idatahist,  ihist, label, cov_area = do_cov_area_norm, logscale = 0, binwid = True):
    resetLogScale()
    # PlotUtils.MnvPlotter mnvPlotter(PlotUtils.kCCQEAntiNuStyle)
    mnvPlotter = MnvPlotter()
    # mnvPlotter.SetBinWidthNorm(False)
    mnvPlotter.draw_normalized_to_bin_width = 0
    # binwid = True
    #  need to clone as plan to bin width correct
    if not ihist or not idatahist: 
        print(" No datahist " , ihist , " or mchist " , ihist , " " , label )
        return
    datahist = MnvH1D()
    datahist = idatahist.Clone()
    datahist.SetDirectory(0)
    hist = MnvH1D()
    hist = ihist.Clone()
    hist.SetDirectory(0)
    # TCanvas cE ("c1","c1")
    # hist.GetXaxis().SetTitle(Form("%s",hist.GetTitle() ))
    hist.GetXaxis().GetTitle()
    hist.GetYaxis().SetTitle("%s"%( "Counts per unit"))
    # PlotUtils.MnvH1D datahist =new PlotUtils.MnvH1D("adsf", "E_#nu (MeV)", nbins, xmin, xmax)
    statPlusSys = True
    mcScale = 1.
    useHistTitles = False
    # print(" check bin width " )
    # datahist.Print("ALL")
    if (binwid): 
        # print(" scale width " )
        datahist.Scale(1., "width")
        hist.Scale(1., "width")
    
    bkgdHist = MnvH1D()
    dataBkgdHist = MnvH1D()
    # datahist.Print("ALL")
    #  gPad.SetLogy(False)
    #  gPad.SetLogx(False)
    #  if (logscale== 2 || logscale ==3): 
    #    gPad.SetLogy()
    #  
    #  if (logscale== 1 || logscale ==3): gPad.SetLogx():
    setLogScale(logscale)
    cov_area = False
    t = TText(.3, .95, label)
    t.SetNDC(1)
    t.SetTextSize(.03)

    # print(label , " BinWidthNorm before" , datahist.GetNormBinWidth(: :
    # datahist.SetNormBinWidth(1.0)
    # hist.SetNormBinWidth(1)
    # mnvPlotter.SetBinWidthNorm(not binwid)
    # print(label , " BinWidthNorm after" , datahist.GetNormBinWidth() )
    mnvPlotter.SetROOT6Palette(57)  # kBird
    
    print ("datahist",type(datahist))
    mnvPlotter.DrawDataMCWithErrorBand(datahist, hist, mcScale, "TL", useHistTitles, 0, 0, cov_area, statPlusSys)
    stat = TH1D()
    stat = datahist.GetCVHistoWithStatError()
    
    stat.SetLineColor(ROOT.kBlack)
    stat.SetMarkerColor(ROOT.kBlack)
    stat.Draw("E1 same")
    # mnvPlotter.DrawMCWithErrorBand(hist) #I think that this call only shows stat errors.
    plotname = "Title: %s_CV_w_err_%s"%( datahist.GetName(), label)
    t.Draw()
    cE.Print(cE.GetName(), plotname)
    if idatahist != ihist:   
        d = MnvH1D()   # don't plot ratio for identical hists.
        d = datahist.Clone()
        d.SetDirectory(0)
        m = MnvH1D()
        m = hist.Clone()
        m.SetDirectory(0)
        if (d.GetXaxis().GetNbins() != m.GetXaxis().GetNbins()): 
            print(" data and mc bins don't agree" , d.GetName() , m.GetName() )
            return
        
        mc = MnvH1D()
        mc = m.Clone()
        mc.SetDirectory(0)
        mc.ClearAllErrorBands()
        mc.AddMissingErrorBandsAndFillWithCV(m)

        d.Divide(d, mc, 1., 1.)

        d.GetYaxis().SetTitle("Data/MC")
        m.Divide(m, mc, 1., 1.)
        # no idea why I should have to do this
        # m.Print("ALL")
        # datahist.Draw()
        cov_area = False
        # mnvPlotter.SetBinWidthNorm(False)
        mnvPlotter.DrawDataMCRatio(d, m, mcScale, True, True)  # "TL", useHistTitles, NULL, NULL,cov_area, statPlusSys)

        t.Draw()
        plotname2 = "Title: ratio %s_CV_w_err_%s"%( datahist.GetName(), label)

        cE.Print(cE.GetName(), plotname2)
    
    resetLogScale()
    # mnvPlotter.MultiPrint(&cE, plotname, "pdf")
    #  mnvPlotter.MultiPrint(&cE, plotname, "C")


def Plot2D(cE, ihist, label, logscale = 0, binwid = True): 
    setLogScale(logscale)
    hist = MnvH2D()
    hist = ihist.Clone()
    hist.SetDirectory(0)
    setLogScale(logscale)

    xtitle = hist.GetXaxis().GetTitle()
    ytitle = hist.GetYaxis().GetTitle()
    title = "%s by %s: %s"%( xtitle, ytitle, label)

    hist.GetXaxis().CenterTitle()
    hist.GetYaxis().CenterTitle()
    hist.SetTitle("%s"%( title))

    #  gPad.SetLogy(False)
    #  gPad.SetLogx(False)
    #  if (logscale == 2 || logscale == 3): gPad.SetLogy():
    #  if (logscale == 1 || logscale == 3): gPad.SetLogx():
    t = TText(.3, .95, label)
    hist.Draw("COLZ")
    t.SetNDC(1)
    t.SetTextSize(.03)
    plotname = "Title: %s_CV_%s"%( hist.GetName(), label)
    t.Draw()

    cE.Print(cE.GetName(), plotname)
    resetLogScale()


# def Plot2DFraction(cE, MnvH1D ihist1, ihist2, label, logscale = 0, binwid = False):   # null version for 1d


def Plot2DFraction( cE, ihist1,  ihist2, label, logscale = 0, binwid = False):
    
    print("pr2D fraction" , ihist1.GetName() )
    setLogScale(logscale)

    hist1 = ihist1.GetCVHistoWithStatError()
    hist2 = ihist2.GetCVHistoWithStatError()
    hist1.SetDirectory(0)
    hist2.SetDirectory(0)
    setLogScale(logscale)

    xtitle = hist1.GetXaxis().GetTitle()
    ytitle = hist1.GetYaxis().GetTitle()
    title = "%s by %s: %s"%(xtitle, ytitle, label)

    hist1.GetXaxis().CenterTitle()
    hist1.GetYaxis().CenterTitle()
    hist1.SetTitle("%s"%title)

    gPad.SetLogy(False)
    gPad.SetLogx(False)
    if (logscale == 2 or logscale == 3): gPad.SetLogy()
    if (logscale == 1 or logscale == 3): gPad.SetLogx()
    t = TText(.3, .90, label)

    hist1.SetLineColor(1)
    hist1.Draw("BOX")
    t.SetNDC(1)
    t.SetTextSize(.03)
    plotname = "Title: %s_CV_%s"%( hist1.GetName(), label)
    t.Draw()
    hist2.SetLineColor(2)
    hist2.Draw("BOX SAME")
    hist1.Print()
    hist2.Print()
    cE.Print(cE.GetName(), plotname)
    resetLogScale()


def PlotCVAndError2D(cE, idatahist, imchist, label, cov_area = do_cov_area_norm, logscale = 0, binwid = True):
    setLogScale(logscale)
    d = MnvH2D()
    d = idatahist.Clone()
    d.SetDirectory(0)
    mc = MnvH2D()
    mc = imchist.Clone()
    d.SetDirectory(0)

    xaxis = mc.GetXaxis().GetTitle()
    yaxis = mc.GetYaxis().GetTitle()
    xtitle = "X Projection " + xaxis
    ytitle = "Y Projection " + yaxis
    xlabel = "_projx"
    ylabel = "_projy"
    t = TText(.3, .90, label)

    d_xhist = d.ProjectionX("%s%s"%( d.GetName(), xlabel), 0, -1, "o")
    d_xhist.GetXaxis().SetTitle("%s"%xtitle)
    d_yhist = d.ProjectionY("%s%s"%( d.GetName(), ylabel), 0, -1, "o")
    d_yhist.GetXaxis().SetTitle("%s"%ytitle)
    mc_xhist = mc.ProjectionX("%s%s"%( mc.GetName(), xlabel), 0, -1, "o")
    mc_xhist.GetXaxis().SetTitle("%s"%xtitle)
    mc_yhist = mc.ProjectionY("%s%s"%( mc.GetName(), ylabel), 0, -1, "o")
    mc_yhist.GetXaxis().SetTitle("%s"%ytitle)

    dlabel = d.GetTitle()
    mclabel = mc.GetTitle()
    Plot2D(cE, d, label, logscale, binwid)
    resetLogScale()
    Plot2D(cE, mc, label, logscale, binwid)
    resetLogScale()
    PlotCVAndError1D(cE, d_xhist, mc_xhist, label, False, logscale, binwid)
    resetLogScale()
    PlotCVAndError1D(cE, d_yhist, mc_yhist, label, False, logscale, binwid)
    resetLogScale()


# 1D
def integrator( h, binwid): 
    inte = 0
    for i in range(1,  h.GetXaxis().GetNbins()+1): 
        val = h.GetBinContent(i)
        wid = 1.0
        if binwid:
            wid =  h.GetBinWidth(i)  
        inte += val * wid
    
    # print("Integral of " , h.GetName() , " " , inte )
    return inte

# 2D
def integrator( h, binwid):
    inte = 0
    for ix in range(1,  h.GetXaxis().GetNbins()+1):
        for iy in range(1,  h.GetYaxis().GetNbins()+1):
            val = h.GetBinContent(ix, iy)
            xwid = 1.
            ywid = 1.
            if binwid:
                xwid = h.GetXaxis().GetBinWidth(ix)  
                ywid = h.GetYaxis().GetBinWidth(iy)  
            inte += val * xwid * ywid
        
    
    # print("Integral of " , h.GetName() , " " , inte )
    return inte


#endif
