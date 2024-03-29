#define CLOSURE 1

#include <map>
#include <vector>
#include <string>

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
                               PlotUtils::Cutter<CVUniverse>& selection, PlotUtils::Model<CVUniverse,PlotUtils::detail::empty>& model,
                               PlotUtils::weight_MCreScale mcRescale) {
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

#ifdef CLOSURE
      const double cvWeight = 1.0;
#else
      const double cvWeight = (data_mc_truth == kData) ? 1.: model.GetWeight(*cvUniv,event);
#endif
    // detail may be used for more complex things
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
#ifdef CLOSURE
          const double weight = 1.0;
        
#else
          const double weight = (data_mc_truth == kData) ? 1. : model.GetWeight(*universe, event);
#endif
        //Only calculate the per-universe weight for events that will actually use it.
        //PlotUtils::detail::empty event;

        //=========================================
        // Fill
        //=========================================

        if(data_mc_truth == kMC){
          if(selection.isMCSelected(*universe, event, weight).all()
             && selection.isSignal(*universe)) {
            //double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
            const double q2qe = universe->GetQ2QEGeV();
            double scale = mcRescale.GetScale(tag, q2qe, uni_name, iuniv); //Only calculate the per-universe weight for events that will actually use it.
#ifdef CLOSURE
            scale = 1.0;
#endif
            FillMC(tag, universe, weight, variables, variables2D, scale);
            FillResponse(tag,universe,weight,variables,variables2D, scale);
          }

        }
        else if (data_mc_truth == kTruth){

          if(selection.isEfficiencyDenom(*universe, weight)){
            const double q2qe = universe->GetTrueQ2QEGeV();
            double scale = mcRescale.GetScale(tag, q2qe, uni_name, iuniv); //Only calculate the per-universe weight for events that will actually use it.
#ifdef CLOSURE
            scale = 1.0;
#endif
            FillSignalTruth(tag, universe, weight, variables, variables2D, scale);
          }
        }
        else{ //kData

          if(selection.isDataSelected(*universe, event).all()) FillData(tag, universe, variables, variables2D);
        }

      } // End universes
    } // End error bands
  } // End entries loop
}

#endif //__CINT__
