#ifndef weight_warper_h
#define weight_warper_h
// =============================================================================
// weight_warper.h
// Used to make custom warps, based off weight_MCreScale that rescales events for
// background constraint. This will take in a specific type of config file that
// the user specifies in their main config. It is is general purpose, so should
// be able to make warps based off certain classifications of events. The config
// can be used to specify:
//     - Which events to weight based off specified values e.g., mcinttype, nfsp
//     - Values to weight events by, direclty specified in config
//     - A file containing a TF1 or TH1D containing weights for events
// This does not replace the methods used for implementing new model tunes
// e.g., MnvTunev2, AMU tune, 2p2h enhancement, etc.. Those need to be built
// in the typical way.
//
// Noah Harvey Vaughan (they/them). April 2025
// Oregon State University
// vaughann@oregonstate.edu
// noah.vaughan31@gmail.com
// =============================================================================

#include <TString.h>

#include <cassert>
#include <cmath>
#include <fstream>   //ifstream
#include <iostream>  //cout
#include <map>
#include <string>
#include <vector>
// #include <TH3D.h>
// #include <TH2D.h>
#include <TF1.h>
#include <TFile.h>
#include <TH1D.h>

#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvVertErrorBand.h"
#include "include/CVUniverse.h"
#include "include/CVFunctions.h"
#include "utils/NuConfig.h"
#include "utils/expandEnv.h"

namespace PlotUtils {
// template <typename T>
class weight_warper {
   private:
    typedef std::function<double(const CVUniverse&)> PointerToCVUniverseFunction;

    // These are pointers to various functions to use when checking classification of event
    std::map<std::string, PointerToCVUniverseFunction> m_fun_pointer_map;

    // This is the pointer for hte function warped over 
    PointerToCVUniverseFunction m_warpvar_fun_pointer; 
   public:
    NuConfig m_warp_config;
    std::string m_warp_type;
    std::string m_category;

    // this is the variable that the warp is dependent on, the weighter will check the value of the univ and look up a corresponding weight
    // TODO: this probably should be a PointerToUniverseFunction type thing
    std::string warpvar;

    std::map<std::string, PlotUtils::subwarp*> m_subwarps;



    // tunedmc set from config. Can be "tuned", "untuned", or "both". Default to false to avoid issues if not tuning.
    std::string m_tunedmc = "untuned";

    // Member file with scale/fraction MnvH1Ds
    TFile* m_f_ScaleFrac;
    std::vector<std::string> m_categories;
    // Member MnvH1D's for each scale from the file (set at initialization)
    std::map<const std::string, MnvH1D*> m_mnvh_Scales;
    // Map detailing all the minima and maxima for each category's scale hist to check
    std::map<const std::string, std::vector<double>> m_scale_minmax;
    // Member scale set to be sig or bkg (set at GetWeight)
    MnvH1D* m_mnvh_Scale;
    TH1D* m_h_scale; // Used as scale factors, should include all the categories you want to warp
    TF1* m_f_scale; // If you're using a TF1 instead, use this
    std::string m_category;

   public:
    // Constructor that reads in hists from file and sets the Cat
    weight_warper(const NuConfig config);

    void SetSubwarps(NuConfig subwarp_config);

    int CheckSubwarp(const CVUniverse& univ, subwarp* subwarp);
    double GetWarpWeight(const CVUniverse& univ, std::string univ_name, int iuniv);
};

// This is a class that contains a series of checks and the warp corresponding to that set
class subwarp {
   private:
    typedef std::function<double(const CVUniverse&)> PointerToCVUniverseFunction; 
   public:
    subwarp(const NuConfig);

    std::string m_warpname;
    std::string m_warpvar;
    std::vector<std::string> m_checkvars;

    std::map<std::string, double> equals;
    std::map<std::string, double> min;
    std::map<std::string, double> max;

    PointerToCVUniverseFunction m_warpvar_fun_pointer;

    // If straight normalization for this warp, can use this
    double m_warpval = -1.0;

    // If using a function or hist for this warp, set this
    TF1* m_warpfunct;
    MnvH1D* m_warphist;

    EHistFunct warptype;

   public:
    int CheckVal(std::string varname, double value);

    double GetWarpWeight(double warpvar_val);
    double GetWarpWeight(const CVUniverse& univ);

    std::vector<std::string> GetCheckVars();

   private:
    void SetWarpFunct(TString warp_filename, std::string warp_functname);
    void SetWarpHist(TString warp_filename, std::string warp_histname);
}; 

enum EHistFunct {
    kHistWarp = 0,
    kFunctWarp = 1 };


}  // namespace PlotUtils

#endif
