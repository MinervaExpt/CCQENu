import os,sys
import ROOT
from ROOT import TH1D, gPad, TCanvas, TText, gStyle
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter
#ifndef plotting_functions_H
#define plotting_functions_H
FULLDUMP=False
PDFALL=False
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

kCompactStyle     = 1 #!< Same as the default style but with less whitespace


class PDFPlotter:

    kDefaultStyle     = 0 #!< The Default style
    #kCompactStyle     = 1 #!< Same as the default style but with less whitespace
    kNukeCCStyle      = 2 #!< Similar to compact but with NukeCC-specifics
    kNukeCCPrintStyle = 3 
    kCCNuPionIncStyle = 4 #!< compact with CCNuPionInc color scheme
    kCCCohStyle       = 5 #!< Coherent rocks!!!
    kCCQENuStyle      = 6

    xmin = 0.
    xmax = 20.e3
    nbins = 30

    def __init__(self, theconfig, pdffilename):
        self.pdfname = pdffilename
        self.filename = pdffilename.replace(".pdf","")
        self.canvas1D = TCanvas(pdffilename)
        self.canvas1D.SetLeftMargin(0.15)
        self.canvas1D.SetRightMargin(0.15)
        self.canvas1D.SetBottomMargin(0.15)
        self.canvas1D.SetTopMargin(0.10)
        self.canvas1D.Print(pdffilename+"(", "pdf")
        self.logx=0
        self.scales=theconfig["Scales"]
        self.PDFALL=True
        if "PDFALL" in theconfig:
            self.PDFALL = theconfig["PDFALL"]

        self.Formats=["png","C","pdf"]
        if "Formats" in theconfig:
            self.Formats=theconfig["Formats"]
        
        self.FULLDUMP=False
        
        
        # defaults 
        self.do_fractional_uncertainty_str = True
        self.do_cov_area_norm = False
        self.include_stat_error = True
        if "AreaNorm" in theconfig:
            self.do_cov_area_norm = theconfig["AreaNorm"]
        if "FractionalUncertainty" in theconfig:
            self.do_fractional_uncertainty_str = theconfig["FractionalUncertainty"]
        if self.do_fractional_uncertainty_str: 
            self.do_fractional_uncertainty = "Frac"
        if self.do_fractional_uncertainty_str: 
            self.do_fractional_uncertainty = "Abs"
        
        #do_fractional_uncertainty_str = do_fractional_uncertainty ? ("Frac") : ("Abs")
        #self.do_cov_area_norm_str = (self.do_cov_area_norm == "CovAreaNorm")

    def close(self):
        ''' method to close a pdf file '''
        if self.PDFALL: 
            self.canvas1D.Print(self.pdfname+")", "pdf")
        pass

    def SetFormats(self,formats=["pdf"]):
        self.Formats = format
    def SetDebug(self,debug=False):
        self.DEBUG = debug
    def SetFullDump(self,dump=False):
        self.FULLDUMP = dump
    
    # def SetDoFractionalUncertainty(self,fractional_uncertainty_s):
    #     if self.do_fractional_uncertainty == "Frac":
    #         self.do_fractional_uncertainty_str = True
    #     if self.do_fractional_uncertainty == "Abs":
    #         self.do_fractional_uncertainty_str = False

    def smallest_nonzero_bin(self,hist):
        minbin = 1.e9
        for i in range(1, hist.GetNbinsX() + 1):
            if (hist.GetBinContent(i) > 0 and hist.GetBinContent(i) < minbin): 
                minbin = hist.GetBinContent(i)
        
        return minbin

    def setLogScale(self,logscale):
        gPad.SetLogy(False)
        gPad.SetLogx(False)
        if (logscale == 0): return
        if (logscale == 2 or logscale == 3): 
            gPad.SetLogy(True)
        
        if (logscale == 1 or logscale == 3): 
            gPad.SetLogx(True)


    def resetLogScale(self):
        gPad.SetLogy(False)
        gPad.SetLogx(False)

    def resetLogScaleY(self):
        gPad.SetLogy(False)
        


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

    def PlotTotalError(self,hist, method_str): 
        if hist.InheritsFrom("TH2D"):
            print("no error bands for 2D")
            return
        
        hTotalErr = TH1D()
        hTotalErr = hist.GetTotalError(self.include_stat_error, self.do_fractional_uncertainty,self.do_cov_area_norm).Clone("h_total_err_errSum_%d"%(0))
        hTotalErr.SetDirectory(0)
        cF = TCanvas("c4", "c4")
        hTotalErr.SetTitle("Total Uncertainty (%s) %s "%(method_str, hist.GetTitle()))
        hTotalErr.Draw()
        cF.Print("%s_TotalUncertainty_%s_%s_%s.png"%(hist.GetName(), self.do_fractional_uncertainty_str, self.do_cov_area_norm_str, method_str))


    # def PlotErrorSummary(cE, hist, label, logscale:  
    #                      print(" no error summary for 2D" : 

    def PlotErrorSummary(self,cE, hist, label, logscale):
        self.mnvPlotter = MnvPlotter(kCompactStyle)#PlotUtils.kCCQEAntiNuStyle)
        self.resetLogScale()
        # TCanvas cE ("c1","c1")
        #  hist.GetXaxis().SetTitle(hist.GetTitle())
        #  xaxis = mc.GetXaxis().GetTitle()
        # mnvPlotter.error_color_map.clear()

        self.mnvPlotter.axis_maximum = 0.2
        self.mnvPlotter.axis_minimum = 0.0
        self.mnvPlotter.error_color_map["Flux"] = ROOT.kViolet + 6
        self.mnvPlotter.error_color_map["Recoil Reconstruction"] = ROOT.kOrange + 2
        self.mnvPlotter.error_color_map["Cross Section Models"] = ROOT.kMagenta
        self.mnvPlotter.error_color_map["FSI Model"] = ROOT.kRed
        self.mnvPlotter.error_color_map["Muon Reconstruction"] = ROOT.kGreen
        self.mnvPlotter.error_color_map["Muon Energy"] = ROOT.kGreen + 3
        self.mnvPlotter.error_color_map["Muon_Energy_MINERvA"] = ROOT.kRed - 3
        self.mnvPlotter.error_color_map["Muon_Energy_MINOS"] = ROOT.kViolet - 3
        self.mnvPlotter.error_color_map["Other"] = ROOT.kGreen + 3
        self.mnvPlotter.error_color_map["Low Recoil Fits"] = ROOT.kRed + 3
        self.mnvPlotter.error_color_map["GEANT4"] = ROOT.kBlue
        self.mnvPlotter.error_color_map["Background Subtraction"] = ROOT.kGreen
        self.mnvPlotter.error_color_map["Tune"] = ROOT.kOrange + 2

        self.mnvPlotter.error_summary_group_map.clear()
    #ifndef NOGENIE
        # print(" include GENIE" )
        print ("summary_map",self.mnvPlotter.error_summary_group_map["FSI Model"])
        self.mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrAbs_N")
        self.mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrAbs_pi")
        self.mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrCEx_N")
        self.mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrCEx_pi")
        self.mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrElas_N")
        self.mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrElas_pi")
        self.mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrInel_N")
        self.mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrInel_pi")
        self.mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrPiProd_N")
        self.mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrPiProd_pi")
        self.mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_MFP_N")
        self.mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_MFP_pi")
        #
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_AGKYxF1pi")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_AhtBY")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_BhtBY")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_CCQEPauliSupViaKF")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_CV1uBY")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_CV2uBY")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_EtaNCEL")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Mab")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaCCQEshape")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaNCEL")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaRES")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MvRES")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormCCQE")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormCCRES")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormDISCC")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormNCRES")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_RDecBR1gamma")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvn1pi")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvn2pi")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvn3pi")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvp1pi")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvp2pi")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Theta_Delta2Npi")
        self.mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_VecFFCCQEshape")
    #endif
        self.mnvPlotter.error_summary_group_map["Tune"].push_back("RPA_LowQ2")
        self.mnvPlotter.error_summary_group_map["Tune"].push_back("RPA_HighQ2")
        self.mnvPlotter.error_summary_group_map["Tune"].push_back("NonResPi")
        self.mnvPlotter.error_summary_group_map["Tune"].push_back("2p2h")
        self.mnvPlotter.error_summary_group_map["Tune"].push_back("LowQ2Pi")
        self.mnvPlotter.error_summary_group_map["Tune"].push_back("Low_Recoil_2p2h_Tune")

        # mnvPlotter.error_summary_group_map["Angle"].push_back("BeamAngleX")
        #   mnvPlotter.error_summary_group_map["Angle"].push_back("BeamAngleY")

        self.mnvPlotter.error_summary_group_map["Response"].push_back("response_em")
        self.mnvPlotter.error_summary_group_map["Response"].push_back("response_proton")
        self.mnvPlotter.error_summary_group_map["Response"].push_back("response_pion")
        self.mnvPlotter.error_summary_group_map["Response"].push_back("response_meson")
        self.mnvPlotter.error_summary_group_map["Response"].push_back("response_other")
        self.mnvPlotter.error_summary_group_map["Response"].push_back("response_low_neutron")
        self.mnvPlotter.error_summary_group_map["Response"].push_back("response_mid_neutron")
        self.mnvPlotter.error_summary_group_map["Response"].push_back("response_high_neutron")

        self.mnvPlotter.error_summary_group_map["Geant"].push_back("GEANT_Neutron")
        self.mnvPlotter.error_summary_group_map["Geant"].push_back("GEANT_Proton")
        self.mnvPlotter.error_summary_group_map["Geant"].push_back("GEANT_Pion")
        #
        self.mnvPlotter.error_summary_group_map["Muon Energy"].push_back("Muon_Energy_MINOS")
        self.mnvPlotter.error_summary_group_map["Muon Energy"].push_back("Muon_Energy_MINERvA")
        self.mnvPlotter.error_summary_group_map["Muon Energy"].push_back("MINOS_Reconstruction_Efficiency")
        self.mnvPlotter.error_summary_group_map["Muon Energy"].push_back("Muon_Energy_Resolution")
        self.mnvPlotter.error_summary_group_map["Muon Energy"].push_back("BeamAngleX")
        self.mnvPlotter.error_summary_group_map["Muon Energy"].push_back("BeamAngleY")
        #  mnvPlotter.error_summary_group_map["Unfolding"].push_back("Unfolding")

        self.mnvPlotter.DrawErrorSummary(hist, "TR", self.include_stat_error, False, 0.0, self.do_cov_area_norm, "", self.do_fractional_uncertainty_str)

        plotname = "Title: ErrorSummary_%s_%s_%s"% (hist.GetName(), self.do_cov_area_norm, label)
        t = TText()
        t = TText(.3, .95, label)
        t.SetNDC(1)
        t.SetTextSize(.03)
        


        self.setLogScale(logscale)
        #  gPad.SetLogy(False)
        #  gPad.SetLogx(False)
        #  if (logscale== 2 || logscale ==3):
        #    gPad.SetLogy()
        #    hist.SetMinimum(0.001)
        #  
        #  if (logscale== 1 || logscale ==3): gPad.SetLogx():
        t.Draw()
        #cE.Print(cE.GetName(), plotname)
        if self.PDFALL: 
            cE.Print(cE.GetName(), plotname)
        else:
            for format in self.Formats:
                alternate = format+"/"+self.filename+"_"+hist.GetName()+"."+format
                cE.SetName(alternate)
            #print ("alternate",alternate)  
                cE.Print(alternate)
        self.resetLogScale()
        if self.FULLDUMP:
            for group in self.mnvPlotter.error_summary_group_map: 
                # print(" error summary for " , group.first :
                self.mnvPlotter.DrawErrorSummary(hist, "TR", self.include_stat_error, False, 0.0, self.do_cov_area_norm, group.first, self.do_fractional_uncertainty)
                plotname = "Title: ErrorSummary_%s_%s_%s_%s"%(hist.GetName(), group.first, self.do_cov_area_norm_str, label)
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
                if self.PDFALL:
                    cE.Print(cE.GetName(), plotname)
                else:
                    for format in self.Formats:
                        alternate = format+"/"+self.filename+"_"+hist.GetName()+"."+format
                        #alternate = format+"/"+hist.GetName()+"."+format
                        cE.SetName(alternate) 
                        cE.Print(alternate)

                self.resetLogScale()
        
    #endif

        # mnvPlotter.MultiPrint(&cE, plotname, "pdf")
        #   mnvPlotter.DrawErrorSummary(hist,"TR",include_stat_error,True,0.0, do_cov_area_norm, "Angle",False)
        #   plotname = Form("ResponseErrorSummary_%s_%s_%s", hist.GetName(),do_cov_area_norm_str,label)
        #   mnvPlotter.MultiPrint(&cE, plotname, "png")


    def PlotVertBand(self, band, method_str, hist):
        h1 = TH1D()
        h1 = hist.GetVertErrorBand(band).GetErrorBand(do_fractional_uncertainty, self.do_cov_area_norm).Clone("%s_%s_%s"%(hist.GetName(), band, method_str))

        if (h1 == 0): 
            print(" no error band " , band )
        
        h1.SetDirectory(0)
        # TH1* h1 = (TH1*)hist.GetVertErrorBand(band)
        cF = TCanvas("c4", "c4")
        h1.SetTitle("%s Uncertainty (%s) Theta_#nu (rad)"%( band, method_str))
        h1.Draw("h")
        cF.Print("%s_%s_band_%s.png"%( hist.GetName(), band, method_str))


    def PlotLatBand(self, band, method_str,  hist) :
        h1 = TH1D()
        h1 = hist.GetLatErrorBand(band).GetErrorBand(self.do_fractional_uncertainty, self.do_cov_area_norm).Clone("%s_%s_%s"%( hist.GetName(), band, method_str))
        h1.SetDirectory(0)
        # TH1* h1 = (TH1*)hist.GetLatErrorBand(band)
        cF = TCanvas("c1", "c1")
        h1.SetTitle("%s Uncertainty (%s) E_#nu (MeV)"%( band, method_str))
        h1.Draw("h")
        cF.Print("%s_%s_band_%s.png"%( hist.GetName(), band, method_str))


    def PlotVertUniverse(self, band, universe, method_str, hist): 
        # print("band " , band , " " , hist.GetName() )
        h1 = hist.GetVertErrorBand(band).GetHist(universe)
        h1.SetDirectory(0)
        cF = TCanvas("c1", "c1")
        h1.SetLineColor(ROOT.kBlack)
        h1.SetLineStyle(1)
        h1.Draw("hist")
        cF.Print("%s_%s_band_universe%i_%s.png"%( hist.GetName(), band, universe + 1, method_str))


    def PlotLatUniverse(self, band,universe, method_str,  hist): 
        h1 = hist.GetLatErrorBand(band).GetHist(universe)
        h1.SetDirectory(0)
        cF = TCanvas("c1", "c1")
        h1.SetLineColor(ROOT.kBlack)
        h1.SetLineStyle(1)
        h1.Draw("hist")
        cF.Print("%s_%s_band_universe%i_%s.png"%( hist.GetName(), band, universe + 1, method_str))


    def PlotCVAndError(self, cE, idatahist,  ihist, label, cov_area, logscale = 0, binwid = True):
        cov_area = self.do_cov_area_norm
        if idatahist.InheritsFrom("TH2D"):
            self.PlotCVAndError2D(cE, idatahist,  ihist, label, cov_area, logscale, binwid)
        else:
            self.PlotCVAndError1D(cE, idatahist,  ihist, label, cov_area, logscale, binwid)



    def PlotCVAndError1D(self, cE, idatahist,  ihist, label, cov_area , logscale = 0, binwid = True):
        cov_area = self.do_cov_area_norm
        self.resetLogScale()
        # PlotUtils.MnvPlotter mnvPlotter(PlotUtils.kCCQEAntiNuStyle)
        self.mnvPlotter = MnvPlotter()
        # self.mnvPlotter.SetBinWidthNorm(False)
        self.mnvPlotter.draw_normalized_to_bin_width = 0
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
        # if logscale > 1: 
        #     minbin = smallest_nonzero_bin(datahist)
        #     datahist.SetMinimum(minbin * 0.5)
        #     for ybin in range(1, datahist.GetNbinsX() + 1):
        #         if (datahist.GetBinContent(ybin) < minbin): 
        #             datahist.SetBinContent(ybin, minbin)
        #     hist.SetMinimum(minbin * 0.5)
        #     print ("reset minimum to", minbin * 0.5, " for ", datahist.GetName(),logscale)
        # hist.Print("ALL")
        # datahist.Print("ALL")
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
        self.setLogScale(logscale)
        cov_area = False
        t = TText(.3, .95, label)
        t.SetNDC(1)
        t.SetTextSize(.03)

        # print(label , " BinWidthNorm before" , datahist.GetNormBinWidth(: :
        # datahist.SetNormBinWidth(1.0)
        # hist.SetNormBinWidth(1)
        # mnvPlotter.SetBinWidthNorm(not binwid)
        # print(label , " BinWidthNorm after" , datahist.GetNormBinWidth() )
        self.mnvPlotter.SetROOT6Palette(57)  # kBird
        # if (logscale > 1):
        #     print ("set minimum to non-0 for log scale" , datahist.GetName() )
        #     gStyle.SetHistMinimumZero(False)
        print ("datahist minimum",type(datahist), datahist.GetMinimum())
        
        self.mnvPlotter.DrawDataMCWithErrorBand(datahist, hist, mcScale, "TL", useHistTitles, 0, 0, cov_area, statPlusSys)
        #gPad.BuildLegend()
        stat = TH1D()
        stat = datahist.GetCVHistoWithStatError()
        
        stat.SetLineColor(ROOT.kBlack)
        stat.SetMarkerColor(ROOT.kBlack)
        stat.Draw("E1 same")
        # mnvPlotter.DrawMCWithErrorBand(hist) #I think that this call only shows stat errors.
        plotname = "Title: %s_CV_w_err_%s"%( datahist.GetName(), label)
        t.Draw()
        if self.PDFALL:
            cE.Print(cE.GetName(), plotname)
        else:
            for format in self.Formats:
                alternate = format+"/"+self.filename+"_"+hist.GetName()+"."+format
                #alternate = format+"/"+hist.GetName()+"."+format
                cE.SetName(alternate) 
                cE.Print(alternate)
        logsave = logscale
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
            cE.SetLogy(False)
            # no idea why I should have to do this
            # m.Print("ALL")
            # datahist.Draw()
            cov_area = False
            # mnvPlotter.SetBinWidthNorm(False)
            if d.GetMaximum() > 5 : d.SetMaximum(5.0)
            if d.GetMinimum() < 0.0: d.SetMinimum(0.0)
            if m.GetMaximum() > 5 : m.SetMaximum(5.0)
            if m.GetMinimum() < 0.0: m.SetMinimum(0.0)
            self.mnvPlotter.DrawDataMCRatio(d, m, mcScale, True, True)  # "TL", useHistTitles, NULL, NULL,cov_area, statPlusSys)

            t.Draw()
            plotname2 = "Title: ratio %s_CV_w_err_%s"%( datahist.GetName(), label)

            #cE.Print(cE.GetName(), plotname2)
            if self.PDFALL: 
                    cE.Print(cE.GetName(), plotname2)
            else:
                for format in self.Formats:
                    alternate = format+"/"+self.filename+"_"+hist.GetName()+"_ratio."+format
                    #alternate = format+"/ratio"+hist.GetName()+"."+format
                    cE.SetName(alternate) 
                    cE.Print(alternate)
        
        self.resetLogScale()
        # mnvPlotter.MultiPrint(&cE, plotname, "pdf")
        #  mnvPlotter.MultiPrint(&cE, plotname, "C")


    def Plot2D(self,cE, ihist, label, logscale = 0, binwid = True): 
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

        #cE.Print(self,cE.GetName(), plotname)
        if self.PDFALL: 
                cE.Print(cE.GetName(), plotname)
        else:
            for format in self.Formats:
                alternate = format+"/"+self.filename+"_"+hist.GetName()+"."+format
                #alternate = format+"/"+hist.GetName()+"."+format
                cE.SetName(alternate) 
                cE.Print(alternate)
        resetLogScale()


    # def Plot2DFraction(cE, MnvH1D ihist1, ihist2, label, logscale = 0, binwid = False):   # null version for 1d


    def Plot2DFraction(self, cE, ihist1,  ihist2, label, logscale = 0, binwid = False):
        
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
        #cE.Print(cE.GetName(), plotname)
        if self.PDFALL: 
            cE.Print(cE.GetName(), plotname)
        else:
            for format in self.Formats:
                alternate = format+"/"+self.filename+"_"+hist.GetName()+"."+format
                #alternate = format+"/"+hist.GetName()+"."+format
                cE.SetName(alternate) 
                cE.Print(alternate)
        resetLogScale()


    def PlotCVAndError2D(self, cE, idatahist, imchist, label, cov_area, logscale = 0, binwid = True):
        
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
    def integrator(self, h, binwid): 
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
    def integrator2D(self, h, binwid):
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
