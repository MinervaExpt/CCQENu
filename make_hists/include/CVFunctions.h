// ========================================================================
// Place to put a map of CVUniverse functions
//
// ========================================================================
#ifndef CVFUNCTIONS_H
#define CVFUNCTIONS_H

#include <iostream>

#include "include/CVUniverse.h"
#include <string>
#include <map>
#include <vector>
#include <functional>
#include <cassert>


template <class CVUNIVERSE>
class CVFunctions{
  
  typedef std::function<double(const CVUNIVERSE&)> PointerToCVUniverseFunction;
  typedef std::function<int(const CVUNIVERSE&)> PointerToCVUniverseIntFunction;
  std::map<const std::string, PointerToCVUniverseFunction> recofunctions;
  std::map<const std::string, PointerToCVUniverseFunction> truefunctions;
  std::map<const std::string, PointerToCVUniverseIntFunction> recointfunctions;
  std::map<const std::string, PointerToCVUniverseIntFunction> trueintfunctions;

public:
  CVFunctions(){
    recofunctions["ZVertex"] = &CVUNIVERSE::GetZVertex;
    truefunctions["TrueZVertex"] = &CVUNIVERSE::GetTrueZVertex;
    
    recofunctions["ApothemX"] = &CVUNIVERSE::GetApothemX;
    truefunctions["TrueApothemX"] = &CVUNIVERSE::GetTrueApothemX;
       
    recofunctions["ApothemY"] = &CVUNIVERSE::GetApothemY;
    truefunctions["TrueApothemY"] = &CVUNIVERSE::GetTrueApothemY;
       
    recofunctions["EnuCCQEGeV"] = &CVUNIVERSE::GetEnuCCQEGeV;
    truefunctions["TrueEnuCCQEGeV"] = &CVUNIVERSE::GetTrueEnuCCQEGeV;
    
    recofunctions["EnuHadGeV"] = &CVUNIVERSE::GetEnuHadGeV;
    truefunctions["TrueEnuGeV"] = &CVUNIVERSE::GetTrueEnuGeV;
    
    recofunctions["PmuGeV"] = &CVUNIVERSE::GetPmuGeV;
    truefunctions["TruePmuGeV"] = &CVUNIVERSE::GetTruePmuGeV;
    
    recofunctions["PparMuGeV"] = &CVUNIVERSE::GetPparMuGeV;
    truefunctions["TruePparMuGeV"] = &CVUNIVERSE::GetTruePparMuGeV;
    
    recofunctions["PperpMuGeV"] = &CVUNIVERSE::GetPperpMuGeV;
    truefunctions["TruePperpMuGeV"] = &CVUNIVERSE::GetTruePperpMuGeV;
    
    recofunctions["Q2QEGeV"] = &CVUNIVERSE::GetQ2QEGeV;
    truefunctions["TrueQ2QEGeV"] = &CVUNIVERSE::GetTrueQ2QEGeV;
    truefunctions["TrueQ2GeV"] = &CVUNIVERSE::GetTrueQ2GeV;
    
    recofunctions["Curvature"] = &CVUNIVERSE::GetCurvature;
    truefunctions["TrueCurvature"] = &CVUNIVERSE::GetTrueCurvature;
    
    recofunctions["RecoilEnergyGeV"] = &CVUNIVERSE::GetRecoilEnergyGeV;
    truefunctions["TrueRecoilEnergyGeV"] = &CVUNIVERSE::GetTrueRecoilEnergyGeV;
    
    recofunctions["Log10RecoilEnergyGeV"] = &CVUNIVERSE::GetLog10RecoilEnergyGeV;
    truefunctions["TrueLog10RecoilEnergyGeV"] = &CVUNIVERSE::GetTrueLog10RecoilEnergyGeV;
    // there is not true value
    
    recofunctions["ThetamuDegrees"] = &CVUNIVERSE::GetThetamuDegrees;
    truefunctions["TrueThetamuDegrees"] = &CVUNIVERSE::GetTrueThetamuDegrees;
    
    recofunctions["DeadTime"] = &CVUNIVERSE::GetDeadTime;
    
    recofunctions["Multiplicity"] = &CVUNIVERSE::GetMultiplicity;
    recointfunctions["Multiplicity"] = &CVUNIVERSE::GetMultiplicity;
      
      // truth only variables for studies
      
      truefunctions["MCTargetA"] = &CVUNIVERSE::GetMCTargetA;
      
      truefunctions["MCTargetZ"] = &CVUNIVERSE::GetMCTargetZ;
      
      truefunctions["MCTargetNucleon"] = &CVUNIVERSE::GetMCTargetNucleon;
      
      recofunctions["MCTargetA"] = &CVUNIVERSE::GetMCTargetA;
      
      recofunctions["MCTargetZ"] = &CVUNIVERSE::GetMCTargetZ;
      
      recofunctions["MCTargetNucleon"] = &CVUNIVERSE::GetMCTargetNucleon;
      
      recofunctions["Dummy"]= &CVUNIVERSE::Dummy;
      
      truefunctions["Dummy"]= &CVUNIVERSE::Dummy;
    
    // integer functions for equals
    
    recointfunctions["IsMinosMatchTrack"] = &CVUNIVERSE::GetIsMinosMatchTrack;
  
    recointfunctions["NuHelicity"] = &CVUNIVERSE::GetNuHelicity;
    
    recointfunctions["GoodRecoil"] = &CVUNIVERSE::GetGoodRecoil;
    
    trueintfunctions["TruthIsCCQELike"] = &CVUNIVERSE::GetTruthIsCCQELike;
    trueintfunctions["TruthIsCCQELikeAll"] = &CVUNIVERSE::GetTruthIsCCQELikeAll;
    
    trueintfunctions["TruthIsCC"] = &CVUNIVERSE::GetTruthIsCC;
    
    trueintfunctions["TruthNuPDG"] = &CVUNIVERSE::GetTruthNuPDG;
    
    trueintfunctions["MCIntType"] = &CVUNIVERSE::GetMCIntType;
      
      trueintfunctions["MCTargetA"] = &CVUNIVERSE::GetMCTargetA;
      
      trueintfunctions["MCTargetZ"] = &CVUNIVERSE::GetMCTargetZ;
      
      trueintfunctions["MCTargetNucleon"] = &CVUNIVERSE::GetMCTargetNucleon;
      
      recointfunctions["MCTargetA"] = &CVUNIVERSE::GetMCTargetA;
      
      recointfunctions["MCTargetZ"] = &CVUNIVERSE::GetMCTargetZ;
      
      recointfunctions["MCTargetNucleon"] = &CVUNIVERSE::GetMCTargetNucleon;
      
      recointfunctions["Dummy"]= &CVUNIVERSE::Dummy;
      trueintfunctions["Dummy"]= &CVUNIVERSE::Dummy;
      
      
    
    // ----------------------- Sean Neutrino Functions ------------------------------------------
  
    // Interaction Vertex

    recointfunctions["HasInteractionVertex"] = &CVUNIVERSE::GetHasInteractionVertex;
    
    // Isolated Blobs
    
    recofunctions["NBlobs"] = &CVUNIVERSE::GetNBlobs;
    
	// Michel Electrons

    recointfunctions["HasMichelElectron"] = &CVUNIVERSE::GetHasMichelElectron;
    recointfunctions["HasImprovedMichelElectron"] = &CVUNIVERSE::GetHasImprovedMichelElectron;
    recointfunctions["NMichel"] = &CVUNIVERSE::GetNMichel;
    recofunctions["NMichel"] = &CVUNIVERSE::GetNMichel;
    recointfunctions["ImprovedNMichel"] = &CVUNIVERSE::GetImprovedNMichel;
    recofunctions["ImprovedNMichel"] = &CVUNIVERSE::GetImprovedNMichel;
    recointfunctions["FittedNMichel"] = &CVUNIVERSE::GetFittedNMichel;
    recofunctions["FittedNMichel"] = &CVUNIVERSE::GetFittedNMichel;
    trueintfunctions["TruthHasMichel"] = &CVUNIVERSE::GetTruthHasMichel;
    truefunctions["TruthHasMichel"] = &CVUNIVERSE::GetTruthHasMichel;
    trueintfunctions["TruthHasImprovedMichel"] = &CVUNIVERSE::GetTruthHasImprovedMichel;
    truefunctions["TruthHasImprovedMichel"] = &CVUNIVERSE::GetTruthHasImprovedMichel;
    trueintfunctions["TrueFittedNMichel"] = &CVUNIVERSE::GetTrueFittedNMichel;
    truefunctions["TrueFittedNMichel"] = &CVUNIVERSE::GetTrueFittedNMichel;

	// Protons

	recofunctions["ProtonScore_0"] = &CVUNIVERSE::GetProtonScore_0;
	recofunctions["ProtonScore_1"] = &CVUNIVERSE::GetProtonScore_1;
	recofunctions["ProtonScore_2"] = &CVUNIVERSE::GetProtonScore_2;
	recofunctions["ProtonScore_3"] = &CVUNIVERSE::GetProtonScore_3;
	recofunctions["ProtonScore_4"] = &CVUNIVERSE::GetProtonScore_4;
	recofunctions["ProtonScore_5"] = &CVUNIVERSE::GetProtonScore_5;
	recofunctions["ProtonScore_6"] = &CVUNIVERSE::GetProtonScore_6;
	recofunctions["ProtonScore_7"] = &CVUNIVERSE::GetProtonScore_7;
	recofunctions["ProtonScore_8"] = &CVUNIVERSE::GetProtonScore_8;
	recofunctions["ProtonScore_9"] = &CVUNIVERSE::GetProtonScore_9;
	
	recointfunctions["PassScoreCutProton_0"] = &CVUNIVERSE::GetPassScoreCutProton_0;
	recointfunctions["PassScoreCutProton_1"] = &CVUNIVERSE::GetPassScoreCutProton_1;
	recointfunctions["PassScoreCutProton_2"] = &CVUNIVERSE::GetPassScoreCutProton_2;
	recointfunctions["PassScoreCutProton_3"] = &CVUNIVERSE::GetPassScoreCutProton_3;
	recointfunctions["PassScoreCutProton_4"] = &CVUNIVERSE::GetPassScoreCutProton_4;
	recointfunctions["PassScoreCutProton_5"] = &CVUNIVERSE::GetPassScoreCutProton_5;
	recointfunctions["PassScoreCutProton_6"] = &CVUNIVERSE::GetPassScoreCutProton_6;
	recointfunctions["PassScoreCutProton_7"] = &CVUNIVERSE::GetPassScoreCutProton_7;
	recointfunctions["PassScoreCutProton_8"] = &CVUNIVERSE::GetPassScoreCutProton_8;
	recointfunctions["PassScoreCutProton_9"] = &CVUNIVERSE::GetPassScoreCutProton_9;

	recointfunctions["SecondaryProtonCandidateCount"] = &CVUNIVERSE::GetSecondaryProtonCandidateCount;
	recofunctions["SecondaryProtonCandidateCount"] = &CVUNIVERSE::GetSecondaryProtonCandidateCount;
    recointfunctions["AllExtraTracksProtons"] = &CVUNIVERSE::GetAllExtraTracksProtons;
    recointfunctions["IsPrimaryProton"] = &CVUNIVERSE::GetIsPrimaryProton;
    recofunctions["PrimaryProtonScore"] = &CVUNIVERSE::GetPrimaryProtonScore;
    trueintfunctions["TruthHasSingleProton"] = &CVUNIVERSE::GetTruthHasSingleProton;
    truefunctions["TruthHasSingleProton"] = &CVUNIVERSE::GetTruthHasSingleProton;
    recointfunctions["ProtonCount"] = &CVUNIVERSE::GetProtonCount;
    recofunctions["ProtonCount"] = &CVUNIVERSE::GetProtonCount;
    
    // Genie Particle Counts
    
    trueintfunctions["TrueChargedPionCount"] = &CVUNIVERSE::GetTrueChargedPionCount;
    truefunctions["TrueChargedPionCount"] = &CVUNIVERSE::GetTrueChargedPionCount;
    trueintfunctions["TrueNeutralPionCount"] = &CVUNIVERSE::GetTrueNeutralPionCount;
    truefunctions["TrueNeutralPionCount"] = &CVUNIVERSE::GetTrueNeutralPionCount;
    trueintfunctions["TruePionCount"] = &CVUNIVERSE::GetTruePionCount;
    truefunctions["TruePionCount"] = &CVUNIVERSE::GetTruePionCount;
    
    trueintfunctions["TrueProtonCount"] = &CVUNIVERSE::GetTrueProtonCount;
    truefunctions["TrueProtonCount"] = &CVUNIVERSE::GetTrueProtonCount;
    
    trueintfunctions["TrueCharmedBaryonCount"] = &CVUNIVERSE::GetTrueCharmedBaryonCount;
    truefunctions["TrueCharmedBaryonCount"] = &CVUNIVERSE::GetTrueCharmedBaryonCount;
    trueintfunctions["TrueStrangeBaryonCount"] = &CVUNIVERSE::GetTrueStrangeBaryonCount;
    truefunctions["TrueStrangeBaryonCount"] = &CVUNIVERSE::GetTrueStrangeBaryonCount;
    
    trueintfunctions["TrueCharmedMesonCount"] = &CVUNIVERSE::GetTrueCharmedMesonCount;
    truefunctions["TrueCharmedMesonCount"] = &CVUNIVERSE::GetTrueCharmedMesonCount;
    trueintfunctions["TrueStrangeMesonCount"] = &CVUNIVERSE::GetTrueStrangeMesonCount;
    truefunctions["TrueStrangeMesonCount"] = &CVUNIVERSE::GetTrueStrangeMesonCount;
    
    trueintfunctions["TruthHasSingleChargedPion"] = &CVUNIVERSE::GetTruthHasSingleChargedPion;
    trueintfunctions["TruthHasSingleNeutralPion"] = &CVUNIVERSE::GetTruthHasSingleNeutralPion;
    trueintfunctions["TruthHasMultiPion"] = &CVUNIVERSE::GetTruthHasMultiPion;
    
    truefunctions["EventRecordTrueEtaCount"] = &CVUNIVERSE::GetEventRecordTrueEtaCount;
    trueintfunctions["EventRecordTrueEtaCount"] = &CVUNIVERSE::GetEventRecordTrueEtaCount;
    
  };
  
  std::vector<std::string> GetRecoKeys()const{
    std::vector<std::string> keys;
    for(auto key:recofunctions) {
      keys.push_back(key.first);
    }
    return keys;
  }
  
  std::vector<std::string> GetTrueKeys()const{
    std::vector< std::string> keys;
    for(auto key:truefunctions) {
      keys.push_back(key.first);
    }
    return keys;
  }
    
  const PointerToCVUniverseFunction GetRecoFunction(const std::string name) {
    assert (recofunctions.count(name));
    PointerToCVUniverseFunction  result = recofunctions[name];
    return result ;
  };
  
  PointerToCVUniverseFunction GetTrueFunction(const std::string name) {
    // try a real function first
    if (truefunctions.count(name)){
      return truefunctions[name];
    }
    else{
      assert(trueintfunctions.count(name));
      return trueintfunctions[name];
    }
  };
  
  const PointerToCVUniverseIntFunction GetRecoIntFunction(const std::string name) {
    assert (recointfunctions.count(name));
    return recointfunctions[name];
  };
  
  PointerToCVUniverseIntFunction GetTrueIntFunction(const std::string name) {
    assert (trueintfunctions.count(name));
    return trueintfunctions[name];
  };
};


#endif
