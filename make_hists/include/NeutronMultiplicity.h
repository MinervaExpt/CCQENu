#ifndef NEUTRONMULTIPLICITY_H
#define NEUTRONMULTIPLICITY_H

#include <map>
#include <string>
#include <unordered_map>
#include <vector>

#include "TLorentzVector.h"
#include "TVector3.h"
#include "stdlib.h"
#include "utils/NuConfig.h"
// #include "include/CVUniverse.h"

namespace NeutronMultiplicity {
class NeutCand {
   public:
    int m_blobID;           // which blob
    int m_is3D;             // is it 3D?
    double m_recoEDep;      // how much energy does it deposit?
    double m_clusterMaxE;   // Max cluster Energy
    TVector3 m_position;    // where is it?
    TVector3 m_flightpath;  // which direction did it travel from the vtx????

    // Truth vars
    int m_truthPID = -1;       // PID of most recent GEANT Parent
    int m_truthTopMCPID = -1;  // PID of the GENIE parent
    TVector3 m_TopMomentum;    // which direction did it travel from the vtx????

    bool m_recoset = false;
    bool m_truthset = false;

    // CTORs
    NeutCand();  // default
    NeutCand(int blobID, int is3D, double recoEDep, TVector3 position);

    ~NeutCand() = default;
    // reco functions
    void SetReco(int blobID, int is3D, double recoEDep, double clusterMaxE, TVector3 position, TVector3 flightpath);

    // SetBlobID(int index);

    // truth functions
    void SetTruth(int truthPID, int truthTopMCPID, TVector3 TopMomentum);

    int GetCandBlobID();
    int GetCandIs3D();
    double GetCandRecoEDep();
    TVector3 GetCandPosition();
    TVector3 GetCandFlightPath();

    double GetCandVtxDist();  // TODO: Andrew does something weird with this

    int GetCandTruthPID();
    int GetCandTruthTopPID();

    double GetCandTruthAngleFromParent();

    bool operator>(const NeutCand& cand) const {
        return (this->m_recoEDep > cand.m_recoEDep);
    }

    // TODO: Something more flexible in development

    // NeutCand(int index);  // give index, intialize internally
};

// class to hold all the neutron candidates for an event
class NeutEvent {
   private:
    // set up via config, contain info to check cands by
    double m_vtxdist_max = -1.;                // in mm
    double m_vtxdist_min = -1.;                // in mm
    double m_vtx_zdist_min = -1.;              // in mm
    std::vector<double> m_vtx_box = {-1., -1.};  // in mm, <z, transverse>
    double m_zpos_min = -1.;                   // in mm, 5980
    double m_zpos_max = -1.;                   // in mm, 8422
    double m_muoncone_min = -1.0;              // in deg
    double m_muondist_min = 0.0;               // in mm
    double m_edep_min = 0.;                    // in MeV
    int m_req3D = 0;                           // Set requirement to 3D blob, set to 1 for 3D only, -1 for 2D only, 0 for both

    int m_nneutcands;
    TVector3 m_vtx;
    TVector3 m_mupath;

    std::vector<NeutronMultiplicity::NeutCand*> m_cands;  // the candidates it contains
    bool _is_cands_set = false;

    bool _recoset = false;
    bool _truthset = false;

   public:
    // TOOD: make neutron config vars in CVUniverse
    NeutEvent(NuConfig config, int n_neutcands, TVector3 vtx, TVector3 mupath, std::vector<int> order = {});  // configure number of cands and set up the cands internally based off how many there are
    NeutEvent(int n_neutcands, TVector3 vtx, TVector3 mupath);
    NeutEvent(NuConfig config);  // would need to set up cands separately using SetCands
    NeutEvent();
    ~NeutEvent() {
        for (auto cand : m_cands) {
            delete cand;
        }
        m_cands.clear();
    }

    void SetConfig(NuConfig config);
    // NeutEvent();
    void SetCands(int n_neutcands, TVector3 vtx, TVector3 mupath);

   private:
    void ClearCands();  // This is to clean up, called internally in SetCands if some cands are set.

   public:
    // Set the reco variables for reco and truth. This is necessary to handle both data and MC without issues
    void SetReco(std::vector<int> blobIDs, std::vector<int> is3Ds, std::vector<double> EDeps, std::vector<double> clusterMaxEs, std::vector<TVector3> positions);
    void SetTruth(std::vector<int> truthPIDs, std::vector<int> truthTopMCPIDs, std::vector<double> truthTopMomentumsX, std::vector<double> truthTopMomentumsY, std::vector<double> truthTopMomentumsZ);

    bool GetIsTruthSet();

    std::vector<NeutronMultiplicity::NeutCand*> GetCands();      // Get all blobs
    std::vector<NeutronMultiplicity::NeutCand*> GetNeutCands();  // Get just the ones passing neutron cuts

    std::vector<NeutronMultiplicity::NeutCand*> GetTrueNeutCands();

    NeutronMultiplicity::NeutCand* GetCand(int index);
    bool GetCandIsNeut(int index);  // checks all the following

    bool CandPassMuonAngle(int index);  // check if outside angle from muon track
    bool CandPassMuonDist(int index);   // check if outside distance from muon track
    bool CandPassFiducial(int index);   // check if inside z bounds
    bool CandPassVtxDist(int index);    // check if pass vtx spherical dist min
    bool CandPassVtxZDist(int index);   // check if pass vtx z dist min
    bool CandPassVtxBox(int index);     // check if cand is outside a box around vtx
    bool CandPassEDep(int index);       // check if Edep is high enough
    bool CandPassIs3D(int index);       // check if cand is 3D or 2D

    int GetCandTruthPID(int index);     // GEANT parent
    int GetCandTruthTopPID(int index);  // GENIE parent
    // Helper for ordering the cands
    static bool compare_cands(NeutronMultiplicity::NeutCand* cand1, NeutronMultiplicity::NeutCand* cand2) {
        return (*cand1 > *cand2);
    }

    // TODO: Something more flexible in development
   private:
    std::vector<std::string> m_selectionvars;
    std::map<std::string, double> m_equals;
    std::map<std::string, double> m_min;
    std::map<std::string, double> m_max;
    std::vector<std::string> m_plotvars;

   public:
    void Configure(NuConfig config);
    bool CheckVal(std::string varname, double val);
    void SetReco(std::map<std::string, std::vector<int>> intVals, std::map<std::string, std::vector<double>> doubleVals);
    void SetTruth(std::map<std::string, std::vector<int>> intVals, std::map<std::string, std::vector<double>> doubleVals);
};

}  // namespace NeutronMultiplicity
#endif  // NEUTRONMULTIPLICITY_H