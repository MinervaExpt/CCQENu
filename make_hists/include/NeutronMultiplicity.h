#ifndef NEUTRONMULTIPLICITY_H
#define NEUTRONMULTIPLICITY_H

#include <map>
#include <string>
#include <unordered_map>
#include <vector>
// #include <Math.h>
#include "Math/Vector3D.h"
#include "Math/VectorUtil.h"


#include "TLorentzVector.h"
// #include "TVector3.h"
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
    ROOT::Math::XYZVector m_position;    // where is it?
    ROOT::Math::XYZVector m_flightpath;  // which direction did it travel from the vtx????

    // Truth vars
    int m_truthPID = -1;       // PID of most recent GEANT Parent
    int m_truthTopMCPID = -1;  // PID of the GENIE parent
    ROOT::Math::XYZVector m_TopMomentum;    // which direction did it travel from the vtx????

    bool m_recoset = false;
    bool m_truthset = false;

    // CTORs
    NeutCand();  // default
    NeutCand(int blobID, int is3D, double recoEDep, ROOT::Math::XYZVector position);
    // NeutCand(NeutCand& cand);

    ~NeutCand() = default;
    // reco functions
    void SetReco(int blobID, int isD, double recoEDep, double clusterMaxE, ROOT::Math::XYZVector position, ROOT::Math::XYZVector flightpath);

    // SetBlobID(int index);

    // truth functions
    void SetTruth(int truthPID, int truthTopMCPID, ROOT::Math::XYZVector TopMomentum);

    int GetCandBlobID();
    int GetCandIs3D();
    double GetCandRecoEDep();
    ROOT::Math::XYZVector GetCandPosition();
    ROOT::Math::XYZVector GetCandFlightPath();

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

    // int m_nneutcands;
    ROOT::Math::XYZVector m_vtx;
    ROOT::Math::XYZVector m_mupath;

    // std::vector<NeutronMultiplicity::NeutCand*> m_cands;  // the candidates it contains //moved to public?
    bool _is_cands_set = false;

    bool _recoset = false;
    bool _truthset = false;

   public:
    int m_ncands = 0;                                             // total number of cands in event
    int m_nneutcands = 0;                                         // total number of cands passing neutron selection
    std::vector<std::unique_ptr<NeutCand>> m_cands = {};          // the candidates the event has
    std::vector<std::unique_ptr<NeutCand>> m_neutcands = {};      // the candidates that pass neutron selection
    std::vector<std::unique_ptr<NeutCand>> m_trueneutcands = {};  // the candidates that pass neutron selection

   public:
    // TOOD: make neutron config vars in CVUniverse
    NeutEvent(NuConfig config, int n_neutcands, ROOT::Math::XYZVector vtx, ROOT::Math::XYZVector mupath, std::vector<int> order = {});  // configure number of cands and set up the cands internally based off how many there are
    NeutEvent(int n_neutcands, ROOT::Math::XYZVector vtx, ROOT::Math::XYZVector mupath);
    NeutEvent(NuConfig config);  // would need to set up cands separately using SetCands
    NeutEvent();
    ~NeutEvent() = default; //{

    // ~NeutEvent() {
    //     for (auto cand : m_cands) {
    //         delete cand;
    //     }
    //     m_cands.clear();
    // }

    void SetConfig(NuConfig config);
    // NeutEvent();
    void SetCands(int n_neutcands, ROOT::Math::XYZVector vtx, ROOT::Math::XYZVector mupath);

   private:
    void ClearCands();  // This is to clean up, called internally in SetCands if some cands are set.

   public:
    // Set the reco variables for reco and truth. This is necessary to handle both data and MC without issues
    void SetReco(std::vector<int> blobIDs, std::vector<int> is3Ds, std::vector<double> EDeps, std::vector<double> clusterMaxEs, std::vector<ROOT::Math::XYZVector> positions);
    void SetTruth(std::vector<int> truthPIDs, std::vector<int> truthTopMCPIDs, std::vector<double> truthTopMomentumsX, std::vector<double> truthTopMomentumsY, std::vector<double> truthTopMomentumsZ);

    bool GetIsTruthSet();

    std::vector<std::unique_ptr<NeutCand>>& GetCands();                 // Get all blobs
    std::vector<std::unique_ptr<NeutCand>>& GetNeutCands();             // Get just the ones passing neutron cuts
    std::vector<std::unique_ptr<NeutCand>>& GetTrueNeutCands();         // Get cands that are actually neutrons (need truth set)
    std::unique_ptr<NeutronMultiplicity::NeutCand> GetCand(int index);  // This makes a copy of a cand to access info outside of neutevent

    double GetTotNeutCandEDep(int max_ncands);

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
    static bool compare_cands(std::unique_ptr<NeutCand>& cand1, std::unique_ptr<NeutCand>& cand2) {return (cand1 > cand2);}

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