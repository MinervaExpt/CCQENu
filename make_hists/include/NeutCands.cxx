// File: NeutCands.cxx
// Info: Neutron Candidate Class. Currently under development. Gleaned from David Last's version (which maybe was borrowed from Andrew Olivier's analysis) here https://github.com/MinervaExpt/Target-Antinu-Neutrons/blob/plasticOverhaul/event/NeutCands.cpp
//
// Author: David Last dlast@sas.upenn.edu/lastd44@gmail.com / Noah Harvey Vaughan vaughann@oregonstate.edu/noah.vaughan31@gmail.com

#include "NeutCands.h"

namespace NeutronCandidates {

std::unordered_map<int, int> GetPDGBins() {
    return {{2112, 2},
            {2212, 3},
            {111, 4},
            {211, 5},
            {-211, 6},
            {22, 7},
            {11, 8},
            {-11, 8},
            {-13, 9},
            {13, 9}};
};

intBranchMap GetBranchIntMap() {
    // return {{"SetID",{"MasterAnaDev_BlobID"}},{"SetIs3D",{"MasterAnaDev_BlobIs3D"}},{"SetMCPID",{"MasterAnaDev_BlobMCPID"}},{"SetTopMCPID",{"MasterAnaDev_BlobTopMCPID"}},{"SetMCParentTrackID",{"MasterAnaDev_BlobMCParentTrackID"}},{"SetMCParentPID",{"MasterAnaDev_BlobMCParentPID"}},};
    // return {{"SetID",{"MasterAnaDev_BlobID"}},{"SetIs3D",{"MasterAnaDev_BlobIs3D"}},{"SetMCPID",{"MasterAnaDev_BlobMCPID"}},{"SetTopMCPID",{"MasterAnaDev_BlobTopMCPID"}},{"SetMCParentTrackID",{"MasterAnaDev_BlobMCParentTrackID"}},};
    return {
        {"SetID", {"_BlobID"}},
        {"SetIs3D", {"_BlobIs3D"}},
        {"SetMCPID", {"_BlobMCPID"}},
        {"SetTopMCPID", {"_BlobTopMCPID"}},
        {"SetMCParentTrackID", {"_BlobMCParentTrackID"}},
    };
}

doubleBranchMap GetBranchDoubleMap() {
    // return {{"SetTotE",{"MasterAnaDev_BlobTotalE"}},{"SetBegPos",{"MasterAnaDev_BlobBegX","MasterAnaDev_BlobBegY","MasterAnaDev_BlobBegZ"}},{"SetEndPos",{"MasterAnaDev_BlobEndX","MasterAnaDev_BlobEndY","MasterAnaDev_BlobEndZ"}}, };
    return {
        {"SetTotE", {"_BlobTotalE"}},
        {"SetBegPos", {"_BlobBegX", "_BlobBegY", "_BlobBegZ"}},
        {"SetEndPos", {"_BlobEndX", "_BlobEndY", "_BlobEndZ"}},
        {"SetTopMCMom", {"_BlobMCTrackPx", "_BlobMCTrackPy", "_BlobMCTrackPz", "_BlobMCTrackE"}},
        {"SetTopMCPos", {"_BlobMCTrackX", "_BlobMCTrackY", "_BlobMCTrackZ", "_BlobMCTrackT"}},
    };
}

NeutCand::NeutCand() {
    this->init();
}

NeutCand::NeutCand(intCandData candIntData, doubleCandData candDoubleData, TVector3 vtx) {
    this->init();
    this->SetEvtVtx(vtx);
    for (const auto& function : candIntData) {
        if (function.first == "SetID")
            this->SetID(function.second);
        else if (function.first == "SetIs3D")
            this->SetIs3D(function.second);
        else if (function.first == "SetMCPID")
            this->SetMCPID(function.second);
        else if (function.first == "SetTopMCPID")
            this->SetTopMCPID(function.second);
        else if (function.first == "SetMCParentTrackID")
            this->SetMCParentTrackID(function.second);
        else if (function.first == "SetMCParentPID")
            this->SetMCParentPID(function.second);
        else
            continue;
    }
    for (const auto& function : candDoubleData) {
        if (function.first == "SetTotE")
            this->SetTotalE(function.second);
        else if (function.first == "SetBegPos")
            this->SetBegPos(function.second);
        else if (function.first == "SetEndPos")
            this->SetEndPos(function.second);
        else if (function.first == "SetTopMCMom")
            this->SetTopMCMom(function.second);
        else if (function.first == "SetTopMCPos")
            this->SetTopMCPos(function.second);
        else
            continue;
    }
}

// NeutCand::NeutCand(NuConfig config, intCandData candIntData, doubleCandData candDoubleData, TVector3 vtx) {
//     // m_Is3DReq = config.GetBool("Is3D");
//     // vars stolen from Andrew
//     fRecoMinEDep = config.GetBool("MinEDep");            // in MeV
//     fRecoMaxZDist = config.GetDouble("MaxZDist");        // in mm
//     fRecoEDepBoxMin = config.GetDouble("EDepBoxMin");    // in MeV
//     fRecoEDistBoxMax = config.GetDouble("EDistBoxMax");  // in mm
//     fMinZCosine = config.GetDouble("MZCosine");          // as double
//     fVertexBoxDist = config.GetDouble("VertexBoxDist");  // in mm
//     fAngleToFPMin = config.GetDouble("AngleToFPMin");    // in rad?
//     fAngleToFPMax = config.GetDouble("AngleToFPMax");    // in rad?
// }

void NeutCand::init() {
    TVector3 tmp;
    tmp.SetXYZ(0.0, 0.0, 0.0);
    TLorentzVector tmp2;
    tmp2.SetXYZT(0.0, 0.0, 0.0, 0.0);
    fID = -1;
    fIs3D = -999;
    fMCPID = -999;
    fTopMCPID = -999;
    fMCParentTrackID = -999;
    fMCParentPID = -999;
    fTotE = -999.0;
    fAngleToFP = -999.0;
    fEvtVtx = tmp;
    fBegPos = tmp;
    fDirection = tmp;
    fFlightPath = tmp;
    fTopMCPos = tmp2;
    fTopMCMom = tmp2;
    tmp.~TVector3();
    tmp2.~TLorentzVector();
}

std::bitset<4> NeutCand::GetClassifier() {
    std::bitset<4> cfier{"0000"};
    if (this->GetIs3D() == 1) cfier.flip(0);
    if (this->GetAngleToFP() > 0.2 && this->GetAngleToFP() < 0.7) cfier.flip(1);
    if (this->GetTotalE() >= 20.0) cfier.flip(2);
    if (abs(this->GetFlightPath().Z()) >= 100.0) cfier.flip(3);
    return cfier;
}

// std::bitset<4> NeutCand::GetClassifier() {
//     std::bitset<4> cfier{"0000"};
//     if (this->GetIs3D() == 1) cfier.flip(0);
//     if (this->GetAngleToFP() > fAngleToFPMin && this->GetAngleToFP() < fAngleToFPMax) cfier.flip(1);
//     if (this->GetTotalE() >= fRecoEDepMin) cfier.flip(2);
//     if (abs(this->GetFlightPath().Z()) >= RecoMaxZDist) cfier.flip(3);
//     return cfier;
// }

int NeutCand::MatchesFSNeutron(TLorentzVector neutMom, double tolerance) {
    if (fTopMCPID != 2112) return -1;
    TLorentzVector diff = fTopMCMom - neutMom;
    diff *= 1.0 / neutMom.Mag();
    if (fabs(diff.X()) < tolerance && fabs(diff.Y()) < tolerance && fabs(diff.Z()) < tolerance && fabs(diff.T()) < tolerance && diff.Mag() < tolerance)
        return 1;
    else
        return 0;
}

NeutCands::NeutCands() {
    this->init();
}

NeutCands::NeutCands(std::vector<NeutCand*> cands) {
    this->init();
    std::map<int, NeutCand*> candsMap;
    double maxE = -1.0;
    for (int i_cand = 0; i_cand < (int)cands.size(); ++i_cand) {
        candsMap[cands.at(i_cand)->GetID()] = cands.at(i_cand);
        if (cands.at(i_cand)->GetTotalE() > maxE) {
            fIDmaxE = cands.at(i_cand)->GetID();
            fCandMaxE = cands.at(i_cand);
            maxE = cands.at(i_cand)->GetTotalE();
        }
        this->SetCands(candsMap);
    }
}

// void NeutCand::SetConfig(NuConfig config){
//     fAngleToFPMin = config.GetDouble("AngleToFPMin");  // in rad, exclusive
//     fAngleToFPMax = config.GetDouble("AngleToFPMax");  // in rad, exclusive
//     fRecoMaxZDist = config.GetDouble("RecoMaxZDist");  // in mm, inclusive
//     fRecoEDepMin = config.GetDouble("RecoEDepMin");    // in MeV, inclusive
// }

// NeutCands::NeutCands(std::vector<NeutCand> cands, NuConfig config) {
//     this->init();
//     std::map<int, NeutCand> candsMap;
//     double maxE = -1.0;
//     for (int i_cand = 0; i_cand < (int)cands.size(); ++i_cand) {
//         candsMap[cands.at(i_cand).GetID()] = cands.at(i_cand);
//         if (cands.at(i_cand).GetTotalE() > maxE) {
//             fIDmaxE = cands.at(i_cand).GetID();
//             fCandMaxE = cands.at(i_cand);
//             maxE = cands.at(i_cand).GetTotalE();
//         }
//         this->SetCands(candsMap);
//     }
// }
// }

NeutCands::NeutCands(std::map<int, intCandData> candsDataInt, std::map<int, doubleCandData> candDataDouble) {
    this->init();
}

void NeutCands::init() {
    fCands = {};
    fNCands = fCands.size();
    fIDmaxE = -1;
    fCandMaxE = new NeutCand();
}

}  // namespace NeutronCandidates