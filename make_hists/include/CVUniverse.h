// ========================================================================
// Base class for an un-systematically shifted (i.e. CV) universe.
// Implement "Get" functions for all the quantities that you need for your
// analysis.
//
// This class inherits from PU::sUniverse. PU::DCVU may already define
// your "Get" functions the way you want them. In that case, you  don't need to
// re-write them here.
// ========================================================================
#ifndef CVUNIVERSE_H
#define CVUNIVERSE_H

#include <iostream>

#include "PlotUtils/ChainWrapper.h"
#include "PlotUtils/MinervaUniverse.h"
#include "PlotUtils/PhysicsVariables.h"
#include "TVector3.h"
#include "PlotUtils/GeantHadronSystematics.h"


class CVUniverse : public PlotUtils::MinervaUniverse {
 public:
  #ifndef HAZMAT
   #include "PlotUtils/SystCalcs/WeightFunctions.h"
   #include "PlotUtils/SystCalcs/MuonFunctions.h"
   #include "PlotUtils/SystCalcs/TruthFunctions.h"
   #include "PlotUtils/SystCalcs/RecoilEnergyFunctions.h"
  #else
   #include "PlotUtils/WeightFunctions.h"
   #include "PlotUtils/MuonFunctions.h"
   #include "PlotUtils/TruthFunctions.h"
   #include "PlotUtils/RecoilEnergyFunctions.h"
  #endif

  // ========================================================================
  // Constructor/Destructor
  // ========================================================================
  
  // fake a default constructor
  
  CVUniverse(){PlotUtils::MinervaUniverse();};
  
  CVUniverse(PlotUtils::ChainWrapper* chw, double nsigma = 0)
  : PlotUtils::MinervaUniverse(chw, nsigma) {}

  virtual ~CVUniverse() {}
  
  // ========================================================================
  // Get 
  // ========================================================================
  
  static std::map<std::string, int> GetEventParticleCounts()
  
  // ========================================================================
  // Get Weight
  // ========================================================================

  virtual double GetWeight() const;

  // ========================================================================
  // Write a "Get" function for all quantities access by your analysis.
  // For composite quantities (e.g. Enu) use a calculator function.
  //
  // Currently PlotUtils::MinervaUniverse may already define some functions
  // that you want. The future of these functions is uncertain. You might want
  // to write all your own functions for now.
  // ========================================================================
  
  virtual int GetMultiplicity() const;
  
  virtual int GetDeadTime() const;
  
  // ----------------------- Analysis-related Variables ------------------------
  
  
  virtual int GetIsMinosMatchTrack()const;

  virtual double GetEnuHadGeV() const;
  virtual double GetTrueEnuGeV() const;

  virtual double GetEnuCCQEGeV() const; // both neutrino and antinu
  virtual double GetTrueEnuCCQEGeV() const; // may be a better way to implement this

  virtual double GetQ2QEGeV() const;
  virtual double GetTrueQ2QEGeV() const;

  virtual double GetLog10Q2QEGeV() const;
  virtual double GetTrueLog10Q2QEGeV() const;


  // ------------------------------ Muon Variables -----------------------------

  virtual double GetEmuGeV() const;
  virtual double GetTrueEmuGeV() const;

  virtual double GetPmuGeV() const;
  virtual double GetTruePmuGeV() const;

  virtual double GetPparMuGeV() const;
  virtual double GetTruePparMuGeV() const;

  virtual double GetPperpMuGeV() const;
  virtual double GetTruePperpMuGeV() const;

  virtual double GetTrueThetaXmu() const;
  virtual double GetTrueThetaYmu() const;

  virtual double GetTrueThetamu() const;
  
  virtual double GetThetamuDegrees() const;
  virtual double GetTrueThetamuDegrees() const;


  // ----------------------------- Proton Variables ----------------------------

  virtual double GetHadronEGeV() const;

  // ----------------------------- Recoil Variables ----------------------------

  
  virtual double GetCalRecoilEnergy() const;
  virtual double GetCalRecoilEnergyGeV() const;
  
  virtual double GetNonCalRecoilEnergy() const;
  virtual double GetNonCalRecoilEnergyGeV() const;

  virtual double GetRecoilEnergyGeV() const;
  virtual double GetTrueRecoilEnergyGeV() const;

  virtual double GetTrueQ0GeV() const;
  virtual double GetTrueQ3GeV() const;
  virtual double GetTrueQ2GeV() const;


  // ----------------------------- Other Variables -----------------------------

  //  virtual double GetWgenie() const { return GetDouble("mc_w"); }
  virtual int GetMCIntType() const;

  virtual int GetTruthNuPDG() const;

  virtual int GetCurrent() const;

  virtual double GetTpiGeV( const int hadron ) const;


  // --------------------- Quantities only needed for cuts ---------------------
  // Although unlikely, in principle these quanties could be shifted by a
  // systematic. And when they are, they'll only be shifted correctly if we
  // write these accessor functions.
  virtual bool IsMinosMatchMuon() const; // This isn't even used anymore, there's something else. This is left over from Amit's analysis

  virtual int GetNuHelicity() const;
  
  virtual double GetCurvature() const;
  virtual double GetTrueCurvature() const;
  
  virtual int GetTDead() const; // Dead electronics, a rock muon removal technique. Amit's analysis doesn't
  // have that cut most likely. Not even in that tuple, only reason it survives is bc it's not called anymore.
  // Can't find it? Just a hard coded constant in CCQENuCutsNSF.h

  // These cuts are already made in the CCQENu AnaTuple, may be unnecessary
  ROOT::Math::XYZTVector GetVertex() const;
  
  // 1-d apothems for cuts
  
  double GetApothemY() const;
  double GetApothemX() const;
  
  double GetTrueApothemY() const;
  double GetTrueApothemX() const;
  
  double GetZVertex() const;
  ROOT::Math::XYZTVector GetTrueVertex() const;
  double GetTrueZVertex() const;


  // Some stuff Heidi added to test out some issues with the NTuples

  virtual int GetRun() const;
  virtual int GetSubRun() const;
  virtual int GetGate() const;
  virtual int GetTrueRun() const;
  virtual int GetTrueSubRun() const;
  virtual int GetTrueGate() const;
  
  // --------------------- put cut functions here ---------------------------------
  
  virtual int GetGoodRecoil() const; // implement Cheryl's cut
  
  virtual int GetTruthIsCC() const;
  
  // helper function
  bool passTrueCCQELike(bool neutrinoMode, std::vector<int> mc_FSPartPDG, std::vector<double> mc_FSPartE, int mc_nFSPart, double proton_KECut) const;
  
  virtual int GetTruthIsCCQELike() const;  // cut hardwired for now
  
  // all CCQElike without proton cut enabled
  
  virtual int GetTruthIsCCQELikeAll() const;  // cut hardwired for now
  
  // ----------------------- Sean Neutrino Functions ------------------------------------------
  
  virtual int GetTruthIsOther() const;
  
  // Interaction Vertex
  
  virtual int GetHasInteractionVertex() const;
  
  // Isolated Blobs and Charged Pions
  
  virtual int GetNBlobs() const;
  virtual int GetTruthHasSingleChargedPion() const;
  
  // Michel Electrons and Neutral Pions
  
  virtual int GetMichelElectronCandidates() const;
  virtual int GetHasMichelElectron() const;
  virtual int GetTruthHasMichel() const;
  virtual int GetTruthHasSingleNeutralPion() const;
  
  // Michel+Blobs and MultiPion
  
  virtual int GetTruthHasMultiPion() const;
  virtual double GetSingleProtonScore() const;
  virtual int GetIsSingleProton() const;
  virtual int GetTruthHasSingleProton() const;
  virtual int GetAllExtraTracksProtons() const;
  
  // GENIE Particle Counts
  
  virtual int GetTrueChargedPionCount() const;
  virtual int GetTrueNeutralPionCount() const;
  virtual int GetTruePionCount() const;
  virtual int GetTrueProtonCount() const;
  virtual int GetTrueLightMesonCount() const;
  virtual int GetTrueCharmedMesonCount() const;
  virtual int GetTrueStrangeMesonCount() const;
  virtual int GetTrueCharmedBaryonCount() const;
  virtual int GetTrueStrangeBaryonCount() const;
  
  virtual int GetEventRecordTrueEtaCount() const;  
  
};
#endif
