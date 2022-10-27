#ifndef VARIABLEFromConfig_H
#define VARIABLEFromConfig_H

#include "CVUniverse.h"
//#include "PlotUtils/HistFolio.h"  - gives annoying error messages
#include "MinervaUnfold/MnvResponse.h"
#include "HistWrapperMap.h"
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


public:
  //=======================================================================================
  // CTOR
  //=======================================================================================
  //template <class... ARGS>
  //VariableFromConfig(ARGS... args) : PlotUtils::VariableBase<CVUniverse>(args...) {}

  // HMS 2-13-202 replace the templated constructor with explicit ones so we can make a config version without introducing a dependency in the Base class.



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
       std::vector<std::string> def = {"data","selected_reco","selected_truth","response","truth"};
      for (auto s:def){
        m_for.push_back(s);
      }
    }

    // Control at variable level whether to run tuned mc or not
    if (config.IsMember("tunedmc")){
      std::string checkval = config.GetString("tunedmc");
      // "both" or 2 runs both tuned and untuned mc
      if(checkval=="both" || checkval=="2"){
        std::cout << "VariableFromConfig(config) set up both tuned and untuned MC." << std::endl;
        m_tunedmc = 2;
      }
      // "only" or 1 runs only tuned mc (not untuned)
      else if(checkval=="only" || checkval=="1"){
        std::cout << "VariableFromConfig(config) set up only tuned MC." << std::endl;
        m_tunedmc = 1;
      }
      // "none" or 0 runs only untunedmc
      else if(checkval=="none" || checkval=="0"){
        std::cout << "VariableFromConfig(config) set up only untuned MC." << std::endl;
        m_tunedmc = 0;
      }
      else{
        std::cout << "VariableFromConfig Warning: invalid 'tunedmc' configured. Defaulting to running both tuned and untuned MC. " << std::endl;
        m_tunedmc = 2;
      }
    }
    else{
      // Default to running both tuned and untuned
      std::cout << "VariableFromConfig: 'tunedmc' not configured. Defaulting to running both tuned and untuned MC. " << std::endl;
      m_tunedmc = 2;
    }

    if (config.IsMember("bins")){
      PlotUtils::VariableBase<CVUniverse>::m_binning =  config.GetDoubleVector("bins");
      if (config.IsMember("recobins")){
          PlotUtils::VariableBase<CVUniverse>::m_reco_binning = config.GetDoubleVector("recobins");
          PlotUtils::VariableBase<CVUniverse>::m_has_reco_binning = true;
      }
      else{
          PlotUtils::VariableBase<CVUniverse>::m_has_reco_binning = false;
      }
    }
    else{
      int nbins = config.GetInt("nbins");
      double xmin = config.GetDouble("min");
      double xmax = config.GetDouble("max");
      PlotUtils::VariableBase<CVUniverse>::m_binning =  MakeUniformBinning(nbins,xmin,xmax);
      if (config.IsMember("nrecobins")){
          int nrecobins = config.GetInt("nrecobins");
          double xrecomin = config.GetDouble("recomin");
          double xrecomax = config.GetDouble("recomax");
          PlotUtils::VariableBase<CVUniverse>::m_reco_binning =  MakeUniformBinning(nrecobins,xrecomin,xrecomax);
      }
      else{
          PlotUtils::VariableBase<CVUniverse>::m_has_reco_binning = false;
      }
    }
      //std::cout << " Check Binning For" << config.GetString("name") << std::endl;
      //PrintBinning();
      //PrintRecoBinning();
  }

  typedef std::map<std::string, std::vector<CVUniverse*>> UniverseMap;
  //=======================================================================================
  // DECLARE NEW HISTOGRAMS
  //=======================================================================================
  // Histwrappers -- selected mc, selected data

  HM m_selected_mc_reco; // HM for normal MC hists - has special constructor to make response
  HM m_tuned_selected_mc_reco; // HM for tuned MC hists used for background subtraction -NHV - has special constructor to make response
  HM m_selected_mc_truth;
  HM m_tuned_selected_mc_truth;
  HM m_signal_mc_truth;
  HM m_tuned_signal_mc_truth;
  HM m_selected_data;
  // ResponseWrapperMap<CVUniverse> m_response;
  // ResponseWrapperMap<CVUniverse> m_tuned_response;
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
  //RESPONSE* m_response;
  // helpers for response

  // std::map< CVUniverse* , int> m_map; // map to get name and index from Universe;
  // Histofolio to categorize MC by interaction channel
  //FOLIO m_selected_mc_by_channel;
  //FOLIO m_selected_mc_truth_by_channel;
  inline virtual std::string GetUnits(){return m_units;};

  inline virtual void SetUnits(std::string units){m_units=units;};

  inline virtual int GetTuned(){return m_tunedmc;};
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

    if(m_tunedmc==1){
      std::cout << "VariableFromConfig Warning: untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
      return;
    }

    //std::vector<double> bins = GetBinVec();
    std::vector<double> recobins = GetRecoBinVec();
// need reco level binning here:
    m_selected_mc_reco = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNRecoBins(), recobins, univs, tags);
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

    if(m_tunedmc==1){
      std::cout << "VariableFromConfig Warning: untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
      return;
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

    if(m_tunedmc==1){
      std::cout << "VariableFromConfig Warning: untuned MC disabled for this variable, only filling tuned MC " << GetName() << std::endl;
      return;
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
    std::vector<double> recobins = GetRecoBinVec();

    m_selected_data = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNRecoBins(), recobins, univs,tags);
    m_selected_data.AppendName("reconstructed",tags);
  }

  template <typename T>
  void InitializeTunedMCHistograms(T reco_univs, T truth_univs, const std::vector< std::string> tuned_tags, const std::vector< std::string> response_tags) {
    if(m_tunedmc<1){
      std::cout << "VariableFromConfig Warning: tunedmc is disabled for this variable " << GetName() << std::endl;
      for(auto tag:tuned_tags){
        hasTunedMC[tag] = false;
      }
      return;
    }

    for (auto tag:tuned_tags){
      hasTunedMC[tag] = true;
    }

    std::vector<double> bins = GetBinVec();
    std::vector<double> recobins = GetRecoBinVec();

    // Check which categories are configured and add a tuned version
    if (std::count(m_for.begin(), m_for.end(),"selected_reco")>=1){  // use recobins
      m_tuned_selected_mc_reco = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(),GetNRecoBins(),recobins, reco_univs, tuned_tags);
      m_tuned_selected_mc_reco.AppendName("reconstructed_tuned",tuned_tags);
    }
    if (std::count(m_for.begin(), m_for.end(),"selected_truth")>=1) { // use bins
      m_tuned_selected_mc_truth = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNBins(), bins, reco_univs, tuned_tags);
      m_tuned_selected_mc_truth.AppendName("selected_truth_tuned",tuned_tags);
    }
    if (std::count(m_for.begin(), m_for.end(),"truth")>=1) { // use bins
      m_tuned_signal_mc_truth = HM(Form("%s", GetName().c_str()), (GetName()+";"+m_xaxis_label).c_str(), GetNBins(), bins, truth_univs, tuned_tags);
      m_tuned_signal_mc_truth.AppendName("all_truth_tuned",tuned_tags);
    }

    if(std::count(m_for.begin(), m_for.end(),"response")>=1){
      // m_response = RM(Form("%s", GetName().c_str()),reco_univs,true_univs, recobins, bins, tags);
      m_tuned_response = RM(Form("%s", GetName().c_str()), reco_univs, recobins, bins, response_tags, "_tuned");
    }
    // // Now do response
    // if (std::count(m_for.begin(), m_for.end(),"response")< 1) {
    //   std::cout << "VariableFromConfig Warning: response is disabled for this variable " << GetName() << std::endl;
    //   for (auto tag:response_tags){
    //     hasResponse[tag] = false;
    //   }
    //   return;
    // }
    // for (auto tag:response_tags){
    //   assert(hasMC[tag]);
    //   assert(hasSelectedTruth[tag]);
    //   hasResponse[tag] = true;
    // }
    //
    // m_tuned_mc_reco.AddResponse(response_tags,"_tuned");
  }


  //========== Add Response =================
  // reco_univs should be the same as selected_mc_reco (tuned or untuned)
  template <typename T>
  void InitializeResponse(T reco_univs, const std::vector<std::string> tags, std::string tail=""){
    // Check if response is configured for this var
    if (std::count(m_for.begin(), m_for.end(),"response")< 1) {
      std::cout << "VariableFromConfig Warning: response is disabled for this variable " << GetName() << std::endl;
      for (auto tag:tags){
        hasResponse[tag] = false;
      }
      return;
    }

    // Check that the var has both MC reco and truth configured, set bool to true
    for (auto tag:tags){
      assert(hasMC[tag]);
      assert(hasSelectedTruth[tag]);
      hasResponse[tag] = true;
    }

    std::vector<double> bins = GetBinVec();
    std::vector<double> recobins = GetRecoBinVec();

    // m_response = RM(Form("%s", GetName().c_str()),reco_univs,true_univs, recobins, bins, tags);

    m_response = RM(Form("%s", GetName().c_str()),reco_univs, recobins, bins, tags,tail);
    //
    // // Count the number of universes in each band
    // std::map<std::string, int> response_bands;
    // for (auto band : reco_univs){ // Using reco_univs since that's what originally was done
    //   std::string name = band.first;
    //   std::string realname = (band.second)[0]->ShortName();
    //   int nuniv = band.second.size();
    //   response_bands[realname] = nuniv;
    // }
    //
    // std::vector<double> bins = GetBinVec();
    // std::vector<double> recobins = GetRecoBinVec();
    //
    // // Loop over tags for initializing the response
    // for(auto tag:tags){
    //   // the name of the histogram. The "tail" at the end should be an empty string or "_tuned".
    //   std::string resp_name = "h___" + tag + "___" + Form("%s", GetName().c_str()) + "___response" + tail;
    //   if(tail!="_tuned"){
    //     m_response[tag] = new MinervaUnfold::MnvResponse(resp_name.c_str(), resp_name.c_str(), GetNRecoBins(), &recobins[0], GetNBins() ,&bins[0], response_bands);
    //   }
    //   else{
    //     m_tuned_response[tag] = new MinervaUnfold::MnvResponse(resp_name.c_str(), resp_name.c_str(), GetNRecoBins(), &recobins[0], GetNBins() ,&bins[0], response_bands);
    //   }
    // }
  }


  //============================================================================
  // WRITE ALL HISTOGRAMS
  //============================================================================


  void WriteAllHistogramsToFile(TFile& f)  {
    std::cout << "should only be called once " << std::endl;
    f.cd();

    for (auto tag:m_tags){
      std::cout << " write out flags " << hasMC[tag] << hasSelectedTruth[tag] << hasTruth[tag] << hasData[tag] << hasTunedMC[tag] <<  std::endl;
      if(hasMC[tag]){
        if(m_tunedmc!=1){
          m_selected_mc_reco.Write(tag);
          std::cout << " write out selected mc histogram " << m_selected_mc_reco.GetHist(tag)->GetName() << std::endl;
        }
        if(hasTunedMC[tag]){
          m_tuned_selected_mc_reco.Write(tag);
          std::cout << " write out tuned selected mc histogram " << m_tuned_selected_mc_reco.GetHist(tag)->GetName() << std::endl;
        }
      }
      if(hasSelectedTruth[tag]){
        if(m_tunedmc!=1){
          std::cout << " write out selected truth histogram " << m_selected_mc_truth.GetHist(tag)->GetName() << std::endl;
          m_selected_mc_truth.Write(tag);
        }
        if(hasTunedMC[tag]){
          m_tuned_selected_mc_truth.Write(tag);
          std::cout << " write out tuned mc histogram " << m_tuned_selected_mc_truth.GetHist(tag)->GetName() << std::endl;
        }
      }
      if(hasTruth[tag]){
        if(m_tunedmc!=1){
          std::cout << " write out truth histogram " << m_signal_mc_truth.GetHist(tag)->GetName() << std::endl;
          m_signal_mc_truth.Write(tag);
        }
        if(hasTunedMC[tag]){
          m_tuned_signal_mc_truth.Write(tag);
          std::cout << " write out tuned mc histogram " << m_tuned_signal_mc_truth.GetHist(tag)->GetName() << std::endl;
        }
      }
      if(hasResponse[tag]){
        if(m_tunedmc!=1){
          std::cout << " write out response histograms " << tag << std::endl;
          m_response.Write(tag);
        }
        if(hasTunedMC[tag]){
          std::cout << " write out tuned response histograms " << tag << std::endl;
          m_tuned_response.Write(tag);
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
        if(m_tunedmc!=1){
          m_selected_mc_reco.SyncCVHistos();
        }
        if(hasTunedMC[tag]){
          m_tuned_selected_mc_reco.SyncCVHistos();
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
      // if(hasTunedMC[tag]){
      //   m_tuned_mc_reco.SyncCVHistos();
      //   m_tuned_selected_mc_truth.SyncCVHistos();
      //   m_tuned_signal_mc_truth.SyncCVHistos();
      // }
    }
  }

  void FillResponse(std::string tag, CVUniverse* univ,
                           const double value, const double truth,
                           const double weight=1.0, const double scale=1.0){

    std::string name = univ->ShortName();
    // int iuniv = m_decoder[univ];

    if(hasMC[tag] && m_tunedmc!=1){
      m_response.Fill(tag,univ,value, truth, weight);
    }
    if(hasTunedMC[tag] && scale>=0.){
      m_tuned_response.Fill(tag,univ,value, truth, weight, scale);
    }
    // if(hasMC[tag] && m_tunedmc!=1){
    //   m_selected_mc_reco.FillResponse(tag, univ, value, truth, weight);
    // }
    // if(hasTunedMC[tag]){
    //   m_tuned_mc_reco.FillResponse(tag, univ, value, truth, weight);
    // }
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
