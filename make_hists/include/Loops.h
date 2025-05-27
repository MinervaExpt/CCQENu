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
#include "TMVA/RBDT.hxx"
#include "include/TMVAUtils.h"
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
                               bool closure=false,
                               bool use_prog_bar=false) {

	// Prepare loop
	MinervaUniverse::SetTruth(false);
	int nentries = -1;
	CVFunctions<CVUniverse> fund;

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
		nentries = util.GetTruthEntries();
		MinervaUniverse::SetTruth(true);
	}

	unsigned int loc = tag.find("___")+3;
	std::string cat(tag,loc,string::npos);
	std::string sample(tag,0,loc-3);

	std::map<std::string,RReader> *tmva_models = CVUniverse::GetPointerToTMVAModels();
	std::vector<std::string> var_names = (*tmva_models)[sample].GetVariableExpressions();
	int tmva_variable_size = (*tmva_models)[sample].GetVariableNames().size();
	std::string sample_category = CVUniverse::GetSampleCategory(sample);
	
	std::cout << " number of error bands: " << error_bands.size() << std::endl;
	std::cout << " " << sample << " category " << cat << std::endl;
	std::cout << " starting loop " << data_mc_truth << " " << nentries << std::endl;
	const clock_t begin_time = clock();
  
	std::cout << std::endl;
	for (auto var : var_names) {
		std::cout << "   " << var << std::endl;
	}
	if (data_mc_truth != kData) {
		std::cout << "\nLooping over error bands:\n";
		for (auto band : error_bands) {
			std::cout << "   " << (band.second)[0]->ShortName() << std::endl;
		}
		std::cout << std::endl;
	}

	int counter = 0;

	// Begin entries loop
	for (int i = 0; i < nentries; i++) {
    		
		ProgressBar(nentries,i,use_prog_bar,data_mc_truth,prescale);
		
		cvUniv->SetEntry(i);
		//atree->GetEntry(i);

		if (data_mc_truth != kData) model.SetEntry(*cvUniv, event);

		if (data_mc_truth == kMC || data_mc_truth == kData){
			if (!cvUniv->FastFilter()) continue;
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

				double aux_weight = 1.;

				if(tmva_variable_size > 0 && data_mc_truth != kTruth){
					/*v1 = universe->GetMultiplicity();
					v2 = universe->GetProtonScore1_0();
					v3 = universe->GetPrimaryProtonTrackVtxGap();
					v4 = universe->GetMuonToPrimaryProtonAngle();
					v5 = universe->ProtonRatioTdEdX2TrackLength_0();
					v6 = universe->GetPrimaryProtonFractionVisEnergyInCone();
					v7 = universe->GetNumClustsPrimaryProtonEnd();
					v8 = universe->GetNBlobs();
					v9 = universe->GetImprovedNMichel();
					v10 = universe->GetRecoilEnergyGeV();
					v11 = universe->GetImprovedMichel_Sum_Views();
					std::vector<float> var_values = {v1,v2,v3,v4,v5,v6,v7,v8,v9,v10,v11};*/
					std::vector<float> var_values = fund.GetVectorOfValues(universe,var_names);
					CVUniverse::ComputeTMVAResponse(sample,var_values);
				}
				//if(sample_category.size() > 0){
				//	double tmva_weight = CVUniverse::GetTMVAClassResponse(sample_category);
				//	aux_weight = aux_weight*tmva_weight;
				//}
				
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
					if(selection.isMCSelected(*universe, event, weight).all() && selection.isSignal(*universe)) {
						//double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
						const double q2qe = universe->GetQ2QEGeV();
						double scale = 1.0;
						if (!closure) scale = mcRescale.GetScale(cat, q2qe, uni_name, iuniv); //Only calculate the per-universe weight for events that will actually use it.
						
						counter++;
						if (counter <= 20) {
							std::cout << sample << " " << sample_category << " " << cat << " " << aux_weight << std::endl;
						}
						
						FillMC(tag, universe, weight, variables, variables2D, scale);
						FillResponse(tag, universe, weight, variables, variables2D, scale);
						FillResolution(tag, universe, weight, variables, variables2D, scale);
					
					}
				}
				else if (data_mc_truth == kTruth){

					if(selection.isEfficiencyDenom(*universe, weight)){
						const double q2qe = universe->GetTrueQ2QEGeV();
						double scale = 1.0;
						if (!closure) scale = mcRescale.GetScale(cat, q2qe, uni_name, iuniv); //Only calculate the per-universe weight for events that will actually use it.
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
          
						FillData(tag, universe, variables, variables2D, aux_weight);
            
					}
				}
        
				CVUniverse::ResetTMVAResponse();
        
			} // End universes
		} // End error bands
    
		if(data_mc_truth != kData) i+= prescale-1;
    
	} // End entries loop
	std::cout << "Elapsed time: " << float( clock() - begin_time )/1000000 << " s" << std::endl;

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

	// CSV setup
  std::string csvFileName = "CSV_"+outNameBase+".csv";
  std::cout << "Making CSV file " << csvFileName << std::endl;
	std::ofstream csvFile;
  csvFile.open(csvFileName);
  csvFile << "Entry";
  for (auto v : variables) {
		csvFile << ";" << v->GetName();
  }
	csvFile << ";Truth;Interaction;mc_intType;qelikeBDTG;1chargedpionBDTG;1neutralpionBDTG;multipionBDTG;otherBDTG;model;weight;ProngTrajID;nERParts;ERIDs;nFSPart;FSPDGs;FSPartEs;Arachne" << std::endl;
	std::vector<std::string> interaction = {"None","QE","RES","DIS","COHPI","AMNUGAMMA","IMD","NUEEL","2P2H","NA","Unknown"};
	
	RReader model_1track(expandEnv("${CCQEMAT}/TMVA/TMVAMulticlass_1track_BDTG.weights.xml"));
  RReader model_2track(expandEnv("${CCQEMAT}/TMVA/TMVAMulticlass_2track_BDTG.weights.xml"));
  RReader model_3ptrack(expandEnv("${CCQEMAT}/TMVA/TMVAMulticlass_3ptrack_BDTG.weights.xml"));
	
	// Begin loop over entries
	std::cout << std::endl << "Beginning loop over " << nentries << " entries\n" << std::endl;
	for (int i = 0; i < nentries; i++) {
	
		std::string model_name;
	
		ProgressBar(nentries,i,use_prog_bar,kMC,1);
		
		cvUniv->SetEntry(i);
		
		model.SetEntry(*cvUniv, event);
		
		if (!cvUniv->FastFilter()) continue;
		
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
					float proton_ratio_T_to_tracklength_0 = universe->ProtonRatioTdEdX2TrackLength_0();
					float proton_ratio_T_to_tracklength_1 = universe->ProtonRatioTdEdX2TrackLength_1();
					float proton_clusters_0 = universe->GetNumClustsPrimaryProtonEnd();
					float proton_clusters_1 = universe->GetNumClustsSecProtonEnd_1();
					float proton_clusters_2 = universe->GetNumClustsSecProtonEnd_2();
					float proton_fraction_vis_energy_in_cone_0 = universe->GetPrimaryProtonFractionVisEnergyInCone();
					float proton_fraction_vis_energy_in_cone_1 = universe->GetSecProtonFractionVisEnergyInCone_1();
					float proton_fraction_vis_energy_in_cone_2 = universe->GetSecProtonFractionVisEnergyInCone_2();
					float proton_cand_count = universe->GetNumberOfProtonCandidates();
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
						if (proton_cand_count == 1) {
							input_vars.emplace_back(proton_score1_0);
							input_vars.emplace_back(proton_track_vtx_gap_0);
							input_vars.emplace_back(proton_ratio_T_to_tracklength_0);
							input_vars.emplace_back(proton_fraction_vis_energy_in_cone_0);
							input_vars.emplace_back(proton_clusters_0);
							input_vars.emplace_back(blob_count);
							input_vars.emplace_back(improved_michel_count);
							input_vars.emplace_back(recoil);
							input_vars.emplace_back(improved_michel_sum_views);
							//input_vars.emplace_back(muon_to_primary_proton_angle);
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
							input_vars.emplace_back(proton_ratio_T_to_tracklength_0);
							input_vars.emplace_back(proton_ratio_T_to_tracklength_1);
							input_vars.emplace_back(proton_clusters_0);
							input_vars.emplace_back(proton_clusters_1);
							input_vars.emplace_back(proton_fraction_vis_energy_in_cone_0);
							input_vars.emplace_back(proton_fraction_vis_energy_in_cone_1);
							input_vars.emplace_back(proton_cand_count);
							input_vars.emplace_back(blob_count);
							input_vars.emplace_back(improved_michel_count);
							input_vars.emplace_back(recoil);
							input_vars.emplace_back(improved_michel_sum_views);
							//input_vars.emplace_back(muon_to_primary_proton_angle);
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
							csvFile << ";" << weight;
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
	Int_t MCIntType;
	std::cout << std::endl << "  entry";
	std::cout << std::endl << "  MCIntType";
	
	Double_t wgt;
	Double_t Q2QE;
	Double_t PperpMuGeV;
	Double_t PparMuGeV;
	Double_t RecoilEnergyGeV;
	Int_t Multiplicity;
	std::cout << std::endl << "  weight";
	std::cout << std::endl << "  Q2QE";
	std::cout << std::endl << "  PperpMuGeV";
	std::cout << std::endl << "  PparMuGeV";
	std::cout << std::endl << "  RecoilEnergyGeV";
	std::cout << std::endl << "  Multiplicity";
	
	Int_t NumberOfProtonCandidates;
	std::cout << std::endl << "  NumberOfProtonCandidates";
	
	Double_t PrimaryProtonScore1;
	Double_t SecProtonScore1_1;
	Double_t SecProtonScore1_2;
	Double_t SecProtonScore1_3;
	std::cout << std::endl << "  PrimaryProtonScore1";
	std::cout << std::endl << "  SecProtonScore1_1";
	std::cout << std::endl << "  SecProtonScore1_2";
	std::cout << std::endl << "  SecProtonScore1_3";
	
	Double_t PrimaryProtonTfromdEdx;
	Double_t SecProtonTfromdEdx_1;
	Double_t SecProtonTfromdEdx_2;
	Double_t SecProtonTfromdEdx_3;
	std::cout << std::endl << "  PrimaryProtonTfromdEdx";
	std::cout << std::endl << "  SecProtonTfromdEdx_1";
	std::cout << std::endl << "  SecProtonTfromdEdx_2";
	std::cout << std::endl << "  SecProtonTfromdEdx_3";
	
	Double_t ProtonRatioTdEdX2TrackLength_0;
	Double_t ProtonRatioTdEdX2TrackLength_1;
	Double_t ProtonRatioTdEdX2TrackLength_2;
	Double_t ProtonRatioTdEdX2TrackLength_3;
	std::cout << std::endl << "  ProtonRatioTdEdX2TrackLength_0";
	//std::cout << std::endl << "  ProtonRatioTdEdX2TrackLength_1";
	//std::cout << std::endl << "  ProtonRatioTdEdX2TrackLength_2";
	//std::cout << std::endl << "  ProtonRatioTdEdX2TrackLength_3";
	
	Double_t PrimaryProtonTrackVtxGap; 
	Double_t SecProtonTrackVtxGap_1;
	Double_t SecProtonTrackVtxGap_2;
	Double_t SecProtonTrackVtxGap_3;
	std::cout << std::endl << "  PrimaryProtonTrackVtxGap";
	//std::cout << std::endl << "  SecProtonTrackVtxGap_1";
	//std::cout << std::endl << "  SecProtonTrackVtxGap_2";
	//std::cout << std::endl << "  SecProtonTrackVtxGap_3";
	
	Double_t PrimaryProtonFractionVisEnergyInCone;
	Double_t SecProtonFractionVisEnergyInCone_1;
	Double_t SecProtonFractionVisEnergyInCone_2;
	Double_t SecProtonFractionVisEnergyInCone_3;
	std::cout << std::endl << "  PrimaryProtonFractionVisEnergyInCone";
	std::cout << std::endl << "  SecProtonFractionVisEnergyInCone_1";
	std::cout << std::endl << "  SecProtonFractionVisEnergyInCone_2";
	std::cout << std::endl << "  SecProtonFractionVisEnergyInCone_3";
	
	Int_t NumClustsPrimaryProtonEnd;
	Int_t NumClustsSecProtonEnd_1;
	Int_t NumClustsSecProtonEnd_2;
	Int_t NumClustsSecProtonEnd_3;
	std::cout << std::endl << "  NumClustsPrimaryProtonEnd";
	std::cout << std::endl << "  NumClustsSecProtonEnd_1";
	std::cout << std::endl << "  NumClustsSecProtonEnd_2";
	std::cout << std::endl << "  NumClustsSecProtonEnd_3";

	Double_t MuonToPrimaryProtonAngle;
	std::cout << std::endl << "  MuonToPrimaryProtonAngle";

	Int_t NBlobs;
	std::cout << std::endl << "  NBlobs";
	
	Int_t ImprovedNMichel;
	Int_t ImprovedMichel_0_Views;
	Int_t ImprovedMichel_1_Views;
	Int_t ImprovedMichel_2_Views;
	Int_t ImprovedMichel_Sum_Views;
	std::cout << std::endl << "  ImprovedNMichel";
	std::cout << std::endl << "  ImprovedMichel_0_Views";
	std::cout << std::endl << "  ImprovedMichel_1_Views";
	std::cout << std::endl << "  ImprovedMichel_2_Views";
	std::cout << std::endl << "  ImprovedMichel_Sum_Views";
	
	// Trees
	std::map<std::string,TTree*> ttrees;
	std::cout << "\n\nMaking following trees for " << rootFileName << ":" << std::endl;
	
	for (auto tname:recotags) {
		ttrees[tname] = tree_mcreco->CloneTree(0);
		ttrees[tname]->SetName(tname.c_str());
		std::cout << "  " << tname << std::endl;
		
		ttrees[tname]->Branch("entry",&entry,"entry/I");
		ttrees[tname]->Branch("MCIntType",&MCIntType,"MCIntType/I");
		
		ttrees[tname]->Branch("weight",&wgt,"weight/D");
		ttrees[tname]->Branch("Q2QE",&Q2QE,"Q2QE/D");
		ttrees[tname]->Branch("PperpMuGeV",&PperpMuGeV,"PperpMuGeV/D");
		ttrees[tname]->Branch("PparMuGeV",&PparMuGeV,"PparMuGeV/D");
		ttrees[tname]->Branch("RecoilEnergyGeV",&RecoilEnergyGeV,"RecoilEnergyGeV/D");
		ttrees[tname]->Branch("Multiplicity",&Multiplicity,"Multiplicity/I");
		
		ttrees[tname]->Branch("NumberOfProtonCandidates",&NumberOfProtonCandidates,"NumberOfProtonCandidates/I");
		
		ttrees[tname]->Branch("PrimaryProtonScore1",&PrimaryProtonScore1,"PrimaryProtonScore1/D");
		ttrees[tname]->Branch("SecProtonScore1_1",&SecProtonScore1_1,"SecProtonScore1_1/D");
		ttrees[tname]->Branch("SecProtonScore1_2",&SecProtonScore1_2,"SecProtonScore1_2/D");
		ttrees[tname]->Branch("SecProtonScore1_3",&SecProtonScore1_3,"SecProtonScore1_3/D");
		
		ttrees[tname]->Branch("PrimaryProtonTfromdEdx",&PrimaryProtonTfromdEdx,"PrimaryProtonTfromdEdx/D");
		ttrees[tname]->Branch("SecProtonTfromdEdx_1",&SecProtonTfromdEdx_1,"SecProtonTfromdEdx_1/D");
		ttrees[tname]->Branch("SecProtonTfromdEdx_2",&SecProtonTfromdEdx_2,"SecProtonTfromdEdx_2/D");
		ttrees[tname]->Branch("SecProtonTfromdEdx_3",&SecProtonTfromdEdx_3,"SecProtonTfromdEdx_3/D");
		
		ttrees[tname]->Branch("ProtonRatioTdEdX2TrackLength_0",&ProtonRatioTdEdX2TrackLength_0,"ProtonRatioTdEdX2TrackLength_0/D");
		//ttrees[tname]->Branch("ProtonRatioTdEdX2TrackLength_1",&ProtonRatioTdEdX2TrackLength_1,"ProtonRatioTdEdX2TrackLength_1/D");
		//ttrees[tname]->Branch("ProtonRatioTdEdX2TrackLength_2",&ProtonRatioTdEdX2TrackLength_2,"ProtonRatioTdEdX2TrackLength_2/D");
		//ttrees[tname]->Branch("ProtonRatioTdEdX2TrackLength_3",&ProtonRatioTdEdX2TrackLength_3,"ProtonRatioTdEdX2TrackLength_3/D");
		
		ttrees[tname]->Branch("PrimaryProtonTrackVtxGap",&PrimaryProtonTrackVtxGap,"PrimaryProtonTrackVtxGap/D");
		//ttrees[tname]->Branch("SecProtonTrackVtxGap_1",&SecProtonTrackVtxGap_1,"SecProtonTrackVtxGap_1/D");
		//ttrees[tname]->Branch("SecProtonTrackVtxGap_2",&SecProtonTrackVtxGap_2,"SecProtonTrackVtxGap_2/D");
		//ttrees[tname]->Branch("SecProtonTrackVtxGap_3",&SecProtonTrackVtxGap_3,"SecProtonTrackVtxGap_3/D");
		
		ttrees[tname]->Branch("PrimaryProtonFractionVisEnergyInCone",
		                      &PrimaryProtonFractionVisEnergyInCone,"PrimaryProtonFractionVisEnergyInCone/D");
		ttrees[tname]->Branch("SecProtonFractionVisEnergyInCone_1",
		                      &SecProtonFractionVisEnergyInCone_1,"SecProtonFractionVisEnergyInCone_1/D");
		ttrees[tname]->Branch("SecProtonFractionVisEnergyInCone_2",
		                      &SecProtonFractionVisEnergyInCone_2,"SecProtonFractionVisEnergyInCone_2/D");
		ttrees[tname]->Branch("SecProtonFractionVisEnergyInCone_3",
		                      &SecProtonFractionVisEnergyInCone_3,"SecProtonFractionVisEnergyInCone_3/D");
		
		ttrees[tname]->Branch("NumClustsPrimaryProtonEnd",&NumClustsPrimaryProtonEnd,"NumClustsPrimaryProtonEnd/I");
		ttrees[tname]->Branch("NumClustsSecProtonEnd_1",&NumClustsSecProtonEnd_1,"NumClustsSecProtonEnd_1/I");
		ttrees[tname]->Branch("NumClustsSecProtonEnd_2",&NumClustsSecProtonEnd_2,"NumClustsSecProtonEnd_2/I");
		ttrees[tname]->Branch("NumClustsSecProtonEnd_3",&NumClustsSecProtonEnd_3,"NumClustsSecProtonEnd_3/I");
		
		ttrees[tname]->Branch("MuonToPrimaryProtonAngle",&MuonToPrimaryProtonAngle,"MuonToPrimaryProtonAngle/D");
		
		ttrees[tname]->Branch("NBlobs",&NBlobs,"NBlobs/I");
		
		ttrees[tname]->Branch("ImprovedNMichel",&ImprovedNMichel,"ImprovedNMichel/I");
		ttrees[tname]->Branch("ImprovedMichel_0_Views",&ImprovedMichel_0_Views,"ImprovedMichel_0_Views/I");
		ttrees[tname]->Branch("ImprovedMichel_1_Views",&ImprovedMichel_1_Views,"ImprovedMichel_1_Views/I");
		ttrees[tname]->Branch("ImprovedMichel_2_Views",&ImprovedMichel_2_Views,"ImprovedMichel_2_Views/I");
		ttrees[tname]->Branch("ImprovedMichel_Sum_Views",&ImprovedMichel_Sum_Views,"ImprovedMichel_Sum_Views/I");
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
							MCIntType = universe->GetMCIntType();
							
							wgt = model.GetWeight(*universe, event);
							Q2QE = universe->GetQ2QEGeV();
							PperpMuGeV = universe->GetPperpMuGeV();
							PparMuGeV = universe->GetPparMuGeV();
							RecoilEnergyGeV = universe->GetRecoilEnergyGeV();
							Multiplicity = universe->GetMultiplicity();
							
							NumberOfProtonCandidates = universe->GetNumberOfProtonCandidates();
							
							PrimaryProtonScore1 = universe->GetProtonScore1_0();
							SecProtonScore1_1 = universe->GetProtonScore1_1();
							SecProtonScore1_2 = universe->GetProtonScore1_2();
							SecProtonScore1_3 = universe->GetProtonScore1_3();
							
							PrimaryProtonTfromdEdx = universe->GetPrimaryProtonTfromdEdx();
							SecProtonTfromdEdx_1 = universe->GetSecProtonTfromdEdx_1();
							SecProtonTfromdEdx_2 = universe->GetSecProtonTfromdEdx_2();
							SecProtonTfromdEdx_3 = universe->GetSecProtonTfromdEdx_3();
							
							ProtonRatioTdEdX2TrackLength_0 = universe->ProtonRatioTdEdX2TrackLength_0();
							//ProtonRatioTdEdX2TrackLength_1 = universe->ProtonRatioTdEdX2TrackLength_1();
							//ProtonRatioTdEdX2TrackLength_2 = universe->ProtonRatioTdEdX2TrackLength_2();
							//ProtonRatioTdEdX2TrackLength_3 = universe->ProtonRatioTdEdX2TrackLength_3();
							
							PrimaryProtonTrackVtxGap = universe->GetPrimaryProtonTrackVtxGap();
							//SecProtonTrackVtxGap_1 = universe->GetSecProtonTrackVtxGap_1();
							//SecProtonTrackVtxGap_2 = universe->GetSecProtonTrackVtxGap_2();
							//SecProtonTrackVtxGap_3 = universe->GetSecProtonTrackVtxGap_3();
							
							PrimaryProtonFractionVisEnergyInCone = universe->GetPrimaryProtonFractionVisEnergyInCone();
							SecProtonFractionVisEnergyInCone_1 = universe->GetSecProtonFractionVisEnergyInCone_1();
							SecProtonFractionVisEnergyInCone_2 = universe->GetSecProtonFractionVisEnergyInCone_2();
							SecProtonFractionVisEnergyInCone_3 = universe->GetSecProtonFractionVisEnergyInCone_3();
							
							NumClustsPrimaryProtonEnd = universe->GetNumClustsPrimaryProtonEnd();
							NumClustsSecProtonEnd_1 = universe->GetNumClustsSecProtonEnd_1();
							NumClustsSecProtonEnd_2 = universe->GetNumClustsSecProtonEnd_2();
							NumClustsSecProtonEnd_3 = universe->GetNumClustsSecProtonEnd_3();
							
							MuonToPrimaryProtonAngle = universe->GetMuonToPrimaryProtonAngle();
							
							NBlobs = universe->GetNBlobs();
							
							ImprovedNMichel = universe->GetImprovedNMichel();
							ImprovedMichel_0_Views = universe->GetImprovedMichel_0_Views();
							ImprovedMichel_1_Views = universe->GetImprovedMichel_1_Views();
							ImprovedMichel_2_Views = universe->GetImprovedMichel_2_Views();
							ImprovedMichel_Sum_Views = universe->GetImprovedMichel_Sum_Views();
							
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
  /*RBDT<> my_1track_bdt("my_1track_BDT","/home/sean/MinervaExpt/CCQENu/make_hists/smg/tmva_1track_Training.root");
  RBDT<> my_2track_bdt("my_2track_BDT","/home/sean/MinervaExpt/CCQENu/make_hists/smg/tmva_2track_Training.root");
  RBDT<> my_3ptrack_bdt("my_3ptrack_BDT","/home/sean/MinervaExpt/CCQENu/make_hists/smg/tmva_3ptrack_Training.root");*/
  
  // TMVA only
	RReader model_1track(expandEnv("${CCQEMAT}/TMVA/TMVAMulticlass_1track_BDTG.weights.xml"));
  RReader model_2track(expandEnv("${CCQEMAT}/TMVA/TMVAMulticlass_2track_BDTG.weights.xml"));
  RReader model_3ptrack(expandEnv("${CCQEMAT}/TMVA/TMVAMulticlass_3ptrack_BDTG.weights.xml"));

	const clock_t begin_time = clock();

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
					float proton_ratio_T_to_length_0 = universe->ProtonRatioTdEdX2TrackLength_0();
					float proton_ratio_T_to_length_1 = universe->ProtonRatioTdEdX2TrackLength_1();
					float proton_ratio_T_to_length_2 = universe->ProtonRatioTdEdX2TrackLength_2();
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
							input_vars.emplace_back(proton_ratio_T_to_length_0);
							input_vars.emplace_back(proton_clusters_0);
							input_vars.emplace_back(proton_fraction_vis_energy_in_cone_0);
							input_vars.emplace_back(blob_count);
							input_vars.emplace_back(improved_michel_count);
							input_vars.emplace_back(recoil);
							input_vars.emplace_back(improved_michel_sum_views);
							
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
							input_vars.emplace_back(proton_ratio_T_to_length_0);
							input_vars.emplace_back(proton_ratio_T_to_length_1);
							input_vars.emplace_back(proton_clusters_0);
							input_vars.emplace_back(proton_clusters_1);
							input_vars.emplace_back(proton_fraction_vis_energy_in_cone_0);
							input_vars.emplace_back(proton_fraction_vis_energy_in_cone_1);
							input_vars.emplace_back(sec_proton_cand_count);
							input_vars.emplace_back(blob_count);
							input_vars.emplace_back(improved_michel_count);
							input_vars.emplace_back(recoil);
							input_vars.emplace_back(improved_michel_sum_views);
							
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
				
				CVUniverse::SetTMVAVectorResponse(response_vec);
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
            FillData(tag, universe, variables, variables2D, 1.);
            
          }
        }

        CVUniverse::ResetTMVAResponse();
        //CVUniverse::ResetXgboostVectorResponse();


      } // End universes
    } // End error bands
    
    if(data_mc_truth != kData) i+= prescale-1;
    
  } // End entries loop
  std::cout << "Elapsed time: " << float( clock() - begin_time )/1000000 << " s" << std::endl;

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
            FillData(tag, universe, variables, variables2D, 1.);
            
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
