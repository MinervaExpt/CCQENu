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
#include "HistWrapperMap.h"
#include "MinervaUnfold/MnvResponse.h"
#include "HistWrapperMap.h"
#include "include/ResponseWrapperMap.h"
#include "utils/NuConfig.h"
// #include "utils/UniverseDecoder.h"


#include "include/CVFunctions.h"
#ifndef __CINT__  // CINT doesn't know about std::function
// #include "PlotUtils/VariableBase.h"
// #include "PlotUtils/VariableHyperDBase.h"
#include "VariableHyperDBase.h"
#endif  // __CINT__


namespace CCQENu {



class VariableHyperDFromConfig : public PlotUtils::VariableHyperDBase<CVUniverse> {
private:
  typedef std::function<double(const CVUniverse&)> PointerToCVUniverseFunction;
  typedef HistWrapperMap<CVUniverse> HM; // TODO: HyperDim HistWrapper? Map?

  typedef ResponseWrapperMap<CVUniverse> RM;
  // typedef PlotUtils::MnvH1D MH1D;
  //  typedef PlotUtils::HistFolio<PlotUtils::MnvH1D> FOLIO;


public:
  //=======================================================================================
  // CTOR
  //=======================================================================================
  template <class... ARGS>
  // VariableHyperDFromConfig(ARGS... args) : PlotUtils::VariableBase<CVUniverse>(args...) {}

  // VariableHyperDFromConfig(const std::string name,
  //                           std::vector<const VariableBase<CVUniverse>&> vars) : 
  // PlotUtils::VariableHyperDBase<CVUniverse>(name, vars){};
  
  VariableHyperDFromConfig(const std::string name,
                            // const std::vector<CCQENu::VariableFromConfig>& vars,
                           const std::vector< std::unique_ptr< PlotUtils::VariableBase<CVUniverse> > > &vars,
                           const std::vector<std::string> fors) : 
  PlotUtils::VariableHyperDBase<CVUniverse>(name, vars)
  {
    if (fors.size() > 0)
    {
      for (auto s : fors)
      {
        m_for.push_back(s);
      }
    }
    else
    {
      std::vector<std::string> def = {"data", "selected_reco", "selected_truth", "response", "truth"};
      for (auto s : def)
      {
        m_for.push_back(s);
      }
    }

    // TODO: Setup tuned checks like in Var2DFromConfig
    // std::vector<int> vars_tunedmc;
  };

  // VariableHyperDFromConfig(const std::string name,
    //                          std::vector<const VariableBase<CVUniverse>&> vars,
    //                          const std::vector<std::string> fors){
    //   // I guess we can build the VariableHyperDBase by hand? Seems unneccessary...

    // }

    typedef std::map<std::string, std::vector<CVUniverse *>> UniverseMap;
    //=======================================================================================
    // DECLARE NEW HISTOGRAMS
    //=======================================================================================
    // Histwrappers -- selected mc, selected data
    // TODO: Need to do hyperdim hist/responsewrappersmaps?

    HM m_selected_mc_reco;       // HM for normal MC hists - has special constructor to make response
    HM m_tuned_selected_mc_reco; // HM for tuned MC hists used for background subtraction -NHV - has special constructor to make response
    HM m_selected_mc_truth;
    HM m_tuned_selected_mc_truth;
    HM m_signal_mc_truth;
    HM m_tuned_signal_mc_truth;
    HM m_selected_data;
    RM m_response;
    RM m_tuned_response;

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
    int m_tunedmc;
    // RESPONSE* m_response;
    //  helpers for response

    // std::map< CVUniverse* , int> m_map; // map to get name and index from Universe;
    // Histofolio to categorize MC by interaction channel
    // FOLIO m_selected_mc_by_channel;
    // FOLIO m_selected_mc_truth_by_channel;
    inline virtual std::string GetUnits() { return m_units; };

    inline virtual void SetUnits(std::string units) { m_units = units; };

    inline virtual int GetTuned() { return m_tunedmc; };
    //=======================================================================================
    // INITIALIZE ALL HISTOGRAMS
    //=======================================================================================

    void AddTags(const std::vector<std::string> tags)
    {
      for (auto t : tags)
      {
        m_tags.push_back(t);
      }
    };

    // all of the following could probably be the same code, sigh...
    template <typename T>
    void InitializeMCHistograms(T univs, const std::vector<std::string> tags)
    {
      if (std::count(m_for.begin(), m_for.end(), "selected_reco") < 1)
      {
        std::cout << "VariableHyperDFromConfig Warning: selected_reco is disabled for this variable " << GetName() << std::endl;
        for (auto tag : tags)
        {
          hasMC[tag] = false;
        }
        return;
      }
      for (auto tag : tags)
      {
        hasMC[tag] = true;
      }

      if (m_tunedmc == 1)
      {
        std::cout << "VariableHyperDFromConfig Warning: untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
        return;
      }

      std::vector<double> bins = GetBinVec();
      std::vector<double> recobins = GetRecoBinVec(); // TODO: set this up in VariableHyperDBase
      // need reco level binning here:
      // m_selected_mc_reco = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNRecoBins(), recobins, univs, tags);
      m_selected_mc_reco = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label + ";").c_str(), bins, recobins, univs, tags);
      m_selected_mc_reco.AppendName("reconstructed", tags); // patch to conform to CCQENU standard m_selected_mc_truth.AppendName("_truth",tags); // patch to conform to CCQENU standard
    }

    template <typename T>
    void InitializeSelectedTruthHistograms(T univs, const std::vector<std::string> tags)
    {
      if (std::count(m_for.begin(), m_for.end(), "selected_truth") < 1)
      {
        std::cout << "VariableHyperDFromConfig Warning: selected_truth is disabled for this variable " << GetName() << std::endl;
        for (auto tag : tags)
        {
          hasSelectedTruth[tag] = false;
        }
        return;
      }
      for (auto tag : tags)
      {
        hasSelectedTruth[tag] = true;
      }

      if (m_tunedmc == 1)
      {
        std::cout << "VariableHyperDFromConfig Warning: untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
        return;
      }

      std::vector<double> bins = GetBinVec();

      m_selected_mc_truth = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNBins(), bins, univs, tags);
      m_selected_mc_truth.AppendName("selected_truth", tags);
    }

    template <typename T>
    void InitializeTruthHistograms(T univs, const std::vector<std::string> tags)
    {
      if (std::count(m_for.begin(), m_for.end(), "truth") < 1)
      {
        std::cout << "VariableHyperDFromConfig Warning: truth is disabled for this variable " << GetName() << std::endl;
        for (auto tag : tags)
        {
          hasTruth[tag] = false;
        }
        return;
      }
      for (auto const tag : tags)
      {
        hasTruth[tag] = true;
      }

      if (m_tunedmc == 1)
      {
        std::cout << "VariableHyperDFromConfig Warning: untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
        return;
      }

      std::vector<double> bins = GetBinVec();

      m_signal_mc_truth = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNBins(), bins, univs, tags);
      m_signal_mc_truth.AppendName("all_truth", tags);
    }

    template <typename T>
    void InitializeDataHistograms(T univs, const std::vector<std::string> tags)
    {
      if (std::count(m_for.begin(), m_for.end(), "data") < 1)
      {
        std::cout << "VariableHyperDFromConfig Warning: data is disabled for this variable " << GetName() << std::endl;
        for (auto tag : tags)
        {
          hasData[tag] = false;
        }
        return;
      }
      for (auto tag : tags)
      {
        hasData[tag] = true;
      }
      std::vector<double> recobins = GetRecoBinVec();

      m_selected_data = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNRecoBins(), recobins, univs, tags);
      m_selected_data.AppendName("reconstructed", tags);
    }

    template <typename T>
    void InitializeTunedMCHistograms(T reco_univs, T truth_univs, const std::vector<std::string> tuned_tags, const std::vector<std::string> response_tags)
    {
      if (m_tunedmc < 1)
      {
        std::cout << "VariableHyperDFromConfig Warning: tunedmc is disabled for this variable " << GetName() << std::endl;
        for (auto tag : tuned_tags)
        {
          hasTunedMC[tag] = false;
        }
        return;
      }

      for (auto tag : tuned_tags)
      {
        hasTunedMC[tag] = true;
      }

      std::vector<double> bins = GetBinVec();
      std::vector<double> recobins = GetRecoBinVec();

      // Check which categories are configured and add a tuned version
      if (std::count(m_for.begin(), m_for.end(), "selected_reco") >= 1)
      { // use recobins
        m_tuned_selected_mc_reco = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNRecoBins(), recobins, reco_univs, tuned_tags);
        m_tuned_selected_mc_reco.AppendName("reconstructed_tuned", tuned_tags);
      }
      if (std::count(m_for.begin(), m_for.end(), "selected_truth") >= 1)
      { // use bins
        m_tuned_selected_mc_truth = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNBins(), bins, reco_univs, tuned_tags);
        m_tuned_selected_mc_truth.AppendName("selected_truth_tuned", tuned_tags);
      }
      if (std::count(m_for.begin(), m_for.end(), "truth") >= 1)
      { // use bins
        m_tuned_signal_mc_truth = HM(Form("%s", GetName().c_str()), (GetName() + ";" + m_lin_axis_label).c_str(), GetNBins(), bins, truth_univs, tuned_tags);
        m_tuned_signal_mc_truth.AppendName("all_truth_tuned", tuned_tags);
      }

      if (std::count(m_for.begin(), m_for.end(), "response") >= 1)
      {
        // m_response = RM(Form("%s", GetName().c_str()),reco_univs,true_univs, recobins, bins, tags);
        m_tuned_response = RM(Form("%s", GetName().c_str()), reco_univs, recobins, bins, response_tags, "_tuned");
      }
    }

    //========== Add Response =================
    // reco_univs should be the same as selected_mc_reco (tuned or untuned)
    template <typename T>
    void InitializeResponse(T reco_univs, const std::vector<std::string> tags, std::string tail = "")
    {
      // Check if response is configured for this var
      if (std::count(m_for.begin(), m_for.end(), "response") < 1)
      {
        std::cout << "VariableHyperDFromConfig Warning: response is disabled for this variable " << GetName() << std::endl;
        for (auto tag : tags)
        {
          hasResponse[tag] = false;
        }
        return;
      }

      // Check that the var has both MC reco and truth configured, set bool to true
      for (auto tag : tags)
      {
        assert(hasMC[tag]);
        assert(hasSelectedTruth[tag]);
        hasResponse[tag] = true;
      }

      std::vector<double> bins = GetBinVec();
      std::vector<double> recobins = GetRecoBinVec();

      // m_response = RM(Form("%s", GetName().c_str()),reco_univs,true_univs, recobins, bins, tags);

      m_response = RM(Form("%s", GetName().c_str()), reco_univs, recobins, bins, tags, tail);
    }

    //============================================================================
    // WRITE ALL HISTOGRAMS
    //============================================================================

    // TODO: Okay yeah will defo need a new histwrappermap class
    void WriteAllHistogramsToFile(TFile & f)
    {
      std::cout << "should only be called once " << std::endl;
      f.cd();

      for (auto tag : m_tags)
      {
        std::cout << " write out flags " << hasMC[tag] << hasSelectedTruth[tag] << hasTruth[tag] << hasData[tag] << hasTunedMC[tag] << std::endl;
        if (hasMC[tag])
        {
          if (m_tunedmc != 1)
          {
            m_selected_mc_reco.Write(tag);
            std::cout << " write out selected mc histogram " << m_selected_mc_reco.GetHist(tag)->GetName() << std::endl;
          }
          if (hasTunedMC[tag])
          {
            m_tuned_selected_mc_reco.Write(tag);
            std::cout << " write out tuned selected mc histogram " << m_tuned_selected_mc_reco.GetHist(tag)->GetName() << std::endl;
          }
        }
        if (hasSelectedTruth[tag])
        {
          if (m_tunedmc != 1)
          {
            std::cout << " write out selected truth histogram " << m_selected_mc_truth.GetHist(tag)->GetName() << std::endl;
            m_selected_mc_truth.Write(tag);
          }
          if (hasTunedMC[tag])
          {
            m_tuned_selected_mc_truth.Write(tag);
            std::cout << " write out tuned mc histogram " << m_tuned_selected_mc_truth.GetHist(tag)->GetName() << std::endl;
          }
        }
        if (hasTruth[tag])
        {
          if (m_tunedmc != 1)
          {
            std::cout << " write out truth histogram " << m_signal_mc_truth.GetHist(tag)->GetName() << std::endl;
            m_signal_mc_truth.Write(tag);
          }
          if (hasTunedMC[tag])
          {
            m_tuned_signal_mc_truth.Write(tag);
            std::cout << " write out tuned mc histogram " << m_tuned_signal_mc_truth.GetHist(tag)->GetName() << std::endl;
          }
        }
        if (hasResponse[tag])
        {
          if (m_tunedmc != 1)
          {
            std::cout << " write out response histograms " << tag << std::endl;
            m_response.Write(tag);
          }
          if (hasTunedMC[tag])
          {
            std::cout << " write out tuned response histograms " << tag << std::endl;
            m_tuned_response.Write(tag);
          }
        }
        if (hasData[tag])
        {
          std::cout << " write out data histogram " << m_selected_data.GetHist(tag)->GetName() << std::endl;
          m_selected_data.Write(tag);
        }
      }
    }

    //============================================================================
    // SYNC ALL HISTOGRAMS
    //============================================================================
    void SyncAllHists()
    {
      for (auto tag : m_tags)
      {
        if (hasMC[tag])
        {
          if (m_tunedmc != 1)
          {
            m_selected_mc_reco.SyncCVHistos();
          }
          if (hasTunedMC[tag])
          {
            m_tuned_selected_mc_reco.SyncCVHistos();
          }
        }
        if (hasSelectedTruth[tag])
        {
          if (m_tunedmc != 1)
          {
            m_selected_mc_truth.SyncCVHistos();
          }
          if (hasTunedMC[tag])
          {
            m_tuned_selected_mc_truth.SyncCVHistos();
          }
        }
        if (hasData[tag])
        {
          m_selected_data.SyncCVHistos();
        }
        if (hasTruth[tag])
        {
          if (m_tunedmc != 1)
          {
            m_signal_mc_truth.SyncCVHistos();
          }
          if (hasTunedMC[tag])
          {
            m_tuned_signal_mc_truth.SyncCVHistos();
          }
        }
        // if(hasTunedMC[tag]){
        //   m_tuned_mc_reco.SyncCVHistos();
        //   m_tuned_selected_mc_truth.SyncCVHistos();
        //   m_tuned_signal_mc_truth.SyncCVHistos();
        // }
      }
    }

    void FillResponse(std::string tag, CVUniverse * univ,
                      const double value, const double truth,
                      const double weight = 1.0, const double scale = 1.0)
    {

      std::string name = univ->ShortName();
      // int iuniv = m_decoder[univ];

      if (hasMC[tag] && m_tunedmc != 1)
      {
        m_response.Fill(tag, univ, value, truth, weight);
      }
      if (hasTunedMC[tag] && scale >= 0.)
      {
        m_tuned_response.Fill(tag, univ, value, truth, weight, scale);
      }
    }

    // helper to return the actual numeric index corresponding to a universe  ie, allows map from name,index space to pure universe space.

    //  inline int UniverseIndex(CVUniverse* univ){
    //    return m_map[univ];
    //  }
    //
    //  //
  }; // end of class

}  // namespace Ben

#endif  // VARIABLE_H
