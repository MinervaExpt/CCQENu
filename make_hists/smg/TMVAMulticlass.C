/// \file
/// \ingroup tutorial_tmva
/// \notebook -nodraw
/// This macro provides a simple example for the training and testing of the TMVA
/// multiclass classification
/// - Project   : TMVA - a Root-integrated toolkit for multivariate data analysis
/// - Package   : TMVA
/// - Root Macro: TMVAMulticlass
///
/// \macro_output
/// \macro_code
/// \author Andreas Hoecker

#include <cstdlib>
#include <iostream>
#include <map>
#include <string>

#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TSystem.h"
#include "TROOT.h"

#include "utils/NuConfig.h"

#include "TMVA/Tools.h"
#include "TMVA/Factory.h"
#include "TMVA/DataLoader.h"
#include "TMVA/TMVAMultiClassGui.h"


using namespace TMVA;

int main( int argc, char** argv )
{
	std::string pl;
	if (argc == 2){
    pl = std::string(argv[1]);
  }
  else{
    std::cout << " arguments are:\n [path/to/]TMVAMulticlass <path/to/config> " << std::endl;
    exit(0);
  }
  
  std::string configfilename(pl+".json");
	NuConfig config;
	config.Read(configfilename);

	// This loads the library
	TMVA::Tools::Instance();

	// to get access to the GUI and all tmva macros
	//
	//     TString tmva_dir(TString(gRootDir) + "/tmva");
	//     if(gSystem->Getenv("TMVASYS"))
	//        tmva_dir = TString(gSystem->Getenv("TMVASYS"));
	//     gROOT->SetMacroPath(tmva_dir + "/test/:" + gROOT->GetMacroPath() );
	//     gROOT->ProcessLine(".L TMVAMultiClassGui.C");the number of


	//---------------------------------------------------------------
	// Default MVA methods to be trained + tested
	NuConfig methodsConfig = config.GetConfig("Methods");
	std::map<std::string,int> Use;
	Use["MLP"]     = methodsConfig.GetBool("MLP");
	Use["BDTG"]    = methodsConfig.GetBool("BDTG");
	Use["DL_CPU"]  = methodsConfig.GetBool("DL_CPU");
	Use["DL_GPU"]  = methodsConfig.GetBool("DL_GPU");
	Use["FDA_GA"]  = methodsConfig.GetBool("FDA_GA");
	Use["PDEFoam"] = methodsConfig.GetBool("PDEFoam");

   //---------------------------------------------------------------

	std::cout << std::endl;
	std::cout << "==> Start TMVAMulticlass" << std::endl;

	// Create a new root output file.
	TString outfileName = std::string("Multiclassed_"+config.GetString("Tag")+"_"+config.GetString("InFile"));
	TFile* outputFile = TFile::Open( outfileName, "RECREATE" );

	TMVA::Factory *factory = new TMVA::Factory( std::string("TMVAMulticlass_"+config.GetString("Tag")), outputFile,
		                                         "!V:!Silent:Color:DrawProgressBar:Transformations=I;D;P;G,D:AnalysisType=Multiclass" );
	TMVA::DataLoader *dataloader=new TMVA::DataLoader("dataset");

	/*dataloader->AddVariable( "var1", 'F' );
	dataloader->AddVariable( "var2", "Variable 2", "", 'F' );
	dataloader->AddVariable( "var3", "Variable 3", "units", 'F' );
	dataloader->AddVariable( "var4", "Variable 4", "units", 'F' );*/
	
	NuConfig varsConfig = config.GetConfig("VariableArgs");
	std::vector<std::string> variables = config.GetStringVector("Variables");
	for (auto var : variables) {
		std::cout << "Adding variable " << var << " to dataloader." << std::endl;
		NuConfig argsConfig = varsConfig.GetConfig(var.c_str());
		char type;
		if (argsConfig.GetString("type")=="F") { 
			type = 'F'; 
		}
		else if (argsConfig.GetString("type")=="I") {
			type = 'I';
		}
		else {
			std::cout << std::endl << "ERROR: Invalid char type for variable " << var << "." << std::endl;
			exit(1);
		}
		dataloader->AddVariable(var.c_str(),
		                        argsConfig.GetString("title").c_str(),
		                        argsConfig.GetString("units").c_str(),
		                        type);
	}
  /*
	dataloader->AddVariable("CCQENu_proton_score1", "Proton Score 1", "units", 'F' );
	dataloader->AddVariable("CCQENu_proton_T_fromdEdx", "Primary Proton T from dEdx", "GeV", 'F' );
	dataloader->AddVariable("CCQENu_sec_protons_proton_scores1_sz", "Secondary Proton Candidate Count","units", 'I' );
	dataloader->AddVariable("clusters_at_end_of_primary_proton","Clusters At End of Primary Proton Prong","count",'I');
	dataloader->AddVariable("primary_proton_track_vtx_gap","Primary Proton Track-Vertex Gap","mm",'F');
	dataloader->AddVariable("blob_count","Blob Count","count",'I');
	dataloader->AddVariable("improved_michel_match_vec_sz","Improved Michel Count","count",'I');
	dataloader->AddVariable("multiplicity","Multiplicity","count",'I');
	*/
	/*
	NuConfig specsConfig = config.GetConfig("SpectatorArgs");
	std::vector<std::string> spectators = config.GetStringVector("Spectators");
	for (auto spec : spectators) {
		std::cout << "Adding spectator " << spec << " to dataloader." << std::endl;
		NuConfig argsConfig = varsConfig.GetConfig(spec.c_str());
		char type;
		if (argsConfig.GetString("type")=="F") { 
			type = 'F'; 
		}
		else if (argsConfig.GetString("type")=="I") {
			type = 'I';
		}
		else {
			std::cout << std::endl << "ERROR: Invalid char type for spectator " << spec << "." << std::endl;
			exit(1);
		}
		dataloader->AddSpectator(spec.c_str(),
		                         argsConfig.GetString("title").c_str(),
		                         argsConfig.GetString("units").c_str(),
		                         type);
	}
	*/
	/*
	dataloader->AddSpectator("mc_intType","mc type","units",'I');
	dataloader->AddSpectator("weight","weight ","units",'F');
	dataloader->AddSpectator("q2qe","Q2QE ","GeV",'F');
	dataloader->AddSpectator("ptmu","ptmu ","GeV",'F');
	dataloader->AddSpectator("pzmu","pzmu ","GeV",'F');
	dataloader->AddSpectator("recoil","recoil ","GeV",'F');
	*/

	TFile *input(0);
	TString fname = config.GetString("InFile");
	if (!gSystem->AccessPathName( fname )) {
		input = TFile::Open( fname ); // check if file in local directory exists
	}
	else {
		std::cout << std::endl << "ERROR: could not open file " << config.GetString("InFile") << std::endl;
		exit(1);
	}
	std::cout << "--- TMVAMulticlass: Using input file: " << input->GetName() << std::endl;
	
	std::string sigT = config.GetString("SignalTree");
	std::vector<std::string> bkgdTs = config.GetStringVector("BackgroundTrees");
	
	std::cout << "Creating and adding Trees." << std::endl;
	TTree *signalTree  = (TTree*)input->Get(sigT.c_str());
	TTree *background0 = (TTree*)input->Get(bkgdTs[0].c_str());
	TTree *background1 = (TTree*)input->Get(bkgdTs[1].c_str());
	TTree *background2 = (TTree*)input->Get(bkgdTs[2].c_str());
	TTree *background3 = (TTree*)input->Get(bkgdTs[3].c_str());
	
	gROOT->cd( outfileName+TString(":/") );
	dataloader->AddTree(signalTree,sigT.c_str());
	dataloader->AddTree(background0,bkgdTs[0].c_str());
	dataloader->AddTree(background1,bkgdTs[1].c_str());
	dataloader->AddTree(background2,bkgdTs[2].c_str());
	dataloader->AddTree(background3,bkgdTs[3].c_str());
	
	std::cout << "Setting weights." << std::endl;
	dataloader->SetWeightExpression("weight",sigT.c_str());
	dataloader->SetWeightExpression("weight",bkgdTs[0].c_str());
	dataloader->SetWeightExpression("weight",bkgdTs[1].c_str());
	dataloader->SetWeightExpression("weight",bkgdTs[2].c_str());
	dataloader->SetWeightExpression("weight",bkgdTs[3].c_str());
	/*
	TTree *signalTree  = (TTree*)input->Get("Mult2p___qelike");
	TTree *background0 = (TTree*)input->Get("Mult2p___1chargedpion");
	TTree *background1 = (TTree*)input->Get("Mult2p___1neutralpion");
	TTree *background2 = (TTree*)input->Get("Mult2p___multipion");
	TTree *background3 = (TTree*)input->Get("Mult2p___other");
	
	gROOT->cd( outfileName+TString(":/") );
	dataloader->AddTree(signalTree,"Mult2p___qelike");
	dataloader->AddTree(background0,"Mult2p___1chargedpion");
	dataloader->AddTree(background1,"Mult2p___1neutralpion");
	dataloader->AddTree(background2,"Mult2p___multipion");
	dataloader->AddTree(background3,"Mult2p___other");
   
	dataloader->SetWeightExpression( "weight", "Mult2p___qelike" );
	dataloader->SetWeightExpression( "weight", "Mult2p___1chargedpion" );
	dataloader->SetWeightExpression( "weight", "Mult2p___1neutralpion" );
	dataloader->SetWeightExpression( "weight", "Mult2p___multipion" );
	dataloader->SetWeightExpression( "weight", "Mult2p___other" );
	*/
	std::cout << "Reading in cuts." << std::endl;
	TCut mycuts = config.GetString("Cuts").c_str();
	
	std::cout << "Preparing Training and Test Trees." << std::endl;
	dataloader->PrepareTrainingAndTestTree(mycuts, "SplitMode=Random:NormMode=NumEvents:!V" );

	if (Use["BDTG"]) // gradient boosted decision trees
		factory->BookMethod( dataloader,  TMVA::Types::kBDT, "BDTG", "!H:!V:NTrees=1000:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.50:nCuts=20:MaxDepth=3");
	if (Use["MLP"]) // neural network
		factory->BookMethod( dataloader,  TMVA::Types::kMLP, "MLP", "!H:!V:NeuronType=tanh:NCycles=1000:HiddenLayers=N+5,5:TestRate=5:EstimatorType=MSE");
	if (Use["FDA_GA"]) // functional discriminant with GA minimizer
		factory->BookMethod( dataloader,  TMVA::Types::kFDA, "FDA_GA", "H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3+(5)*x4+(6)*x5+(7)*x6+(8)*x7:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=GA:PopSize=300:Cycles=3:Steps=20:Trim=True:SaveBestGen=1" );
	if (Use["PDEFoam"]) // PDE-Foam approach
		factory->BookMethod( dataloader,  TMVA::Types::kPDEFoam, "PDEFoam", "!H:!V:TailCut=0.001:VolFrac=0.0666:nActiveCells=500:nSampl=2000:nBin=5:Nmin=100:Kernel=None:Compress=T" );


	if (Use["DL_CPU"]) {
		TString layoutString("Layout=TANH|100,TANH|50,TANH|10,LINEAR");
		TString trainingStrategyString("TrainingStrategy=Optimizer=ADAM,LearningRate=1e-3,"
		                               "TestRepetitions=1,ConvergenceSteps=10,BatchSize=100");
		TString nnOptions("!H:V:ErrorStrategy=CROSSENTROPY:VarTransform=N:"
		                  "WeightInitialization=XAVIERUNIFORM:Architecture=GPU");
		nnOptions.Append(":");
		nnOptions.Append(layoutString);
		nnOptions.Append(":");
		nnOptions.Append(trainingStrategyString);
		factory->BookMethod(dataloader, TMVA::Types::kDL, "DL_CPU", nnOptions);
	}
	if (Use["DL_GPU"]) {
		TString layoutString("Layout=TANH|100,TANH|50,TANH|10,LINEAR");
		TString trainingStrategyString("TrainingStrategy=Optimizer=ADAM,LearningRate=1e-3,"
		                               "TestRepetitions=1,ConvergenceSteps=10,BatchSize=100");
		TString nnOptions("!H:V:ErrorStrategy=CROSSENTROPY:VarTransform=N:"
		                  "WeightInitialization=XAVIERUNIFORM:Architecture=GPU");
		nnOptions.Append(":");
		nnOptions.Append(layoutString);
		nnOptions.Append(":");
		nnOptions.Append(trainingStrategyString);
		factory->BookMethod(dataloader, TMVA::Types::kDL, "DL_GPU", nnOptions);
	}
   
	// Train MVAs using the set of training events
	factory->TrainAllMethods();

	// Evaluate all MVAs using the set of test events
	factory->TestAllMethods();

	// Evaluate and compare performance of all configured MVAs
	factory->EvaluateAllMethods();

	// --------------------------------------------------------------

	// Save the output
	outputFile->Close();

	std::cout << "==> Wrote root file: " << outputFile->GetName() << std::endl;
	std::cout << "==> TMVAMulticlass is done!" << std::endl;

	auto c0 = factory->GetROCCurve(dataloader);
	c0->Draw();

	delete factory;
	delete dataloader;

	// Launch the GUI for the root macros
	if (!gROOT->IsBatch()) TMVAMultiClassGui( outfileName );
	TMVAMultiClassGui( outfileName );

	return 0;
}
