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

weight_warper::weight_warper(TString filename) {
    read(filename);
    m_tunedmc = "both";
}

weight_warper::weight_warper(const NuConfig config) {
    CVFunctions<CVUniverse> fun;

    // TODO: these need to come from a config, this needs to parse checkvars and warpvars
    std::vector<std::string> recovars;
    std::vector<std::string> truevars;

    // Get the relevant things for subwarps from the config
    // TODO: this is so gross
    if (config.IsMember("warps")) {
        SetSubwarps(config.GetConfig("warps"));
        NuConfig warp_config = config.GetConfig("warps");
        for (auto key : warp_config.GetKeys()) {
            NuConfig subwarp_config = warp_config.GetConfig(key);
            // First get the warp vars
            if (subwarp_config.GetString("warpvartype") == "reco")
                recovars.push_back(warp_config.GetConfig(key).GetString("warpvar"));
            if (subwarp_config.GetString("warpvartype") == "true")
                truevars.push_back(warp_config.GetConfig(key).GetString("warpvar"));
            for (auto check_var : subwarp_config.GetConfig("check").GetKeys()) {
                if (subwarp_config.GetConfig("check").GetConfig(check_var).GetString("type") == "reco") {
                    recovars.push_back(check_var);
                } else {
                    truevars.push_back(check_var);
                }
            }
        }
    }

    for (auto var : recovars) m_recofun_pointer_map[var] = fun.GetRecoFunction(var);
    for (auto var : truevars) m_truefun_pointer_map[var] = fun.GetTrueFunction(var);

    // if (config.IsMember("warps")) {
    //     SetSubwarps(config.GetConfig("warps"));
    // }
    // TODO: flexibility to do more general warps?
}

void weight_warper::SetSubwarps(NuConfig config) {
    NuConfig warps = config.GetConfig("warps");
    for (auto key : warps.GetKeys()) {
        PlotUtils::subwarp* subwarp = new PlotUtils::subwarp(warps.GetConfig(key));
        m_subwarps[key] = subwarp;
    }
}


void weight_warper::read(TString filename) {
    m_f_ScaleFrac = TFile::Open(filename, "READ");
    if (m_f_ScaleFrac) {
        std::cout << "weight_warper: I'm using this scale file " << filename << std::endl;
        for (auto cat : m_categories) {
            std::string name = "h___QElike___" + cat + "___Q2QE___scale";
            m_mnvh_Scales[cat] = (MnvH1D*)m_f_ScaleFrac->Get(name.c_str());
            // m_scale_minmax[cat] = { m_mnvh_Scales[cat]->GetXaxis()->GetXmin}
        }
    } else {
        std::cout << "weight_warper::read: WARNING: Cannot find input file for weight_warper: " << filename << std::endl;
        std::cout << "                                 Defaulting to no tuning." << std::endl;
        m_tunedmc = "untuned";
    }
    if (m_mnvh_Scales.size() < 1) {
        std::cout << "weight_warper: failed to find signal or background scale fractions in " << filename << std::endl;
        exit(1);
    }
}

void weight_warper::SetCat(std::string cat) {
    if (std::find(m_categories.begin(), m_categories.end(), cat) == m_categories.end()) {
        // std::cout << " can't find this category for mcrescale in scale file " << cat << std::endl;
        m_category = "None";
        return;
    }
    m_category = cat;

    m_mnvh_Scale = m_mnvh_Scales[cat];
}

double weight_warper::GetScaleInternal(const double checkval, std::string uni_name, int iuniv) {
    double retval = 1.;
    double xval = checkval;
    int xbin = -1;

    if (m_category == "None") {
        // std::cout << "weight_warper: This variable is not recognized as category. Returning 1.0." << std::endl;
        return 1.0;
    }

    // if (xval < 0.) {
    if (xval < m_mnvh_Scale->GetBinLowEdge(1)) {
        // std::cout << "weight_warper: You have a check value less than minimum. Returning 1.0 since could be unphysical." << std::endl;
        // std::cout << "                  xval = " << xval << std::endl;
        // return 1.0;
        xbin = 1;
    }
    // else if(q2qe>=2.0){
    else if (m_mnvh_Scale->FindFirstBinAbove(xval) < 0) {
        // Some scale files only go up to 2GeV^2 in Q2. This sets you in that highest bin if you give it a value higher than 2GeV^2
        // checkval = 1.99;
        // std::cout << "weight_warper: You have a check value less than minimum. Returning 1.0" << std::endl;
        // xval = m_mnvh_Scale->GetBinContent(m_mnvh_Scale->GetMaximumBin());
        xbin = m_mnvh_Scale->GetMaximumBin();
    } else {
        xbin = m_mnvh_Scale->GetXaxis()->FindBin(xval);
    }

    static int errcount = 0;
    TH1D* hcv = (TH1D*)m_mnvh_Scale;
    if (uni_name == "cv" || uni_name == "CV") {
        m_h_scale = hcv;
        // double s = hcv->GetBinError(xbin);
        // double x = TRandom::Gaus(0.0,1.0);
    } else {  // check to see that error band exists
        if (m_mnvh_Scale->HasVertErrorBand(uni_name) && iuniv < m_mnvh_Scale->GetVertErrorBand(uni_name)->GetNHists()) {
            m_h_scale = (TH1D*)m_mnvh_Scale->GetVertErrorBand(uni_name)->GetHist(iuniv);
            // std::cout << "weight_warper: pulling out error band " << uni_name << std::endl;
        } else {
            errcount++;
            if (!m_mnvh_Scale->HasVertErrorBand(uni_name)) {
                if (errcount < 100) std::cout << " MCreScale could not find error band  " << uni_name << " at all, returning CV" << std::endl;
                m_h_scale = hcv;
                return m_h_scale->GetBinContent(xbin);
            }
            if (iuniv >= m_mnvh_Scale->GetVertErrorBand(uni_name)->GetNHists()) {
                if (errcount < 100) std::cout << " MCreScale could not find " << uni_name << " error band # " << iuniv << " you need to set requested number to value <= " << m_mnvh_Scale->GetVertErrorBand(uni_name)->GetNHists() << std::endl;
                assert(0);
            }
        }
    }
    retval = m_h_scale->GetBinContent(xbin);
    // std::cout << "weight_warper: Finished error band " << uni_name << std::endl;
    return retval;
}

// Returns a scale factor. If it's not set up, it returns -1 (which isn't possible).
double weight_warper::GetScale(std::string cat, const double q2qe, std::string uni_name, int iuniv) {
    // Default value, not physical. Checked so you can switch scaling on and off easier.
    double retval = -1.;
    if (m_tunedmc != "untuned") {
        SetCat(cat);
        retval = GetScaleInternal(q2qe, uni_name, iuniv);
    }

    return retval;
}

// This one takes a universe and gets the q2qe value internally. This can save
// some time maybe? Especially for events where this isn't necessary.
double weight_warper::GetScale(std::string cat, const CVUniverse* univ, std::string uni_name, int iuniv) {
    // Default value, not physical. Checked so you can switch scaling on and off easier.
    double retval = -1.;
    if (m_tunedmc != "untuned") {
        const double q2qe = univ->GetQ2QEGeV();
        SetCat(cat);
        retval = GetScaleInternal(q2qe, uni_name, iuniv);
    }

    return retval;
}

double weight_warper::GetScale(const CVUniverse*univ, std::string uni_name, int iuniv) { 
    double retval = -1.0;
    std::map<std::string, const double> var_values;
    

    return retval;
}

double weight_warper::GetScaleInternal(std::map<std::string, const double> var_values, std::string uni_name, int iuniv) {
    return -1.;
}


// ============================ subwarp stuff ==================================
subwarp::subwarp(NuConfig warp_config) {
    m_warpvar = warp_config.GetString("warpvar");
    NuConfig checks = warp_config.GetConfig("check");

    for (auto var : checks.GetKeys()) {
        NuConfig varconfig = warp_config.GetValue(var);
        if (varconfig.IsMember("equals"))
            equals[var] = varconfig.GetDouble("equals");
        if (varconfig.IsMember("min"))
            equals[var] = varconfig.GetDouble("min");
        if (varconfig.IsMember("max"))
            equals[var] = varconfig.GetDouble("max");
    }

    if (warp_config.IsMember("warpval")) {
        m_warpval = warp_config.GetDouble("warpval");
    } else {
        m_warpval = -1.0;
    }

    if (warp_config.IsMember("warpfile")) {
        if (warp_config.IsMember("warpfunct")) {
            SetWarpFunct(warp_config.GetString("warpfile")), warp_config.GetString("warpfunct");
            warptype = kFunctWarp;
        }
        else if (warp_config.IsMember("warphist")) {
            SetWarpHist(warp_config.GetString("warpfile")), warp_config.GetString("warphist");
            warptype = kHistWarp;
        }
    }
    // If you're using a function or hist from a file, this is set externally
}

// private functions 
void subwarp::SetWarpFunct(TString warp_filename, std::string warp_functname) {
    TFile* warpfile = TFile::Open(warp_filename, "READ");
    if (warpfile) {
        std::cout << "weight_warper::subwarp: I'm using this file for the warp: " << warp_filename << std::endl;
        m_warpfunct = (TF1*)warpfile->Get(warp_functname.c_str());
    } else {
        std::cout << "weight_warper::subwarp: WARNING: Cannot find input file for subwarp: " << filename << std::endl;
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
int subwarp::CheckVal(std::string varname, double val) {
    if (equals.find(varname) != equals.end())
        // If equal set, return if equal to it
        return val = equals[varname];

    bool pass_min = 0;
    if (min.find(varname) != min.end())
        // If  if min set and lower than minimum, return 0
        if (val < min[varname]) 
            return 0;
        // else, pass minimum
        pass_min = 1;
    if (max.find(varname) != max.end())
        // If max set, return passs if below it
        return val <= max[varname];
    // If no max set, return pass_min (default 0)
    return pass_min;
}

double subwarp::GetWarpVal(double warpvar_val) { 
    if (m_warpval >= 0) 
        return m_warpval;
    return -1.;
}
