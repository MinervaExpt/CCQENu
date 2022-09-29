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
	// ===========================================================
	// ====================== Configurables ======================
	// ===========================================================

	///////////////// Defaults and Declarations /////////////////
	double CVUniverse::m_min_blob_zvtx = 4750.0;
	double CVUniverse::m_photon_energy_cut = 10.0; // in MeV
	double CVUniverse::m_proton_ke_cut = NSFDefaults::TrueProtonKECutCentral; // Default value
	
	NuConfig CVUniverse::m_proton_score_config = Json::Value::null;
	std::vector<double> CVUniverse::m_proton_score_Q2QEs = { 0.2, 0.6 };
	std::vector<double> CVUniverse::m_proton_score_mins = { 0.2, 0.1, 0.0 };
	/*
	The vectors
		m_proton_score_Q2QEs
		m_proton_score_mins
	come from m_proton_score_config through SetProtonScoreConfig().
	
	Substituting
		q2qe   = m_proton_score_Q2QEs
		pscore = m_proton_score_mins
	these vectors are interpreted to mean...
		 ____________________________________________________________
		|                             |                             |
		|  for...                     |  proton if...               |
		|_____________________________|_____________________________|
		|                             |                             |
		|            Q2QE <= q2qe[0]  |  proton score >= pscore[0]  |
		|  q2qe[0] < Q2QE <= q2qe[1]  |  proton score >= pscore[1]  |
		|  q2qe[1] < Q2QE             |  proton score >= pscore[2]  |
		|_____________________________|_____________________________|
		
	Valid proton score configuration inputs are of the form:
	
		"ProtonScoreConfig": {
			"band1":{ "Q2QE_max":0.2, "pass_proton_score_min":0.2 },
			"band2":{ "Q2QE_range":[0.2,0.6], "pass_proton_score_min":0.1 },
			"band3":{ "Q2QE_min":0.6, "pass_proton_score_min":0.0 }
		},
			
		which means
		 ______________________________________________
		|                     |                       |
		|  for...             |  proton if...         |
		|_____________________|_______________________|
		|                     |                       |
		|        Q2QE <= 0.2  |  proton score >= 0.2  |
		|  0.2 < Q2QE <= 0.6  |  proton score >= 0.1  |
		|  0.6 < Q2QE         |  proton score >= 0.0  |
		|_____________________|_______________________|
		
		In terms of q2qe and pscore this would be:
		
		"ProtonScoreConfig": {
			"band1":{ "Q2QE_max":q2qe[0], "pass_proton_score_min":pscore[0] },
			"band2":{ "Q2QE_range":[q2qe[0],q2qe[1]], "pass_proton_score_min":pscore[1] },
			"band3":{ "Q2QE_min":q2qe[1], "pass_proton_score_min":pscore[2] }
		},
		
	-OR-
	
		"ProtonScoreConfig": { "pass_proton_score_min":0.15 },
	
		which means for
		 ________________________________________________
		|                      |                        |
		|  for...              |  proton if...          |
		|______________________|________________________|
		|                      |                        |
		|  all values of Q2QE  |  proton score >= 0.15  |
		|______________________|________________________|
		
		In terms of q2qe and pscore this would be:
		
		"ProtonScoreConfig": { "pass_proton_score_min":pscore[0] },
		
	*/
	
	bool CVUniverse::_is_min_blob_zvtx_set = false;
	bool CVUniverse::_is_photon_energy_cut_set = false;
	bool CVUniverse::_is_proton_ke_cut_set = false;
	bool CVUniverse::_is_proton_score_config_set = false;
	
	///////////////// Blob minimum Z vertex in order to be counted /////////////////
	double CVUniverse::GetMinBlobZVtx() { return m_min_blob_zvtx; }
	bool CVUniverse::SetMinBlobZVtx( double min_zvtx, bool print ) {
		if( _is_min_blob_zvtx_set ) {  
			std::cout << "WARNING: YOU ATTEMPTED TO SET MIN BLOB ZVTX A SECOND TIME. "
			          << "THIS IS NOT ALLOWED FOR CONSISTENCY." << std::endl;
			return 0; 
		} else {
			m_min_blob_zvtx = min_zvtx;
			_is_min_blob_zvtx_set = true;
			if ( print ) std::cout << "Minimum blob Z vertex cutoff set to " << m_min_blob_zvtx << std::endl;
			return 1;
		}
	}
	
	///////////////// Photon Energy Cut /////////////////
	double CVUniverse::GetPhotonEnergyCut() { return m_photon_energy_cut; }
	bool CVUniverse::SetPhotonEnergyCut( double energy, bool print ) {
		if( _is_photon_energy_cut_set ) {  
			std::cout << "WARNING: YOU ATTEMPTED TO SET PHOTON ENERGY CUT A SECOND TIME. "
			          << "THIS IS NOT ALLOWED FOR CONSISTENCY." << std::endl;
			return 0; 
		} else {
			m_photon_energy_cut = energy;
			_is_photon_energy_cut_set = true;
			if ( print ) std::cout << "Photon low energy cutoff set to " << m_photon_energy_cut << " MeV" << std::endl;
			return 0;
		}
	}

	///////////////// Proton KE Cut setting /////////////////
	double CVUniverse::GetProtonKECut() { return m_proton_ke_cut; }
	bool CVUniverse::SetProtonKECut( double proton_KECut, bool print ) {
		if( _is_proton_ke_cut_set ) {  
			std::cout << "WARNING: YOU ATTEMPTED TO SET PROTON KE CUT A SECOND TIME. "
			          << "THIS IS NOT ALLOWED FOR CONSISTENCY." << std::endl;
			return 0; 
		} else {
			m_proton_ke_cut = proton_KECut;
			_is_proton_ke_cut_set = true;
			if ( print ) std::cout << "ProtonKECut set to " << m_proton_ke_cut << " MeV" << std::endl;
			return 1;
		}
	}
	
	///////////////// Proton Score configuration /////////////////
	NuConfig CVUniverse::GetProtonScoreConfig(bool print = false) {
		if (!_is_proton_score_config_set) { // Uses default configuration, which produces default m_proton_score_* values
			std::cout << "\nUSING DEFAULT PROTON SCORE CONFIGURATION.\n\n";
			m_proton_score_config.ReadFromString(R"({"band1":{"Q2QE_max":0.2,"pass_proton_score_min":0.2},"band2":{"Q2QE_range":[0.2,0.6],"pass_proton_score_min":0.1},"band3":{"Q2QE_min":0.6,"pass_proton_score_min":0.0}})");
			if ( print ) m_proton_score_config.Print();
		}
		else {
			std::cout << "\nUsing proton score configuration provided by user configuration file.\n\n";
			if ( print ) m_proton_score_config.Print();
		}
		return m_proton_score_config;
	}
	bool CVUniverse::SetProtonScoreConfig(NuConfig protonScoreConfig, bool print ) {
		if( _is_proton_score_config_set ) {  
			std::cout << "WARNING: YOU ATTEMPTED TO SET PROTON SCORE CONFIGURATION A SECOND TIME. "
			          << "THIS IS NOT ALLOWED FOR CONSISTENCY." << std::endl;
			return 0; 
		} else {
			m_proton_score_config = protonScoreConfig;
			if ( print == true ) m_proton_score_config.Print();
			if ( m_proton_score_config.GetKeys().size() == 1) {
				// Passing proton score value same for all values of Q2QE
				m_proton_score_mins = {};
				m_proton_score_Q2QEs = {};
				m_proton_score_mins.push_back(m_proton_score_config.GetDouble("pass_proton_score_min"));
			}
			else { // There are Q2QE values that dictate passing proton score values
				m_proton_score_mins = {};
				m_proton_score_Q2QEs = {};
				for ( auto band:m_proton_score_config.GetKeys() ) {
					NuConfig bandConfig = m_proton_score_config.GetConfig(band);
					m_proton_score_mins.push_back(bandConfig.GetDouble("pass_proton_score_min"));
					if ( bandConfig.IsMember("Q2QE_max") ) {
						m_proton_score_Q2QEs.push_back(bandConfig.GetDouble("Q2QE_max"));
					}
					else if ( bandConfig.IsMember("Q2QE_range") ) {
						m_proton_score_Q2QEs.push_back(bandConfig.GetDoubleVector("Q2QE_range")[1]);
					}
				}
			}
			_is_proton_score_config_set = true;
			return 1;
		}
	}

	// ========================================================================
	// ============================== Get Weight ==============================
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

	int CVUniverse::GetMultiplicity() const { return GetInt("multiplicity"); }
	int CVUniverse::GetDeadTime() const { return GetInt("phys_n_dead_discr_pair_upstream_prim_track_proj"); }
	
	// ----------------------- Analysis-related Variables ------------------------


	int CVUniverse::GetIsMinosMatchTrack()const { return GetInt("muon_is_minos_match_track"); }
	double CVUniverse::GetEnuHadGeV() const { return CVUniverse::GetEmuGeV()+CVUniverse::GetHadronEGeV(); } // GetEnuGeV()?
	double CVUniverse::GetTrueEnuGeV() const { return GetDouble("mc_incomingE")*MeVGeV; }

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

	double CVUniverse::GetLog10Q2QEGeV() const { return std::log10( CVUniverse::GetQ2QEGeV() ); }
	double CVUniverse::GetTrueLog10Q2QEGeV() const { return std::log10( GetTrueQ2QEGeV() ); }


	// ------------------------------ Muon Variables -----------------------------

	double CVUniverse::GetEmuGeV() const { return std::sqrt(GetPmu()*GetPmu() + pow( MinervaUnits::M_mu, 2 ))*MeVGeV; }
	double CVUniverse::GetTrueEmuGeV() const { return GetElepTrue(); } // not sure if this is right
	double CVUniverse::GetPmuGeV() const { return GetPmu()*MeVGeV;	}
	double CVUniverse::GetTruePmuGeV() const { return GetPlepTrue()*MeVGeV; }
	double CVUniverse::GetPparMuGeV() const { return GetPmuGeV()*std::cos( GetThetamu() ); }
	double CVUniverse::GetTruePparMuGeV() const { return GetTruePmuGeV()*std::cos( GetTrueThetamu() ); }
	double CVUniverse::GetPperpMuGeV() const { return GetPmuGeV()*std::sin( GetThetamu() ); }
	double CVUniverse::GetTruePperpMuGeV() const { return GetTruePmuGeV()*std::sin( GetTrueThetamu() ); }

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

	double CVUniverse::GetTrueThetamu() const { return GetThetalepTrue(); }
	double CVUniverse::GetThetamuDegrees() const { return GetThetamu()*180/M_PI; }
	double CVUniverse::GetTrueThetamuDegrees() const { return GetThetalepTrue()*180/M_PI; }

	// ----------------------------- Proton Variables ----------------------------

	double CVUniverse::GetHadronEGeV() const { return (GetCalRecoilEnergyGeV() + GetNonCalRecoilEnergyGeV()); }

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

	double CVUniverse::GetCalRecoilEnergyGeV() const { return CVUniverse::GetCalRecoilEnergy()*MeVGeV; }
	double CVUniverse::GetNonCalRecoilEnergy() const { return 0; } // not certain why I want to implement this but there ya go.
	double CVUniverse::GetNonCalRecoilEnergyGeV() const { return GetNonCalRecoilEnergy()*MeVGeV; }
	double CVUniverse::GetRecoilEnergyGeV() const { return GetRecoilEnergy()*MeVGeV; } // GetCalRecoilEnergy()?
	double CVUniverse::GetTrueRecoilEnergyGeV() const { return CVUniverse::GetTrueQ0GeV(); } // need this?
	double CVUniverse::GetTrueLog10RecoilEnergyGeV() const { return std::log10(CVUniverse::GetTrueQ0GeV()); } // need this?
	double CVUniverse::GetLog10RecoilEnergyGeV() const { return std::log10(GetRecoilEnergy())-3.; }
		// return CVUniverse::GetCalRecoilEnergy();
		// std::cout << GetRecoilEnergy()*MeVGeV <<  " " << std::log10(GetRecoilEnergy()) << std::log10(GetRecoilEnergy())  - 3. << std::endl;

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
	int CVUniverse::GetMCIntType() const { return GetInt("mc_intType"); }
	int CVUniverse::GetTruthNuPDG() const { return GetInt("mc_incoming"); }
	int CVUniverse::GetCurrent() const { return GetInt("mc_current"); }

	double CVUniverse::GetTpiGeV( const int hadron ) const {
		double TLA = GetVecElem("hadron_track_length_area", hadron);
		return (2.3112 * TLA + 37.03)*MeVGeV; // what are these numbers
	}


	// --------------------- Quantities only needed for cuts ---------------------
	// Although unlikely, in principle these quanties could be shifted by a
	// systematic. And when they are, they'll only be shifted correctly if we
	// write these accessor functions.
	bool CVUniverse::IsMinosMatchMuon() const { return GetInt("muon_is_minos_match_track") == -1; }
		// does this flip for neutrino?
		// This isn't even used anymore, there's something else. This is left over from Amit's analysis

	int CVUniverse::GetNuHelicity() const {
		return GetInt(std::string(MinervaUniverse::GetTreeName()+"_nuHelicity").c_str());
	}
	double CVUniverse::GetCurvature() const {
		return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_minos_trk_qp").c_str());
	}
	
	double CVUniverse::GetTrueCurvature() const { return 0.0; }
	int CVUniverse::GetTDead() const { return GetInt("tdead"); }
		// Dead electronics, a rock muon removal technique. Amit's analysis doesn't have
		// that cut most likely. Not even in that tuple, only reason it survives is bc it's
		// not called anymore. Can't find it? Just a hard coded constant in CCQENuCutsNSF.h

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

	int CVUniverse::GetRun() const { return GetInt("ev_run"); }
	int CVUniverse::GetSubRun() const { return GetInt("ev_subrun"); }
	int CVUniverse::GetGate() const { return GetInt("ev_gate"); }
	int CVUniverse::GetTrueRun() const { return GetInt("mc_run"); }
	int CVUniverse::GetTrueSubRun() const { return GetInt("mc_subrun"); }
	int CVUniverse::GetTrueGate() const { return GetInt("mc_nthEvtInFile")+1; } // not certain if this is stored

	// --------------------- put cut functions here ---------------------------------

	int CVUniverse::GetGoodRecoil() const { // implement Cheryl's cut
		double Q2 = CVUniverse::GetQ2QEGeV();
		double recoil = CVUniverse::GetRecoilEnergyGeV();
		double offset=0.05;
		if( Q2 < 0.175 ) return ( recoil <= 0.08+offset);
		else if( Q2 < 1.4 )return (recoil <= 0.03 + 0.3*Q2+offset);
		else return (recoil <= 0.45+offset); //antinu
	}

	int CVUniverse::GetTruthIsCC() const { return CVUniverse::GetCurrent() == 1; }

	// helper function
	bool CVUniverse::passTrueCCQELike(bool neutrinoMode, std::vector<int> mc_FSPartPDG, std::vector<double> mc_FSPartE, int mc_nFSPart, double proton_KECut) const {
		int genie_n_muons = 0;
		int genie_n_antimuons = 0;
		double protonKECut = proton_KECut;
		for(int i = 0; i < mc_nFSPart; i++){
			int pdg =  mc_FSPartPDG[i];
			int abs_pdg = abs(pdg);
			double energy = mc_FSPartE[i];
			double KEp = energy - MinervaUnits::M_p;

			// implement 120 MeV KE cut, if needed
			// The photon energy cut is hard-coded at 10 MeV at present. We're happy to make it general, if the need arises !
			
			if(      abs_pdg ==  211 ||            // Charged Pions            Pions
			         pdg     ==  111   ) return 0; // Neutral Pions            Pions
			else if( abs_pdg == 3112 ||            // Sigma- and Sigma~+      Strange Baryons
				     abs_pdg == 3122 ||            // Lambda0 and Lambda~0    Strange Baryons
				     abs_pdg == 3212 ||            // Sigma0 and Sigma~0      Strange Baryons
				     abs_pdg == 3222   ) return 0; // Sigma+ and Sigma~-      Strange Baryons
			else if( energy > m_photon_energy_cut &&
			         pdg     ==   22   ) return 0; // Photons > Energy Cut
			else if( pdg     ==  130 ||            // KL0                     Strange Mesons
				     pdg     ==  310 ||            // KS0                     Strange Mesons
				     abs_pdg ==  311 ||            // K0 and K~0              Strange Mesons
				     abs_pdg ==  313 ||            // K*(892)0 and K*(892)~0  Strange Mesons
				     abs_pdg ==  321 ||            // K+ and K-               Strange Mesons
				     abs_pdg ==  323   ) return 0; // K*(892)+ and K*(892)-   Strange Mesons
			else if( abs_pdg == 4112 ||            // Sigma_c0 and Sigma_c~0   Charmed Baryons
				     abs_pdg == 4122 ||            // Lambda_c+ and Lambda_c~- Charmed Baryons
				     abs_pdg == 4212 ||            // Sigma_c+ and Sigma_c~-   Charmed Baryons
				     abs_pdg == 4222   ) return 0; // Sigma_c++ and Sigma_c~-- Charmed Baryons
			else if( abs_pdg ==  411 ||            // D+ and D-                Charned Mesons
				     abs_pdg ==  421   ) return 0; // D0 and D~0               Charmed Mesons
			else if( !neutrinoMode   &&
				     pdg     == 2212 && 
				     KEp  > protonKECut) return 0; // For antinus, no protons > cut-off KE
			else if( pdg     ==   13   ) genie_n_muons++;
			else if( pdg     ==  -13   ) genie_n_antimuons++;
			// Intermediate muon counts check
			if( genie_n_muons + genie_n_antimuons > 1 ) return 0;
		}
		/*
		bool passes = 1;
		if( neutrinoMode ) {
			for(int i = 0; i < mc_nFSPart; i++) {
				int pdg =  mc_FSPartPDG[i];
				double energy = mc_FSPartE[i];
				
				if( pdg == 13 ) { // muon
					genie_n_muons++;
					if( genie_n_muons > 1 ) return 0;
					else continue;
				}
				else if( pdg == 2112 ) continue; // neutrons allowed
				else if( pdg == 2212 ) continue; // protons allowed
				else if( pdg == 22 && energy <= m_photon_energy_cut ) continue; // low energy photons allowed
				else return 0; // not other pdgs allowed
		
			}
		}
		else {
			for(int i = 0; i < mc_nFSPart; i++) {
				int pdg =  mc_FSPartPDG[i];
				double energy = mc_FSPartE[i];
				double KEp = energy - MinervaUnits::M_p;
				
				if( pdg == -13 ) { // antimuon
					genie_n_muons++;
					if( genie_n_muons > 1 ) return 0; // Check muon count
					continue;
				}
				else if( pdg == 2112 ) continue; // neutron
				else if( pdg == 2212 && KEp <= protonKECut ) continue; // proton <= proton KE cut
				else if( pdg == 22 && energy <= m_photon_energy_cut ) continue; // low energy photons
				else return 0; // not other pdgs allowed
			}
		}
		*/
		if( ( neutrinoMode && genie_n_muons     == 0) ||
		    (!neutrinoMode && genie_n_antimuons == 0)   ) return 0;
		else return 1;
	}

	int CVUniverse::GetTruthIsCCQELike() const {  // cut hardwired for now
		std::vector<int>mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		std::vector<double>mc_FSPartE = GetVecDouble("mc_FSPartE");
		bool neutrinoMode = CVUniverse::GetTruthNuPDG() > 0;
		int mc_nFSPart = GetInt("mc_nFSPart");
		//int mc_incoming = GetInt("mc_incoming");
		//int mc_current = GetInt("mc_current");
		bool passes = ( CVUniverse::passTrueCCQELike(neutrinoMode, mc_FSPartPDG, mc_FSPartE, mc_nFSPart, m_proton_ke_cut));

		return passes;
	}

	// all CCQElike without proton cut enabled

	int CVUniverse::GetTruthIsCCQELikeAll() const {  // cut hardwired for now
		std::vector<int>mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		std::vector<double>mc_FSPartE = GetVecDouble("mc_FSPartE");
		bool neutrinoMode = CVUniverse::GetTruthNuPDG() > 0;
		int mc_nFSPart = GetInt("mc_nFSPart");
		//int mc_incoming = GetInt("mc_incoming");
		//int mc_current = GetInt("mc_current");
		bool passes = ( CVUniverse::passTrueCCQELike(neutrinoMode, mc_FSPartPDG, mc_FSPartE, mc_nFSPart, 10000.));

		return passes;
	}

	// ------------------------------------------------------------------------------
	// ----------------- Added by Sean for Neutrino ---------------------------------
	// ------------------------------------------------------------------------------

	// Interaction Vertex

	int CVUniverse::GetHasInteractionVertex() const { return GetInt("has_interaction_vertex"); }

	// Isolated Blobs and Charged Pions
	
	int CVUniverse::GetNBlobs() const {
		int n_blobs = 0;
		int kmax = GetInt("nonvtx_iso_blobs_start_position_z_in_prong_sz");
		std::vector<double> blob_z_starts = GetVecDouble("nonvtx_iso_blobs_start_position_z_in_prong");	
		// counts blobs with zvertex greater than set value
		for(int k=0; k<kmax; ++k){
			if(blob_z_starts[k] > m_min_blob_zvtx) n_blobs++;
		}
		return n_blobs;
	}

	// One charged pion and charged pion count
	
	int CVUniverse::GetTruthHasSingleChargedPion() const {
		int genie_n_charged_pion = 0;
		std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		std::vector<double> mc_FSPartE = GetVecDouble("mc_FSPartE");
		int mc_nFSPart = GetInt("mc_nFSPart");

		for(int i = 0; i < mc_nFSPart; i++){
			int pdg =  mc_FSPartPDG[i];

			if(      pdg             ==  111   ) return 0; // Neutral pions
			else if( abs(pdg)        ==  211   ) genie_n_charged_pion++;
			// Intermediate check of charged pion count
			if ( genie_n_charged_pion >    1   ) return 0;
		}
		
		if( genie_n_charged_pion == 1 ) return 1;
		return 0; // i.e. if genie_n_charged_pion == 0
	}

	int CVUniverse::GetTrueChargedPionCount() const {
		int genie_n_charged_pion = 0;
		std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		int mc_nFSPart = GetInt("mc_nFSPart");

		for(int i = 0; i < mc_nFSPart; i++){
			if( abs(mc_FSPartPDG[i]) == 211 ) genie_n_charged_pion++;
		}
		
		return genie_n_charged_pion;
	}

	// Michel Electrons and Neutral Pions

	int CVUniverse::GetNMichel() const { return GetInt("has_michel_vertex_type_sz"); }
	int CVUniverse::GetImprovedNMichel() const { return GetInt("improved_michel_match_vec_sz"); }
	int CVUniverse::GetFittedNMichel() const { return GetInt("FittedMichel_michel_fitPass_sz"); }
	
	int CVUniverse::GetTrueFittedNMichel() const {
		int ntruefittedmichels = 0;
		int nfittedmichels = GetFittedNMichel();
		for (int i =0; i< nfittedmichels; i++) {
			double datafrac = GetVecElem("FittedMichel_michel_datafraction", i);
			int fitted = GetVecElem("FittedMichel_michel_fitPass", i);
			if (fitted == 0) continue;
			if (datafrac > 0.5) continue;
			ntruefittedmichels++;
		}
		return ntruefittedmichels;
	}

	int CVUniverse::GetHasMichelElectron() const {
		if(GetNMichel() > 0) return 1;
		return 0;
	}
	
	int CVUniverse::GetHasImprovedMichelElectron() const {
		if(GetImprovedNMichel() > 0) return 1;
		return 0;
	}

	int CVUniverse::GetTruthHasMichel() const { return GetInt("truth_reco_has_michel_electron"); }
	int CVUniverse::GetTruthHasImprovedMichel() const { return GetInt("truth_improved_michel_electron"); }

	int CVUniverse::GetTruthHasSingleNeutralPion() const {
		int genie_n_neutral_pion = 0;
		std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		int mc_nFSPart = GetInt("mc_nFSPart");

		for(int i = 0; i < mc_nFSPart; i++){
			int pdg =  mc_FSPartPDG[i];

			if(      abs(pdg)        ==  211   ) return 0; // Charged pions
			else if( pdg             ==  111   ) genie_n_neutral_pion++;
			// Intermediate check of neutral pion count
			if( genie_n_neutral_pion >     1   ) return 0;
		}
		// Check final neutral pion count
		if( genie_n_neutral_pion == 1 ) return 1;
		return 0; // By process of elimination, if neutral pion count == 0
	}

	int CVUniverse::GetTrueNeutralPionCount() const {
		int genie_n_neutral_pion = 0;
		std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		int mc_nFSPart = GetInt("mc_nFSPart");

		for(int i = 0; i < mc_nFSPart; i++){
			if( mc_FSPartPDG[i] == 111 ) genie_n_neutral_pion++;
		}

		return genie_n_neutral_pion;
	}

	// Michel+Blobs and MultiPion

	int CVUniverse::GetTruthHasMultiPion() const {
		int genie_n_pion = 0;
		int genie_er_n_eta = 0;
		std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		int mc_nFSPart = GetInt("mc_nFSPart");

		for(int i = 0; i < mc_nFSPart; i++){
			int pdg =  mc_FSPartPDG[i];
			if( abs(pdg)      ==  211 ||
			    pdg           ==  111   ) genie_n_pion++;
			if( genie_n_pion > 1 ) return 1; // End early if conditions met
		}
		
		// Look for presence of Eta in mc_er_*... They typically decay into 2+ pions
		int nerpart = GetInt("mc_er_nPart");
		std::vector<int> erpartID = GetVecInt("mc_er_ID");
		std::vector<int> erpartstatus = GetVecInt("mc_er_status");
		for(int i = 0; i < nerpart; i++){
			int status = erpartstatus[i];
			int id = erpartID[i];

			if(abs(status) == 14 && id == 221) return 1; // If there is an Eta passes
		}
		
		// If no eta and genie_n_pion < 2 then fails
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
	
	int CVUniverse::PassProtonScoreCut(double score, double tree_Q2) const {
		int index = 0;
		for (int i = 0 ; i < m_proton_score_Q2QEs.size() ; i++ ) {
			if ( tree_Q2 >= m_proton_score_Q2QEs[i] ) index++;
		}
		if ( score < m_proton_score_mins[index] ) return 0;
		return 1; 
	}
	
	int CVUniverse::PassAllProtonScoreCuts(std::vector<double> scores, double tree_Q2) const {
		int index = 0;
		for ( int i = 0 ; i < m_proton_score_Q2QEs.size() ; i++ ) {
			if ( tree_Q2 >= m_proton_score_Q2QEs[i] ) index++;
		}
		for ( auto score:scores ) {
			if ( score < m_proton_score_mins[index] ) return 0;
		}
		return 1; 
	}

	double CVUniverse::GetPrimaryProtonScore() const {
		return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_score1").c_str());
	}

	int CVUniverse::GetIsPrimaryProton() const {
		if(GetMultiplicity() == 1) return 1; // NA when multiplicity is 1
		// define and get applicable variables
		double tree_Q2 = GetQ2QEGeV();
		double proton_score1 = GetPrimaryProtonScore();
		int passes = PassProtonScoreCut(proton_score1,tree_Q2);
		return passes;
	}

	int CVUniverse::GetTruthHasSingleProton() const { return GetInt("truth_reco_has_single_proton"); }

	int CVUniverse::GetAllExtraTracksProtons() const {
		if(GetMultiplicity() == 1) return 1; // NA when multiplicity is 1
		int n_sec_proton_scores1 = GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1_sz").c_str());
		if(n_sec_proton_scores1 == 0) return 1; // NA if not secondary proton candidates

		// define and get applicable variables
		double tree_Q2 = GetQ2QEGeV();
		std::vector<double> sec_proton_scores1 = GetVecDouble(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1").c_str());

		int passes = PassAllProtonScoreCuts(sec_proton_scores1,tree_Q2);
		return passes;
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
			if( pdg == 2212         && 
				KEp  > m_proton_ke_cut ) genie_n_protons++;
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

	int CVUniverse::GetMCTargetA() const { return GetInt("mc_targetA"); }
	int CVUniverse::GetMCTargetZ() const { return GetInt("mc_targetZ"); }
	int CVUniverse::GetMCTargetNucleon() const { return GetInt("mc_targetNucleon"); }

	int CVUniverse::Dummy() const { return 0; }
    
#endif
