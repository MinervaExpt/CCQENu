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
#include "include/Variable2DFromConfig.h"
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
}

#include "include/Loops.h"

int main(const int argc, const char *argv[] ) {


  gROOT->ProcessLine("gErrorIgnoreLevel = kWarning;");
  //++++++++++++++++++=  Initialization +++++++++++++++++++++++++

  std::string pl = "5A";
  if (argc > 1){
    pl = std::string(argv[1]);
  }
  else{
    std::cout << " arguments are:\n loop <config> [<prescale from config file>] " << std::endl;
    exit(0);
  }
  std::string configfilename(pl+".json");
  NuConfig config;
  config.Read(configfilename);

  if (argc > 2){
    prescale = std::stoi(argv[2]);
  }
  else{
    prescale = config.GetDouble("prescale");
  }
  std::string dir = "";
  if (argc > 3) dir = std::string(argv[3]);
  //bool LOCAL = config.GetBool("local");
  //double kecut = config.GetDouble("protonKECutMeV");
  int pdg = config.GetInt("pdg");
  bool neutrinomode = (pdg>0);
  int version = 1;
  if (config.IsMember("version")){
    version = config.GetInt("version");
  }
  
  bool closure = false;
  if (config.IsMember("closure")){
    closure = config.GetBool("closure");
  }
  
  std::string tunedmc = "untuned"; // can be set to "both", "tuned", or "untuned"
  if(config.IsMember("tunedmc"))
  {
    tunedmc = config.GetString("tunedmc");
    std::cout << "runsamplesMain: \'tunedmc\' configured in main config and set to " << tunedmc << std::endl;
  }
  if (config.IsMember("scalefileIn")) { // check if you have a scalefile specified
    if (config.GetString("scalefileIn") == "") {
        tunedmc = "untuned";
        std::cout << "runsamplesMain: WARNING: no \'scalefileIn\' specficied. Defaulting \'tunedmc\' to \'untuned\'." << std::endl;
    }
  } else {
    tunedmc = "untuned";
    std::cout << "runsamplesMain: WARNING: \'scalefileIn\' not found in main config. Defaulting \'tunedmc\' to \'untuned\'." << std::endl;
  }

  // Deprecated but should be backwards compatible
  bool useTuned;
  if(config.IsMember("useTuned")){
    useTuned = config.GetBool("useTuned");
    std::cout << "runsamplesMain: WARNING: useTuned deprecated. Use tunedmc instead. Setting tunedmc accordingly" << std::endl;
    useTuned == false ? tunedmc = "untuned" : tunedmc = "both";
  }

  bool doresolution = false;
  if (config.IsMember("DoResolution")){
    doresolution = config.GetBool("DoResolution");
    std::cout << " ask for resolutions" << std::endl;
  }

  //=========================================S
  // MacroUtil (makes your anatuple chains)
  //=========================================

  const std::string mc_file_list(config.GetString("mcIn"));
  std::string data_file_list;
  if (!closure){
    data_file_list = config.GetString("dataIn");
  }
  else{
    data_file_list = mc_file_list;
  }
  
  

  const std::string plist_string(config.GetString("playlist"));
  const std::string reco_tree_name(config.GetString("recoName"));

  const std::string truth_tree_name("Truth");

  //const std::string background_tag = config.GetString("background");
  //const std::string signal_tag = config.GetString("signal");
  //const std::string data_tag = config.GetString("data");
  const bool do_truth = true;

  PlotUtils::MacroUtil util(reco_tree_name, mc_file_list, data_file_list,
                            plist_string, do_truth);

  //Data, MC reco, and Truth trees


  util.PrintMacroConfiguration("runEventLoop");

  // Setup systematics-related constants
  // TODO These should be handled by PU::MacroUtil

  //PlotUtils::MinervaUniverse::SetNonResPiReweight(config.GetInt("NonResPiReweight"));

  //PlotUtils::MinervaUniverse::SetDeuteriumGeniePiTune (config.GetInt("DeuteriumGeniePiTune"));

  PlotUtils::MinervaUniverse::SetNuEConstraint(config.GetInt("NuEConstraint")); //Needs to be on to match Dan's ME 2D inclusive analysis

  PlotUtils::MinervaUniverse::SetNFluxUniverses(config.GetInt("fluxUniverses"));

  PlotUtils::MinervaUniverse::SetPlaylist(plist_string);

  PlotUtils::MinervaUniverse::SetAnalysisNuPDG(pdg);

  // see docdb 28556 for description of these flags for the hadron interaction reweighter.
  PlotUtils::MinervaUniverse::SetReadoutVolume("Tracker");
  //Neutron CV reweight is on by default (recommended you keep this on)
  PlotUtils::MinervaUniverse::SetMHRWeightNeutronCVReweight( config.GetInt("Geant4NeutronCV") );
  //Elastics are on by default (recommended you keep this on)
  PlotUtils::MinervaUniverse::SetMHRWeightElastics( config.GetInt("Geant4Elastics") );
  PlotUtils::MinervaUniverse::SetTreeName(reco_tree_name);



  //=== MODELS === needs a driver
  std::string modeltune="MnvTunev1";
  if(config.IsMember("MinervaModel")){ //TODO
    modeltune = config.GetString("MinervaModel");
    std::cout << "runsamplesMain: MinervaModel configured in main config and set to " << modeltune << std::endl;
  }
  else{
    std::cout << "runsamplesMain: MinervaModel NOT configured or set in main config. Defaulting to MnvTunev1." << std::endl;
    modeltune="MnvTunev1";
  }
  std::vector<std::unique_ptr<PlotUtils::Reweighter<CVUniverse,PlotUtils::detail::empty>>> MnvTune;
  if(modeltune=="MnvTunev1" || modeltune=="MnvTunev2"){
    MnvTune.emplace_back(new PlotUtils::FluxAndCVReweighter<CVUniverse, PlotUtils::detail::empty>());
      bool NonResPiReweight = true;
      bool DeuteriumGeniePiTune = false; // Deut should be 0? for v1?
    MnvTune.emplace_back(new PlotUtils::GENIEReweighter<CVUniverse,PlotUtils::detail::empty>(NonResPiReweight,DeuteriumGeniePiTune));  // Deut should be 0? for v1?
    MnvTune.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, PlotUtils::detail::empty>());
    MnvTune.emplace_back(new PlotUtils::MINOSEfficiencyReweighter<CVUniverse, PlotUtils::detail::empty>());
    MnvTune.emplace_back(new PlotUtils::RPAReweighter<CVUniverse, PlotUtils::detail::empty>());
  }
  if(modeltune=="MnvTunev2"){
    MnvTune.emplace_back(new PlotUtils::LowQ2PiReweighter<CVUniverse, PlotUtils::detail::empty>("JOINT"));
  }

  PlotUtils::Model<CVUniverse, PlotUtils::detail::empty> model(std::move(MnvTune));

  //====================MC Reco tuning for bkg subtraction======================
  // Initialize the rescale for tuning MC reco for background subtraction later
  PlotUtils::weight_MCreScale mcRescale = weight_MCreScale(config);

  //=========================================
  // Systematics
  // GetStandardSystematics in Systematics.h
  //=========================================
  std::map<std::string, std::vector<CVUniverse*> > mc_error_bands =
  systematics::GetStandardSystematics(util.m_mc,config);

  std::map<std::string, std::vector<CVUniverse*> > truth_error_bands =
  systematics::GetStandardSystematics(util.m_truth,config);

  std::cout << " mc error bands is " << mc_error_bands.size() << std::endl;
  std::cout << " truth error bands is " << truth_error_bands.size() << std::endl;

  // If we're doing data we need a single central value universe.
  // TODO Take care of this in PU::MacroUtil.
  CVUniverse* data_universe = new CVUniverse(util.m_data);
  std::vector<CVUniverse*> data_band = {data_universe};
  std::map<std::string, std::vector<CVUniverse*> > data_error_bands;

  data_error_bands["cv"] = data_band;

  //Selection Criteria
	if (config.IsMember("paramsFile")) {

		std::cout << " configuring cvuniverse parameters" << std::endl;
		std::string paramsfilename = config.GetString("paramsFile");
		NuConfig paramsConfig;
		paramsConfig.Read(paramsfilename);
		// Print applicable configurables?
		bool printConfigs = 0;
		if (paramsConfig.IsMember("printConfigs")) printConfigs = paramsConfig.GetBool("printConfigs");
		// Set applicable configurables
		if (paramsConfig.IsMember("MinimumBlobZVtx")) {
			CVUniverse::SetMinBlobZVtx(paramsConfig.GetConfig("MinimumBlobZVtx").GetDouble("min"),printConfigs);
		}
		if (paramsConfig.IsMember("PhotonEnergyCut")) {
			CVUniverse::SetPhotonEnergyCut(paramsConfig.GetConfig("PhotonEnergyCut").GetDouble("energy"),printConfigs);
		}
		if (paramsConfig.IsMember("ProtonScoreConfig")) {
			CVUniverse::SetProtonScoreConfig(paramsConfig.GetConfig("ProtonScoreConfig"),printConfigs);
		}
		if (paramsConfig.IsMember("ProtonKECut")) {
			CVUniverse::SetProtonKECut(paramsConfig.GetConfig("ProtonKECut").GetDouble("energy"),printConfigs);
		}
		CVUniverse::SetAnalysisNeutrinoPDG(pdg,printConfigs);
	}

  std::string cutsfilename = config.GetString("cutsFile");
  NuConfig cutsConfig;
  cutsConfig.Read(cutsfilename);

  std::string samplesfilename = config.GetString("samplesFile");
  NuConfig samplesConfig;
  //cutsConfig.Print();
  std::vector<string> samplesToDo=config.GetStringVector("runsamples"); // get the master list.
  samplesConfig.Read(samplesfilename);
  //samplesConfig.Print();

  std::vector<CCQENu::Sample> samples;

  for (auto s:samplesToDo){
    if (samplesConfig.IsMember(s)){
      std::cout << "IsMember(" << s << "): TRUE" << std::endl;
      if(samplesConfig.CheckMember(s)) std::cout << "CheckMember(" << s << "): TRUE" << std::endl;
      NuConfig tmp = samplesConfig.GetConfig(s);
      samples.push_back(CCQENu::Sample(tmp));
    }
    else{
      std::cout << "requested sample " << s << " which is not in " << samplesfilename << std::endl;
      assert(0);
    }
  }
  PlotUtils::cuts_t<CVUniverse> noSidebands;
  PlotUtils::constraints_t<CVUniverse> signal, phaseSpace;
  std::map<std::string,PlotUtils::Cutter<CVUniverse> *> selectionCriteria;

  std::vector<std::string> tags;
  std::string tag;
  for (auto sample:samples){
  	std::string name = sample.GetName();
    std::string tag = name+"___data";
    tags.push_back(tag);
    std::cout << " load in cuts for sample " << name << std::endl;
    NuConfig recocuts = cutsConfig.GetValue(sample.GetReco());
    NuConfig phasespace = cutsConfig.GetValue(sample.GetPhaseSpace());
    NuConfig truecuts = cutsConfig.GetValue("data");
    // do data here
    selectionCriteria[tag] = new PlotUtils::Cutter<CVUniverse> (\
                                                                config_reco::GetCCQECutsFromConfig<CVUniverse>(recocuts),\
                                                                std::move(noSidebands),\
                                                                config_truth::GetCCQESignalFromConfig<CVUniverse>(truecuts),\
                                                                config_truth::GetCCQEPhaseSpaceFromConfig<CVUniverse>(phasespace));

    // now do for signal categories
    std::map<const std::string, CCQENu::Category> categories = sample.GetCategories();

    for (auto category:categories){
      std::string cname = category.first;
      tag = name + "___" + cname;
      tags.push_back(tag);
      std::cout << "make a tag " << tag << std::endl;
      if (!cutsConfig.IsMember(cname)){
        std::cout << " sample category " << cname << " does not have an associated  cut in " << cutsfilename << std::endl;
        assert(0);
      }
      NuConfig truecuts = cutsConfig.GetValue(cname);
      selectionCriteria[tag] = new PlotUtils::Cutter<CVUniverse> (\
                                                                  config_reco::GetCCQECutsFromConfig<CVUniverse>(recocuts),\
                                                                  std::move(noSidebands),\
                                                                  config_truth::GetCCQESignalFromConfig<CVUniverse>(truecuts),\
                                                                  config_truth::GetCCQEPhaseSpaceFromConfig<CVUniverse>(phasespace));
    }
  }
  //=========================================
  // Get variables and initialize their hists
  //=========================================


  std::vector<std::string> vars1D = config.GetStringVector("AnalyzeVariables");
  std::vector<std::string> vars2D = config.GetStringVector("Analyze2DVariables");

  std::vector<CCQENu::VariableFromConfig*> variables1D;
  std::vector<CCQENu::Variable2DFromConfig*> variables2D;

  // std::string variables1Dname = config.GetString("varsFile");
  std::string varsFile = config.GetString("varsFile");

  NuConfig configvar;
  if (varsFile != "" ){
    configvar.Read(varsFile);
  }
  else{
    std::cout << " no varsFile" << std::endl;
    exit(1);
  }

  // new way
  std::map<std::string,CCQENu::VariableFromConfig*> variablesmap1D = GetVariablesFromConfig(vars1D,tags,configvar,doresolution,tunedmc);

  std::map<std::string,CCQENu::Variable2DFromConfig*> variablesmap2D = Get2DVariablesFromConfig(vars2D,variablesmap1D,tags,configvar);


  // associate different datasets with types so you don't have to loop over everything for everything

  //  std::vector<std::string> selected_reco_tags = {signal_tag,background_tag};  //bkg only needed for recontructed MC
  //  std::vector<std::string> datatags = {data_tag};
  //  std::vector<std::string> truthtags = {signal_tag};
  //  std::vector<std::string> responsetags = {signal_tag};
  //
  // for (auto v : variables) {

  std::vector<std::string> selected_reco_tags ;  //bkg only needed for recontructed MC
  std::vector<std::string> selected_truth_tags ;
  std::vector<std::string> datatags;
  std::vector<std::string> truthtags;
  // std::vector<std::string> tuned_mc_tags ;
  std::vector<std::string> responsetags;
  std::vector<std::string> types;

  // here we decide what histograms to fill

  for (auto sample:samples){
    std::map<const std::string, CCQENu::Category> categories = sample.GetCategories();
    std::string data_tag = sample.GetName()+"___data";
    datatags.push_back(data_tag);
    for (auto category:categories){
      std::string cname = category.first;
      std::vector<std::string> forlist = category.second.GetFor();
      std::cout << "for ";
      for (auto f:forlist){
        std::cout << " " << f;
      }
      std::cout << std::endl;

      std::string tag = sample.GetName()+"___"+cname;
      std::cout << "make a tag " << tag << std::endl;

      if (IsInVector<std::string>("selected_reco",forlist)){
        selected_reco_tags.push_back(tag);
      }
      if (IsInVector<std::string>("selected_truth",forlist)){
        selected_truth_tags.push_back(tag);
      }
      if(IsInVector<std::string>("truth",forlist )){
        truthtags.push_back(tag);
      }
      if(IsInVector<std::string>("response",forlist)){
        responsetags.push_back(tag);
      }
    }
  }

  for (auto tag:tags){
  std:cout << "tag: " << tag << std::endl;
  }
  // here we initialist ghem

  for (auto var1D : variablesmap1D) {
    CCQENu::VariableFromConfig* v = var1D.second;
    v->InitializeMCHistograms(mc_error_bands,selected_reco_tags);
    v->InitializeSelectedTruthHistograms(mc_error_bands,selected_truth_tags);
    v->InitializeDataHistograms(data_error_bands,datatags);
    // v->AddMCResponse(responsetags);
    v->InitializeTruthHistograms(truth_error_bands,truthtags);
    v->InitializeResponse(mc_error_bands,responsetags);
    v->InitializeTunedMCHistograms(mc_error_bands,truth_error_bands,selected_reco_tags,responsetags);
    variables1D.push_back(v);
  }


  for (auto var2D : variablesmap2D ) {
    std::string varname = var2D.first;
    CCQENu::Variable2DFromConfig* v = var2D.second;
    v->InitializeMCHistograms2D(mc_error_bands,selected_reco_tags);
    v->InitializeSelectedTruthHistograms2D(mc_error_bands,selected_truth_tags);
    v->InitializeDataHistograms2D(data_error_bands,datatags);
    // v->AddMCResponse2D(responsetags);
    v->InitializeTruthHistograms2D(truth_error_bands,truthtags);
    v->InitializeResponse2D(mc_error_bands,responsetags);
    v->InitializeTunedMCHistograms2D(mc_error_bands,truth_error_bands,selected_reco_tags,responsetags);
    variables2D.push_back(v);
  }
	
	bool bdtg_vars = 0;
	if (config.IsMember("bdtgVars")) {
		bdtg_vars = config.GetBool("bdtgVars");
	}
	// Check if using progress bar during loops
	bool use_prog_bar = 0;
	if (config.IsMember("useProgressBar")) {
		use_prog_bar = config.GetBool("useProgressBar");
	}

	std::cout << " just before event loop" << std::endl;
	util.PrintMacroConfiguration("runEventLoop");
  // here we fill them

	if (bdtg_vars) {
		for (auto tag:datatags){
		  //=========================================
		  // Entry loop and fill
		  //=========================================
		  std::cout << "Loop and Fill Data for " << tag << "\n";
		  
		  LoopAndFillBDTG(tag, util, data_error_bands, variables1D, variables2D, kData, *selectionCriteria[tag], model, mcRescale, closure, use_prog_bar);

		  // LoopAndFillEventSelection2D(tag, util, data_error_bands, variables2D, kData, *selectionCriteria[tag]);

		  std::cout << "\nCut summary for Data:" <<  tag << "\n" << *selectionCriteria[tag] << "\n";
		  selectionCriteria[tag]->resetStats();
		}

		for (auto tag:selected_reco_tags){
		  unsigned int loc = tag.find("___")+3;
		  std::string cat(tag,loc,string::npos);
		  std::string sample(tag,0,loc-3);
		  mcRescale.SetCat(cat);
		  std::cout << "Loop and Fill MC Reco  for " <<  tag << "\n";
		  
		  if(cutsfilename.find("speedtest") != std::string::npos) {
		  	std::cout << "Doing speed test..." << std::endl;
		  	LoopAndFillBDTG(tag, util, mc_error_bands, variables1D, variables2D, kMC, *selectionCriteria[tag], model, mcRescale, closure, use_prog_bar);
		  }
		  else {
		  	LoopAndFillBDTG(tag, util, mc_error_bands, variables1D, variables2D, kMC, *selectionCriteria[tag], model, mcRescale, closure, use_prog_bar);
		  }
		  // LoopAndFillEventSelection2D(tag, util, mc_error_bands, variables2D, kMC, *selectionCriteria[tag]);
		  
		  std::cout << "\nCut summary for MC Reco:" <<  tag << "\n" << *selectionCriteria[tag] << "\n";
		  selectionCriteria[tag]->resetStats();
		}

		for (auto tag:truthtags){
		  std::cout << "Loop and Fill MC Truth  for " <<  tag << "\n";

			if(cutsfilename.find("speedtest") != std::string::npos) {
		  	std::cout << "Doing speed test..." << std::endl;
		  	LoopAndFillBDTG(tag, util, truth_error_bands, variables1D, variables2D, kTruth, *selectionCriteria[tag], model, mcRescale, closure, use_prog_bar);
		  }
		  else {
		  	LoopAndFillBDTG(tag, util, truth_error_bands, variables1D, variables2D, kTruth, *selectionCriteria[tag], model, mcRescale, closure, use_prog_bar);
		  }
		  // LoopAndFillEventSelection2D(tag, util, truth_error_bands, variables2D, kTruth, *selectionCriteria[tag]);
		  
		  std::cout << "\nCut summary for MC Truth:" <<  tag << "\n";
		  // this is a special overload to allow printing truth
		  (*selectionCriteria[tag]).summarizeTruthWithStats(std::cout);
		  selectionCriteria[tag]->resetStats();
		}
	}
	else {
		for (auto tag:datatags){
		  //=========================================
		  // Entry loop and fill
		  //=========================================
		  std::cout << "Loop and Fill Data for " << tag << "\n";
		  
		  LoopAndFillEventSelection(tag, util, data_error_bands, variables1D, variables2D, kData, *selectionCriteria[tag], model, mcRescale, closure, use_prog_bar);

		  // LoopAndFillEventSelection2D(tag, util, data_error_bands, variables2D, kData, *selectionCriteria[tag]);

		  std::cout << "\nCut summary for Data:" <<  tag << "\n" << *selectionCriteria[tag] << "\n";
		  selectionCriteria[tag]->resetStats();
		}

		for (auto tag:selected_reco_tags){
		  unsigned int loc = tag.find("___")+3;
		  std::string cat(tag,loc,string::npos);
		  std::string sample(tag,0,loc-3);
		  mcRescale.SetCat(cat);
		  std::cout << "Loop and Fill MC Reco  for " <<  tag << "\n";
		  
		  if(cutsfilename.find("speedtest") != std::string::npos) {
		  	std::cout << "Doing speed test..." << std::endl;
		  	LoopAndFillEventSelection2(tag, util, mc_error_bands, variables1D, variables2D, kMC, *selectionCriteria[tag], model, mcRescale, closure, use_prog_bar);
		  }
		  else {
		  	LoopAndFillEventSelection(tag, util, mc_error_bands, variables1D, variables2D, kMC, *selectionCriteria[tag], model, mcRescale, closure, use_prog_bar);
		  }
		  // LoopAndFillEventSelection2D(tag, util, mc_error_bands, variables2D, kMC, *selectionCriteria[tag]);
		  
		  std::cout << "\nCut summary for MC Reco:" <<  tag << "\n" << *selectionCriteria[tag] << "\n";
		  selectionCriteria[tag]->resetStats();
		}

		for (auto tag:truthtags){
		  std::cout << "Loop and Fill MC Truth  for " <<  tag << "\n";

			if(cutsfilename.find("speedtest") != std::string::npos) {
		  	std::cout << "Doing speed test..." << std::endl;
		  	LoopAndFillEventSelection2(tag, util, truth_error_bands, variables1D, variables2D, kTruth, *selectionCriteria[tag], model, mcRescale, closure, use_prog_bar);
		  }
		  else {
		  	LoopAndFillEventSelection(tag, util, truth_error_bands, variables1D, variables2D, kTruth, *selectionCriteria[tag], model, mcRescale, closure, use_prog_bar);
		  }
		  // LoopAndFillEventSelection2D(tag, util, truth_error_bands, variables2D, kTruth, *selectionCriteria[tag]);
		  
		  std::cout << "\nCut summary for MC Truth:" <<  tag << "\n";
		  // this is a special overload to allow printing truth
		  (*selectionCriteria[tag]).summarizeTruthWithStats(std::cout);
		  selectionCriteria[tag]->resetStats();
		}
	}
  //std::cout << "\nCut summary for MC:\n" << selectionCriteria << "\n";

  // Sync CV hists

  for (auto v : variables1D) v->SyncAllHists();
  for (auto v : variables2D) v->SyncAllHists();
  //=========================================
  // Plot
  //=========================================
  std::cout << "\n\nDone filling. Begin plotting.\n";

  std::string path(pl);

  std::string base = path.substr(path.find_last_of("/\\") + 1);
  std::string outname = Form("%s_%s_%d.root",config.GetString("outRoot").c_str(),base.c_str(),prescale);
  std::cout << " outname is " << outname << " prescale was " << prescale << std::endl;
  // std::string outname = config.GetString("outRoot")+"_"+pl+"_"+prescale+".root";
  TFile* out=TFile::Open((dir.append(outname)).c_str(),"RECREATE");

  // dump the json files

  std::string top = config.ToString();
  TNamed topobj("main",top.c_str());
  topobj.Write();
  std::string var = configvar.ToString();
  TNamed varobj("varsFile",var.c_str());
  varobj.Write();
  std::string cuts = cutsConfig.ToString();
  TNamed cutsobj("cutsFile",cuts.c_str());
  cutsobj.Write();
  std::string sam = samplesConfig.ToString();
  TNamed samobj("samplesFile",cuts.c_str());
  samobj.Write();
  //std::string git = git::commitHash();
  //TNamed gitobj("gitVersion",git.c_str());
  //gitobj.Write();

  for (auto v : variables1D){
    std::cout << "Writing 1D hist to file" << std::endl;
    v->WriteAllHistogramsToFile(*out);
  }
  for (auto v : variables2D){
    std::cout << "Writing 2D hist to file" << std::endl;
    v->WriteAllHistogramsToFile2D(*out);
  }

  PlotUtils::MnvH1D* h_pot = new PlotUtils::MnvH1D("POT_summary","data, mc, Prescaled mc", 3, 0., 3.);

  h_pot->Fill(0.5, util.m_data_pot);
  h_pot->Fill(1.5, util.m_mc_pot);
  h_pot->Fill(2.5, util.m_mc_pot/prescale);  // compensate for prescale
  h_pot->Print();
  h_pot->Write();
  // make compatible with Amit
  TVector2 *pot = new TVector2( util.m_data_pot,util.m_mc_pot/prescale);
  out->WriteTObject( pot, "pot" );
  out->Close();
  std::cout << "Successfully wrote everything to file " << outname << std::endl;
  std::cout << "Done" << std::endl;
}
