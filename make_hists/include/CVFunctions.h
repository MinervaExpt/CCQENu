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
    // there is not true value
    
    recofunctions["ThetamuDegrees"] = &CVUNIVERSE::GetThetamuDegrees;
    truefunctions["TrueThetamuDegrees"] = &CVUNIVERSE::GetTrueThetamuDegrees;
    
    recofunctions["DeadTime"] = &CVUNIVERSE::GetDeadTime;
    
    recofunctions["Multiplicity"] = &CVUNIVERSE::GetMultiplicity;
    
    // integer functions for equals
    
    recointfunctions["IsMinosMatchTrack"] = &CVUNIVERSE::GetIsMinosMatchTrack;
  
    recointfunctions["NuHelicity"] = &CVUNIVERSE::GetNuHelicity;
    
    recointfunctions["GoodRecoil"] = &CVUNIVERSE::GetGoodRecoil;
    
    trueintfunctions["IsCCQELike"] = &CVUNIVERSE::GetIsCCQELike;
    trueintfunctions["IsCCQELikeAll"] = &CVUNIVERSE::GetIsCCQELikeAll;
    
    trueintfunctions["IsCC"] = &CVUNIVERSE::GetIsCC;
    
    trueintfunctions["TruthNuPDG"] = &CVUNIVERSE::GetTruthNuPDG;
    
    // Added by Sean for Neutrino

    recointfunctions["HasInteractionVertex"] = &CVUNIVERSE::GetHasInteractionVertex;
    recofunctions["HasMichelElectron"] = &CVUNIVERSE::GetHasMichelElectron;
    recofunctions["NBlobs"] = &CVUNIVERSE::GetNBlobs;
    recointfunctions["AllExtraTracksProtons"] = &CVUNIVERSE::GetAllExtraTracksProtons;
    recofunctions["IsSingleProton"] = &CVUNIVERSE::GetIsSingleProton;
    recofunctions["SingleProtonScore"] = &CVUNIVERSE::GetSingleProtonScore;

    truefunctions["TruthHasSingleProton"] = &CVUNIVERSE::GetTruthHasSingleProton;
    truefunctions["TruthHasMichel"] = &CVUNIVERSE::GetTruthHasMichel;

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
    assert (truefunctions.count(name));
    return truefunctions[name];
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
