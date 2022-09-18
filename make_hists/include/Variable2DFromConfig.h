#ifndef VARIABLE2DFromConfig_H
#define VARIABLE2DFromConfig_H

#include "CVUniverse.h"
// #include "PlotUtils/HistFolio.h"
#include "HistWrapperMap.h"
#include "Hist2DWrapperMap.h" //TODO: Need to make this to play wit Hist2DWrapper
#include "MinervaUnfold/MnvResponse.h"


#ifndef __CINT__  // CINT doesn't know about std::function
#include "PlotUtils/Variable2DBase.h"
#endif  // __CINT__

namespace CCQENu {

class Variable2DFromConfig : public PlotUtils::Variable2DBase<CVUniverse> {
private:
  typedef PlotUtils::Hist2DWrapperMap<CVUniverse> HM2D;

  typedef PlotUtils::MnvH1D MH1D;
  typedef PlotUtils::MnvH2D MH2D;
  // typedef PlotUtils::HistFolio<PlotUtils::MnvH1D> FOLIO;
  // typedef PlotUtils::HistFolio<PlotUtils::MnvH2D> FOLIO2D;


public:
  //=======================================================================================
  // CTOR
  //=======================================================================================
  template <class... ARGS>
  // Variable2DFromConfig(ARGS... args) : PlotUtils::Variable2DBase<CVUniverse>(args...) {}

  // NHV 3/16/21 replace templated version with explicit ones so we can use a config without changing the base class.

  Variable2DFromConfig(const std::string name,
                       const VariableBase<CVUniverse>& x,
                       const VariableBase<CVUniverse>& y) :
  PlotUtils::Variable2DBase<CVUniverse>(name, x, y ){
    std::vector<std::string> def = {"data","selected_reco","selected_truth","response","truth"};
   for (auto s:def){
     m_for.push_back(s);
   }
  };

  Variable2DFromConfig(const VariableBase<CVUniverse>& x,
                       const VariableBase<CVUniverse>& y) :
  PlotUtils::Variable2DBase<CVUniverse>(x, y ){
    std::vector<std::string> def = {"data","selected_reco","selected_truth","response","truth"};
   for (auto s:def){
     m_for.push_back(s);
   }
  };

  Variable2DFromConfig(const std::string name,
                       const VariableBase<CVUniverse>& x,
                       const VariableBase<CVUniverse>& y,
                       const NuConfig config) :
  PlotUtils::Variable2DBase<CVUniverse>(name, x, y){
    if (config.IsMember("for")){
      m_for = config.GetStringVector("for");
    }
    else{
      std::vector<std::string> def = {"data","selected_reco","selected_truth","response","truth"};
      for (auto s:def){
        m_for.push_back(s);
      }
    }
  };

  Variable2DFromConfig(const std::string name,
                       const CCQENu::VariableFromConfig& x,
                       const CCQENu::VariableFromConfig& y,
                       const std::vector<std::string> fors) :
  PlotUtils::Variable2DBase<CVUniverse>(name, x, y){
    if (fors.size()>0){
      for (auto s:fors){
        m_for.push_back(s);
      }
    }
    else{
      std::vector<std::string> def = {"data","selected_reco","selected_truth","response","truth"};
      for (auto s:def){
        m_for.push_back(s);
      }
    }

    int x_tunedmc = x.m_tunedmc;
    int y_tunedmc = y.m_tunedmc;
    if(x_tunedmc==y_tunedmc){
      m_tunedmc=x_tunedmc;
    }
    else if(x_tunedmc!=2 && y_tunedmc!=2){
      std::cout << "Variable2DFromConfig: Incompatible 'tunedmc' from input. Setting to run both tuned and untuned. " << std::endl;
      m_tunedmc=2;
    }
    else if(x_tunedmc==1 || y_tunedmc==1){
      m_tunedmc=1; //Should default be 2?
    }
    else if(x_tunedmc==0 || y_tunedmc==0){
      m_tunedmc=0;
    }
    else{
      m_tunedmc=2;
    }
  };


  typedef std::map<std::string, std::vector<CVUniverse*>> UniverseMap;
  //=======================================================================================
  // DECLARE NEW HISTOGRAMS
  //=======================================================================================
  // Histwrappers -- selected mc, selected data

  HM2D m_selected_mc_reco;
  HM2D m_tuned_mc_reco; // HM for tuned MC hists used for background subtraction -NHV
  HM2D m_selected_mc_truth;
  HM2D m_tuned_selected_mc_truth;
  HM2D m_signal_mc_truth;
  HM2D m_tuned_signal_mc_truth;
  HM2D m_selected_data;
  UniverseMap m_universes; //need to change this?
  std::string m_units;
  std::map<const std::string, bool> hasData;
  std::map<const std::string, bool> hasMC;
  std::map<const std::string, bool> hasTunedMC;
  std::map<const std::string, bool> hasTruth;
  std::map<const std::string, bool> hasSelectedTruth;
  std::map<const std::string, bool> hasResponse;
  std::vector<std::string> m_tags;
  std::vector<std::string> m_for;
  int m_tunedmc;
  //RESPONSE* m_response;
  // helpers for response

  // std::map< CVUniverse* , int> m_map; // map to get name and index from Universe;
  // Histofolio to categorize MC by interaction channel
  //FOLIO m_selected_mc_by_channel;
  //FOLIO m_selected_mc_truth_by_channel;
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

  template <typename T>
  void InitializeMCHistograms2D(T univs, const std::vector<std::string> tags) {
    if (std::count(m_for.begin(), m_for.end(),"selected_reco")< 1) {
      std::cout << "Variable2DFromConfig Warning: selected_reco is disabled for this 2D variable " << GetName() << std::endl;
      for (auto tag:tags){
        hasMC[tag] = false;
      }
      return;
    }
    for (auto tag:tags){
      hasMC[tag] = true;
    }

    if(m_tunedmc==1){
      std::cout << "Variable2DFromConfig Warning: untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
      return;
    }

    std::vector<double> xbins = GetBinVecX();
    std::vector<double> ybins = GetBinVecY();

    m_selected_mc_reco = HM2D(Form("%s",GetName().c_str()), (GetName()+";"+m_xaxis_label+";"+m_yaxis_label).c_str(), xbins, ybins, univs, tags); //Hist2DWrapper doesn't need nbins for variable binning
    m_selected_mc_reco.AppendName("reconstructed",tags);
  }

  template <typename T>
  void InitializeSelectedTruthHistograms2D(T univs, const std::vector<std::string> tags) {
    if (std::count(m_for.begin(), m_for.end(),"selected_truth")< 1) {
      std::cout << "Variable2DFromConfig Warning: selected_truth is disabled for this 2D variable " << GetName() << std::endl;
      for (auto tag:tags){
        hasSelectedTruth[tag] = false;
      }
      return;
    }
    for (auto tag:tags){
      hasSelectedTruth[tag] = true;
    }

    if(m_tunedmc==1){
      std::cout << "Variable2DFromConfig Warning: untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
      return;
    }

    std::vector<double> xbins = GetBinVecX();
    std::vector<double> ybins = GetBinVecY();

    m_selected_mc_truth = HM2D(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label+";"+m_yaxis_label).c_str(), xbins, ybins, univs, tags); //Hist2DWrapper doesn't need nbins for variable binning
    m_selected_mc_truth.AppendName("selected_truth",tags); // patch to conform to CCQENU standardm_selected_mc_truth.AppendName("_truth",tags); // patch to conform to CCQENU standard
  }


  template <typename T>
  void InitializeTruthHistograms2D(T univs, const std::vector<std::string> tags) {
    if (std::count(m_for.begin(), m_for.end(),"truth")< 1) {
      std::cout << "Variable2DFromConfig Warning: truth is disabled for this 2D variable " << GetName() << std::endl;
      for (auto tag:tags){
        hasTruth[tag] = false;
      }
      return;
    }
    for (auto const tag:tags){
      hasTruth[tag] = true;
    }

    if(m_tunedmc==1){
      std::cout << "Variable2DFromConfig Warning: untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
      return;
    }

    std::vector<double> xbins = GetBinVecX();
    std::vector<double> ybins = GetBinVecY();


    m_signal_mc_truth = HM2D(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label+";"+m_yaxis_label).c_str(), xbins, ybins, univs, tags);
    m_signal_mc_truth.AppendName("all_truth",tags);
  }

  //  void AddTruthWrapper(std::string tag){
  //     m_signal_mc_truth.AddResponse(tag);
  //  }

  template <typename T>
  void InitializeDataHistograms2D(T univs, const std::vector<std::string> tags) {
    if (std::count(m_for.begin(), m_for.end(),"data")< 1)  {
      std::cout << "Variable2DFromConfig Warning: data is disabled for this variable " << GetName() << std::endl;
      for (auto tag:tags){
        hasData[tag] = false;
      }
      return;
    }
    for (auto tag:tags){
      hasData[tag] = true;
    }
    std::vector<double> xbins = GetBinVecX();
    std::vector<double> ybins = GetBinVecY();

    m_selected_data = HM2D(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label+";"+m_yaxis_label).c_str(), xbins, ybins, univs, tags); //Hist2DWrapper doesn't need nbins for variable binning
    m_selected_data.AppendName("reconstructed",tags);
  }

  template <typename T>
  void InitializeTunedMCHistograms2D(T reco_univs, T truth_univs, const std::vector< std::string> tuned_tags, const std::vector< std::string> response_tags) {
    if(m_tunedmc<1){
      std::cout << "Variable2DFromConfig Warning: tunedmc is disabled for this variable " << GetName() << std::endl;
      for (auto tag:tuned_tags){
        hasTunedMC[tag] = false;
      }
      return;
    }
    for (auto tag:tuned_tags){
      hasTunedMC[tag] = true;
    }
    std::vector<double> xbins = GetBinVecX();
    std::vector<double> ybins = GetBinVecY();

    // Check which categories are configured and add a tuned version
    if (std::count(m_for.begin(), m_for.end(),"selected_reco")>=1){
      m_tuned_mc_reco = HM2D(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label+";"+m_yaxis_label).c_str(), xbins, ybins, reco_univs, tuned_tags);
      m_tuned_mc_reco.AppendName("reconstructed_tuned",tuned_tags);
    }
    if (std::count(m_for.begin(), m_for.end(),"selected_truth")>=1) {
      m_tuned_selected_mc_truth = HM2D(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label+";"+m_yaxis_label).c_str(), xbins, ybins, reco_univs, tuned_tags);
      m_tuned_selected_mc_truth.AppendName("selected_truth_tuned",tuned_tags);
    }
    if (std::count(m_for.begin(), m_for.end(),"truth")>=1) {
      m_tuned_signal_mc_truth = HM2D(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label+";"+m_yaxis_label).c_str(), xbins, ybins, truth_univs, tuned_tags);
      m_tuned_signal_mc_truth.AppendName("all_truth_tuned",tuned_tags);
    }

    // Now do response
    if (std::count(m_for.begin(), m_for.end(),"response")< 1) {
      std::cout << "Variable2DFromConfig Warning: response is disabled for this variable " << GetName() << std::endl;
      for (auto tag:response_tags){
        hasResponse[tag] = false;
      }
      return;
    }
    for (auto tag:response_tags){
      assert(hasTunedMC[tag]);
      assert(hasSelectedTruth[tag]);
    }
    m_tuned_mc_reco.AddResponse2D(response_tags,"_tuned");
  }

  //========== Add Response =================


  void AddMCResponse2D(const std::vector<std::string>  tags) { //Does this take in True at all?
    if (std::count(m_for.begin(), m_for.end(),"response")< 1) {
      std::cout << "Variable2DFromConfig Warning: response is disabled for this variable " << GetName() << std::endl;
      for (auto tag:tags){
        hasResponse[tag] = false;
      }
      return;
    }
    for (auto tag:tags){
      assert(hasMC[tag]);
    }

    if(m_tunedmc==1){
      std::cout << "Variable2DFromConfig Warning: untuned MC disabled. Disabling untuned response for this variable " << GetName() << std::endl;
      return;
    }

    m_selected_mc_reco.AddResponse2D(tags);
    for (auto tag:tags){
      hasResponse[tag] = true;
    }
  }

  //=======================================================================================
  // WRITE ALL HISTOGRAMS
  //=======================================================================================
  // Does it make sense to have separate implementation of 2D Writes? Is it smart enough to know the difference?
  void WriteAllHistogramsToFile2D(TFile& f)  {
    std::cout << "should only be called once " << std::endl;
    f.cd();
    // selected mc reco

    for (auto tag:m_tags){
      std::cout << " write out flags " << hasMC[tag] << hasTunedMC[tag] << hasTruth[tag] << hasData[tag] <<  std::endl;
      if(hasMC[tag]) {
        if(m_tunedmc!=1){
          m_selected_mc_reco.Write(tag);
          std::cout << " write out mc histogram " << m_selected_mc_reco.GetHist(tag)->GetName() << std::endl;
        }
        if(hasTunedMC[tag]){
          m_tuned_mc_reco.Write(tag);
          std::cout << " write out tuned mc histogram " << m_tuned_mc_reco.GetHist(tag)->GetName() << std::endl;
        }
      }
      if(hasSelectedTruth[tag]){
        if(m_tunedmc!=1){
          m_selected_mc_truth.Write(tag);
          std::cout << " write out truth histogram " << m_selected_mc_truth.GetHist(tag)->GetName() << std::endl;
        }
        if(hasTunedMC[tag]){
          m_tuned_selected_mc_truth.Write(tag);
          std::cout << " write out tuned mc histogram " << m_tuned_selected_mc_truth.GetHist(tag)->GetName() << std::endl;
        }
      }
      if(hasTruth[tag]){
        if(m_tunedmc!=1){
          m_signal_mc_truth.Write(tag);
          std::cout << " write out truth histogram " << m_signal_mc_truth.GetHist(tag)->GetName() << std::endl;
        }
        if(hasTunedMC[tag]){
          m_tuned_signal_mc_truth.Write(tag);
          std::cout << " write out tuned mc histogram " << m_tuned_signal_mc_truth.GetHist(tag)->GetName() << std::endl;
        }
      }
      if(hasData[tag]){
        m_selected_data.Write(tag);
        std::cout << " write out data histogram " << m_selected_data.GetHist(tag)->GetName() << std::endl;
      }
    }
  }

  //=======================================================================================
  // SYNC ALL HISTOGRAMS
  //=======================================================================================
  void SyncAllHists() {
    for (auto tag:m_tags){
      if(hasMC[tag]){
        if(m_tunedmc!=1){
          m_selected_mc_reco.SyncCVHistos();
        }
        if(hasTunedMC[tag]){
          m_tuned_mc_reco.SyncCVHistos();
        }
      }
      if(hasSelectedTruth[tag]){
        if(m_tunedmc!=1){
          m_selected_mc_truth.SyncCVHistos();
        }
        if(hasTunedMC[tag]){
          m_tuned_selected_mc_truth.SyncCVHistos();
        }
      }
      if(hasData[tag]){
        m_selected_data.SyncCVHistos();
      }
      if(hasTruth[tag]){
        if(m_tunedmc!=1){
          m_signal_mc_truth.SyncCVHistos();
        }
        if(hasTunedMC[tag]){
          m_tuned_signal_mc_truth.SyncCVHistos();
        }
      }
    }
  }



  inline void FillResponse2D(const std::string tag, CVUniverse* univ, const double x_value, const double y_value, const double x_truth, const double y_truth, const double weight, const double scale=1.0){ //From Hist2DWrapperMap
    if(hasMC[tag] && m_tunedmc!=1){
      m_selected_mc_reco.FillResponse2D(tag, univ, x_value, y_value, x_truth, y_truth, weight, 1.0); //value here is reco
    }
    if(hasTunedMC[tag]){
      m_tuned_mc_reco.FillResponse2D(tag, univ, x_value, y_value, x_truth, y_truth, weight, scale); //value here is reco
    }
  }

  // helper to return the actual numeric index corresponding to a universe  ie, allows map from name,index space to pure universe space.

  //  inline int UniverseIndex(CVUniverse* univ){
  //    return m_map[univ];
  //  }
  //
  //  //
};

}  // namespace Ben

#endif  // VARIABLE_H
