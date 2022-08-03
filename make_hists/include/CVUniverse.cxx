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
      //if (GetVecDouble("recoil_summed_energy").size()==0) return -999.; // protect against bad input,
      //return (GetVecDouble("recoil_summed_energy")[0] - GetDouble("recoil_energy_nonmuon_vtx100mm"));
      return GetDouble("recoil_energy_nonmuon_nonvtx100mm");
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

double CVUniverse::GetLog10RecoilEnergyGeV() const {
  // return CVUniverse::GetCalRecoilEnergy();
 // std::cout << GetRecoilEnergy()*MeVGeV <<  " " << std::log10(GetRecoilEnergy()) << std::log10(GetRecoilEnergy())  - 3. << std::endl;
  return std::log10(GetRecoilEnergy())-3.;
}

double CVUniverse::GetTrueLog10RecoilEnergyGeV() const {
  // don't know if this needs to exist
  // return 0;

  return std::log10(CVUniverse::GetTrueQ0GeV());
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
  
  int CVUniverse::GetTruthIsCC() const{
    return CVUniverse::GetCurrent() == 1;
  }
  
  // helper function
  bool CVUniverse::passTrueCCQELike(bool neutrinoMode, std::vector<int> mc_FSPartPDG, std::vector<double> mc_FSPartE, int mc_nFSPart, double proton_KECut) const {
    int genie_n_muons = 0;
    int genie_n_charged_pion = 0;
    int genie_n_neutral_pion = 0;
    int genie_n_photons = 0;
    int genie_n_strange_baryon = 0;
    int genie_n_charmed_baryon = 0;
    int genie_n_strange_meson = 0;
    int genie_n_charmed_meson = 0;
    int genie_n_protons = 0;
    
    for(int i = 0; i < mc_nFSPart; i++){
      int pdg =  mc_FSPartPDG[i];
      double energy = mc_FSPartE[i];
      double KEp = energy - MinervaUnits::M_p;
      
      // implement 120 MeV KE cut, if needed
      
      
      //The photon energy cut is hard-coded at 10 MeV at present. We're happy to make it general, if the need arises !
      
      if(      abs(pdg) ==   13   ) genie_n_muons++;
      else if( abs(pdg) ==  211   ) genie_n_charged_pion++;
      else if( pdg      ==  111   ) genie_n_neutral_pion++;
      else if( pdg      ==   22 && 
               energy    >   10   ) genie_n_photons++;
      else if( pdg      == 3112 || 
               pdg      == 3122 || 
               pdg      == 3212 || 
               pdg      == 3222   ) genie_n_strange_baryon++;
      else if( pdg      == 4112 || 
               pdg      == 4122 || 
               pdg      == 4212 || 
               pdg      == 4222   ) genie_n_charmed_baryon++;
      else if( pdg      ==  130 ||
               pdg      ==  310 ||
               pdg      ==  311 ||
               pdg      ==  313 ||
               abs(pdg) ==  321 ||
               abs(pdg) ==  323   ) genie_n_strange_meson++;
      else if( pdg      ==  411 ||
               pdg      ==  421   ) genie_n_charmed_meson++;
      else if( pdg      == 2212 && 
               KEp  > proton_KECut) genie_n_protons++;
    } // Add else for mystery particle
    // Call functions instead
    // Place functions likely to be true first
    
    if(neutrinoMode){
      if(genie_n_muons          == 1 &&
         genie_n_neutral_pion   == 0 && 
         genie_n_charged_pion   == 0 &&
         genie_n_photons        == 0 &&
         genie_n_strange_baryon == 0 &&
         genie_n_charmed_baryon == 0 &&
         genie_n_strange_meson  == 0 &&
         genie_n_charmed_meson  == 0   ) return 1;
    }
    else{
      if(genie_n_muons          == 1 &&
         genie_n_neutral_pion   == 0 && 
         genie_n_charged_pion   == 0 &&
         genie_n_photons        == 0 &&
         genie_n_strange_baryon == 0 &&
         genie_n_charmed_baryon == 0 &&
         genie_n_strange_meson  == 0 &&
         genie_n_charmed_meson  == 0 &&
         genie_n_protons        == 0   ) return 1;
    }
    return 0;   // Add else for mystery particle
    // Call functions instead
    // Place functions likely to be true first
    
  }
  
  int CVUniverse::GetTruthIsCCQELike() const{  // cut hardwired for now
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
  
  int CVUniverse::GetTruthIsCCQELikeAll() const{  // cut hardwired for now
    std::vector<int>mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    std::vector<double>mc_FSPartE = GetVecDouble("mc_FSPartE");
    bool neutrinoMode = CVUniverse::GetTruthNuPDG() > 0;
    int mc_nFSPart = GetInt("mc_nFSPart");
    int mc_incoming = GetInt("mc_incoming");
    int mc_current = GetInt("mc_current");
    bool passes = ( CVUniverse::passTrueCCQELike(neutrinoMode,  mc_FSPartPDG, mc_FSPartE, mc_nFSPart, 10000.));
    
    return passes;
    
  }
  
  // ------------------------------------------------------------------------------
  // ----------------- Added by Sean for Neutrino ---------------------------------
  // ------------------------------------------------------------------------------
  
  int CVUniverse::GetTruthIsOther() const{
    std::vector<int>mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    std::vector<double>mc_FSPartE = GetVecDouble("mc_FSPartE");
    bool neutrinoMode = CVUniverse::GetTruthNuPDG() > 0;
    int mc_nFSPart = GetInt("mc_nFSPart");
    int mc_incoming = GetInt("mc_incoming");
    int mc_current = GetInt("mc_current");
    
    bool passesCCQE = CVUniverse::passTrueCCQELike(neutrinoMode, mc_FSPartPDG, mc_FSPartE, mc_nFSPart, NSFDefaults::TrueProtonKECutCentral);
    int passesSingleChargedPion = CVUniverse::GetTruthHasSingleChargedPion();
    int passesSingleNeutralPion = CVUniverse::GetTruthHasSingleNeutralPion();
    int passesMultiPion = CVUniverse::GetTruthHasMultiPion();
    
    if(passesCCQE || passesSingleChargedPion || passesSingleNeutralPion || passesMultiPion) return 0;
    else return 1;
  }
  
  // Interaction Vertex
  
  int CVUniverse::GetHasInteractionVertex() const {
    return GetInt("has_interaction_vertex");
  }
  
  // Isolated Blobs and Charged Pions
  
  int CVUniverse::GetNBlobs() const {
    // define and get applicable variables
    int n_blobs = 0;
    int kmax = GetInt("nonvtx_iso_blobs_start_position_z_in_prong_sz");
    std::vector<double> blob_z_starts = GetVecDouble("nonvtx_iso_blobs_start_position_z_in_prong");
    // counts blobs with zvertex greater than set value
    for(int k=0; k<kmax; ++k){
      if(blob_z_starts[k] > 4750) n_blobs++; // why 4750? how can this be defined in a config file?
    }
    return n_blobs;
  }
  
  int CVUniverse::GetTruthHasSingleChargedPion() const {
    int genie_n_charged_pion = 0;
    int genie_n_neutral_pion = 0;
    int genie_n_photons = 0;
    int genie_n_strange_baryon = 0;
    int genie_n_charmed_baryon = 0;
    int genie_n_strange_meson = 0;
    int genie_n_charmed_meson = 0;
    
    std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    std::vector<double> mc_FSPartE = GetVecDouble("mc_FSPartE");
    int mc_nFSPart = GetInt("mc_nFSPart");
    
    for(int i = 0; i < mc_nFSPart; i++){
      int pdg =  mc_FSPartPDG[i];
      double energy = mc_FSPartE[i];
      double KEp = energy - MinervaUnits::M_p;
      
      if(      abs(pdg) ==  211   ) genie_n_charged_pion++;
      else if( pdg      ==  111   ) genie_n_neutral_pion++;
      else if( pdg      ==   22 && 
               energy    >   10   ) genie_n_photons++;
      else if( pdg      == 3112 || 
               pdg      == 3122 || 
               pdg      == 3212 || 
               pdg      == 3222   ) genie_n_strange_baryon++;
      else if( pdg      == 4112 || 
               pdg      == 4122 || 
               pdg      == 4212 || 
               pdg      == 4222   ) genie_n_charmed_baryon++;
      else if( pdg      ==  130 ||
               pdg      ==  310 ||
               pdg      ==  311 ||
               pdg      ==  313 ||
               abs(pdg) ==  321 ||
               abs(pdg) ==  323   ) genie_n_strange_meson++;
      else if( pdg      ==  411 ||
               pdg      ==  421   ) genie_n_charmed_meson++;
    }
    
    if(genie_n_neutral_pion   == 0 && 
       genie_n_charged_pion   == 1 &&
       genie_n_photons        == 0 &&
       genie_n_strange_baryon == 0 &&
       genie_n_charmed_baryon == 0 &&
       genie_n_strange_meson  == 0 &&
       genie_n_charmed_meson  == 0   ) return 1;
    return 0;
  }
  
  int CVUniverse::GetTrueChargedPionCount() const {
    int genie_n_charged_pion = 0;
    
    std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    int mc_nFSPart = GetInt("mc_nFSPart");
    
    for(int i = 0; i < mc_nFSPart; i++){
      int pdg =  mc_FSPartPDG[i];
      if( abs(pdg) == 211 ) genie_n_charged_pion++;
    }

    return genie_n_charged_pion;
  }
  
  // Michel Electrons and Neutral Pions

  int CVUniverse::GetNMichel() const {
    return GetInt("has_michel_vertex_type_sz");
  }
  
  int CVUniverse::GetImprovedNMichel() const {
  	return GetInt("improved_michel_match_vec_sz");
  }
  
  int CVUniverse::GetHasMichelElectron() const {
    if(GetNMichel() > 0) return 1;
    return 0;
  }

  int CVUniverse::GetTruthHasMichel() const {
    return GetInt("truth_reco_has_michel_electron");
  }
  
  int CVUniverse::GetTruthHasImprovedMichel() const {
  	return GetInt("truth_improved_michel_electron");
  }
  
  int CVUniverse::GetTruthHasSingleNeutralPion() const {
    int genie_n_charged_pion = 0;
    int genie_n_neutral_pion = 0;
    int genie_n_photons = 0;
    int genie_n_strange_baryon = 0;
    int genie_n_charmed_baryon = 0;
    int genie_n_strange_meson = 0;
    int genie_n_charmed_meson = 0;
    
    std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    std::vector<double> mc_FSPartE = GetVecDouble("mc_FSPartE");
    int mc_nFSPart = GetInt("mc_nFSPart");
    
    for(int i = 0; i < mc_nFSPart; i++){
      int pdg =  mc_FSPartPDG[i];
      double energy = mc_FSPartE[i];
      
      if(      abs(pdg) ==  211   ) genie_n_charged_pion++;
      else if( pdg      ==  111   ) genie_n_neutral_pion++;
      else if( pdg      ==   22 && 
               energy    >   10   ) genie_n_photons++;
      else if( pdg      == 3112 || 
               pdg      == 3122 || 
               pdg      == 3212 || 
               pdg      == 3222   ) genie_n_strange_baryon++;
      else if( pdg      == 4112 || 
               pdg      == 4122 || 
               pdg      == 4212 || 
               pdg      == 4222   ) genie_n_charmed_baryon++;
      else if( pdg      ==  130 ||
               pdg      ==  310 ||
               pdg      ==  311 ||
               pdg      ==  313 ||
               abs(pdg) ==  321 ||
               abs(pdg) ==  323   ) genie_n_strange_meson++;
      else if( pdg      ==  411 ||
               pdg      ==  421   ) genie_n_charmed_meson++;
    }
    
    if(genie_n_neutral_pion   == 1 && 
       genie_n_charged_pion   == 0 &&
       genie_n_photons        == 0 &&
       genie_n_strange_baryon == 0 &&
       genie_n_charmed_baryon == 0 &&
       genie_n_strange_meson  == 0 &&
       genie_n_charmed_meson  == 0   ) return 1;
    return 0;
  }
  
  int CVUniverse::GetTrueNeutralPionCount() const {
    int genie_n_neutral_pion = 0;
    
    std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    int mc_nFSPart = GetInt("mc_nFSPart");
    
    for(int i = 0; i < mc_nFSPart; i++){
      int pdg =  mc_FSPartPDG[i];
      if( pdg == 111 ) genie_n_neutral_pion++;
    }

    return genie_n_neutral_pion;
  }
  
  // Michel+Blobs and MultiPion
  
  int CVUniverse::GetTruthHasMultiPion() const {
    int genie_n_charged_pion = 0;
    int genie_n_neutral_pion = 0;
    int genie_n_photons = 0;
    int genie_n_strange_baryon = 0;
    int genie_n_charmed_baryon = 0;
    int genie_n_strange_meson = 0;
    int genie_n_charmed_meson = 0;
    int genie_er_n_eta = 0;
    
    std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    std::vector<double> mc_FSPartE = GetVecDouble("mc_FSPartPDG");
    int mc_nFSPart = GetInt("mc_nFSPart");
    
    for(int i = 0; i < mc_nFSPart; i++){
      int pdg =  mc_FSPartPDG[i];
      double energy = mc_FSPartE[i];
      
      if(      abs(pdg) ==  211   ) genie_n_charged_pion++;
      else if( pdg      ==  111   ) genie_n_neutral_pion++;
      else if( pdg      ==   22 && 
               energy    >   10   ) genie_n_photons++;
      else if( pdg      == 3112 || 
               pdg      == 3122 || 
               pdg      == 3212 || 
               pdg      == 3222   ) genie_n_strange_baryon++;
      else if( pdg      == 4112 || 
               pdg      == 4122 || 
               pdg      == 4212 || 
               pdg      == 4222   ) genie_n_charmed_baryon++;
      else if( pdg      ==  130 ||
               pdg      ==  310 ||
               pdg      ==  311 ||
               pdg      ==  313 ||
               abs(pdg) ==  321 ||
               abs(pdg) ==  323   ) genie_n_strange_meson++;
      else if( pdg      ==  411 ||
               pdg      ==  421   ) genie_n_charmed_meson++;
    }
    
    int nerpart = GetInt("mc_er_nPart");
    std::vector<int> erpartID = GetVecInt("mc_er_ID");
    std::vector<int> erpartstatus = GetVecInt("mc_er_status");
    
    for(int i = 0; i < nerpart; i++){
      bool neutrinoMode = GetAnalysisNuPDG() > 0;
      int status = erpartstatus[i];
      int id = erpartID[i];
      
      if(abs(status) == 14 && id == 221){
        genie_er_n_eta = 1;
        break;
      }
    }
    
    int genie_n_pion = genie_n_charged_pion + genie_n_neutral_pion;
    if(genie_n_pion            > 1 && 
       genie_n_photons        == 0 &&
       genie_n_strange_baryon == 0 &&
       genie_n_charmed_baryon == 0 &&
       genie_n_strange_meson  == 0 &&
       genie_n_charmed_meson  == 0   ) return 1;
    else if(genie_er_n_eta         == 1 && 
            genie_n_photons        == 0 &&
            genie_n_strange_baryon == 0 &&
            genie_n_charmed_baryon == 0 &&
            genie_n_strange_meson  == 0 &&
            genie_n_charmed_meson  == 0   ) return 1;
    return 0;
  }
  
  int CVUniverse::GetTruePionCount() const {
    int genie_n_charged_pion = 0;
    int genie_n_neutral_pion = 0;
    
    std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    int mc_nFSPart = GetInt("mc_nFSPart");
    
    for(int i = 0; i < mc_nFSPart; i++){
      int pdg =  mc_FSPartPDG[i];
      if(      abs(pdg) == 211 ) genie_n_charged_pion++;
      else if( pdg      == 111 ) genie_n_neutral_pion++;
    }

    return genie_n_neutral_pion + genie_n_charged_pion;
  }
  
  int CVUniverse::GetEventRecordTrueEtaCount() const {
    int genie_er_n_eta = 0;
    
    int nerpart = GetInt("mc_er_nPart");
    std::vector<int> erpartID = GetVecInt("mc_er_ID");
    std::vector<int> erpartstatus = GetVecInt("mc_er_status");
    
    for(int i = 0; i < nerpart; i++){
      bool neutrinoMode = GetAnalysisNuPDG() > 0;
      int status = erpartstatus[i];
      int id = erpartID[i];
      
      if(abs(status) == 14 && id == 221) genie_er_n_eta++;
    }

    return genie_er_n_eta;
  }
  
  // Protons

  double CVUniverse::GetSingleProtonScore() const {
    return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_score1").c_str());
  }

  int CVUniverse::GetIsSingleProton() const {
  	if(GetMultiplicity() == 1) return 1; // NA when multiplicity is 1
    // define and get applicable variables
    double tree_Q2 = GetQ2QEGeV();
    double proton_score1 = GetSingleProtonScore();
    
    // How to define Q2 and proton score limits in config?
    if(      tree_Q2        < 0.2 &&
             proton_score1  < 0.2   ) return 0;
    else if( tree_Q2       >= 0.2 &&
             tree_Q2        < 0.6 &&
             proton_score1  < 0.1   ) return 0;
    else if( tree_Q2       >= 0.6 &&
             proton_score1  < 0.0   ) return 0;
    else return 1; // if false not returned by now must be true
  }
  
  int CVUniverse::GetTruthHasSingleProton() const {
    return GetInt("truth_reco_has_single_proton");
  }
  
  int CVUniverse::GetAllExtraTracksProtons() const {
  	if(GetMultiplicity() == 1) return 1; // NA when multiplicity is 1
    // get secondary proton candidates
    int n_sec_proton_scores1 = GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1_sz").c_str());
    // if 0, return true (vacuously)
    if(n_sec_proton_scores1==0) return 1;
    
    // define and get applicable variables
    double tree_Q2 = GetQ2QEGeV();
    std::vector<double> sec_proton_scores1 = GetVecDouble(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1").c_str());
    
    // How to define Q2 and proton score limits in config?
    if(tree_Q2<0.2){
      for(int i=0; i<n_sec_proton_scores1; i++) if(sec_proton_scores1[i]<0.2) return 0;
    }
    else if(tree_Q2>=0.2 && tree_Q2<0.6){
      for(int i=0; i<n_sec_proton_scores1; i++) if(sec_proton_scores1[i]<0.1) return 0;
    }
    else if(tree_Q2>=0.6){
       for(int i=0; i<n_sec_proton_scores1; i++) if(sec_proton_scores1[i]<0.0) return 0;
    }
    // if false not returned by now must be true
    return 1;
  }
  
  int CVUniverse::GetTrueProtonCount() const {
    int genie_n_protons = 0;
    
    std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    std::vector<double> mc_FSPartE = GetVecDouble("mc_FSPartPDG");
    int mc_nFSPart = GetInt("mc_nFSPart");
    
    for(int i = 0; i < mc_nFSPart; i++){
      int pdg =  mc_FSPartPDG[i];
      double energy = mc_FSPartE[i];
      double KEp = energy - MinervaUnits::M_p;
      double proton_KECut = NSFDefaults::TrueProtonKECutCentral;
      if( pdg == 2212         && 
          KEp  > proton_KECut   ) genie_n_protons++;
    }

    return genie_n_protons;
  }
  
  // Other particles
  
  int CVUniverse::GetTrueLightMesonCount() const { // Just base etas right now
    int genie_n_light_meson = 0;
    std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    int mc_nFSPart = GetInt("mc_nFSPart");
    for(int i = 0; i < mc_nFSPart; i++){
      if( mc_FSPartPDG[i] == 221) genie_n_light_meson++;
    }
    return genie_n_light_meson; 
  }
  
  int CVUniverse::GetTrueCharmedMesonCount() const { // D_+ and D_0
    int genie_n_charmed_meson = 0;
    std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    int mc_nFSPart = GetInt("mc_nFSPart");
    for(int i = 0; i < mc_nFSPart; i++){
      if( mc_FSPartPDG[i] == 411 || 
          mc_FSPartPDG[i] == 421   ) genie_n_charmed_meson++;
    }
    return genie_n_charmed_meson; 
  }
  
  int CVUniverse::GetTrueStrangeMesonCount() const { // K__L0, K_S0, K_0, K_*(892)0, K_+, K_*(892)+
    int genie_n_strange_meson = 0;
    std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    int mc_nFSPart = GetInt("mc_nFSPart");
    for(int i = 0; i < mc_nFSPart; i++){
      if( mc_FSPartPDG[i]      == 130 ||
          mc_FSPartPDG[i]      == 310 || 
          mc_FSPartPDG[i]      == 311 || 
          mc_FSPartPDG[i]      == 313 || 
          abs(mc_FSPartPDG[i]) == 321 || 
          abs(mc_FSPartPDG[i]) == 323   ) genie_n_strange_meson++;
    }
    return genie_n_strange_meson;
  }
  
  int CVUniverse::GetTrueCharmedBaryonCount() const { // Sigma_c0, Lambda_c+, Sigma_c+, Sigma_c++
    int genie_n_charmed_baryon = 0;
    std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    int mc_nFSPart = GetInt("mc_nFSPart");
    for(int i = 0; i < mc_nFSPart; i++){
      if( mc_FSPartPDG[i] == 4112 || 
          mc_FSPartPDG[i] == 4122 || 
          mc_FSPartPDG[i] == 4212 || 
          mc_FSPartPDG[i] == 4222   ) genie_n_charmed_baryon++;
    }
    return genie_n_charmed_baryon; 
  }
  
  int CVUniverse::GetTrueStrangeBaryonCount() const { // Sigma_-, Lambda, Sigma_0, Sigma_+
    int genie_n_strange_baryon = 0;
    std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
    int mc_nFSPart = GetInt("mc_nFSPart");
    for(int i = 0; i < mc_nFSPart; i++){
      if( mc_FSPartPDG[i] == 3112 || 
          mc_FSPartPDG[i] == 3122 || 
          mc_FSPartPDG[i] == 3212 || 
          mc_FSPartPDG[i] == 3222   ) genie_n_strange_baryon++;
    }
    return genie_n_strange_baryon; 
  }

 int CVUniverse::GetMCTargetA() const{
     return GetInt("mc_targetA");
 }

 int CVUniverse::GetMCTargetZ() const{
     return GetInt("mc_targetZ");
 }

 int CVUniverse::GetMCTargetNucleon() const{
     return GetInt("mc_targetNucleon");
 }

 int CVUniverse::Dummy() const {
     return 0.;
 }
    
#endif
