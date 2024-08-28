#include "include/NeutronMultiplicity.h"
#include "NeutronMultiplicity.h"

// TODO: Universe templating
namespace NeutronMultiplicity{
// NeutCand stuff
// NeutCand::NeutCand() {

// }
NeutCand::NeutCand() {};
// NeutCand::NeutCand(int index) : m_blobID(GetBlobID(index)),
//                                 m_is3D(GetBlobIs3D(index)),
//                                 m_recoEDep(GetBlobTotE(index)),
//                                 m_truthPID(GetBlobMCPID(index)),
//                                 m_truthTopMCPID(GetBlobTopMCPID(index)),
//                                 m_position(GetBlobBegPosition(index)) {
//     // TODO: set flight path                                
// }

NeutCand::NeutCand(int blobID, int is3D, int recoEDep, TVector3 position) : m_blobID(blobID),
                                                                            m_is3D(is3D),
                                                                            m_recoEDep(recoEDep),
                                                                            m_position(position) {
}

// Reco functions
void NeutCand::SetReco(int blobID, int is3D, int recoEDep, TVector3 position, TVector3 flightpath) {
    m_recoset = true;
    m_blobID = blobID;
    m_is3D = is3D;
    m_recoEDep = recoEDep;
    m_position = position;
    m_flightpath = flightpath;
}

void NeutCand::SetTruth(int truthPID, int truthTopMCPID) {
    m_truthset = true;
    m_truthPID = truthPID;
    m_truthTopMCPID = truthTopMCPID;
}

int NeutCand::GetCandBlobID() {
    if (!m_recoset) return -1;
    return m_blobID;
}

int NeutCand::GetCandIs3D() {
    if (!m_recoset) return -1;
    return m_is3D;
}

double NeutCand::GetCandRecoEDep() {
    if (!m_recoset) return -1.0;
    return m_recoEDep;
}

TVector3 NeutCand::GetCandPosition() {
    if (!m_recoset) return TVector3();
    return m_position;
}

TVector3 NeutCand::GetCandFlightPath() {
    if (!m_recoset) return TVector3();
    return m_flightpath;
}

double NeutCand::GetCandVtxDist() {
    if (!m_recoset) return -1.0;
    return m_flightpath.Mag();
}

int NeutCand::GetCandTruthPID() {
    if (!m_truthset) return -1;
    return m_truthTopMCPID;
}

int NeutCand::GetCandTruthTopPID() {
    if (!m_truthset) return -1;
    return m_truthPID;
}

// NeutEvent stuff
// CTORS
NeutEvent::NeutEvent(NuConfig config, int n_neutcands, TVector3 vtx, TVector3 mupath) : m_vtx(vtx),
                                                                                        m_mupath(mupath),
                                                                                        m_nneutcands(n_neutcands) {
    if (config.IsMember("vtxdist_max")) m_vtxdist_max = config.GetDouble("vtxdist_max");
    if (config.IsMember("vtxdist_min")) m_vtxdist_min = config.GetDouble("vtxdist_min");
    if (config.IsMember("zpos_max")) m_zpos_max = config.GetDouble("zpos_max");
    if (config.IsMember("zpos_min")) m_zpos_min = config.GetDouble("zpos_min");
    if (config.IsMember("muoncone_min")) m_muoncone_min = config.GetDouble("muoncone_min");
    if (config.IsMember("muondist_min")) m_muondist_min = config.GetDouble("muondist_min");
    if (config.IsMember("edep_min")) m_edep_min = config.GetDouble("edep_min");
    for (int i = 0; i < n_neutcands; i++) {
        NeutCand* cand = new NeutCand();
        m_cands.push_back(cand);
    }
    _is_cands_set = true;
}

NeutEvent::NeutEvent(int n_neutcands, TVector3 vtx, TVector3 mupath) : m_vtx(vtx),
                                                                       m_mupath(mupath),
                                                                       m_nneutcands(n_neutcands) {
    for (int i = 0; i < n_neutcands; i++) {
        NeutCand* cand = new NeutCand();
        m_cands.push_back(cand);
    }
    _is_cands_set = true;
}

NeutEvent::NeutEvent(NuConfig config) {
    std::cout << "WARNING: NeutronMultiplicity::NeutEvent: you are setting a neutevent without setting up candidates.\nYou will need to use NeutronMultiplicity::NeutEvent::SetCands()." << std::endl;
    if (config.IsMember("vtxdist_max")) m_vtxdist_max = config.GetDouble("vtxdist_max");
    if (config.IsMember("vtxdist_min")) m_vtxdist_min = config.GetDouble("vtxdist_min");
    if (config.IsMember("zpos_max")) m_zpos_max = config.GetDouble("zpos_max");
    if (config.IsMember("zpos_min")) m_zpos_min = config.GetDouble("zpos_min");
    if (config.IsMember("muoncone_min")) m_muoncone_min = config.GetDouble("muoncone_min");
    if (config.IsMember("muondist_min")) m_muondist_min = config.GetDouble("muondist_min");
    if (config.IsMember("edep_min")) m_edep_min = config.GetDouble("edep_min");
}

NeutEvent::NeutEvent() {}

void NeutEvent::SetCands(int n_neutcands, TVector3 vtx, TVector3 mupath) {
    m_nneutcands = n_neutcands;
    m_vtx = vtx;
    m_mupath = mupath;
    if(_is_cands_set) {
        std::cout << "WARNING: resetting cands" << std::endl;
        this->ClearCands();
    }
    for (int i = 0; i < n_neutcands; i++) {
        NeutCand* cand = new NeutCand();
        m_cands.push_back(cand);
    }
    _is_cands_set = true;
}

void NeutEvent::ClearCands() {
    if (!_is_cands_set) return;
    for (auto cand : m_cands){
        delete cand;
    }
    m_cands.clear();
    _is_cands_set = false;
}

void NeutEvent::SetReco(std::vector<int> blobIDs, std::vector<int> is3Ds, std::vector<double> EDeps, std::vector<TVector3> positions) {
    if (blobIDs.size() != m_nneutcands) {
        std::cout << "ERROR: NeutronMultiplicity - number of blobs doesn't match input." << std::endl;
        exit(1);
    }
    for (int i = 0; i < m_nneutcands; i++) {
        TVector3 flightpath = positions[i] - m_vtx;
        m_cands[i]->SetReco(blobIDs[i], is3Ds[i], EDeps[i], positions[i], flightpath);
    }
}

void NeutEvent::SetTruth(std::vector<int> truthPIDs, std::vector<int> truthTopMCPIDs) {
    if (truthPIDs.size() != m_nneutcands) {
        std::cout << "ERROR: NeutronMultiplicity - number of blobs doesn't match input." << std::endl;
        exit(1);
    }
    for (int i = 0; i < m_nneutcands; i++) {
        m_cands[i]->SetTruth(truthPIDs[i], truthTopMCPIDs[i]);
    }
}

std::vector<NeutronMultiplicity::NeutCand*> NeutEvent::GetNeutCands() {
    return m_cands;
}

NeutronMultiplicity::NeutCand* NeutEvent::GetMaxNeutCand() {
    std::pair<int, double> max_edep(0, 0.0);
    for (int i = 0; i < m_nneutcands; i++) {
        if (m_cands[i]->m_recoEDep > max_edep.second && GetCandIsNeut(i))
            max_edep = {i, m_cands[i]->m_recoEDep};
    }
    return m_cands[max_edep.first];
}

NeutCand* NeutEvent::GetCand(int index) {
    return m_cands[index];
}

int NeutEvent::GetCandIsNeut(int index) {
    // return (CandIsOutsideMuonDist(index) && CandIsFiducial(index) && CandIsIsolated(index) && CandIsHighE(index));
    return (CandIsOutsideMuonAngle(index) && CandIsOutsideMuonDist(index) && CandIsFiducial(index) && CandIsIsolated(index) && CandIsHighE(index));
}

int NeutEvent::CandIsOutsideMuonAngle(int index) {
    if (m_muoncone_min < 0.0) return 1;
    TVector3 candfp = m_cands[index]->GetCandFlightPath();
    double angle = m_mupath.Angle(candfp) * 180. / M_PI; // need this in deg (for user configurability)
    return angle > m_muoncone_min;
}

int NeutEvent::CandIsOutsideMuonDist(int index) {
    TVector3 candfp = m_cands[index]->GetCandFlightPath();
    double angle = m_mupath.Angle(candfp);
    double dist = candfp.Mag() * std::sin(angle);
    return dist > m_muondist_min;
}

int NeutEvent::CandIsFiducial(int index) {
    TVector3 candpos = m_cands[index]->GetCandPosition();
    return (candpos.Z() > m_zpos_min && candpos.Z() < m_zpos_max);
}

int NeutEvent::CandIsIsolated(int index) {
    double dist = m_cands[index]->GetCandVtxDist();
    return dist > m_vtxdist_min;
}

int NeutEvent::CandIsHighE(int index) {
    double edep = m_cands[index]->GetCandRecoEDep();
    return edep > m_edep_min;
}

int NeutEvent::GetCandTruthPID(int index) {
    return m_cands[index]->GetCandTruthPID();
}

int NeutEvent::GetCandTruthTopPID(int index) {
    return m_cands[index]->GetCandTruthTopPID();
}

// int NeutEvent::GetCandIsNeut(int index) {
//     NeutCand* cand = m_cands[index];
//     return (cand->GetCandIs3D() == 1 && (cand->GetCandPosition().Z() < m_zpos_max && cand->GetCandPosition().Z() > m_zpos_min) && (cand->GetCandVtxDist() > m_vtxdist_min && cand->GetCandVtxDist() < m_vtxdist_max) && )
// }

}  // namespace NeutronMultiplicity
