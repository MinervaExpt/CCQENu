#ifndef XSEC_H
#define XSEC_H
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

#include "MinervaUnfold/MnvResponse.h"
#include "MinervaUnfold/MnvUnfold.h"
#include "PlotUtils/FluxReweighter.h"
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "TCanvas.h"
#include "TF2.h"
#include "TH2D.h"
#include "utils/NuConfig.h"
#include "utils/RebinFlux.h"
#include "utils/SyncBands.h"

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
namespace CCQENu {
template <class MnvHistoType>
class XSec {
   public:
    XSec();
    XSec(NuConfig* config);

    std::string m_name;
    std::string m_base_name;
    std::string m_variable_name;
    std::string m_sample_name;

    NuConfig* m_main_config;
    std::string m_tunedmc;

   private:
    // Data hists, from raw event rates to x-section
    MnvHistoType* m_data_hist;
    MnvHistoType* m_bkgsub_hist;
    MnvHistoType* m_unfolded_hist;
    MnvHistoType* m_effcorr_hist;
    MnvHistoType* m_sigma_hist;

    // Reconstructed MC hists
    MnvHistoType* m_mc_sig_hist;
    MnvHistoType* m_mc_bkg_hist;
    MnvHistoType* m_mc_tot_hist;

    // Truth MC hists, including x-section
    MnvHistoType* m_sel_truth_hist;
    MnvHistoType* m_all_truth_hist;
    MnvHistoType* m_sigma_mc;

    // Response and unfolding objectects
    MnvH2D* m_response;
    MinervaUnfold::MnvUnfold m_unfold;

    // Flux hists
    MnvH1D* m_flux_hist;
    MnvHistoType* m_flux_ebins;
    MnvHistoType* m_flux_varbins;

   public:
    // Canvas things get printed to
    TCanvas& m_canvas;

    // Methods
    void SetNames(std::string basename, std::string sample, std::string variable);

    void SetDataMCTruthHists(MnvHistoType* data_hist, 
                             MnvHistoType* mc_bkg_hist, MnvHistoType* mc_sig_hist,
                             MnvHistoType* sel_truth_hist, MnvHistoType* all_truth_hist);

    void SetResponse(MnvH2D* response);
    void SetUnfold(MinervaUnfold::MnvUnfold unfold);

    void SetFluxHist(MnvH1D* flux_hist)

    void MakeMCtot();
    void SubtractBackground();
    void DoUnfolding();
    void DoEfficiencyCorrection();
    void FluxNormalize();
    void TargetNormalize();
    void POTNormalize();
    // Helpers
    std::vector<std::string> split(std::string s, std::string delimiter);
    TMatrixD ZeroDiagonal(const TMatrixD& m);
    std::map<std::string, bool> CheckFluxNorm(NuConfig* configvar, std::string variable);
}  // class CrossSection
}  // namespace CCQENu

#endif //XSEC_H