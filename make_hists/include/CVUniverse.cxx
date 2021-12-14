// ========================================================================
// Base class for an un-systematically shifted (i.e. CV) universe.
// Implement "Get" functions for all the quantities that you need for your
// analysis.
//
// This class inherits from PU::sUniverse. PU::DCVU may already define
// your "Get" functions the way you want them. In that case, you  don't need to
// re-write them here.
// ========================================================================
#ifndef CVUNIVERSE_cxx
#define CVUNIVERSE_cxx

#include "include/CVUniverse.h"

#include <algorithm>

using namespace PlotUtils;

namespace {
  
  double MeVGeV = 0.001; // lazy conversion from MeV to GeV before filling histos
  bool m_useNeutronCVReweight = true;
  
}
  
  // ========================================================================
  // Get Weight
  // ========================================================================
  
  double CVUniverse::GetWeight() const {
    double wgt_flux_and_cv = 1., wgt_genie = 1., wgt_2p2h = 1.;
    double wgt_rpa = 1., wgt_mueff = 1.;
    double wgt_geant = 1.0;
    // flux + cv
    wgt_flux_and_cv = GetFluxAndCVWeight();

    // genie
    wgt_genie = GetGenieWeight();

    // 2p2h
    wgt_2p2h = GetLowRecoil2p2hWeight();

    // rpa
    wgt_rpa = GetRPAWeight();
    
     
    if(!IsTruth()) wgt_geant = GetGeantHadronWeight();
       // if (wgt_geant != 1.0) std::cout << ShortName() << wgt_geant << std::endl;
     

    // MINOS muon tracking efficiency
    if (!IsTruth() && IsMinosMatchMuon()) wgt_mueff = GetMinosEfficiencyWeight();

    return wgt_flux_and_cv * wgt_genie * wgt_2p2h * wgt_rpa * wgt_mueff * wgt_geant;
  }

  // ========================================================================
  // Write a "Get" function for all quantities access by your analysis.
  // For composite quantities (e.g. Enu) use a calculator function.
  //
  // Currently PlotUtils::MinervaUniverse may already define some functions
  // that you want. The future of these functions is uncertain. You might want
  // to write all your own functions for now.
  // ========================================================================
  
  int CVUniverse::GetMultiplicity() const{
    return GetInt("multiplicity");
  }
  
  int CVUniverse::GetDeadTime() const{
    return GetInt("phys_n_dead_discr_pair_upstream_prim_track_proj") ;
  }
  // ----------------------- Analysis-related Variables ------------------------
  
  
  int CVUniverse::GetIsMinosMatchTrack()const{
    return GetInt("muon_is_minos_match_track");
  }
    

  double CVUniverse::GetEnuHadGeV() const {
  // double GetEnuGeV() const {
    return CVUniverse::GetEmuGeV()+CVUniverse::GetHadronEGeV();
  }

  double CVUniverse::GetTrueEnuGeV() const {
    return GetDouble("mc_incomingE")*MeVGeV;
  }

  double CVUniverse::GetEnuCCQEGeV() const {
    int charge = GetAnalysisNuPDG() > 0? 1:-1;
    //std::cout << " before try" << GetEmu() <<  std::endl;
    double val = PlotUtils::nuEnergyCCQE( GetEmu(), GetPmu(), GetThetamu(), charge ); // un-PlotUtil's this?
    //std::cout << " try to getEnuCCQE" << val << std::endl;
    return val*MeVGeV;
  } // both neutrino and antinu

  double CVUniverse::GetTrueEnuCCQEGeV() const {
    int charge = GetAnalysisNuPDG() > 0? 1:-1;
    //std::cout << " before try" << GetEmu() <<  std::endl;
    double val = PlotUtils::nuEnergyCCQE( GetElepTrue(), GetPlepTrue(), GetThetalepTrue(), charge ); // un-PlotUtil's this?
    //std::cout << " try to getEnuCCQE" << val << std::endl;
    return val*MeVGeV;
  } // may be a better way to implement this

  double CVUniverse::GetQ2QEGeV() const {
    const double q2min = 0.001;
    int charge = GetAnalysisNuPDG() > 0? 1:-1;
    if (CVUniverse::GetEnuCCQEGeV()<=0.0)return 0.0;
    //std::cout<<"CVUniverse::GetQ2QE Cannot calculate neutrino energy "<<std::endl;
    else{
    // Q2 = 2.0*GetEnuCCQE() * ( GetEmu() - GetPmu() * cos( GetThetamu() ) ) - pow( MinervaUnits::M_mu, 2 );
      double q2 = PlotUtils::qSquaredCCQE( GetEmu(), GetPmu(), GetThetamu(), charge )*MeVGeV*MeVGeV;
    //  if (q2 < q2min)q2 =  q2min;
      return q2;
    }
    // return Q2;
  }

  double CVUniverse::GetTrueQ2QEGeV() const {
      const double q2min = 0.001;
      int charge = GetAnalysisNuPDG() > 0? 1:-1;
      double q2 = PlotUtils::qSquaredCCQE( GetElepTrue(), GetPlepTrue(), GetThetalepTrue(), charge )*MeVGeV*MeVGeV;
     // if (q2 < q2min)q2 =  q2min;
      return q2;
    }

  double CVUniverse::GetLog10Q2QEGeV() const {
    return std::log10( CVUniverse::GetQ2QEGeV() );
  }

  double CVUniverse::GetTrueLog10Q2QEGeV() const {
    return std::log10( GetTrueQ2QEGeV() );
  }


  // ------------------------------ Muon Variables -----------------------------

  double CVUniverse::GetEmuGeV() const {
    return std::sqrt(GetPmu()*GetPmu() + pow( MinervaUnits::M_mu, 2 ))*MeVGeV;
  }

  double CVUniverse::GetTrueEmuGeV() const {
    return GetElepTrue(); // not sure if this is right
  }

  double CVUniverse::GetPmuGeV() const {
    return GetPmu()*MeVGeV;
  }

  double CVUniverse::GetTruePmuGeV() const {
    return GetPlepTrue()*MeVGeV;
  }

  double CVUniverse::GetPparMuGeV() const {
  // double CVUniverse::GetPparMuGeV(bool istruth=false) const {
    return GetPmuGeV()*std::cos( GetThetamu() );
  }

  double CVUniverse::GetTruePparMuGeV() const {
    return GetTruePmuGeV()*std::cos( GetTrueThetamu() );
  }

  double CVUniverse::GetPperpMuGeV() const {
  // virtual double GetPperpMu(bool istruth=false) const {
    return GetPmuGeV()*std::sin( GetThetamu() );
  }

  double CVUniverse::GetTruePperpMuGeV() const {
    return GetTruePmuGeV()*std::sin( GetTrueThetamu() );
  }

  double CVUniverse::GetTrueThetaXmu() const {
    TVector3 p3lep( GetVecElem("mc_primFSLepton",0), GetVecElem("mc_primFSLepton",1), GetVecElem("mc_primFSLepton",2) );
      p3lep.RotateX(MinervaUnits::numi_beam_angle_rad);
      double px =  p3lep[0];
      double pz =  p3lep[2];
      //std::cout << "tx " << px << " " << pz << std::endl;
      return std::atan2(px,pz);
  }
  double CVUniverse::GetTrueThetaYmu() const {
    TVector3 p3lep( GetVecElem("mc_primFSLepton",0), GetVecElem("mc_primFSLepton",1), GetVecElem("mc_primFSLepton",2) );
      p3lep.RotateX(MinervaUnits::numi_beam_angle_rad);
      double py =  p3lep[1];
      double pz =  p3lep[2];
      //std::cout << "tx " << px << " " << pz << std::endl;
      return std::atan2(py,pz);
  }

  double CVUniverse::GetTrueThetamu() const {
     return GetThetalepTrue();
   }
  
  double CVUniverse::GetThetamuDegrees() const {
    return GetThetamu()*180/M_PI;
  }
  
  double CVUniverse::GetTrueThetamuDegrees() const {
    return GetThetalepTrue()*180/M_PI;
  }


  // ----------------------------- Proton Variables ----------------------------

  double CVUniverse::GetHadronEGeV() const {
    return (CVUniverse::GetCalRecoilEnergyGeV() + CVUniverse::GetNonCalRecoilEnergyGeV());
  }


  // ----------------------------- Recoil Variables ----------------------------

  
  double CVUniverse::GetCalRecoilEnergy() const {
    bool neutrinoMode = GetAnalysisNuPDG() > 0;
    if(neutrinoMode) return (GetDouble("nonvtx_iso_blobs_energy")+GetDouble("dis_id_energy")); // several definitions of this, be careful
    else {
      if (GetVecDouble("recoil_summed_energy").size()==0) return -999.; // protect against bad input,
      return (GetVecDouble("recoil_summed_energy")[0] - GetDouble("recoil_energy_nonmuon_vtx100mm"));
    }
  }

  double CVUniverse::GetCalRecoilEnergyGeV() const {
    return CVUniverse::GetCalRecoilEnergy()*MeVGeV;
  }
  
  
  double CVUniverse::GetNonCalRecoilEnergy() const {
    // not certain why I want to implement this but there ya go.
    return 0;
  }
  
  double CVUniverse::GetNonCalRecoilEnergyGeV() const {
    return GetNonCalRecoilEnergy()*MeVGeV;
  }

  double CVUniverse::GetRecoilEnergyGeV() const {
    // return CVUniverse::GetCalRecoilEnergy();
    return GetRecoilEnergy()*MeVGeV;
  }

  double CVUniverse::GetTrueRecoilEnergyGeV() const {
    // don't know if this needs to exist
    // return 0;     
    return CVUniverse::GetTrueQ0GeV();
  }

  double CVUniverse::GetTrueQ0GeV() const {
    static std::vector<double> mc_incomingPartVec;
    static std::vector<double> mc_primFSLepton;
    mc_incomingPartVec = GetVecDouble("mc_incomingPartVec");
    mc_primFSLepton = GetVecDouble("mc_primFSLepton");
    double q0 = mc_incomingPartVec[3] - mc_primFSLepton[3];
    return q0*MeVGeV;
  }
  double CVUniverse::GetTrueQ3GeV() const {
    static std::vector<double> mc_incomingPartVec;
    static std::vector<double> mc_primFSLepton;
    mc_incomingPartVec = GetVecDouble("mc_incomingPartVec");
    mc_primFSLepton = GetVecDouble("mc_primFSLepton");
    double px = mc_primFSLepton[0] - mc_incomingPartVec[0];
    double py = mc_primFSLepton[1] - mc_incomingPartVec[1];
    double pz = mc_primFSLepton[2] - mc_incomingPartVec[2];
    double q3 = std::sqrt( px*px + py*py + pz*pz );
    return q3*MeVGeV;
  }
  double CVUniverse::GetTrueQ2GeV() const {
    double q3 = CVUniverse::GetTrueQ3GeV();
    double q0 = CVUniverse::GetTrueQ0GeV();
    return q3*q3 - q0*q0;
  }


  // ----------------------------- Other Variables -----------------------------

  //  virtual double GetWgenie() const { return GetDouble("mc_w"); }
  int CVUniverse::GetMCIntType() const {
    return GetInt("mc_intType");
  }

  int CVUniverse::GetTruthNuPDG() const {
    return GetInt("mc_incoming");
  }

  int CVUniverse::GetCurrent() const {
    return GetInt("mc_current");
  }

  double CVUniverse::GetTpiGeV( const int hadron ) const {
    double TLA = GetVecElem("hadron_track_length_area", hadron);
    return (2.3112 * TLA + 37.03)*MeVGeV; // what are these numbers
  }


  // --------------------- Quantities only needed for cuts ---------------------
  // Although unlikely, in principle these quanties could be shifted by a
  // systematic. And when they are, they'll only be shifted correctly if we
  // write these accessor functions.
  bool CVUniverse::IsMinosMatchMuon() const {
    return GetInt("muon_is_minos_match_track") == -1;  // does this flip for neutrino?
  } // This isn't even used anymore, there's something else. This is left over from Amit's analysis

  int CVUniverse::GetNuHelicity() const {
    return GetInt(std::string(MinervaUniverse::GetTreeName()+"_nuHelicity").c_str());
  }
  
  double CVUniverse::GetCurvature() const {
    return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_minos_trk_qp").c_str());
  }

  double CVUniverse::GetTrueCurvature() const {
    return 0.0;
  }
  int CVUniverse::GetTDead() const {
    return GetInt("tdead");
  } // Dead electronics, a rock muon removal technique. Amit's analysis doesn't
  // have that cut most likely. Not even in that tuple, only reason it survives is bc it's not called anymore.
  // Can't find it? Just a hard coded constant in CCQENuCutsNSF.h

  // These cuts are already made in the CCQENu AnaTuple, may be unnecessary
  ROOT::Math::XYZTVector CVUniverse::GetVertex() const {
    ROOT::Math::XYZTVector result;
    result.SetCoordinates(GetVec<double>("vtx").data());
    return result;
  }
  
  // 1-d apothems for cuts
  
  double CVUniverse::GetApothemY() const {  // this should be less than apothem cut
    const double fSlope = 1./sqrt(3.);
    std::vector<double> vertex = GetVec<double>("vtx");
    return (fabs(vertex[1]) + fSlope*fabs(vertex[0]))*sqrt(3.)/2.;
  }
  
  double CVUniverse::GetApothemX() const {  // this should be less than apothem cut
    std::vector<double> vertex = GetVec<double>("vtx");
    return fabs(vertex[0]);
  }
  
  double CVUniverse::GetTrueApothemY() const {  // this should be less than apothem cut
    const double fSlope = 1./sqrt(3.);
    std::vector<double> vertex = GetVec<double>("mc_vtx");
    return (fabs(vertex[1]) + fSlope*fabs(vertex[0]))*sqrt(3.)/2.;
  }
  
  double CVUniverse::GetTrueApothemX() const {  // this should be less than apothem cut
    std::vector<double> vertex = GetVec<double>("mc_vtx");
    return fabs(vertex[0]);
  }
  
  double CVUniverse::GetZVertex() const {
    std::vector<double> tmp = GetVec<double>("vtx");
    return tmp[2];
  }

  ROOT::Math::XYZTVector CVUniverse::GetTrueVertex() const {
    ROOT::Math::XYZTVector result;
    result.SetCoordinates(GetVec<double>("mc_vtx").data());
    return result;
  }
  
  double CVUniverse::GetTrueZVertex() const {
    std::vector<double> tmp = GetVec<double>("mc_vtx");
    return tmp[2];
  }


  // Some stuff Heidi added to test out some issues with the NTuples

  int CVUniverse::GetRun() const {
    return GetInt("ev_run");
  }

  int CVUniverse::GetSubRun() const {
    return GetInt("ev_subrun");
  }

  int CVUniverse::GetGate() const {
    return GetInt("ev_gate");
  }

  int CVUniverse::GetTrueRun() const {
     return GetInt("mc_run");
  }

  int CVUniverse::GetTrueSubRun() const {
     return GetInt("mc_subrun");
  }

  int CVUniverse::GetTrueGate() const {  // mot certain if this is stored
     return GetInt("mc_nthEvtInFile")+1;
  }
  
  // --------------------- put cut functions here ---------------------------------
  
   int CVUniverse::GetGoodRecoil() const{ // implement Cheryl's cut
     double Q2 = CVUniverse::GetQ2QEGeV();
     double recoil = CVUniverse::GetRecoilEnergyGeV();
     double offset=0.05;
     if( Q2 < 0.175 ) return ( recoil <= 0.08+offset);
     else if( Q2 < 1.4 )return (recoil <= 0.03 + 0.3*Q2+offset);
     else return (recoil <= 0.45+offset); //antinu
   }
  
  int CVUniverse::GetIsCC() const{
    return CVUniverse::GetCurrent() == 1;
  }
  
  // helper function
  bool CVUniverse::passTrueCCQELike(bool neutrinoMode, std::vector<int> mc_FSPartPDG, std::vector<double> mc_FSPartE, int mc_nFSPart, double proton_KECut) const {
    int genie_n_muons = 0;
    int genie_n_mesons        = 0;
    int genie_n_heavy_baryons_plus_pi0s = 0;
    int genie_n_photons       = 0;
    int genie_n_protons       = 0; //antinu
    
    for(int i = 0; i < mc_nFSPart; ++i) {
      int pdg =  mc_FSPartPDG[i];
      double energy = mc_FSPartE[i];
      double KEp = energy-MinervaUnits::M_p;
      
      // implement 120 MeV KE cut, if needed
      
      
      //The photon energy cut is hard-coded at 10 MeV at present. We're happy to make it general, if the need arises !
      if( abs(pdg) == 13 ) genie_n_muons++;
      else if( pdg == 22 && energy >10 ) genie_n_photons++;
      else if( abs(pdg) == 211 || abs(pdg) == 321 || abs(pdg) == 323 || pdg == 111 || pdg == 130 || pdg == 310 || pdg == 311 || pdg == 313 ) genie_n_mesons++;
      else if( pdg == 3112 || pdg == 3122 || pdg == 3212 || pdg == 3222 || pdg == 4112 || pdg == 4122 || pdg == 4212 || pdg == 4222 || pdg == 411 || pdg == 421 || pdg == 111 ) genie_n_heavy_baryons_plus_pi0s++;
      else if( pdg == 2212 && KEp > proton_KECut) genie_n_protons++; //antinu
    }
     
      if(neutrinoMode){
        if( genie_n_muons         == 1 &&
           genie_n_mesons        == 0 &&
           genie_n_heavy_baryons_plus_pi0s == 0 &&
           genie_n_photons       == 0 ) return true;
      }
      else{
        if( genie_n_muons         == 1 &&
           genie_n_mesons        == 0 &&
           genie_n_heavy_baryons_plus_pi0s == 0 &&
           genie_n_photons       == 0 &&
           genie_n_protons        == 0 ) return true;
      }
      return false;
  }
  
  int CVUniverse::GetIsCCQELike() const{  // cut hardwired for now
    std::vector<int>mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    std::vector<double>mc_FSPartE = GetVecDouble("mc_FSPartE");
    bool neutrinoMode = CVUniverse::GetTruthNuPDG() > 0;
    int mc_nFSPart = GetInt("mc_nFSPart");
    int mc_incoming = GetInt("mc_incoming");
    int mc_current = GetInt("mc_current");
    bool passes = ( CVUniverse::passTrueCCQELike(neutrinoMode,  mc_FSPartPDG, mc_FSPartE, mc_nFSPart, NSFDefaults::TrueProtonKECutCentral));
    
    return passes;
    
  }
  
  // all CCQElike without proton cut enabled
  
  int CVUniverse::GetIsCCQELikeAll() const{  // cut hardwired for now
    std::vector<int>mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    std::vector<double>mc_FSPartE = GetVecDouble("mc_FSPartE");
    bool neutrinoMode = CVUniverse::GetTruthNuPDG() > 0;
    int mc_nFSPart = GetInt("mc_nFSPart");
    int mc_incoming = GetInt("mc_incoming");
    int mc_current = GetInt("mc_current");
    bool passes = ( CVUniverse::passTrueCCQELike(neutrinoMode,  mc_FSPartPDG, mc_FSPartE, mc_nFSPart, 10000.));
    
    return passes;
    
  }
    
#endif
