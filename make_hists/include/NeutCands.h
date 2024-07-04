// File: NeutCands.h
// Info: Neutron Candidate Class. Currently under development. Gleaned from David Last's version (which maybe was borrowed from Andrew Olivier's analysis) here https://github.com/MinervaExpt/Target-Antinu-Neutrons/blob/plasticOverhaul/event/NeutCands.h
//
// Author: David Last dlast@sas.upenn.edu/lastd44@gmail.com / Noah Harvey Vaughan vaughann@oregonstate.edu/noah.vaughan31@gmail.com

#ifndef NEUTCANDS_H
#define NEUTCANDS_H

#include <bitset>
#include <map>
#include <string>
#include <unordered_map>
#include <vector>

#include "TLorentzVector.h"
#include "TVector3.h"
#include "stdlib.h"

namespace NeutronCandidates {
typedef std::map<std::string, std::vector<std::string>> intBranchMap;
typedef std::map<std::string, std::vector<std::string>> doubleBranchMap;
typedef std::map<std::string, std::vector<int>> intCandData;
typedef std::map<std::string, std::vector<double>> doubleCandData;

intBranchMap GetBranchIntMap();
doubleBranchMap GetBranchDoubleMap();

std::unordered_map<int, int> GetPDGBins();

class NeutCand {
   private:
    // Currently only coding in the members that I actively use in MnvTgtNeutrons/particleCannon/nonMAT/interactiveMacros/Basic_Cuts_Try.cc

    int fID;
    int fIs3D;
    int fMCPID;
    int fTopMCPID;
    int fMCParentTrackID;
    int fMCParentPID;
    double fTotE;
    double fAngleToFP;
    TVector3 fEvtVtx;
    TVector3 fBegPos;
    TVector3 fEndPos;
    TVector3 fDirection;
    TVector3 fFlightPath;
    TLorentzVector fTopMCMom;
    TLorentzVector fTopMCPos;

    void init();

   public:
    // CTOR
    NeutCand();
    NeutCand(NeutronCandidates::intCandData candIntData, NeutronCandidates::doubleCandData candDoubleData, TVector3 vtx);

    // Here for use in Variable-like classes
    double GetDummyVar() const { return -999.; }

    int MatchesFSNeutron(TLorentzVector neutMom, double tolerance);
    int GetID() const { return fID; };
    int GetIs3D() const { return fIs3D; };
    int GetMCPID() const { return fMCPID; };
    int GetTopMCPID() const { return fTopMCPID; };
    int GetMCParentTrackID() const { return fMCParentTrackID; };
    int GetMCParentPID() const { return fMCParentPID; };

    double GetTotalE() const { return fTotE; };
    double GetAngleToFP() const { return fAngleToFP; };

    double GetPDGBin() const {
        std::unordered_map<int, int> bins = GetPDGBins();
        if (fMCParentTrackID == 0)
            return bins[fMCPID];
        else
            return bins[fTopMCPID];
    };
    double GetLength() const {
        if (fID >= 0)
            return fDirection.Mag();
        else
            return -1.0;
    };
    double GetDEDX() const {
        if (fDirection.Mag() > 0)
            return fTotE / (fDirection.Mag());
        else
            return -1.0;
    };
    double GetVtxDist() const {
        if (fID >= 0)
            return fFlightPath.Mag();
        else
            return -1.0;
    };
    double GetVtxZDist() const {
        if (fID >= 0)
            return abs(fFlightPath.Z());
        else
            return -1.0;
    };
    double GetXPos() const { return fBegPos.X(); }
    double GetYPos() const { return fBegPos.Y(); }
    double GetZPos() const { return fBegPos.Z(); }

    TVector3 GetBegPos() const { return fBegPos; };
    TVector3 GetEndPos() const { return fEndPos; };
    TVector3 GetFlightPath() const { return fFlightPath; };
    TVector3 GetDirection() const { return fDirection; };
    TVector3 GetEvtVtx() const { return fEvtVtx; };

    TLorentzVector GetTopMCPos() const { return fTopMCPos; };
    TLorentzVector GetTopMCMom() const { return fTopMCMom; };

    std::bitset<4> GetClassifier();

    void SetID(std::vector<int> ID) { fID = ID.at(0); };
    void SetIs3D(std::vector<int> is3D) { fIs3D = is3D.at(0); };
    void SetMCPID(std::vector<int> MCPID) { fMCPID = MCPID.at(0); };
    void SetTopMCPID(std::vector<int> TopPID) { fTopMCPID = TopPID.at(0); };
    void SetMCParentTrackID(std::vector<int> ParentID) { fMCParentTrackID = ParentID.at(0); };
    void SetMCParentPID(std::vector<int> ParentPID) { fMCParentPID = ParentPID.at(0); };
    void SetTotalE(std::vector<double> TotE) { fTotE = TotE.at(0); };
    void SetEvtVtx(TVector3 EvtVtx) { fEvtVtx = EvtVtx; };
    // Move MULTI-LINE DEFINITIONS TO CPP...???
    void SetBegPos(std::vector<double> BegPos) {
        fBegPos.SetXYZ(BegPos.at(0), BegPos.at(1), BegPos.at(2));
        fDirection = fEndPos - fBegPos;
        fFlightPath = fBegPos - fEvtVtx;
        if (fFlightPath.Mag() > 0 && fDirection.Mag() > 0) {
            fAngleToFP = fFlightPath.Angle(fDirection);
        } else {
            fAngleToFP = -9999.0;
        }
    };
    void SetEndPos(std::vector<double> EndPos) {
        fEndPos.SetXYZ(EndPos.at(0), EndPos.at(1), EndPos.at(2));
        fDirection = fEndPos - fBegPos;
        fAngleToFP = fFlightPath.Angle(fDirection);
        if (fFlightPath.Mag() > 0 && fDirection.Mag() > 0) {
            fAngleToFP = fFlightPath.Angle(fDirection);
        } else {
            fAngleToFP = -9999.0;
        }
    };
    void SetTopMCPos(std::vector<double> TopMCPos) {
        fTopMCPos.SetXYZT(TopMCPos.at(0), TopMCPos.at(1), TopMCPos.at(2), TopMCPos.at(3));
    };
    void SetTopMCMom(std::vector<double> TopMCMom) {
        fTopMCPos.SetPxPyPzE(TopMCMom.at(0), TopMCMom.at(1), TopMCMom.at(2), TopMCMom.at(3));
    };

    // DTOR
    virtual ~NeutCand() = default;
};

class NeutCands {
   private:
    int fNCands;
    int fIDmaxE;
    NeutCand fCandMaxE;
    std::map<int, NeutCand> fCands;

    void init();

   public:
    // CTORS
    NeutCands();
    NeutCands(std::vector<NeutCand> cands);
    NeutCands(std::map<int, intCandData> candsDataInt, std::map<int, doubleCandData> candDataDouble);

    // DTOR
    virtual ~NeutCands() = default;

    void SetCands(std::map<int, NeutCand> inCands) {
        fCands = inCands;
        fNCands = inCands.size();
    }

    int GetIDMaxE() const { return fIDmaxE; };
    int GetNCands() const { return fNCands; };
    NeutCand GetCandidate(int ID) {
        if (fNCands == 0)
            return NeutCand();
        else
            return fCands[ID];
    };
    NeutCand GetMaxCandidate() const { return fCandMaxE; };
    std::map<int, NeutCand> GetCandidates() const { return fCands; };
};

}  // namespace NeutronCandidates

class NeutronEvent {
   private:
    bool fIsSignal;
    bool fIsFSSignal;
    bool fIsMC;
    int fIntType;
    int fIntCode;
    int fTgtZ;
    int fBinPTPZ;
    double fEMNBlobs, fEMBlobE, fEMBlobNHits;
    double fMaxFSNeutronKE;
    std::bitset<64> fSideBands;
    NeutronCandidates::NeutCands fNeutCands;

   public:
    NeutronEvent() : fNeutCands(), fIsSignal(false), fIsFSSignal(false), fIsMC(false), fIntType(-999), fIntCode(-999), fTgtZ(-999), fBinPTPZ(-1.0), fEMNBlobs(-999.0), fEMBlobE(-999.0), fEMBlobNHits(-999.0), fMaxFSNeutronKE(-999.0), fSideBands(0) {}
    NeutronEvent(NeutronCandidates::NeutCands cands) : fIsSignal(false), fIsFSSignal(false), fIsMC(false), fIntType(-999), fIntCode(-999), fTgtZ(-999), fBinPTPZ(-1.0), fEMNBlobs(-999.0), fEMBlobE(-999.0), fEMBlobNHits(-999.0), fMaxFSNeutronKE(-999.0), fSideBands(0) { fNeutCands = cands; }

    // Use in Variable-like classes
    double GetDummyVar() const { return -999.; }

    bool IsSignal() const { return fIsSignal; }
    bool IsFSSignal() const { return fIsFSSignal; }
    bool IsMC() const { return fIsMC; }
    int GetIntType() const { return fIntType; }
    int GetIntCode() const { return fIntCode; }
    int GetTgtZ() const { return fTgtZ; }
    int GetBinPTPZ() const { return fBinPTPZ; }
    double GetEMNBlobs() const { return fEMNBlobs; }
    double GetEMBlobE() const { return fEMBlobE; }
    double GetEMBlobNHits() const { return fEMBlobNHits; }
    double GetEMBlobENHitRatio() const {
        if (fEMBlobNHits > 0.0)
            return fEMBlobE / fEMBlobNHits;
        else
            return -999.0;
    }
    double GetMaxFSNeutronKE() const { return fMaxFSNeutronKE; }
    std::bitset<64> GetSideBandStat() const { return fSideBands; }

    NeutronCandidates::NeutCand GetLeadingNeutCand() const { return fNeutCands.GetMaxCandidate(); }
    NeutronCandidates::NeutCands GetNeutCands() const { return fNeutCands; }

    void SetSignal(bool isSignal) { fIsSignal = isSignal; }
    void SetFSSignal(bool isFSSignal) { fIsFSSignal = isFSSignal; }
    void SetIsMC() { fIsMC = true; }
    void SetIntType(int intType) { fIntType = intType; }
    void SetIntCode(int intCode) { fIntCode = intCode; }
    void SetTgtZ(int tgtZ) { fTgtZ = tgtZ; }
    void SetBinPTPZ(int binPTPZ) { fBinPTPZ = binPTPZ; }
    void SetEMBlobInfo(std::vector<double> EMInfo) {
        fEMNBlobs = EMInfo.at(0);
        fEMBlobE = EMInfo.at(1);
        fEMBlobNHits = EMInfo.at(2);
    }
    void SetMaxFSNeutronKE(double KE) { fMaxFSNeutronKE = KE; }
    void SetSideBandStat(std::bitset<64> SBStat) { fSideBands = SBStat; }
};

#endif