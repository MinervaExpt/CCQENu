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
#include "TSystem.h" 

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
  
  bool useTuned=false;
  if(config.IsMember("useTuned")){
    useTuned = config.GetBool("useTuned");
    std::cout << "runsamplesMain: useTuned configured in main config and set to " << useTuned << std::endl;
  }
  bool doresolution = false;
  if (config.IsMember("DoResolution")){
    doresolution = config.GetBool("DoResolution");
    std::cout << " ask for resolutions" << std::endl;
  }
  
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
  
  // Check if sending events to csv file
	bool mc_reco_to_csv = 0;
	bool tmva_trees = 0;
	std::vector<std::string> branches;
	if (config.IsMember("mcRecoToCSV")) {
		mc_reco_to_csv = config.GetBool("mcRecoToCSV");
	}
	if (config.IsMember("tmvaTrees")) {
		tmva_trees = config.GetBool("tmvaTrees");
	}
	// Check if using progress bar during loops
	bool use_prog_bar = 0;
	if (config.IsMember("useProgressBar")) {
		use_prog_bar = config.GetBool("useProgressBar");
	}
	
	// Do this to prevent annoying warning
	PlotUtils::MinervaUniverse::RPAMaterials(true);
	PlotUtils::MinervaUniverse::SetZExpansionFaReweight(true);
	
	//Selection Criteria

  std::string cutsfilename = config.GetString("cutsFile");
  NuConfig cutsConfig;
  cutsConfig.Read(cutsfilename);

  std::string samplesfilename = config.GetString("samplesFile");
  NuConfig samplesConfig;
  //cutsConfig.Print();
  std::vector<string> samplesToDo=config.GetStringVector("runsamples"); // get the master list.
  samplesConfig.Read(samplesfilename);
  //samplesConfig.Print();
  
  // Model Tune
  std::string modeltune="MnvTunev1";
  if(config.IsMember("MinervaModel")){ //TODO
    modeltune = config.GetString("MinervaModel");
    std::cout << "runsamplesMain: MinervaModel configured in main config and set to " << modeltune << std::endl;
  }
  else{
    std::cout << "runsamplesMain: MinervaModel NOT configured or set in main config. Defaulting to MnvTunev1." << std::endl;
    modeltune="MnvTunev1";
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
  const bool do_truth = true;
  
  std::vector<int> file_entries;
  std::vector<std::string> file_names;
  std::vector<std::string> output_names;
  std::string line;
  std::ifstream mFile (mc_file_list);
  while (mFile.peek()!=EOF) {
  	getline(mFile, line);
  	TFile *f = new TFile(line.c_str(),"read");
  	//TTree *t=(TTree*)f->Get("CCQENu");
  	TTree *t=(TTree*)f->Get(reco_tree_name.c_str());
  	file_entries.push_back(t->GetEntries());
  	delete t;
  	f->Close();
  	std::string fn = line.c_str();
  	file_names.push_back(fn);
  	output_names.push_back(fn.substr(fn.find_last_of("_")+1,fn.find_last_of("t")-fn.find_last_of("_")));
  }
  
  std::cout << std::endl << "Entries per file: { ";
  for (int i=0; i<file_entries.size()-1; i++) {
  	std::cout << file_entries[i] << ", ";
  }
  std::cout << file_entries[file_entries.size()-1] << " }" << std::endl;
  
  for( auto fname : file_names ){
  
  	std::cout << std::endl << "Doing file " << fname << " ..." << std::endl;

		PlotUtils::MacroUtil util(reco_tree_name, fname, data_file_list,
		                          plist_string, do_truth);

		//Data, MC reco, and Truth trees


		util.PrintMacroConfiguration("runEventLoop");
		
		// Setup systematics-related constants
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
		  NuConfig recocuts = cutsConfig.GetValue(sample.GetReco());
		  NuConfig phasespace = cutsConfig.GetValue(sample.GetPhaseSpace());
		  std::map<const std::string, CCQENu::Category> categories = sample.GetCategories();

		  for (auto category:categories){
		    std::string cname = category.first;
		    tag = cname;
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
		std::vector<CCQENu::VariableFromConfig*> variables1D;
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
		std::map<std::string,CCQENu::VariableFromConfig*> variablesmap1D = GetVariablesFromConfig(vars1D,tags,configvar,doresolution);

		std::vector<std::string> recotags;
		
		//std::string path(pl);
		//std::string outNameBase = path.substr(path.find_last_of("/\\") + 1);
		std::string path(fname);
		std::string outNameBase = path.substr(path.find_last_of("_") + 1,path.find(".")-path.find_last_of("_")-1);

		for (auto sample:samples){
		  std::map<const std::string, CCQENu::Category> categories = sample.GetCategories();
		  std::string name = sample.GetName();
		  for (auto category:categories){
		    std::string cname = category.first;
		    std::string tag = cname;
		    recotags.push_back(tag);
		  }
		}

		for (auto tag:tags){
			std:cout << "tag: " << tag << std::endl;
		}

		for (auto var1D : variablesmap1D) {
		  CCQENu::VariableFromConfig* v = var1D.second;
		  variables1D.push_back(v);
		}
		
		std::cout << " just before event loop" << std::endl;
		util.PrintMacroConfiguration("runEventLoop");
		// here we fill them

		//=========================================
		// Entry loop and fill
		//=========================================
		std::cout << "Loop and Fill ...\n";
		int nentries = util.GetMCEntries();
		
		if (tmva_trees) {
			branches = config.GetStringVector("tmvaBranches");
			LoopAndFillTMVA(file_entries, nentries, mc_error_bands, variables1D, selectionCriteria, model, outNameBase, 
				              recotags, branches, closure, use_prog_bar);
		}
		
		if (mc_reco_to_csv) {
			LoopAndFillCSV(file_entries, nentries, mc_error_bands, variables1D, selectionCriteria, model,
			               outNameBase, recotags, closure, use_prog_bar);
		}

		std::cout << "Success" << std::endl;
	}
	
	std::cout << std::endl << "Combining root files ... " << std::endl << std::endl;
	
	std::string hadd_func = "hadd -f ";
	hadd_func += mc_file_list.substr(mc_file_list.find_last_of("/\\")+1,mc_file_list.find(".")-mc_file_list.find_last_of("/\\")-1);
	hadd_func += "_TMVA.root";
	for (auto outname : output_names){
		hadd_func += " " + outname;
	}
	
	gSystem->Exec(hadd_func.c_str());
	
	for (auto outname : output_names){
		std::string rm_func = "rm " + outname;
		gSystem->Exec(rm_func.c_str());
		std::cout << std::endl << "Removing " << outname;
	}
	
	std::cout << std::endl << std::endl << "Success" << std::endl;

}
