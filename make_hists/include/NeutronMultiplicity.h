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

const std::vector<double> view_angles = {0.0,         // 3D
                                         0.0,         // X view
                                         M_PI / 3,    // U? view
                                         -M_PI / 3};  // V? view

class NeutCand {
   public:
    int m_blobID = -1;                                              // which blob
    int m_is3D = -1;                                                // is it 3D?
    int m_view = 0;                                                   // 0 is none, 1 is x, 2 is u?, 3 is v?
    double m_recoEDep = 0.0;                                        // how much energy does it deposit?
    double m_clusterMaxE = 0.0;                                     // Max cluster Energy
    ROOT::Math::XYZVector m_begposition = ROOT::Math::XYZVector();  // where is it?
    ROOT::Math::XYZVector m_endposition = ROOT::Math::XYZVector();  // where does it end
    ROOT::Math::XYZVector m_flightpath = ROOT::Math::XYZVector();   // which direction did it travel from the vtx????
    ROOT::Math::XYZVector m_trackend = ROOT::Math::XYZVector();     // If there is a track, where did it end (detector coords)

    // Truth vars
    int m_truthPID = -1;                                            // PID of most recent GEANT Parent
    int m_truthTopMCPID = -1;                                       // PID of the GENIE parent
    ROOT::Math::XYZVector m_TopMomentum = ROOT::Math::XYZVector();  // which direction did it travel from the vtx????

    bool m_recoset = false;
    bool m_truthset = false;

    bool _is_candtrackend_set = false;

    // CTORs
    NeutCand();  // default
    NeutCand(int blobID, int is3D, int view, double recoEDep, ROOT::Math::XYZVector begposition, ROOT::Math::XYZVector endposition);
    // NeutCand(NeutCand& cand);

    ~NeutCand() = default;
    // reco functions
    void SetReco(int blobID, int is3D, int view, double recoEDep, double clusterMaxE, ROOT::Math::XYZVector begposition, ROOT::Math::XYZVector endposition, ROOT::Math::XYZVector flightpath);
    void SetReco(int blobID, int is3D, int view, double recoEDep, double clusterMaxE, ROOT::Math::XYZVector begposition, ROOT::Math::XYZVector endposition, ROOT::Math::XYZVector flightpath, ROOT::Math::XYZVector trackendpath);

    // SetBlobID(int index);

    // truth functions
    void SetTruth(int truthPID, int truthTopMCPID, ROOT::Math::XYZVector TopMomentum);

    int GetCandBlobID();
    int GetCandIs3D();
    int GetCandView();
    double GetCandRecoEDep();
    double GetCandMaxClusterE();
    double GetCandLength();

    ROOT::Math::XYZVector GetCandPosition();
    ROOT::Math::XYZVector GetCandViewPosition();
    ROOT::Math::XYZVector GetCandFlightPath();
    ROOT::Math::XYZVector GetCandTrackFlightPath();

    double GetCandVtxDist();  // TODO: Andrew does something weird with this
    double GetCandVtxZDist();
    double GetCandVtxTDist();
    int GetCandTruthPID();
    int GetCandTruthTopPID();

    double GetCandTruthAngleFromParent();
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
    double m_maxlength = -1.;                  // Set Maximum length for the track, may be deprecated bc not really useful
    double m_trackenddist_max = -1.;           // Check val set in config, in mm
    std::vector<std::pair<double, double>> m_vtxdist_edep;
    bool _is_vtxdist_edep_set = false;
    
    // int m_nneutcands;
    ROOT::Math::XYZVector m_vtx;
    ROOT::Math::XYZVector m_mupath;
    ROOT::Math::XYZVector m_trackend;  // not every event has a proton track, should be entered as -9999 for each dim if no proton track

    // std::vector<NeutronMultiplicity::NeutCand*> m_cands;  // the candidates it contains //moved to public?
    bool _is_config_set = false;
    bool _is_cands_set = false;
    bool _is_neutcands_set = false;
    bool _is_trueneutcands_set = false;
    bool _recoset = false;
    bool _truthset = false;
    bool m_evthastrack = false;  // Check bool to see if event has a track

    // More complicated stuff


   public:
    int m_ncands = 0;                                             // total number of cands in event
    int m_nneutcands = 0;                                         // total number of cands passing neutron selection
    int m_ntrueneutcands = 0;                                     // total number of cands passing neutron selection
    std::vector<std::unique_ptr<NeutCand>> m_cands = {};          // the candidates the event has
    std::vector<std::unique_ptr<NeutCand>> m_neutcands = {};      // the candidates that pass neutron selection
    std::vector<std::unique_ptr<NeutCand>> m_trueneutcands = {};  // the candidates that pass neutron selection

   public:
    // TOOD: make neutron config vars in CVUniverse
    NeutEvent(NuConfig config, int n_neutcands, ROOT::Math::XYZVector vtx, ROOT::Math::XYZVector mupath, ROOT::Math::XYZVector trackend);  // configure number of cands and set up the cands internally based off how many there are
    NeutEvent(int ncands, ROOT::Math::XYZVector vtx, ROOT::Math::XYZVector mupath, ROOT::Math::XYZVector trackend);
    NeutEvent(NuConfig config);  // would need to set up cands separately using SetCands
    NeutEvent();

    ~NeutEvent() {
        m_cands.clear();
        m_neutcands.clear();
        m_trueneutcands.clear();
    }

    void SetConfig(NuConfig config);
    void Reset(); // Used to clear everything except what comes from the config
    // NeutEvent();
    // void SetCands(int n_neutcands, ROOT::Math::XYZVector vtx, ROOT::Math::XYZVector mupath);
    void SetCands(int ncands, ROOT::Math::XYZVector vtx, ROOT::Math::XYZVector mupath, ROOT::Math::XYZVector trackend);

   private:
    // void ClearCands();  // This is to clean up, called internally in SetCands if some cands are set.
    void SetNeutCands();
    void SetTrueNeutCands();
   public:
    // Set the reco variables for reco and truth. This is necessary to handle both data and MC without issues
    void SetReco(std::vector<int> blobIDs, std::vector<int> is3Ds, std::vector<int> views, std::vector<double> EDeps, std::vector<double> clusterMaxEs, std::vector<ROOT::Math::XYZVector> begpositions, std::vector<ROOT::Math::XYZVector> endpositions);
    void SetTruth(std::vector<int> truthPIDs, std::vector<int> truthTopMCPIDs, std::vector<double> truthTopMomentumsX, std::vector<double> truthTopMomentumsY, std::vector<double> truthTopMomentumsZ);

    bool GetIsTruthSet();

    std::vector<std::unique_ptr<NeutCand>>& GetCands();                 // Get all blobs
    std::vector<std::unique_ptr<NeutCand>>& GetNeutCands();             // Get just the ones passing neutron cuts
    std::vector<std::unique_ptr<NeutCand>>& GetTrueNeutCands();         // Get cands that are actually neutrons (need truth set)
    
    const std::unique_ptr<NeutronMultiplicity::NeutCand>& GetCand(int index);  // This makes a copy of a cand to access info outside of neutevent
    const std::unique_ptr<NeutCand>& GetNeutCand(int index);
    const std::unique_ptr<NeutCand>& GetTrueNeutCand(int index);

    int GetNCands();
    int GetNNeutCands();
    int GetNTrueNeutCands();

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
    bool CandPassLength(int index);     // how long is the blob
    bool CandPassTrackEndDist( int index); // check if the blob is near a track end

    int GetCandTruthPID(int index);     // GEANT parent
    int GetCandTruthTopPID(int index);  // GENIE parent
    // Helper for ordering the cands
    // static bool compare_cands(const std::unique_ptr<NeutCand>& cand1, const std::unique_ptr<NeutCand>& cand2) { return (cand1 > cand2); }
    static bool compare_cands(const std::unique_ptr<NeutCand>& cand1, const std::unique_ptr<NeutCand>& cand2) { 
        return (cand1->GetCandRecoEDep() > cand2->GetCandRecoEDep()); 
    }
    // static bool compare_cands(std::shared_ptr<NeutCand> cand1, std::shared_ptr<NeutCand> cand2) { return (cand1 > cand2); }

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