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

    typedef HistHyperDWrapperMap<CVUniverse> HMHD;  // TODO: HyperDim HistWrapper? Map?
    typedef ResponseHyperDWrapperMap<CVUniverse> RMHD;

   public:
    //=======================================================================================
    // CTOR
    //=======================================================================================
    template <class... ARGS>

    VariableHyperDFromConfig(const std::string name,
                             const std::vector<CCQENu::VariableFromConfig *> &vars,
                             const std::vector<std::string> fors,
                             const EAnalysisType t2D_t1D = k1D) : PlotUtils::VariableHyperDBase<CVUniverse>(name, t2D_t1D) {  // Right now GetVariables isn't clever on getting "fors". Either takes in some form Variable config file, or defaults to all of them
        int tmp_tunedmc = 0;

        for (int i = 0; i < vars.size(); i++) {
            AddVariable(*vars[i]);

            // Hack to get tuned things here...
            if (vars[i]->GetTuned() > tmp_tunedmc) {
                tmp_tunedmc = vars[i]->GetTuned();
            }
        }
        m_tunedmc = tmp_tunedmc;

        // Fors isn't very sophisticated atm. Could be better.
        if (fors.size() > 0) {
            for (auto s : fors)
                m_for.push_back(s);
        } else {
            std::vector<std::string> def = {"data", "selected_reco", "selected_truth", "response", "truth"};
            for (auto s : def)
                m_for.push_back(s);
        }
        // TODO: Setup tuned checks like in Var2DFromConfig
        // std::vector<int> vars_tunedmc;
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
    int m_tunedmc;  // 0 is no tuned, 1 is only tuned, 2 is both

    inline virtual std::string GetUnits() { return m_units; };

    inline virtual void SetUnits(std::string units) { m_units = units; };

    inline virtual int GetTuned() { return m_tunedmc; };
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
            std::cout << "VariableHyperDFromConfig Warning: selected_reco is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags)
                hasMC[tag] = false;
            return;
        }
        for (auto tag : tags)
            hasMC[tag] = true;

        if (m_tunedmc == 1) {
            std::cout << "VariableHyperDFromConfig Warning: untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
            return;
        }
        std::vector<double> xrecolinbins = GetRecoBinVec();  // TODO: set this up in VariableHyperDBase
        if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
            m_selected_mc_reco = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNRecoBins(), xrecolinbins, univs, tags);
        else if (m_analysis_type == k2D || m_analysis_type == k2D_lite) {
            std::vector<double> yrecobins = GetRecoBinVec(1);
            m_selected_mc_reco = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xrecolinbins, yrecobins, univs, tags);
        }
        m_selected_mc_reco.AppendName("reconstructed", tags);  // patch to conform to CCQENU standard m_selected_mc_truth.AppendName("_truth",tags); // patch to conform to CCQENU standard
    }

    template <typename T>
    void InitializeSelectedTruthHistograms(T univs, const std::vector<std::string> tags) {
        if (std::count(m_for.begin(), m_for.end(), "selected_truth") < 1) {
            std::cout << "VariableHyperDFromConfig Warning: selected_truth is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags) {
                hasSelectedTruth[tag] = false;
            }
            return;
        }
        for (auto tag : tags) {
            hasSelectedTruth[tag] = true;
        }

        if (m_tunedmc == 1) {
            std::cout << "VariableHyperDFromConfig Warning: untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
            return;
        }

        std::vector<double> xlinbins = GetBinVec();
        if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
            m_selected_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNBins(), xlinbins, univs, tags);
        else if (m_analysis_type == k2D || m_analysis_type == k2D_lite) {
            std::vector<double> ybins = GetBinVec(1);
            m_selected_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xlinbins, ybins, univs, tags);
        }
        m_selected_mc_truth.AppendName("selected_truth", tags);
    }

    template <typename T>
    void InitializeTruthHistograms(T univs, const std::vector<std::string> tags) {
        if (std::count(m_for.begin(), m_for.end(), "truth") < 1) {
            std::cout << "VariableHyperDFromConfig Warning: truth is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags)
                hasTruth[tag] = false;
            return;
        }

        for (auto const tag : tags)
            hasTruth[tag] = true;

        if (m_tunedmc == 1) {
            std::cout << "VariableHyperDFromConfig Warning: untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
            return;
        }

        std::vector<double> xlinbins = GetBinVec();

        if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
            m_signal_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNBins(), xlinbins, univs, tags);
        else if (m_analysis_type == k2D || m_analysis_type == k2D_lite) {
            std::vector<double> ybins = GetBinVec(1);
            m_signal_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xlinbins, ybins, univs, tags);
        }
        m_signal_mc_truth.AppendName("all_truth", tags);
    }

    template <typename T>
    void InitializeDataHistograms(T univs, const std::vector<std::string> tags) {
        if (std::count(m_for.begin(), m_for.end(), "data") < 1) {
            std::cout << "VariableHyperDFromConfig Warning: data is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags)
                hasData[tag] = false;
            return;
        }
        for (auto tag : tags)
            hasData[tag] = true;
        std::vector<double> xrecolinbins = GetRecoBinVec();
        if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
            m_selected_data = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNRecoBins(), xrecolinbins, univs, tags);
        else if (m_analysis_type == k2D || m_analysis_type == k2D_lite) {
            std::vector<double> yrecobins = GetRecoBinVec(1);
            m_selected_data = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xrecolinbins, yrecobins, univs, tags);
        }
        m_selected_data.AppendName("reconstructed", tags);
    }

    template <typename T>
    void InitializeTunedMCHistograms(T reco_univs, T truth_univs, const std::vector<std::string> tuned_tags, const std::vector<std::string> response_tags) {
        if (m_tunedmc < 1) {
            std::cout << "VariableHyperDFromConfig Warning: tunedmc is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tuned_tags)
                hasTunedMC[tag] = false;
            return;
        }

        for (auto tag : tuned_tags)
            hasTunedMC[tag] = true;

        std::vector<double> xlinbins = GetBinVec();
        std::vector<double> xrecolinbins = GetRecoBinVec();

        // Only used if doing a 2D type 0 analysis
        std::vector<double> ybins = GetBinVec(1);
        std::vector<double> yrecobins = GetRecoBinVec(1);

        // Check which categories are configured and add a tuned version
        if (std::count(m_for.begin(), m_for.end(), "selected_reco") >= 1) {  // use recobins
            if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
                m_tuned_selected_mc_reco = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNRecoBins(), xrecolinbins, reco_univs, tuned_tags);
            else if (m_analysis_type == k2D || m_analysis_type == k2D_lite)
                m_tuned_selected_mc_reco = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xrecolinbins, yrecobins, reco_univs, tuned_tags);
            m_tuned_selected_mc_reco.AppendName("reconstructed_tuned", tuned_tags);
        }
        if (std::count(m_for.begin(), m_for.end(), "selected_truth") >= 1) {  // use bins
            if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
                m_tuned_selected_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNBins(), xlinbins, reco_univs, tuned_tags);
            else if (m_analysis_type == k2D || m_analysis_type == k2D_lite)
                m_tuned_selected_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xlinbins, ybins, reco_univs, tuned_tags);
            m_tuned_selected_mc_truth.AppendName("selected_truth_tuned", tuned_tags);
        }
        if (std::count(m_for.begin(), m_for.end(), "truth") >= 1) {  // use bins
            if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
                m_tuned_signal_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNBins(), xlinbins, truth_univs, tuned_tags);
            else if (m_analysis_type == k2D || m_analysis_type == k2D_lite)
                m_tuned_signal_mc_truth = HMHD(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";" + m_y_axis_label).c_str(), xlinbins, ybins, truth_univs, tuned_tags);
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
            std::cout << "VariableHyperDFromConfig Warning: response is disabled for this variable " << GetName() << std::endl;
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
            std::cout << "VariableHyperDFromConfig: FillResponse2D: Set to analysis type " << m_analysis_type << ". Will not fill response for 1D HyperD hists." << std::endl;
            return;
        }

        std::string name = univ->ShortName();
        // int iuniv = m_decoder[univ];
        if (hasMC[tag] && m_tunedmc != 1)
            m_response.Fill(tag, univ, value, truth, weight);
        if (hasTunedMC[tag] && scale >= 0.)
            m_tuned_response.Fill(tag, univ, value, truth, weight, scale);
    }

    void FillResponse(const std::string tag, CVUniverse *univ,
                      const double x_value, const double y_value,
                      const double x_truth, const double y_truth,
                      const double weight, const double scale = 1.0)  // From Hist2DWrapperMap
    {
        if (m_analysis_type != k2D) { // skip if not 2D type 0 analysis
            std::cout << "VariableHyperDFromConfig: FillResponse: Set to analysis type " << m_analysis_type << ". Will not fill response for 2D HyperD hists." << std::endl;
            return;
        }

        std::string name = univ->ShortName();
        if (hasMC[tag] && m_tunedmc != 1)
            m_response.Fill(tag, univ, x_value, y_value, x_truth, y_truth, weight);  // value here is reco
        if (hasTunedMC[tag] && scale >= 0.)
            m_tuned_response.Fill(tag, univ, x_value, y_value, x_truth, y_truth, weight, scale);  // value here is reco
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
                if (m_tunedmc != 1) {
                    m_selected_mc_reco.Write(tag);
                    std::cout << " write out selected mc histogram " << m_selected_mc_reco.GetHistName(tag) << std::endl;
                }
                if (hasTunedMC[tag]) {
                    m_tuned_selected_mc_reco.Write(tag);
                    std::cout << " write out tuned selected mc histogram " << m_tuned_selected_mc_reco.GetHistName(tag) << std::endl;
                }
            }
            if (hasSelectedTruth[tag]) {
                if (m_tunedmc != 1) {
                    std::cout << " write out selected truth histogram " << m_selected_mc_truth.GetHistName(tag) << std::endl;
                    m_selected_mc_truth.Write(tag);
                }
                if (hasTunedMC[tag]) {
                    m_tuned_selected_mc_truth.Write(tag);
                    std::cout << " write out tuned mc histogram " << m_tuned_selected_mc_truth.GetHistName(tag) << std::endl;
                }
            }
            if (hasTruth[tag]) {
                if (m_tunedmc != 1) {
                    std::cout << " write out truth histogram " << m_signal_mc_truth.GetHistName(tag) << std::endl;
                    m_signal_mc_truth.Write(tag);
                }
                if (hasTunedMC[tag]) {
                    m_tuned_signal_mc_truth.Write(tag);
                    std::cout << " write out tuned mc histogram " << m_tuned_signal_mc_truth.GetHistName(tag) << std::endl;
                }
            }
            if (hasResponse[tag]) {
                if (m_tunedmc != 1) {
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
                if (m_tunedmc != 1)
                    m_selected_mc_reco.SyncCVHistos();
                if (hasTunedMC[tag])
                    m_tuned_selected_mc_reco.SyncCVHistos();
            }
            if (hasSelectedTruth[tag]) {
                if (m_tunedmc != 1)
                    m_selected_mc_truth.SyncCVHistos();
                if (hasTunedMC[tag])
                    m_tuned_selected_mc_truth.SyncCVHistos();
            }
            if (hasTruth[tag]) {
                if (m_tunedmc != 1)
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
