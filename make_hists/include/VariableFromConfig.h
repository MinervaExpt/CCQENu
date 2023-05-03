/**
 * @file
 * @author  Heidi Schellman/Noah Vaughan/SeanGilligan
 * @version 1.0 *
 * @section LICENSE *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version. *
 * @section DESCRIPTION *
 * Code to create Variables from Config file
 * @file
 * @author  Heidi Schellman/Noah Vaughan/SeanGilligan
 * @version 1.0 *
 * @section LICENSE *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version. *
 * @section DESCRIPTION *
 * Code to create Variables from Config file
 */
#ifndef VARIABLEFromConfig_H
#define VARIABLEFromConfig_H

#include "CVUniverse.h"
// #include "PlotUtils/HistFolio.h"  - gives annoying error messages
#include "HistWrapperMap.h"
// #include "PlotUtils/HistFolio.h"  - gives annoying error messages
#include "HistWrapperMap.h"
#include "MinervaUnfold/MnvResponse.h"
#include "include/ResponseWrapperMap.h"
#include "utils/NuConfig.h"
// #include "utils/UniverseDecoder.h"

#include "include/CVFunctions.h"
#ifndef __CINT__  // CINT doesn't know about std::function
#include "PlotUtils/VariableBase.h"
#endif  // __CINT__

namespace CCQENu {

class VariableFromConfig : public PlotUtils::VariableBase<CVUniverse> {
   private:
    typedef std::function<double(const CVUniverse&)> PointerToCVUniverseFunction;
    typedef HistWrapperMap<CVUniverse> HM;
    // typedef PlotUtils::HistWrapperMap<CVUniverse> HM;
    typedef ResponseWrapperMap<CVUniverse> RM;
    // typedef PlotUtils::MnvH1D MH1D;
    //  typedef PlotUtils::HistFolio<PlotUtils::MnvH1D> FOLIO;
    bool m_doresolution;

   public:
    //=======================================================================================
    // CTOR
    //=======================================================================================
    // template <class... ARGS>
    // VariableFromConfig(ARGS... args) : PlotUtils::VariableBase<CVUniverse>(args...) {}
   public:
    //=======================================================================================
    // CTOR
    //=======================================================================================
    // template <class... ARGS>
    // VariableFromConfig(ARGS... args) : PlotUtils::VariableBase<CVUniverse>(args...) {}

    // HMS 2-13-202 replace the templated constructor with explicit ones so we can make a config version without introducing a dependency in the Base class.
    // HMS 2-13-202 replace the templated constructor with explicit ones so we can make a config version without introducing a dependency in the Base class.

    void SetDoResolution(const bool doresolution) {
        m_doresolution = doresolution;
    }

    bool GetDoResolution() {
        return m_doresolution;
    }

    VariableFromConfig(const NuConfig config) {
        // config.Print();

        CVFunctions<CVUniverse> fun;
        // fun.InitFunctionMaps();
        std::string recovar = config.GetString("reco");
        bool good = false;
        for (auto key : fun.GetRecoKeys()) {
            if (recovar == key) {
                std::cout << " reco function keys " << key << std::endl;
                good = true;
                break;
            }
        }
        CVFunctions<CVUniverse> fun;
        // fun.InitFunctionMaps();
        std::string recovar = config.GetString("reco");
        bool good = false;
        for (auto key : fun.GetRecoKeys()) {
            if (recovar == key) {
                std::cout << " reco function keys " << key << std::endl;
                good = true;
                break;
            }
        }

        if (!good) {
            std::cout << "VariableFromConfig(config) is asking for an unimplemented reco variable " << recovar << std::endl;
            exit(1);
        }
        bool tgood = false;
        std::string truevar = config.GetString("true");
        for (auto key : fun.GetTrueKeys()) {
            if (truevar == key) {
                std::cout << " true function keys " << key << std::endl;
                tgood = true;
                break;
            }
        }
        if (!good) {
            std::cout << "VariableFromConfig(config) is asking for an unimplemented reco variable " << recovar << std::endl;
            exit(1);
        }
        bool tgood = false;
        std::string truevar = config.GetString("true");
        for (auto key : fun.GetTrueKeys()) {
            if (truevar == key) {
                std::cout << " true function keys " << key << std::endl;
                tgood = true;
                break;
            }
        }

        if (!tgood) {
            std::cout << "VariableFromConfig(config) is asking for an unimplemented true variable " << truevar << std::endl;
            exit(1);
        }
        if (!tgood) {
            std::cout << "VariableFromConfig(config) is asking for an unimplemented true variable " << truevar << std::endl;
            exit(1);
        }

        PlotUtils::VariableBase<CVUniverse>::m_pointer_to_GetRecoValue = (fun.GetRecoFunction(recovar));
        PlotUtils::VariableBase<CVUniverse>::m_pointer_to_GetTrueValue = (fun.GetTrueFunction(truevar));
        PlotUtils::VariableBase<CVUniverse>::m_pointer_to_GetRecoValue = (fun.GetRecoFunction(recovar));
        PlotUtils::VariableBase<CVUniverse>::m_pointer_to_GetTrueValue = (fun.GetTrueFunction(truevar));

        PlotUtils::VariableBase<CVUniverse>::m_name = config.GetString("name");
        PlotUtils::VariableBase<CVUniverse>::m_xaxis_label = config.GetString("title");
        PlotUtils::VariableBase<CVUniverse>::m_name = config.GetString("name");
        PlotUtils::VariableBase<CVUniverse>::m_xaxis_label = config.GetString("title");

        if (config.IsMember("for")) {
            m_for = config.GetStringVector("for");
        } else {  // turn them all on for now
            std::vector<std::string> def = {"data", "selected_reco", "selected_truth", "response", "truth"};
            for (auto s : def) {
                m_for.push_back(s);
            }
        }
        if (config.IsMember("for")) {
            m_for = config.GetStringVector("for");
        } else {  // turn them all on for now
            std::vector<std::string> def = {"data", "selected_reco", "selected_truth", "response", "truth"};
            for (auto s : def) {
                m_for.push_back(s);
            }
        }

        if (config.IsMember("bins")) {
            PlotUtils::VariableBase<CVUniverse>::m_binning = config.GetDoubleVector("bins");
            if (config.IsMember("recobins")) {
                PlotUtils::VariableBase<CVUniverse>::m_reco_binning = config.GetDoubleVector("recobins");
                PlotUtils::VariableBase<CVUniverse>::m_has_reco_binning = true;
            } else {
                PlotUtils::VariableBase<CVUniverse>::m_has_reco_binning = false;
            }
        } else {
            int nbins = config.GetInt("nbins");
            double xmin = config.GetDouble("min");
            double xmax = config.GetDouble("max");
            PlotUtils::VariableBase<CVUniverse>::m_binning = MakeUniformBinning(nbins, xmin, xmax);
            if (config.IsMember("nrecobins")) {
                int nrecobins = config.GetInt("nrecobins");
                double xrecomin = config.GetDouble("recomin");
                double xrecomax = config.GetDouble("recomax");
                PlotUtils::VariableBase<CVUniverse>::m_reco_binning = MakeUniformBinning(nrecobins, xrecomin, xrecomax);
            } else {
                PlotUtils::VariableBase<CVUniverse>::m_has_reco_binning = false;
            }
        }
        // std::cout << " Check Binning For" << config.GetString("name") << std::endl;
        // PrintBinning();
        // wPrintRecoBinning();
    }

    typedef std::map<std::string, std::vector<CVUniverse*>> UniverseMap;
    //=======================================================================================
    // DECLARE NEW HISTOGRAMS
    //=======================================================================================
    // Histwrappers -- selected mc, selected data

    HM m_selected_mc_reco;        // HM for normal MC hists - has special constructor to make response
    HM m_tuned_selected_mc_reco;  // HM for tuned MC hists used for background subtraction -NHV - has special constructor to make response
    HM m_selected_mc_truth;
    HM m_tuned_selected_mc_truth;
    HM m_signal_mc_truth;
    HM m_tuned_signal_mc_truth;
    HM m_selected_data;
    RM m_response;
    RM m_tuned_response;
    HM m_resolution;
    HM m_tuned_resolution;

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
    std::string m_tunedmc;  // Can be set to "both", "tuned", or "untuned"

    inline virtual std::string GetUnits() { return m_units; };

    inline virtual void SetUnits(std::string units) { m_units = units; };

    std::string GetTunedMC() { return m_tunedmc; };

    void SetTunedMC(std::string tunedmc) {
        if (tunedmc != "both" && tunedmc != "tuned" && tunedmc != "untuned") {
            std::cout << "VariableFromConfig::SetTunedMC: Warning: invalid value for \'tunedmc\' " << tunedmc << ". Defaulting to \'untuned\'." << std::endl;
            tunedmc = "untuned";
            return;
        }
        m_tunedmc = tunedmc;
    };

    //=======================================================================================
    // INITIALIZE ALL HISTOGRAMS
    //=======================================================================================

    void AddTags(const std::vector<std::string> tags) {
        for (auto t : tags) {
            m_tags.push_back(t);
        }
    };

    // all of the following could probably be the same code, sigh...
    template <typename T>
    void InitializeMCHistograms(T univs, const std::vector<std::string> tags) {
        if (std::count(m_for.begin(), m_for.end(), "selected_reco") < 1) {
            std::cout << "VariableFromConfig Warning: selected_reco is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags) {
                hasMC[tag] = false;
            }
            return;
        }
        for (auto tag : tags) {
            hasMC[tag] = true;
        }

        if (m_tunedmc == "tuned") {
            std::cout << "VariableFromConfig Warning: untuned MC disabled for this variable" << GetName() << std::endl;
            return;
        }

        std::vector<double> recobins = GetRecoBinVec();
        // need reco level binning here:
        m_selected_mc_reco = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_xaxis_label).c_str(), GetNRecoBins(), recobins, univs, tags);
        m_selected_mc_reco.AppendName("reconstructed", tags);  // patch to conform to CCQENU standard m_selected_mc_truth.AppendName("_truth",tags); // patch to conform to CCQENU standard
    }

    template <typename T>
    void InitializeSelectedTruthHistograms(T univs, const std::vector<std::string> tags) {
        if (std::count(m_for.begin(), m_for.end(), "selected_truth") < 1) {
            std::cout << "VariableFromConfig Warning: selected_truth is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags) {
                hasSelectedTruth[tag] = false;
            }
            return;
        }
        for (auto tag : tags) {
            hasSelectedTruth[tag] = true;
        }

        if (m_tunedmc == "tuned") {
            std::cout << "VariableFromConfig Warning: untuned MC disabled for this variable" << GetName() << std::endl;
            return;
        }

        std::vector<double> bins = GetBinVec();

        m_selected_mc_truth = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_xaxis_label).c_str(), GetNBins(), bins, univs, tags);
        m_selected_mc_truth.AppendName("selected_truth", tags);
        double range = bins[1] - bins[GetNBins()];

        if (m_doresolution) {
            m_resolution = HM(Form("%s_resolution", GetName().c_str()), (GetName() + ";" + m_xaxis_label + " reco-true").c_str(), 50, -range / 10., range / 10., univs, tags);
            m_resolution.AppendName("resolution", tags);
            std::cout << " created m_resolution " << GetName() << std::endl;
        }
    }

    template <typename T>
    void InitializeTruthHistograms(T univs, const std::vector<std::string> tags) {
        if (std::count(m_for.begin(), m_for.end(), "truth") < 1) {
            std::cout << "VariableFromConfig Warning: truth is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags) {
                hasTruth[tag] = false;
            }
            return;
        }
        for (auto const tag : tags) {
            hasTruth[tag] = true;
        }

        if (m_tunedmc == "tuned") {
            std::cout << "VariableFromConfig Warning: untuned MC disabled for this variable" << GetName() << std::endl;
            return;
        }

        std::vector<double> bins = GetBinVec();

        m_signal_mc_truth = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_xaxis_label).c_str(), GetNBins(), bins, univs, tags);
        m_signal_mc_truth.AppendName("all_truth", tags);
    }

    template <typename T>
    void InitializeDataHistograms(T univs, const std::vector<std::string> tags) {
        if (std::count(m_for.begin(), m_for.end(), "data") < 1) {
            std::cout << "VariableFromConfig Warning: data is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags) {
                hasData[tag] = false;
            }
            return;
        }
        for (auto tag : tags) {
            hasData[tag] = true;
        }
        std::vector<double> recobins = GetRecoBinVec();

        m_selected_data = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_xaxis_label).c_str(), GetNRecoBins(), recobins, univs, tags);
        m_selected_data.AppendName("reconstructed", tags);
    }

    template <typename T>
    void InitializeTunedMCHistograms(T reco_univs, T truth_univs, const std::vector<std::string> tuned_tags, const std::vector<std::string> response_tags) {
        if (m_tunedmc == "untuned") {
            std::cout << "VariableFromConfig Warning: tunedmc is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tuned_tags) {
                hasTunedMC[tag] = false;
            }
            return;
        }

        for (auto tag : tuned_tags) {
            hasTunedMC[tag] = true;
        }

        std::vector<double> bins = GetBinVec();
        std::vector<double> recobins = GetRecoBinVec();

        // Check which categories are configured and add a tuned version
        if (std::count(m_for.begin(), m_for.end(), "selected_reco") >= 1) {  // use recobins
            m_tuned_selected_mc_reco = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_xaxis_label).c_str(), GetNRecoBins(), recobins, reco_univs, tuned_tags);
            m_tuned_selected_mc_reco.AppendName("reconstructed_tuned", tuned_tags);
        }
        if (std::count(m_for.begin(), m_for.end(), "selected_truth") >= 1) {  // use bins
            m_tuned_selected_mc_truth = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_xaxis_label).c_str(), GetNBins(), bins, reco_univs, tuned_tags);
            m_tuned_selected_mc_truth.AppendName("selected_truth_tuned", tuned_tags);
        }
        if (std::count(m_for.begin(), m_for.end(), "truth") >= 1) {  // use bins
            m_tuned_signal_mc_truth = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_xaxis_label).c_str(), GetNBins(), bins, truth_univs, tuned_tags);
            m_tuned_signal_mc_truth.AppendName("all_truth_tuned", tuned_tags);
        }

        if (m_doresolution) {
            if (std::count(m_for.begin(), m_for.end(), "selected_truth") >= 1) {  // use bins
                double range = bins[1] - bins[GetNBins()];
                m_tuned_resolution = HM(Form("%s_resolution", GetName().c_str()), (GetName() + ";" + m_xaxis_label + " reco-true").c_str(), 50, -range / 10., range / 10., reco_univs, tuned_tags);
                m_tuned_resolution.AppendName("resolution_tuned", tuned_tags);
            }
        }

        if (std::count(m_for.begin(), m_for.end(), "response") >= 1) {
            m_tuned_response = RM(Form("%s", GetName().c_str()), reco_univs, recobins, bins, response_tags, "_tuned");
        }
    }

    //========== Add Response =================
    // reco_univs should be the same as selected_mc_reco (tuned or untuned)
    template <typename T>
    void InitializeResponse(T reco_univs, const std::vector<std::string> tags, std::string tail = "") {
        // Check if response is configured for this var
        if (std::count(m_for.begin(), m_for.end(), "response") < 1) {
            std::cout << "VariableFromConfig Warning: response is disabled for this variable " << GetName() << std::endl;
            for (auto tag : tags) {
                hasResponse[tag] = false;
            }
            return;
        }

        // Check that the var has both MC reco and truth configured, set bool to true
        for (auto tag : tags) {
            assert(hasMC[tag]);
            assert(hasSelectedTruth[tag]);
            hasResponse[tag] = true;
        }

        std::vector<double> bins = GetBinVec();
        std::vector<double> recobins = GetRecoBinVec();

        m_response = RM(Form("%s", GetName().c_str()), reco_univs, recobins, bins, tags, tail);
    }

    //============================================================================
    // WRITE ALL HISTOGRAMS
    //============================================================================

    void WriteAllHistogramsToFile(TFile& f) {
        std::cout << "should only be called once " << std::endl;
        f.cd();

        for (auto tag : m_tags) {
            std::cout << " write out flags " << hasMC[tag] << hasSelectedTruth[tag] << hasTruth[tag] << hasData[tag] << hasTunedMC[tag] << std::endl;
            if (hasMC[tag]) {
                if (m_tunedmc != "tuned") {
                    m_selected_mc_reco.Write(tag);
                    std::cout << " write out selected mc histogram " << m_selected_mc_reco.GetHist(tag)->GetName() << std::endl;
                }
                if (hasTunedMC[tag]) {
                    m_tuned_selected_mc_reco.Write(tag);
                    std::cout << " write out tuned selected mc histogram " << m_tuned_selected_mc_reco.GetHist(tag)->GetName() << std::endl;
                }
            }
            if (hasSelectedTruth[tag]) {
                if (m_tunedmc != "tuned") {
                    std::cout << " write out selected truth histogram " << m_selected_mc_truth.GetHist(tag)->GetName() << std::endl;
                    m_selected_mc_truth.Write(tag);

                    if (m_doresolution) {
                        std::cout << " write out resolution histogram " << m_resolution.GetHist(tag)->GetName() << std::endl;
                        m_resolution.Write(tag);
                        m_resolution.GetHist(tag)->Print("ALL");
                    }
                }
                if (hasTunedMC[tag]) {
                    m_tuned_selected_mc_truth.Write(tag);
                    if (m_doresolution) {
                        m_tuned_resolution.Write(tag);
                        std::cout << " write out tuned mc histogram " << m_tuned_selected_mc_truth.GetHist(tag)->GetName() << std::endl;
                        std::cout << " write out resolution histogram " << m_tuned_resolution.GetHist(tag)->GetName() << std::endl;
                    }
                }
            }
            if (hasTruth[tag]) {
                if (m_tunedmc != "tuned") {
                    std::cout << " write out truth histogram " << m_signal_mc_truth.GetHist(tag)->GetName() << std::endl;
                    m_signal_mc_truth.Write(tag);
                }
                if (hasTunedMC[tag]) {
                    m_tuned_signal_mc_truth.Write(tag);
                    std::cout << " write out tuned mc histogram " << m_tuned_signal_mc_truth.GetHist(tag)->GetName() << std::endl;
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
                std::cout << " write out data histogram " << m_selected_data.GetHist(tag)->GetName() << std::endl;
                m_selected_data.Write(tag);
            }
        }
        // f.ls();
    }

    //============================================================================
    // SYNC ALL HISTOGRAMS
    //============================================================================
    void SyncAllHists() {
        for (auto tag : m_tags) {
            if (hasMC[tag]) {
                if (m_tunedmc != "tuned") {
                    m_selected_mc_reco.SyncCVHistos();
                }
                if (hasTunedMC[tag]) {
                    m_tuned_selected_mc_reco.SyncCVHistos();
                }
            }
            if (hasSelectedTruth[tag]) {
                if (m_tunedmc != "tuned") {
                    m_selected_mc_truth.SyncCVHistos();

                    if (m_doresolution) m_resolution.SyncCVHistos();
                }
                if (hasTunedMC[tag]) {
                    m_tuned_selected_mc_truth.SyncCVHistos();
                    if (m_doresolution) m_tuned_resolution.SyncCVHistos();
                }
            }
            if (hasData[tag]) {
                m_selected_data.SyncCVHistos();
            }
            if (hasTruth[tag]) {
                if (m_tunedmc != "tuned") {
                    m_signal_mc_truth.SyncCVHistos();
                }
                if (hasTunedMC[tag]) {
                    m_tuned_signal_mc_truth.SyncCVHistos();
                }
            }
        }
    }

    void FillResponse(std::string tag, CVUniverse* univ,
                      const double value, const double truth,
                      const double weight = 1.0, const double scale = 1.0) {
        std::string name = univ->ShortName();
        // int iuniv = m_decoder[univ];

        if (hasMC[tag] && m_tunedmc != "tuned") {
            m_response.Fill(tag, univ, value, truth, weight);
        }
        if (hasTunedMC[tag] && scale >= 0.) {
            m_tuned_response.Fill(tag, univ, value, truth, weight, scale);
        }
    }

    void FillResolution(std::string tag, CVUniverse* univ,
                        const double value, const double truth,
                        const double weight = 1.0, const double scale = 1.0) {
        if (!m_doresolution) return;

        std::string name = univ->ShortName();
        // int iuniv = m_decoder[univ];

        if (hasMC[tag] && m_tunedmc != "tuned") {
            m_resolution.Fill(tag, univ, value - truth, weight);
        }
        if (hasTunedMC[tag] && scale >= 0.) {
            m_tuned_resolution.Fill(tag, univ, value - truth, weight * scale);
        }
    }

    // helper to return the actual numeric index corresponding to a universe  ie, allows map from name,index space to pure universe space.

    //  inline int UniverseIndex(CVUniverse* univ){
    //    return m_map[univ];
    //  }
    //
    //  //
};  // end of class

}  // namespace CCQENu

#endif  // VARIABLE_H
