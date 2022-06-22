#ifndef weight_mcrescale_h
#define weight_mcrescale_h

#include <fstream>  //ifstream
#include <iostream> //cout

#include <TString.h>
// #include <TH3D.h>
#include <TH2D.h>
#include <TH1D.h>
#include <TFile.h>
#include <cmath>
#include <cassert>
#include <TF1.h>
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvVertErrorBand.h"
#include "weight_MCreScale.h"

using namespace PlotUtils;
void weight_MCreScale::read(TString filename){
  f_Q2QEScaleFrac = TFile::Open(filename,"READONLY");
  if(f_Q2QEScaleFrac){
    h_SigScale = (MnvH1D*)f_Q2QEScaleFrac->Get("h___QELike___qelike___Q2QE___scale");
    h_BkgScale = (MnvH1D*)f_Q2QEScaleFrac->Get("h___QELike___qelikenot___Q2QE___scale");
  }
  else{
    std::cout << "Bad file input for weight_MCreScale. Try again" << std::endl;
    exit(1);

  }
}

double weight_MCreScale::getScaleInternal(/*std::string sigbkg, */ const double q2qe, std::string uni_name, std::int uni_index){
  double retval = 1.;
  double checkval = q2qe;
  MnvH1D* mnvh_scale;
  TH1D* h_scale;
  // if (sigbkg==ksig){
  //   mnvh_scale = h_SigScale;
  // }
  // else if (sigbkg==kbkg){
  //   mnvh_scale = h_BkgScale;
  // }
  mnvh_scale = h_SigScale;
  if(q2qe<0){
    std::cout << "You have a q2qe passed to weight_minervaq2qe less than 0. Non-physical. Returning 1.0"<< std::endl;
    return 1.0;
  }

  if (uni_name=="cv" || uni_name=="CV") {
    h_scale = mnvh_scale->GetCVHistoWithStatError()
  }
  else{
    h_scale = mnvh_scale->GetVertErrorBand(uni_name)->GetHist(uni_index);
  }

  xbin = h_scale->GetXaxis()->FindBin(checkval);

  retval = h_scale.GetBinValue(xbin);
  return retval;
}

double weight_MCreScale::getScale(/*std::string sigbkg, */const double q2qe, std::string uni_name, std::int uni_index==1){
  return getScaleInternal(/*sigbkg, */q2qe, uni_name, uni_index);
}
