//==============================================================================
// Adapted from the MINERvA Analysis Toolkit Example
// Compared to previous examples, this script is a more faithful attempt to
// perform a realistic event selection for the cross section pipeline.
//
// It attempts to use all/most of the new MAT tools as of 2020-09.
// These include:
// * CVUniverse + Histwrapper
// * PlotUtils::MacroUtil
// * Variable class
// * PlotUtils::Cutter
//
// This script follows the canonical event-looping structure:
// Setup (I/O, variables, histograms, systematics)
// Loop events
//   loop universes
//     make cuts
//     loop variables
//       fill histograms
// Plot and Save
//==============================================================================
#include <iostream>
#include <vector>
#include "utils/NuConfig.h"
//#include "utils/gitVersion.h"
#include "PlotUtils/MacroUtil.h"
#include "include/CVUniverse.h"

#include "include/Systematics.h"  // GetStandardSystematics
#ifndef __CINT__
#include "PlotUtils/Cut.h"
#include "PlotUtils/Cutter.h"
#include "include/GetCCQECutsFromConfig.h"
#include "include/GetVariablesFromConfig.h"
#include "include/Get2DVariablesFromConfig.h"
#include "include/GetHyperDVariablesFromConfig.h"
#include "include/Variable2DFromConfig.h"
#include "include/VariableHyperDFromConfig.h"
#include "include/weight_MCreScale.h"
//#include "include/plotting_pdf.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TError.h"
#include "TNamed.h"
#endif
#ifndef HAZMAT
#include "PlotUtils/reweighters/Model.h"
#include "PlotUtils/reweighters/FluxAndCVReweighter.h"
#include "PlotUtils/reweighters/GENIEReweighter.h"
#include "PlotUtils/reweighters/LowRecoil2p2hReweighter.h"
#include "PlotUtils/reweighters/RPAReweighter.h"
#include "PlotUtils/reweighters/MINOSEfficiencyReweighter.h"
#include "PlotUtils/reweighters/LowQ2PiReweighter.h"
#else
#include "weighters/Model.h"
#include "weighters/FluxAndCVReweighter.h"
#include "weighters/GENIEReweighter.h"
#include "weighters/LowRecoil2p2hReweighter.h"
#include "weighters/RPAReweighter.h"
#include "weighters/MINOSEfficiencyReweighter.h"
#include "weighters/LowQ2PiReweighter.h"
#endif
#include "include/Fillers.h"
#include "include/Sample.h"
//#include <filesystem>


// needs to be global
int prescale;

template <typename T> bool IsInVector(const T & what, const std::vector<T> & vec)
{
    return std::find(vec.begin(),vec.end(),what)!=vec.end();
}


// Forward declare my variables because we're hiding the header.
namespace CCQENu {
  class VariableFromConfig;
  class Variable2DFromConfig;
  class VariableHyperDFromConfig;
}

#include "include/Loops.h"
//
//enum EDataMCTruth {kData, kMC, kTruth, kNDataMCTruthTypes};
//
//
//
//
////==============================================================================
//// Loop and fill
////==============================================================================
//#ifndef __CINT__ //for PlotUtils::cuts_t<>
//void LoopAndFillEventSelection(std::string tag,
//                               const PlotUtils::MacroUtil& util,
//                               std::map<std::string, std::vector<CVUniverse*> > error_bands,
//                               std::vector<CCQENu::VariableFromConfig*>& variables,
//                               std::vector<CCQENu::Variable2DFromConfig*>& variables2D,
//                               EDataMCTruth data_mc_truth,
//                               PlotUtils::Cutter<CVUniverse>& selection) {
//  // Prepare loop
//  MinervaUniverse::SetTruth(false);
//  int nentries = -1;
//  if (data_mc_truth == kData ){
//    nentries = util.GetDataEntries();
//  }
//  else if (data_mc_truth == kMC ){
//    nentries = util.GetMCEntries();
//  }
//  else{
//
//    nentries = util.GetTruthEntries() ;
//    MinervaUniverse::SetTruth(true);
//
//  }
//
//  std::cout << " starting loop " << data_mc_truth << " " << nentries << std::endl;
//  // Begin entries loop
//  for (int i = 0; i < nentries; i++) {
//    if(data_mc_truth != kData) i+= prescale-1;
//    if (i+1 % 1000 == 0) std::cout << (i / 1000) << "k " << std::endl;
//    // Loop bands and universes
//    for (auto band : error_bands) {
//      std::vector<CVUniverse*> error_band_universes = band.second;
//      for (auto universe : error_band_universes) {
//
//        universe->SetEntry(i);
//
//        // Process this event/universe
//        double weight = 1;
//        if (universe->ShortName() == "cv" ) weight = data_mc_truth == kData ? 1. : universe->GetWeight();
//
//        //TODO: Put the IsVertical() short circuit into PlotUtils::Cutter directly
//        PlotUtils::detail::empty event;
//
//        //=========================================
//        // Fill
//        //=========================================
//
//        if(data_mc_truth == kMC){
//          if(selection.isMCSelected(*universe, event, weight).all()
//             && selection.isSignal(*universe)) {
//            double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
//            FillMC(tag, universe, weight, variables);
//            FillResponse(tag, universe,weight,variables);
//          }
//
//        }
//        else if (data_mc_truth == kTruth){
//
//          if(selection.isEfficiencyDenom(*universe, weight)){
//            double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
//            FillSignalTruth(tag, universe, weight, variables);
//          }
//        }
//        else{ //kData
//
//          if(selection.isDataSelected(*universe, event).all()) FillData(tag, universe, variables);
//        }
//
//      } // End universes
//    } // End error bands
//  } // End entries loop
//}
//
//void LoopAndFillEventSelection2D(std::string tag,
//                                 const PlotUtils::MacroUtil& util,
//                                 std::map<std::string, std::vector<CVUniverse*> > error_bands,
//                                 std::vector<CCQENu::Variable2DFromConfig*>& variables2D,
//                                 EDataMCTruth data_mc_truth,
//                                 PlotUtils::Cutter<CVUniverse>& selection) {
//  // Prepare loop
//  MinervaUniverse::SetTruth(false);
//  int nentries = -1;
//  if (data_mc_truth == kData ){
//    nentries = util.GetDataEntries();
//  }
//  else if (data_mc_truth == kMC ){
//    nentries = util.GetMCEntries();
//  }
//  else{
//
//    nentries = util.GetTruthEntries() ;
//    MinervaUniverse::SetTruth(true);
//
//  }
//
//  std::cout << " starting 2D loop " << data_mc_truth << " " << nentries << std::endl;
//  // Begin entries loop
//  for (int i = 0; i < nentries; i++) {
//    if(data_mc_truth != kData) i+= prescale-1;
//    if (i+1 % 1000 == 0) std::cout << (i / 1000) << "k " << std::endl;
//    // Loop bands and universes
//    for (auto band : error_bands) {
//      std::vector<CVUniverse*> error_band_universes = band.second;
//      for (auto universe : error_band_universes) {
//
//        universe->SetEntry(i);
//
//        // Process this event/universe
//        double weight = 1;
//        if (universe->ShortName() == "cv" ) weight = data_mc_truth == kData ? 1. : universe->GetWeight();
//
//        //TODO: Put the IsVertical() short circuit into PlotUtils::Cutter directly
//        PlotUtils::detail::empty event;
//
//        //=========================================
//        // Fill
//        //=========================================
//
//        if(data_mc_truth == kMC){
//          if(selection.isMCSelected(*universe, event, weight).all()
//             && selection.isSignal(*universe)) {
//            double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
//            FillMC2D(tag, universe, weight, variables2D);
//            FillResponse2D(tag, universe,weight,variables2D);
//          }
//
//        }
//        else if (data_mc_truth == kTruth){
//
//          if(selection.isEfficiencyDenom(*universe, weight)){
//            double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
//            FillSignalTruth2D(tag, universe, weight, variables2D);
//          }
//        }
//        else{ //kData
//
//          if(selection.isDataSelected(*universe, event).all()) FillData2D(tag, universe, variables2D);
//        }
//
//      } // End universes
//    } // End error bands
//  } // End entries loop
//}
//#endif //__CINT__

//==============================================================================
// Main
//==============================================================================

//int main(const int argc, const char *argv[]){}
#include "runsamplesMain.C"

//
//int main(const int argc, const char *argv[] ) {
//
//  gROOT->ProcessLine("gErrorIgnoreLevel = kWarning;");
//  //++++++++++++++++++=  Initialization +++++++++++++++++++++++++
//
//  std::string pl = "5A";
//  if (argc > 1){
//    pl = std::string(argv[1]);
//  }
//  else{
//    std::cout << " arguments are:\n loop <config> [<prescale from config file>] " << std::endl;
//    exit(0);
//  }
//  std::string configfilename(pl+".json");
//  NuConfig config;
//  config.Read(configfilename);
//
//  if (argc > 2){
//    prescale = std::stoi(argv[2]);
//  }
//  else{
//    prescale = config.GetDouble("prescale");
//  }
//  std::string dir = "";
//  if (argc > 3) dir = std::string(argv[3]);
//  //bool LOCAL = config.GetBool("local");
//  //double kecut = config.GetDouble("protonKECutMeV");
//  int pdg = config.GetInt("pdg");
//  bool neutrinomode = (pdg>0);
//  int version = 1;
//  if (config.IsMember("version")){
//    version = config.GetInt("version");
//  }
//
//
//  //=========================================S
//  // MacroUtil (makes your anatuple chains)
//  //=========================================
//
//  const std::string mc_file_list(config.GetString("mcIn"));
//  const std::string data_file_list(config.GetString("dataIn"));
//
//
//  const std::string plist_string(config.GetString("playlist"));
//  const std::string reco_tree_name(config.GetString("recoName"));
//
//  const std::string truth_tree_name("Truth");
//
//  //const std::string background_tag = config.GetString("background");
//  //const std::string signal_tag = config.GetString("signal");
//  //const std::string data_tag = config.GetString("data");
//  const bool do_truth = true;
//
//  PlotUtils::MacroUtil util(reco_tree_name, mc_file_list, data_file_list,
//                            plist_string, do_truth);
//
//  //Data, MC reco, and Truth trees
//
//
//  util.PrintMacroConfiguration("runEventLoop");
//
//  // Setup systematics-related constants
//  // TODO These should be handled by PU::MacroUtil
//
//  PlotUtils::MinervaUniverse::SetNonResPiReweight(config.GetInt("NonResPiReweight"));
//
//  PlotUtils::MinervaUniverse::SetDeuteriumGeniePiTune (config.GetInt("DeuteriumGeniePiTune"));
//
//  PlotUtils::MinervaUniverse::SetNuEConstraint(config.GetInt("NuEConstraint")); //Needs to be on to match Dan's ME 2D inclusive analysis
//
//  PlotUtils::MinervaUniverse::SetNFluxUniverses(config.GetInt("fluxUniverses"));
//
//  PlotUtils::MinervaUniverse::SetPlaylist(plist_string);
//
//  PlotUtils::MinervaUniverse::SetAnalysisNuPDG(pdg);
//
//  // see docdb 28556 for description of these flags for the hadron interaction reweighter.
//  PlotUtils::MinervaUniverse::SetReadoutVolume("Tracker");
//  //Neutron CV reweight is on by default (recommended you keep this on)
//  PlotUtils::MinervaUniverse::SetMHRWeightNeutronCVReweight( config.GetInt("Geant4NeutronCV") );
//  //Elastics are on by default (recommended you keep this on)
//  PlotUtils::MinervaUniverse::SetMHRWeightElastics( config.GetInt("Geant4Elastics") );
//  PlotUtils::MinervaUniverse::SetTreeName(reco_tree_name);
//
//
//
//  //=== MODELS === needs a driver
//
//
//
//  std::vector<std::unique_ptr<PlotUtils::Reweighter<CVUniverse,PlotUtils::detail::empty>>> MnvTunev1;
//  MnvTunev1.emplace_back(new PlotUtils::FluxAndCVReweighter<CVUniverse, PlotUtils::detail::empty>());
//  MnvTunev1.emplace_back(new PlotUtils::GENIEReweighter<CVUniverse,PlotUtils::detail::empty>(true, false));
//  MnvTunev1.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, PlotUtils::detail::empty>());
//  MnvTunev1.emplace_back(new PlotUtils::MINOSEfficiencyReweighter<CVUniverse, PlotUtils::detail::empty>());
//  MnvTunev1.emplace_back(new PlotUtils::RPAReweighter<CVUniverse, PlotUtils::detail::empty>());
//
//  PlotUtils::Model<CVUniverse, PlotUtils::detail::empty> model(std::move(MnvTunev1));
//
//  //=========================================
//  // Systematics
//  // GetStandardSystematics in Systematics.h
//  //=========================================
//  std::map<std::string, std::vector<CVUniverse*> > mc_error_bands =
//  systematics::GetStandardSystematics(util.m_mc,config);
//
//  std::map<std::string, std::vector<CVUniverse*> > truth_error_bands =
//  systematics::GetStandardSystematics(util.m_truth,config);
//
//  std::cout << " mc error bands is " << mc_error_bands.size() << std::endl;
//  std::cout << " truth error bands is " << truth_error_bands.size() << std::endl;
//
//
//  // If we're doing data we need a single central value universe.
//  // TODO Take care of this in PU::MacroUtil.
//  CVUniverse* data_universe = new CVUniverse(util.m_data);
//  std::vector<CVUniverse*> data_band = {data_universe};
//  std::map<std::string, std::vector<CVUniverse*> > data_error_bands;
//
//  data_error_bands["cv"] = data_band;
//
//  //Selection Criteria
//
//  std::string cutsfilename = config.GetString("cutsFile");
//  std::string samplesfilename = config.GetString("samplesFile");
//  NuConfig cutsConfig;
//  NuConfig samplesConfig;
//
//  cutsConfig.Read(cutsfilename);
//  //cutsConfig.Print();
//  std::vector<string> samplesToDo=config.GetStringVector("runsamples"); // get the master list.
//  samplesConfig.Read(samplesfilename);
//  //samplesConfig.Print();
//  std::vector<std::string> samplelist=samplesConfig.GetKeys();
//  std::vector<std::pair<std::string,std::string> >samples;
//  std::map<std::string, std::map<std::string,std::vector<std::string> > > type_list;
//  std::map<std::string, std::map<std::string,std::string > > h_name;
//  std::map<std::string, std::map<std::string,std::string > > phasespaces;
//  // loop over samples
//  for (auto key:samplelist){
//    std::cout << key  << " " ;
//  }
//  std::cout << std::endl;
//  // at version six start using samples list from main driver instead of everything in config
//
//  if (version <= 5){
//    samplesToDo = samplelist;
//  }
//
//  for (auto key:samplesToDo){
//    if (!IsInVector<std::string>(key,samplelist)){
//      std::cout << " runsamples is asking for a sample " << key << " that has not been configured in "<< samplesfilename << std::endl;
//      assert(0);
//      continue;
//    }
//    std::vector<NuConfig> subsamples = samplesConfig.GetConfigVector(key);
//    std::cout << " configure sample " << key << std::endl;
//    // get the subsamples
//    for (auto sampleconfig:subsamples){
//      sampleconfig.Print();
//      std::string truecuts=sampleconfig.GetString("true");
//      if (sampleconfig.IsMember("phase_space")){
//        std::string phasespace=sampleconfig.GetString("phase_space");
//        phasespaces[key][truecuts] = sampleconfig.GetString("phase_space");
//      }
//      else{
//        phasespaces[key][truecuts] = "None";
//      }
//      std::pair<std::string,std::string>  temp = make_pair(key,truecuts);
//      samples.push_back(temp);
//      type_list[key][truecuts] = sampleconfig.GetStringVector("for");
//      //std::cout << "phasespace" << phasespaces[key][truecuts] << std::endl;
//      h_name[key][truecuts] = Form("%s___%s",key.c_str(),truecuts.c_str());
//    }
//  }
//
//  PlotUtils::cuts_t<CVUniverse> noSidebands;
//  PlotUtils::constraints_t<CVUniverse> signal, phaseSpace;
//  std::map<std::string,PlotUtils::Cutter<CVUniverse> *> selectionCriteria;
//
//  std::vector<std::string> tags;
//
//  for (auto sample:samples){
//    std::cout << " load in cuts for samples" << sample.first << " " << sample.second << std::endl;
//    NuConfig recocuts = cutsConfig.GetValue(sample.first);
//    NuConfig truecuts = cutsConfig.GetValue(sample.second);
//    truecuts.Print();
//
//    NuConfig phasespace = cutsConfig.GetValue(phasespaces[sample.first][sample.second]);
//
//    std::string tag = h_name[sample.first][sample.second];
//    tags.push_back(tag);
//    selectionCriteria[tag] = new PlotUtils::Cutter<CVUniverse> (\
//                                                                config_reco::GetCCQECutsFromConfig<CVUniverse>(recocuts),\
//                                                                std::move(noSidebands),\
//                                                                config_truth::GetCCQESignalFromConfig<CVUniverse>(truecuts),\
//                                                                config_truth::GetCCQEPhaseSpaceFromConfig<CVUniverse>(phasespace));
//  }
//  //=========================================
//  // Get variables and initialize their hists
//  //=========================================
//
//
//  std::vector<std::string> vars1D = config.GetStringVector("AnalyzeVariables");
//  std::vector<std::string> vars2D = config.GetStringVector("Analyze2DVariables");
//
//  std::vector<CCQENu::VariableFromConfig*> variables1D;
//  std::vector<CCQENu::Variable2DFromConfig*> variables2D;
//
//  // std::string variables1Dname = config.GetString("varsFile");
//  std::string varsFile = config.GetString("varsFile");
//
//  NuConfig configvar;
//  if (varsFile != "" ){
//    configvar.Read(varsFile);
//  }
//  else{
//    std::cout << " no varsFile" << std::endl;
//    exit(1);
//  }
//
//  // new way
//  std::map<std::string,CCQENu::VariableFromConfig*> variablesmap1D = GetVariablesFromConfig(vars1D,tags,configvar);
//
//  std::map<std::string,CCQENu::Variable2DFromConfig*> variablesmap2D = Get2DVariablesFromConfig(vars2D,variablesmap1D,tags,configvar);
//
//
//  // associate different datasets with types so you don't have to loop over everything for everything
//
//  //  std::vector<std::string> selected_reco_tags = {signal_tag,background_tag};  //bkg only needed for recontructed MC
//  //  std::vector<std::string> datatags = {data_tag};
//  //  std::vector<std::string> truthtags = {signal_tag};
//  //  std::vector<std::string> responsetags = {signal_tag};
//  //
//  // for (auto v : variables) {
//
//  std::vector<std::string> selected_reco_tags ;  //bkg only needed for recontructed MC
//  std::vector<std::string> selected_truth_tags ;
//  std::vector<std::string> datatags;
//  std::vector<std::string> truthtags;
//  std::vector<std::string> responsetags;
//
//  std::vector<std::string> types;
//
//  for (auto sample:samples){
//    std::string tag = h_name[sample.first][sample.second];
//    if (  IsInVector<std::string>("data",type_list[sample.first][sample.second])) {
//      datatags.push_back(tag);
//    }
//
//    if (IsInVector<std::string>("selected_reco",type_list[sample.first][sample.second])){
//      selected_reco_tags.push_back(tag);
//    }
//
//    if (IsInVector<std::string>("selected_truth",type_list[sample.first][sample.second])){
//      selected_truth_tags.push_back(tag);
//    }
//    if(IsInVector<std::string>("truth",type_list[sample.first][sample.second]  )){
//      truthtags.push_back(tag);
//    }
//    if(IsInVector<std::string>("response",type_list[sample.first][sample.second])){
//      responsetags.push_back(tag);
//    }
//  }
//
//
//
//  for (auto var1D : variablesmap1D) {
//    CCQENu::VariableFromConfig* v = var1D.second;
//    v->InitializeMCHistograms(mc_error_bands,selected_reco_tags);
//    v->InitializeSelectedTruthHistograms(mc_error_bands,selected_truth_tags);
//    v->InitializeDataHistograms(data_error_bands,datatags);
//    v->AddMCResponse(responsetags);
//    v->InitializeTruthHistograms(truth_error_bands,truthtags);
//    variables1D.push_back(v);
//  }
//
//  for (auto var2D : variablesmap2D ) {
//    std::string varname = var2D.first;
//    CCQENu::Variable2DFromConfig* v = var2D.second;
//    v->InitializeMCHistograms2D(mc_error_bands,selected_reco_tags);
//    v->InitializeSelectedTruthHistograms2D(mc_error_bands,selected_truth_tags);
//    v->InitializeDataHistograms2D(data_error_bands,datatags);
//    v->AddMCResponse2D(responsetags);
//    v->InitializeTruthHistograms2D(truth_error_bands,truthtags);
//    variables2D.push_back(v);
//  }
//
//  for (auto tag:datatags){
//    //=========================================
//    // Entry loop and fill
//    //=========================================
//    std::cout << "Loop and Fill Data for " << tag << "\n" ;
//    LoopAndFillEventSelection(tag, util, data_error_bands, variables1D, variables2D, kData, *selectionCriteria[tag],model);
//    // LoopAndFillEventSelection2D(tag, util, data_error_bands, variables2D, kData, *selectionCriteria[tag]);
//
//    std::cout << "\nCut summary for Data:" <<  tag << "\n" << *selectionCriteria[tag] << "\n";
//    selectionCriteria[tag]->resetStats();
//  }
//
//  for (auto tag:selected_reco_tags){
//    std::cout << "Loop and Fill MC Reco  for " <<  tag << "\n";
//    LoopAndFillEventSelection(tag, util, mc_error_bands, variables1D, variables2D, kMC, *selectionCriteria[tag],model);
//    // LoopAndFillEventSelection2D(tag, util, mc_error_bands, variables2D, kMC, *selectionCriteria[tag]);
//
//    std::cout << "\nCut summary for MC Reco:" <<  tag << "\n" << *selectionCriteria[tag] << "\n";
//    selectionCriteria[tag]->resetStats();
//  }
//
//  for (auto tag:truthtags){
//    std::cout << "Loop and Fill MC Truth  for " <<  tag << "\n";
//    LoopAndFillEventSelection(tag, util, truth_error_bands, variables1D, variables2D, kTruth, *selectionCriteria[tag],model);
//    // LoopAndFillEventSelection2D(tag, util, truth_error_bands, variables2D, kTruth, *selectionCriteria[tag]);
//    std::cout << "\nCut summary for MC Truth:" <<  tag << "\n";
//    // this is a special overload to allow printing truth
//    (*selectionCriteria[tag]).summarizeTruthWithStats(std::cout);
//    selectionCriteria[tag]->resetStats();
//  }
//  //std::cout << "\nCut summary for MC:\n" << selectionCriteria << "\n";
//
//  // Sync CV hists
//
//  for (auto v : variables1D) v->SyncAllHists();
//  for (auto v : variables2D) v->SyncAllHists();
//  //=========================================
//  // Plot
//  //=========================================
//  std::cout << "Done filling. Begin plotting.\n";
//
//  //  for (auto tag:tags){
//  //    for (auto v : variables1D) {
//  //      if (v->hasMC[tag] && v->hasData[tag]){
//  //        PlotDataMCAndError(v->m_selected_data.GetHist(tag), v->m_selected_mc_reco.GetHist(tag),
//  //                           (util.m_data_pot/util.m_mc_pot*prescale), v->GetName()+"_eff");
//  //        PlotErrorSummary(v->m_selected_mc_reco.GetHist(tag), v->GetName()+"_eff");
//  //      }
//  //      if (v->hasMC[tag] && v->hasTruth[tag]){
//  //        PlotDataMCAndError(v->m_selected_mc_truth.GetHist(tag), v->m_signal_mc_truth.GetHist(tag), 1, v->GetName()+"_ratio");
//  //      }
//  //    }
//  //  }
//
//
//  std::string outname = Form("%s_%s_%d.root",config.GetString("outRoot").c_str(),pl.c_str(),prescale);
//  std::cout << " outname is " << outname << " prescale was " << prescale << std::endl;
//  // std::string outname = config.GetString("outRoot")+"_"+pl+"_"+prescale+".root";
//  TFile* out=TFile::Open((dir.append(outname)).c_str(),"RECREATE");
//
//  // dump the json files
//
//  std::string top = config.ToString();
//  TNamed topobj("main",top.c_str());
//  topobj.Write();
//  std::string var = configvar.ToString();
//  TNamed varobj("varsFile",var.c_str());
//  varobj.Write();
//  std::string cuts = cutsConfig.ToString();
//  TNamed cutsobj("cutsFile",cuts.c_str());
//  cutsobj.Write();
//  std::string sam = samplesConfig.ToString();
//  TNamed samobj("samplesFile",cuts.c_str());
//  samobj.Write();
//
//  for (auto v : variables1D){
//    v->WriteAllHistogramsToFile(*out);
//  }
//  for (auto v : variables2D){
//    std::cout << "Writing 2D hist to file" << std::endl;
//    v->WriteAllHistogramsToFile2D(*out);
//  }
//
//  PlotUtils::MnvH1D* h_pot = new PlotUtils::MnvH1D("POT_summary","data, mc, Prescaled mc", 3, 0., 3.);
//
//  h_pot->Fill(0.5, util.m_data_pot);
//  h_pot->Fill(1.5, util.m_mc_pot);
//  h_pot->Fill(2.5, util.m_mc_pot/prescale);  // compensate for prescale
//  h_pot->Print();
//  h_pot->Write();
//  // make compatible with Amit
//  TVector2 *pot = new TVector2( util.m_data_pot,util.m_mc_pot/prescale);
//  out->WriteTObject( pot, "pot" );
//  out->Close();
//  std::cout << "Success" << std::endl;
//}
