#ifndef XSEC_CXX
#define XSEC_CXX
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

#include "include/XSec.h"
#include "XSec.h"
using namespace CCQENu;
template <class MnvHistoType>
XSec<MnvHistoType>::XSec(){}

template <class MnvHistoType>
XSec<MnvHistoType>::XSec(NuConfig* config) {
    
}

template <class MnvHistoType>
void XSec<MnvHistoType>::SetNames(std::string basename, std::string sample, std::string variable) {
    m_basename = basename;
    m_sample = sample;
    m_variable = variable;
}


template <class MnvHistoType>
void XSec<MnvHistoType>::SetDataMCTruthHists(MnvHistoType* data_hist, 
                                             MnvHistoType* mc_bkg_hist, MnvHistoType* mc_sig_hist,
                                             MnvHistoType* sel_truth_hist, MnvHistoType* all_truth_hist) {
    m_data_hist = data_hist.Clone();
    m_mc_bkg_hist = mc_bkg_hist.Clone();
    m_mc_sig_hist = mc_sig_hist.Clone();
    m_sel_truth_hist = sel_truth_hist.Clone();
    m_all_truth_hist = all_truth_hist.Clone();
}

template <class MnvHistoType>
void CCQENu::XSec<MnvHistoType>::SetResponse(MnvH2D* response) {
    m_response = response.Clone();
}

template <class MnvHistoType>
void XSec<MnvHistoType>::SetUnfold(MinervaUnfold::MnvUnfold unfold) {
    m_unfold = unfold;
}

template <class MnvHistoType>
void CCQENu::XSec<MnvHistoType>::SetFluxHist(MnvH1D* flux_hist) {
    m_flux_hist = flux_hist.Clone();
}

template <class MnvHistoType>
void CCQENu::XSec<MnvHistoType>::SetFluxHist(MnvH2D* response) {
}

template <class MnvHistoType>
void XSec<MnvHistoType>::MakeMCtot() {
    std::string mc_tot_name = m_name + "_mc_tot";
    m_mc_tot_hist = (MnvHistoType*)m_mc_sig_hist.Clone(mc_tot_name.c_str());
    m_mc_tot_hist->SetDirectory(0);
    m_mc_tot_hist->Add(m_mc_bkg_hist.Clone());
    m_mc_tot_hist.SyncBands();
}

template <class MnvHistoType>
void XSec<MnvHistoType>::SubtractBackground() {
    std::string bkg_sub_name = m_name + "_bkgsub";
    m_bkgsub_hist = (MnvHistoType*)m_data_hist.Clone(bkg_sub_name.cstr());
    m_mc_tot_hist->SetDirectory(0);
    m_bkgsubhist->Add(m_mc_bkg_hist.Clone(),-1);
    m_bkgsubhist.SyncBands();
}

template <class MnvHistoType>
void XSec<MnvHistoType>::DoUnfolding() {
}

template <class MnvHistoType>
void XSec<MnvHistoType>::DoEfficiencyCorrection() {
}

template <class MnvHistoType>
void XSec<MnvHistoType>::FluxNormalize() {
}

template <class MnvHistoType>
void XSec<MnvHistoType>::TargetNormalize() {
}

template <class MnvHistoType>
void XSec<MnvHistoType>::POTNormalize() {
}

#endif // XSEC_CXX
