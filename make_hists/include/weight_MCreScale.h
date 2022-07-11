#ifndef weight_mcrescale_h
#define weight_mcrescale_h

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


namespace PlotUtils{
// template <typename T>
  class weight_MCreScale{
    public:
      // Constructor that reads in hists from file
      weight_MCreScale(const TString f);

      // Constructor that reads in hists from file and sets the tag
      // weight_MCreScale(std::string tag, TString filename);
      // std::string m_tag;

      // Boolean set based off tag
      bool isSignal;

      // Member file with scale/fraction MnvH1Ds
      TFile* f_Q2QEScaleFrac;

      // Member MnvH1D's for each scale from the file (set at initialization)
      // TODO: turn these into a map to allow for more bkg channels for Sean's analysis
      MnvH1D* mnvh_SigScale;
      MnvH1D* mnvh_BkgScale;

      // Member scale set to be sig or bkg (set at GetWeight)
      MnvH1D* mnvh_Scale;
      TH1D* h_scale;

      double getScale(std::string tag, const double q2qe, std::string uni_name, int iuniv); // q2qe in GeV2
      // double getFrac(std::string sigbkg, const double q2qe); // q2qe in GeV2
      void read(TString filename);
      void SetTag(std::string tag);

    private:
      double getScaleInternal(const double q2qe, std::string uni_name, int iuniv);
  };

}

#endif
