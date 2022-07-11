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
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvVertErrorBand.h"
#include "weight_MCreScale.h"
// #include "TRandom.h"

using namespace PlotUtils;

weight_MCreScale::weight_MCreScale(TString filename){
  read(filename);
}

// weight_MCreScale::weight_MCreScale(std::string tag, TString filename){
//   read(filename);
//   SetTag(tag);
// }

void weight_MCreScale::read(TString filename){

  f_Q2QEScaleFrac = TFile::Open(filename,"READONLY");
  if(f_Q2QEScaleFrac){
    mnvh_SigScale = (MnvH1D*)f_Q2QEScaleFrac->Get("h___QELike___qelike___Q2QE___scale");
    mnvh_BkgScale = (MnvH1D*)f_Q2QEScaleFrac->Get("h___QELike___qelikenot___Q2QE___scale");
  }
  else{
    std::cout << "weight_MCreScale: Bad file input for weight_MCreScale. Try again." << std::endl;
    exit(1);

  }
}

void weight_MCreScale::SetTag(std::string tag){
  isSignal = -1;

  if(tag.find("qelikenot")!=std::string::npos){
    isSignal = 0;
  }
  else if(tag.find("qelike")!=std::string::npos){
    isSignal = 1;
  }
}


double weight_MCreScale::getScaleInternal(const double q2qe, std::string uni_name, int iuniv){
  double retval = 1.;
  double checkval = q2qe;
  int xbin = -1;

  // See if signal or bkg, then set mnvh to be
  if(isSignal>0){
    mnvh_Scale = mnvh_SigScale;
  }
  else if (isSignal==0){
    mnvh_Scale = mnvh_BkgScale;
  }
  else{
    std::cout << "weight_MCreScale: This variable is not recognized as qelike or qelikenot. Returning 1.0."<< std::endl;
    return 1.0;
  }

  if(q2qe<0){
    std::cout << "weight_MCreScale: You have a q2qe passed to weight_minervaq2qe less than 0. Non-physical. Returning 1.0"<< std::endl;
    return 1.0;
  }
  else if(q2qe>=2.0){
    // Q2 is fit up to 2.0 GeV^2 (as of 7/11/22), but some events have higher values. -NHV
    checkval = 1.99;
  }

  xbin = mnvh_Scale->GetXaxis()->FindBin(checkval);

  if (uni_name=="cv" || uni_name=="CV") {
    // h_scale = (TH1D*)mnvh_Scale->GetCVHistoWithStatError();
    TH1D *hcv = (TH1D*)mnvh_Scale;
    h_scale = hcv;
    // double s = hcv->GetBinError(xbin);
    // double x = TRandom::Gaus(0.0,1.0);
  }
  else{
    h_scale = (TH1D*)mnvh_Scale->GetVertErrorBand(uni_name)->GetHist(iuniv);
    // std::cout << "weight_MCreScale: pulling out error band " << uni_name << std::endl;
  }


  retval = h_scale->GetBinContent(xbin);
  // std::cout << "weight_MCreScale: Finished error band " << uni_name << std::endl;
  return retval;
}

double weight_MCreScale::getScale(std::string tag, const double q2qe, std::string uni_name, int iuniv){
  SetTag(tag);
  return getScaleInternal(q2qe, uni_name, iuniv);
}
