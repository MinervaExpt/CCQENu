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
#include "utils/NuConfig.h"
#include "utils/expandEnv.h"
#include "weight_MCreScale.h"
// #include "TRandom.h"

using namespace PlotUtils;

weight_MCreScale::weight_MCreScale(TString filename) {
    read(filename);
    m_tunedmc = "both";
}

weight_MCreScale::weight_MCreScale(const NuConfig config) {
    std::string filename = "";
    if (config.IsMember("tunedmc")) {
        m_tunedmc = config.GetString("tunedmc");
    } else {
        std::cout << "weight_MCreScale: \'tunedmc\' not set in main config. Defaulting to \'untuned\'." << std::endl;
    }

    if (config.IsMember("scalefileIn")) {
        filename = config.GetString("scalefileIn");
    } else {
        std::cout << "weight_MCreScale: \'scalefileIn\' not configured in main. Will just run without tuning." << std::endl;
        m_tunedmc = "untuned";
        filename = "";
    }

    if (config.IsMember("TuneCategories")) {
        m_categories = config.GetStringVector("TuneCategories");
    } else {
        m_categories = {"qelike", "qelikenot"};
    }
    if (m_tunedmc != "untuned") {
        read(filename);
    }
}

void weight_MCreScale::read(TString filename) {
    m_f_ScaleFrac = TFile::Open(filename, "READ");
    if (m_f_ScaleFrac) {
        std::cout << "weight_MCreScale: I'm using this scale file " << filename << std::endl;
        for (auto cat : m_categories) {
            std::string name = "h___Background___" + cat + "___Q2QE___scale";
            m_mnvh_Scales[cat] = (MnvH1D*)m_f_ScaleFrac->Get(name.c_str());
            // m_scale_minmax[cat] = { m_mnvh_Scales[cat]->GetXaxis()->GetXmin}
        }
    } else {
        std::cout << "weight_MCreScale::read: WARNING: Cannot find input file for weight_MCreScale: " << filename << std::endl;
        std::cout << "                                 Defaulting to no tuning." << std::endl;
        m_tunedmc = "untuned";
    }
    if (m_mnvh_Scales.size() < 1) {
        std::cout << "weight_MCreScale: failed to find signal or background scale fractions in " << filename << std::endl;
        exit(1);
    }
}

void weight_MCreScale::SetCat(std::string cat) {
    if (std::find(m_categories.begin(), m_categories.end(), cat) == m_categories.end()) {
        // std::cout << " can't find this category for mcrescale in scale file " << cat << std::endl;
        m_category = "None";
        return;
    }
    m_category = cat;

    m_mnvh_Scale = m_mnvh_Scales[cat];
}

double weight_MCreScale::GetScaleInternal(const double checkval, std::string uni_name, int iuniv) {
    double retval = 1.;
    double xval = checkval;
    int xbin = -1;

    if (m_category == "None") {
        // std::cout << "weight_MCreScale: This variable is not recognized as category. Returning 1.0." << std::endl;
        return 1.0;
    }

    // if (xval < 0.) {
    if (xval < m_mnvh_Scale->GetBinLowEdge(1)) {
        // std::cout << "weight_MCreScale: You have a check value less than minimum. Returning 1.0 since could be unphysical." << std::endl;
        // std::cout << "                  xval = " << xval << std::endl;
        // return 1.0;
        xbin = 1;
    }
    // else if(q2qe>=2.0){
    else if (m_mnvh_Scale->FindFirstBinAbove(xval) < 0) {
        // Some scale files only go up to 2GeV^2 in Q2. This sets you in that highest bin if you give it a value higher than 2GeV^2
        // checkval = 1.99;
        // std::cout << "weight_MCreScale: You have a check value less than minimum. Returning 1.0" << std::endl;
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
            // std::cout << "weight_MCreScale: pulling out error band " << uni_name << std::endl;
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
    // std::cout << "weight_MCreScale: Finished error band " << uni_name << std::endl;
    return retval;
}

// Returns a scale factor. If it's not set up, it returns -1 (which isn't possible).
double weight_MCreScale::GetScale(std::string cat, const double q2qe, std::string uni_name, int iuniv) {
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
double weight_MCreScale::GetScale(std::string cat, const CVUniverse* univ, std::string uni_name, int iuniv) {
    // Default value, not physical. Checked so you can switch scaling on and off easier.
    double retval = -1.;
    if (m_tunedmc != "untuned") {
        const double q2qe = univ->GetQ2QEGeV();
        SetCat(cat);
        retval = GetScaleInternal(q2qe, uni_name, iuniv);
    }

    return retval;
}
