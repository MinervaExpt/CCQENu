#ifndef plotting_functions_H
#define plotting_functions_H
#define FULLDUMP 1
#include "TCanvas.h"
#include "PlotUtils/MnvVertErrorBand.h"
#include "PlotUtils/MnvPlotter.h"
#include "PlotUtils/HistogramUtils.h"
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include <iostream>
#include "TText.h"

double xmin = 0.;
double xmax = 20.e3;
int nbins   = 30;

const bool do_fractional_uncertainty = true;
const bool do_cov_area_norm          = false;
const bool include_stat_error        = true;


const std::string do_fractional_uncertainty_str = do_fractional_uncertainty ?
std::string("Frac") :
std::string("Abs");
const std::string do_cov_area_norm_str = do_cov_area_norm ?
std::string("CovAreaNorm") :
std::string("POT");

void setLogScale(int logscale){
  gPad->SetLogy(false);
  gPad->SetLogx(false);
  if (logscale == 0) return;
  if (logscale== 2 || logscale ==3){
    gPad->SetLogy(true);
  }
  if (logscale== 1 || logscale ==3) gPad->SetLogx(true);
}

void resetLogScale(){
  gPad->SetLogy(false);
  gPad->SetLogx(false);
}
  

void PlotErrorSummary(PlotUtils::MnvH1D* hist, std::string label);
void PlotErrorSummary(PlotUtils::MnvH2D* hist, std::string label){std::cout<<"no error bands for 2D" << std::endl;}
void PlotVertBand(std::string band, std::string method_str, PlotUtils::MnvH1D* hist);
void PlotLatBand(std::string band,  std::string method_str, PlotUtils::MnvH1D* hist);
void PlotVertUniverse(std::string band, unsigned int universe, std::string method_str, PlotUtils::MnvH1D* hist);
void PlotLatUniverse(std::string band, unsigned int universe, std::string method_str,  PlotUtils::MnvH1D* hist);
void PlotCVAndError(PlotUtils::MnvH1D* hist, std::string label);
void PlotTotalError(PlotUtils::MnvH1D* hist, std::string method_str );
void Plot2D(PlotUtils::MnvH2D* hist, std::string label);
void PlotCVAndError(PlotUtils::MnvH2D* hist, std::string label);

double integrator(PlotUtils::MnvH1D*);
double integrator(PlotUtils::MnvH2D*);

void PlotTotalError(PlotUtils::MnvH1D* hist, std::string method_str ){
  TH1D *hTotalErr = (TH1D*)hist->GetTotalError( include_stat_error, do_fractional_uncertainty, do_cov_area_norm ).Clone( Form("h_total_err_errSum_%d", __LINE__) );
  hTotalErr->SetDirectory(0);
  TCanvas cF ("c4","c4");
  hTotalErr->SetTitle(Form("Total Uncertainty (%s); %s ", method_str.c_str(),hist->GetTitle() ));
  hTotalErr->Draw();
  cF.Print(Form("%s_TotalUncertainty_%s_%s_%s.png",hist->GetName() , do_fractional_uncertainty_str.c_str(), do_cov_area_norm_str.c_str(), method_str.c_str()));
}

void PlotErrorSummary(TCanvas & cE, PlotUtils::MnvH2D* hist, std::string label, int logscale){std::cout<<" no error summary for 2D" << std::endl;}

void PlotErrorSummary(TCanvas & cE, PlotUtils::MnvH1D* hist, std::string label, int logscale){
  PlotUtils::MnvPlotter mnvPlotter(PlotUtils::kCCQEAntiNuStyle);
  resetLogScale();
  //TCanvas cE ("c1","c1");
  // hist->GetXaxis()->SetTitle(hist->GetTitle());
  // std::string xaxis = mc->GetXaxis()->GetTitle();
  //mnvPlotter.error_color_map.clear();

  mnvPlotter.axis_maximum=0.2;
  mnvPlotter.axis_minimum=0.0;
  mnvPlotter.error_color_map["Flux"]                    = kViolet+6;
  mnvPlotter.error_color_map["Recoil Reconstruction"]   = kOrange+2;
  mnvPlotter.error_color_map["Cross Section Models"]         = kMagenta;
  mnvPlotter.error_color_map["FSI Model"]              = kRed;
  mnvPlotter.error_color_map["Muon Reconstruction"]     = kGreen;
  mnvPlotter.error_color_map["Muon Energy"]     = kGreen+3;
  mnvPlotter.error_color_map["Muon_Energy_MINERvA"]     = kRed-3;
  mnvPlotter.error_color_map["Muon_Energy_MINOS"]     = kViolet-3;
  mnvPlotter.error_color_map["Other"]                  = kGreen+3;
  mnvPlotter.error_color_map["Low Recoil Fits"]         = kRed+3;
  mnvPlotter.error_color_map["GEANT4"]                = kBlue;
  mnvPlotter.error_color_map["Background Subtraction"] = kGreen;
  mnvPlotter.error_color_map["Tune"]=kOrange+2;
  
  mnvPlotter.error_summary_group_map.clear();
#ifndef NOGENIE
  //std::cout << " include GENIE" << std::endl;
  mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrAbs_N");
  mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrAbs_pi");
  mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrCEx_N");
  mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrCEx_pi");
  mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrElas_N");
  mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrElas_pi");
  mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrInel_N");
  mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrInel_pi");
  mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrPiProd_N");
  mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrPiProd_pi");
  mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_MFP_N");
  mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_MFP_pi");
  //
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_AGKYxF1pi");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_AhtBY");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_BhtBY");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_CCQEPauliSupViaKF");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_CV1uBY");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_CV2uBY");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_EtaNCEL");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaCCQE");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaCCQEshape");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaNCEL");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaRES");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MvRES");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormCCQE");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormCCRES");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormDISCC");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormNCRES");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_RDecBR1gamma");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvn1pi");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvn2pi");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvn3pi");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvp1pi");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvp2pi");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Theta_Delta2Npi");
  mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_VecFFCCQEshape");
#endif
  mnvPlotter.error_summary_group_map["Tune"].push_back("RPA_LowQ2");
  mnvPlotter.error_summary_group_map["Tune"].push_back("RPA_HighQ2");
  mnvPlotter.error_summary_group_map["Tune"].push_back("NonResPi");
  mnvPlotter.error_summary_group_map["Tune"].push_back("2p2h");
  mnvPlotter.error_summary_group_map["Tune"].push_back("LowQ2Pi");
  mnvPlotter.error_summary_group_map["Tune"].push_back("Low_Recoil_2p2h_Tune");


//mnvPlotter.error_summary_group_map["Angle"].push_back("BeamAngleX");
//  mnvPlotter.error_summary_group_map["Angle"].push_back("BeamAngleY");

  mnvPlotter.error_summary_group_map["Response"].push_back("response_em");
  mnvPlotter.error_summary_group_map["Response"].push_back("response_proton");
  mnvPlotter.error_summary_group_map["Response"].push_back("response_pion");
  mnvPlotter.error_summary_group_map["Response"].push_back("response_meson");
  mnvPlotter.error_summary_group_map["Response"].push_back("response_other");
  mnvPlotter.error_summary_group_map["Response"].push_back("response_low_neutron");
  mnvPlotter.error_summary_group_map["Response"].push_back("response_mid_neutron");
  mnvPlotter.error_summary_group_map["Response"].push_back("response_high_neutron");

  mnvPlotter.error_summary_group_map["Geant"].push_back("GEANT_Neutron");
  mnvPlotter.error_summary_group_map["Geant"].push_back("GEANT_Proton");
  mnvPlotter.error_summary_group_map["Geant"].push_back("GEANT_Pion");
  //
   mnvPlotter.error_summary_group_map["Muon Energy"].push_back("Muon_Energy_MINOS");
 mnvPlotter.error_summary_group_map["Muon Energy"].push_back("Muon_Energy_MINERvA");
  mnvPlotter.error_summary_group_map["Muon Energy"].push_back("MINOS_Reconstruction_Efficiency");
   mnvPlotter.error_summary_group_map["Muon Energy"].push_back("Muon_Energy_Resolution");
    mnvPlotter.error_summary_group_map["Muon Energy"].push_back("BeamAngleX");
    mnvPlotter.error_summary_group_map["Muon Energy"].push_back("BeamAngleY");
//  mnvPlotter.error_summary_group_map["Unfolding"].push_back("Unfolding");


  mnvPlotter.DrawErrorSummary(hist,"TR",include_stat_error,false,0.0, do_cov_area_norm, "",do_fractional_uncertainty);
   
  std::string plotname = Form("Title: ErrorSummary_%s_%s_%s", hist->GetName(),do_cov_area_norm_str.c_str(),label.c_str());
  TText *t = new TText(.3,.95,label.c_str());
  t->SetNDC(1);
  t->SetTextSize(.03);
  setLogScale(logscale);
//  gPad->SetLogy(false);
//  gPad->SetLogx(false);
//  if (logscale== 2 || logscale ==3){
//    gPad->SetLogy();
//    hist->SetMinimum(0.001);
//  }
//  if (logscale== 1 || logscale ==3) gPad->SetLogx();
  t->Draw();
  cE.Print(cE.GetName(),plotname.c_str());
  resetLogScale();
#ifdef FULLDUMP
    for( auto group:mnvPlotter.error_summary_group_map){
        //std::cout << " error summary for " << group.first << std::endl;
        mnvPlotter.DrawErrorSummary(hist,"TR",include_stat_error,false,0.0, do_cov_area_norm, group.first,do_fractional_uncertainty);
        plotname = Form("Title: ErrorSummary_%s_%s_%s_%s", hist->GetName(),group.first.c_str(),do_cov_area_norm_str.c_str(),label.c_str());
        TText *t = new TText(.3,.95,label.c_str());
        t->SetNDC(1);
        t->SetTextSize(.03);
        setLogScale(logscale);
      //  gPad->SetLogy(false);
      //  gPad->SetLogx(false);
      //  if (logscale== 2 || logscale ==3){
      //    gPad->SetLogy();
      //    hist->SetMinimum(0.001);
      //  }
      //  if (logscale== 1 || logscale ==3) gPad->SetLogx();
        t->Draw();
        cE.Print(cE.GetName(),plotname.c_str());
        resetLogScale();
    }
#endif
  //mnvPlotter.MultiPrint(&cE, plotname, "pdf");
  //  mnvPlotter.DrawErrorSummary(hist,"TR",include_stat_error,true,0.0, do_cov_area_norm, "Angle",false);
  //  plotname = Form("ResponseErrorSummary_%s_%s_%s", hist->GetName(),do_cov_area_norm_str.c_str(),label.c_str());
  //  mnvPlotter.MultiPrint(&cE, plotname, "png");
}

void PlotVertBand(std::string band, std::string method_str, PlotUtils::MnvH1D* hist){
  TH1* h1 = (TH1*)hist->GetVertErrorBand(band.c_str())->GetErrorBand(do_fractional_uncertainty, do_cov_area_norm).Clone(Form("%s_%s_%s", hist->GetName(),band.c_str(), method_str.c_str()));

  if (h1 == NULL){
    std::cout << " no error band " << band << std::endl;
  }
  h1->SetDirectory(0);
  //TH1* h1 = (TH1*)hist->GetVertErrorBand(band.c_str());
  TCanvas cF ("c4","c4");
  h1->SetTitle(Form("%s Uncertainty (%s); Theta_{#nu} (rad)", band.c_str(), method_str.c_str()));
  h1->Draw("h");
  cF.Print(Form("%s_%s_band_%s.png",hist->GetName(), band.c_str(), method_str.c_str()));
}

void PlotLatBand(std::string band, std::string method_str, PlotUtils::MnvH1D* hist){
  TH1* h1 = (TH1*)hist->GetLatErrorBand(band.c_str())->GetErrorBand(do_fractional_uncertainty, do_cov_area_norm).Clone(Form("%s_%s_%s",hist->GetName(), band.c_str(), method_str.c_str()));
  h1->SetDirectory(0);
  //TH1* h1 = (TH1*)hist->GetLatErrorBand(band.c_str());
  TCanvas cF ("c1","c1");
  h1->SetTitle(Form("%s Uncertainty (%s); E_{#nu} (MeV)", band.c_str(), method_str.c_str()));
  h1->Draw("h");
  cF.Print(Form("%s_%s_band_%s.png", hist->GetName(),band.c_str(), method_str.c_str()));
}

void PlotVertUniverse(std::string band, unsigned int universe, std::string method_str, PlotUtils::MnvH1D* hist){

  //std::cout << "band " << band << " " << hist->GetName() << std::endl;
  TH1D* h1 = hist->GetVertErrorBand(band.c_str())->GetHist(universe);
  h1->SetDirectory(0);
  TCanvas cF ("c1","c1");
  h1->SetLineColor(kBlack);
  h1->SetLineStyle(1);
  h1->Draw("hist");
  cF.Print(Form("%s_%s_band_universe%i_%s.png",hist->GetName(), band.c_str(), universe+1, method_str.c_str()));
}

void PlotLatUniverse(std::string band, unsigned int universe, std::string method_str, PlotUtils::MnvH1D* hist){
  TH1D* h1 = hist->GetLatErrorBand(band.c_str())->GetHist(universe);
  h1->SetDirectory(0);
  TCanvas cF ("c1","c1");
  h1->SetLineColor(kBlack);
  h1->SetLineStyle(1);
  h1->Draw("hist");
  cF.Print(Form("%s_%s_band_universe%i_%s.png",hist->GetName() , band.c_str(), universe+1, method_str.c_str()));
}

void PlotCVAndError(TCanvas & cE, PlotUtils::MnvH1D* idatahist,PlotUtils::MnvH1D* ihist, std::string label,bool cov_area=do_cov_area_norm, int logscale=0, bool binwid = true){
  resetLogScale();
  // PlotUtils::MnvPlotter mnvPlotter(PlotUtils::kCCQEAntiNuStyle);
  PlotUtils::MnvPlotter mnvPlotter(PlotUtils::kDefaultStyle);
  //mnvPlotter.SetBinWidthNorm(false);
  mnvPlotter.draw_normalized_to_bin_width=0;
  //binwid = true;
  // need to clone as plan to bin width correct
  if(!ihist || !idatahist){ std::cout<< " No datahist " << ihist << " or mchist " << ihist << " " << label <<  std::endl;
    return;
  }
  MnvH1D* datahist = idatahist->Clone();
  datahist->SetDirectory(0);
  MnvH1D* hist = ihist->Clone();
  hist->SetDirectory(0);
  // TCanvas cE ("c1","c1");
  // hist->GetXaxis()->SetTitle(Form("%s",hist->GetTitle() ));
  hist->GetXaxis()->GetTitle();
  hist->GetYaxis()->SetTitle(Form("%s","Counts per unit" ));
  //PlotUtils::MnvH1D* datahist =new PlotUtils::MnvH1D("adsf", "E_{#nu} (MeV)", nbins, xmin, xmax);
  bool statPlusSys           = true;
  int mcScale                = 1.;
  bool useHistTitles         = false;
  //std::cout << " check bin width " << std::endl;
  //datahist->Print("ALL");
  if (binwid){
    //std::cout << " scale width " << std::endl;
    datahist->Scale(1.,"width");
    hist->Scale(1.,"width");
  }
  const PlotUtils::MnvH1D* bkgdHist     = NULL;
  const PlotUtils::MnvH1D* dataBkgdHist = NULL;
  //datahist->Print("ALL");
//  gPad->SetLogy(false);
//  gPad->SetLogx(false);
//  if (logscale== 2 || logscale ==3) {
//    gPad->SetLogy();
//  }
//  if (logscale== 1 || logscale ==3) gPad->SetLogx();
  setLogScale(logscale);
  cov_area = false;
  TText *t = new TText(.3,.95,label.c_str());
  t->SetNDC(1);
  t->SetTextSize(.03);
  
  
  //std::cout << label << " BinWidthNorm before" << datahist->GetNormBinWidth() << std::endl;
  //datahist->SetNormBinWidth(1.0);
  //hist->SetNormBinWidth(1);
  //mnvPlotter.SetBinWidthNorm(!binwid);
  //std::cout << label << " BinWidthNorm after" << datahist->GetNormBinWidth() << std::endl;
  mnvPlotter.SetROOT6Palette(57); // kBird

  mnvPlotter.DrawDataMCWithErrorBand(datahist, hist, mcScale, "TL", useHistTitles, NULL, NULL,cov_area, statPlusSys);
    TH1D  stat = datahist->GetCVHistoWithStatError();
    stat.SetLineColor(kBlack);
    stat.SetMarkerColor(kBlack);
    stat.Draw("E1 same");
  //mnvPlotter.DrawMCWithErrorBand(hist); //I think that this call only shows stat errors.
  std::string plotname = Form("Title: %s_CV_w_err_%s",datahist->GetName() ,label.c_str());
  t->Draw();
  cE.Print(cE.GetName(),plotname.c_str());

  MnvH1D* d = (MnvH1D*) datahist->Clone();
  d->SetDirectory(0);
  MnvH1D* m = (MnvH1D*) hist->Clone();
  m->SetDirectory(0);

  MnvH1D* mc = (MnvH1D*) m->Clone();
  mc->SetDirectory(0);
  mc->ClearAllErrorBands();
  mc->AddMissingErrorBandsAndFillWithCV(*m);

  d->Divide(d,mc,1.,1.);

  d->GetYaxis()->SetTitle("Data/MC");
  m->Divide(m,mc,1.,1.);
  // no idea why I should have to do this
  //m->Print("ALL");
  //datahist->Draw();
  cov_area = false;
  //mnvPlotter.SetBinWidthNorm(false);
  mnvPlotter.DrawDataMCRatio(d, m, mcScale,true,true);// "TL", useHistTitles, NULL, NULL,cov_area, statPlusSys);

  t->Draw();
  std::string plotname2 = Form("Title: ratio %s_CV_w_err_%s",datahist->GetName() ,label.c_str());

  cE.Print(cE.GetName(),plotname2.c_str());
  resetLogScale();
  //mnvPlotter.MultiPrint(&cE, plotname, "pdf");
  // mnvPlotter.MultiPrint(&cE, plotname, "C");
}

void Plot2D(TCanvas & cE, MnvH2D* ihist, std::string label, int logscale=0, bool binwid = true){
  setLogScale(logscale);
  MnvH2D* hist = (MnvH2D*)ihist->Clone();
  hist->SetDirectory(0);
  setLogScale(logscale);

  std::string xtitle = hist->GetXaxis()->GetTitle();
  std::string ytitle = hist->GetYaxis()->GetTitle();
  std::string title = Form("%s by %s: %s",xtitle.c_str(),ytitle.c_str(),label.c_str());

  hist->GetXaxis()->CenterTitle();
  hist->GetYaxis()->CenterTitle();
  hist->SetTitle(Form("%s",title.c_str()));

//  gPad->SetLogy(false);
//  gPad->SetLogx(false);
//  if (logscale == 2 || logscale == 3) gPad->SetLogy();
//  if (logscale == 1 || logscale == 3) gPad->SetLogx();
  TText *t = new TText(.3,.95,label.c_str());
  hist->Draw("COLZ");
  t->SetNDC(1);
  t->SetTextSize(.03);
  std::string plotname = Form("Title: %s_CV_%s",hist->GetName(),label.c_str());
  t->Draw();

  cE.Print(cE.GetName(),plotname.c_str());
  resetLogScale();
}

void Plot2DFraction(TCanvas & cE, MnvH1D* ihist1, MnvH1D* ihist2, std::string label, int logscale=0, bool binwid = false){ // null version for 1d
}

void Plot2DFraction(TCanvas & cE, MnvH2D* ihist1, MnvH2D* ihist2, std::string label, int logscale=0, bool binwid = false){
    std::cout << "print 2D fraction" << ihist1->GetName() << std::endl;
  setLogScale(logscale);
  TH2D hist1 =  ihist1->GetCVHistoWithStatError();
  TH2D hist2 =  ihist2->GetCVHistoWithStatError();
  hist1.SetDirectory(0);
  hist2.SetDirectory(0);
  setLogScale(logscale);

  std::string xtitle = hist1.GetXaxis()->GetTitle();
  std::string ytitle = hist1.GetYaxis()->GetTitle();
  std::string title = Form("%s by %s: %s",xtitle.c_str(),ytitle.c_str(),label.c_str());

  hist1.GetXaxis()->CenterTitle();
  hist1.GetYaxis()->CenterTitle();
  hist1.SetTitle(Form("%s",title.c_str()));

  gPad->SetLogy(false);
  gPad->SetLogx(false);
  if (logscale == 2 || logscale == 3) gPad->SetLogy();
  if (logscale == 1 || logscale == 3) gPad->SetLogx();
  TText *t = new TText(.3,.90,label.c_str());
  
  hist1.SetLineColor(1);
  hist1.Draw("BOX");
    t->SetNDC(1);
    t->SetTextSize(.03);
    std::string plotname = Form("Title: %s_CV_%s",hist1.GetName(),label.c_str());
    t->Draw();
  hist2.SetLineColor(2);
  hist2.Draw("BOX SAME");
  hist1.Print();
  hist2.Print();
  cE.Print(cE.GetName(),plotname.c_str());
  resetLogScale();
}

void PlotCVAndError(TCanvas & cE, MnvH2D* idatahist, MnvH2D* imchist, std::string label,bool cov_area=do_cov_area_norm, int logscale=0, bool binwid = true){
  setLogScale(logscale);
  
  MnvH2D* d = (MnvH2D*)idatahist->Clone();
  d->SetDirectory(0);
  MnvH2D* mc = (MnvH2D*)imchist->Clone();
  d->SetDirectory(0);

  std::string xaxis = mc->GetXaxis()->GetTitle();
  std::string yaxis = mc->GetYaxis()->GetTitle();
  std::string xtitle = "X Projection "+xaxis;
  std::string ytitle = "Y Projection "+yaxis;
  std::string xlabel = "_projx";
  std::string ylabel = "_projy";


  MnvH1D* d_xhist = d->ProjectionX(Form("%s%s",d->GetName(),xlabel.c_str()),0,-1,"o");
  d_xhist->GetXaxis()->SetTitle(Form("%s",xtitle.c_str()));
  MnvH1D* d_yhist = d->ProjectionY(Form("%s%s",d->GetName(),ylabel.c_str()),0,-1,"o");
  d_yhist->GetXaxis()->SetTitle(Form("%s",ytitle.c_str()));
  MnvH1D* mc_xhist = mc->ProjectionX(Form("%s%s",mc->GetName(),xlabel.c_str()),0,-1,"o");
  mc_xhist->GetXaxis()->SetTitle(Form("%s",xtitle.c_str()));
  MnvH1D* mc_yhist = mc->ProjectionY(Form("%s%s",mc->GetName(),ylabel.c_str()),0,-1,"o");
  mc_yhist->GetXaxis()->SetTitle(Form("%s",ytitle.c_str()));

  std::string dlabel = d->GetTitle();
  std::string mclabel = mc->GetTitle();
  Plot2D(cE,d,dlabel,logscale,binwid);
  resetLogScale();
  Plot2D(cE,mc,dlabel,logscale,binwid);
  resetLogScale();
  PlotCVAndError(cE,d_xhist,mc_xhist,mclabel,false,logscale,binwid);
  resetLogScale();
  PlotCVAndError(cE,d_yhist,mc_yhist,mclabel,false,logscale,binwid);
  resetLogScale();
}


//1D
double integrator(PlotUtils::MnvH1D* h,bool binwid){
  double inte = 0;
  for(int i = 1; i <= h->GetXaxis()->GetNbins(); i++ ){
    double val = h->GetBinContent(i);
    double wid = binwid?h->GetBinWidth(i):1.0;
    inte+=val*wid;
  }
  //std::cout << "Integral of " << h->GetName() << " " << inte << std::endl;
  return inte;
}
//2D
double integrator(PlotUtils::MnvH2D* h,bool binwid){
  double inte = 0;
  for(int ix = 1; ix <= h->GetXaxis()->GetNbins(); ix++ ){
    for(int iy = 1; iy <= h->GetYaxis()->GetNbins(); iy++){
      double val = h->GetBinContent(ix,iy);
      double xwid = binwid?h->GetXaxis()->GetBinWidth(ix):1.0;
      double ywid = binwid?h->GetYaxis()->GetBinWidth(iy):1.0;
      inte+=val*xwid*ywid;
    }
  }
  //std::cout << "Integral of " << h->GetName() << " " << inte << std::endl;
  return inte;
}


#endif
