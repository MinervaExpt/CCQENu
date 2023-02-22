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

enum EDataMCTruth {kData, kMC, kTruth, kNDataMCTruthTypes};


//#define CLOSUREDETAIL

//==============================================================================
// Loop and fill
//==============================================================================
ifndef __CINT__ //for PlotUtils::cuts_t<>
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

	std::ofstream csvFile;
  if ( variables.size() < 1) {
    std::cout << " no variables to fill " << std::endl;
    return;  // don't bother if there are no variables.
  }

  if (data_mc_truth == kData ){
    nentries = util.GetDataEntries();
  }
  else if (data_mc_truth == kMC ){
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
  
  // If sending MC Reco values to CSV create file and add columns names
  if (data_mc_truth == kMC && mc_reco_to_csv){

  	std::string csvFileName = "mc_reco_entries_"+sample+"_"+cat+".csv";
	  csvFile.open(csvFileName);
	  csvFile << "Entry";
	  for (auto v : variables) {
	  	if (v->hasMC[tag]){
	  		csvFile << ";" << v->GetName();
	  	}
	  }
	  csvFile << std::endl;

  }
  
  // status bar stuff
  std::cout << std::endl;
	std::cout << "  0% 10% 20% 30% 40% 50% 60% 70% 80% 90% 100%" << std::endl;
	std::cout << "   \\___\\___\\___\\___\\___\\___\\___\\___\\___\\___\\ " << std::endl;
	std::cout << "   |________________________________________|   [__0.0%]";
	double progress = 0;
	
	// Begin entries loop
  for (int i = 0; i < nentries; i++) {
    if(data_mc_truth != kData) i+= prescale-1;
    
    //if (i+1 % 1000 == 0) std::cout << (i / 1000) << "k " << std::endl;
    // status bar stuff
    if( ((double)(i+1)/nentries)*100 >= progress+2.5 ) {
	  
	  	progress+=2.5;
			std::cout << '\r' << std::flush << "   |";
			//std::cout << std::endl << "   |";
		
			for(int j=0;j<progress/2.5;j++) std::cout << "\e[0;31;47m \e[0m";
			for(int j=40;j>progress/2.5;j--) std::cout << "_";

			std::cout << "|   [";
			if(progress<10) std::cout << "_";
			if(progress<100) std::cout << "_";
			std::cout << progress;
			if(((int)(0.5 + progress/2.5))%2==0) std::cout << ".0";
			std::cout << "%]";
			std::cout << "   ( ";
			for(int j=((int)log10(nentries)-(int)log10(i+1)); j>0; j--) {
				std::cout << "_";
			}
			std::cout << i+1 << " / " << nentries << " )";

			if(progress == 100) std::cout << std::endl << std::endl;
		}
		
    cvUniv->SetEntry(i);

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
            
            // Send MC Reco value to CSV here
            if (mc_reco_to_csv) {
		          csvFile << i;
		          for (auto v : variables) {
		          	if (v->hasMC[tag]){
		          		csvFile << ";" << v->GetRecoValue(*universe, 0);
		          	}
		          }
		          csvFile << std::endl;
            }
            // Done Sending MC Reco value to CSV

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
  } // End entries loop
  if (data_mc_truth == kMC && mc_reco_to_csv) {
  	csvFile.close();
  	std::string csvFileName = "mc_reco_entries_"+sample+"_"+cat+".csv";
    std::cout << std::endl;
    std::cout << "MC Reco events for " << sample << " category " << cat << " saved to " << csvFileName;
    std::cout << std::endl;
  }
}

#endif //__CINT__
