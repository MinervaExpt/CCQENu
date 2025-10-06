/**
// * @file
// * @author  Heidi Schellman/Noah Vaughan/SeanGilligan
// * @version 1.0 *
// * @section LICENSE *
// * This program is free software; you can redistribute it and/or
// * modify it under the terms of the GNU General Public License as
// * published by the Free Software Foundation; either version 2 of
// * the License, or (at your option) any later version. *
// * @section DESCRIPTION *
// * Code to create Variables from Config file
 */
#ifndef VARIABLEHYPERDFromConfig_H
#define VARIABLEHYPERDFromConfig_H

#include "CVUniverse.h"
// #include "VariableFromConfig.h"
#include "HistHyperDWrapperMap.h"
#include "MinervaUnfold/MnvResponse.h"
#include "include/ResponseHyperDWrapperMap.h"
#include "utils/NuConfig.h"
// #include "utils/UniverseDecoder.h"

#include "include/CVFunctions.h"
#ifndef __CINT__  // CINT doesn't know about std::function

#include "PlotUtils/VariableHyperDBase.h"

#endif  // __CINT__

namespace CCQENu {

class VariableHyperDFromConfig : public PlotUtils::VariableHyperDBase<CVUniverse> {
   private:
    typedef std::function<double(const CVUniverse &)> PointerToCVUniverseFunction;
    typedef std::function<double(const CVUniverse &, int)> PointerToCVUniverseArgFunction;

    typedef HistHyperDWrapperMap<CVUniverse> HMHD;  // TODO: HyperDim HistWrapper? Map?
    typedef ResponseHyperDWrapperMap<CVUniverse> RMHD;


    PointerToCVUniverseFunction m_pointer_to_RecoIndex; // I think this should be the same for all the vars you look at
    PointerToCVUniverseFunction m_pointer_to_TrueIndex; // I think this should be the same for all the vars you look at

    std::vector<PointerToCVUniverseArgFunction> m_pointer_to_ArgGetRecoValue_vec;
    std::vector<PointerToCVUniverseArgFunction> m_pointer_to_ArgGetTrueValue_vec;
    // std::vector<PointerToCVUniverseFunction> m_pointer_to_RecoIndex_vec;
    // std::vector<PointerToCVUniverseFunction> m_pointer_to_TrueIndex_vec;

   public:
    std::vector<bool> m_do_argvalue_vec = {};
    bool m_do_argvalue = false;
    //=======================================================================================
    // CTOR
    //=======================================================================================
    template <class... ARGS>

    VariableHyperDFromConfig(const std::string name,
                             const std::vector<CCQENu::VariableFromConfig *> &vars,
                             const std::vector<std::string> fors,
                             const EAnalysisType type) : PlotUtils::VariableHyperDBase<CVUniverse>(name, type) {  // Right now GetVariables isn't clever on getting "fors". Either takes in some form Variable config file, or defaults to all of them

        for (int i = 0; i < vars.size(); i++) {
            AddVariable(*vars[i]);
            m_tunedmc = vars[i]->GetTunedMC();
            if (vars[i]->m_do_argvalue) {
                m_pointer_to_ArgGetRecoValue_vec.push_back(vars[i]->GetPointerToArgRecoFunction());
                m_pointer_to_ArgGetTrueValue_vec.push_back(vars[i]->GetPointerToArgTrueFunction());
                m_pointer_to_RecoIndex = vars[i]->GetPointerToRecoIndexFunction();
                m_pointer_to_TrueIndex = vars[i]->GetPointerToTrueIndexFunction();
                // m_pointer_to_RecoIndex_vec.push_back(vars[i]->GetPointerToRecoIndexFunction());
                // m_pointer_to_TrueIndex_vec.push_back(vars[i]->GetPointerToTrueIndexFunction());
                m_do_argvalue_vec.push_back(true);
            } else {
                m_do_argvalue_vec.push_back(false);
                m_pointer_to_ArgGetRecoValue_vec.push_back(vars[i]->GetPointerToArgRecoFunction());
                m_pointer_to_ArgGetTrueValue_vec.push_back(vars[i]->GetPointerToArgTrueFunction());
                // m_pointer_to_RecoIndex_vec.push_back(vars[i]->GetPointerToRecoIndexFunction());
                // m_pointer_to_TrueIndex_vec.push_back(vars[i]->GetPointerToTrueIndexFunction());
            }
        }

        for (auto val : m_do_argvalue_vec) {
            if (val) {
                m_do_argvalue = true;
                break;
            }
        }
        // Fors isn't very sophisticated atm. Could be better.
        if (fors.size() > 0) {
            for (auto s : fors)
                m_for.push_back(s);
        } else {
            std::vector<std::string> def = {"data", "selected_reco", "selected_truth", "response", "truth"};
            for (auto s : def)
                m_for.push_back(s);
        }
    };

    typedef std::map<std::string, std::vector<CVUniverse *>> UniverseMap;
    //=======================================================================================
    // DECLARE NEW HISTOGRAMS
    //=======================================================================================
    // Histwrappers -- selected mc, selected data
    // TODO: Need to do hyperdim hist/responsewrappersmaps?

    HMHD m_selected_mc_reco;        // HM for normal MC hists - has special constructor to make response
    HMHD m_tuned_selected_mc_reco;  // HM for tuned MC hists used for background subtraction -NHV - has special constructor to make response
    HMHD m_selected_mc_truth;
    HMHD m_tuned_selected_mc_truth;
    HMHD m_signal_mc_truth;
    HMHD m_tuned_signal_mc_truth;
    HMHD m_selected_data;
    RMHD m_response;
    RMHD m_tuned_response;

    UniverseMap m_universes;
    std::string m_units;
    std::map<const std::string, bool> hasData;
    std::map<const std::string, bool> hasMC;
    std::map<const std::string, bool> hasSelectedTruth;
    std::map<const std::string, bool> hasTruth;
    std::map<const std::string, bool> hasResponse;
    std::map<const std::string, bool> hasTunedMC;
    std::vector<std::string> m_tags;
    std::vector<std::string> m_for;
    std::string m_tunedmc; 

    inline virtual std::string GetUnits() { return m_units; };

    inline virtual void SetUnits(std::string units) { m_units = units; };

    inline virtual std::string GetTuned() { return m_tunedmc; };
    //=======================================================================================
    // INITIALIZE ALL HISTOGRAMS
    //=======================================================================================

    void AddTags(const std::vector<std::string> tags) {
        for (auto t : tags) {
            m_tags.push_back(t);
        }
    };

    EAnalysisType GetAnalysisType() { return m_analysis_type; }

    // all of the following could probably be the same code, sigh...
    template <typename T>
    void InitializeMCHistograms(T univs, const std::vector<std::string> tags) {
        if (std::count(m_for.begin(), m_for.end(), "selected_reco") < 1) {
            // std::cout << "VariableHyperDFromConfig::InitializeMCHistograms: WARNING selected_reco is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags)
                hasMC[tag] = false;
            return;
        }
        for (auto tag : tags)
            hasMC[tag] = true;

        if (m_tunedmc == "tuned") {
            // std::cout << "VariableHyperDFromConfig::InitializeMCHistograms: WARNING untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
            return;
        }
        std::vector<double> xrecolinbins = GetRecoBinVec();  // TODO: set this up in VariableHyperDBase
        // if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
        //     m_selected_mc_reco = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNRecoBins(), xrecolinbins, univs, tags);
        // else if (m_analysis_type == k2D || m_analysis_type == k2D_lite) {
        //     std::vector<double> yrecobins = GetRecoBinVec(1);
        //     m_selected_mc_reco = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xrecolinbins, yrecobins, univs, tags);
        // }

        std::vector<double> yrecobins = GetRecoBinVec(1);
        std::string axis_label = (GetName() + ";" + m_lin_axis_label).c_str();
        if (m_analysis_type == k2D || m_analysis_type == k2D_lite)
            axis_label += ";" + m_y_axis_label;
        m_selected_mc_reco = HMHD(Form("%s", GetName().c_str()), axis_label, xrecolinbins, yrecobins, univs, tags, m_analysis_type);

        m_selected_mc_reco.AppendName("reconstructed", tags);  // patch to conform to CCQENU standard m_selected_mc_truth.AppendName("_truth",tags); // patch to conform to CCQENU standard
    }

    template <typename T>
    void InitializeSelectedTruthHistograms(T univs, const std::vector<std::string> tags) {
        if (std::count(m_for.begin(), m_for.end(), "selected_truth") < 1) {
            // std::cout << "VariableHyperDFromConfig::InitializeSelectedTruthHistograms: WARNING selected_truth is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags) {
                hasSelectedTruth[tag] = false;
            }
            return;
        }
        for (auto tag : tags) {
            hasSelectedTruth[tag] = true;
        }

        if (m_tunedmc == "tuned") {
            // std::cout << "VariableHyperDFromConfig::InitializeSelectedTruthHistograms: WARNING untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
            return;
        }

        std::vector<double> xlinbins = GetBinVec();
        // if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
        //     m_selected_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNBins(), xlinbins, univs, tags);
        // else if (m_analysis_type == k2D || m_analysis_type == k2D_lite) {
        //     std::vector<double> ybins = GetBinVec(1);
        //     m_selected_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xlinbins, ybins, univs, tags);
        // }
        std::vector<double> ybins = GetBinVec(1);
        std::string axis_label = (GetName() + ";" + m_lin_axis_label).c_str();
        if (m_analysis_type == k2D || m_analysis_type == k2D_lite)
            axis_label += ";" + m_y_axis_label;
        m_selected_mc_truth = HMHD(Form("%s", GetName().c_str()), axis_label, xlinbins, ybins, univs, tags, m_analysis_type);
        m_selected_mc_truth.AppendName("selected_truth", tags);
    }

    template <typename T>
    void InitializeTruthHistograms(T univs, const std::vector<std::string> tags) {
        if (std::count(m_for.begin(), m_for.end(), "truth") < 1) {
            // std::cout << "VariableHyperDFromConfig::InitializeTruthHistograms: WARNING truth is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags)
                hasTruth[tag] = false;
            return;
        }

        for (auto const tag : tags)
            hasTruth[tag] = true;

        if (m_tunedmc == "tuned") {
            // std::cout << "VariableHyperDFromConfig::InitializeTruthHistograms: WARNING untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
            return;
        }

        std::vector<double> xlinbins = GetBinVec();
        // if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
        //     m_signal_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNBins(), xlinbins, univs, tags);
        // else if (m_analysis_type == k2D || m_analysis_type == k2D_lite) {
        //     std::vector<double> ybins = GetBinVec(1);
        //     m_signal_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xlinbins, ybins, univs, tags);
        // }
        std::vector<double> ybins = GetBinVec(1);
        std::string axis_label = (GetName() + ";" + m_lin_axis_label).c_str();
        if (m_analysis_type == k2D || m_analysis_type == k2D_lite)
            axis_label += ";" + m_y_axis_label;
        m_signal_mc_truth = HMHD(Form("%s", GetName().c_str()), axis_label, xlinbins, ybins, univs, tags, m_analysis_type);

        m_signal_mc_truth.AppendName("all_truth", tags);
    }

    template <typename T>
    void InitializeDataHistograms(T univs, const std::vector<std::string> tags) {
        if (std::count(m_for.begin(), m_for.end(), "data") < 1) {
            // std::cout << "VariableHyperDFromConfig::InitializeDataHistograms: WARNING data is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags)
                hasData[tag] = false;
            return;
        }
        for (auto tag : tags)
            hasData[tag] = true;

        std::vector<double> xrecolinbins = GetRecoBinVec();
        // if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
        //     m_selected_data = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNRecoBins(), xrecolinbins, univs, tags);
        // else if (m_analysis_type == k2D || m_analysis_type == k2D_lite) {
        //     std::vector<double> yrecobins = GetRecoBinVec(1);
        //     m_selected_data = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xrecolinbins, yrecobins, univs, tags);
        // }
        std::vector<double> yrecobins = GetRecoBinVec(1);
        std::string axis_label = (GetName() + ";" + m_lin_axis_label).c_str();
        if (m_analysis_type == k2D || m_analysis_type == k2D_lite)
            axis_label += ";" + m_y_axis_label;
        m_selected_data = HMHD(Form("%s", GetName().c_str()), axis_label, xrecolinbins, yrecobins, univs, tags, m_analysis_type);

        m_selected_data.AppendName("reconstructed", tags);
    }

    template <typename T>
    void InitializeTunedMCHistograms(T reco_univs, T truth_univs, const std::vector<std::string> tuned_tags, const std::vector<std::string> response_tags) {
        if (m_tunedmc == "untuned") {
            // std::cout << "VariableHyperDFromConfig::InitializeTunedMCHistograms: WARNING tunedmc is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tuned_tags)
                hasTunedMC[tag] = false;
            return;
        }

        for (auto tag : tuned_tags)
            hasTunedMC[tag] = true;

        std::vector<double> xlinbins = GetBinVec();
        std::vector<double> xrecolinbins = GetRecoBinVec();
        std::vector<double> ybins = GetBinVec(1);
        std::vector<double> yrecobins = GetRecoBinVec(1);

        std::string axis_label = (GetName() + ";" + m_lin_axis_label).c_str();
        if (m_analysis_type == k2D || m_analysis_type == k2D_lite)
            axis_label += ";" + m_y_axis_label;

        // Check which categories are configured and add a tuned version
        if (std::count(m_for.begin(), m_for.end(), "selected_reco") >= 1) {  // use recobins
            // if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
            //     m_tuned_selected_mc_reco = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNRecoBins(), xrecolinbins, reco_univs, tuned_tags);
            // else if (m_analysis_type == k2D || m_analysis_type == k2D_lite)
            //     m_tuned_selected_mc_reco = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xrecolinbins, yrecobins, reco_univs, tuned_tags);
            m_tuned_selected_mc_reco = HMHD(Form("%s", GetName().c_str()), axis_label, xrecolinbins, yrecobins, reco_univs, tuned_tags, m_analysis_type);
            m_tuned_selected_mc_reco.AppendName("reconstructed_tuned", tuned_tags);
        }
        if (std::count(m_for.begin(), m_for.end(), "selected_truth") >= 1) {  // use bins
            // if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
            //     m_tuned_selected_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNBins(), xlinbins, reco_univs, tuned_tags);
            // else if (m_analysis_type == k2D || m_analysis_type == k2D_lite)
            //     m_tuned_selected_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xlinbins, ybins, reco_univs, tuned_tags);
            m_tuned_selected_mc_truth = HMHD(Form("%s", GetName().c_str()), axis_label, xlinbins, ybins, reco_univs, tuned_tags, m_analysis_type);
            m_tuned_selected_mc_truth.AppendName("selected_truth_tuned", tuned_tags);
        }
        if (std::count(m_for.begin(), m_for.end(), "truth") >= 1) {  // use bins
            // if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
            //     m_tuned_signal_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNBins(), xlinbins, truth_univs, tuned_tags);
            // else if (m_analysis_type == k2D || m_analysis_type == k2D_lite)
            //     m_tuned_signal_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xlinbins, ybins, truth_univs, tuned_tags);
            m_tuned_signal_mc_truth = HMHD(Form("%s", GetName().c_str()), axis_label, xlinbins, ybins, truth_univs, tuned_tags, m_analysis_type);
            m_tuned_signal_mc_truth.AppendName("all_truth_tuned", tuned_tags);
        }
        if (std::count(m_for.begin(), m_for.end(), "response") >= 1) {
            if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
                m_tuned_response = RMHD(Form("%s", GetName().c_str()), reco_univs, xrecolinbins, xlinbins, response_tags, "_tuned");
            else if (m_analysis_type == k2D || m_analysis_type == k2D_lite)
                m_tuned_response = RMHD(Form("%s", GetName().c_str()), reco_univs, xrecolinbins, xlinbins, yrecobins, ybins, response_tags, "_tuned");
        }
    }

    //============================================================================
    // RESPONSE STUFF
    //============================================================================

    // reco_univs should be the same as selected_mc_reco (tuned or untuned)
    template <typename T>
    void InitializeResponse(T reco_univs, const std::vector<std::string> tags, std::string tail = "") {
        // Check if response is configured for this var
        if (std::count(m_for.begin(), m_for.end(), "response") < 1) {
            // std::cout << "VariableHyperDFromConfig::InitializeResponse: WARNING response is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags)
                hasResponse[tag] = false;
            return;
        }

        // Check that the var has both MC reco and truth configured, set bool to true
        for (auto tag : tags) {
            assert(hasMC[tag]);
            assert(hasSelectedTruth[tag]);
            hasResponse[tag] = true;
        }

        std::vector<double> xlinbins = GetBinVec();
        std::vector<double> xrecolinbins = GetRecoBinVec();
        if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
            m_response = RMHD(Form("%s", GetName().c_str()), reco_univs, xrecolinbins, xlinbins, tags, tail);
        else if (m_analysis_type == k2D || m_analysis_type == k2D_lite) {
            std::vector<double> ybins = GetBinVec(1);
            std::vector<double> yrecobins = GetRecoBinVec(1);
            m_response = RMHD(Form("%s", GetName().c_str()), reco_univs, xrecolinbins, xlinbins, yrecobins, ybins, tags, tail);
        }
    }

    void FillResponse(std::string tag, CVUniverse *univ,
                      const double value, const double truth,
                      const double weight, const double scale = 1.0) {
        if (m_analysis_type != k1D) {  // skip if not 1D type 1 analysis
            std::cout << "VariableHyperDFromConfig::FillResponse2D: Set to analysis type " << m_analysis_type << ". Will not fill response for 1D HyperD hists." << std::endl;
            return;
        }

        std::string name = univ->ShortName();
        // int iuniv = m_decoder[univ];
        if (hasMC[tag] && m_tunedmc != "tuned")
            m_response.Fill(tag, univ, value, truth, weight);
        if (hasTunedMC[tag] && scale >= 0.)
            m_tuned_response.Fill(tag, univ, value, truth, weight, scale);
    }

    void FillResponse(const std::string tag, CVUniverse *univ,
                      const double x_value, const double y_value,
                      const double x_truth, const double y_truth,
                      const double weight, const double scale = 1.0) {  // From Hist2DWrapperMap
        if (m_analysis_type != k2D) { // skip if not 2D type 0 analysis
            std::cout << "VariableHyperDFromConfig::FillResponse: Set to analysis type " << m_analysis_type << ". Will not fill response for 2D HyperD hists." << std::endl;
            return;
        }

        std::string name = univ->ShortName();
        if (hasMC[tag] && m_tunedmc != "tuned")
            m_response.Fill(tag, univ, x_value, y_value, x_truth, y_truth, weight);  // value here is reco
        if (hasTunedMC[tag] && scale >= 0.)
            m_tuned_response.Fill(tag, univ, x_value, y_value, x_truth, y_truth, weight, scale);  // value here is reco
    }
    //============================================================================
    // GetValue overloads for doing vector branches (e.g. blobs)
    //============================================================================

    std::vector<double> GetArgRecoValue(const CVUniverse &universe, const int maxidx) const {
        assert(m_do_argvalue);

        std::vector<double> out_vec;
        // std::vector<std::vector<double>> val_vec; // should be a list of val_vecs to plug into hyperdim to get the value for each blob
        for (int i = 0; i < maxidx; i++) {
            std::vector<double> tmp_val_vec = {};
            for (int j = 0; j < m_dimension; j++) {
                if (!m_do_argvalue_vec[j]) {
                    double tmp_val = m_vars_vec[j]->PlotUtils::VariableBase<CVUniverse>::GetRecoValue(universe);
                    tmp_val_vec.push_back(tmp_val);
                    continue;
                }
                tmp_val_vec.push_back(m_pointer_to_ArgGetRecoValue_vec[j](universe,i));
            }
            if (!m_has_reco_binning) out_vec.push_back((m_hyperdim->GetBin(tmp_val_vec)).first + 0.0001);
            else out_vec.push_back((m_reco_hyperdim->GetBin(tmp_val_vec)).first + 0.0001);
        }
        return out_vec;
    }

    std::vector<double> GetArgTrueValue(const CVUniverse &universe, const int maxidx) const {
        assert(m_do_argvalue);
        std::vector<double> out_vec;
        for (int i = 0; i < maxidx; i++) {
            std::vector<double> tmp_val_vec = {};
            for (int j = 0; j < m_dimension; j++) {
                if (!m_do_argvalue_vec[j]) {
                    tmp_val_vec.push_back(m_vars_vec[j]->GetTrueValue(universe)); // TODO this could be optimized to be called only once
                    continue;
                }
                tmp_val_vec.push_back(m_pointer_to_ArgGetTrueValue_vec[j](universe,i));
            }
            out_vec.push_back((m_hyperdim->GetBin(tmp_val_vec)).first + 0.0001);
        }
        return out_vec;
    }


    std::vector<double> GetArgRecoValue(const int axis, const CVUniverse &universe, const int maxidx) const {
        assert(m_do_argvalue);
        std::vector<double> out_vec = {};
        if (!m_do_argvalue_vec[axis]) {
            double val = m_vars_vec[axis]->GetRecoValue(universe);
            for (int i = 0; i < maxidx; i++)
                out_vec.push_back(val);
            return out_vec;
        }
        for (int i = 0; i < maxidx; i++)
            out_vec.push_back(m_pointer_to_ArgGetRecoValue_vec[axis](universe,i));
        return out_vec;
    }

    std::vector<double> GetArgTrueValue(const int axis, const CVUniverse &universe, const int maxidx) const {
        assert(m_do_argvalue);
        std::vector<double> out_vec = {};
        if (!m_do_argvalue_vec[axis]) {
            double val = m_vars_vec[axis]->GetTrueValue(universe);
            for (int i = 0; i < maxidx; i++)
                out_vec.push_back(val);
            return out_vec;
        }
        for (int i = 0; i < maxidx; i++)
            out_vec.push_back(m_pointer_to_ArgGetTrueValue_vec[axis](universe,i));
        return out_vec;
    }


    int GetRecoIndex( const CVUniverse& universe) const {
        if (!m_do_argvalue) return 1;
        return m_pointer_to_RecoIndex(universe);
    }

    int GetTrueIndex( const CVUniverse& universe) const {
        if (!m_do_argvalue) return 1;
        return m_pointer_to_TrueIndex(universe);
    }

    //============================================================================
    // WRITE ALL HISTOGRAMS
    //============================================================================

    // TODO: Okay yeah will defo need a new histwrappermap class
    void WriteAllHistogramsToFile(TFile &f) {
        std::cout << "should only be called once " << std::endl;
        f.cd();

        for (auto tag : m_tags) {
            std::cout << " write out flags " << hasMC[tag] << hasSelectedTruth[tag] << hasTruth[tag] << hasData[tag] << hasTunedMC[tag] << std::endl;
            if (hasMC[tag]) {
                if (m_tunedmc != "tuned") {
                    m_selected_mc_reco.Write(tag);
                    std::cout << " write out selected mc histogram " << m_selected_mc_reco.GetHistName(tag) << std::endl;
                }
                if (hasTunedMC[tag]) {
                    m_tuned_selected_mc_reco.Write(tag);
                    std::cout << " write out tuned selected mc histogram " << m_tuned_selected_mc_reco.GetHistName(tag) << std::endl;
                }
            }
            if (hasSelectedTruth[tag]) {
                if (m_tunedmc != "tuned") {
                    std::cout << " write out selected truth histogram " << m_selected_mc_truth.GetHistName(tag) << std::endl;
                    m_selected_mc_truth.Write(tag);
                }
                if (hasTunedMC[tag]) {
                    m_tuned_selected_mc_truth.Write(tag);
                    std::cout << " write out tuned mc histogram " << m_tuned_selected_mc_truth.GetHistName(tag) << std::endl;
                }
            }
            if (hasTruth[tag]) {
                if (m_tunedmc != "tuned") {
                    std::cout << " write out truth histogram " << m_signal_mc_truth.GetHistName(tag) << std::endl;
                    m_signal_mc_truth.Write(tag);
                }
                if (hasTunedMC[tag]) {
                    m_tuned_signal_mc_truth.Write(tag);
                    std::cout << " write out tuned mc histogram " << m_tuned_signal_mc_truth.GetHistName(tag) << std::endl;
                }
            }
            if (hasResponse[tag]) {
                if (m_tunedmc != "tuned") {
                    std::cout << " write out response histograms " << tag << std::endl;
                    m_response.Write(tag);
                }
                if (hasTunedMC[tag]) {
                    std::cout << " write out tuned response histograms " << tag << std::endl;
                    m_tuned_response.Write(tag);
                }
            }
            if (hasData[tag]) {
                std::cout << " write out data histogram " << m_selected_data.GetHistName(tag) << std::endl;
                m_selected_data.Write(tag);
            }
        }
    }

    //============================================================================
    // SYNC ALL HISTOGRAMS
    //============================================================================

    void SyncAllHists() {
        for (auto tag : m_tags) {
            if (hasMC[tag]) {
                if (m_tunedmc != "tuned")
                    m_selected_mc_reco.SyncCVHistos();
                if (hasTunedMC[tag])
                    m_tuned_selected_mc_reco.SyncCVHistos();
            }
            if (hasSelectedTruth[tag]) {
                if (m_tunedmc != "tuned")
                    m_selected_mc_truth.SyncCVHistos();
                if (hasTunedMC[tag])
                    m_tuned_selected_mc_truth.SyncCVHistos();
            }
            if (hasTruth[tag]) {
                if (m_tunedmc != "tuned")
                    m_signal_mc_truth.SyncCVHistos();
                if (hasTunedMC[tag])
                    m_tuned_signal_mc_truth.SyncCVHistos();
            }
            if (hasData[tag])
                m_selected_data.SyncCVHistos();
        }
    }

};  // end of class

}  // namespace CCQENu

#endif  // VARIABLEHyperDFromConfig_H
