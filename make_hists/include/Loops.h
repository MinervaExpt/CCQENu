

enum EDataMCTruth {kData, kMC, kTruth, kNDataMCTruthTypes};




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
                               PlotUtils::Cutter<CVUniverse>& selection, PlotUtils::Model<CVUniverse,PlotUtils::detail::empty>& model) {
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
  
  std::cout << " starting loop " << data_mc_truth << " " << nentries << std::endl;
  // Begin entries loop
  for (int i = 0; i < nentries; i++) {
    if(data_mc_truth != kData) i+= prescale-1;
    if (i+1 % 1000 == 0) std::cout << (i / 1000) << "k " << std::endl;
    cvUniv->SetEntry(i);
    
    if (data_mc_truth != kData) model.SetEntry(*cvUniv, event);
    
  
    const double cvWeight = (data_mc_truth == kData) ? 1. : model.GetWeight(*cvUniv,event);  // detail may be used for more complex things
    
    // Loop bands and universes
    for (auto band : error_bands) {
      std::vector<CVUniverse*> error_band_universes = band.second;
      for (auto universe : error_band_universes) {

        universe->SetEntry(i);

        // Process this event/universe
        //double weight = 1;
        //if (universe->ShortName() == "cv" ) weight = data_mc_truth == kData ? 1. : universe->GetWeight();
    
          // probably want to move this later on inside the loop
        const double weight = (data_mc_truth == kData) ? 1. : model.GetWeight(*universe, event); //Only calculate the per-universe weight for events that will actually use it.

        //TODO: Put the IsVertical() short circuit into PlotUtils::Cutter directly
        //PlotUtils::detail::empty event;

        //=========================================
        // Fill
        //=========================================

        if(data_mc_truth == kMC){
          if(selection.isMCSelected(*universe, event, weight).all()
             && selection.isSignal(*universe)) {
            //double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
            FillMC(tag, universe, weight, variables, variables2D);
            FillResponse(tag, universe,weight,variables,variables2D);
          }

        }
        else if (data_mc_truth == kTruth){

          if(selection.isEfficiencyDenom(*universe, weight)){
           
            FillSignalTruth(tag, universe, weight, variables, variables2D);
          }
        }
        else{ //kData

          if(selection.isDataSelected(*universe, event).all()) FillData(tag, universe, variables, variables2D);
        }

      } // End universes
    } // End error bands
  } // End entries loop
}

// Deprecate
void LoopAndFillEventSelection2D(std::string tag,
                                 const PlotUtils::MacroUtil& util,
                                 std::map<std::string, std::vector<CVUniverse*> > error_bands,
                                 std::vector<CCQENu::Variable2DFromConfig*>& variables2D,
                                 EDataMCTruth data_mc_truth,
                                 PlotUtils::Cutter<CVUniverse>& selection) {
  // Prepare loop

  if ( variables2D.size() < 1) return;  // don't bother if there are no variables.

  MinervaUniverse::SetTruth(false);
  int nentries = -1;
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

  std::cout << " starting 2D loop " << data_mc_truth << " " << nentries << std::endl;
  // Begin entries loop
  for (int i = 0; i < nentries; i++) {
    if(data_mc_truth != kData) i+= prescale-1;
    if (i+1 % 1000 == 0) std::cout << (i / 1000) << "k " << std::endl;
    // Loop bands and universes
    for (auto band : error_bands) {
      std::vector<CVUniverse*> error_band_universes = band.second;
      for (auto universe : error_band_universes) {

        universe->SetEntry(i);

        // Process this event/universe
        double weight = 1;
        if (universe->ShortName() == "cv" ) weight = data_mc_truth == kData ? 1. : universe->GetWeight();

        //TODO: Put the IsVertical() short circuit into PlotUtils::Cutter directly
        PlotUtils::detail::empty event;

        //=========================================
        // Fill
        //=========================================

        if(data_mc_truth == kMC){
          if(selection.isMCSelected(*universe, event, weight).all()
             && selection.isSignal(*universe)) {
            double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
            FillMC2D(tag, universe, weight, variables2D);
            FillResponse2D(tag, universe,weight,variables2D);
          }

        }
        else if (data_mc_truth == kTruth){

          if(selection.isEfficiencyDenom(*universe, weight)){
            double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
            FillSignalTruth2D(tag, universe, weight, variables2D);
          }
        }
        else{ //kData

          if(selection.isDataSelected(*universe, event).all()) FillData2D(tag, universe, variables2D);
        }

      } // End universes
    } // End error bands
  } // End entries loop
}
#endif //__CINT__