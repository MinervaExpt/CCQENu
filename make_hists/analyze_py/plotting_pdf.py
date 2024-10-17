import os,sys
from ROOT import *
from PlotUtils import *
#ifndef plotting_functions_H
#define plotting_functions_H
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

xmin = 0.
xmax = 20.e3
nbins = 30

do_fractional_uncertainty = True
do_cov_area_norm = False
include_stat_error = True

do_fractional_uncertainty_str = do_fractional_uncertainty ? ("Frac") : ("Abs")
do_cov_area_norm_str = do_cov_area_norm ? ("CovAreaNorm") : ("POT")

void setLogScale(logscale) 
    gPad.SetLogy(False)
    gPad.SetLogx(False)
    if (logscale == 0): return
    if (logscale == 2 || logscale == 3): 
        gPad.SetLogy(True)
    
    if (logscale == 1 || logscale == 3): gPad.SetLogx(True):


void resetLogScale() 
    gPad.SetLogy(False)
    gPad.SetLogx(False)


void PlotErrorSummary(PlotUtils.MnvH1D hist, label)
void PlotErrorSummary(PlotUtils.MnvH2D hist, label:  print("no error bands for 2D" : 
void PlotVertBand(band, method_str, PlotUtils.MnvH1D hist)
void PlotLatBand(band, method_str, PlotUtils.MnvH1D hist)
void PlotVertUniverse(band, unsigned universe, method_str, PlotUtils.MnvH1D hist)
void PlotLatUniverse(band, unsigned universe, method_str, PlotUtils.MnvH1D hist)
void PlotCVAndError(PlotUtils.MnvH1D hist, label)
void PlotTotalError(PlotUtils.MnvH1D hist, method_str)
void Plot2D(PlotUtils.MnvH2D hist, label)
void PlotCVAndError(PlotUtils.MnvH2D hist, label)

integrator(PlotUtils.MnvH1D)
integrator(PlotUtils.MnvH2D)

void PlotTotalError(PlotUtils.MnvH1D hist, method_str) 
    TH1D* hTotalErr = (TH1D*)hist.GetTotalError(include_stat_error, do_fractional_uncertainty, do_cov_area_norm).Clone(Form("h_total_err_errSum_%d", __LINE__))
    hTotalErr.SetDirectory(0)
    TCanvas cF("c4", "c4")
    hTotalErr.SetTitle(Form("Total Uncertainty (%s) %s ", method_str, hist.GetTitle()))
    hTotalErr.Draw()
    cF.Print(Form("%s_TotalUncertainty_%s_%s_%s.png", hist.GetName(), do_fractional_uncertainty_str, do_cov_area_norm_str, method_str))


void PlotErrorSummary(TCanvas& cE, PlotUtils.MnvH2D hist, label, logscale:  print(" no error summary for 2D" : 

void PlotErrorSummary(TCanvas& cE, PlotUtils.MnvH1D hist, label, logscale) 
    PlotUtils.MnvPlotter mnvPlotter(PlotUtils.kCCQEAntiNuStyle)
    resetLogScale()
    # TCanvas cE ("c1","c1")
    #  hist.GetXaxis().SetTitle(hist.GetTitle())
    #  xaxis = mc.GetXaxis().GetTitle()
    # mnvPlotter.error_color_map.clear()

    mnvPlotter.axis_maximum = 0.2
    mnvPlotter.axis_minimum = 0.0
    mnvPlotter.error_color_map["Flux"] = kViolet + 6
    mnvPlotter.error_color_map["Recoil Reconstruction"] = kOrange + 2
    mnvPlotter.error_color_map["Cross Section Models"] = kMagenta
    mnvPlotter.error_color_map["FSI Model"] = kRed
    mnvPlotter.error_color_map["Muon Reconstruction"] = kGreen
    mnvPlotter.error_color_map["Muon Energy"] = kGreen + 3
    mnvPlotter.error_color_map["Muon_Energy_MINERvA"] = kRed - 3
    mnvPlotter.error_color_map["Muon_Energy_MINOS"] = kViolet - 3
    mnvPlotter.error_color_map["Other"] = kGreen + 3
    mnvPlotter.error_color_map["Low Recoil Fits"] = kRed + 3
    mnvPlotter.error_color_map["GEANT4"] = kBlue
    mnvPlotter.error_color_map["Background Subtraction"] = kGreen
    mnvPlotter.error_color_map["Tune"] = kOrange + 2

    mnvPlotter.error_summary_group_map.clear()
#ifndef NOGENIE
    # print(" include GENIE" )
    mnvPlotter.error_summary_group_map["FSI Model"].append("GENIE_FrAbs_N")
    mnvPlotter.error_summary_group_map["FSI Model"].append("GENIE_FrAbs_pi")
    mnvPlotter.error_summary_group_map["FSI Model"].append("GENIE_FrCEx_N")
    mnvPlotter.error_summary_group_map["FSI Model"].append("GENIE_FrCEx_pi")
    mnvPlotter.error_summary_group_map["FSI Model"].append("GENIE_FrElas_N")
    mnvPlotter.error_summary_group_map["FSI Model"].append("GENIE_FrElas_pi")
    mnvPlotter.error_summary_group_map["FSI Model"].append("GENIE_FrInel_N")
    mnvPlotter.error_summary_group_map["FSI Model"].append("GENIE_FrInel_pi")
    mnvPlotter.error_summary_group_map["FSI Model"].append("GENIE_FrPiProd_N")
    mnvPlotter.error_summary_group_map["FSI Model"].append("GENIE_FrPiProd_pi")
    mnvPlotter.error_summary_group_map["FSI Model"].append("GENIE_MFP_N")
    mnvPlotter.error_summary_group_map["FSI Model"].append("GENIE_MFP_pi")
    #
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_AGKYxF1pi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_AhtBY")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_BhtBY")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_CCQEPauliSupViaKF")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_CV1uBY")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_CV2uBY")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_EtaNCEL")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_MaCCQE")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_MaCCQEshape")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_MaNCEL")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_MaRES")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_MvRES")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_NormCCQE")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_NormCCRES")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_NormDISCC")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_NormNCRES")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_RDecBR1gamma")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_Rvn1pi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_Rvn2pi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_Rvn3pi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_Rvp1pi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_Rvp2pi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_Theta_Delta2Npi")
    mnvPlotter.error_summary_group_map["Genie Interaction Model"].append("GENIE_VecFFCCQEshape")
#endif
    mnvPlotter.error_summary_group_map["Tune"].append("RPA_LowQ2")
    mnvPlotter.error_summary_group_map["Tune"].append("RPA_HighQ2")
    mnvPlotter.error_summary_group_map["Tune"].append("NonResPi")
    mnvPlotter.error_summary_group_map["Tune"].append("2p2h")
    mnvPlotter.error_summary_group_map["Tune"].append("LowQ2Pi")
    mnvPlotter.error_summary_group_map["Tune"].append("Low_Recoil_2p2h_Tune")

    # mnvPlotter.error_summary_group_map["Angle"].append("BeamAngleX")
    #   mnvPlotter.error_summary_group_map["Angle"].append("BeamAngleY")

    mnvPlotter.error_summary_group_map["Response"].append("response_em")
    mnvPlotter.error_summary_group_map["Response"].append("response_proton")
    mnvPlotter.error_summary_group_map["Response"].append("response_pion")
    mnvPlotter.error_summary_group_map["Response"].append("response_meson")
    mnvPlotter.error_summary_group_map["Response"].append("response_other")
    mnvPlotter.error_summary_group_map["Response"].append("response_low_neutron")
    mnvPlotter.error_summary_group_map["Response"].append("response_mid_neutron")
    mnvPlotter.error_summary_group_map["Response"].append("response_high_neutron")

    mnvPlotter.error_summary_group_map["Geant"].append("GEANT_Neutron")
    mnvPlotter.error_summary_group_map["Geant"].append("GEANT_Proton")
    mnvPlotter.error_summary_group_map["Geant"].append("GEANT_Pion")
    #
    mnvPlotter.error_summary_group_map["Muon Energy"].append("Muon_Energy_MINOS")
    mnvPlotter.error_summary_group_map["Muon Energy"].append("Muon_Energy_MINERvA")
    mnvPlotter.error_summary_group_map["Muon Energy"].append("MINOS_Reconstruction_Efficiency")
    mnvPlotter.error_summary_group_map["Muon Energy"].append("Muon_Energy_Resolution")
    mnvPlotter.error_summary_group_map["Muon Energy"].append("BeamAngleX")
    mnvPlotter.error_summary_group_map["Muon Energy"].append("BeamAngleY")
    #  mnvPlotter.error_summary_group_map["Unfolding"].append("Unfolding")

    mnvPlotter.DrawErrorSummary(hist, "TR", include_stat_error, False, 0.0, do_cov_area_norm, "", do_fractional_uncertainty)

    plotname = Form("Title: ErrorSummary_%s_%s_%s", hist.GetName(), do_cov_area_norm_str, label)
    TText* t = new TText(.3, .95, label)
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
#ifdef FULLDUMP
    for group in mnvPlotter.error_summary_group_map: 
        # print(" error summary for " , group.first :
        mnvPlotter.DrawErrorSummary(hist, "TR", include_stat_error, False, 0.0, do_cov_area_norm, group.first, do_fractional_uncertainty)
        plotname = Form("Title: ErrorSummary_%s_%s_%s_%s", hist.GetName(), group.first, do_cov_area_norm_str, label)
        TText* t = new TText(.3, .95, label)
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


void PlotVertBand(band, method_str, PlotUtils.MnvH1D hist) 
    TH1* h1 = (TH1*)hist.GetVertErrorBand(band).GetErrorBand(do_fractional_uncertainty, do_cov_area_norm).Clone(Form("%s_%s_%s", hist.GetName(), band, method_str))

    if (h1 == NULL): 
        print(" no error band " , band )
    
    h1.SetDirectory(0)
    # TH1* h1 = (TH1*)hist.GetVertErrorBand(band)
    TCanvas cF("c4", "c4")
    h1.SetTitle(Form("%s Uncertainty (%s) Theta_#nu (rad)", band, method_str))
    h1.Draw("h")
    cF.Print(Form("%s_%s_band_%s.png", hist.GetName(), band, method_str))


void PlotLatBand(band, method_str, PlotUtils.MnvH1D hist) 
    TH1* h1 = (TH1*)hist.GetLatErrorBand(band).GetErrorBand(do_fractional_uncertainty, do_cov_area_norm).Clone(Form("%s_%s_%s", hist.GetName(), band, method_str))
    h1.SetDirectory(0)
    # TH1* h1 = (TH1*)hist.GetLatErrorBand(band)
    TCanvas cF("c1", "c1")
    h1.SetTitle(Form("%s Uncertainty (%s) E_#nu (MeV)", band, method_str))
    h1.Draw("h")
    cF.Print(Form("%s_%s_band_%s.png", hist.GetName(), band, method_str))


void PlotVertUniverse(band, unsigned universe, method_str, PlotUtils.MnvH1D hist) 
    # print("band " , band , " " , hist.GetName() )
    TH1D* h1 = hist.GetVertErrorBand(band).GetHist(universe)
    h1.SetDirectory(0)
    TCanvas cF("c1", "c1")
    h1.SetLineColor(kBlack)
    h1.SetLineStyle(1)
    h1.Draw("hist")
    cF.Print(Form("%s_%s_band_universe%i_%s.png", hist.GetName(), band, universe + 1, method_str))


void PlotLatUniverse(band, unsigned universe, method_str, PlotUtils.MnvH1D hist) 
    TH1D* h1 = hist.GetLatErrorBand(band).GetHist(universe)
    h1.SetDirectory(0)
    TCanvas cF("c1", "c1")
    h1.SetLineColor(kBlack)
    h1.SetLineStyle(1)
    h1.Draw("hist")
    cF.Print(Form("%s_%s_band_universe%i_%s.png", hist.GetName(), band, universe + 1, method_str))


void PlotCVAndError(TCanvas& cE, PlotUtils.MnvH1D idatahist, PlotUtils.MnvH1D ihist, label, cov_area = do_cov_area_norm, logscale = 0, binwid = True) 
    resetLogScale()
    # PlotUtils.MnvPlotter mnvPlotter(PlotUtils.kCCQEAntiNuStyle)
    PlotUtils.MnvPlotter mnvPlotter(PlotUtils.kDefaultStyle)
    # mnvPlotter.SetBinWidthNorm(False)
    mnvPlotter.draw_normalized_to_bin_width = 0
    # binwid = True
    #  need to clone as plan to bin width correct
    if (not ihist || not idatahist): 
        print(" No datahist " , ihist , " or mchist " , ihist , " " , label )
        return
    
    MnvH1D datahist = idatahist.Clone()
    datahist.SetDirectory(0)
    MnvH1D hist = ihist.Clone()
    hist.SetDirectory(0)
    # TCanvas cE ("c1","c1")
    # hist.GetXaxis().SetTitle(Form("%s",hist.GetTitle() ))
    hist.GetXaxis().GetTitle()
    hist.GetYaxis().SetTitle(Form("%s", "Counts per unit"))
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
    
    PlotUtils.MnvH1D bkgdHist = NULL
    PlotUtils.MnvH1D dataBkgdHist = NULL
    # datahist.Print("ALL")
    #  gPad.SetLogy(False)
    #  gPad.SetLogx(False)
    #  if (logscale== 2 || logscale ==3): 
    #    gPad.SetLogy()
    #  
    #  if (logscale== 1 || logscale ==3): gPad.SetLogx():
    setLogScale(logscale)
    cov_area = False
    TText* t = new TText(.3, .95, label)
    t.SetNDC(1)
    t.SetTextSize(.03)

    # print(label , " BinWidthNorm before" , datahist.GetNormBinWidth(: :
    # datahist.SetNormBinWidth(1.0)
    # hist.SetNormBinWidth(1)
    # mnvPlotter.SetBinWidthNorm(not binwid)
    # print(label , " BinWidthNorm after" , datahist.GetNormBinWidth() )
    mnvPlotter.SetROOT6Palette(57)  # kBird

    mnvPlotter.DrawDataMCWithErrorBand(datahist, hist, mcScale, "TL", useHistTitles, NULL, NULL, cov_area, statPlusSys)
    TH1D stat = datahist.GetCVHistoWithStatError()
    stat.SetLineColor(kBlack)
    stat.SetMarkerColor(kBlack)
    stat.Draw("E1 same")
    # mnvPlotter.DrawMCWithErrorBand(hist) #I think that this call only shows stat errors.
    plotname = Form("Title: %s_CV_w_err_%s", datahist.GetName(), label)
    t.Draw()
    cE.Print(cE.GetName(), plotname)
    if (idatahist not = ihist.      # don't plot ratio for identical hists.
        MnvH1D d = (MnvH1D)datahist.Clone()
        d.SetDirectory(0)
        MnvH1D m = (MnvH1D)hist.Clone()
        m.SetDirectory(0)
        if (d.GetXaxis():.GetNbins(): not = m.GetXaxis():.GetNbins():): 
            print(" data and mc bins don't agree" , d.GetName() , m.GetName() )
            return
        
    
        MnvH1D mc = (MnvH1D)m.Clone()
        mc.SetDirectory(0)
        mc.ClearAllErrorBands()
        mc.AddMissingErrorBandsAndFillWithCV(*m)

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
        plotname2 = Form("Title: ratio %s_CV_w_err_%s", datahist.GetName(), label)

        cE.Print(cE.GetName(), plotname2)
    
    resetLogScale()
    # mnvPlotter.MultiPrint(&cE, plotname, "pdf")
    #  mnvPlotter.MultiPrint(&cE, plotname, "C")


void Plot2D(TCanvas& cE, MnvH2D ihist, label, logscale = 0, binwid = True) 
    setLogScale(logscale)
    MnvH2D hist = (MnvH2D)ihist.Clone()
    hist.SetDirectory(0)
    setLogScale(logscale)

    xtitle = hist.GetXaxis().GetTitle()
    ytitle = hist.GetYaxis().GetTitle()
    title = Form("%s by %s: %s", xtitle, ytitle, label)

    hist.GetXaxis().CenterTitle()
    hist.GetYaxis().CenterTitle()
    hist.SetTitle(Form("%s", title))

    #  gPad.SetLogy(False)
    #  gPad.SetLogx(False)
    #  if (logscale == 2 || logscale == 3): gPad.SetLogy():
    #  if (logscale == 1 || logscale == 3): gPad.SetLogx():
    TText* t = new TText(.3, .95, label)
    hist.Draw("COLZ")
    t.SetNDC(1)
    t.SetTextSize(.03)
    plotname = Form("Title: %s_CV_%s", hist.GetName(), label)
    t.Draw()

    cE.Print(cE.GetName(), plotname)
    resetLogScale()


void Plot2DFraction(TCanvas& cE, MnvH1D ihist1, MnvH1D ihist2, label, logscale = 0, binwid = False:   # null version for 1d


void Plot2DFraction(TCanvas& cE, MnvH2D ihist1, MnvH2D ihist2, label, logscale = 0, binwid = False) 
    print("pr2D fraction" , ihist1.GetName() )
    setLogScale(logscale)
    TH2D hist1 = ihist1.GetCVHistoWithStatError()
    TH2D hist2 = ihist2.GetCVHistoWithStatError()
    hist1.SetDirectory(0)
    hist2.SetDirectory(0)
    setLogScale(logscale)

    xtitle = hist1.GetXaxis().GetTitle()
    ytitle = hist1.GetYaxis().GetTitle()
    title = Form("%s by %s: %s", xtitle, ytitle, label)

    hist1.GetXaxis().CenterTitle()
    hist1.GetYaxis().CenterTitle()
    hist1.SetTitle(Form("%s", title))

    gPad.SetLogy(False)
    gPad.SetLogx(False)
    if (logscale == 2 || logscale == 3): gPad.SetLogy():
    if (logscale == 1 || logscale == 3): gPad.SetLogx():
    TText* t = new TText(.3, .90, label)

    hist1.SetLineColor(1)
    hist1.Draw("BOX")
    t.SetNDC(1)
    t.SetTextSize(.03)
    plotname = Form("Title: %s_CV_%s", hist1.GetName(), label)
    t.Draw()
    hist2.SetLineColor(2)
    hist2.Draw("BOX SAME")
    hist1.Print()
    hist2.Print()
    cE.Print(cE.GetName(), plotname)
    resetLogScale()


void PlotCVAndError(TCanvas& cE, MnvH2D idatahist, MnvH2D imchist, label, cov_area = do_cov_area_norm, logscale = 0, binwid = True) 
    setLogScale(logscale)

    MnvH2D d = (MnvH2D)idatahist.Clone()
    d.SetDirectory(0)
    MnvH2D mc = (MnvH2D)imchist.Clone()
    d.SetDirectory(0)

    xaxis = mc.GetXaxis().GetTitle()
    yaxis = mc.GetYaxis().GetTitle()
    xtitle = "X Projection " + xaxis
    ytitle = "Y Projection " + yaxis
    xlabel = "_projx"
    ylabel = "_projy"
    TText* t = new TText(.3, .90, label)

    MnvH1D d_xhist = d.ProjectionX(Form("%s%s", d.GetName(), xlabel), 0, -1, "o")
    d_xhist.GetXaxis().SetTitle(Form("%s", xtitle))
    MnvH1D d_yhist = d.ProjectionY(Form("%s%s", d.GetName(), ylabel), 0, -1, "o")
    d_yhist.GetXaxis().SetTitle(Form("%s", ytitle))
    MnvH1D mc_xhist = mc.ProjectionX(Form("%s%s", mc.GetName(), xlabel), 0, -1, "o")
    mc_xhist.GetXaxis().SetTitle(Form("%s", xtitle))
    MnvH1D mc_yhist = mc.ProjectionY(Form("%s%s", mc.GetName(), ylabel), 0, -1, "o")
    mc_yhist.GetXaxis().SetTitle(Form("%s", ytitle))

    dlabel = d.GetTitle()
    mclabel = mc.GetTitle()
    Plot2D(cE, d, label, logscale, binwid)
    resetLogScale()
    Plot2D(cE, mc, label, logscale, binwid)
    resetLogScale()
    PlotCVAndError(cE, d_xhist, mc_xhist, label, False, logscale, binwid)
    resetLogScale()
    PlotCVAndError(cE, d_yhist, mc_yhist, label, False, logscale, binwid)
    resetLogScale()


# 1D
integrator(PlotUtils.MnvH1D h, binwid) 
    inte = 0
    fori = 1 i <= h.GetXaxis(:.GetNbins(: i++: 
        val = h.GetBinContent(i)
        wid = binwid ? h.GetBinWidth(i) : 1.0
        inte += val * wid
    
    # print("Integral of " , h.GetName() , " " , inte )
    return inte

# 2D
integrator(PlotUtils.MnvH2D h, binwid) 
    inte = 0
    forix = 1 ix <= h.GetXaxis(:.GetNbins(: ix++: 
        foriy = 1 iy <= h.GetYaxis(:.GetNbins(: iy++: 
            val = h.GetBinContent(ix, iy)
            xwid = binwid ? h.GetXaxis().GetBinWidth(ix) : 1.0
            ywid = binwid ? h.GetYaxis().GetBinWidth(iy) : 1.0
            inte += val * xwid * ywid
        
    
    # print("Integral of " , h.GetName() , " " , inte )
    return inte


#endif
