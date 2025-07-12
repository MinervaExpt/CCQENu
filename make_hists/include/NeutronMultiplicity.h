
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
    TVector3 m_position;    // where is it?
    TVector3 m_flightpath;  // which direction did it travel from the vtx????

    // Truth vars
    int m_truthPID = -1;         // what is it in truth?
    int m_truthTopMCPID = -1;    // what is mc pid?

    bool m_recoset = false;
    bool m_truthset = false;

    // CTORs
    NeutCand();  // default
    NeutCand(int blobID, int is3D, int recoEDep, TVector3 position);

    // reco functions
    void SetReco(int blobID, int is3D, int recoEDep, TVector3 position, TVector3 flightpath); 
    
    // SetBlobID(int index);

    // truth functions
    void SetTruth(int truthPID, int TopMCPID);


    int GetCandBlobID();
    int GetCandIs3D();
    double GetCandRecoEDep();
    TVector3 GetCandPosition();
    TVector3 GetCandFlightPath();

    double GetCandVtxDist(); // TODO: Andrew does something weird with this

    int GetCandTruthPID();
    int GetCandTruthTopPID();

    // NeutCand(int index);  // give index, intialize internally
};

// class to hold all the neutron candidates for an event
class NeutEvent {
   private:
    // set up via config, contain info to check cands by
    double m_vtxdist_max = 10000.;  // in mm
    double m_vtxdist_min = 100.;    // in mm
    double m_zpos_min = 5980.0;      // in mm
    double m_zpos_max = 8422.0;      // in mm
    double m_muoncone_min = -1.0;    // in deg
    double m_muondist_min = 0.0;    // in mm
    double m_edep_min = 0.;         // in MeV

    int m_nneutcands;
    TVector3 m_vtx;
    TVector3 m_mupath;

    std::vector<NeutronMultiplicity::NeutCand*> m_cands;  // the candidates it contains
    bool _is_cands_set = false;

   public:
    // TOOD: make neutron config vars in CVUniverse
    NeutEvent(NuConfig config, int n_neutcands, TVector3 vtx, TVector3 mupath);  // configure number of cands and set up the cands internally based off how many there are
    NeutEvent(int n_neutcands, TVector3 vtx, TVector3 mupath);
    NeutEvent(NuConfig config);  // would need to set up cands separately using SetCands
    NeutEvent();

    // NeutEvent();
    void SetCands(int n_neutcands, TVector3 vtx, TVector3 mupath);
   private:
    void ClearCands(); // This is to clean up, called internally in SetCands if some cands are set.
   public:
    // Set the reco variables for reco and truth. This is necessary to handle both data and MC without issues
    void SetReco(std::vector<int> blobIDs, std::vector<int> is3Ds, std::vector<double> EDeps, std::vector<TVector3> positions);
    void SetTruth(std::vector<int> truthPIDs, std::vector<int> TopMCPIDs);

    // Get the candidates
    std::vector<NeutronMultiplicity::NeutCand*> GetNeutCands();  
    NeutronMultiplicity::NeutCand* GetMaxNeutCand();
    double GetMaxNeutCandE();
    NeutCand* GetCand(int index);

    int GetCandIsNeut(int index); // checks all the following 

    int CandIsOutsideMuonAngle(int index);  // check if outside angle from muon track
    int CandIsOutsideMuonDist(int index);   // check if outside distance from muon track
    int CandIsFiducial(int index);          // check if inside z bounds
    int CandIsIsolated(int index);          // check if far from vertex
    int CandIsHighE(int index);             // check if Edep is high enough

    int GetCandTruthPID(int index);
    int GetCandTruthTopPID(int index);

    // int GetCandIsNeut(int index);
//    private:
    // void CheckCandIsNeut(int index);  // internally check all the candidates if they're neutrons
};

}  // namespace NeutronMultipicity
#endif  // NEUTRONMULTIPLICITY_H