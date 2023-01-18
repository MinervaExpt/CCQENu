#ifndef VARIABLEHYPERDFromConfig_H
#define VARIABLEHYPERDFromConfig_H

#include "CVUniverse.h"
#include "VariableFromConfig.h"
//#include "PlotUtils/HistFolio.h"  - gives annoying error messages
#include "HistWrapperMap.h"
#include "MinervaUnfold/MnvResponse.h"
#include "utils/NuConfig.h"
#include "PlotUtils/HyperDimLinearizer.h"


#include "include/CVFunctions.h"
#ifndef __CINT__  // CINT doesn't know about std::function
#include "PlotUtils/VariableBase.h"
#endif  // __CINT__


namespace CCQENu {



class VariableHyperDFromConfig : public VariableHyperDBase<CVUniverse> {
private:
  typedef std::function<double(const CVUniverse&)> PointerToCVUniverseFunction;
  typedef PlotUtils::HistWrapperMap<CVUniverse> HM;
  typedef PlotUtils::MnvH1D MH1D;
  typedef PlotUtils::HyperDimLinearizer HyperDL;
  //  typedef PlotUtils::HistFolio<PlotUtils::MnvH1D> FOLIO;


public:
  VariableHyperDFromConfig(const NuConfig config,
                           std::vector<const CCQENu:VariableFromConfig<CVUniverse>&> vars1D,
                           const std::vector<std::string> fors){

    PlotUtils::VariableHyperDBase<CVUniverse>::m_name = config.GetString("name");

    for(auto var:vars1D){
      m_varbins.push_back(var->GetbinVec());
      m_axis_label_vec.push_back(var->GetAxisLabel());
    }
    m_hyperdim = new HyperDL(m_varbins,0);

    int n_bins_lin = 1;
    // Found out number of bins in variable space.
    // Bin vecs are n_bins+1, so we add +1 more to also account for under/overflow
    for(auto vec:m_varbins){n_bins_lin *= (vec.size()+1)}
    // Now use that to make a vector of bin edges in bin space
    for(int i=0; i<n_bins_lin; i++){m_lin_bins.push_back(i)}

    if (fors.size()>0){
      for (auto s:fors){
        m_for.push_back(s);
      }
    }
    else{
      std::vector<std::string> def = {"data","selected_reco","tuned_mc","selected_truth","response","truth"};
      for (auto s:def){
        m_for.push_back(s);
      }
    }
  }

  typedef std::map<std::string, std::vector<CVUniverse*>> UniverseMap;
  //=======================================================================================
  // DECLARE NEW HISTOGRAMS
  //=======================================================================================
  // Histwrappers -- selected mc, selected data

  HM m_selected_mc_reco;
  HM m_tuned_mc_reco; // HM for tuned MC hists used for background subtraction -NHV
  HM m_selected_mc_truth;
  HM m_tuned_selected_mc_truth;
  HM m_signal_mc_truth;
  HM m_tuned_signal_mc_truth;
  HM m_selected_data;

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

  std::vector<std::vector<double>> m_varbins; // This a list of the bin edge vectors for the variable space
  std::vector<double> m_linbins;
  HyperDL m_hyperdim;
  std::vector<std::string> m_axis_label_vec;


  inline virtual std::string GetUnits(){return m_units;};

  inline virtual void SetUnits(std::string units){m_units=units;};

  //=======================================================================================
  // INITIALIZE ALL HISTOGRAMS
  //=======================================================================================


  void AddTags(const std::vector<std::string> tags){
    for(auto t:tags){
      m_tags.push_back(t);
    }
  };

  // all of the following could probably be the same code, sigh...
  template <typename T>
  void InitializeMCHistograms(T univs, const std::vector< std::string> tags) {
    if (std::count(m_for.begin(), m_for.end(),"selected_reco")< 1) {
      std::cout << "VariableFromConfig Warning: selected_reco is disabled for this variable " << GetName() << std::endl;
      for (auto tag:tags){
        hasMC[tag] = false;
      }
      return;
    }
    for (auto tag:tags){
      hasMC[tag] = true;
    }
    std::vector<double> bins = GetBinVec();
    m_selected_mc_reco = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNBins(), bins, univs, tags);
    m_selected_mc_reco.AppendName("reconstructed",tags); // patch to conform to CCQENU standard m_selected_mc_truth.AppendName("_truth",tags); // patch to conform to CCQENU standard
  }

  template <typename T>
  void InitializeSelectedTruthHistograms(T univs, const std::vector<std::string> tags) {
    if (std::count(m_for.begin(), m_for.end(),"selected_truth")< 1) {
      std::cout << "VariableFromConfig Warning: selected_truth is disabled for this variable " << GetName() << std::endl;
      for (auto tag:tags){
        hasSelectedTruth[tag] = false;
      }
      return;
    }
    for (auto tag:tags){
      hasSelectedTruth[tag] = true;
    }
    std::vector<double> bins = GetBinVec();

    m_selected_mc_truth = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNBins(), bins, univs, tags);
    m_selected_mc_truth.AppendName("selected_truth",tags);
  }

  template <typename T>
  void InitializeTruthHistograms(T univs, const std::vector< std::string> tags) {
    if (std::count(m_for.begin(), m_for.end(),"truth")< 1) {
      std::cout << "VariableFromConfig Warning: truth is disabled for this variable " << GetName() << std::endl;
      for (auto tag:tags){
        hasTruth[tag] = false;
      }
      return;
    }
    for (auto const tag:tags){
      hasTruth[tag] = true;
    }
    std::vector<double> bins = GetBinVec();

    m_signal_mc_truth = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNBins(), bins, univs, tags);
    m_signal_mc_truth.AppendName("all_truth",tags);
  }

  template <typename T>
  void InitializeDataHistograms(T univs, const std::vector< std::string> tags) {
    if (std::count(m_for.begin(), m_for.end(),"data")< 1)  {
      std::cout << "VariableFromConfig Warning: data is disabled for this variable " << GetName() << std::endl;
      for (auto tag:tags){
        hasData[tag] = false;
      }
      return;
    }
    for (auto tag:tags){
      hasData[tag] = true;
    }
    std::vector<double> bins = GetBinVec();

    m_selected_data = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNBins(), bins, univs,tags);
    m_selected_data.AppendName("reconstructed",tags);
  }

  template <typename T>
  void InitializeTunedMCHistograms(T reco_univs, T truth_univs, const std::vector< std::string> tuned_tags, const std::vector< std::string> response_tags) {
    if (std::count(m_for.begin(), m_for.end(),"tuned_mc")< 1) {
      std::cout << "VariableFromConfig Warning: tuned_mc is disabled for this variable " << GetName() << std::endl;
      for (auto tag:tuned_tags){
        hasTunedMC[tag] = false;
      }
      return;
    }
    for (auto tag:tuned_tags){
      hasTunedMC[tag] = true;
    }
    std::vector<double> bins = GetBinVec();

    // Check which categories are configured and add a tuned version
    if (std::count(m_for.begin(), m_for.end(),"selected_reco")>=1){
      m_tuned_mc_reco = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNBins(), bins, reco_univs, tuned_tags);
      m_tuned_mc_reco.AppendName("reconstructed_tuned",tuned_tags);
    }
    if (std::count(m_for.begin(), m_for.end(),"selected_truth")>=1) {
      m_tuned_selected_mc_truth = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNBins(), bins, reco_univs, tuned_tags);
      m_tuned_selected_mc_truth.AppendName("selected_truth_tuned",tuned_tags);
    }
    if (std::count(m_for.begin(), m_for.end(),"truth")>=1) {
      m_tuned_signal_mc_truth = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNBins(), bins, truth_univs, tuned_tags);
      m_tuned_signal_mc_truth.AppendName("all_truth_tuned",tuned_tags);
    }

    // Now do response
    if (std::count(m_for.begin(), m_for.end(),"response")< 1) {
      std::cout << "VariableFromConfig Warning: response is disabled for this variable " << GetName() << std::endl;
      for (auto tag:response_tags){
        hasResponse[tag] = false;
      }
      return;
    }
    for (auto tag:response_tags){
      assert(hasTunedMC[tag]);
      assert(hasSelectedTruth[tag]);
    }
    m_tuned_mc_reco.AddResponse(response_tags,"_tuned");
  }


  //========== Add Response =================

  void AddMCResponse(const std::vector<std::string>  tags) {
    if (std::count(m_for.begin(), m_for.end(),"response")< 1) {
      std::cout << "VariableFromConfig Warning: response is disabled for this variable " << GetName() << std::endl;
      for (auto tag:tags){
        hasResponse[tag] = false;
      }
      return;
    }
    for (auto tag:tags){
      assert(hasMC[tag]);
      assert(hasSelectedTruth[tag]);
    }
    m_selected_mc_reco.AddResponse(tags);

    for (auto tag:tags){
      hasResponse[tag] = true;
    }
  }


  //============================================================================
  // WRITE ALL HISTOGRAMS
  //============================================================================
  void WriteAllHistogramsToFile(TFile& f)  {
    std::cout << "should only be called once " << std::endl;
    f.cd();

    for (auto tag:m_tags){
      std::cout << " write out flags " << hasMC[tag] << hasTunedMC[tag] << hasSelectedTruth[tag] << hasTruth[tag] << hasData[tag] <<  std::endl;
      if(hasMC[tag]){
        m_selected_mc_reco.Write(tag);
        std::cout << " write out mc histogram " << m_selected_mc_reco.GetHist(tag)->GetName() << std::endl;
        if(hasTunedMC[tag]){
          m_tuned_mc_reco.Write(tag);
          std::cout << " write out tuned mc histogram " << m_tuned_mc_reco.GetHist(tag)->GetName() << std::endl;
        }
      }
      if(hasSelectedTruth[tag]){
        std::cout << " write out selected truth histogram " << m_selected_mc_truth.GetHist(tag)->GetName() << std::endl;
        m_selected_mc_truth.Write(tag);
        if(hasTunedMC[tag]){
          m_tuned_selected_mc_truth.Write(tag);
          std::cout << " write out tuned mc histogram " << m_tuned_selected_mc_truth.GetHist(tag)->GetName() << std::endl;
        }
      }
      if(hasTruth[tag]){
        std::cout << " write out truth histogram " << m_signal_mc_truth.GetHist(tag)->GetName() << std::endl;
        m_signal_mc_truth.Write(tag);
        if(hasTunedMC[tag]){
          m_tuned_signal_mc_truth.Write(tag);
          std::cout << " write out tuned mc histogram " << m_tuned_signal_mc_truth.GetHist(tag)->GetName() << std::endl;
        }
      }
      if(hasData[tag]){
        std::cout << " write out data histogram " << m_selected_data.GetHist(tag)->GetName() << std::endl;
        m_selected_data.Write(tag);
      }
    }
  }

  //============================================================================
  // SYNC ALL HISTOGRAMS
  //============================================================================
  void SyncAllHists() {
    for (auto tag:m_tags){
      if(hasMC[tag]){
        m_selected_mc_reco.SyncCVHistos();
        if(hasTunedMC[tag]){
          m_tuned_mc_reco.SyncCVHistos();
        }
      }
      if(hasSelectedTruth[tag]){
        m_selected_mc_truth.SyncCVHistos();
        if(hasTunedMC[tag]){
          m_tuned_selected_mc_truth.SyncCVHistos();
        }
      }
      if(hasData[tag]){
        m_selected_data.SyncCVHistos();
      }
      if(hasTruth[tag]){
        m_signal_mc_truth.SyncCVHistos();
        if(hasTunedMC[tag]){
          m_tuned_signal_mc_truth.SyncCVHistos();
        }
      }
    }
  }

  inline void FillResponse(std::string tag, CVUniverse* univ, const double value, const double truth, const double weight=1.0, const double scale=1.0){
    if(hasMC[tag]){
      m_selected_mc_reco.FillResponse(tag, univ, value, truth, weight);
    }
    if(hasTunedMC[tag]){
      m_tuned_mc_reco.FillResponse(tag, univ, value, truth, weight);
    }
  }
};  //end of class



}  // namespace Ben

#endif  // VARIABLE_H
