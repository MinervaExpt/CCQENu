#include <TString.h>

#include <fstream>   //ifstream
#include <iostream>  //cout
// #include <TH3D.h>
// #include <TH2D.h>
#include <TFile.h>
#include <TH1D.h>

#include <cassert>
#include <cmath>
// #include <TF1.h>
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvVertErrorBand.h"
#include "include/CVUniverse.h"
#include "include/CVFunctions.h"
#include "utils/NuConfig.h"
#include "utils/expandEnv.h"
#include "weight_warper.h"
// #include "TRandom.h"

using namespace PlotUtils;

weight_warper::weight_warper(const NuConfig config) {
    // Check if you want to do the warp, m_dowarp is a switch to turn this mechanism on & defaults to false, can set to other values to be used in other places for model warps
    if(config.IsMember("warpedmc")) {
        m_warpedmc = config.GetString("warpedmc");
    }
    if(config.IsMember("warpedmc")) {
        if(config.GetString("warpedmc")=="warped" || config.GetString("warpedmc")=="both" || config.GetString("warpedmc")=="custom") {
            m_dowarp = true;
            std::cout << "dowarp set to true" << std::endl;
        } else {
            std::cout << "dowarp set to false" << std::endl;
        }
    }

    if (m_dowarp) {
        // Assumes you're feeding a main config
        NuConfig warpdriver_config;
        warpdriver_config.Read(config.GetString("warpdriverFile"));
        // Dummy to take care of function stuff
        CVFunctions<CVUniverse> fun;

        // These are used to store the function pointer names. Need to do truth and Reco separate bc the getters are different.
        std::vector<std::string> recovars;
        std::vector<std::string> truevars;

        // Set the tag if you have it config'd, defaults to "warped"
        if (warpdriver_config.IsMember("tag")) {
            m_tag = warpdriver_config.GetString("tag");
            std::cout << "weight_warper: tag set to " << m_tag << std::endl; 
        }

        // From the config, set up the subwarps and get all the used variable names
        if (warpdriver_config.IsMember("subwarps")) {
            NuConfig warp_config = warpdriver_config.GetConfig("subwarps");
            SetSubwarps(warpdriver_config);
            for (auto key : warp_config.GetKeys()) {
                NuConfig subwarp_config = warp_config.GetConfig(key);
                // First get the warp vars
                if (subwarp_config.IsMember("warpvartype")) {
                    if (subwarp_config.GetString("warpvartype") == "reco")
                        recovars.push_back(warp_config.GetConfig(key).GetString("warpvar"));
                    if (subwarp_config.GetString("warpvartype") == "true")
                        truevars.push_back(warp_config.GetConfig(key).GetString("warpvar"));
                }
                for (auto check_var : subwarp_config.GetConfig("check").GetKeys()) {
                    if (subwarp_config.GetConfig("check").GetConfig(check_var).GetString("type") == "reco") {
                        recovars.push_back(check_var);
                    } else {
                        truevars.push_back(check_var);
                    }
                }
            }
        }

        // Get all the variables found into the function pointer map
        for (auto var : recovars) m_fun_pointer_map[var] = fun.GetRecoFunction(var);
        for (auto var : truevars) m_fun_pointer_map[var] = fun.GetTrueFunction(var);

        // if (config.IsMember("subwarps")) {
        //     SetSubwarps(config.GetConfig("subwarps"));
        // }
        // TODO: flexibility to do more general warps?
    }
}

void weight_warper::SetSubwarps(NuConfig config) {
    NuConfig warps = config.GetConfig("subwarps");
    for (auto key : warps.GetKeys()) {
        std::cout << "weight_warper: setting up subwarp " << key << std::endl;
        subwarp* my_subwarp = new subwarp(warps.GetConfig(key));
        m_subwarps[key] = my_subwarp;
    }
}

int weight_warper::CheckSubwarp(const CVUniverse& univ, subwarp* my_subwarp) {
    int tmp_check = 1;
    for (auto var : my_subwarp->GetCheckVars()) {
        PointerToCVUniverseFunction fun = m_fun_pointer_map[var];
        tmp_check = my_subwarp->CheckVal(var, fun(univ));
        if (tmp_check == 0) 
            return tmp_check;
    }
    return tmp_check;
}

// double weight_warper::GetWarpWeight(const CVUniverse& univ, std::string univ_name, int iuniv) {
// Don't warp systematic universes?
// if (univ_name != "cv" || univ_name != "CV")
//     return 1.;
double weight_warper::GetWarpWeight(const CVUniverse& univ) {
    if (!m_dowarp)
        return 1.;
    double weight = 1.;
    for (auto my_subwarp : m_subwarps) {
        if (CheckSubwarp(univ, my_subwarp.second)) {
            weight *= my_subwarp.second->GetSubwarpWeight(univ);

            // this would assume all the warps are exclusive from each other. Would be faster, but relies more on user knowing what they're doing.
            // return tmp_weight
        }
    }
    return weight;
}

bool weight_warper::GetDoWarp() {
    return m_dowarp;
}

std::string weight_warper::GetWarpedMCConfig() {
    return m_warpedmc;
}

std::string weight_warper::GetTag() {
    return m_tag;
}

// ============================ subwarp stuff ==================================
subwarp::subwarp(NuConfig warp_config) {
    CVFunctions<CVUniverse> fun;

    NuConfig checks = warp_config.GetConfig("check");
    for (auto var : checks.GetKeys()) {
        NuConfig varconfig = checks.GetConfig(var);
        if (varconfig.IsMember("equals"))
            equals[var] = varconfig.GetDouble("equals");
        if (varconfig.IsMember("min"))
            equals[var] = varconfig.GetDouble("min");
        if (varconfig.IsMember("max"))
            equals[var] = varconfig.GetDouble("max");
        m_checkvars.push_back(var);
    }

    if (warp_config.IsMember("warpval")) {
        m_warpval = warp_config.GetDouble("warpval");
    } else {
        m_warpval = -1.0;
    }

    if (warp_config.IsMember("warpvar")) {
        m_warpvar = warp_config.GetString("warpvar");
        if (warp_config.GetString("warpvartype") == "reco")
            m_warpvar_fun_pointer = fun.GetRecoFunction(warp_config.GetString("warpvar"));
        if (warp_config.GetString("warpvartype") == "true")
            m_warpvar_fun_pointer = fun.GetTrueFunction(warp_config.GetString("warpvar"));
    }
    if (warp_config.IsMember("warpfile")) {
        if (warp_config.IsMember("warpfunct")) {
            SetWarpFunct(warp_config.GetString("warpfile"), warp_config.GetString("warpfunct"));
            warptype = kFunctWarp;
        }
        else if (warp_config.IsMember("warphist")) {
            SetWarpHist(warp_config.GetString("warpfile"), warp_config.GetString("warphist"));
            warptype = kHistWarp;
        }
    }
}

std::vector<std::string> subwarp::GetCheckVars() {
    return m_checkvars;
}

// private functions 
void subwarp::SetWarpFunct(TString warp_filename, std::string warp_functname) {
    TFile* warpfile = TFile::Open(warp_filename, "READ");
    if (warpfile) {
        std::cout << "weight_warper::subwarp: I'm using this file for the warp: " << warp_filename << std::endl;
        m_warpfunct = (TF1*)warpfile->Get(warp_functname.c_str());
    } else {
        std::cout << "weight_warper::subwarp: WARNING: Cannot find input file for subwarp: " << warp_filename << std::endl;
        std::cout << "  Defaulting to no warp." << std::endl;
        m_warpval = 1.;
    }
    // if (m_warpfunct.size() < 1) {
    //     std::cout << "weight_warper::subwarp: failed to find warp hist in " << warp_filename << std::endl;
    //     exit(1);
    // }
}

void subwarp::SetWarpHist(TString warp_filename, std::string warp_histname) {
    TFile* warpfile = TFile::Open(warp_filename, "READ");
    if (warpfile) {
        std::cout << "weight_warper::subwarp: I'm using this file for the warp: " << warp_filename << std::endl;
        m_warphist = (MnvH1D*)warpfile->Get(warp_histname.c_str());
    } else {
        std::cout << "weight_warper::subwarp: WARNING: Cannot find input file for subwarp: " << warp_filename << std::endl;
        std::cout << "  Defaulting to no warp." << std::endl;
        m_warpval = 1.;
    }
    // if (m_warphist.size() < 1) {
    //     std::cout << "weight_warper::subwarp: failed to find warp hist in " << warp_filename << std::endl;
    //     exit(1);
    // }
}

// public functions

bool subwarp::CheckVal(std::string varname, double val) {
    if (equals.find(varname) != equals.end())
        // If equal set, return if equal to it
        return val == equals[varname];

    bool pass_min = 0;
    if (min.find(varname) != min.end())
        // If  if min set and lower than minimum, return 0
        if (val < min[varname]) 
            return 0;
        // else, pass minimum
        pass_min = 1;
    if (max.find(varname) != max.end())
        // If max set, return pass at or if below it
        return val <= max[varname];
    // If no max set, return pass_min (default 0)
    return pass_min;
}

double subwarp::GetWarpWeight(double warpvar_val) { 
    if (m_warpval >= 0) 
        return m_warpval;
    
    return -1.;
}

double subwarp::GetSubwarpWeight(const CVUniverse& univ) {
    // if a straight warp is set, warpval>0, use that 
    if (m_warpval >= 0)
        return m_warpval;
    double warpvar_val = m_warpvar_fun_pointer(univ);

    // TODO: read out the value from the function or histogram

    // If you have a function, use that
    if (warptype==kFunctWarp) {
        m_warpfunct->Eval(warpvar_val);
    }
    // If you have a hist, use that
    if (warptype==kHistWarp) {
        // Check which bin the warpvalue is. If it's below or above the bounds of the hist, return the lowest or highest bin respectively.
        int xbin;
        if (warpvar_val < m_warphist->GetBinLowEdge(1)) {
            xbin = 1;
        } else if (m_warphist->FindFirstBinAbove(warpvar_val) < 0.) {
            xbin = m_warphist->GetMaximumBin();
        } else {
            xbin = m_warphist->GetXaxis()->FindBin(warpvar_val);
        }
        return m_warphist->GetBinContent(xbin);
    }
    std::cout << "WARNING: no weight found for this subwarp, returning -1. Results may be bad..." << std::endl;
    return -1.;
}
