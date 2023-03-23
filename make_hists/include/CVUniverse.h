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
* The main universe class, it inherits from MinervaUniverse which implements most of the variations
* one addition is units of GeV and degrees where the base classes use MeV and radians


// ========================================================================
// Base class for an un-systematically shifted (i.e. CV) universe.
// Implement "Get" functions for all the quantities that you need for your
// analysis.
//
//
// your "Get" functions the way you want them. In that case, you  don't need to
// re-write them here.
// ========================================================================
 */
#ifndef CVUNIVERSE_H
#define CVUNIVERSE_H

#include <iostream>
#include "utils/NuConfig.h"

#include "PlotUtils/ChainWrapper.h"
#include "PlotUtils/MinervaUniverse.h"
#include "PlotUtils/PhysicsVariables.h"
#include "TVector3.h"
#include "PlotUtils/GeantHadronSystematics.h"

class CVUniverse : public PlotUtils::MinervaUniverse {
protected:
	// default values
	static int m_analysis_neutrino_pdg;
	static double m_min_blob_zvtx;
	static double m_photon_energy_cut;
	static double m_proton_ke_cut;
	static NuConfig m_proton_score_config;
	static std::vector<double> m_proton_score_Q2QEs;
	static std::vector<double> m_proton_score_mins;

	// initially set to false
	static bool _is_analysis_neutrino_pdg_set;
	static bool _is_min_blob_zvtx_set;
	static bool _is_photon_energy_cut_set;
	static bool _is_proton_ke_cut_set;
	static bool _is_proton_score_config_set;

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

	static std::map<std::string, int> GetEventParticleCounts();

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

	virtual double GetEventID() const;
	virtual int GetMultiplicity() const;
	virtual int GetDeadTime() const;

	// ----------------------- Cut-configuring Functions -------------------------

	static int GetAnalysisNeutrinoPDG();
	static bool SetAnalysisNeutrinoPDG(int neutrino_pdg, bool print);	

	static double GetMinBlobZVtx();
	static bool SetMinBlobZVtx(double min_zvtx, bool print);

	static double GetPhotonEnergyCut();
	static bool SetPhotonEnergyCut(double energy, bool print);

	static double GetProtonKECut();
	static bool SetProtonKECut(double proton_KECut, bool print);

	static NuConfig GetProtonScoreConfig(bool print);
	static bool SetProtonScoreConfig(NuConfig protonScoreConfig, bool print);

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
	
	virtual double GetThetaXmuDegrees() const;
	virtual double GetTrueThetaXmuDegrees() const;

	virtual double GetThetaYmuDegrees() const;
	virtual double GetTrueThetaYmuDegrees() const;


	// ----------------------------- Hadron Variables ----------------------------

	virtual double GetHadronEGeV() const;

	// ----------------------------- Recoil Variables ----------------------------


	virtual double GetCalRecoilEnergy() const;
	virtual double GetCalRecoilEnergyGeV() const;

	virtual double GetNonCalRecoilEnergy() const;
	virtual double GetNonCalRecoilEnergyGeV() const;

	virtual double GetRecoilEnergyGeV() const;
	virtual double GetTrueRecoilEnergyGeV() const;

	virtual double GetLog10RecoilEnergyGeV() const;
	virtual double GetTrueLog10RecoilEnergyGeV() const;

	virtual double GetTrueQ0GeV() const;
	virtual double GetTrueQ3GeV() const;
	virtual double GetTrueQ2GeV() const;


	// ----------------------------- Other Variables -----------------------------

	//  virtual double GetWgenie() const { return GetDouble("mc_w"); }
	virtual int GetIntType() const;
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

	virtual int GetTruthIsQELike() const;

	// ----------------------- Sean Neutrino Functions ------------------------------------------


	// Interaction Vertex

	virtual int GetHasInteractionVertex() const;

	// Isolated Blobs

	virtual int GetNBlobs() const;

	// Michel Electrons

	virtual int GetNMichel() const;
	virtual std::vector<int> GetMichelVertexType() const;
	virtual int GetImprovedNMichel() const;
	virtual std::vector<int> GetImprovedMichelMatch() const;
	virtual int GetFittedNMichel() const;
	virtual std::vector<int> GetFittedMichelFitPass() const;
	virtual int GetHasMichelElectron() const;
	virtual int GetHasImprovedMichelElectron() const;
	virtual int GetTrueFittedNMichel() const;
	virtual int GetTruthHasMichel() const;
	virtual int GetTruthHasImprovedMichel() const;

	// Both

	virtual int GetHasMichelOrNBlobs() const;

	// Charged and Neutral Pions

	virtual int GetTruthCCQELikeExceptForChargedPions() const;
	virtual int GetTruthHasSingleChargedPion() const;
	virtual int GetTruthHasSingleNeutralPion() const;
	virtual int GetTruthHasMultiPion() const;
	virtual double GetPionScore() const;
	virtual double GetPionScore1() const;
	virtual double GetPionScore2() const;

	// Proton Score, Primary and Secondary Proton Tracks

	virtual int GetNumberOfProtonCandidates() const;

	virtual double GetProtonScore(int i) const;
	virtual double GetProtonScore1(int i) const;
	virtual double GetProtonScore_0() const;
	virtual double GetProtonScore_1() const;
	virtual double GetProtonScore_2() const;
	virtual double GetProtonScore_3() const;
	virtual double GetProtonScore_4() const;
	virtual double GetProtonScore_5() const;
	virtual double GetProtonScore_6() const;
	virtual double GetProtonScore_7() const;
	virtual double GetProtonScore_8() const;
	virtual double GetProtonScore_9() const;

	virtual int GetPassProtonScoreCut(double score, double tree_Q2) const;
	virtual int GetPassScoreCutProton_0() const;
	virtual int GetPassScoreCutProton_1() const;
	virtual int GetPassScoreCutProton_2() const;
	virtual int GetPassScoreCutProton_3() const;
	virtual int GetPassScoreCutProton_4() const;
	virtual int GetPassScoreCutProton_5() const;
	virtual int GetPassScoreCutProton_6() const;
	virtual int GetPassScoreCutProton_7() const;
	virtual int GetPassScoreCutProton_8() const;
	virtual int GetPassScoreCutProton_9() const;

	virtual int GetSecondaryProtonCandidateCount() const;
	virtual int GetSecondaryProtonCandidateCount1() const;

	virtual double GetPrimaryProtonScore() const;
	virtual double GetPrimaryProtonScore1() const;
	virtual double GetPrimaryProtonScore2() const;

	virtual int GetAreClustsFoundAtPrimaryProtonEnd() const;
	
	virtual int GetNumClustsProtonEnd(int i) const;
	virtual int GetNumClustsPrimaryProtonEnd() const;
	virtual int GetNumClustsSecProtonEnd_1() const;
	virtual int GetNumClustsSecProtonEnd_2() const;
	virtual int GetNumClustsSecProtonEnd_3() const;
	virtual int GetNumClustsSecProtonEnd_4() const;
	virtual int GetNumClustsSecProtonEnd_5() const;
	virtual int GetNumClustsSecProtonEnd_6() const;

	virtual double GetPrimaryProtonTrackLength() const;
	virtual double GetPrimaryProtonTrackEndX() const;
	virtual double GetPrimaryProtonTrackEndY() const;
	virtual double GetPrimaryProtonTrackEndZ() const;
	
	virtual double GetProtonAngle(int i) const;
	virtual double GetPrimaryProtonAngle() const;
	virtual double GetSecProtonAngle_1() const;
	virtual double GetSecProtonAngle_2() const;
	virtual double GetSecProtonAngle_3() const;
	virtual double GetSecProtonAngle_4() const;
	virtual double GetSecProtonAngle_5() const;
	virtual double GetSecProtonAngle_6() const;
	
	virtual double GetProtonTrackVtxGap(int i) const;
	virtual double GetPrimaryProtonTrackVtxGap() const;
	virtual double GetSecProtonTrackVtxGap_1() const;
	virtual double GetSecProtonTrackVtxGap_2() const;
	virtual double GetSecProtonTrackVtxGap_3() const;
	virtual double GetSecProtonTrackVtxGap_4() const;
	virtual double GetSecProtonTrackVtxGap_5() const;
	virtual double GetSecProtonTrackVtxGap_6() const;

	virtual double GetCalibEClustsProtonEnd(int i) const;
	virtual double GetCalibEClustsPrimaryProtonEnd() const;
	virtual double GetCalibEClustsSecProtonEnd_1() const;
	virtual double GetCalibEClustsSecProtonEnd_2() const;
	virtual double GetCalibEClustsSecProtonEnd_3() const;
	virtual double GetCalibEClustsSecProtonEnd_4() const;
	virtual double GetCalibEClustsSecProtonEnd_5() const;
	virtual double GetCalibEClustsSecProtonEnd_6() const;
	
	virtual double GetVisEClustsProtonEnd(int i) const;
	virtual double GetVisEClustsPrimaryProtonEnd() const;
	virtual double GetVisEClustsSecProtonEnd_1() const;
	virtual double GetVisEClustsSecProtonEnd_2() const;
	virtual double GetVisEClustsSecProtonEnd_3() const;
	virtual double GetVisEClustsSecProtonEnd_4() const;
	virtual double GetVisEClustsSecProtonEnd_5() const;
	virtual double GetVisEClustsSecProtonEnd_6() const;
	
	virtual double GetPrimaryProtonTfromdEdx() const;
	virtual double GetSecProtonTfromdEdx(int i) const;
	virtual double GetSecProtonTfromdEdx_1() const;
	virtual double GetSecProtonTfromdEdx_2() const;
	virtual double GetSecProtonTfromdEdx_3() const;
	virtual double GetSecProtonTfromdEdx_4() const;
	virtual double GetSecProtonTfromdEdx_5() const;
	virtual double GetSecProtonTfromdEdx_6() const;
	
	virtual double GetTotalProtonEnergy(int i) const;
	virtual double GetTotalPrimaryProtonEnergy() const;
	virtual double GetTotalSecProtonEnergy_1() const;
	virtual double GetTotalSecProtonEnergy_2() const;
	virtual double GetTotalSecProtonEnergy_3() const;
	virtual double GetTotalSecProtonEnergy_4() const;
	virtual double GetTotalSecProtonEnergy_5() const;
	virtual double GetTotalSecProtonEnergy_6() const;
	
	virtual double GetProtonFractionEnergyInCone(int i) const;
	virtual double GetPrimaryProtonFractionEnergyInCone() const;
	virtual double GetSecProtonFractionEnergyInCone_1() const;
	virtual double GetSecProtonFractionEnergyInCone_2() const;
	virtual double GetSecProtonFractionEnergyInCone_3() const;
	virtual double GetSecProtonFractionEnergyInCone_4() const;
	virtual double GetSecProtonFractionEnergyInCone_5() const;
	virtual double GetSecProtonFractionEnergyInCone_6() const;
	
	virtual double GetProtonTrueKE(int i) const;
	virtual double GetPrimaryProtonTrueKE() const;
	virtual double GetSecProtonTrueKE_1() const;
	virtual double GetSecProtonTrueKE_2() const;
	virtual double GetSecProtonTrueKE_3() const;
	virtual double GetSecProtonTrueKE_4() const;
	virtual double GetSecProtonTrueKE_5() const;
	virtual double GetSecProtonTrueKE_6() const;
	
	virtual int GetProtonCandidatePDG(int i) const;
	virtual int GetPrimaryProtonCandidatePDG() const;
	virtual int GetSecProtonCandidatePDG_1() const;
	virtual int GetSecProtonCandidatePDG_2() const;
	virtual int GetSecProtonCandidatePDG_3() const;
	virtual int GetSecProtonCandidatePDG_4() const;
	virtual int GetSecProtonCandidatePDG_5() const;
	virtual int GetSecProtonCandidatePDG_6() const;
	
	virtual double GetEnergyDiffTruedEdx() const;

	virtual int GetRecoTruthIsPrimaryProton() const;
	virtual int GetRecoTruthIsPrimaryPion() const;
	virtual int GetRecoTruthIsPrimaryOther() const;    

	virtual int GetIsPrimaryProton() const;
	virtual int GetIsPrimaryProton1() const;
	virtual int GetTruthHasSingleProton() const;

	virtual int GetPassAllProtonScoreCuts(std::vector<double> scores, double tree_Q2) const;
	virtual int GetAllExtraTracksProtons() const;
	virtual int GetAllExtraTracksProtons1() const;
	virtual int GetProtonCount() const;
	virtual int GetProtonCount1() const;

	// GENIE Particle Counts

	virtual int GetTrueNumberOfFSParticles() const;
	virtual int GetTrueChargedPionCount() const;
	virtual int GetTrueNeutralPionCount() const;
	virtual int GetTruePionCount() const;
	virtual int GetTrueProtonCount() const;
	virtual int GetTrueLightMesonCount() const;
	virtual int GetTrueCharmedMesonCount() const;
	virtual int GetTrueStrangeMesonCount() const;
	virtual int GetTrueCharmedBaryonCount() const;
	virtual int GetTrueStrangeBaryonCount() const;
	virtual int GetTrueNeutronCount() const;
	virtual int GetTrueNegMuonCount() const;
	virtual int GetTrueGammaCount() const;
	
	virtual std::map<int,int> GetTrueFSCountsPerPDG() const;

	//

	virtual int GetEventRecordTrueEtaCount() const;
	virtual int GetMCTargetA() const; 
	virtual int GetMCTargetZ() const;
	virtual int GetMCTargetNucleon() const;
	virtual int Dummy() const;

	// Arachne

	virtual void PrintTrueArachneLink() const;
	virtual void PrintDataArachneLink() const;
	virtual std::string StringTrueArachneLink() const;
	virtual std::string StringDataArachneLink() const;

	//

	virtual void Print() const;

};
#endif
