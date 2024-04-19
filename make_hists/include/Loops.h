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
* This implements a loop over the tuple that fills the histograms
 */
#include "TMVA/RReader.hxx"
#include "TMVA/RBDT.hxx"
#include "utils/expandEnv.h"

enum EDataMCTruth {kData, kMC, kTruth, kNDataMCTruthTypes};

void ProgressBar(int nentries,
                 int entry,
                 bool pbar, 
                 EDataMCTruth data_mc_truth,
                 int prescale) {

	if(pbar) {
		if(data_mc_truth != kData) {
			entry = int(entry/prescale);
			nentries = int(nentries/prescale);
		}
		int progress = 40.*(entry+1)/nentries;
		int minprogress = 0;
		if (data_mc_truth == kMC) { minprogress = 2; }
		
		if (progress >= minprogress) {	
			if ((entry+1 == std::ceil((nentries/40.)*progress)) || entry == 0) {
				if (progress == minprogress) { // First entry produces bar labels
					std::cout << std::endl;
					std::cout << "  0% 10% 20% 30% 40% 50% 60% 70% 80% 90% 100%" << std::endl;
					std::cout << "   \\___\\___\\___\\___\\___\\___\\___\\___\\___\\___\\ " << std::endl;
				}	
				std::cout << '\r' << std::flush << "   |"; //Clear current line
				for (int step=0; step<progress; step++) { std::cout << "\e[0;31;47m \e[0m"; }
				for (int step=0; step<40-progress; step++) { std::cout << "_"; }
				std::cout << "|   [";
				if (progress<4) { std::cout << "_"; }
				if (progress<40) { std::cout << "_"; }
				std::cout << progress*2.5;
				if (progress % 2 == 0) { std::cout << ".0%]   ( "; }
				else { std::cout << "%]   ( "; }
				for(int j=((int)log10(nentries)-(int)log10(entry+1)); j>0; j--) {
					std::cout << "_";
				}
				std::cout << entry+1 << " / " << nentries << " )";

				if (entry == nentries-1) { // Last entry closes status bar
					std::cout << std::endl << std::endl;
				}
			}
		}
	}
	
}

//#define CLOSUREDETAIL

//==============================================================================
// Loop and fill
//==============================================================================
#ifndef __CINT__ //for PlotUtils::cuts_t<>
void LoopAndFillEventSelection(std::string tag,
                               const PlotUtils::MacroUtil& util,
                               std::map<std::string, std::vector<CVUniverse*> > error_bands,
                               std::vector<CCQENu::VariableFromConfig*>& variables,
                               std::vector<CCQENu::Variable2DFromConfig*>& variables2D,
                               EDataMCTruth data_mc_truth,
                               PlotUtils::Cutter<CVUniverse>& selection, 
                               PlotUtils::Model<CVUniverse,PlotUtils::detail::empty>& model, 
                               PlotUtils::weight_MCreScale mcRescale,
                               bool closure=false, bool mc_reco_to_csv=false) {

  // Prepare loop
  MinervaUniverse::SetTruth(false);
  int nentries = -1;

  // get ready for weights by finding cv universe pointer

  assert(!error_bands["cv"].empty() && "\"cv\" error band is empty!  Can't set Model weight.");
  auto& cvUniv = error_bands["cv"].front();
  // make a dummy event - may need to make fancier
  PlotUtils::detail::empty event;

  if ( variables.size() < 1) {
    std::cout << " no variables to fill " << std::endl;
    return;  // don't bother if there are no variables.
  }

  if (data_mc_truth == kData){
    nentries = util.GetDataEntries();
  }
  else if (data_mc_truth == kMC){
    nentries = util.GetMCEntries();
  }
  else{
    nentries = util.GetTruthEntries() ;
    MinervaUniverse::SetTruth(true);
  }


  unsigned int loc = tag.find("___")+3;
  std::string cat(tag,loc,string::npos);
  std::string sample(tag,0,loc-3);
  std::cout << sample << " category " << cat << std::endl;
  std::cout << " starting loop " << data_mc_truth << " " << nentries << std::endl;

	// Begin entries loop
  for (int i = 0; i < nentries; i++) {
    		
		ProgressBar(nentries,i,false,data_mc_truth,prescale);
		
    cvUniv->SetEntry(i);
    //atree->GetEntry(i);

    if (data_mc_truth != kData) model.SetEntry(*cvUniv, event);


    const double cvWeight = (data_mc_truth == kData ||  closure ) ? 1. : model.GetWeight(*cvUniv,event);  // detail may be used for more complex things
    // TODO: Is this scaled cvWeight necessary?
    // const double cvWeightScaled = (data_mc_truth kData) ? 1. : cvWeight*mcRescale.GetScale(q2qe, "cv");
    
    // Loop bands and universes
    for (auto band : error_bands) {
      std::vector<CVUniverse*> error_band_universes = band.second;
      //  HMS replace with iuniv to access weights more easily
      //  HMS for (auto universe : error_band_universes) {
      std::string uni_name = (band.second)[0]->ShortName();
      for (int iuniv=0; iuniv < error_band_universes.size(); iuniv++){

        auto universe = error_band_universes[iuniv];
        universe->SetEntry(i);

        // Process this event/universe
        //double weight = 1;
        //if (universe->ShortName() == "cv" ) weight = data_mc_truth == kData ? 1. : universe->GetWeight();

        // probably want to move this later on inside the loop
        const double weight = (data_mc_truth == kData || closure) ? 1. : model.GetWeight(*universe, event); //Only calculate the per-universe weight for events that will actually use it.
        //PlotUtils::detail::empty event;

        //=========================================
        // Fill
        //=========================================
        
        if(data_mc_truth == kMC){
#ifdef CLOSUREDETAIL
          if(closure && universe->ShortName() == "cv" && selection.isMCSelected(*universe, event, weight).all()){
            std::cout  << universe->GetRun() << " " << universe->GetSubRun() << " " << universe->GetGate() << " " << universe->GetPmuGeV() << " " << weight << " " << selection.isDataSelected(*universe, event).all() << " " << selection.isMCSelected(*universe, event, weight).all() << " " << tag  << selection.isSignal(*universe)  << " " << universe->ShortName() <<  std::endl;
              universe->Print();
          }
#endif
					if(selection.isMCSelected(*universe, event, weight).all()
						&& selection.isSignal(*universe)) {

						//double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
						const double q2qe = universe->GetQ2QEGeV();
						double scale = 1.0;
						if (!closure) scale = mcRescale.GetScale(cat, q2qe, uni_name, iuniv); //Only calculate the per-universe weight for events that will actually use it.

						FillMC(tag, universe, weight, variables, variables2D, scale);
						FillResponse(tag,universe,weight,variables,variables2D, scale);
						FillResolution(tag,universe,weight,variables,variables2D, scale);
		      }
				}
        else if (data_mc_truth == kTruth){

          if(selection.isEfficiencyDenom(*universe, weight)){
            const double q2qe = universe->GetTrueQ2QEGeV();
            double scale = 1.0;
            if (!closure) scale =mcRescale.GetScale(cat, q2qe, uni_name, iuniv); //Only calculate the per-universe weight for events that will actually use it.
            if (closure) scale = 1.0;
            FillSignalTruth(tag, universe, weight, variables, variables2D, scale);
          }
        }
        else{ //kData
#ifdef CLOSUREDETAIL
          if (closure && selection.isDataSelected(*universe, event).all() ){
            std::cout  << universe->GetRun() << " " << universe->GetSubRun() << " " << universe->GetGate() << " " << universe->GetPmuGeV() << " " << weight << " " << selection.isDataSelected(*universe, event).all() << " " << selection.isMCSelected(*universe, event, weight).all()  << "  " << tag  << "1" << " " << universe->ShortName() <<  std::endl;
          }
#endif
          if(selection.isDataSelected(*universe, event).all()) {
            FillData(tag, universe, variables, variables2D);
            
          }
        }

      } // End universes
    } // End error bands
    
    if(data_mc_truth != kData) i+= prescale-1;
    
  } // End entries loop

}

void LoopAndFillCSV(std::vector<int> file_entries,
                    int nentries,
                    std::map<std::string, std::vector<CVUniverse*> > error_bands,
                    std::vector<CCQENu::VariableFromConfig*>& variables,
                    std::map<std::string,PlotUtils::Cutter<CVUniverse> *> selectionCriteria, 
                    PlotUtils::Model<CVUniverse,PlotUtils::detail::empty>& model,
                    std::string outNameBase,
                    std::vector<std::string> recotags,
                    bool closure=false, bool use_prog_bar=false) {

	gROOT->ProcessLine("#include <vector>");

	// Prepare loop
  MinervaUniverse::SetTruth(false);

  // get ready for weights by finding cv universe pointer

  assert(!error_bands["cv"].empty() && "\"cv\" error band is empty!  Can't set Model weight.");
  auto& cvUniv = error_bands["cv"].front();
  // make a dummy event - may need to make fancier
  PlotUtils::detail::empty event;

  if ( variables.size() < 1) {
    std::cout << " no variables to fill " << std::endl;
    return;  // don't bother if there are no variables.
  }
  
  // TMVA setup
  /*
  std::cout << std::endl << "Loading TMVA Macro "
            << "/home/sean/MinervaExpt/CCQENu/make_hists/smg/dataset/weights/TMVAMulticlass_BDTG.class.C" 
            << std::endl;
  gROOT->LoadMacro("/home/sean/MinervaExpt/CCQENu/make_hists/smg/dataset/weights/TMVAMulticlass_BDTG.class.C");
  // define the names of the input variables (same as for training)
  std::vector<std::string> inputVars = {"CCQENu_proton_score1",
                                        "primary_proton_track_vtx_gap",
                                        "CCQENu_proton_T_fromdEdx",
                                        "primary_proton_clusters",
                                        "primary_proton_fraction_vis_energy_in_cone",
                                        "blob_count",
                                        "improved_michel_match_vec_sz",
                                        "recoil"};
	// create a class object for the BDTG response
	IClassifierReader* bdtgResponse = new ReadBDTG( inputVars );*/

	// CSV setup
  std::string csvFileName = "CSV_"+outNameBase+".csv";
  std::cout << "Making CSV file " << csvFileName << std::endl;
	std::ofstream csvFile;
  csvFile.open(csvFileName);
  csvFile << "Entry";
  for (auto v : variables) {
		csvFile << ";" << v->GetName();
  }
	csvFile << ";Truth;Interaction;mc_intType;qelikeBDTG;1chargedpionBDTG;1neutralpionBDTG;multipionBDTG;otherBDTG;model;ProngTrajID;nERParts;ERIDs;nFSPart;FSPDGs;FSPartEs;Arachne" << std::endl;
	std::vector<std::string> interaction = {"None","QE","RES","DIS","COHPI","AMNUGAMMA","IMD","NUEEL","2P2H","NA","Unknown"};
	
	TMVA::Experimental::RReader model_1track(expandEnv("${CCQEMAT}/TMVA/TMVAMulticlass_1track_BDTG.weights.xml"));
  TMVA::Experimental::RReader model_2track(expandEnv("${CCQEMAT}/TMVA/TMVAMulticlass_2track_BDTG.weights.xml"));
  TMVA::Experimental::RReader model_3ptrack(expandEnv("${CCQEMAT}/TMVA/TMVAMulticlass_3ptrack_BDTG.weights.xml"));
	
	// Begin loop over entries
	std::cout << std::endl << "Beginning loop over " << nentries << " entries\n" << std::endl;
	for (int i = 0; i < nentries; i++) {
	
		std::string model_name;
	
		ProgressBar(nentries,i,use_prog_bar,kMC,1);
		
		cvUniv->SetEntry(i);
		model.SetEntry(*cvUniv, event);
		
		for (auto band : error_bands) {
			std::vector<CVUniverse*> error_band_universes = band.second;
			std::string uni_name = (band.second)[0]->ShortName();
    	for (int iuniv=0; iuniv < error_band_universes.size(); iuniv++) {
    		auto universe = error_band_universes[iuniv];
    		universe->SetEntry(i);
    		const double weight = closure ? 1. : model.GetWeight(*universe, event);
    		// Reco tag loop
    		if (universe->ShortName() == "cv") {
    			std::vector<float> response_vec;
		      
			    float multiplicity = universe->GetMultiplicity();
					float proton_score1_0 = universe->GetPrimaryProtonScore1();
					float proton_score1_1 = universe->GetProtonScore1_1();
					float proton_score1_2 = universe->GetProtonScore1_2();
					float proton_track_vtx_gap_0 = universe->GetPrimaryProtonTrackVtxGap();
					float proton_track_vtx_gap_1 = universe->GetSecProtonTrackVtxGap_1();
					float proton_track_vtx_gap_2 = universe->GetSecProtonTrackVtxGap_2();
					float proton_T_from_dEdX_0 = universe->GetPrimaryProtonTfromdEdx();
					float proton_T_from_dEdX_1 = universe->GetSecProtonTfromdEdx_1();
					float proton_T_from_dEdX_2 = universe->GetSecProtonTfromdEdx_2();
					float proton_clusters_0 = universe->GetNumClustsPrimaryProtonEnd();
					float proton_clusters_1 = universe->GetNumClustsSecProtonEnd_1();
					float proton_clusters_2 = universe->GetNumClustsSecProtonEnd_2();
					float proton_fraction_vis_energy_in_cone_0 = universe->GetPrimaryProtonFractionVisEnergyInCone();
					float proton_fraction_vis_energy_in_cone_1 = universe->GetSecProtonFractionVisEnergyInCone_1();
					float proton_fraction_vis_energy_in_cone_2 = universe->GetSecProtonFractionVisEnergyInCone_2();
					float sec_proton_cand_count = universe->GetSecondaryProtonCandidateCount1();
					float muon_to_primary_proton_angle = universe->GetMuonToPrimaryProtonAngle();
					float blob_count = universe->GetNBlobs();
					float improved_michel_count = universe->GetImprovedNMichel();
					float recoil = universe->GetRecoilEnergyGeV();
					float improved_michel_1_views = universe->GetImprovedMichel_0_Views();
					float improved_michel_2_views = universe->GetImprovedMichel_1_Views();
					float improved_michel_3_views = universe->GetImprovedMichel_2_Views();
					float improved_michel_sum_views = universe->GetImprovedMichel_Sum_Views();
					
					std::vector<float> input_vars;
					
					input_vars.emplace_back(multiplicity);
					if (proton_score1_0 >= 0) {
						if (sec_proton_cand_count == 0) {
							input_vars.emplace_back(proton_score1_0);
							input_vars.emplace_back(proton_track_vtx_gap_0);
							input_vars.emplace_back(proton_T_from_dEdX_0);
							input_vars.emplace_back(proton_clusters_0);
							input_vars.emplace_back(proton_fraction_vis_energy_in_cone_0);
							input_vars.emplace_back(blob_count);
							input_vars.emplace_back(improved_michel_count);
							input_vars.emplace_back(recoil);
							input_vars.emplace_back(improved_michel_sum_views);
							input_vars.emplace_back(muon_to_primary_proton_angle);
							if (input_vars.size() == model_2track.GetVariableNames().size()) {
								response_vec = model_2track.Compute(input_vars);
								model_name = "2track";
							}
							else {
								response_vec = {0,0,0,0,0};
								std::cout << "WARNING: INPUT VECTOR SIZE DOES NOT MATCH 2 TRACK MODEL EXPECTATION" << std::endl;
							}
						}
						else {
							input_vars.emplace_back(proton_score1_0);
							input_vars.emplace_back(proton_score1_1);
							input_vars.emplace_back(proton_track_vtx_gap_0);
							input_vars.emplace_back(proton_track_vtx_gap_1);
							input_vars.emplace_back(proton_T_from_dEdX_0);
							input_vars.emplace_back(proton_clusters_0);
							input_vars.emplace_back(proton_clusters_1);
							input_vars.emplace_back(proton_fraction_vis_energy_in_cone_0);
							input_vars.emplace_back(proton_fraction_vis_energy_in_cone_1);
							input_vars.emplace_back(sec_proton_cand_count);
							input_vars.emplace_back(blob_count);
							input_vars.emplace_back(improved_michel_count);
							input_vars.emplace_back(recoil);
							input_vars.emplace_back(improved_michel_sum_views);
							input_vars.emplace_back(muon_to_primary_proton_angle);
							if (input_vars.size() == model_3ptrack.GetVariableNames().size()) {
								response_vec = model_3ptrack.Compute(input_vars);
								model_name = "3ptrack";
							}
							else {
								response_vec = {0,0,0,0,0};
								std::cout << "WARNING: INPUT VECTOR SIZE DOES NOT MATCH 3+ TRACK MODEL EXPECTATION" << std::endl;
							}
						}
					}
					else {
						input_vars.emplace_back(blob_count);
						input_vars.emplace_back(improved_michel_count);
						input_vars.emplace_back(recoil);
						input_vars.emplace_back(improved_michel_sum_views);
						if (input_vars.size() == model_1track.GetVariableNames().size()) {
								response_vec = model_1track.Compute(input_vars);
								model_name = "1track";
						}
						else {
							response_vec = {0,0,0,0,0};
							std::cout << "WARNING: INPUT VECTOR SIZE DOES NOT MATCH 1 TRACK MODEL EXPECTATION" << std::endl;
						}
					}
					
					CVUniverse::SetVectorResponse(response_vec);
					
    			for (auto tname:recotags) {
    				if(selectionCriteria[tname]->isMCSelected(*universe, event, weight).all()
    				   && selectionCriteria[tname]->isSignal(*universe)) {
							// CSV
							int mcinttype = universe->GetMCIntType();
							int ProngTrajID = universe->GetInt("proton_prong_traj_ID");
							int nERParts = universe->GetInt("mc_er_nPart");
							std::vector<int> ERIDs = universe->GetVecInt("mc_er_ID");
							int nFSParts = universe->GetTrueNumberOfFSParticles();
							std::vector<int> FSPartPDG = universe->GetVecInt("mc_FSPartPDG");
							std::vector<double> mc_FSPartE = universe->GetVecDouble("mc_FSPartE");
							
							csvFile << i;
							for (auto v : variables) {
								csvFile << ";" << v->GetRecoValue(*universe, 0);
							}
							csvFile << ";" << tname;
							csvFile << ";" << interaction[mcinttype];
							csvFile << ";" << mcinttype;
							csvFile << ";" << response_vec[0];
							csvFile << ";" << response_vec[1];
							csvFile << ";" << response_vec[2];
							csvFile << ";" << response_vec[3];
							csvFile << ";" << response_vec[4];
							csvFile << ";" << model_name;
							csvFile << ";" << ProngTrajID;
							csvFile << ";" << nERParts;
							for (int iter = 0; iter < nERParts; iter++) { 
								if (iter == 0) { csvFile << ";{"; } // Before first element
								csvFile << ERIDs[iter];
								if (iter < nERParts-1) { csvFile << ","; } // Between elements
								else { csvFile << "}"; } // After last element
							}	
							csvFile << ";" << nFSParts;					    
							for (int iter = 0; iter < nFSParts; iter++) { 
								if (iter == 0) { csvFile << ";{"; } // Before first element
								csvFile << FSPartPDG[iter];
								if (iter < nFSParts-1) { csvFile << ","; } // Between elements
								else { csvFile << "}"; } // After last element
							}							    
							for (int iter = 0; iter < nFSParts; iter++) {
								if (iter == 0) { csvFile << ";{"; } // Before first element
								csvFile << mc_FSPartE[iter];
								if (iter < nFSParts-1) { csvFile << ","; } // Between elements
								else { csvFile << "}"; } // After last element
							}							    
							csvFile << ";" << universe->StringTrueArachneLink() << std::endl;
							
		  			}
		  		}
    		}
    	}
		}
	}
	csvFile.close();
  std::cout << std::endl;
  std::cout << "Finished loop";;
  std::cout << std::endl;

}

void LoopAndFillTMVA(std::vector<int> file_entries,
                     int nentries,
                     std::map<std::string, std::vector<CVUniverse*> > error_bands,
                     std::vector<CCQENu::VariableFromConfig*>& variables,
                     std::map<std::string,PlotUtils::Cutter<CVUniverse> *> selectionCriteria, 
                     PlotUtils::Model<CVUniverse,PlotUtils::detail::empty>& model,
                     std::string outNameBase,
                     std::vector<std::string> recotags,
                     std::vector<std::string> branches={},
                     bool closure=false, bool use_prog_bar=false) {

	gROOT->ProcessLine("#include <vector>");

	// Prepare loop
  MinervaUniverse::SetTruth(false);

  // get ready for weights by finding cv universe pointer

  assert(!error_bands["cv"].empty() && "\"cv\" error band is empty!  Can't set Model weight.");
  auto& cvUniv = error_bands["cv"].front();
  // make a dummy event - may need to make fancier
  PlotUtils::detail::empty event;

  if ( variables.size() < 1) {
    std::cout << " no variables to fill " << std::endl;
    return;  // don't bother if there are no variables.
  }
	
	// tmva tree root file setup
	//TString rootFileName = "forTMVA_"+outNameBase+".root";
	TString rootFileName = outNameBase+".root";
	TFile *rootFile = new TFile(rootFileName,"recreate");
	// Tree reference and Branches
	std::cout << std::endl << "Copied branches: ";
	TTree *tree_mcreco = cvUniv->GetTree()->GetTree()->GetTree(); //This tells you how terrible our code is
	tree_mcreco->SetBranchStatus("*",0);
	for (auto activeBranchName : branches) {
		const char* branchName = activeBranchName.c_str();
		tree_mcreco->SetBranchStatus(branchName, 1);
		std::cout << std::endl << "  " << branchName;
	}
	
	std::cout << std::endl << std::endl << "New branches: ";
	
	Int_t entry;
	std::cout << std::endl << "  entry";
	
	Double_t wgt;
	Double_t q2qe;
	Double_t ptmu;
	Double_t pzmu;
	Double_t recoil;
	std::cout << std::endl << "  weight";
	std::cout << std::endl << "  q2qe";
	std::cout << std::endl << "  ptmu";
	std::cout << std::endl << "  pzmu";
	std::cout << std::endl << "  recoil";
	
	Double_t sec_proton_score1_1;
	Double_t sec_proton_score1_2;
	Double_t sec_proton_score1_3;
	std::cout << std::endl << "  sec_proton_score1_1";
	std::cout << std::endl << "  sec_proton_score1_2";
	std::cout << std::endl << "  sec_proton_score1_3";
	
	Double_t sec_proton_T_from_dEdX_1;
	Double_t sec_proton_T_from_dEdX_2;
	Double_t sec_proton_T_from_dEdX_3;
	std::cout << std::endl << "  sec_proton_T_from_dEdX_1";
	std::cout << std::endl << "  sec_proton_T_from_dEdX_2";
	std::cout << std::endl << "  sec_proton_T_from_dEdX_3";
	
	Double_t primary_proton_track_vtx_gap; 
	Double_t sec_proton_track_vtx_gap_1;
	Double_t sec_proton_track_vtx_gap_2;
	Double_t sec_proton_track_vtx_gap_3;
	std::cout << std::endl << "  primary_proton_track_vtx_gap";
	std::cout << std::endl << "  sec_proton_track_vtx_gap_1";
	std::cout << std::endl << "  sec_proton_track_vtx_gap_2";
	std::cout << std::endl << "  sec_proton_track_vtx_gap_3";
	
	Double_t primary_proton_fraction_vis_energy_in_cone;
	Double_t sec_proton_fraction_vis_energy_in_cone_1;
	Double_t sec_proton_fraction_vis_energy_in_cone_2;
	Double_t sec_proton_fraction_vis_energy_in_cone_3;
	std::cout << std::endl << "  primary_proton_fraction_vis_energy_in_cone";
	std::cout << std::endl << "  sec_proton_fraction_vis_energy_in_cone_1";
	std::cout << std::endl << "  sec_proton_fraction_vis_energy_in_cone_2";
	std::cout << std::endl << "  sec_proton_fraction_vis_energy_in_cone_3";
	
	Int_t primary_proton_clusters;
	Int_t sec_proton_clusters_1;
	Int_t sec_proton_clusters_2;
	Int_t sec_proton_clusters_3;
	std::cout << std::endl << "  primary_proton_clusters";
	std::cout << std::endl << "  sec_proton_clusters_1";
	std::cout << std::endl << "  sec_proton_clusters_2";
	std::cout << std::endl << "  sec_proton_clusters_3";

	Double_t muon_to_primary_proton_angle;
	std::cout << std::endl << "muon_to_primary_proton_angle";

	Int_t blob_count;
	std::cout << std::endl << "  blob_count";
	
	Int_t improved_michel_1_views;
	Int_t improved_michel_2_views;
	Int_t improved_michel_3_views;
	Int_t improved_michel_sum_views;
	std::cout << std::endl << "  improved_michel_1_views";
	std::cout << std::endl << "  improved_michel_2_views";
	std::cout << std::endl << "  improved_michel_3_views";
	std::cout << std::endl << "  improved_michel_sum_views";
	
	// Trees
	std::map<std::string,TTree*> ttrees;
	std::cout << "\n\nMaking following trees for " << rootFileName << ":" << std::endl;
	
	for (auto tname:recotags) {
		ttrees[tname] = tree_mcreco->CloneTree(0);
		ttrees[tname]->SetName(tname.c_str());
		std::cout << "  " << tname << std::endl;
		
		ttrees[tname]->Branch("entry",&entry,"entry/I");
		
		ttrees[tname]->Branch("weight",&wgt,"weight/D");
		ttrees[tname]->Branch("q2qe",&q2qe,"q2qe/D");
		ttrees[tname]->Branch("ptmu",&ptmu,"ptmu/D");
		ttrees[tname]->Branch("pzmu",&pzmu,"pzmu/D");
		ttrees[tname]->Branch("recoil",&recoil,"recoil/D");
		
		ttrees[tname]->Branch("sec_proton_score1_1",&sec_proton_score1_1,"sec_proton_score1_1/D");
		ttrees[tname]->Branch("sec_proton_score1_2",&sec_proton_score1_2,"sec_proton_score1_2/D");
		ttrees[tname]->Branch("sec_proton_score1_3",&sec_proton_score1_3,"sec_proton_score1_3/D");
		
		ttrees[tname]->Branch("sec_proton_T_from_dEdX_1",&sec_proton_T_from_dEdX_1,"sec_proton_T_from_dEdX_1/D");
		ttrees[tname]->Branch("sec_proton_T_from_dEdX_2",&sec_proton_T_from_dEdX_2,"sec_proton_T_from_dEdX_2/D");
		ttrees[tname]->Branch("sec_proton_T_from_dEdX_3",&sec_proton_T_from_dEdX_3,"sec_proton_T_from_dEdX_3/D");
		
		ttrees[tname]->Branch("primary_proton_track_vtx_gap",&primary_proton_track_vtx_gap,"primary_proton_track_vtx_gap/D");
		ttrees[tname]->Branch("sec_proton_track_vtx_gap_1",&sec_proton_track_vtx_gap_1,"sec_proton_track_vtx_gap_1/D");
		ttrees[tname]->Branch("sec_proton_track_vtx_gap_2",&sec_proton_track_vtx_gap_2,"sec_proton_track_vtx_gap_2/D");
		ttrees[tname]->Branch("sec_proton_track_vtx_gap_3",&sec_proton_track_vtx_gap_3,"sec_proton_track_vtx_gap_3/D");
		
		ttrees[tname]->Branch("primary_proton_fraction_vis_energy_in_cone",
		                      &primary_proton_fraction_vis_energy_in_cone,"CCQENu_proton_fraction_vis_energy_in_cone/D");
		ttrees[tname]->Branch("sec_proton_fraction_vis_energy_in_cone_1",
		                      &sec_proton_fraction_vis_energy_in_cone_1,"sec_proton_fraction_vis_energy_in_cone_1/D");
		ttrees[tname]->Branch("sec_proton_fraction_vis_energy_in_cone_2",
		                      &sec_proton_fraction_vis_energy_in_cone_2,"sec_proton_fraction_vis_energy_in_cone_2/D");
		ttrees[tname]->Branch("sec_proton_fraction_vis_energy_in_cone_3",
		                      &sec_proton_fraction_vis_energy_in_cone_3,"sec_proton_fraction_vis_energy_in_cone_3/D");
		
		ttrees[tname]->Branch("primary_proton_clusters",&primary_proton_clusters,"primary_proton_clusters/I");
		ttrees[tname]->Branch("sec_proton_clusters_1",&sec_proton_clusters_1,"sec_proton_clusters_1/I");
		ttrees[tname]->Branch("sec_proton_clusters_2",&sec_proton_clusters_2,"sec_proton_clusters_2/I");
		ttrees[tname]->Branch("sec_proton_clusters_3",&sec_proton_clusters_3,"sec_proton_clusters_3/I");
		
		ttrees[tname]->Branch("muon_to_primary_proton_angle",&muon_to_primary_proton_angle,"muon_to_primary_proton_angle/D");
		
		ttrees[tname]->Branch("blob_count",&blob_count,"blob_count/I");
		
		ttrees[tname]->Branch("improved_michel_1_views",&improved_michel_1_views,"improved_michel_1_views/I");
		ttrees[tname]->Branch("improved_michel_2_views",&improved_michel_1_views,"improved_michel_2_views/I");
		ttrees[tname]->Branch("improved_michel_3_views",&improved_michel_1_views,"improved_michel_3_views/I");
		ttrees[tname]->Branch("improved_michel_sum_views",&improved_michel_sum_views,"improved_michel_sum_views/I");
	}
	tree_mcreco->SetBranchStatus("*",1);
	
	// Begin loop over entries
	std::cout << std::endl << "Beginning loop over " << nentries << " entries\n" << std::endl;
	for (int i = 0; i < nentries; i++) {
	
		ProgressBar(nentries,i,use_prog_bar,kMC,1);
		
		cvUniv->SetEntry(i);
		model.SetEntry(*cvUniv, event);
		
		for (auto band : error_bands) {
			std::vector<CVUniverse*> error_band_universes = band.second;
			std::string uni_name = (band.second)[0]->ShortName();
    	for (int iuniv=0; iuniv < error_band_universes.size(); iuniv++) {
    		auto universe = error_band_universes[iuniv];
    		universe->SetEntry(i);
    		const double weight = closure ? 1. : model.GetWeight(*universe, event);
    		// Reco tag loop
    		if (universe->ShortName() == "cv") {  		
    			for (auto tname:recotags) {
    				if(selectionCriteria[tname]->isMCSelected(*universe, event, weight).all()
    				   && selectionCriteria[tname]->isSignal(*universe)) {
							
							// TMVA trees fill
							entry = i;
							
							wgt = universe->GetWeight();
							q2qe = universe->GetQ2QEGeV();
							ptmu = universe->GetPperpMuGeV();
							pzmu = universe->GetPparMuGeV();
							recoil = universe->GetRecoilEnergyGeV();
							
							sec_proton_score1_1 = universe->GetProtonScore1_1();
							sec_proton_score1_2 = universe->GetProtonScore1_2();
							sec_proton_score1_3 = universe->GetProtonScore1_3();
							
							sec_proton_T_from_dEdX_1 = universe->GetSecProtonTfromdEdx_1();
							sec_proton_T_from_dEdX_2 = universe->GetSecProtonTfromdEdx_2();
							sec_proton_T_from_dEdX_3 = universe->GetSecProtonTfromdEdx_3();
							
							primary_proton_track_vtx_gap = universe->GetPrimaryProtonTrackVtxGap();
							sec_proton_track_vtx_gap_1 = universe->GetSecProtonTrackVtxGap_1();
							sec_proton_track_vtx_gap_2 = universe->GetSecProtonTrackVtxGap_2();
							sec_proton_track_vtx_gap_3 = universe->GetSecProtonTrackVtxGap_3();
							
							primary_proton_fraction_vis_energy_in_cone = universe->GetPrimaryProtonFractionVisEnergyInCone();
							sec_proton_fraction_vis_energy_in_cone_1 = universe->GetSecProtonFractionVisEnergyInCone_1();
							sec_proton_fraction_vis_energy_in_cone_2 = universe->GetSecProtonFractionVisEnergyInCone_2();
							sec_proton_fraction_vis_energy_in_cone_3 = universe->GetSecProtonFractionVisEnergyInCone_3();
							
							primary_proton_clusters = universe->GetNumClustsPrimaryProtonEnd();
							sec_proton_clusters_1 = universe->GetNumClustsSecProtonEnd_1();
							sec_proton_clusters_2 = universe->GetNumClustsSecProtonEnd_2();
							sec_proton_clusters_3 = universe->GetNumClustsSecProtonEnd_3();
							
							muon_to_primary_proton_angle = universe->GetMuonToPrimaryProtonAngle();
							
							blob_count = universe->GetNBlobs();
							
							improved_michel_1_views = universe->GetImprovedMichel_0_Views();
							improved_michel_2_views = universe->GetImprovedMichel_1_Views();
							improved_michel_3_views = universe->GetImprovedMichel_2_Views();
							improved_michel_sum_views = universe->GetImprovedMichel_Sum_Views();
							
							tree_mcreco->GetEntry(i);
							ttrees[tname]->Fill();				
		  			}
		  		}
    		}
    	}
		}
	}
	rootFile->Write();
  std::cout << std::endl;
  std::cout << "Finished loop";;
  std::cout << std::endl;
  rootFile->Close();

}

void LoopAndFillBDTG(std::string tag,
                     const PlotUtils::MacroUtil& util,
                     std::map<std::string, std::vector<CVUniverse*> > error_bands,
                     std::vector<CCQENu::VariableFromConfig*>& variables,
                     std::vector<CCQENu::Variable2DFromConfig*>& variables2D,
                     EDataMCTruth data_mc_truth,
                     PlotUtils::Cutter<CVUniverse>& selection,
                     PlotUtils::Model<CVUniverse,PlotUtils::detail::empty>& model, 
                     PlotUtils::weight_MCreScale mcRescale,
                     bool closure=false, bool mc_reco_to_csv=false) {

  // Prepare loop
  MinervaUniverse::SetTruth(false);
  int nentries = -1;

  // get ready for weights by finding cv universe pointer

  assert(!error_bands["cv"].empty() && "\"cv\" error band is empty!  Can't set Model weight.");
  auto& cvUniv = error_bands["cv"].front();
  // make a dummy event - may need to make fancier
  PlotUtils::detail::empty event;

  if ( variables.size() < 1) {
    std::cout << " no variables to fill " << std::endl;
    return;  // don't bother if there are no variables.
  }

  if (data_mc_truth == kData){
    nentries = util.GetDataEntries();
  }
  else if (data_mc_truth == kMC){
    nentries = util.GetMCEntries();
  }
  else{
    nentries = util.GetTruthEntries() ;
    MinervaUniverse::SetTruth(true);
  }
  
  // xgboost
  /*TMVA::Experimental::RBDT<> my_1track_bdt("my_1track_BDT","/home/sean/MinervaExpt/CCQENu/make_hists/smg/tmva_1track_Training.root");
  TMVA::Experimental::RBDT<> my_2track_bdt("my_2track_BDT","/home/sean/MinervaExpt/CCQENu/make_hists/smg/tmva_2track_Training.root");
  TMVA::Experimental::RBDT<> my_3ptrack_bdt("my_3ptrack_BDT","/home/sean/MinervaExpt/CCQENu/make_hists/smg/tmva_3ptrack_Training.root");*/
  
  // TMVA only
	TMVA::Experimental::RReader model_1track(expandEnv("${CCQEMAT}/TMVA/TMVAMulticlass_1track_BDTG.weights.xml"));
  TMVA::Experimental::RReader model_2track(expandEnv("${CCQEMAT}/TMVA/TMVAMulticlass_2track_BDTG.weights.xml"));
  TMVA::Experimental::RReader model_3ptrack(expandEnv("${CCQEMAT}/TMVA/TMVAMulticlass_3ptrack_BDTG.weights.xml"));

  unsigned int loc = tag.find("___")+3;
  std::string cat(tag,loc,string::npos);
  std::string sample(tag,0,loc-3);
  std::cout << sample << " category " << cat << std::endl;
  std::cout << " starting loop " << data_mc_truth << " " << nentries << std::endl;

	// Begin entries loop
  for (int i = 0; i < nentries; i++) {
    		
		ProgressBar(nentries,i,true,data_mc_truth,prescale);
		
    cvUniv->SetEntry(i);
    //atree->GetEntry(i);

    if (data_mc_truth != kData) model.SetEntry(*cvUniv, event);


    const double cvWeight = (data_mc_truth == kData ||  closure ) ? 1. : model.GetWeight(*cvUniv,event);  // detail may be used for more complex things
    // TODO: Is this scaled cvWeight necessary?
    // const double cvWeightScaled = (data_mc_truth kData) ? 1. : cvWeight*mcRescale.GetScale(q2qe, "cv");
    
    // Loop bands and universes
    for (auto band : error_bands) {
      std::vector<CVUniverse*> error_band_universes = band.second;
      //  HMS replace with iuniv to access weights more easily
      //  HMS for (auto universe : error_band_universes) {
      std::string uni_name = (band.second)[0]->ShortName();
      for (int iuniv=0; iuniv < error_band_universes.size(); iuniv++){

        auto universe = error_band_universes[iuniv];
        universe->SetEntry(i);

        // Process this event/universe
        //double weight = 1;
        //if (universe->ShortName() == "cv" ) weight = data_mc_truth == kData ? 1. : universe->GetWeight();

        // probably want to move this later on inside the loop
        const double weight = (data_mc_truth == kData || closure) ? 1. : model.GetWeight(*universe, event); //Only calculate the per-universe weight for events that will actually use it.
        //double weight = (data_mc_truth == kData || closure) ? 1. : model.GetWeight(*universe, event);
        //PlotUtils::detail::empty event;
        
        std::vector<float> response_vec;
        //std::vector<float> xgboost_response_vec;
        
        if (data_mc_truth != kTruth) {
        
		      float multiplicity = universe->GetMultiplicity();
					float proton_score1_0 = universe->GetPrimaryProtonScore1();
					float proton_score1_1 = universe->GetProtonScore1_1();
					float proton_score1_2 = universe->GetProtonScore1_2();
					float proton_track_vtx_gap_0 = universe->GetPrimaryProtonTrackVtxGap();
					float proton_track_vtx_gap_1 = universe->GetSecProtonTrackVtxGap_1();
					float proton_track_vtx_gap_2 = universe->GetSecProtonTrackVtxGap_2();
					float proton_T_from_dEdX_0 = universe->GetPrimaryProtonTfromdEdx();
					float proton_T_from_dEdX_1 = universe->GetSecProtonTfromdEdx_1();
					float proton_T_from_dEdX_2 = universe->GetSecProtonTfromdEdx_2();
					float proton_clusters_0 = universe->GetNumClustsPrimaryProtonEnd();
					float proton_clusters_1 = universe->GetNumClustsSecProtonEnd_1();
					float proton_clusters_2 = universe->GetNumClustsSecProtonEnd_2();
					float proton_fraction_vis_energy_in_cone_0 = universe->GetPrimaryProtonFractionVisEnergyInCone();
					float proton_fraction_vis_energy_in_cone_1 = universe->GetSecProtonFractionVisEnergyInCone_1();
					float proton_fraction_vis_energy_in_cone_2 = universe->GetSecProtonFractionVisEnergyInCone_2();
					float sec_proton_cand_count = universe->GetSecondaryProtonCandidateCount1();
					float muon_to_primary_proton_angle = universe->GetMuonToPrimaryProtonAngle();
					float blob_count = universe->GetNBlobs();
					float improved_michel_count = universe->GetImprovedNMichel();
					float recoil = universe->GetRecoilEnergyGeV();
					float improved_michel_1_views = universe->GetImprovedMichel_0_Views();
					float improved_michel_2_views = universe->GetImprovedMichel_1_Views();
					float improved_michel_3_views = universe->GetImprovedMichel_2_Views();
					float improved_michel_sum_views = universe->GetImprovedMichel_Sum_Views();
					
					std::vector<float> input_vars;
					//std::vector<float> xgboost_input_vars;
					
					input_vars.emplace_back(multiplicity);
					//xgboost_input_vars.emplace_back(multiplicity);
					if (proton_score1_0 >= 0) {
						if (sec_proton_cand_count == 0) {
						
							input_vars.emplace_back(proton_score1_0);
							input_vars.emplace_back(proton_track_vtx_gap_0);
							input_vars.emplace_back(proton_T_from_dEdX_0);
							input_vars.emplace_back(proton_clusters_0);
							input_vars.emplace_back(proton_fraction_vis_energy_in_cone_0);
							input_vars.emplace_back(blob_count);
							input_vars.emplace_back(improved_michel_count);
							input_vars.emplace_back(recoil);
							input_vars.emplace_back(improved_michel_sum_views);
							input_vars.emplace_back(muon_to_primary_proton_angle);
							
							/*xgboost_input_vars.emplace_back(proton_score1_0);
							xgboost_input_vars.emplace_back(proton_track_vtx_gap_0);
							xgboost_input_vars.emplace_back(proton_T_from_dEdX_0);
							xgboost_input_vars.emplace_back(proton_clusters_0);
							xgboost_input_vars.emplace_back(proton_fraction_vis_energy_in_cone_0);
							xgboost_input_vars.emplace_back(blob_count);
							xgboost_input_vars.emplace_back(improved_michel_1_views);
							xgboost_input_vars.emplace_back(improved_michel_2_views);*/
							
							if (input_vars.size() == model_2track.GetVariableNames().size()) {
								response_vec = model_2track.Compute(input_vars);
								//xgboost_response_vec = my_2track_bdt.Compute(xgboost_input_vars);
							}
							else {
								response_vec = {0,0,0,0,0};
								std::cout << "WARNING: INPUT VECTOR SIZE DOES NOT MATCH 2 TRACK MODEL EXPECTATION" << std::endl;
							}
						}
						else {
						
							input_vars.emplace_back(proton_score1_0);
							input_vars.emplace_back(proton_score1_1);
							input_vars.emplace_back(proton_track_vtx_gap_0);
							input_vars.emplace_back(proton_track_vtx_gap_1);
							input_vars.emplace_back(proton_T_from_dEdX_0);
							input_vars.emplace_back(proton_clusters_0);
							input_vars.emplace_back(proton_clusters_1);
							input_vars.emplace_back(proton_fraction_vis_energy_in_cone_0);
							input_vars.emplace_back(proton_fraction_vis_energy_in_cone_1);
							input_vars.emplace_back(sec_proton_cand_count);
							input_vars.emplace_back(blob_count);
							input_vars.emplace_back(improved_michel_count);
							input_vars.emplace_back(recoil);
							input_vars.emplace_back(improved_michel_sum_views);
							input_vars.emplace_back(muon_to_primary_proton_angle);
							
							/*xgboost_input_vars.emplace_back(proton_score1_0);
							xgboost_input_vars.emplace_back(proton_score1_1);
							xgboost_input_vars.emplace_back(proton_track_vtx_gap_0);
							xgboost_input_vars.emplace_back(proton_track_vtx_gap_1);
							xgboost_input_vars.emplace_back(proton_T_from_dEdX_0);
							xgboost_input_vars.emplace_back(proton_T_from_dEdX_1);
							xgboost_input_vars.emplace_back(proton_clusters_0);
							xgboost_input_vars.emplace_back(proton_clusters_1);
							xgboost_input_vars.emplace_back(proton_fraction_vis_energy_in_cone_0);
							xgboost_input_vars.emplace_back(proton_fraction_vis_energy_in_cone_1);
							xgboost_input_vars.emplace_back(sec_proton_cand_count);
							xgboost_input_vars.emplace_back(blob_count);
							xgboost_input_vars.emplace_back(improved_michel_count);
							xgboost_input_vars.emplace_back(recoil);
							xgboost_input_vars.emplace_back(improved_michel_1_views);
							xgboost_input_vars.emplace_back(improved_michel_2_views);*/
							
							if (input_vars.size() == model_3ptrack.GetVariableNames().size()) {
								response_vec = model_3ptrack.Compute(input_vars);
								//xgboost_response_vec = my_3ptrack_bdt.Compute(xgboost_input_vars);
							}
							else {
								response_vec = {0,0,0,0,0};
								std::cout << "WARNING: INPUT VECTOR SIZE DOES NOT MATCH 3+ TRACK MODEL EXPECTATION" << std::endl;
							}
						}
					}
					else {
					
						input_vars.emplace_back(blob_count);
						input_vars.emplace_back(improved_michel_count);
						input_vars.emplace_back(recoil);
						input_vars.emplace_back(improved_michel_sum_views);
						
						/*xgboost_input_vars.emplace_back(blob_count);
						xgboost_input_vars.emplace_back(improved_michel_count);
						xgboost_input_vars.emplace_back(recoil);
						xgboost_input_vars.emplace_back(improved_michel_1_views);
						xgboost_input_vars.emplace_back(improved_michel_2_views);*/
						
						if (input_vars.size() == model_1track.GetVariableNames().size()) {
								response_vec = model_1track.Compute(input_vars);
								//xgboost_response_vec = my_1track_bdt.Compute(xgboost_input_vars);
						}
						else {
							response_vec = {0,0,0,0,0};
							std::cout << "WARNING: INPUT VECTOR SIZE DOES NOT MATCH 1 TRACK MODEL EXPECTATION" << std::endl;
						}
					}
				}
				else {
					if (universe->GetTruthIsCCQELike()) { 
						response_vec = {1,0,0,0,0}; 
						//xgboost_response_vec = {0,0,0,0,1};
					}
					else if (universe->GetTruthHasSingleChargedPion()) { 
						response_vec = {0,1,0,0,0}; 
						//xgboost_response_vec = {0,0,0,1,0};
					}
					else if (universe->GetTruthHasSingleNeutralPion()) { 
						response_vec = {0,0,1,0,0}; 
						//xgboost_response_vec = {0,0,1,0,0};
					}
					else if (universe->GetTruthHasMultiPion()) { 
						response_vec = {0,0,0,1,0}; 
						//xgboost_response_vec = {0,1,0,0,0};
					}
					else { 
						response_vec = {0,0,0,0,1}; 
						//xgboost_response_vec = {1,0,0,0,0};
					}
				}
				
				CVUniverse::SetVectorResponse(response_vec);
				//CVUniverse::SetXgboostVectorResponse(xgboost_response_vec);

        //=========================================
        // Fill
        //=========================================
        
        //weight = weight*xgboost_response_vec[4];
        
        if(data_mc_truth == kMC){
#ifdef CLOSUREDETAIL
          if(closure && universe->ShortName() == "cv" && selection.isMCSelected(*universe, event, weight).all()){
            std::cout  << universe->GetRun() << " " << universe->GetSubRun() << " " << universe->GetGate() << " " << universe->GetPmuGeV() << " " << weight << " " << selection.isDataSelected(*universe, event).all() << " " << selection.isMCSelected(*universe, event, weight).all() << " " << tag  << selection.isSignal(*universe)  << " " << universe->ShortName() <<  std::endl;
              universe->Print();
          }
#endif
					if(selection.isMCSelected(*universe, event, weight).all()
						&& selection.isSignal(*universe)) {

						//double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
						const double q2qe = universe->GetQ2QEGeV();
						double scale = 1.0;
						if (!closure) scale = mcRescale.GetScale(cat, q2qe, uni_name, iuniv); //Only calculate the per-universe weight for events that will actually use it.

						FillMC(tag, universe, weight, variables, variables2D, scale);
						FillResponse(tag,universe,weight,variables,variables2D, scale);
						FillResolution(tag,universe,weight,variables,variables2D, scale);
		      }
				}
        else if (data_mc_truth == kTruth){

          if(selection.isEfficiencyDenom(*universe, weight)){
            const double q2qe = universe->GetTrueQ2QEGeV();
            double scale = 1.0;
            if (!closure) scale =mcRescale.GetScale(cat, q2qe, uni_name, iuniv); //Only calculate the per-universe weight for events that will actually use it.
            if (closure) scale = 1.0;
            FillSignalTruth(tag, universe, weight, variables, variables2D, scale);
          }
        }
        else{ //kData
#ifdef CLOSUREDETAIL
          if (closure && selection.isDataSelected(*universe, event).all() ){
            std::cout  << universe->GetRun() << " " << universe->GetSubRun() << " " << universe->GetGate() << " " << universe->GetPmuGeV() << " " << weight << " " << selection.isDataSelected(*universe, event).all() << " " << selection.isMCSelected(*universe, event, weight).all()  << "  " << tag  << "1" << " " << universe->ShortName() <<  std::endl;
          }
#endif
          if(selection.isDataSelected(*universe, event).all()) {
            FillData(tag, universe, variables, variables2D);
            
          }
        }

        CVUniverse::ResetVectorResponse();
        //CVUniverse::ResetXgboostVectorResponse();


      } // End universes
    } // End error bands
    
    if(data_mc_truth != kData) i+= prescale-1;
    
  } // End entries loop

}

void LoopAndFillEventSelection2(std::string tag,
                               const PlotUtils::MacroUtil& util,
                               std::map<std::string, std::vector<CVUniverse*> > error_bands,
                               std::vector<CCQENu::VariableFromConfig*>& variables,
                               std::vector<CCQENu::Variable2DFromConfig*>& variables2D,
                               EDataMCTruth data_mc_truth,
                               PlotUtils::Cutter<CVUniverse>& selection, 
                               PlotUtils::Model<CVUniverse,PlotUtils::detail::empty>& model, 
                               PlotUtils::weight_MCreScale mcRescale,
                               bool closure=false, bool mc_reco_to_csv=false) {

  // Prepare loop
  MinervaUniverse::SetTruth(false);
  int nentries = -1;

  // get ready for weights by finding cv universe pointer

  assert(!error_bands["cv"].empty() && "\"cv\" error band is empty!  Can't set Model weight.");
  auto& cvUniv = error_bands["cv"].front();
  // make a dummy event - may need to make fancier
  PlotUtils::detail::empty event;

  if ( variables.size() < 1) {
    std::cout << " no variables to fill " << std::endl;
    return;  // don't bother if there are no variables.
  }

  if (data_mc_truth == kData){
    nentries = util.GetDataEntries();
  }
  else if (data_mc_truth == kMC){
    nentries = util.GetMCEntries();
  }
  else{
    nentries = util.GetTruthEntries() ;
    MinervaUniverse::SetTruth(true);
  }


  unsigned int loc = tag.find("___")+3;
  std::string cat(tag,loc,string::npos);
  std::string sample(tag,0,loc-3);
  std::cout << sample << " category " << cat << std::endl;
  std::cout << " starting loop " << data_mc_truth << " " << nentries << std::endl;

	// Begin entries loop
  for (int i = 0; i < nentries; i++) {
    		
		ProgressBar(nentries,i,false,data_mc_truth,prescale);
		
    cvUniv->SetEntry(i);
    //atree->GetEntry(i);

    if (data_mc_truth != kData) {
    	model.SetEntry(*cvUniv, event);
    }


    const double cvWeight = (data_mc_truth == kData ||  closure ) ? 1. : model.GetWeight(*cvUniv,event);  // detail may be used for more complex things
    // TODO: Is this scaled cvWeight necessary?
    // const double cvWeightScaled = (data_mc_truth kData) ? 1. : cvWeight*mcRescale.GetScale(q2qe, "cv");
    
    // Loop bands and universes
    for (auto band : error_bands) {
      std::vector<CVUniverse*> error_band_universes = band.second;
      //  HMS replace with iuniv to access weights more easily
      //  HMS for (auto universe : error_band_universes) {
      std::string uni_name = (band.second)[0]->ShortName();
      for (int iuniv=0; iuniv < error_band_universes.size(); iuniv++){

        auto universe = error_band_universes[iuniv];
        universe->SetEntry(i);

        // Process this event/universe
        //double weight = 1;
        //if (universe->ShortName() == "cv" ) weight = data_mc_truth == kData ? 1. : universe->GetWeight();

        // probably want to move this later on inside the loop
        const double weight = (data_mc_truth == kData || closure) ? 1. : model.GetWeight(*universe, event); //Only calculate the per-universe weight for events that will actually use it.
        //PlotUtils::detail::empty event;
        
        if (data_mc_truth != kData && !CVUniverse::AreSignalTruthsSet()) {
        	universe->SetFSParticlePDGCounts();
        	universe->SetSignalTruths();
        }
        if (data_mc_truth != kData && !CVUniverse::AreSignalTruthsSet_old()) {
        	universe->SetSignalTruths_old();
        }

        //=========================================
        // Fill
        //=========================================
        
        if(data_mc_truth == kMC){
#ifdef CLOSUREDETAIL
          if(closure && universe->ShortName() == "cv" && selection.isMCSelected(*universe, event, weight).all()){
            std::cout  << universe->GetRun() << " " << universe->GetSubRun() << " " << universe->GetGate() << " " << universe->GetPmuGeV() << " " << weight << " " << selection.isDataSelected(*universe, event).all() << " " << selection.isMCSelected(*universe, event, weight).all() << " " << tag  << selection.isSignal(*universe)  << " " << cvUniv->ShortName() <<  std::endl;
              universe->Print();
          }
#endif
					if(selection.isMCSelected(*universe, event, weight).all() && selection.isSignal(*universe)) {

						//double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
						const double q2qe = universe->GetQ2QEGeV();
						double scale = 1.0;
						if (!closure) scale = mcRescale.GetScale(cat, q2qe, uni_name, iuniv); //Only calculate the per-universe weight for events that will actually use it.

						FillMC(tag, universe, weight, variables, variables2D, scale);
						FillResponse(tag,universe,weight,variables,variables2D, scale);
						FillResolution(tag,universe,weight,variables,variables2D, scale);
		      }
				}
        else if (data_mc_truth == kTruth){

          if(selection.isEfficiencyDenom(*universe, weight)){
            const double q2qe = universe->GetTrueQ2QEGeV();
            double scale = 1.0;
            if (!closure) scale =mcRescale.GetScale(cat, q2qe, uni_name, iuniv); //Only calculate the per-universe weight for events that will actually use it.
            if (closure) scale = 1.0;
            FillSignalTruth(tag, universe, weight, variables, variables2D, scale);
          }
        }
        else{ //kData
#ifdef CLOSUREDETAIL
          if (closure && selection.isDataSelected(*universe, event).all() ){
            std::cout  << universe->GetRun() << " " << universe->GetSubRun() << " " << universe->GetGate() << " " << universe->GetPmuGeV() << " " << weight << " " << selection.isDataSelected(*universe, event).all() << " " << selection.isMCSelected(*universe, event, weight).all()  << "  " << tag  << "1" << " " << universe->ShortName() <<  std::endl;
          }
#endif
          if(selection.isDataSelected(*universe, event).all()) {
            FillData(tag, universe, variables, variables2D);
            
          }
        }

      } // End universes
    } // End error bands
    
    if (data_mc_truth != kData) {
    	i+= prescale-1;
    	CVUniverse::ResetSignalTruths();
    	CVUniverse::ResetFSParticlePDGCounts();
    }
    
  } // End entries loop

}
                            

#endif //__CINT__
