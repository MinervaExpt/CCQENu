#include <fstream>  //ifstream
#include <iostream> //cout

#include <TString.h>
// #include <TH3D.h>
// #include <TH2D.h>
#include <TH1D.h>
#include <TFile.h>
#include <cmath>
#include <cassert>
// #include <TF1.h>
#include "include/CVUniverse.h"
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvVertErrorBand.h"
#include "weight_MCreScale.h"
#include "utils/NuConfig.h"
#include "utils/expandEnv.h"
// #include "TRandom.h"

using namespace PlotUtils;

weight_MCreScale::weight_MCreScale(TString filename){
  read(filename);
  // m_useTuned=true;
  m_tunedmc="both";
}

weight_MCreScale::weight_MCreScale(const NuConfig config){
  std::string filename = "${CCQEMAT}/data/BkgStudy6A_BkgStudy_1_OutVals_fix.root";
  if(config.IsMember("scalefileIn")){
    filename=config.GetString("scalefileIn");
  }
  else{
    std::cout << "weight_MCreScale: 'scalefileIn' not configured in main. Setting to default (may cause issues if running outside of CCQENu/make_hists) " << std::endl;
  }
  if(config.IsMember("tunedmc"))
  {
    m_tunedmc = config.GetString("tunedmc");
    if(m_tunedmc != "untuned")
      m_useTuned = true;
  }
  if (config.IsMember("useTuned"))
    m_useTuned = config.GetBool("useTuned");

  if(config.IsMember("TuneCategories")){
    m_categories = config.GetStringVector("TuneCategories");
  }
  else{
    m_categories = {"qelike","qelikenot"};
  }
  
  if(m_useTuned){
    read(filename);
  }
  
}


void weight_MCreScale::read(TString filename){

  m_f_Q2QEScaleFrac = TFile::Open(filename,"READ");
  if(m_f_Q2QEScaleFrac){
    std::cout << "weight_MCreScale: I'm using this scale file " << filename << std::endl;
    for (auto cat:m_categories){
      std::string name = "h___Background___"+cat+"___Q2QE___scale";
      m_mnvh_Scales[cat] = (MnvH1D*)m_f_Q2QEScaleFrac->Get(name.c_str());
   }
  }
  else{
    std::cout << "weight_MCreScale::read: WARNING: Cannot find input file for weight_MCreScale: " << filename << std::endl;
    std::cout << "                                 Defaulting to no tuning." << std::endl;
    m_useTuned = false;
  }
  if (m_mnvh_Scales.size() < 1){
    std::cout << "weight_MCreScale: failed to find signal or background scale fractions in "  << filename << std::endl;
    exit(1);
  }
}

void weight_MCreScale::SetCat(std::string cat){
  //isSignal = -1;
  if (std::find(m_categories.begin(), m_categories.end(), cat ) == m_categories.end()){
    //std::cout << " can't find this category for mcrescale " << cat << std::endl;
    m_category = "None";
    return;
  }
  m_category = cat;

  m_mnvh_Scale = m_mnvh_Scales[cat];
  //
  // if(Cat.find("qelikenot")!=std::string::npos){
  //   isSignal = 0;
  //   mnvh_Scale = mnvh_BkgScale;
  // }
  // else if(Cat.find("qelike")!=std::string::npos){
  //   isSignal = 1;
  //   mnvh_Scale = mnvh_SigScale;
  // }
}


double weight_MCreScale::GetScaleInternal(const double q2qe, std::string uni_name, int iuniv){
  double retval = 1.;
  double checkval = q2qe;
  int xbin = -1;

  // See if signal or bkg, then set mnvh to be
  // if(isSignal>0){
  //   mnvh_Scale = mnvh_SigScale;
  // }
  // else if (isSignal==0){
  //   mnvh_Scale = mnvh_BkgScale;
  // }
  // else{
  if(m_category == "None"){
    std::cout << "weight_MCreScale: This variable is not recognized as qelike or qelikenot. Returning 1.0."<< std::endl;
    return 1.0;
  }

  if(q2qe<0.){
    std::cout << "weight_MCreScale: You have a q2qe passed less than 0. Non-physical. Returning 1.0"<< std::endl;
    return 1.0;
  }
  // else if(q2qe>=2.0){
  else if(m_mnvh_Scale->FindFirstBinAbove(q2qe)<0){
    // Q2 is fit up to 2.0 GeV^2 (as of 7/11/22), but some events have higher values. -NHV
    checkval = 1.99;
  }

  xbin = m_mnvh_Scale->GetXaxis()->FindBin(checkval);
  static int errcount = 0;
  TH1D *hcv = (TH1D*)m_mnvh_Scale;
  if (uni_name=="cv" || uni_name=="CV") {
    // h_scale = (TH1D*)mnvh_Scale->GetCVHistoWithStatError();
    m_h_scale = hcv;
    // double s = hcv->GetBinError(xbin);
    // double x = TRandom::Gaus(0.0,1.0);
  }
  else{  // check to see that error band exists
    if (m_mnvh_Scale->HasVertErrorBand(uni_name) && iuniv < m_mnvh_Scale->GetVertErrorBand(uni_name)->GetNHists()){

      m_h_scale = (TH1D*)m_mnvh_Scale->GetVertErrorBand(uni_name)->GetHist(iuniv);
    // std::cout << "weight_MCreScale: pulling out error band " << uni_name << std::endl;
    }
    else{
      errcount ++;
      if (!m_mnvh_Scale->HasVertErrorBand(uni_name)){
        if(errcount < 100) std::cout << " MCreScale could not find error band  " << uni_name << " at all, returning CV" << std::endl;
        m_h_scale = hcv;
        return m_h_scale->GetBinContent(xbin);
      }
      if (iuniv >= m_mnvh_Scale->GetVertErrorBand(uni_name)->GetNHists()){
        if (errcount < 100) std::cout << " MCreScale could not find " << uni_name << " error band # " << iuniv << " you need to set requested number to value <= " << m_mnvh_Scale->GetVertErrorBand(uni_name)->GetNHists() << std::endl;
        assert(0);
      }
    }
  }
  retval = m_h_scale->GetBinContent(xbin);
  // std::cout << "weight_MCreScale: Finished error band " << uni_name << std::endl;
  return retval;
}

// Returns a scale factor. If it's not set up, it returns -1 (which isn't possible).
double weight_MCreScale::GetScale(std::string cat, const double q2qe, std::string uni_name, int iuniv){
  // Default value, not physical. Checked so you can switch scaling on and off easier.
  double retval = -1.;
  if(m_useTuned){
    SetCat(cat);
    retval = GetScaleInternal(q2qe, uni_name, iuniv);
  }

  return retval;
}

// This one takes a universe and gets the q2qe value internally. This can save
// some time maybe? Especially for events where this isn't necessary.
double weight_MCreScale::GetScale(std::string cat, const CVUniverse* univ, std::string uni_name, int iuniv){
  // Default value, not physical. Checked so you can switch scaling on and off easier.
  double retval = -1.;
  if(m_useTuned){
    const double q2qe = univ->GetQ2QEGeV();
    SetCat(cat);
    retval = GetScaleInternal(q2qe, uni_name, iuniv);
  }

  return retval;
}
