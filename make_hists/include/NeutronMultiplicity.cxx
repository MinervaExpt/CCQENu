// #include "include/NeutronMultiplicity.h"
#include "NeutronMultiplicity.h"

// TODO: Universe templating
namespace NeutronMultiplicity{
// NeutCand stuff
// NeutCand::NeutCand() {

// }
NeutCand::NeutCand() {};

NeutCand::NeutCand(int blobID, int is3D, int view,
                   double recoEDep,
                   ROOT::Math::XYZVector begposition, ROOT::Math::XYZVector endposition)
    : m_blobID(blobID),
      m_is3D(is3D),
      m_view(view),
      m_recoEDep(recoEDep),
      m_begposition(begposition),
      m_endposition(endposition) {
}

// Reco functions
void NeutCand::SetReco(int blobID, int is3D, int view,
                       double recoEDep, double clusterMaxE,
                       ROOT::Math::XYZVector begposition, ROOT::Math::XYZVector endposition, ROOT::Math::XYZVector flightpath) {
    m_recoset = true;
    m_blobID = blobID;
    m_is3D = is3D;
    m_view = view;
    m_recoEDep = recoEDep;
    m_clusterMaxE = clusterMaxE;
    m_begposition = begposition;
    m_endposition = endposition;
    m_flightpath = flightpath;
}

void NeutCand::SetReco(int blobID, int is3D, int view,
                       double recoEDep, double clusterMaxE,
                       ROOT::Math::XYZVector begposition, ROOT::Math::XYZVector endposition, ROOT::Math::XYZVector flightpath, ROOT::Math::XYZVector trackend) {
    m_recoset = true;
    m_blobID = blobID;
    m_is3D = is3D;
    m_view = view;
    m_recoEDep = recoEDep;
    m_clusterMaxE = clusterMaxE;
    m_begposition = begposition;
    m_endposition = endposition;
    m_flightpath = flightpath;
    m_trackend = trackend;
    _is_candtrackend_set = true;
}

void NeutCand::SetTruth(int truthPID, int truthTopMCPID, ROOT::Math::XYZVector TopMomentum) {
    m_truthset = true;
    m_truthPID = truthPID;
    m_truthTopMCPID = truthTopMCPID;
    m_TopMomentum = TopMomentum;
}

int NeutCand::GetCandBlobID() {
    if (!m_recoset) return -1;
    return m_blobID;
}

int NeutCand::GetCandIs3D() {
    if (!m_recoset) return -1;
    return m_is3D;
}

int NeutCand::GetCandView() {
    if (!m_recoset) return -1;
    return m_view;
}

double NeutCand::GetCandRecoEDep() {
    if (!m_recoset) return -1.0;
    return m_recoEDep;
}

double NeutCand::GetCandMaxClusterE() {
    if (!m_recoset) return -1.0;
    return m_clusterMaxE;
}

ROOT::Math::XYZVector NeutCand::GetCandPosition() {
    if (!m_recoset) return ROOT::Math::XYZVector();
    return m_begposition;
}

ROOT::Math::XYZVector NeutCand::GetCandViewPosition() {
    if (!m_recoset) return ROOT::Math::XYZVector();
    if (m_is3D) return m_begposition;
    if (m_view == 1) {
        return ROOT::Math::XYZVector(m_begposition.X(), 0.0, m_begposition.Z());
    } else {
        ROOT::Math::XYZVector view_pos(ROOT::Math::VectorUtil::RotateZ(m_begposition, NeutronMultiplicity::view_angles[m_view]));
        return ROOT::Math::XYZVector(view_pos.X(), 0.0, view_pos.Z());
    }
    return ROOT::Math::XYZVector();
}

double NeutCand::GetCandLength() {
    if (!m_recoset) return -1;
    return abs((m_begposition - m_endposition).Rho());
}

ROOT::Math::XYZVector NeutCand::GetCandFlightPath() {
    if (!m_recoset) return ROOT::Math::XYZVector();
    return m_flightpath;
}

ROOT::Math::XYZVector NeutCand::GetCandTrackFlightPath() {
    if (!m_recoset || !_is_candtrackend_set) return ROOT::Math::XYZVector(-9999.,-9999.,-9999.);
    if (m_is3D) return m_begposition - m_trackend;
    if (m_view == 1) {
        return ROOT::Math::XYZVector(m_begposition.X() - m_trackend.X(), 0.0, m_begposition.Z() - m_trackend.Z());
    } else {
        ROOT::Math::XYZVector view_candbegpos(ROOT::Math::VectorUtil::RotateZ(m_begposition, NeutronMultiplicity::view_angles[m_view]));
        ROOT::Math::XYZVector view_trackend(ROOT::Math::VectorUtil::RotateZ(m_trackend, NeutronMultiplicity::view_angles[m_view]));
        return ROOT::Math::XYZVector(view_candbegpos.X() - view_trackend.X(), 0.0, view_candbegpos.Z() - view_trackend.Z());
    }
}

double NeutCand::GetCandVtxDist() {
    if (!m_recoset) return -1.0;
    return m_flightpath.R();
}

double NeutCand::GetCandVtxZDist() {
    if (!m_recoset) return -99999.0;
    return m_flightpath.Z();
}

double NeutCand::GetCandVtxTDist() {
    if (!m_recoset) return -99999.0;
    return m_flightpath.Rho();
}

int NeutCand::GetCandTruthPID() {
    if (!m_truthset) {
        std::cout << "no truth set" << std::endl;
        return -1;
    }
    return m_truthPID;
}

int NeutCand::GetCandTruthTopPID() {
    if (!m_truthset) {
        std::cout << "no truth set" << std::endl;
        return -1;
    }
    return m_truthTopMCPID;
}

double NeutCand::GetCandTruthAngleFromParent() {
    if (!m_truthset) return -1.;
    // return m_TopMomentum.Angle(m_flightpath) * 180 / M_PI;
    return ROOT::Math::VectorUtil::Angle(m_TopMomentum, m_flightpath) * 180 / M_PI;
}

// NeutEvent stuff
// CTORS
NeutEvent::NeutEvent(NuConfig config,
                     int ncands,
                     ROOT::Math::XYZVector vtx, ROOT::Math::XYZVector mupath, ROOT::Math::XYZVector trackend) : m_vtx(vtx),
                                                                                                                m_mupath(mupath),
                                                                                                                m_ncands(ncands) {
    if (!_is_config_set) {
        SetConfig(config);
        _is_config_set = true;
    }
    if (trackend.Z() > 0) {
        m_evthastrack = true;
        m_trackend = trackend;
        // std::cout << "\ttrack end dist: \t" << m_trackend.X() << "\t" << m_trackend.Y() << "\t" << m_trackend.Z() << std::endl;
    }
    for (int i = 0; i < ncands; i++) {
        m_cands.emplace_back(std::make_unique<NeutCand>(NeutCand()));
    }
    _is_cands_set = true;
}

NeutEvent::NeutEvent(int ncands, ROOT::Math::XYZVector vtx, ROOT::Math::XYZVector mupath, ROOT::Math::XYZVector trackend) : m_vtx(vtx),
                                                                                             m_mupath(mupath),
                                                                                             m_ncands(ncands) {
    if (trackend.Z() == -9999) {
        m_evthastrack = true;
        m_trackend = trackend;
    }
    for (int i = 0; i < ncands; i++) {
        m_cands.emplace_back(std::make_unique<NeutCand>(NeutCand()));
    }
    _is_cands_set = true;
}

NeutEvent::NeutEvent(NuConfig config) {
    // std::cout << "WARNING: NeutronMultiplicity::NeutEvent: you are setting a neutevent without setting up candidates.\nYou will need to use NeutronMultiplicity::NeutEvent::SetCands()." << std::endl;
    SetConfig(config);
}

NeutEvent::NeutEvent() {}

void NeutEvent::SetConfig(NuConfig config) {
    if (config.IsMember("vtxdist_max")) m_vtxdist_max = config.GetDouble("vtxdist_max");
    if (config.IsMember("vtxdist_min")) m_vtxdist_min = config.GetDouble("vtxdist_min");
    if (config.IsMember("vtx_zdist_min")) m_vtx_zdist_min = config.GetDouble("vtx_zdist_min");
    if (config.IsMember("vtx_box")) m_vtx_box = config.GetDoubleVector("vtx_box");
    if (config.IsMember("zpos_max")) m_zpos_max = config.GetDouble("zpos_max");
    if (config.IsMember("zpos_min")) m_zpos_min = config.GetDouble("zpos_min");
    if (config.IsMember("muoncone_min")) m_muoncone_min = config.GetDouble("muoncone_min");
    if (config.IsMember("muondist_min")) m_muondist_min = config.GetDouble("muondist_min");
    if (config.IsMember("edep_min")) m_edep_min = config.GetDouble("edep_min");
    if (config.IsMember("Is3D")) m_req3D = config.GetInt("Is3D");
    if (config.IsMember("maxlength")) m_maxlength = config.GetDouble("maxlength");
    if (config.IsMember("trackenddist_max")) m_trackenddist_max = config.GetDouble("trackenddist_max");
    if (config.IsMember("vtxdist_edep_min")) {
        NuConfig subconfig = config.GetConfig("vtxdist_edep_min");

        for (auto band : subconfig.GetKeys()) {
            NuConfig band_config = subconfig.GetConfig(band);
            double tmp_edep = 100000.0;
            double tmp_vtxdist = 0.0;
            if (band_config.IsMember("edep_max")) {
                tmp_edep = band_config.GetDouble("edep_max");
            } else if (band_config.IsMember("edep_range")) {
                tmp_edep = band_config.GetDoubleVector("edep_range")[1];
            } 
            tmp_vtxdist = band_config.GetDouble("vtxdist_min");
            std::pair<double,double> mypair = {tmp_edep,tmp_vtxdist};
            m_vtxdist_edep.push_back(mypair);
        }
        _is_vtxdist_edep_set = true;
    }
}

void NeutEvent::Reset() {
    if (!_is_cands_set) return;
    _is_cands_set = false;
    _is_neutcands_set = false;
    _is_trueneutcands_set = false;
    _recoset = false;
    _truthset = false;
    m_evthastrack = false;

    m_vtx = ROOT::Math::XYZVector();
    m_mupath = ROOT::Math::XYZVector();
    m_trackend = ROOT::Math::XYZVector();

    if (m_ncands == 0) return;
    m_cands.clear();
    m_neutcands.clear();
    m_trueneutcands.clear();

    m_ncands = 0;
    m_nneutcands = 0;
    m_ntrueneutcands = 0;


}

// void NeutEvent::SetCands(int ncands, ROOT::Math::XYZVector vtx, ROOT::Math::XYZVector mupath) {
//     m_ncands = ncands;
//     m_vtx = vtx;
//     m_mupath = mupath;
//     if(_is_cands_set) {
//         std::cout << "WARNING: resetting cands" << std::endl;
//         this->ClearCands();
//     }
//     for (int i = 0; i < ncands; i++) {
//         m_cands.emplace_back(std::make_unique<NeutCand>(NeutCand()));
//     }
//     _is_cands_set = true;
// }

void NeutEvent::SetCands(int ncands,
                         ROOT::Math::XYZVector vtx, ROOT::Math::XYZVector mupath, ROOT::Math::XYZVector trackend) {
    if (_is_cands_set) {
        std::cout << "WARNING: resetting cands" << std::endl;
        this->Reset();
    }
    m_ncands = ncands;
    m_vtx = vtx;
    m_mupath = mupath;
    if (trackend.Z() > 0) {
        m_evthastrack = true;
        m_trackend = trackend;
        // std::cout << "\ttrack end dist: \t" << m_trackend.X() << "\t" << m_trackend.Y() << "\t" << m_trackend.Z() << std::endl;
    }
    for (int i = 0; i < ncands; i++) {
        m_cands.emplace_back(std::make_unique<NeutCand>(NeutCand()));
    }
    _is_cands_set = true;
}

void NeutEvent::SetReco(std::vector<int> blobIDs, std::vector<int> is3Ds, std::vector<int> views, std::vector<double> EDeps, std::vector<double> clusterMaxE, std::vector<ROOT::Math::XYZVector> begpositions, std::vector<ROOT::Math::XYZVector> endpositions) {
    if (blobIDs.size() != m_ncands) {
        std::cout << "ERROR: NeutronMultiplicity::NeutEvent::SetReco number of blobs doesn't match input.\n\tblobIDs.size() " << blobIDs.size() << "m_ncands " << m_ncands << std::endl;
        exit(1);
    }
    // Avoid filling with uninited memory
    if (m_ncands == 0) {
        _recoset = true;
        return;
    }
    for (int i = 0; i < m_ncands; i++) {
        ROOT::Math::XYZVector flightpath = ROOT::Math::XYZVector();
        if (!is3Ds[i]) {
            // std::cout << "view: " << views[i] << std::endl;
            // std::cout << "\tstart blob pos:\t" << begpositions[i].X() << "\t" << begpositions[i].Y() << "\t" << begpositions[i].Z() << std::endl;

            if (views[i] == 1) {
                begpositions[i].SetXYZ(begpositions[i].X(), m_vtx.Y(), begpositions[i].Z());
            } else {
                ROOT::Math::XYZVector tmp_begpos = ROOT::Math::VectorUtil::RotateZ(begpositions[i], NeutronMultiplicity::view_angles[views[i]]);
                ROOT::Math::XYZVector tmp_vtx = ROOT::Math::VectorUtil::RotateZ(m_vtx, NeutronMultiplicity::view_angles[views[i]]);
                // std::cout << "\tmid blob pos:  \t" << tmp_begpos.X() << "\t" << tmp_begpos.Y() << "\t" << tmp_begpos.Z() << std::endl;
                // std::cout << "\tmid vtx pos:   \t" << tmp_vtx.X() << "\t" << tmp_vtx.Y() << "\t" << tmp_vtx.Z() << std::endl;
                tmp_begpos.SetXYZ(tmp_begpos.X(), tmp_vtx.Y(), tmp_begpos.Z());
                begpositions[i] = ROOT::Math::VectorUtil::RotateZ(tmp_begpos, -view_angles[views[i]]);
            }
            // std::cout << "\tend blob pos:  \t" << begpositions[i].X() << "\t" << begpositions[i].Y() << "\t" << begpositions[i].Z() << std::endl;
        }
        flightpath = begpositions[i] - m_vtx;

        if (!m_evthastrack)
            m_cands[i]->SetReco(blobIDs[i], is3Ds[i], views[i], EDeps[i], clusterMaxE[i], begpositions[i], endpositions[i], flightpath);
        else
            m_cands[i]->SetReco(blobIDs[i], is3Ds[i], views[i], EDeps[i], clusterMaxE[i], begpositions[i], endpositions[i], flightpath, m_trackend);
    }
    std::sort(m_cands.begin(), m_cands.end(), compare_cands);
    _recoset = true;

    this->SetNeutCands();
}

void NeutEvent::SetTruth(std::vector<int> truthPIDs, std::vector<int> truthTopMCPIDs, std::vector<double> truthTopMomentumsX, std::vector<double> truthTopMomentumsY, std::vector<double> truthTopMomentumsZ) {
    if (truthPIDs.size() != m_ncands) {
        std::cout << "ERROR: NeutronMultiplicity::NeutEvent::SetTruth number of blobs doesn't match input.\n\truthPIDs.size() " << truthPIDs.size() << "m_ncands " << m_ncands << std::endl;
        exit(1);
    }
    // Avoid filling with uninited memory
    if (m_ncands == 0) {
        _truthset = true;
        return;
    }
    for (int i = 0; i < m_ncands; i++) {
        int blobID(m_cands[i]->m_blobID);
        ROOT::Math::XYZVector TopMomentum(truthTopMomentumsX[blobID], truthTopMomentumsY[blobID], truthTopMomentumsZ[blobID]);
        m_cands[i]->SetTruth(truthPIDs[blobID], truthTopMCPIDs[blobID], TopMomentum);
    }
    if (_is_neutcands_set) {
        for (auto &cand : m_neutcands) {
            int blobID(cand->m_blobID);
            // std::cout << "neutblobid " << blobID << std::endl;
            ROOT::Math::XYZVector TopMomentum(truthTopMomentumsX[blobID], truthTopMomentumsY[blobID], truthTopMomentumsZ[blobID]);
            cand->SetTruth(truthPIDs[blobID], truthTopMCPIDs[blobID], TopMomentum);
        }
    }
    
    _truthset = true;
    this->SetTrueNeutCands();
}

void NeutEvent::SetNeutCands() {
    assert(_recoset);
    if(_is_neutcands_set) {
        std::cout << " m_neutcands set already. Clearing..." << std::endl;
        m_neutcands.clear();
        m_nneutcands = 0;
    }
    for (int i = 0; i < m_ncands; i++) {
        if (GetCandIsNeut(i)) {
            m_neutcands.emplace_back(std::make_unique<NeutCand>(NeutCand(*m_cands[i])));
            m_nneutcands += 1;
        }
    }
    _is_neutcands_set = true;
}

void NeutEvent::SetTrueNeutCands() {
    assert(_truthset);
    if (_is_trueneutcands_set) {
        m_trueneutcands.clear();
        m_ntrueneutcands = 0;
    }
    for (int i = 0; i < m_ncands; i++) {
        // Only check if it's fiducial and is a true neutron
        if (CandPassFiducial(i) && (m_cands[i]->GetCandTruthTopPID() == 2112 || abs(m_cands[i]->GetCandTruthTopPID()) == 13 || m_cands[i]->GetCandTruthTopPID() == 0)) {
            m_trueneutcands.emplace_back(std::make_unique<NeutCand>(NeutCand(*m_cands[i])));
            m_ntrueneutcands +=1;
        }
    }
    _is_trueneutcands_set = true;
}


std::vector<std::unique_ptr<NeutCand>>& NeutEvent::GetCands() {
    // Be careful with this, it doesn't necessarily have anything in those cands
    assert(_is_cands_set);
    return m_cands;
}

std::vector<std::unique_ptr<NeutCand>>& NeutEvent::GetNeutCands() {
    assert(_is_neutcands_set);
    return m_neutcands;
}

std::vector<std::unique_ptr<NeutCand>>& NeutEvent::GetTrueNeutCands() {
    assert(_is_trueneutcands_set);
    return m_trueneutcands;
}

const std::unique_ptr<NeutCand>& NeutEvent::GetCand(int index) {
    assert(_is_cands_set);
    assert(index < m_ncands);
    return m_cands[index];
}

const std::unique_ptr<NeutCand>& NeutEvent::GetNeutCand(int index) {
    assert(_is_neutcands_set);
    assert(index < m_nneutcands);
    return m_neutcands[index];
}

const std::unique_ptr<NeutCand>& NeutEvent::GetTrueNeutCand(int index) {
    assert(_is_trueneutcands_set);
    assert(index < m_ntrueneutcands);
    return m_trueneutcands[index];
}

int NeutEvent::GetNCands() {
    assert(_is_cands_set);
    return m_ncands;
}

int NeutEvent::GetNNeutCands() {
    // assert(_is_cands_set);
    assert(_is_neutcands_set);
    return m_nneutcands;
}

int NeutEvent::GetNTrueNeutCands() {
    // assert(_is_cands_set);
    assert(_is_trueneutcands_set);
    return m_ntrueneutcands;
}

bool NeutEvent::GetIsTruthSet() {
    return _truthset;
}


double NeutEvent::GetTotNeutCandEDep(int max_ncands) {
    if (m_nneutcands == 0) return 0.;
    double edep = 0.;
    for (unsigned int i = 0; i < m_nneutcands; i++) {
        if (i == max_ncands) break;
        edep += m_cands[i]->m_recoEDep;
    }
    return edep;
}

bool NeutEvent::GetCandIsNeut(int index) {
    if (m_ncands == 0) return true;
    return (CandPassMuonAngle(index) && 
            CandPassMuonDist(index) && 
            CandPassFiducial(index) && 
            CandPassVtxDist(index) && 
            CandPassVtxZDist(index) &&
            CandPassEDep(index) && 
            CandPassIs3D(index) &&
            CandPassVtxBox(index)
        );
}


bool NeutEvent::CandPassMuonAngle(int index) {
    if (m_muoncone_min <= 0.0) return true;
    ROOT::Math::XYZVector candfp = m_cands[index]->m_flightpath;
    // double angle = m_mupath.Angle(candfp) * 180. / M_PI;  // need this in deg (for user configurability)
    double angle = ROOT::Math::VectorUtil::Angle(m_mupath, candfp) * 180. / M_PI;  // need this in deg (for user configurability)
    return angle >= m_muoncone_min;
}

bool NeutEvent::CandPassMuonDist(int index) {
    if (m_muondist_min <= 0.0) return true;
    ROOT::Math::XYZVector candfp = m_cands[index]->m_flightpath;
    // double angle = m_mupath.Angle(candfp);
    // double dist = candfp.Mag() * std::sin(angle);
    double angle = ROOT::Math::VectorUtil::Angle(m_mupath,candfp);
    double dist = candfp.R() * std::sin(angle);
    return dist >= m_muondist_min;
}

bool NeutEvent::CandPassFiducial(int index) {
    if (m_zpos_min < 0. &&  m_zpos_max < 0.) return true;
    double candzpos = m_cands[index]->GetCandPosition().Z();
    return (candzpos >= m_zpos_min && candzpos <= m_zpos_max);
    // ROOT::Math::XYZVector candpos = m_cands[index]->GetCandPosition();
    // if (candpos.Z() >= m_zpos_min && candpos.Z() <= m_zpos_max)
    //     return true;
    // else
    //     return false;
    // return (candpos.Z() >= m_zpos_min && candpos.Z() <= m_zpos_max);
}

bool NeutEvent::CandPassVtxDist(int index) {
    if (m_vtxdist_min <= 0 && !_is_vtxdist_edep_set) return true;
    bool pass = false;
    double dist = m_cands[index]->GetCandVtxDist();
    if (_is_vtxdist_edep_set) {
        double edep = m_cands[index]->GetCandRecoEDep();
        for (auto band : m_vtxdist_edep) {
            if (edep < band.first) {
                // std::cout << "edep, vtx dist: " << edep << ", " << dist << "\tband " << band.first << ", " << band.second << std::endl;
                return dist >= band.second;
            }
        }
        return false;
    }
    // if (m_cands[index]->GetCandRecoEDep() < 12.0) return true;
    return dist >= m_vtxdist_min;
}

bool NeutEvent::CandPassVtxZDist(int index) {
    if (m_vtx_zdist_min <= 0) return true;
    double zdist = m_cands[index]->GetCandFlightPath().Z();

    return zdist >= m_vtx_zdist_min;
}

bool NeutEvent::CandPassVtxBox(int index) {
    if (m_vtx_box[0] < 0. || m_vtx_box[1] < 0.) return true;  // default value
    ROOT::Math::XYZVector fp = m_cands[index]->GetCandFlightPath();
    if (fp.Z() <= m_vtx_box[0] && fp.Rho() <= m_vtx_box[1]) return false;
    return true;
}

bool NeutEvent::CandPassEDep(int index) {
    if (m_edep_min <=0 ) return true;
    double edep = m_cands[index]->GetCandRecoEDep();
    return edep >= m_edep_min;
}

bool NeutEvent::CandPassIs3D(int index) {
    if (m_req3D == 0) return true;  // m_req3D should only be set to 1 (3D only), -1 (2D only), 0 (both, default)
    int is3D = m_cands[index]->GetCandIs3D();
    if (is3D < 0) return false;
    if (m_req3D == 1)
        return is3D == 1;
    if (m_req3D == -1)
        return is3D == 0;
    return false;
    // int pass = m_req3D == 1 ? is3D == 1 : is3D == 0;
    // return pass;
}

bool NeutEvent::CandPassLength(int index) {
    if (m_maxlength <= 0) return true;
    return false;
}

bool NeutEvent::CandPassTrackEndDist(int index) {
    if (!m_evthastrack || m_trackenddist_max <= 0.0) return true;
    if (m_cands[index]->GetCandIs3D()) {
        ROOT::Math::XYZVector cand_pos = m_cands[index]->GetCandPosition();
        double trackenddist = (cand_pos - m_trackend).R();
        return trackenddist > m_trackenddist_max;
    } else {
        ROOT::Math::XYZVector candview_pos = m_cands[index]->GetCandViewPosition();
        if (m_cands[index]->GetCandView() == 1) {
            ROOT::Math::XYZVector tmp_candview_pos = ROOT::Math::XYZVector(candview_pos.X(), m_trackend.Y(), candview_pos.Z());
            return (tmp_candview_pos - m_trackend).R() > m_trackenddist_max;
        } else {
            ROOT::Math::XYZVector candview_trackend(ROOT::Math::VectorUtil::RotateZ(m_trackend, NeutronMultiplicity::view_angles[m_cands[index]->GetCandView()]));
            ROOT::Math::XYZVector tmp_candview_pos = ROOT::Math::XYZVector(candview_pos.X(), candview_trackend.Y(), candview_pos.Z());
            return (tmp_candview_pos - candview_trackend).R() > m_trackenddist_max;
        }
    }
    return false;
}

int NeutEvent::GetCandTruthPID(int index) {
    return m_cands[index]->GetCandTruthPID();
}

int NeutEvent::GetCandTruthTopPID(int index) {
    return m_cands[index]->GetCandTruthTopPID();
}

void NeutEvent::Configure(NuConfig config) {
    // if (config.IsMember("global")) {
    //     NuConfig globalsel_config = config.GetValue("global");
    //     for (auto var : globalsel_config.GetKeys()) {
    //         NuConfig varconfig = globalsel_config.GetConfig(var);
    //         if (varconfig.IsMember("equals"))
    //             m_global_equals[var] = varconfig.GetDouble("equals");
    //         if (varconfig.IsMember("min"))
    //             m_global_min[var] = varconfig.GetDouble("min");
    //         if (varconfig.IsMember("max"))
    //             m_global_max[var] = varconfig.GetDouble("max");
    //     }
    // }
    // if (config.IsMember("subselections")) {
    //     NuConfig subsel_config = config.GetValue("subselections");
    //     for (auto sub : subsel_config.GetKeys()) {
    //         for (auto var : subsel_config.GetKeys()) {
    //             NuConfig varconfig = subsel_config.GetConfig(var);
    //             if (varconfig.IsMember("equals"))
    //                 m_subsel_equals[sub][var] = varconfig.GetDouble("equals");
    //             if (varconfig.IsMember("min"))
    //                 m_subsel_min[sub][var] = varconfig.GetDouble("min");
    //             if (varconfig.IsMember("max"))
    //                 m_subsel_max[sub][var] = varconfig.GetDouble("max");
    //         }
    //     }
    // }


    if (config.IsMember("selection")) {
        NuConfig selection_config = config.GetValue("selection");
        for (auto var : selection_config.GetKeys()) {
            NuConfig varconfig = selection_config.GetConfig(var);
            if (varconfig.IsMember("equals"))
                m_equals[var] = varconfig.GetDouble("equals");
            if (varconfig.IsMember("min"))
                m_min[var] = varconfig.GetDouble("min");
            if (varconfig.IsMember("max"))
                m_max[var] = varconfig.GetDouble("max");
            m_selectionvars.push_back(std::string(var));
            m_plotvars.push_back(std::string(var));
        }
    }
    if (config.IsMember("plot")) {
        std::vector<std::string> i_plotvars = config.GetStringVector("i_plotvars");
        for (auto var : i_plotvars) {
            m_plotvars.push_back(var);
        }
    }
}

// bool NeutEvent::CheckCand(int index) {
//     for ()
// }

bool NeutEvent::CheckVal(std::string varname, double val) {
    if (std::find(m_selectionvars.begin(), m_selectionvars.end(), varname) == m_selectionvars.end()) {
        return 1;
    }
    if (m_equals.find(varname) != m_equals.end())
        // If equal set, return if equal to it
        return val == m_equals[varname];
    bool pass_min = 0;
    if (m_min.find(varname) != m_min.end())
        // If  if min set and lower than minimum, return 0
        if (val < m_min[varname])
            return 0;
    // else, pass minimum
    pass_min = 1;
    if (m_max.find(varname) != m_max.end())
        // If max set, return pass at or if below it
        return val <= m_max[varname];
    // If no max set, return pass_min (default 0)
    return pass_min;
}

void NeutEvent::SetReco(std::map<std::string, std::vector<int>> intVals, std::map<std::string, std::vector<double>> doubleVals) {
}

void NeutEvent::SetTruth(std::map<std::string, std::vector<int>> intVals, std::map<std::string, std::vector<double>> doubleVals) {
}

}  // namespace NeutronMultiplicity
