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
 * This implements a map of CVFunctions so you can configure them at run time
 */
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
class CVFunctions
{

	typedef std::function<double(const CVUNIVERSE &)> PointerToCVUniverseFunction;
	typedef std::function<int(const CVUNIVERSE &)> PointerToCVUniverseIntFunction;
	std::map<const std::string, PointerToCVUniverseFunction> recofunctions;
	std::map<const std::string, PointerToCVUniverseFunction> truefunctions;
	std::map<const std::string, PointerToCVUniverseIntFunction> recointfunctions;
	std::map<const std::string, PointerToCVUniverseIntFunction> trueintfunctions;

public:
	CVFunctions()
	{
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

		recofunctions["EmuGeV"] = &CVUNIVERSE::GetEmuGeV;
		truefunctions["TrueEmuGeV"] = &CVUNIVERSE::GetTrueEmuGeV;

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

		recofunctions["ThetaXmuDegrees"] = &CVUNIVERSE::GetThetaXmuDegrees;
		truefunctions["TrueThetaXmuDegrees"] = &CVUNIVERSE::GetTrueThetaXmuDegrees;

		recofunctions["ThetaYmuDegrees"] = &CVUNIVERSE::GetThetaYmuDegrees;
		truefunctions["TrueThetaYmuDegrees"] = &CVUNIVERSE::GetTrueThetaYmuDegrees;

		recofunctions["Thetamu"] = &CVUNIVERSE::GetThetamu;
		truefunctions["TrueThetamu"] = &CVUNIVERSE::GetTrueThetamu;

		recofunctions["ThetaXmu"] = &CVUNIVERSE::GetThetaXmu;
		truefunctions["TrueThetaXmu"] = &CVUNIVERSE::GetTrueThetaXmu;

		recofunctions["ThetaYmu"] = &CVUNIVERSE::GetThetaYmu;
		truefunctions["TrueThetaYmu"] = &CVUNIVERSE::GetTrueThetaYmu;

		recofunctions["DeadTime"] = &CVUNIVERSE::GetDeadTime;

		recofunctions["Multiplicity"] = &CVUNIVERSE::GetMultiplicity;
		recointfunctions["Multiplicity"] = &CVUNIVERSE::GetMultiplicity;

		recofunctions["EventID"] = &CVUNIVERSE::GetEventID;
		truefunctions["EventID"] = &CVUNIVERSE::GetEventID;

		// truth only variables for studies

		truefunctions["MCTargetA"] = &CVUNIVERSE::GetMCTargetA;

		truefunctions["MCTargetZ"] = &CVUNIVERSE::GetMCTargetZ;

		truefunctions["MCTargetNucleon"] = &CVUNIVERSE::GetMCTargetNucleon;

		recofunctions["MCTargetA"] = &CVUNIVERSE::GetMCTargetA;

		recofunctions["MCTargetZ"] = &CVUNIVERSE::GetMCTargetZ;

		recofunctions["MCTargetNucleon"] = &CVUNIVERSE::GetMCTargetNucleon;

		recofunctions["Dummy"] = &CVUNIVERSE::Dummy;

		truefunctions["Dummy"] = &CVUNIVERSE::Dummy;

		// integer functions for equals

		recointfunctions["IsMinosMatchTrack"] = &CVUNIVERSE::GetIsMinosMatchTrack;

		recointfunctions["NuHelicity"] = &CVUNIVERSE::GetNuHelicity;

		recointfunctions["GoodRecoil"] = &CVUNIVERSE::GetGoodRecoil;

		trueintfunctions["TruthIsCCQELike"] = &CVUNIVERSE::GetTruthIsCCQELike;
		truefunctions["TruthIsCCQELike"] = &CVUNIVERSE::GetTruthIsCCQELike;
		trueintfunctions["TruthIsCCQELikeAll"] = &CVUNIVERSE::GetTruthIsCCQELikeAll;
		
		trueintfunctions["TruthIsCCQELike_old"] = &CVUNIVERSE::GetTruthIsCCQELike_old;
		trueintfunctions["TruthIs1ChargedPion_old"] = &CVUNIVERSE::GetTruthIs1ChargedPion_old;
		trueintfunctions["TruthIs1NeutralPion_old"] = &CVUNIVERSE::GetTruthIs1NeutralPion_old;
		trueintfunctions["TruthIsMultiPion_old"] = &CVUNIVERSE::GetTruthIsMultiPion_old;
		trueintfunctions["TruthIsOther_old"] = &CVUNIVERSE::GetTruthIsOther_old;
		
		trueintfunctions["TruthIsCCQELike_new"] = &CVUNIVERSE::GetTruthIsCCQELike_new;
		trueintfunctions["TruthIs1ChargedPion_new"] = &CVUNIVERSE::GetTruthIs1ChargedPion_new;
		trueintfunctions["TruthIs1NeutralPion_new"] = &CVUNIVERSE::GetTruthIs1NeutralPion_new;
		trueintfunctions["TruthIsMultiPion_new"] = &CVUNIVERSE::GetTruthIsMultiPion_new;

		trueintfunctions["TruthIsCC"] = &CVUNIVERSE::GetTruthIsCC;

		trueintfunctions["TruthNuPDG"] = &CVUNIVERSE::GetTruthNuPDG;

		trueintfunctions["TruthIsQELike"] = &CVUNIVERSE::GetTruthIsQELike;

		trueintfunctions["MCIntType"] = &CVUNIVERSE::GetMCIntType;
		truefunctions["MCIntType"] = &CVUNIVERSE::GetMCIntType;
		recointfunctions["MCIntType"] = &CVUNIVERSE::GetMCIntType;
		recofunctions["MCIntType"] = &CVUNIVERSE::GetMCIntType;
		recointfunctions["IntType"] = &CVUNIVERSE::GetIntType;
		recofunctions["IntType"] = &CVUNIVERSE::GetIntType;

		trueintfunctions["MCTargetA"] = &CVUNIVERSE::GetMCTargetA;

		trueintfunctions["MCTargetZ"] = &CVUNIVERSE::GetMCTargetZ;

		trueintfunctions["MCTargetNucleon"] = &CVUNIVERSE::GetMCTargetNucleon;

		recointfunctions["MCTargetA"] = &CVUNIVERSE::GetMCTargetA;

		recointfunctions["MCTargetZ"] = &CVUNIVERSE::GetMCTargetZ;

		recointfunctions["MCTargetNucleon"] = &CVUNIVERSE::GetMCTargetNucleon;

		recointfunctions["Dummy"] = &CVUNIVERSE::Dummy;
		trueintfunctions["Dummy"] = &CVUNIVERSE::Dummy;

		// ----------------------- Sean Neutrino Functions ------------------------------------------

		recointfunctions["MissingTrackCount"] = &CVUNIVERSE::GetMissingTrackCount;
		recofunctions["MissingTrackCount"] = &CVUNIVERSE::GetMissingTrackCount;

		// Interaction Vertex

		recointfunctions["HasInteractionVertex"] = &CVUNIVERSE::GetHasInteractionVertex;

		// Isolated Blobs

		recofunctions["NBlobs"] = &CVUNIVERSE::GetNBlobs;
		
		recofunctions["BlobDistance0"] = &CVUNIVERSE::GetBlobDistance0;
		recofunctions["BlobDistance1"] = &CVUNIVERSE::GetBlobDistance1;
		recofunctions["BlobDistance2"] = &CVUNIVERSE::GetBlobDistance2;
		recofunctions["BlobDistance3"] = &CVUNIVERSE::GetBlobDistance3;
		recofunctions["BlobDistance4"] = &CVUNIVERSE::GetBlobDistance4;

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
		
		recointfunctions["ImprovedMichel_0_Views"] = &CVUNIVERSE::GetImprovedMichel_0_Views;
		recofunctions["ImprovedMichel_0_Views"] = &CVUNIVERSE::GetImprovedMichel_0_Views;
		recointfunctions["ImprovedMichel_1_Views"] = &CVUNIVERSE::GetImprovedMichel_1_Views;
		recofunctions["ImprovedMichel_1_Views"] = &CVUNIVERSE::GetImprovedMichel_1_Views;
		recointfunctions["ImprovedMichel_2_Views"] = &CVUNIVERSE::GetImprovedMichel_2_Views;
		recofunctions["ImprovedMichel_2_Views"] = &CVUNIVERSE::GetImprovedMichel_2_Views;
		recointfunctions["ImprovedMichel_Sum_Views"] = &CVUNIVERSE::GetImprovedMichel_Sum_Views;
		recofunctions["ImprovedMichel_Sum_Views"] = &CVUNIVERSE::GetImprovedMichel_Sum_Views;
		recofunctions["ImprovedMichel_Avg_Views"] = &CVUNIVERSE::GetImprovedMichel_Avg_Views;
		recointfunctions["MaxImprovedMichelViews"] = &CVUNIVERSE::GetMaxImprovedMichelViews;
		recofunctions["MaxImprovedMichelViews"] = &CVUNIVERSE::GetMaxImprovedMichelViews;

		// Both

		recointfunctions["HasMichelOrNBlobs"] = &CVUNIVERSE::GetHasMichelOrNBlobs;

		// Protons

		recointfunctions["NumberOfProtonCandidates"] = &CVUNIVERSE::GetNumberOfProtonCandidates;
		recofunctions["NumberOfProtonCandidates"] = &CVUNIVERSE::GetNumberOfProtonCandidates;
		
		recofunctions["MinProtonScore1"] = &CVUNIVERSE::GetMinProtonScore1;

		recofunctions["PrimaryProtonScore"] = &CVUNIVERSE::GetProtonScore_0;
		recofunctions["SecProtonScore_1"] = &CVUNIVERSE::GetProtonScore_1;
		recofunctions["SecProtonScore_2"] = &CVUNIVERSE::GetProtonScore_2;
		recofunctions["SecProtonScore_3"] = &CVUNIVERSE::GetProtonScore_3;
		recofunctions["SecProtonScore_4"] = &CVUNIVERSE::GetProtonScore_4;
		recofunctions["SecProtonScore_5"] = &CVUNIVERSE::GetProtonScore_5;
		recofunctions["SecProtonScore_6"] = &CVUNIVERSE::GetProtonScore_6;
		recofunctions["SecProtonScore_7"] = &CVUNIVERSE::GetProtonScore_7;
		recofunctions["SecProtonScore_8"] = &CVUNIVERSE::GetProtonScore_8;
		recofunctions["SecProtonScore_9"] = &CVUNIVERSE::GetProtonScore_9;
		
		recofunctions["PrimaryProtonScore1"] = &CVUNIVERSE::GetProtonScore1_0;
		recofunctions["SecProtonScore1_1"] = &CVUNIVERSE::GetProtonScore1_1;
		recofunctions["SecProtonScore1_2"] = &CVUNIVERSE::GetProtonScore1_2;
		recofunctions["SecProtonScore1_3"] = &CVUNIVERSE::GetProtonScore1_3;
		recofunctions["SecProtonScore1_4"] = &CVUNIVERSE::GetProtonScore1_4;
		recofunctions["SecProtonScore1_5"] = &CVUNIVERSE::GetProtonScore1_5;
		recofunctions["SecProtonScore1_6"] = &CVUNIVERSE::GetProtonScore1_6;
		recofunctions["SecProtonScore1_7"] = &CVUNIVERSE::GetProtonScore1_7;
		recofunctions["SecProtonScore1_8"] = &CVUNIVERSE::GetProtonScore1_8;
		recofunctions["SecProtonScore1_9"] = &CVUNIVERSE::GetProtonScore1_9;
		
		recofunctions["PrimaryProtonScore2"] = &CVUNIVERSE::GetProtonScore2_0;
		recofunctions["SecProtonScore2_1"] = &CVUNIVERSE::GetProtonScore2_1;
		recofunctions["SecProtonScore2_2"] = &CVUNIVERSE::GetProtonScore2_2;
		recofunctions["SecProtonScore2_3"] = &CVUNIVERSE::GetProtonScore2_3;
		recofunctions["SecProtonScore2_4"] = &CVUNIVERSE::GetProtonScore2_4;
		recofunctions["SecProtonScore2_5"] = &CVUNIVERSE::GetProtonScore2_5;
		recofunctions["SecProtonScore2_6"] = &CVUNIVERSE::GetProtonScore2_6;
		recofunctions["SecProtonScore2_7"] = &CVUNIVERSE::GetProtonScore2_7;
		recofunctions["SecProtonScore2_8"] = &CVUNIVERSE::GetProtonScore2_8;
		recofunctions["SecProtonScore2_9"] = &CVUNIVERSE::GetProtonScore2_9;

		recointfunctions["PassScoreCutProton1_0"] = &CVUNIVERSE::GetPassScoreCutProton1_0;
		recointfunctions["PassScoreCutProton1_1"] = &CVUNIVERSE::GetPassScoreCutProton1_1;
		recointfunctions["PassScoreCutProton1_2"] = &CVUNIVERSE::GetPassScoreCutProton1_2;
		recointfunctions["PassScoreCutProton1_3"] = &CVUNIVERSE::GetPassScoreCutProton1_3;
		recointfunctions["PassScoreCutProton1_4"] = &CVUNIVERSE::GetPassScoreCutProton1_4;
		recointfunctions["PassScoreCutProton1_5"] = &CVUNIVERSE::GetPassScoreCutProton1_5;
		recointfunctions["PassScoreCutProton1_6"] = &CVUNIVERSE::GetPassScoreCutProton1_6;
		recointfunctions["PassScoreCutProton1_7"] = &CVUNIVERSE::GetPassScoreCutProton1_7;
		recointfunctions["PassScoreCutProton1_8"] = &CVUNIVERSE::GetPassScoreCutProton1_8;
		recointfunctions["PassScoreCutProton1_9"] = &CVUNIVERSE::GetPassScoreCutProton1_9;

		recointfunctions["IsPrimaryProton"] = &CVUNIVERSE::GetIsPrimaryProton;
		recointfunctions["IsPrimaryProton1"] = &CVUNIVERSE::GetIsPrimaryProton1;

		recointfunctions["AreClustsFoundAtPrimaryProtonEnd"] = &CVUNIVERSE::GetAreClustsFoundAtPrimaryProtonEnd;
		recofunctions["AreClustsFoundAtPrimaryProtonEnd"] = &CVUNIVERSE::GetAreClustsFoundAtPrimaryProtonEnd;

		recointfunctions["NumClustsPrimaryProtonEnd"] = &CVUNIVERSE::GetNumClustsPrimaryProtonEnd;
		recofunctions["NumClustsPrimaryProtonEnd"] = &CVUNIVERSE::GetNumClustsPrimaryProtonEnd;
		recointfunctions["NumClustsSecProtonEnd_1"] = &CVUNIVERSE::GetNumClustsSecProtonEnd_1;
		recofunctions["NumClustsSecProtonEnd_1"] = &CVUNIVERSE::GetNumClustsSecProtonEnd_1;
		recointfunctions["NumClustsSecProtonEnd_2"] = &CVUNIVERSE::GetNumClustsSecProtonEnd_2;
		recofunctions["NumClustsSecProtonEnd_2"] = &CVUNIVERSE::GetNumClustsSecProtonEnd_2;
		recointfunctions["NumClustsSecProtonEnd_3"] = &CVUNIVERSE::GetNumClustsSecProtonEnd_3;
		recofunctions["NumClustsSecProtonEnd_3"] = &CVUNIVERSE::GetNumClustsSecProtonEnd_3;
		recointfunctions["NumClustsSecProtonEnd_4"] = &CVUNIVERSE::GetNumClustsSecProtonEnd_4;
		recofunctions["NumClustsSecProtonEnd_4"] = &CVUNIVERSE::GetNumClustsSecProtonEnd_4;
		recointfunctions["NumClustsSecProtonEnd_5"] = &CVUNIVERSE::GetNumClustsSecProtonEnd_5;
		recofunctions["NumClustsSecProtonEnd_5"] = &CVUNIVERSE::GetNumClustsSecProtonEnd_5;
		recointfunctions["NumClustsSecProtonEnd_6"] = &CVUNIVERSE::GetNumClustsSecProtonEnd_6;
		recofunctions["NumClustsSecProtonEnd_6"] = &CVUNIVERSE::GetNumClustsSecProtonEnd_6;

		recofunctions["PrimaryProtonTrackLength"] = &CVUNIVERSE::GetPrimaryProtonTrackLength;
		recofunctions["PrimaryProtonTrackEndX"] = &CVUNIVERSE::GetPrimaryProtonTrackEndX;
		recofunctions["PrimaryProtonTrackEndY"] = &CVUNIVERSE::GetPrimaryProtonTrackEndY;
		recofunctions["PrimaryProtonTrackEndZ"] = &CVUNIVERSE::GetPrimaryProtonTrackEndZ;
		
		recofunctions["ProtonCandTrackLength_0"] = &CVUNIVERSE::GetProtonCandTrackLength_0;
		recofunctions["ProtonCandTrackLength_1"] = &CVUNIVERSE::GetProtonCandTrackLength_1;
		recofunctions["ProtonCandTrackLength_2"] = &CVUNIVERSE::GetProtonCandTrackLength_2;
		recofunctions["ProtonCandTrackLength_3"] = &CVUNIVERSE::GetProtonCandTrackLength_3;
		recofunctions["ProtonCandTrackLength_4"] = &CVUNIVERSE::GetProtonCandTrackLength_4;
		recofunctions["ProtonCandTrackLength_5"] = &CVUNIVERSE::GetProtonCandTrackLength_5;
		recofunctions["ProtonCandTrackLength_6"] = &CVUNIVERSE::GetProtonCandTrackLength_6;

		recofunctions["PrimaryProtonAngle"] = &CVUNIVERSE::GetPrimaryProtonAngle;
		recofunctions["SecProtonAngle_1"] = &CVUNIVERSE::GetSecProtonAngle_1;
		recofunctions["SecProtonAngle_2"] = &CVUNIVERSE::GetSecProtonAngle_2;
		recofunctions["SecProtonAngle_3"] = &CVUNIVERSE::GetSecProtonAngle_3;
		recofunctions["SecProtonAngle_4"] = &CVUNIVERSE::GetSecProtonAngle_4;
		recofunctions["SecProtonAngle_5"] = &CVUNIVERSE::GetSecProtonAngle_5;
		recofunctions["SecProtonAngle_6"] = &CVUNIVERSE::GetSecProtonAngle_6;
		
		recofunctions["ThetaProton0"] = &CVUNIVERSE::GetThetaProton0;
		recofunctions["ThetaProton1"] = &CVUNIVERSE::GetThetaProton1;
		recofunctions["ThetaProton2"] = &CVUNIVERSE::GetThetaProton2;
		recofunctions["ThetaProton3"] = &CVUNIVERSE::GetThetaProton3;
		recofunctions["ThetaProton4"] = &CVUNIVERSE::GetThetaProton4;
		recofunctions["ThetaProton5"] = &CVUNIVERSE::GetThetaProton5;
		recofunctions["ThetaProton6"] = &CVUNIVERSE::GetThetaProton6;
		
		recofunctions["MuonToPrimaryProtonAngle"] = &CVUNIVERSE::GetMuonToPrimaryProtonAngle;
		
		recofunctions["PperpProtonGeV0"] = &CVUNIVERSE::GetPperpProtonGeV0;
		recofunctions["PperpProtonGeV1"] = &CVUNIVERSE::GetPperpProtonGeV1;
		recofunctions["PperpProtonGeV2"] = &CVUNIVERSE::GetPperpProtonGeV2;
		recofunctions["PperpProtonGeV3"] = &CVUNIVERSE::GetPperpProtonGeV3;
		recofunctions["PperpProtonGeV4"] = &CVUNIVERSE::GetPperpProtonGeV4;
		recofunctions["PperpProtonGeV5"] = &CVUNIVERSE::GetPperpProtonGeV5;
		recofunctions["PperpProtonGeV6"] = &CVUNIVERSE::GetPperpProtonGeV6;
		
		recofunctions["PtImbalance"] = &CVUNIVERSE::GetPtImbalance;
		recofunctions["PtImbalanceGeV"] = &CVUNIVERSE::GetPtImbalanceGeV;

		recofunctions["PrimaryProtonTrackVtxGap"] = &CVUNIVERSE::GetPrimaryProtonTrackVtxGap;
		recofunctions["SecProtonTrackVtxGap_1"] = &CVUNIVERSE::GetSecProtonTrackVtxGap_1;
		recofunctions["SecProtonTrackVtxGap_2"] = &CVUNIVERSE::GetSecProtonTrackVtxGap_2;
		recofunctions["SecProtonTrackVtxGap_3"] = &CVUNIVERSE::GetSecProtonTrackVtxGap_3;
		recofunctions["SecProtonTrackVtxGap_4"] = &CVUNIVERSE::GetSecProtonTrackVtxGap_4;
		recofunctions["SecProtonTrackVtxGap_5"] = &CVUNIVERSE::GetSecProtonTrackVtxGap_5;
		recofunctions["SecProtonTrackVtxGap_6"] = &CVUNIVERSE::GetSecProtonTrackVtxGap_6;
		
		recofunctions["PrimaryProtonTOF"] = &CVUNIVERSE::GetPrimaryProtonTOF;

		recofunctions["CalibEClustsPrimaryProtonEnd"] = &CVUNIVERSE::GetCalibEClustsPrimaryProtonEnd;
		recofunctions["CalibEClustsSecProtonEnd_1"] = &CVUNIVERSE::GetCalibEClustsSecProtonEnd_1;
		recofunctions["CalibEClustsSecProtonEnd_2"] = &CVUNIVERSE::GetCalibEClustsSecProtonEnd_2;
		recofunctions["CalibEClustsSecProtonEnd_3"] = &CVUNIVERSE::GetCalibEClustsSecProtonEnd_3;
		recofunctions["CalibEClustsSecProtonEnd_4"] = &CVUNIVERSE::GetCalibEClustsSecProtonEnd_4;
		recofunctions["CalibEClustsSecProtonEnd_5"] = &CVUNIVERSE::GetCalibEClustsSecProtonEnd_5;
		recofunctions["CalibEClustsSecProtonEnd_6"] = &CVUNIVERSE::GetCalibEClustsSecProtonEnd_6;

		recofunctions["VisEClustsPrimaryProtonEnd"] = &CVUNIVERSE::GetVisEClustsPrimaryProtonEnd;
		recofunctions["VisEClustsSecProtonEnd_1"] = &CVUNIVERSE::GetVisEClustsSecProtonEnd_1;
		recofunctions["VisEClustsSecProtonEnd_2"] = &CVUNIVERSE::GetVisEClustsSecProtonEnd_2;
		recofunctions["VisEClustsSecProtonEnd_3"] = &CVUNIVERSE::GetVisEClustsSecProtonEnd_3;
		recofunctions["VisEClustsSecProtonEnd_4"] = &CVUNIVERSE::GetVisEClustsSecProtonEnd_4;
		recofunctions["VisEClustsSecProtonEnd_5"] = &CVUNIVERSE::GetVisEClustsSecProtonEnd_5;
		recofunctions["VisEClustsSecProtonEnd_6"] = &CVUNIVERSE::GetVisEClustsSecProtonEnd_6;

		recofunctions["PrimaryProtonTfromdEdx"] = &CVUNIVERSE::GetPrimaryProtonTfromdEdx;
		recofunctions["SecProtonTfromdEdx_1"] = &CVUNIVERSE::GetSecProtonTfromdEdx_1;
		recofunctions["SecProtonTfromdEdx_2"] = &CVUNIVERSE::GetSecProtonTfromdEdx_2;
		recofunctions["SecProtonTfromdEdx_3"] = &CVUNIVERSE::GetSecProtonTfromdEdx_3;
		recofunctions["SecProtonTfromdEdx_4"] = &CVUNIVERSE::GetSecProtonTfromdEdx_4;
		recofunctions["SecProtonTfromdEdx_5"] = &CVUNIVERSE::GetSecProtonTfromdEdx_5;
		recofunctions["SecProtonTfromdEdx_6"] = &CVUNIVERSE::GetSecProtonTfromdEdx_6;
		
		recofunctions["ProtonRatioTdEdX2TrackLength_0"] = &CVUNIVERSE::ProtonRatioTdEdX2TrackLength_0;
		recofunctions["ProtonRatioTdEdX2TrackLength_1"] = &CVUNIVERSE::ProtonRatioTdEdX2TrackLength_1;
		recofunctions["ProtonRatioTdEdX2TrackLength_2"] = &CVUNIVERSE::ProtonRatioTdEdX2TrackLength_2;
		recofunctions["ProtonRatioTdEdX2TrackLength_3"] = &CVUNIVERSE::ProtonRatioTdEdX2TrackLength_3;

		recofunctions["TotalPrimaryProtonVisEnergy"] = &CVUNIVERSE::GetTotalPrimaryProtonVisEnergy;
		recofunctions["TotalSecProtonVisEnergy_1"] = &CVUNIVERSE::GetTotalSecProtonVisEnergy_1;
		recofunctions["TotalSecProtonVisEnergy_2"] = &CVUNIVERSE::GetTotalSecProtonVisEnergy_2;
		recofunctions["TotalSecProtonVisEnergy_3"] = &CVUNIVERSE::GetTotalSecProtonVisEnergy_3;
		recofunctions["TotalSecProtonVisEnergy_4"] = &CVUNIVERSE::GetTotalSecProtonVisEnergy_4;
		recofunctions["TotalSecProtonVisEnergy_5"] = &CVUNIVERSE::GetTotalSecProtonVisEnergy_5;
		recofunctions["TotalSecProtonVisEnergy_6"] = &CVUNIVERSE::GetTotalSecProtonVisEnergy_6;

		recofunctions["PrimaryProtonFractionVisEnergyInCone"] = &CVUNIVERSE::GetPrimaryProtonFractionVisEnergyInCone;
		recofunctions["SecProtonFractionVisEnergyInCone_1"] = &CVUNIVERSE::GetSecProtonFractionVisEnergyInCone_1;
		recofunctions["SecProtonFractionVisEnergyInCone_2"] = &CVUNIVERSE::GetSecProtonFractionVisEnergyInCone_2;
		recofunctions["SecProtonFractionVisEnergyInCone_3"] = &CVUNIVERSE::GetSecProtonFractionVisEnergyInCone_3;
		recofunctions["SecProtonFractionVisEnergyInCone_4"] = &CVUNIVERSE::GetSecProtonFractionVisEnergyInCone_4;
		recofunctions["SecProtonFractionVisEnergyInCone_5"] = &CVUNIVERSE::GetSecProtonFractionVisEnergyInCone_5;
		recofunctions["SecProtonFractionVisEnergyInCone_6"] = &CVUNIVERSE::GetSecProtonFractionVisEnergyInCone_6;

		recofunctions["PrimaryProtonTrueKE"] = &CVUNIVERSE::GetPrimaryProtonTrueKE;
		recofunctions["SecProtonTrueKE_1"] = &CVUNIVERSE::GetSecProtonTrueKE_1;
		recofunctions["SecProtonTrueKE_2"] = &CVUNIVERSE::GetSecProtonTrueKE_2;
		recofunctions["SecProtonTrueKE_3"] = &CVUNIVERSE::GetSecProtonTrueKE_3;
		recofunctions["SecProtonTrueKE_4"] = &CVUNIVERSE::GetSecProtonTrueKE_4;
		recofunctions["SecProtonTrueKE_5"] = &CVUNIVERSE::GetSecProtonTrueKE_5;
		recofunctions["SecProtonTrueKE_6"] = &CVUNIVERSE::GetSecProtonTrueKE_6;

		recofunctions["VisEnergyDiffTruedEdx"] = &CVUNIVERSE::GetVisEnergyDiffTruedEdx;

		recointfunctions["PrimaryProtonCandidatePDG"] = &CVUNIVERSE::GetPrimaryProtonCandidatePDG;
		recofunctions["PrimaryProtonCandidatePDG"] = &CVUNIVERSE::GetPrimaryProtonCandidatePDG;
		recointfunctions["SecProtonCandidatePDG_1"] = &CVUNIVERSE::GetSecProtonCandidatePDG_1;
		recofunctions["SecProtonCandidatePDG_1"] = &CVUNIVERSE::GetSecProtonCandidatePDG_1;
		recointfunctions["SecProtonCandidatePDG_2"] = &CVUNIVERSE::GetSecProtonCandidatePDG_2;
		recofunctions["SecProtonCandidatePDG_2"] = &CVUNIVERSE::GetSecProtonCandidatePDG_2;
		recointfunctions["SecProtonCandidatePDG_3"] = &CVUNIVERSE::GetSecProtonCandidatePDG_3;
		recofunctions["SecProtonCandidatePDG_3"] = &CVUNIVERSE::GetSecProtonCandidatePDG_3;
		recointfunctions["SecProtonCandidatePDG_4"] = &CVUNIVERSE::GetSecProtonCandidatePDG_4;
		recofunctions["SecProtonCandidatePDG_4"] = &CVUNIVERSE::GetSecProtonCandidatePDG_4;
		recointfunctions["SecProtonCandidatePDG_5"] = &CVUNIVERSE::GetSecProtonCandidatePDG_5;
		recofunctions["SecProtonCandidatePDG_5"] = &CVUNIVERSE::GetSecProtonCandidatePDG_5;
		recointfunctions["SecProtonCandidatePDG_6"] = &CVUNIVERSE::GetSecProtonCandidatePDG_6;
		recofunctions["SecProtonCandidatePDG_6"] = &CVUNIVERSE::GetSecProtonCandidatePDG_6;
		
		recointfunctions["PrimaryProtonCandidatePDG_abs"] = &CVUNIVERSE::GetPrimaryProtonCandidatePDG_abs;
		recofunctions["PrimaryProtonCandidatePDG_abs"] = &CVUNIVERSE::GetPrimaryProtonCandidatePDG_abs;
		recointfunctions["SecProtonCandidatePDG_abs_1"] = &CVUNIVERSE::GetSecProtonCandidatePDG_abs_1;
		recofunctions["SecProtonCandidatePDG_abs_1"] = &CVUNIVERSE::GetSecProtonCandidatePDG_abs_1;
		recointfunctions["SecProtonCandidatePDG_abs_2"] = &CVUNIVERSE::GetSecProtonCandidatePDG_abs_2;
		recofunctions["SecProtonCandidatePDG_abs_2"] = &CVUNIVERSE::GetSecProtonCandidatePDG_abs_2;
		recointfunctions["SecProtonCandidatePDG_abs_3"] = &CVUNIVERSE::GetSecProtonCandidatePDG_abs_3;
		recofunctions["SecProtonCandidatePDG_abs_3"] = &CVUNIVERSE::GetSecProtonCandidatePDG_abs_3;
		recointfunctions["SecProtonCandidatePDG_abs_4"] = &CVUNIVERSE::GetSecProtonCandidatePDG_abs_4;
		recofunctions["SecProtonCandidatePDG_abs_4"] = &CVUNIVERSE::GetSecProtonCandidatePDG_abs_4;
		recointfunctions["SecProtonCandidatePDG_abs_5"] = &CVUNIVERSE::GetSecProtonCandidatePDG_abs_5;
		recofunctions["SecProtonCandidatePDG_abs_5"] = &CVUNIVERSE::GetSecProtonCandidatePDG_abs_5;
		recointfunctions["SecProtonCandidatePDG_abs_6"] = &CVUNIVERSE::GetSecProtonCandidatePDG_abs_6;
		recofunctions["SecProtonCandidatePDG_abs_6"] = &CVUNIVERSE::GetSecProtonCandidatePDG_abs_6;

		recointfunctions["RecoTruthIsPrimaryProton"] = &CVUNIVERSE::GetRecoTruthIsPrimaryProton;
		recointfunctions["RecoTruthIsPrimaryPion"] = &CVUNIVERSE::GetRecoTruthIsPrimaryPion;
		recointfunctions["RecoTruthIsPrimaryOther"] = &CVUNIVERSE::GetRecoTruthIsPrimaryOther;

		recofunctions["MaxProtonTrueKE"] = &CVUNIVERSE::GetMaxProtonTrueKE;
		truefunctions["MaxProtonTrueKE"] = &CVUNIVERSE::GetMaxProtonTrueKE;
		truefunctions["PrimaryProtonTrueKE"] = &CVUNIVERSE::GetPrimaryProtonTrueKE;

		trueintfunctions["TruthHasSingleProton"] = &CVUNIVERSE::GetTruthHasSingleProton;
		truefunctions["TruthHasSingleProton"] = &CVUNIVERSE::GetTruthHasSingleProton;

		recointfunctions["SecondaryProtonCandidateCount"] = &CVUNIVERSE::GetSecondaryProtonCandidateCount;
		recofunctions["SecondaryProtonCandidateCount"] = &CVUNIVERSE::GetSecondaryProtonCandidateCount;
		recointfunctions["SecondaryProtonCandidateCount1"] = &CVUNIVERSE::GetSecondaryProtonCandidateCount1;
		recofunctions["SecondaryProtonCandidateCount1"] = &CVUNIVERSE::GetSecondaryProtonCandidateCount1;
		recointfunctions["AllExtraTracksProtons"] = &CVUNIVERSE::GetAllExtraTracksProtons;
		recointfunctions["AllExtraTracksProtons1"] = &CVUNIVERSE::GetAllExtraTracksProtons1;

		recointfunctions["ProtonCount"] = &CVUNIVERSE::GetProtonCount;
		recofunctions["ProtonCount"] = &CVUNIVERSE::GetProtonCount;
		recointfunctions["ProtonCount1"] = &CVUNIVERSE::GetProtonCount1;
		recofunctions["ProtonCount1"] = &CVUNIVERSE::GetProtonCount1;

		// Pions

		recofunctions["PionScore"] = &CVUNIVERSE::GetPionScore;
		recofunctions["PionScore1"] = &CVUNIVERSE::GetPionScore1;
		recofunctions["PionScore2"] = &CVUNIVERSE::GetPionScore2;

		// Genie Particle Counts

		trueintfunctions["TrueFSPartCount"] = &CVUNIVERSE::GetTrueNumberOfFSParticles;
		truefunctions["TrueFSPartCount"] = &CVUNIVERSE::GetTrueNumberOfFSParticles;

		trueintfunctions["TrueChargedPionCount"] = &CVUNIVERSE::GetTrueChargedPionCount;
		truefunctions["TrueChargedPionCount"] = &CVUNIVERSE::GetTrueChargedPionCount;
		trueintfunctions["TrueNeutralPionCount"] = &CVUNIVERSE::GetTrueNeutralPionCount;
		truefunctions["TrueNeutralPionCount"] = &CVUNIVERSE::GetTrueNeutralPionCount;
		trueintfunctions["TruePionCount"] = &CVUNIVERSE::GetTruePionCount;
		truefunctions["TruePionCount"] = &CVUNIVERSE::GetTruePionCount;

		trueintfunctions["TrueProtonCount"] = &CVUNIVERSE::GetTrueProtonCount;
		truefunctions["TrueProtonCount"] = &CVUNIVERSE::GetTrueProtonCount;
		trueintfunctions["TrueNeutronCount"] = &CVUNIVERSE::GetTrueNeutronCount;
		truefunctions["TrueNeutronCount"] = &CVUNIVERSE::GetTrueNeutronCount;

		trueintfunctions["TrueCharmedBaryonCount"] = &CVUNIVERSE::GetTrueCharmedBaryonCount;
		truefunctions["TrueCharmedBaryonCount"] = &CVUNIVERSE::GetTrueCharmedBaryonCount;
		trueintfunctions["TrueStrangeBaryonCount"] = &CVUNIVERSE::GetTrueStrangeBaryonCount;
		truefunctions["TrueStrangeBaryonCount"] = &CVUNIVERSE::GetTrueStrangeBaryonCount;

		trueintfunctions["TrueCharmedMesonCount"] = &CVUNIVERSE::GetTrueCharmedMesonCount;
		truefunctions["TrueCharmedMesonCount"] = &CVUNIVERSE::GetTrueCharmedMesonCount;
		trueintfunctions["TrueStrangeMesonCount"] = &CVUNIVERSE::GetTrueStrangeMesonCount;
		truefunctions["TrueStrangeMesonCount"] = &CVUNIVERSE::GetTrueStrangeMesonCount;

		trueintfunctions["TrueNeutronCount"] = &CVUNIVERSE::GetTrueNeutronCount;
		truefunctions["TrueNeutronCount"] = &CVUNIVERSE::GetTrueNeutronCount;
		trueintfunctions["TrueNegMuonCount"] = &CVUNIVERSE::GetTrueNegMuonCount;
		truefunctions["TrueNegMuonCount"] = &CVUNIVERSE::GetTrueNegMuonCount;
		trueintfunctions["TrueGammaCount"] = &CVUNIVERSE::GetTrueGammaCount;
		truefunctions["TrueGammaCount"] = &CVUNIVERSE::GetTrueGammaCount;

		trueintfunctions["TruthCCQELikeExceptForChargedPions"] = &CVUNIVERSE::GetTruthCCQELikeExceptForChargedPions;
		trueintfunctions["TruthHasSingleChargedPion"] = &CVUNIVERSE::GetTruthHasSingleChargedPion;
		trueintfunctions["TruthHasSingleNeutralPion"] = &CVUNIVERSE::GetTruthHasSingleNeutralPion;
		trueintfunctions["TruthHasMultiPion"] = &CVUNIVERSE::GetTruthHasMultiPion;
		trueintfunctions["TruthIsOther"] = &CVUNIVERSE::GetTruthIsOther;
		
		truefunctions["TruthCCQELikeExceptForChargedPions"] = &CVUNIVERSE::GetTruthCCQELikeExceptForChargedPions;
		truefunctions["TruthHasSingleChargedPion"] = &CVUNIVERSE::GetTruthHasSingleChargedPion;
		truefunctions["TruthHasSingleNeutralPion"] = &CVUNIVERSE::GetTruthHasSingleNeutralPion;
		truefunctions["TruthHasMultiPion"] = &CVUNIVERSE::GetTruthHasMultiPion;
		truefunctions["TruthIsOther"] = &CVUNIVERSE::GetTruthIsOther;

		truefunctions["EventRecordTrueEtaCount"] = &CVUNIVERSE::GetEventRecordTrueEtaCount;
		trueintfunctions["EventRecordTrueEtaCount"] = &CVUNIVERSE::GetEventRecordTrueEtaCount;
		
		// TMVA
		recofunctions["bdtgQELike"] = &CVUNIVERSE::bdtgQELike;
		recofunctions["bdtg1ChargedPion"] = &CVUNIVERSE::bdtg1ChargedPion;
		recofunctions["bdtg1NeutralPion"] = &CVUNIVERSE::bdtg1NeutralPion;
		recofunctions["bdtgMultiPion"] = &CVUNIVERSE::bdtgMultiPion;
		recofunctions["bdtgOther"] = &CVUNIVERSE::bdtgOther;
		
		recointfunctions["PassbdtgQELikeCut"] = &CVUNIVERSE::GetPassbdtgQELikeCut;
		
		// TMVA
		recofunctions["xgboostQELike"] = &CVUNIVERSE::xgboostQELike;
		recofunctions["xgboost1ChargedPion"] = &CVUNIVERSE::xgboost1ChargedPion;
		recofunctions["xgboost1NeutralPion"] = &CVUNIVERSE::xgboost1NeutralPion;
		recofunctions["xgboostMultiPion"] = &CVUNIVERSE::xgboostMultiPion;
		recofunctions["xgboostOther"] = &CVUNIVERSE::xgboostOther;
		
	};

	std::vector<std::string> GetRecoKeys() const
	{
		std::vector<std::string> keys;
		for (auto key : recofunctions)
		{
			keys.push_back(key.first);
		}
		return keys;
	}

	std::vector<std::string> GetTrueKeys() const
	{
		std::vector<std::string> keys;
		for (auto key : truefunctions)
		{
			keys.push_back(key.first);
		}
		return keys;
	}

	const PointerToCVUniverseFunction GetRecoFunction(const std::string name)
	{
		assert(recofunctions.count(name));
		PointerToCVUniverseFunction result = recofunctions[name];
		return result;
	};

	PointerToCVUniverseFunction GetTrueFunction(const std::string name)
	{
		// try a real function first
		if (truefunctions.count(name))
		{
			return truefunctions[name];
		}
		else
		{
			assert(trueintfunctions.count(name));
			return trueintfunctions[name];
		}
	};

	const PointerToCVUniverseIntFunction GetRecoIntFunction(const std::string name)
	{
		assert(recointfunctions.count(name));
		return recointfunctions[name];
	};

	PointerToCVUniverseIntFunction GetTrueIntFunction(const std::string name)
	{
		assert(trueintfunctions.count(name));
		return trueintfunctions[name];
	};
	
	std::vector<float> GetVectorOfValues(const CVUNIVERSE * univ, const std::vector<std::string> varlist)
	{
	 
		std::vector<float> vals;
		float val;
        
		for (auto name : varlist){
			val = recofunctions[name](*univ);
		  vals.emplace_back(val);      
		}
		
		return vals;
	}
};

#endif
