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

#include <cassert>
#include <functional>
#include <iostream>
#include <map>
#include <string>
#include <vector>

#include "include/CVUniverse.h"

template <class CVUNIVERSE>
class CVFunctions {
    typedef std::function<double(const CVUNIVERSE &)> PointerToCVUniverseFunction;
    typedef std::function<int(const CVUNIVERSE &)> PointerToCVUniverseIntFunction;
    std::map<const std::string, PointerToCVUniverseFunction> recofunctions;
    std::map<const std::string, PointerToCVUniverseFunction> truefunctions;
    std::map<const std::string, PointerToCVUniverseIntFunction> recointfunctions;
    std::map<const std::string, PointerToCVUniverseIntFunction> trueintfunctions;

   public:
    CVFunctions() {
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
        trueintfunctions["TruthIsCCQELikeAll"] = &CVUNIVERSE::GetTruthIsCCQELikeAll;

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

        // Interaction Vertex

        recointfunctions["HasInteractionVertex"] = &CVUNIVERSE::GetHasInteractionVertex;

        // Isolated Blobs

        recofunctions["NBlobs"] = &CVUNIVERSE::GetNBlobs;
        truefunctions["TrueNBlobs"] = &CVUNIVERSE::GetTrueNBlobs;

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

        // Both

        recointfunctions["HasMichelOrNBlobs"] = &CVUNIVERSE::GetHasMichelOrNBlobs;

        // Protons

        recointfunctions["NumberOfProtonCandidates"] = &CVUNIVERSE::GetNumberOfProtonCandidates;
        recofunctions["NumberOfProtonCandidates"] = &CVUNIVERSE::GetNumberOfProtonCandidates;

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

        recointfunctions["IsAllTracksProtons"] = &CVUNIVERSE::GetIsAllTracksProtons;
        
        recointfunctions["IsPrimaryProton"] = &CVUNIVERSE::GetIsPrimaryProton;
        recointfunctions["IsPrimaryProton1"] = &CVUNIVERSE::GetIsPrimaryProton1;
        recofunctions["PrimaryProtonScore"] = &CVUNIVERSE::GetPrimaryProtonScore;
        recofunctions["PrimaryProtonScore1"] = &CVUNIVERSE::GetPrimaryProtonScore1;
        recofunctions["PrimaryProtonScore2"] = &CVUNIVERSE::GetPrimaryProtonScore2;

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

        recofunctions["PrimaryProtonAngle"] = &CVUNIVERSE::GetPrimaryProtonAngle;
        recofunctions["SecProtonAngle_1"] = &CVUNIVERSE::GetSecProtonAngle_1;
        recofunctions["SecProtonAngle_2"] = &CVUNIVERSE::GetSecProtonAngle_2;
        recofunctions["SecProtonAngle_3"] = &CVUNIVERSE::GetSecProtonAngle_3;
        recofunctions["SecProtonAngle_4"] = &CVUNIVERSE::GetSecProtonAngle_4;
        recofunctions["SecProtonAngle_5"] = &CVUNIVERSE::GetSecProtonAngle_5;
        recofunctions["SecProtonAngle_6"] = &CVUNIVERSE::GetSecProtonAngle_6;

        recofunctions["PrimaryProtonTrackVtxGap"] = &CVUNIVERSE::GetPrimaryProtonTrackVtxGap;
        recofunctions["SecProtonTrackVtxGap_1"] = &CVUNIVERSE::GetSecProtonTrackVtxGap_1;
        recofunctions["SecProtonTrackVtxGap_2"] = &CVUNIVERSE::GetSecProtonTrackVtxGap_2;
        recofunctions["SecProtonTrackVtxGap_3"] = &CVUNIVERSE::GetSecProtonTrackVtxGap_3;
        recofunctions["SecProtonTrackVtxGap_4"] = &CVUNIVERSE::GetSecProtonTrackVtxGap_4;
        recofunctions["SecProtonTrackVtxGap_5"] = &CVUNIVERSE::GetSecProtonTrackVtxGap_5;
        recofunctions["SecProtonTrackVtxGap_6"] = &CVUNIVERSE::GetSecProtonTrackVtxGap_6;

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

        recofunctions["TotalPrimaryProtonEnergy"] = &CVUNIVERSE::GetTotalPrimaryProtonEnergy;
        recofunctions["TotalSecProtonEnergy_1"] = &CVUNIVERSE::GetTotalSecProtonEnergy_1;
        recofunctions["TotalSecProtonEnergy_2"] = &CVUNIVERSE::GetTotalSecProtonEnergy_2;
        recofunctions["TotalSecProtonEnergy_3"] = &CVUNIVERSE::GetTotalSecProtonEnergy_3;
        recofunctions["TotalSecProtonEnergy_4"] = &CVUNIVERSE::GetTotalSecProtonEnergy_4;
        recofunctions["TotalSecProtonEnergy_5"] = &CVUNIVERSE::GetTotalSecProtonEnergy_5;
        recofunctions["TotalSecProtonEnergy_6"] = &CVUNIVERSE::GetTotalSecProtonEnergy_6;

        recofunctions["PrimaryProtonFractionEnergyInCone"] = &CVUNIVERSE::GetPrimaryProtonFractionEnergyInCone;
        recofunctions["SecProtonFractionEnergyInCone_1"] = &CVUNIVERSE::GetSecProtonFractionEnergyInCone_1;
        recofunctions["SecProtonFractionEnergyInCone_2"] = &CVUNIVERSE::GetSecProtonFractionEnergyInCone_2;
        recofunctions["SecProtonFractionEnergyInCone_3"] = &CVUNIVERSE::GetSecProtonFractionEnergyInCone_3;
        recofunctions["SecProtonFractionEnergyInCone_4"] = &CVUNIVERSE::GetSecProtonFractionEnergyInCone_4;
        recofunctions["SecProtonFractionEnergyInCone_5"] = &CVUNIVERSE::GetSecProtonFractionEnergyInCone_5;
        recofunctions["SecProtonFractionEnergyInCone_6"] = &CVUNIVERSE::GetSecProtonFractionEnergyInCone_6;

        recofunctions["PrimaryProtonTrueKE"] = &CVUNIVERSE::GetPrimaryProtonTrueKE;
        recofunctions["SecProtonTrueKE_1"] = &CVUNIVERSE::GetSecProtonTrueKE_1;
        recofunctions["SecProtonTrueKE_2"] = &CVUNIVERSE::GetSecProtonTrueKE_2;
        recofunctions["SecProtonTrueKE_3"] = &CVUNIVERSE::GetSecProtonTrueKE_3;
        recofunctions["SecProtonTrueKE_4"] = &CVUNIVERSE::GetSecProtonTrueKE_4;
        recofunctions["SecProtonTrueKE_5"] = &CVUNIVERSE::GetSecProtonTrueKE_5;
        recofunctions["SecProtonTrueKE_6"] = &CVUNIVERSE::GetSecProtonTrueKE_6;

        recofunctions["EnergyDiffTruedEdx"] = &CVUNIVERSE::GetEnergyDiffTruedEdx;

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
        trueintfunctions["TruePositivePionCount"] = &CVUNIVERSE::GetTruePositivePionCount;
        truefunctions["TruePositivePionCount"] = &CVUNIVERSE::GetTruePositivePionCount;
        trueintfunctions["TrueNegativePionCount"] = &CVUNIVERSE::GetTrueNegativePionCount;
        truefunctions["TrueNegativePionCount"] = &CVUNIVERSE::GetTrueNegativePionCount;
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
        trueintfunctions["TruthHasSinglePositivePion"] = &CVUNIVERSE::GetTruthHasSinglePositivePion;
        trueintfunctions["TruthHasSingleNegativePion"] = &CVUNIVERSE::GetTruthHasSingleNegativePion;
        trueintfunctions["TruthHasSingleNeutralPion"] = &CVUNIVERSE::GetTruthHasSingleNeutralPion;
        trueintfunctions["TruthHasMultiPion"] = &CVUNIVERSE::GetTruthHasMultiPion;

        truefunctions["EventRecordTrueEtaCount"] = &CVUNIVERSE::GetEventRecordTrueEtaCount;
        trueintfunctions["EventRecordTrueEtaCount"] = &CVUNIVERSE::GetEventRecordTrueEtaCount;
    };

    std::vector<std::string> GetRecoKeys() const {
        std::vector<std::string> keys;
        for (auto key : recofunctions) {
            keys.push_back(key.first);
        }
        return keys;
    }

    std::vector<std::string> GetTrueKeys() const {
        std::vector<std::string> keys;
        for (auto key : truefunctions) {
            keys.push_back(key.first);
        }
        return keys;
    }

    const PointerToCVUniverseFunction GetRecoFunction(const std::string name) {
        assert(recofunctions.count(name));
        PointerToCVUniverseFunction result = recofunctions[name];
        return result;
    };

    PointerToCVUniverseFunction GetTrueFunction(const std::string name) {
        // try a real function first
        if (truefunctions.count(name)) {
            return truefunctions[name];
        } else {
            assert(trueintfunctions.count(name));
            return trueintfunctions[name];
        }
    };

    const PointerToCVUniverseIntFunction GetRecoIntFunction(const std::string name) {
        assert(recointfunctions.count(name));
        return recointfunctions[name];
    };

    PointerToCVUniverseIntFunction GetTrueIntFunction(const std::string name) {
        assert(trueintfunctions.count(name));
        return trueintfunctions[name];
    };
};

#endif
