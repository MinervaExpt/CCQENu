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
  
    trueintfunctions["TruthIsOther"] = &CVUNIVERSE::GetTruthIsOther;
  
    // Interaction Vertex

    recointfunctions["HasInteractionVertex"] = &CVUNIVERSE::GetHasInteractionVertex;
    
    // Isolated Blobs and Charged Pions
    
    recofunctions["NBlobs"] = &CVUNIVERSE::GetNBlobs;
    
    recointfunctions["HasMichelElectron"] = &CVUNIVERSE::GetHasMichelElectron;
    recointfunctions["MichelElectronCandidates"] = &CVUNIVERSE::GetMichelElectronCandidates;
    recofunctions["MichelElectronCandidates"] = &CVUNIVERSE::GetMichelElectronCandidates;
    trueintfunctions["TruthHasMichel"] = &CVUNIVERSE::GetTruthHasMichel;
    truefunctions["TruthHasMichel"] = &CVUNIVERSE::GetTruthHasMichel;

    recointfunctions["AllExtraTracksProtons"] = &CVUNIVERSE::GetAllExtraTracksProtons;
    recointfunctions["IsSingleProton"] = &CVUNIVERSE::GetIsSingleProton;
    trueintfunctions["TruthHasSingleProton"] = &CVUNIVERSE::GetTruthHasSingleProton;
    
    // genie particle counts
    trueintfunctions["TrueChargedPionCount"] = &CVUNIVERSE::GetTrueChargedPionCount;
    truefunctions["TrueChargedPionCount"] = &CVUNIVERSE::GetTrueChargedPionCount;
    trueintfunctions["TrueNeutralPionCount"] = &CVUNIVERSE::GetTrueNeutralPionCount;
    truefunctions["TrueNeutralPionCount"] = &CVUNIVERSE::GetTrueNeutralPionCount;
    trueintfunctions["TruePionCount"] = &CVUNIVERSE::GetTruePionCount;
    truefunctions["TruePionCount"] = &CVUNIVERSE::GetTruePionCount;
    
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
