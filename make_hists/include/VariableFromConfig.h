#ifndef VARIABLEFromConfig_H
#define VARIABLEFromConfig_H

#include "CVUniverse.h"
//#include "PlotUtils/HistFolio.h"  - gives annoying error messages
#include "HistWrapperMap.h"
#include "MinervaUnfold/MnvResponse.h"
#include "utils/NuConfig.h"


#include "include/CVFunctions.h"
#ifndef __CINT__  // CINT doesn't know about std::function
#include "PlotUtils/VariableBase.h"
#endif  // __CINT__


namespace CCQENu {



class VariableFromConfig : public PlotUtils::VariableBase<CVUniverse> {
private:
  typedef std::function<double(const CVUniverse&)> PointerToCVUniverseFunction;
  typedef PlotUtils::HistWrapperMap<CVUniverse> HM;
  typedef PlotUtils::MnvH1D MH1D;
  //  typedef PlotUtils::HistFolio<PlotUtils::MnvH1D> FOLIO;


public:
  //=======================================================================================
  // CTOR
  //=======================================================================================
  //template <class... ARGS>
  //VariableFromConfig(ARGS... args) : PlotUtils::VariableBase<CVUniverse>(args...) {}

  // HMS 2-13-202 replace the templated constructor with explicit ones so we can make a config version without introducing a dependency in the Base class.

  //  // variable binning
//  VariableFromConfig(const std::string name, const std::string xaxis_label,
//                  const std::vector<double> binning,
//                  PointerToCVUniverseFunction reco_func = &CVUniverse::GetDummyVar,
//                  PointerToCVUniverseFunction true_func = &CVUniverse::GetDummyVar) :
//  PlotUtils::VariableBase<CVUniverse>(name,  xaxis_label, binning,reco_func, true_func ){
//    m_for = {"data","selected_reco","selected_truth","response","truth"};
//  };
//
//  // uniform binning
//  VariableFromConfig(const std::string name, const std::string xaxis_label,
//                  const int nbins, const double xmin, const double xmax,
//                  PointerToCVUniverseFunction reco_func = &CVUniverse::GetDummyVar,
//                  PointerToCVUniverseFunction true_func = &CVUniverse::GetDummyVar) :
//  PlotUtils::VariableBase<CVUniverse>(name,  xaxis_label, nbins,xmin,xmax,reco_func, true_func ){
//    m_for = {"data","selected_reco","selected_truth","response","truth"};
//  };
  //template <class... ARGS>

  //  VariableFromConfig(const NuConfig config,
  //                  PointerToCVUniverseFunction recofun  = &CVUniverse::GetDummyVar ,
  //                  PointerToCVUniverseFunction truefun  = &CVUniverse::GetDummyVar):
  //  PlotUtils::VariableBase<CVUniverse>(config.GetString("name"),config.GetString("title"),config.GetDoubleVector("bins"),recofun,truefun){};

//  VariableFromConfig(const NuConfig config,
//                  PointerToCVUniverseFunction recofun   ,
//                  PointerToCVUniverseFunction truefun  = &CVUniverse::GetDummyVar){
//   // config.Print();
//    //      m_name(),
//    //      m_xaxis_label(),
//    //      m_binning(),
//    PlotUtils::VariableBase<CVUniverse>::m_pointer_to_GetRecoValue = recofun;
//    PlotUtils::VariableBase<CVUniverse>::m_pointer_to_GetTrueValue = truefun;
//
//    PlotUtils::VariableBase<CVUniverse>::m_name = config.GetString("name");
//    PlotUtils::VariableBase<CVUniverse>::m_xaxis_label = config.GetString("title");
//    m_for = {"data","selected_reco","selected_truth","response","truth"};
//    if (config.IsMember("bins")){
//      PlotUtils::VariableBase<CVUniverse>::m_binning =  config.GetDoubleVector("bins");
//    }
//    else{
//      int nbins = config.GetInt("nbins");
//      double xmin = config.GetDouble("min");
//      double xmax = config.GetDouble("max");
//      PlotUtils::VariableBase<CVUniverse>::m_binning =  MakeUniformBinning(nbins,xmin,xmax);
//    }
//  }
//
  // new 3-5-2021  Only needs the config

  VariableFromConfig(const NuConfig config){
    //config.Print();

    CVFunctions<CVUniverse> fun;
    //fun.InitFunctionMaps();
    std::string recovar = config.GetString("reco");
    bool good = false;
    for (auto key:fun.GetRecoKeys()){

      if (recovar == key){
        std::cout << " reco function keys " << key <<  std::endl;
        good = true;
        break;
      }
    }

    if (!good){
      std::cout << "VariableFromConfig(config) is asking for an unimplemented reco variable " << recovar << std::endl;
      exit(1);
    }
    bool tgood = false;
    std::string truevar = config.GetString("true");
    for (auto key:fun.GetTrueKeys()){

      if (truevar == key){
        std::cout << " true function keys " << key <<  std::endl;
        tgood = true;
        break;
      }
    }

    if (!tgood){
      std::cout << "VariableFromConfig(config) is asking for an unimplemented true variable " << truevar << std::endl;
      exit(1);
    }

    PlotUtils::VariableBase<CVUniverse>::m_pointer_to_GetRecoValue = (fun.GetRecoFunction(recovar));
    PlotUtils::VariableBase<CVUniverse>::m_pointer_to_GetTrueValue = (fun.GetTrueFunction(truevar));

    PlotUtils::VariableBase<CVUniverse>::m_name = config.GetString("name");
    PlotUtils::VariableBase<CVUniverse>::m_xaxis_label = config.GetString("title");

    if (config.IsMember("for")){
      m_for = config.GetStringVector("for");
    }
    else{ // turn them all on for now
       std::vector<std::string> def = {"data","selected_reco","tuned_reco","selected_truth","response","truth"};
      for (auto s:def){
        m_for.push_back(s);
      }
    }

    if (config.IsMember("bins")){
      PlotUtils::VariableBase<CVUniverse>::m_binning =  config.GetDoubleVector("bins");
    }
    else{
      int nbins = config.GetInt("nbins");
      double xmin = config.GetDouble("min");
      double xmax = config.GetDouble("max");
      PlotUtils::VariableBase<CVUniverse>::m_binning =  MakeUniformBinning(nbins,xmin,xmax);
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
  HM m_signal_mc_truth;
  HM m_selected_data;
  UniverseMap m_universes;
  std::string m_units;
  std::map<const std::string, bool> hasData;
  std::map<const std::string, bool> hasMC;
  std::map<const std::string, bool> hasTunedMC;
  std::map<const std::string, bool> hasSelectedTruth;
  std::map<const std::string, bool> hasTruth;
  std::map<const std::string, bool> hasResponse;
  std::vector<std::string> m_tags;
  std::vector<std::string> m_for;
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
//     m_selected_mc_reco = HM(Form("selected_mc_reco_%s", name), (GetName()+";"+m_xaxis_label).c_str(), GetNBins(), bins, univs, tags);
    m_selected_mc_reco = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNBins(), bins, univs, tags);
    m_selected_mc_reco.AppendName("reconstructed",tags); // patch to conform to CCQENU standard m_selected_mc_truth.AppendName("_truth",tags); // patch to conform to CCQENU standard

    // TODO: Should tuned mc reco get its own InitializeHist function? -NHV 6-28-22
    if (std::count(m_for.begin(), m_for.end(),"tuned_reco")< 1) {
      std::cout << "VariableFromConfig Warning: tuned_reco is disabled for this variable " << GetName() << std::endl;
      for (auto tag:tags){
        hasTunedMC[tag] = false;
      }
      return;
    }
    for (auto tag:tags){
      hasTunedMC[tag] = true;
    }
    m_tuned_mc_reco = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNBins(), bins, univs, tags);
    m_tuned_mc_reco.AppendName("reconstructed_tuned",tags);
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
      }
      if(hasTunedMC[tag]){
        m_tuned_mc_reco.Write((tag+"_rescale").c_str());
        std::cout << " write out tuned mc histogram " << m_tuned_mc_reco.GetHist((tag+"_rescale").c_str())->GetName() << std::endl;
      }
      if(hasSelectedTruth[tag]){
        std::cout << " write out selected truth histogram " << m_selected_mc_truth.GetHist(tag)->GetName() << std::endl;
        m_selected_mc_truth.Write(tag);
      }
      if(hasTruth[tag]){
        std::cout << " write out truth histogram " << m_signal_mc_truth.GetHist(tag)->GetName() << std::endl;
        m_signal_mc_truth.Write(tag);
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
      }
      if(hasTunedMC[tag]){
        m_tuned_mc_reco.SyncCVHistos();
      }
      if(hasSelectedTruth[tag]){
        m_selected_mc_truth.SyncCVHistos();
      }
      if(hasData[tag]){
        m_selected_data.SyncCVHistos();
      }
      if(hasTruth[tag]){
        m_signal_mc_truth.SyncCVHistos();
      }
    }
  }

  inline void FillResponse(std::string tag, CVUniverse* univ, const double value, const double truth, const double weight=1.0){
    if(hasMC[tag]){
      m_selected_mc_reco.FillResponse(tag, univ, value, truth, weight);
    }
    if(hasTunedMC[tag]){
      m_tuned_mc_reco.FillResponse(tag, univ, value, truth, weight);

    }
  }

  // helper to return the actual numeric index corresponding to a universe  ie, allows map from name,index space to pure universe space.

  //  inline int UniverseIndex(CVUniverse* univ){
  //    return m_map[univ];
  //  }
  //
  //  //
};  //end of class



}  // namespace Ben

#endif  // VARIABLE_H
