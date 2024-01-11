#ifndef weight_mcrescale_h
#define weight_mcrescale_h

#include <fstream>  //ifstream
#include <iostream> //cout
#include <cmath>
#include <cassert>
#include <vector>
#include <map>
#include <string> 
#include <TString.h>
// #include <TH3D.h>
// #include <TH2D.h>
#include "include/CVUniverse.h"
#include <TH1D.h>
#include <TFile.h>

// #include <TF1.h>
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvVertErrorBand.h"
#include "utils/NuConfig.h"
#include "utils/expandEnv.h"


namespace PlotUtils{
// template <typename T>
  class weight_MCreScale{
    public:
      // tunedmc set from config. Can be "tuned", "untuned", or "both". Default to false to avoid issues if not tuning.
      std::string m_tunedmc = "untuned";

      // Member file with scale/fraction MnvH1Ds
      TFile* m_f_Q2QEScaleFrac;
      std::vector<std::string> m_categories;
      // Member MnvH1D's for each scale from the file (set at initialization)
      std::map<const std::string, MnvH1D*> m_mnvh_Scales;
      // Member scale set to be sig or bkg (set at GetWeight)
      MnvH1D* m_mnvh_Scale;
      TH1D* m_h_scale;
      std::string m_category;

    public:
      // Constructor that reads in hists from file
      weight_MCreScale(const TString f);
      // Constructor that reads in hists from file and sets the Cat
      weight_MCreScale(const NuConfig config);

      double GetScale(std::string cat, const double q2qe, std::string uni_name, int iuniv); // q2qe in GeV2
      double GetScale(std::string cat, const CVUniverse* univ, std::string uni_name, int iuniv);

      void read(TString filename);
      void SetCat(std::string cat);

    private:
      double GetScaleInternal(const double q2qe, std::string uni_name, int iuniv);
  };

}

#endif
