/**
* @file
* @author  Heidi Schellman/Noah Vaughan/SeanGilligan
* @version 1.0 *
* @section LICENSE *
* This program is free software; you can redistribute it and/or
* modify it under the terms of the GNU General Public License as
* published by the Free Software Foundation; either version 2 of
* the License, or (at your option) any later version. *
* @section DESCRIPTION *
* Code to fill histograms
 */
#include <iostream>
#include <string>
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "MinervaUnfold/MnvResponse.h"
#include "MinervaUnfold/MnvUnfold.h"
#include "utils/RebinFlux.h"
#include "utils/SyncBands.h"
#include "TH2D.h"
#include "TF2.h"
#include "TCanvas.h"
#include "utils/NuConfig.h"
#include "PlotUtils/FluxReweighter.h"

#ifndef __CINT__
#include "include/plotting_pdf.h"
#endif


/*
================================= GetXSec.h ====================================

This templates the analysis steps of doing a 1D and 2D cross section analysis at
MINERvA. Each step is templated to recieve both 1D and 2D inputs. The steps are
as follows:
  - MakeMC: Combine MC signal and bkg to make full MC
  - GetSignalFraction: Uses MC bkg and full MC to create a signal fraction
  - DoBkgSutraction: Uses signal fraction to make bkg on data, then subtracts it
      from data
  - DoUnfolding: Does unfolding in one oftwo ways depending on the variable you
      are analyzing: 1. Crude ratio of (selected truth)/(all truth), 2. Using
      UnfoldUtils.
  - DoEfficiencyCorrection: Corrects unsmeared data for efficiency.
  - DoNormalization: Normalizes for Flux and number of targets. For 1D can do an
      flat flux or energy dependent flux if the variable needs it. For 2D can do
      only flat right now.


Noah Harvey Vaughan, May 2021
Schellman Neutrino Group, Oregon State University
vaughann@oregonstate.edu
================================================================================
*/
//============================ Some Useful Tools ===============================

// Splits a string by given delimiter, useful for separating categories of 2D variable names
std::vector<std::string> split (std::string s, std::string delimiter) {
  size_t pos_start = 0, pos_end, delim_len = delimiter.length();
  std::string token;
  std::vector<std::string> res;

  while ((pos_end = s.find (delimiter, pos_start)) != std::string::npos) {
    token = s.substr (pos_start, pos_end - pos_start);
    pos_start = pos_end + delim_len;
    res.push_back (token);
  }

  res.push_back (s.substr (pos_start));
  return res;
}

TMatrixD ZeroDiagonal(const TMatrixD &m){
  std::cout << " TRACE: enter ZeroDiagonal  "   << std::endl;
  TMatrixD newm = TMatrixD(m);
  int n = newm.GetNrows();
  for (int i = 0; i < n; i++){
    newm[i][i] = 0;
  }
  return newm;
}

// Returns a map of bools for { 'fluxnorm', 'xfluxnorm', 'yfluxnorm'} based off "fluxnorm" set in variable config
// Used to tell the code when and how to use an integrated flux normalization vs an energy dependent flux normalization
std::map< std::string, bool > CheckFluxNorm( NuConfig* configvar, std::string variable){
  // what it will spit out
  std::map< std::string, bool > fluxnormBoolMap;
  // Default to false. 1D uses fluxnorm only, 2D uses xfluxnorm and yfluxnorm
  fluxnormBoolMap["fluxnorm"] = false;
  fluxnormBoolMap["xfluxnorm"] = false;
  fluxnormBoolMap["yfluxnorm"] = false;

//  std::string varsFile = config.GetString("varsFile");
//NuConfig configvar;
//  if (varsFile != "" ){
//    configvar.Read(varsFile);
//  }
//  else{
//    std::cout << " no varsFile" << std::endl;
//    exit(1);
//  }

  NuConfig varconfig = configvar->GetConfigVariable(variable);
  if(varconfig.IsMember("fluxnorm")){
    fluxnormBoolMap["fluxnorm"] = varconfig.GetBool("fluxnorm");
  }
  else if(varconfig.IsMember("xvar") && varconfig.IsMember("yvar")){
    std::string xvar = varconfig.GetString("xvar");
    NuConfig xconfig = configvar->GetConfigVariable(xvar);
    if(xconfig.IsMember("fluxnorm")){
      fluxnormBoolMap["xfluxnorm"] = xconfig.GetBool("fluxnorm");
      if(fluxnormBoolMap["xfluxnorm"]) fluxnormBoolMap["fluxnorm"] = true;
    }
    std::string yvar = varconfig.GetString("yvar");
    NuConfig yconfig = configvar->GetConfigVariable(yvar);
    if(yconfig.IsMember("fluxnorm")){
      fluxnormBoolMap["yfluxnorm"] = yconfig.GetBool("fluxnorm");
      if(fluxnormBoolMap["yfluxnorm"]) fluxnormBoolMap["fluxnorm"] = true;
    }
  }
  else{
    std::cout << " CheckFluxNorm: " << variable << " has no fluxnorm member, defaulting to false." << std::endl;
  }

  // sets 'fluxnorm' to true if xfluxnorm or yfluxnorm are set to true.
  // if (fluxnormBoolMap["xfluxnorm"] || fluxnormBoolMap["yfluxnorm"]) {
  //   fluxnormBoolMap["fluxnorm"] = true;
  // }

  return fluxnormBoolMap;
}




//================================= Make MC ====================================
// Makes a total MC hist from MC signal + MC background
template <class MnvHistoType>
  MnvHistoType* MakeMC(std::string basename, MnvHistoType* imcsighist, MnvHistoType* imcbkghist){
    std::string mcname = basename+"_mc_tot";
    MnvHistoType* mc = (MnvHistoType*)imcsighist->Clone(mcname.c_str());
    mc->SetDirectory(0);

    mc->Add(imcbkghist);
    SyncBands(mc);

    return mc;
  }
template MnvH1D* MakeMC<MnvH1D>(std::string basename, MnvH1D* imcsighist, MnvH1D* imcbkghist);
template MnvH2D* MakeMC<MnvH2D>(std::string basename, MnvH2D* imcsighist, MnvH2D* imcbkghist);



//============================== Signal Fraction ===============================
// Gets signal fraction of MC signal over MC total
template <class MnvHistoType>
  MnvHistoType* GetSignalFraction(std::string basename, MnvHistoType* imcsighist, MnvHistoType* mc){
    std::string fracname = basename+"_signalfraction";
    MnvHistoType* signalFraction = (MnvHistoType*)imcsighist->Clone(fracname.c_str());
    signalFraction->SetDirectory(0);

    signalFraction->Divide(imcsighist,mc,1.,1.,"B");
    SyncBands(signalFraction);

    return signalFraction;
  }
template MnvH1D* GetSignalFraction<MnvH1D>(std::string basename, MnvH1D* imcsighist, MnvH1D* mc);
template MnvH2D* GetSignalFraction<MnvH2D>(std::string basename, MnvH2D* imcsighist, MnvH2D* mc);

template <class MnvHistoType>
  MnvHistoType* GetBkgFraction(std::string basename, MnvHistoType* imcbkghist, MnvHistoType* mc){
    std::string fracname = basename+"_bkgfraction";
    MnvHistoType* bkgFraction = (MnvHistoType*)imcbkghist->Clone(fracname.c_str());
    bkgFraction->SetDirectory(0);

    bkgFraction->Divide(imcbkghist,mc,1.,1.,"B");
    SyncBands(bkgFraction);

    return bkgFraction;
  }
template MnvH1D* GetBkgFraction<MnvH1D>(std::string basename, MnvH1D* imcbkghist, MnvH1D* mc);
template MnvH2D* GetBkgFraction<MnvH2D>(std::string basename, MnvH2D* imcbkghist, MnvH2D* mc);



//========================== Background Subtraction ============================
// Rough background subtraction using input signal fraction
template <class MnvHistoType>
  MnvHistoType* DoBkgSubtraction(std::string basename, MnvHistoType* idatahist, MnvHistoType* mc, MnvHistoType* signalFraction){
    std::string bkgsubname = basename+"_bkgsub";
    MnvHistoType* bkgsub = (MnvHistoType*)idatahist->Clone(bkgsubname.c_str());
    bkgsub->SetDirectory(0);

    bkgsub->AddMissingErrorBandsAndFillWithCV(*mc);
    bkgsub->Multiply(bkgsub,signalFraction);
    SyncBands(bkgsub);

    return bkgsub;
  }
template MnvH1D* DoBkgSubtraction<MnvH1D>(std::string basename, MnvH1D* idatahist, MnvH1D* mc, MnvH1D* signalFraction);
template MnvH2D* DoBkgSubtraction<MnvH2D>(std::string basename, MnvH2D* idatahist, MnvH2D* mc, MnvH2D* signalFraction);



//================================ Unfolding ===================================

//------------------------------ Ratio Unfolding -------------------------------
// Unfolding for things that don't really need it. Just uses crude ratio of
// sel_truth over full MCReco.
template <class MnvHistoType>
  std::vector<MnvHistoType*> DoRatioUnfolding(std::string basename, MnvHistoType* bkgsub, MnvHistoType* imcsighist, MnvHistoType* idatahist, MnvHistoType* iseltruhist){
    std::vector<MnvHistoType*> outUnsmearingVec;
    std::string unsmearedname = std::string(bkgsub->GetName()) + "_unfolded";
    MnvHistoType* unsmeared = (MnvHistoType*)idatahist->Clone(unsmearedname.c_str());
    
    unsmeared->SetDirectory(0);

    std::string unsmearingname = basename + "_ratiounsmearing";
    MnvHistoType* unsmearing = (MnvHistoType*)bkgsub->Clone(unsmearingname.c_str());
    unsmearing->AddMissingErrorBandsAndFillWithCV(*iseltruhist);
    unsmearing->SetDirectory(0);

    unsmearing->Divide(iseltruhist,imcsighist,1.,1.,"B");
    unsmeared->Multiply(unsmeared,unsmearing,1.,1.);

    // Commenting out since may not be necessary.
    SyncBands(unsmeared);
    SyncBands(unsmearing);
    outUnsmearingVec.push_back(unsmeared);
    outUnsmearingVec.push_back(unsmearing);
    // Returns a vector of size two of < (roughly unsmeared variable hist), ( rough unsmearing hist ) >
    return outUnsmearingVec;
  }

template std::vector<MnvH1D*> DoRatioUnfolding<MnvH1D>(std::string basename, MnvH1D* bkgsub, MnvH1D* imcsighist, MnvH1D* idatahist, MnvH1D* iseltruhist);
template std::vector<MnvH2D*> DoRatioUnfolding<MnvH2D>(std::string basename, MnvH2D* bkgsub, MnvH2D* imcsighist, MnvH2D* idatahist, MnvH2D* iseltruhist);

//---------------------------- Response Unfolding ------------------------------

// Dummy template. Do not use.
template <class MnvHistoType>
  MnvHistoType* DoResponseUnfolding(std::string basename, MnvH2D* iresponse, MnvHistoType* imcsighist, MnvHistoType* iseltruhist, MnvHistoType* bkgsub, MnvHistoType* idatahist, MinervaUnfold::MnvUnfold unfold, double num_iter){
    std::string unsmearedname = std::string(bkgsub->GetName()) + "_notunfolded";
    MnvHistoType* unsmeared = (MnvHistoType*)idatahist->Clone(unsmearedname.c_str());
    unsmeared->SetDirectory(0);
    SyncBands(unsmeared);
    std::cout << " WARNING: something's wrong, used default response unfolding that does nothing." << std::endl;
    return unsmeared;
  }

// 1D
template<> MnvH1D* DoResponseUnfolding<MnvH1D>(std::string basename, MnvH2D* iresponse, MnvH1D* imcsighist, MnvH1D* iseltruhist, MnvH1D* bkgsub, MnvH1D* idatahist, MinervaUnfold::MnvUnfold unfold, double num_iter){
  MnvH2D* migration = (MnvH2D*)iresponse->Clone();
  if (migration == 0) {
  std::cout << " no migration, stop here for " << basename << std::endl;
    SyncBands(bkgsub);
    return bkgsub;
  }
  // Commenting out since may not be necessary.
  SyncBands(migration);
  // you can't put the cv in as the unfolding code does not expect it.
  migration->PopVertErrorBand("cv");

  std::string unsmearedname = std::string(bkgsub->GetName()) + "_unfolded";
    MnvH1D* unsmeared;// = (MnvH1D*)iseltruhist->Clone(unsmearedname.c_str());
    // make an unsmeared without error bands so that the unfolding can add them
  unsmeared = new MnvH1D( *dynamic_cast<const TH1D*>((iseltruhist)->Clone(unsmearedname.c_str())) );
  //  unsmeared->SetName(unsmearedname.c_str());
  //unsmeared->AddMissingErrorBandsAndFillWithCV(*iseltruhist);
  unsmeared->SetDirectory(0);
  std::cout << " Migration matrix has size " << migration->GetErrorBandNames().size() << std::endl;
  std::cout << " Data has  size " << bkgsub->GetErrorBandNames().size() << std::endl;
  //MnvH1D* empty = (MnvH1D*)bkgsub->Clone((std::string(bkgsub->GetName())+"_empty").c_str());
  //empty->Reset();
  // make an empty covariance matrix for the unfolding to give back to you
  TMatrixD covmatrix;


  // try doing with variable size matrices.
    bool data_unfolded = unfold.UnfoldHisto(unsmeared,covmatrix,migration,bkgsub,RooUnfold::kBayes,num_iter,true,true);
   // bool MnvUnfold::UnfoldHistoWithFakes(PlotUtils::MnvH1D* &h_unfold, TMatrixD &covmx, const PlotUtils::MnvH2D* const h_migration, const PlotUtils::MnvH1D* const h_data, const PlotUtils::MnvH1D* const  h_model_reco, const PlotUtils::MnvH1D* const h_model_truth, const PlotUtils::MnvH1D* const h_model_background, double regparam,bool addSystematics,bool useSysVariatedMigrations) const
    // this defaults to Bayesian
   // bool data_unfolded = unfold.UnfoldHistoWithFakes(unsmeared,covmatrix,migration,bkgsub,imcsighist,iseltruhist,empty,4.,true, true);
    if(DEBUG) bkgsub->Print("ALL");

  for (int i = 0; i < covmatrix.GetNrows(); i++){
    covmatrix[i][i] = 0.0;
  }
    

  unsmeared->FillSysErrorMatrix("Unfolding",covmatrix);
    
  // Commenting out since may not be necessary.
  SyncBands(unsmeared);
  
  //  unsmeared->Print("ALL");
  return unsmeared;
};

// Response unfolding for 2D histos
template<> MnvH2D* DoResponseUnfolding<MnvH2D>(std::string basename, MnvH2D* iresponse,
                                      MnvH2D* imcsighist, MnvH2D* iseltruhist, MnvH2D* bkgsub, MnvH2D* idatahist,
                                      MinervaUnfold::MnvUnfold unfold, double num_iter){
  MnvH2D* migration = (MnvH2D*)iresponse->Clone();
  if (migration == 0) {
  std::cout << " no migration, stop here for " << basename << std::endl;
    return bkgsub;
  }
  // Commenting out since may not be necessary.
  SyncBands(migration);
  // you can't put the cv in as the unfolding code does not expect it.
  migration->PopVertErrorBand("cv");
  // std::cout << " Migration matrix has size " << migration->GetErrorBandNames().size() << std::endl;
  // std::cout << " Data has  size " << bkgsub->GetErrorBandNames().size() << std::endl;

  std::string unsmearedname = std::string(bkgsub->GetName()) + "_unfolded";
  // HMS MnvH2D* unsmeared = (MnvH2D*)idatahist->Clone(unsmearedname.c_str());
  MnvH2D* unsmeared = (MnvH2D*)iseltruhist->Clone(unsmearedname.c_str());
  unsmeared->SetDirectory(0);
  bkgsub->Print();
  iseltruhist->Print();
  imcsighist->Print();
  
  // now to get the covariance matrix for the unfolding itself using only the central value  This is the method Amit used
  // make an empty covariance matrix for the unfolding to give back to you
  std::cout << " starting 2D unfolding " << std::endl;
  // bool data_unfolded = unfold.UnfoldHisto2D(unsmeared,migration,mc,iseltruhist,bkgsub,num_iter,true,true);
  std::cout << "imcsighist " << imcsighist->Integral() << " " << imcsighist->Integral() << std::endl;
  std::cout << "iseltruhist " << iseltruhist->Integral() << " " << iseltruhist->Integral() << std::endl;
  std::cout << "bkgsub " << bkgsub->Integral() << " " << bkgsub->Integral() << std::endl;
  
  std::cout << "migration x y" << migration->ProjectionX()->Integral() << " " << migration->ProjectionY()->Integral() << std::endl;
//  if (imcsighist->Integral() != migration->ProjectionX()->Integral() ){
//    std::cout << " make migration matrix have same scale as imcsighist" << std::endl;
//    migration->Scale(imcsighist->Integral()/migration->ProjectionX()->Integral());
//  }
  bool data_unfolded = unfold.UnfoldHisto2D(unsmeared,migration,imcsighist,iseltruhist,bkgsub,num_iter,true,true);
  std::cout << " Done with 2D unfolding " << std::endl;
  std::cout << "unsmeared " << unsmeared->Integral() << " " << unsmeared->Integral() << std::endl;
  bkgsub->Print();
  imcsighist->Print();
  iseltruhist->Print();
  // extra code just to get CV covmx
  TH2D* hUnfoldedDummy=new TH2D(unsmeared->GetCVHistoWithStatError());
  TH2D* hMigrationDummy=new TH2D(migration->GetCVHistoWithStatError());
  TH2D* hRecoDummy=new TH2D(imcsighist->GetCVHistoWithStatError());
  TH2D* hTruthDummy=new TH2D(iseltruhist->GetCVHistoWithStatError());
  TH2D* hBGSubDataDummy=new TH2D(bkgsub->GetCVHistoWithStatError());
  TMatrixD unfoldingCovMatrixOrig_hist_type;
  std::cout << "HERE for COVARIANCE " << std::endl;
  //unfoldingCovMatrixOrig_hist_type.Print("ALL");
  unfold.UnfoldHisto2D(hUnfoldedDummy, unfoldingCovMatrixOrig_hist_type, hMigrationDummy, hRecoDummy, hTruthDummy, hBGSubDataDummy, num_iter);
  int correctNbins = hUnfoldedDummy->fN;
  int matrixRows = unfoldingCovMatrixOrig_hist_type.GetNrows();
  
  if(correctNbins!=matrixRows){
  
  cout << "****************************************************************************" << endl;
 cout << "*  Fixing unfolding matrix size because of RooUnfold bug. From " << matrixRows << " to " << correctNbins << endl;
 cout << "****************************************************************************" << endl;
 // It looks like this DTRT, since the extra last two bins don't have any content
 unfoldingCovMatrixOrig_hist_type.ResizeTo(correctNbins, correctNbins);
  }
 TMatrix unfoldingCov = ZeroDiagonal(unfoldingCovMatrixOrig_hist_type);
 //unsmeared->PushCovMatrix("",unfoldingCov);
  unsmeared->FillSysErrorMatrix("Unfolding",unfoldingCov);
  // Commenting out since may not be necessary.
  SyncBands(unsmeared);
  return unsmeared;
};

//-------------------------------- DoUnfolding ---------------------------------
// Putting the unfolding all together.

// check call  std::vector<MnvHistoType*> unsmearedVec = DoUnfolding(basename,iresponse,iresponse_reco,iresponse_truth,bkgsub,idatahist,unfold,num_iter);
template<class MnvHistoType>
  std::vector<MnvHistoType*> DoUnfolding(std::string basename, MnvH2D* iresponse,
                              MnvHistoType* imcsighist, MnvHistoType* iseltruhist, MnvHistoType* bkgsub,
                              MnvHistoType* idatahist, MinervaUnfold::MnvUnfold unfold, double num_iter){
    // If there's no response, do a rough ratio unfolding
    if(iresponse == 0){
      std::cout << " use ratio unfolding for " << basename  << std::endl;
      // If there's no truth histogram you can't do unfolding.
      if (iseltruhist == 0){
        std::cout << " No truth info so no unsmearing possible for " << basename << std::endl;
        // Returns an empty vector, which makes the loop continue to the next variable, useful for sidebands
        return {};
      }
      // Output is a vector of size two < (unsmeared variable hist), (rough unsmearing hist) >
      std::vector<MnvHistoType*> unsmearedVec = DoRatioUnfolding(basename,bkgsub,imcsighist,idatahist,iseltruhist);

      return unsmearedVec;
    }
    // If there is response, do real unfolding
    else{
      std::cout << " use response unfolding for " << basename  << std::endl;
      // Output is a vector of size one < (unsmeared variable hist) >
      std::vector<MnvHistoType*> unsmearedVec;
      MnvHistoType* unsmeared = DoResponseUnfolding(basename,iresponse,imcsighist,iseltruhist,bkgsub,idatahist,unfold,num_iter);
      SyncBands(unsmeared);
      unsmearedVec.push_back(unsmeared);

      return unsmearedVec;
    }
  }
template std::vector<MnvH1D*> DoUnfolding<MnvH1D>(std::string basename, MnvH2D* iresponse, MnvH1D* mc, MnvH1D* iseltruhist, MnvH1D* bkgsub, MnvH1D* idatahist, MinervaUnfold::MnvUnfold unfold, double num_iter);
template std::vector<MnvH2D*> DoUnfolding<MnvH2D>(std::string basename, MnvH2D* iresponse, MnvH2D* mc, MnvH2D* iseltruhist, MnvH2D* bkgsub, MnvH2D* idatahist, MinervaUnfold::MnvUnfold unfold, double num_iter);



//========================== Efficiency Correction =============================
// Divides unfolded hists by efficiency (calculated as (selected truth)/(all truth) )
template <class MnvHistoType>
  std::vector<MnvHistoType*> DoEfficiencyCorrection(std::string basename, MnvHistoType* unsmeared, MnvHistoType* iseltruhist, MnvHistoType* ialltruhist, const bool fluxhere=false){

    // Vector passed out of < (efficiency corrected hist), (efficiency hist) >
    std::vector<MnvHistoType*> outEffVec;
    std::cout << "start DoEfficiencyCorrection" << std::endl;
    std::string effcorrname = std::string(unsmeared->GetName())+"_effcorr";
    MnvHistoType* effcorr = (MnvHistoType*)unsmeared->Clone(effcorrname.c_str());
    std::cout << "clone unsmeared" << std::endl;
    effcorr->SetDirectory(0);

    // make the efficiency
    std::string efficiencyname = basename+"_efficiency";
    std::cout << "make efficiency" << std::endl;
    MnvHistoType* efficiency = (MnvHistoType*)iseltruhist->Clone(efficiencyname.c_str());
    efficiency->SetDirectory(0);

    // apply the efficiency
    efficiency->AddMissingErrorBandsAndFillWithCV(*ialltruhist); //should be seltruhists?
    SyncBands(efficiency);
    // make certain efficiency has all error bands for thing it will be applied to
    if (fluxhere) { // special code to make the errors include variable dependend flux
      efficiency->PopVertErrorBand("Flux");

      std::cout << "removed Flux Error band from efficiency" << std::endl;
    }
    efficiency->AddMissingErrorBandsAndFillWithCV(*unsmeared);
    SyncBands(efficiency);
    efficiency->Divide(efficiency,ialltruhist,1.,1.,"B");
    //efficiency->AddMissingErrorBandsAndFillWithCV(*unsmeared);
    // Commenting out since may not be necessary.
    SyncBands(efficiency);
    effcorr->Divide(unsmeared,efficiency,1.,1.);
    // Commenting out since may not be necessary.
    SyncBands(effcorr);

    outEffVec.push_back(effcorr);
    outEffVec.push_back(efficiency);
    return outEffVec;
  }
template std::vector<MnvH1D*> DoEfficiencyCorrection<MnvH1D>(std::string basename, MnvH1D* unsmeared, MnvH1D* iseltruhist, MnvH1D* ialltruhist, const bool fluxhere);
template std::vector<MnvH2D*> DoEfficiencyCorrection<MnvH2D>(std::string basename, MnvH2D* unsmeared, MnvH2D* iseltruhist, MnvH2D* ialltruhist, const bool fluxhere);


//============================== Normalization =================================
// Does number of target normalization (passed in from analyze code) and flux normalization.
// Returns a vector of size to of < (Data xsec), (MC xsec) >
template<class MnvHistoType>
  std::vector<MnvHistoType*> DoNormalization( std::map<const std::string, NuConfig *> configs, std::string basename, std::map< std::string, bool> FluxNorm, double norm, MnvHistoType* effcorr, MnvHistoType* ialltruhist, MnvH1D* h_flux_dewidthed){
      NuConfig* config = configs["main"];
    std::string sigmaname = std::string(effcorr->GetName())+"_sigma";
    MnvHistoType* sigma = (MnvHistoType*)effcorr->Clone(sigmaname.c_str());
    sigma->SetDirectory(0);
    std::string sigmaMCname = basename+"_sigmaMC";
    MnvHistoType* sigmaMC = (MnvHistoType*)ialltruhist->Clone(sigmaMCname.c_str());
    sigmaMC->SetDirectory(0);

    // Integrated flux normalization for non-energy variables
    // Set by 'fluxnorm':false on 1D variables in the variables config
    if(!FluxNorm["fluxnorm"]){
      std::cout << " Using flat flux normalization. " << std::endl;
      // Returns integrated flux hist in bins input hist
      MnvHistoType* theflux = GetFluxFlat(configs, sigma);

      theflux->AddMissingErrorBandsAndFillWithCV(*sigma);
      sigma->AddMissingErrorBandsAndFillWithCV(*theflux);
      sigma->Divide(sigma,theflux);
      // target normalization
      sigma->Scale(norm);

      theflux->AddMissingErrorBandsAndFillWithCV(*sigmaMC);
      sigmaMC->AddMissingErrorBandsAndFillWithCV(*theflux);
      sigmaMC->Divide(sigmaMC,theflux);
      // target normalization
      sigmaMC->Scale(norm);
    }
    // Energy dependent flux normalization
    // Set by 'fluxnorm':true on 1D variables in the variables config
    else{
      std::cout << " Using energy dependent flux normalization. " << std::endl;
      // Returns flux hist in bins of energy variable of input hist (for 2D the bins on the non-energy axis are integrated)
      MnvHistoType* h_flux_ebins = GetFluxEbins(h_flux_dewidthed,ialltruhist,*config,FluxNorm);
       

      // TODO: Flipped the order of the Divide and Scale steps. Does this matter?
      h_flux_ebins->AddMissingErrorBandsAndFillWithCV(*sigma);
        h_flux_ebins->SetName(std::string("h_flux_ebins_"+basename).c_str());
      h_flux_ebins->Write();
      sigma->AddMissingErrorBandsAndFillWithCV(*h_flux_ebins);
      sigma->Divide(sigma,h_flux_ebins);
      // target normalization
      sigma->Scale(norm);
  
      SyncBands(sigma);
      // if (DEBUG) sigma->GetSysErrorMatrix("Unfolding").Print();

      h_flux_ebins->AddMissingErrorBandsAndFillWithCV(*sigmaMC);
      sigmaMC->AddMissingErrorBandsAndFillWithCV(*h_flux_ebins);
      sigmaMC->Divide(sigmaMC,h_flux_ebins,1.0,1.0);
      // target normalization
      sigmaMC->Scale(norm);
      
    }
    SyncBands(sigma);
    SyncBands(sigmaMC);
    if(sigma->InheritsFrom("TH2")){
      MnvH2D* sigma2D=dynamic_cast<MnvH2D*>(sigma->Clone());
      sigma2D->MnvH2DToCSV(sigma2D->GetName(),"./csv",1.E39,false,true,true,true);
    }
    else{
      MnvH1D* sigma1D=dynamic_cast<MnvH1D*>(sigma->Clone());
      sigma1D->MnvH1DToCSV(sigma1D->GetName(),"./csv",1.E39,false,true,true,true);
    }
    std::vector<MnvHistoType*> sigmaVec;
    sigmaVec.push_back(sigma);
    sigmaVec.push_back(sigmaMC);
    return sigmaVec;
  }


template std::vector<MnvH1D*> DoNormalization<MnvH1D>( std::map<const std::string,NuConfig* > configs, std::string basename, std::map< std::string, bool> FluxNorm, double norm, MnvH1D* effcorr, MnvH1D* ialltruhist, MnvH1D* h_flux_dewidthed);
template std::vector<MnvH2D*> DoNormalization<MnvH2D>( std::map<const std::string,NuConfig* > configs, std::string basename, std::map< std::string, bool> FluxNorm, double norm, MnvH2D* effcorr, MnvH2D* ialltruhist,  MnvH1D* h_flux_dewidthed);



//============================= GetCrossSection ================================

// dummy for backwards compatibility config > map of config*
template<class MnvHistoType>
  int GetCrossSection(std::string sample, std::string variable, std::string basename,
                      std::map< std::string, std::map <std::string, MnvHistoType*> > histsND,
                      std::map< std::string, std::map <std::string, MnvH2D*> > responseND,
                      NuConfig oneconfig, TCanvas & canvas, double norm, double POTScale, MnvH1D* h_flux_dewidthed,
                      MinervaUnfold::MnvUnfold unfold, double num_iter, bool DEBUG, bool hasbkgsub, bool usetune) {
      std::map<const std::string, NuConfig*> configmap;
      configmap["main"]= &oneconfig;
      std::cout << " pass single config into map" << std::endl;
      return GetCrossSection(sample,  variable,  basename,
                             histsND,
                             responseND,
                             configmap,  canvas, norm, POTScale,  h_flux_dewidthed,
                             unfold,  num_iter, DEBUG, hasbkgsub,usetune);
  }

template<class MnvHistoType>
  int GetCrossSection(std::string sample, std::string variable, std::string basename,
                      std::map< std::string, std::map <std::string, MnvHistoType*> > histsND,
                      std::map< std::string, std::map <std::string, MnvH2D*> > responseND,
                      std::map< const std::string, NuConfig *> configs, TCanvas & canvas, double norm, double POTScale,  MnvH1D* h_flux_dewidthed,
                      MinervaUnfold::MnvUnfold unfold, double num_iter, bool DEBUG, bool hasbkgsub, bool usetune) {
    bool binwid = true;
    int logscale = 0; // 0 for none, 1 for x, 2 for y, 3 for both

    // Get "category" tags set in config. Needs to match ones used in the event loop.
    //TODO: Make this a map in config.
    
    std::cout << " at the top of GetXsec" << sample <<  std::endl;
    // this can come out of the sample information:
    // configs["main"]->Print();
    NuConfig sigkey = configs["main"]->GetConfig("signal");
    //sigkey.Print();
    std::string sig = sigkey.GetString(sample);
    std::cout << " got sig " << sig << std::endl;
    NuConfig bkgkey;
    std::string bkg;
    if (!hasbkgsub){
      // this likely needs to be fixed
      bkgkey = configs["main"]->GetConfig("background");
      //bkgkey.Print();
      std::cout << bkgkey.CheckMember(sample) << std::endl;
      bkg = bkgkey.GetString(sample);
      std::cout << " got bkg " << bkg << std::endl;
    }
    NuConfig datkey = configs["main"]->GetConfig("data");
    std::string dat = datkey.GetString(sample);
    std::cout << " got dat " << dat << std::endl;
    
    
    //datkey.Print();
    //std::string bkg = config.GetString("background");
    // std::string dat = config.GetString("data");

    // parse out variable to get axes
    std::vector<std::string> varparse;

    // "basename" input of the form "h_<sample>_<variable>" or "h2D_<sample>_<variable>"
    // Check if not 2D then make logscale for plotting if looking at Q^2_QE
    if(basename.find("h2D_")==std::string::npos){
      if(variable.find("Q2QE")!=std::string::npos) logscale = 1;
    }
    // If 2D, then set log scale for each axis if needed
    else{
      varparse = split(variable,"_");
      if(varparse[0].find("Q2QE")!=std::string::npos) logscale+=1;
      if(varparse[1].find("Q2QE")!=std::string::npos) logscale+=2;
    }

    std::cout << " analyze " << variable << std::endl;

    if (DEBUG) std::cout << "logscale " << variable << " " << logscale << std::endl;

    // Print out the "type" tag from analyze code (e.g. "reconstructed", "selected_truth", etc.)
    // Scale POT for all MC hists, except response (get segfault if done this way...) -NHV
    std::cout << " starting on variable " << sample << " " << variable << std::endl;
    for(auto types : histsND){
      std::string type = types.first;
      std::cout << "hists key " << type << std::endl;
      for(auto categories : histsND[type]){
        std::string category = categories.first;
        if (category.find(dat)==std::string::npos){
          
          if (histsND[type][category] != 0) {
            double t = histsND[type][category]->Integral();
            histsND[type][category]->Scale(POTScale);
            std::cout << " POTScaled " << histsND[type][category]->GetName() << " " << t << " " << histsND[type][category]->Integral() <<  std::endl;
          }
        }
      }
    }
    for(auto types : responseND){
      std::string type = types.first;
      std::cout << "response key " << type << std::endl;
      for(auto categories : responseND[type]){
        std::string category = categories.first;
        if (category.find(dat)==std::string::npos){
          
          if (responseND[type][category] != 0) {
            double t = responseND[type][category]->Integral();
            responseND[type][category]->Scale(POTScale);
            std::cout << " POTScaled " << responseND[type][category]->GetName() << " " << t << " " << responseND[type][category]->Integral() <<  std::endl;
          }
        }
      }
    }

    // Assign each input histogram type used for doing the analysis.
    // MnvHistoType can be MnvH1D or MnvH2D so far. Response is always MnvH2D.
    MnvHistoType* idatahist = histsND["reconstructed"][dat];
    MnvHistoType* imcsighist = histsND["reconstructed"][sig];
    std::string stuned = "";
    if (histsND.count("reconstructed_tuned") && usetune){
        stuned = "Tuned ";
        imcsighist = histsND["reconstructed_tuned"][sig];
        std::cout << " using " << imcsighist->GetName() << std::endl;
    }
    //std::cout << "using signal " << imcsighist->GetName() << std::endl;
    MnvHistoType* imcbkghist;
    MnvHistoType* ibkgsubhist;
    if (!hasbkgsub){
      imcbkghist = histsND["reconstructed"][bkg];
      if (histsND.count("reconstructed_tuned")&& usetune){
        imcbkghist = histsND["reconstructed_tuned"][bkg];
        std::cout << " using " << imcbkghist->GetName() << std::endl;
      }
    }
    std::cout << "using background " << imcbkghist->GetName() << std::endl;
    if (hasbkgsub) ibkgsubhist = histsND["fitted"]["bkgsub"];
      MnvHistoType* iseltruhist;
    if (histsND.count("selected_truth_tuned") && usetune){
        iseltruhist = histsND["selected_truth_tuned"][sig];
        std::cout << " using " << iseltruhist->GetName() << std::endl;
    }
    else{
        iseltruhist = histsND["selected_truth"][sig];
    }
    MnvHistoType* ialltruhist;
      
    if (histsND.count("all_truth_tuned") && usetune){
        ialltruhist = histsND["all_truth_tuned"][sig];
        std::cout << " using " << ialltruhist->GetName() << std::endl;
    }
    else{
        ialltruhist = histsND["all_truth"][sig];
    }
    
    MnvH2D* iresponse;
    MnvHistoType* iresponse_reco=imcsighist;
    MnvHistoType* iresponse_truth=iseltruhist;
    if (responseND.count("response_migration_tuned") && usetune){
        iresponse = responseND["response_migration_tuned"][sig];
        iresponse_reco=histsND["response_tuned_reco"][sig];
        iresponse_truth=histsND["response_tuned_truth"][sig];
        std::cout << " using " << iresponse->GetName() <<  " " << iresponse->ProjectionX()->Integral()<< " " <<iresponse->ProjectionY()->Integral()<< std::endl;
    }
    else{
        iresponse = responseND["response_migration"][sig];
        iresponse_reco=histsND["response_reco"][sig];
        iresponse_truth=histsND["response_truth"][sig];
        std::cout << " using " << iresponse->GetName() <<  " " << iresponse->ProjectionX()->Integral()<< " " <<iresponse->ProjectionY()->Integral()<< std::endl;
    }
    // TODO: POTScale by if (not data) --> POTScale


    // Check for each hist "category" for the variable you're analyzing.
    if (idatahist == 0){
      std::cout << " no data for " << variable << std::endl;
      return 1; // Exits if cannot be found
    }
    idatahist->Print();
    idatahist->Write();

    if (imcsighist == 0){
      std::cout << " no sig for " << variable << std::endl;
      return 1;
    }
    //imcsighist->Scale(POTScale);
    imcsighist->Print();
    imcsighist->Write();
    // if (DEBUG) std::cout << " MC sig scaled by POT for " << variable << std::endl;

    if (imcbkghist == 0 && !hasbkgsub){
      std::cout << " no bkg for " << variable << std::endl;
      return 1;
    }
    // imcbkghist->Scale(POTScale);
    if (!hasbkgsub){
      imcbkghist->Print();
      imcbkghist->Write();
    }
    
    // if (DEBUG) std::cout << " MC bkg scaled by POT for " << variable << std::endl;
 
    
    
 

      // HACK as the response seems to have gotten the wrong normalization
    //  double fix = imcsighist->Integral()/iresponse->ProjectionX()->Integral();
    //  iresponse->Scale(fix);
    //  if (DEBUG) std::cout << " HACK? response scaled by " << fix << " for " << iresponse->GetName() << "POTScale would be "<< POTScale<< std::endl;
    

    //==================================Make MC=====================================
    MnvHistoType* mc;
    MnvHistoType* signalFraction;
    
      if (!hasbkgsub){
          if (DEBUG) std::cout << " Start MakeMC... " << std::endl;
          // std::string mcname = basename+"_mc_tot";
          mc = MakeMC(basename,imcsighist,imcbkghist);
          if(DEBUG)mc->Print();
          mc->Write();
          
         
          PlotCVAndError(canvas,idatahist,mc,stuned+sample + "_"+ "DATA_vs_MC" ,true,logscale,binwid);
          PlotErrorSummary(canvas,mc,sample + "_"+"Raw MC Systematics" ,logscale );
          
          //================================Signal Fraction===========================
          
          if (DEBUG) std::cout << " Start signal fraction... " << std::endl;
          // std::string fracname = basename+"_signalfraction";
          signalFraction = GetSignalFraction(basename,imcsighist,mc);
          MnvHistoType* bkgFraction = GetBkgFraction(basename,imcbkghist,mc);
          if(DEBUG) signalFraction->Print();
          signalFraction->Write();
          bkgFraction->Write();
          Plot2DFraction(canvas, signalFraction,bkgFraction, stuned+sample + "_fractions",logscale);
          
          PlotCVAndError(canvas,signalFraction,signalFraction, stuned+sample + "_"+"Signal Fraction" ,true,logscale,false);
          PlotErrorSummary(canvas,signalFraction,stuned+sample+" Signal Fraction Systematics" ,0);
      }
      else{
          mc = (MnvHistoType*)imcsighist->Clone();
          
          
      }
    

    //============================Background Subtraction========================

    if (DEBUG) std::cout << " Start background subtraction... " << std::endl;
    // std::string bkgsubname = basename+"_bkgsub";;
    MnvHistoType* bkgsub;
    if (hasbkgsub){
      if (ibkgsubhist){
        bkgsub=(MnvHistoType*)ibkgsubhist->Clone((basename+"_bkgsub").c_str());
      }
      else{
        std::cout << " failed to find background histogram" << std::endl;
        exit(0);
      }
    }
    else{
       bkgsub = DoBkgSubtraction(basename,idatahist,mc,signalFraction);
    }
    if(DEBUG)bkgsub->Print();
      bkgsub->Write();
 
    
    PlotCVAndError(canvas,bkgsub,imcsighist, stuned+sample + "_"+"BKGsub vs. MC signal" ,true,logscale,binwid);
    PlotErrorSummary(canvas,bkgsub,stuned+sample + "_"+"BKGsub Systematics" ,0);

    //==================================Unfolding===============================

    if (DEBUG) std::cout << " Start unfolding... " << std::endl;
    // std::string unsmearedname = bkgsubname+"_unfolded";
    // std::string unsmearingname = basename+"_unsmearing";
    MnvHistoType* unsmeared;
    // change this to use
    std::vector<MnvHistoType*> unsmearedVec = DoUnfolding(basename,iresponse,iresponse_reco,iresponse_truth,bkgsub,idatahist,unfold,num_iter);

    std::cout << "Unfolding Vector Size: " << unsmearedVec.size() << std::endl;
    if(unsmearedVec.size()==0){
        std::cout << " No unfolding. Exiting now. " << std::endl;
        return 0;
    }
    if(unsmearedVec.size()>0){
      // Output for Bayesian unfolding, does not include the "unsmearing"
      unsmeared = unsmearedVec[0];
      if (DEBUG) unsmeared->Print();
      unsmeared->Write();
      PlotCVAndError(canvas,bkgsub,unsmeared,stuned+sample + "_"+"Data Before and After Unsmearing", true,logscale,binwid); 
      
    }
    if(unsmearedVec.size()==2){
      // Output for crude ratio unfolding, DOES include "unsmearing" hist, so this picks that up
      MnvHistoType* unsmearing = unsmearedVec[1];
      if (DEBUG) unsmearing->Print();
      unsmearing->Write();
      // PlotCVAndError(canvas,imcsighist,iseltruhist,"Fractional Unfolding" ,true,logscale,binwid);
    }

    PlotCVAndError(canvas,unsmeared,iseltruhist,stuned+sample + "_"+ "Unsmeared Data Compared to Selected MC" ,true,logscale,binwid);
    PlotErrorSummary(canvas,unsmeared,stuned+sample + "_"+"Unsmeared Data Systematics" ,0);

    //==================================Efficiency==============================

    if (DEBUG) std::cout << " Start efficiency correction... " << std::endl;
    if (iseltruhist == 0){
      std::cout << " No efficiency numerator. Stopping here." << std::endl;
      return 2;
    }
    if (ialltruhist == 0){
      std::cout << " No efficiency denominator. Stopping here." << std::endl;
      return 2;
    }
    bool fluxhere = false;  // this was just a test to see if using bin by bin to see the error might be interesting.
    std::vector<MnvHistoType*> vecEffCorr = DoEfficiencyCorrection(basename, unsmeared, iseltruhist, ialltruhist, fluxhere);
    if (fluxhere){
      h_flux_dewidthed->PopVertErrorBand("Flux");
    }
    MnvHistoType* effcorr = vecEffCorr[0];
    if (DEBUG) effcorr->Print();
    effcorr->Write();
    MnvHistoType* efficiency = vecEffCorr[1];
    if (DEBUG) efficiency->Print();
    efficiency->Write();
    PlotCVAndError(canvas,iseltruhist,ialltruhist, stuned+sample + "_"+"efficiency: selected and true" ,true,logscale,binwid);
    PlotCVAndError(canvas,effcorr,ialltruhist,stuned+ sample + "_"+"effcorr data vs truth" ,true,logscale,binwid);
    PlotErrorSummary(canvas,efficiency,stuned+sample + "_"+"Efficiency Factor Systematics" ,0);
    PlotErrorSummary(canvas,effcorr,stuned+sample + "_"+"Efficiency Corrected Data Systematics" ,0);
    
    //============================POT/Flux Normalization========================
    // bool energydep = false;
    // bool energydepx = false;
    // bool energydepy = false;
    // //TODO: may need to check where this is originally defined.
    //
    if (DEBUG) std::cout << " Start normalization... " << std::endl;
    // // This checks if you need to use an energy dependent flux, and sets binwidth
    // // corrections needed for plotting.
    // if(variable.find("enuQE")==std::string::npos && variable.find("EnuHad")==std::string::npos && variable.find("EnuCCQE")==std::string::npos){
    //   std::cout << " Using a flat flux. " << std::endl;
    //   energydep = false;
    // }
    // else{
    //   std::cout << " Using an energy dependent flux. ";
    //   energydep = true;
    // }
    // binwid = energydep;
      // hack in a varsFile if it does not exist 
      if (!(configs.count("varsFile")>0)){
  
          // backwards compatibility change a file read into a configmap
          NuConfig* vars = new NuConfig();
          vars->Read(configs["main"]->GetString("varsFile"));
          configs["varsFile"]=vars;
          
      }
      std::map< std::string, bool> fluxnorm = CheckFluxNorm(configs["varsFile"],variable);
    if(DEBUG) std::cout << " fluxnorm: " << fluxnorm["fluxnorm"] << ", xfluxnorm: " << fluxnorm["xfluxnorm"] << ", yfluxnorm: " << fluxnorm["yfluxnorm"] << std::endl;
    
    // HMS dec-1-2021 - flip these? 
    if (fluxnorm["fluxnorm"]) {
      binwid =  true;
    }
    if (!fluxnorm["fluxnorm"]) {
      binwid = true;
    }
    
   

    std::vector<MnvHistoType*> sigmaVec = DoNormalization(configs,basename,fluxnorm,norm,effcorr,ialltruhist,h_flux_dewidthed);
    MnvHistoType* sigma = sigmaVec[0];
    sigma->Write();
    sigma->Print();
    if(DEBUG) sigma->Print("ALL");

    MnvHistoType* sigmaMC = sigmaVec[1];
    sigmaMC->Write();
    sigmaMC->Print();

    PlotCVAndError(canvas,sigma,sigmaMC, stuned+sample + "_"+"sigma" ,true,logscale,binwid);
    PlotErrorSummary(canvas,sigma,stuned+sample + "_"+"Cross Section Systematics" ,0);
    

    //============================Binwidth Normalization============================
    // Just a check on bin width corrections...
    double id = integrator(sigma,binwid);
    double im = integrator(sigmaMC,binwid);
    std::cout << "sigma " << variable << " " << id << " " << sigma->Integral() << " " << im << " " << sigmaMC->Integral() << std::endl;
    std::cout << " end of loop over types " << std::endl;

    //=====================================Exit======================================
    return 0;
  }

template int GetCrossSection<MnvH1D>(std::string sample, std::string variable, std::string basename,
                                     std::map< std::string, std::map <std::string, MnvH1D*> > histsND,
                                     std::map< std::string, std::map <std::string, MnvH2D*> > responseND,
                                     std::map< const std::string, NuConfig *> configs, TCanvas & canvas, double norm, double POTScale,  MnvH1D* h_flux_dewidthed,
                                     MinervaUnfold::MnvUnfold unfold, double num_iter, bool DEBUG=false, bool hasbksub=false, bool usetune=false);

template int GetCrossSection<MnvH2D>(std::string sample, std::string variable, std::string basename,
                                     std::map< std::string, std::map <std::string, MnvH2D*> > histsND,
                                     std::map< std::string, std::map <std::string, MnvH2D*> > responseND,
                                     std::map< const std::string, NuConfig *> configs, TCanvas & canvas, double norm, double POTScale,  MnvH1D* h_flux_dewidthed,
                                     MinervaUnfold::MnvUnfold unfold, double num_iter, bool DEBUG=false,bool hasbksub=false, bool usetune = false);

template int GetCrossSection<MnvH1D>(std::string sample, std::string variable, std::string basename,
                                     std::map< std::string, std::map <std::string, MnvH1D*> > histsND,
                                     std::map< std::string, std::map <std::string, MnvH2D*> > responseND,
                                     NuConfig mainconfig, TCanvas & canvas, double norm, double POTScale,  MnvH1D* h_flux_dewidthed,
                                     MinervaUnfold::MnvUnfold unfold, double num_iter, bool DEBUG=false, bool hasbksub=false, bool usetune=false);

template int GetCrossSection<MnvH2D>(std::string sample, std::string variable, std::string basename,
                                     std::map< std::string, std::map <std::string, MnvH2D*> > histsND,
                                     std::map< std::string, std::map <std::string, MnvH2D*> > responseND,
                                     NuConfig mainconfig, TCanvas & canvas, double norm, double POTScale, MnvH1D* h_flux_dewidthed,
                                     MinervaUnfold::MnvUnfold unfold, double num_iter, bool DEBUG=false,bool hasbksub=false, bool usetune = false);


