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


namespace PlotUtils{

  class scale_bkgtune
  {
    public:
      // Default constructor

      scale_bkgtune(const TString f){ read(f); } // Read in all relevant MnvH1Ds

      // Member file with scale/fraction MnvH1Ds
      Tfile* f_Q2QEScaleFrac

      // Member histograms for each scale/frac from file
      MnvH1D* h_SigScale
      // MnvH1D* h_SigFrac
      MnvH1D* h_BkgScale
      // MnvH1D* h_BkgFrac
      // TODO: Add in fraction funcionality

      double getScale(/*std::string sigbkg, */const double q2qe, std::string uni_name, std::int uni_index); // q2qe in GeV2

      // double getFrac(std::string sigbkg, const double q2qe); // q2qe in GeV2

      void read(TString filename);

  private:
      double getScaleInternal(/*std::string sigbkg, */const double q2qe, const MnvH1D* hist, std::string uni_name, std::int uni_index);


  };

}

#endif
