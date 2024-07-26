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
#include "include/CVFunctions.h"
#include "include/TMVAUtils.h"
#include "utils/expandEnv.h"
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
	int CVUniverse::m_analysis_neutrino_pdg = -14;
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
	std::map<int,int> CVUniverse::m_fs_pdg_counts = std::map<int,int>();
	std::map<int,int> CVUniverse::m_fs_pdg_counts_with_constraints = std::map<int,int>();
	std::map<std::string,bool> CVUniverse::m_passes_signal_cuts = std::map<std::string,bool>();
	std::map<std::string,bool> CVUniverse::m_passes_signal_cuts_old = std::map<std::string,bool>();
	std::map<std::string,RReader> CVUniverse::m_tmva_models = std::map<std::string,RReader>();
	std::vector<std::string> CVUniverse::m_tmva_classes = {};
	std::vector<float> CVUniverse::m_response_vec = {};
	std::map<std::string,float> CVUniverse::m_response_map = std::map<std::string,float>();
	std::vector<std::string> CVUniverse::m_tmva_model_names = {};
	std::map<std::string,std::string> CVUniverse::m_sample_categories = std::map<std::string,std::string>();
	std::vector<float> CVUniverse::m_xgboost_response_vec = {};
	
	bool CVUniverse::_is_analysis_neutrino_pdg_set = false;
	bool CVUniverse::_is_min_blob_zvtx_set = false;
	bool CVUniverse::_is_photon_energy_cut_set = false;
	bool CVUniverse::_is_proton_ke_cut_set = false;
	bool CVUniverse::_is_proton_score_config_set = false;
	bool CVUniverse::_are_fs_pdgs_counted = false;
	bool CVUniverse::_are_signal_truths_set = false;
	bool CVUniverse::_are_signal_truths_set_old = false;
	bool CVUniverse::_is_tmva_model_loaded = false;
	bool CVUniverse::_is_response_vec_filled = false;
	bool CVUniverse::_is_xgboost_response_vec_filled = false;
	
	///////////////// Incoming Neutrino PDG /////////////////
	int CVUniverse::GetAnalysisNeutrinoPDG() { return m_analysis_neutrino_pdg; }
	bool CVUniverse::SetAnalysisNeutrinoPDG( int neutrino_pdg, bool print ) {
		if( _is_analysis_neutrino_pdg_set ) {  
			std::cout << "WARNING: YOU ATTEMPTED TO SET PHOTON ENERGY CUT A SECOND TIME. "
			          << "THIS IS NOT ALLOWED FOR CONSISTENCY." << std::endl;
			return 0; 
		} else {
			m_analysis_neutrino_pdg = neutrino_pdg;
			_is_analysis_neutrino_pdg_set = true;
			if( print ) std::cout << "Analysis neutrino PDG set to " << m_analysis_neutrino_pdg << std::endl;
			return 1;
		}
	}
	
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
			if( print ) std::cout << "Minimum blob Z vertex cutoff set to " << m_min_blob_zvtx << std::endl;
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
			if( print ) std::cout << "Photon low energy cutoff set to " << m_photon_energy_cut << " MeV" << std::endl;
			return 1;
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
			if( print ) std::cout << "ProtonKECut set to " << m_proton_ke_cut << " MeV" << std::endl;
			return 1;
		}
	}
	
	///////////////// Proton Score configuration /////////////////
	NuConfig CVUniverse::GetProtonScoreConfig(bool print = false) {
		if(!_is_proton_score_config_set) { // Uses default configuration, which produces default m_proton_score_* values
			std::cout << "\nUSING DEFAULT PROTON SCORE CONFIGURATION.\n\n";
			m_proton_score_config.ReadFromString(R"({"band1":{"Q2QE_max":0.2,"pass_proton_score_min":0.2},"band2":{"Q2QE_range":[0.2,0.6],"pass_proton_score_min":0.1},"band3":{"Q2QE_min":0.6,"pass_proton_score_min":0.0}})");
			if( print ) m_proton_score_config.Print();
		}
		else {
			std::cout << "\nUsing proton score configuration provided by user configuration file.\n\n";
			if( print ) m_proton_score_config.Print();
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
			if( print ) m_proton_score_config.Print();
			if( m_proton_score_config.GetKeys().size() == 1) {
				// Passing proton score value same for all values of Q2QE
				m_proton_score_mins = {};
				m_proton_score_Q2QEs = {};
				m_proton_score_mins.push_back(m_proton_score_config.GetDouble("pass_proton_score_min"));
			}
			else { // There are Q2QE values that dictate passing proton score values
				m_proton_score_mins = {};
				m_proton_score_Q2QEs = {};
				for( auto band:m_proton_score_config.GetKeys() ) {
					NuConfig bandConfig = m_proton_score_config.GetConfig(band);
					m_proton_score_mins.push_back(bandConfig.GetDouble("pass_proton_score_min"));
					if( bandConfig.IsMember("Q2QE_max") ) {
						m_proton_score_Q2QEs.push_back(bandConfig.GetDouble("Q2QE_max"));
					}
					else if( bandConfig.IsMember("Q2QE_range") ) {
						m_proton_score_Q2QEs.push_back(bandConfig.GetDoubleVector("Q2QE_range")[1]);
					}
				}
			}
			_is_proton_score_config_set = true;
			return 1;
		}
	}
	///////////////// FS PDG Counts /////////////////
	bool CVUniverse::SetFSParticlePDGCounts() const {
		if( _are_fs_pdgs_counted ) {  
			std::cout << "WARNING: YOU ATTEMPTED TO COUNT FS PARTICLE PDGS A SECOND TIME WITHOUT RESETTING. "
			          << "THIS IS NOT ALLOWED FOR CONSISTENCY." << std::endl;
			return 0; 
		}
		else {
			std::vector<int> mc_FSPartPDG = GetVec<int>("mc_FSPartPDG");
			std::vector<double> mc_FSPartE = GetVec<double>("mc_FSPartE");
			double m_proton_energy_cut = m_proton_ke_cut + MinervaUnits::M_p;
			for( int i=0; i<mc_FSPartPDG.size(); i++ ) {
				m_fs_pdg_counts[mc_FSPartPDG[i]]++;
				if( (mc_FSPartPDG[i] == 22   && mc_FSPartE[i] > m_photon_energy_cut) ||
				    (mc_FSPartPDG[i] == 2212 && mc_FSPartE[i] > m_proton_energy_cut) ||
				    (mc_FSPartPDG[i] != 22   && mc_FSPartPDG[i] != 2212            )   ) {
					m_fs_pdg_counts_with_constraints[mc_FSPartPDG[i]]++;
				}
			}
			_are_fs_pdgs_counted = true;
			return 1;
		}
	}
	bool CVUniverse::AreFSParticlePDGsCounted() {
		return _are_fs_pdgs_counted;
	}
	int CVUniverse::GetFSConstrainedParticleCount(int pdg) { 
		if( !_are_fs_pdgs_counted ) {
			std::cout << "WARNING: FS PDGS NOT COUNTED." << std::endl;
			return 0;
		}
		return m_fs_pdg_counts_with_constraints[pdg]; 
	}
	int CVUniverse::GetFSParticleCount(int pdg) { 
		if( !_are_fs_pdgs_counted ) {
			std::cout << "WARNING: FS PDGS NOT COUNTED." << std::endl;
			return 0;
		}
		return m_fs_pdg_counts[pdg]; 
	}
	bool CVUniverse::ResetFSParticlePDGCounts() {
		m_fs_pdg_counts = std::map<int,int>();
		m_fs_pdg_counts_with_constraints = std::map<int,int>();
		_are_fs_pdgs_counted = false;
		return 1;
	}
	
	///////////////// Signal Cuts /////////////////
	bool CVUniverse::SetSignalTruths() const {
		if( _are_signal_truths_set ) {
			std::cout << "WARNING: YOU ATTEMPTED TO GET SIGNAL TRUTHS A SECOND TIME WITHOUT RESETTING. "
			          << "EITHER RESET BETWEEN EVENTS OR DELETE SECOND INSTANCE OF CVUniverse::GetSignalTruths()." << std::endl;
			return 0; 
		}
		else {
			m_passes_signal_cuts["qelike"] = GetTruthIsCCQELike_new();
			m_passes_signal_cuts["1chargedpion"] = GetTruthIs1ChargedPion_new();
			m_passes_signal_cuts["1neutralpion"] = GetTruthIs1NeutralPion_new();
			m_passes_signal_cuts["multipion"] = GetTruthIsMultiPion_new();
			_are_signal_truths_set = true;
			return 1;
		}
	}
	bool CVUniverse::SetSignalTruths_old() const {
		if( _are_signal_truths_set_old ) {
			std::cout << "WARNING: YOU ATTEMPTED TO GET SIGNAL TRUTHS A SECOND TIME WITHOUT RESETTING. "
			          << "EITHER RESET BETWEEN EVENTS OR DELETE SECOND INSTANCE OF CVUniverse::GetSignalTruths_old()." << std::endl;
			return 0; 
		}
		else {
			m_passes_signal_cuts_old["qelike"] = GetTruthIsCCQELike_old();
			m_passes_signal_cuts_old["1chargedpion"] = GetTruthIs1ChargedPion_old();
			m_passes_signal_cuts_old["1neutralpion"] = GetTruthIs1NeutralPion_old();
			m_passes_signal_cuts_old["multipion"] = GetTruthIsMultiPion_old();
			_are_signal_truths_set_old = true;
			return 1;
		}
	}
	bool CVUniverse::AreSignalTruthsSet() {
		return _are_signal_truths_set;
	}
	bool CVUniverse::AreSignalTruthsSet_old() {
		return _are_signal_truths_set_old;
	}
	bool CVUniverse::GetSignalTruth(std::string signal) {
		if( (signal == "qelike")       ||
		    (signal == "1chargedpion") ||
		    (signal == "1neutralpion") ||
		    (signal == "multipion")      ) {
			if( !_are_fs_pdgs_counted ) {
				std::cout << "WARNING: FS PDGS NOT COUNTED." << std::endl;
				return 0;
			}
			else if( !_are_signal_truths_set ) { 
				std::cout << "WARNING: SIGNAL TRUTHS NOT SET." << std::endl;
				return 0;
			}
			else return m_passes_signal_cuts[signal];
		} 
		else {
			std::cout << "ERROR: " << signal << " NOT A VALID SIGNAL NAME." << std::endl;
			return 0;
		}
	}
	bool CVUniverse::GetSignalTruth_old(std::string signal) {
		if( (signal == "qelike")       ||
		    (signal == "1chargedpion") ||
		    (signal == "1neutralpion") ||
		    (signal == "multipion")      ) {
			if( !_are_signal_truths_set_old ) { 
				std::cout << "WARNING: SIGNAL TRUTHS NOT SET." << std::endl;
				return 0;
			}
			else return m_passes_signal_cuts_old[signal];
		}
		else {
			std::cout << "ERROR: " << signal << " NOT A VALID SIGNAL NAME." << std::endl;
			return 0;
		}
	}
	bool CVUniverse::ResetSignalTruths() {
		m_passes_signal_cuts = std::map<std::string,bool>();
		_are_signal_truths_set = false;
		m_passes_signal_cuts_old = std::map<std::string,bool>();
		_are_signal_truths_set_old = false;
		return 1;
	}
	
	//////// TMVA Models /////////
	bool CVUniverse::LoadTMVAModel(std::string name, std::string path) {
		m_tmva_models[name].LoadModel(path);
		m_tmva_classes = m_tmva_models[name].GetClassNames();
		return 1;
	}
	std::map<std::string,RReader> * CVUniverse::GetPointerToTMVAModels() {
		std::map<std::string,RReader> * models = &m_tmva_models;
		return models;
	}
	bool CVUniverse::ComputeTMVAResponse(std::string name, std::vector<float> var_values) {
		m_response_vec = m_tmva_models[name].Compute(var_values);
		for (int i=0; i<m_response_vec.size(); i++) {
			m_response_map[m_tmva_classes[i]] = m_response_vec[i];
		}
		_is_response_vec_filled = true;
		return 1;
	}
	bool CVUniverse::SetTMVAResponse(std::vector<float> vector_response) {
		m_response_vec = vector_response;
		for (int i=0; i<vector_response.size(); i++) {
			m_response_map[m_tmva_classes[i]] = vector_response[i];
		}
		_is_response_vec_filled = true;
		return 1;
	}
	bool CVUniverse::ResetTMVAResponse() {
		m_response_vec = {};
		m_response_map = std::map<std::string,float>();
		_is_response_vec_filled = false;
		return 1;
	}
	std::vector<float> CVUniverse::GetTMVAVectorResponse() {
		return m_response_vec;
	}
	float CVUniverse::GetTMVAClassResponse(std::string name) {
		return m_response_map[name];
	}
	bool CVUniverse::SetSampleCategory(std::string sample,std::string truth) {
		m_sample_categories[sample] = truth;
		return 1;
	}
	std::string CVUniverse::GetSampleCategory(std::string sample) {
		return m_sample_categories[sample];
	}
	
	//////// xgboost Models /////////
	bool CVUniverse::SetXgboostVectorResponse(std::vector<float> response_vec) {
		m_xgboost_response_vec = response_vec;
		_is_xgboost_response_vec_filled = true;
		return 1;
	}
	bool CVUniverse::ResetXgboostVectorResponse() {
		m_xgboost_response_vec = {};
		_is_xgboost_response_vec_filled = false;
		return 1;
	}
	std::vector<float> CVUniverse::GetXgboostVectorResponse() {
		return m_xgboost_response_vec;
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
		// if(wgt_geant != 1.0) std::cout << ShortName() << wgt_geant << std::endl;
		 
		// MINOS muon tracking efficiency
		if(!IsTruth() && IsMinosMatchMuon()) wgt_mueff = GetMinosEfficiencyWeight();

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

	// fast filter that reproduces CCQENu tuple cuts

	bool CVUniverse::FastFilter() const {
		bool result = false;
		// if (GetMultiplicity() < 1) return result;
		if (GetIsMinosMatchTrack() != -1) return result;
		if (GetZVertex() < 5980 || GetZVertex() > 8422) return result;
		if (GetApothemX() > 850.) return result;
		if (GetApothemY() > 850.) return result;
		return true;
	}
	bool CVUniverse::TrueFastFilter() const { return true; }

	double CVUniverse::GetEventID() const { return GetDouble("eventID"); }
	int CVUniverse::GetMultiplicity() const { return GetInt("multiplicity"); }
	int CVUniverse::GetDeadTime() const { return GetInt("phys_n_dead_discr_pair_upstream_prim_track_proj"); }
	
	// ----------------------- Analysis-related Variables ------------------------

	int CVUniverse::GetIsMinosMatchTrack() const { return GetInt("muon_is_minos_match_track"); }
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
		if(CVUniverse::GetEnuCCQEGeV()<=0.0)return 0.0;
		//std::cout<<"CVUniverse::GetQ2QE Cannot calculate neutrino energy "<<std::endl;
		else{
			// Q2 = 2.0*GetEnuCCQE() * ( GetEmu() - GetPmu() * cos( GetThetamu() ) ) - pow( MinervaUnits::M_mu, 2 );
			double q2 = PlotUtils::qSquaredCCQE( GetEmu(), GetPmu(), GetThetamu(), charge )*MeVGeV*MeVGeV;
			//  if(q2 < q2min)q2 =  q2min;
			return q2;
		}
		// return Q2;
	}

	double CVUniverse::GetTrueQ2QEGeV() const {
		const double q2min = 0.001;
		int charge = GetAnalysisNuPDG() > 0? 1:-1;
		double q2 = PlotUtils::qSquaredCCQE( GetElepTrue(), GetPlepTrue(), GetThetalepTrue(), charge )*MeVGeV*MeVGeV;
		// if(q2 < q2min)q2 =  q2min;
		return q2;
	}

	double CVUniverse::GetLog10Q2QEGeV() const { return std::log10( CVUniverse::GetQ2QEGeV() ); }
	double CVUniverse::GetTrueLog10Q2QEGeV() const { return std::log10( GetTrueQ2QEGeV() ); }


	// ------------------------------ Muon Variables -----------------------------

	double CVUniverse::GetEmuGeV() const { return std::sqrt(GetPmu()*GetPmu() + pow( MinervaUnits::M_mu, 2 ))*MeVGeV; }
	double CVUniverse::GetTrueEmuGeV() const { return GetElepTrue()*MeVGeV; } // not sure if this is right
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
	double CVUniverse::GetTrueThetamu() const {
		TVector3 p3lep( GetVecElem("mc_primFSLepton",0), GetVecElem("mc_primFSLepton",1), GetVecElem("mc_primFSLepton",2) );
		p3lep.RotateX(MinervaUnits::numi_beam_angle_rad);
		return p3lep.Theta();  //HMS fix this after a question from Christian
	}
	//double CVUniverse::GetTrueThetamu() const { return GetThetalepTrue(); }
	
	double CVUniverse::GetThetamuDegrees() const { return GetThetamu()*180/M_PI; }
	double CVUniverse::GetTrueThetamuDegrees() const { return GetTrueThetamu()*180/M_PI; }
	double CVUniverse::GetThetaXmuDegrees() const { return GetThetaXmu()*180/M_PI; }
	double CVUniverse::GetTrueThetaXmuDegrees() const { return GetTrueThetaXmu()*180/M_PI; }
	double CVUniverse::GetThetaYmuDegrees() const { return GetThetaYmu()*180/M_PI; }
	double CVUniverse::GetTrueThetaYmuDegrees() const { return GetTrueThetaYmu()*180/M_PI; }

	// Tracks not included amongst the primary muon track or any of the proton candidate tracks
	int CVUniverse::GetMissingTrackCount() const {
		int obs_tracks = GetNumberOfProtonCandidates();
		if (GetEmuGeV() >= 0) {
			obs_tracks++;
		}
		int all_tracks = GetMultiplicity();
		return all_tracks - obs_tracks;
	}

	// ----------------------------- Proton Variables ----------------------------

	double CVUniverse::GetHadronEGeV() const { return (GetCalRecoilEnergyGeV() + GetNonCalRecoilEnergyGeV()); }
	
	int CVUniverse::GetNumberOfProtonCandidates() const {
		int count = 0;
		if (GetPrimaryProtonScore1() >= 0) count++;
		int sec_count = GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1_sz").c_str());
		if (sec_count >= 1) {	
			count += sec_count;
		}
		return count;
	}
	
	double CVUniverse::GetMinProtonScore1() const {
		double primary_score = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_score1").c_str());
		if (primary_score < 0) {
			return -9999.;
		} 
		else if (GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1_sz").c_str()) == 0) {
			return primary_score;
		} 
		else {
			std::vector<double> scores = GetVec<double>(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1").c_str());
			scores.push_back(primary_score);
			return *min_element(std::begin(scores), std::end(scores));
		}
	}
	
	double CVUniverse::GetProtonScore(int i) const {
		if( i == 0 ) return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_score").c_str());
		else if( GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores_sz").c_str()) < i ) return -9999.;
		else return GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores").c_str(), i-1);
	}
	double CVUniverse::GetProtonScore1(int i) const {
		if( i == 0 ) return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_score1").c_str());
		else if( GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1_sz").c_str()) < i ) return -9999.;
		else return GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1").c_str(), i-1);
	}
	double CVUniverse::GetProtonScore2(int i) const {
		if( i == 0 ) return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_score2").c_str());
		else if( GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores2_sz").c_str()) < i ) return -9999.;
		else return GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores2").c_str(), i-1);
	}
	double CVUniverse::GetProtonScore_0() const { return GetProtonScore(0); }
	double CVUniverse::GetProtonScore_1() const { return GetProtonScore(1); }
	double CVUniverse::GetProtonScore_2() const { return GetProtonScore(2); }
	double CVUniverse::GetProtonScore_3() const { return GetProtonScore(3); }
	double CVUniverse::GetProtonScore_4() const { return GetProtonScore(4); }
	double CVUniverse::GetProtonScore_5() const { return GetProtonScore(5); }
	double CVUniverse::GetProtonScore_6() const { return GetProtonScore(6); }
	double CVUniverse::GetProtonScore_7() const { return GetProtonScore(7); }
	double CVUniverse::GetProtonScore_8() const { return GetProtonScore(8); }
	double CVUniverse::GetProtonScore_9() const { return GetProtonScore(9); }
	
	double CVUniverse::GetProtonScore1_0() const { return GetProtonScore1(0); }
	double CVUniverse::GetProtonScore1_1() const { return GetProtonScore1(1); }
	double CVUniverse::GetProtonScore1_2() const { return GetProtonScore1(2); }
	double CVUniverse::GetProtonScore1_3() const { return GetProtonScore1(3); }
	double CVUniverse::GetProtonScore1_4() const { return GetProtonScore1(4); }
	double CVUniverse::GetProtonScore1_5() const { return GetProtonScore1(5); }
	double CVUniverse::GetProtonScore1_6() const { return GetProtonScore1(6); }
	double CVUniverse::GetProtonScore1_7() const { return GetProtonScore1(7); }
	double CVUniverse::GetProtonScore1_8() const { return GetProtonScore1(8); }
	double CVUniverse::GetProtonScore1_9() const { return GetProtonScore1(9); }
	
	double CVUniverse::GetProtonScore2_0() const { return GetProtonScore2(0); }
	double CVUniverse::GetProtonScore2_1() const { return GetProtonScore2(1); }
	double CVUniverse::GetProtonScore2_2() const { return GetProtonScore2(2); }
	double CVUniverse::GetProtonScore2_3() const { return GetProtonScore2(3); }
	double CVUniverse::GetProtonScore2_4() const { return GetProtonScore2(4); }
	double CVUniverse::GetProtonScore2_5() const { return GetProtonScore2(5); }
	double CVUniverse::GetProtonScore2_6() const { return GetProtonScore2(6); }
	double CVUniverse::GetProtonScore2_7() const { return GetProtonScore2(7); }
	double CVUniverse::GetProtonScore2_8() const { return GetProtonScore2(8); }
	double CVUniverse::GetProtonScore2_9() const { return GetProtonScore2(9); }
	
	int CVUniverse::GetPassProtonScoreCut(int method, int candidate, double tree_Q2) const {
		double score;
		if( method == 0 ) { score = GetProtonScore(candidate); }
		else if( method == 1 ) { score = GetProtonScore1(candidate); }
		else if( method == 2 ) { score = GetProtonScore2(candidate); }
		else { score = -1; }		
		if( score < 0 ) return -1;
		int index = 0;
		for ( int i = 0 ; i < m_proton_score_Q2QEs.size() ; i++ ) {
			if( tree_Q2 >= m_proton_score_Q2QEs[i] ) index++;
		}
		if( score < m_proton_score_mins[index] ) return 0;
		else return 1; 
	}
	int CVUniverse::GetPassScoreCutProton1_0() const { return GetPassProtonScoreCut(1,0,GetQ2QEGeV()); }
	int CVUniverse::GetPassScoreCutProton1_1() const { return GetPassProtonScoreCut(1,1,GetQ2QEGeV()); }
	int CVUniverse::GetPassScoreCutProton1_2() const { return GetPassProtonScoreCut(1,2,GetQ2QEGeV()); }
	int CVUniverse::GetPassScoreCutProton1_3() const { return GetPassProtonScoreCut(1,3,GetQ2QEGeV()); }
	int CVUniverse::GetPassScoreCutProton1_4() const { return GetPassProtonScoreCut(1,4,GetQ2QEGeV()); }
	int CVUniverse::GetPassScoreCutProton1_5() const { return GetPassProtonScoreCut(1,5,GetQ2QEGeV()); }
	int CVUniverse::GetPassScoreCutProton1_6() const { return GetPassProtonScoreCut(1,6,GetQ2QEGeV()); }
	int CVUniverse::GetPassScoreCutProton1_7() const { return GetPassProtonScoreCut(1,7,GetQ2QEGeV()); }
	int CVUniverse::GetPassScoreCutProton1_8() const { return GetPassProtonScoreCut(1,8,GetQ2QEGeV()); }
	int CVUniverse::GetPassScoreCutProton1_9() const { return GetPassProtonScoreCut(1,9,GetQ2QEGeV()); }
	
	int CVUniverse::GetSecondaryProtonCandidateCount1() const {
		return GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1_sz").c_str());
	}
	
	int CVUniverse::GetSecondaryProtonCandidateCount() const {
		return GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores_sz").c_str());
	}
	
	int CVUniverse::GetPassAllProtonScoreCuts(std::vector<double> scores, double tree_Q2, int count) const {
		int index = 0;
		for ( int i = 0 ; i < m_proton_score_Q2QEs.size() ; i++ ) {
			if( tree_Q2 >= m_proton_score_Q2QEs[i] ) index++;
		}
		for ( int i = 0 ; i < count ; i++ ) {
			if( scores[i] < m_proton_score_mins[index] ) return 0;
		}
		return 1; 
	}

	double CVUniverse::GetPrimaryProtonScore() const {
		return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_score").c_str());
	}
	double CVUniverse::GetPrimaryProtonScore1() const {
		return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_score1").c_str());
	}
	double CVUniverse::GetPrimaryProtonScore2() const {
		return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_score2").c_str());
	}

	int CVUniverse::GetIsPrimaryProton() const {
		if(GetMultiplicity() < 2) return 1; // NA when multiplicity is < 2
		// define and get applicable variables
		double tree_Q2 = GetQ2QEGeV();
		int passes = GetPassProtonScoreCut(0,0,tree_Q2);
		return passes;
	}
	int CVUniverse::GetIsPrimaryProton1() const {
		if(GetMultiplicity() < 2) return 1; // NA when multiplicity is < 2
		// define and get applicable variables
		double tree_Q2 = GetQ2QEGeV();
		int passes = GetPassProtonScoreCut(1,0,tree_Q2);
		return passes;
	}
	
	// Proton Candidate End-of-Track Clusters
	int CVUniverse::GetAreClustsFoundAtPrimaryProtonEnd() const {
		if(GetInt("clusters_found_at_end_proton_prong_sz") > 0) {
			return 1;
		}
		else return 0;
	}
	int CVUniverse::GetNumClustsProtonEnd(int i) const {
		if(GetInt("number_clusters_at_end_proton_prong_sz") > i) {
			return GetVecElem("number_clusters_at_end_proton_prong",i);
		}
		else return -9999;
	}
	int CVUniverse::GetNumClustsPrimaryProtonEnd() const { return GetNumClustsProtonEnd(0); }
	int CVUniverse::GetNumClustsSecProtonEnd_1() const { return GetNumClustsProtonEnd(1); }
	int CVUniverse::GetNumClustsSecProtonEnd_2() const { return GetNumClustsProtonEnd(2); }
	int CVUniverse::GetNumClustsSecProtonEnd_3() const { return GetNumClustsProtonEnd(3); }
	int CVUniverse::GetNumClustsSecProtonEnd_4() const { return GetNumClustsProtonEnd(4); }
	int CVUniverse::GetNumClustsSecProtonEnd_5() const { return GetNumClustsProtonEnd(5); }
	int CVUniverse::GetNumClustsSecProtonEnd_6() const { return GetNumClustsProtonEnd(6); }

	// Calibrated Energy in cluster(s) at end of proton candidate track
	double CVUniverse::GetCalibEClustsProtonEnd(int i) const {
		if(GetInt("calibE_clusters_at_end_proton_prong_sz") > i) {
			return GetVecElem("calibE_clusters_at_end_proton_prong",i);
		}
		else if(GetNumClustsProtonEnd(i) >= 0) return 0.;
		else return -9999.;
	}
	double CVUniverse::GetCalibEClustsPrimaryProtonEnd() const { return GetCalibEClustsProtonEnd(0); }
	double CVUniverse::GetCalibEClustsSecProtonEnd_1() const { return GetCalibEClustsProtonEnd(1); }
	double CVUniverse::GetCalibEClustsSecProtonEnd_2() const { return GetCalibEClustsProtonEnd(2); }
	double CVUniverse::GetCalibEClustsSecProtonEnd_3() const { return GetCalibEClustsProtonEnd(3); }
	double CVUniverse::GetCalibEClustsSecProtonEnd_4() const { return GetCalibEClustsProtonEnd(4); }
	double CVUniverse::GetCalibEClustsSecProtonEnd_5() const { return GetCalibEClustsProtonEnd(5); }
	double CVUniverse::GetCalibEClustsSecProtonEnd_6() const { return GetCalibEClustsProtonEnd(6); }
	
	// Visible Energy in cluster(s) at end of proton candidate track
	double CVUniverse::GetVisEClustsProtonEnd(int i) const {
		if(GetInt("visE_clusters_at_end_proton_prong_sz") > i) {
			return GetVecElem("visE_clusters_at_end_proton_prong",i);
		}
		else if(GetNumClustsProtonEnd(i) >= 0) return 0.;
		else return -9999.;
	}
	double CVUniverse::GetVisEClustsPrimaryProtonEnd() const { return GetVisEClustsProtonEnd(0); }
	double CVUniverse::GetVisEClustsSecProtonEnd_1() const { return GetVisEClustsProtonEnd(1); }
	double CVUniverse::GetVisEClustsSecProtonEnd_2() const { return GetVisEClustsProtonEnd(2); }
	double CVUniverse::GetVisEClustsSecProtonEnd_3() const { return GetVisEClustsProtonEnd(3); }
	double CVUniverse::GetVisEClustsSecProtonEnd_4() const { return GetVisEClustsProtonEnd(4); }
	double CVUniverse::GetVisEClustsSecProtonEnd_5() const { return GetVisEClustsProtonEnd(5); }
	double CVUniverse::GetVisEClustsSecProtonEnd_6() const { return GetVisEClustsProtonEnd(6); }

	// Proton Candidate Track Misc
	double CVUniverse::GetPrimaryProtonTrackLength() const { return GetDouble("proton_track_length"); }
	double CVUniverse::GetPrimaryProtonTrackEndX() const { return GetDouble("proton_track_endx"); }
	double CVUniverse::GetPrimaryProtonTrackEndY() const { return GetDouble("proton_track_endy"); }
	double CVUniverse::GetPrimaryProtonTrackEndZ() const { return GetDouble("proton_track_endz"); }
	
	double CVUniverse::GetProtonCandTrackLength(int i) const {
		double startX, startY, startZ, endX, endY, endZ;
		if (i == 0) {
			startX = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_startPointX").c_str());
			startY = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_startPointY").c_str());
			startZ = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_startPointZ").c_str());
			endX = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_endPointX").c_str());
			endY = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_endPointY").c_str());
			endZ = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_endPointZ").c_str());
		}
		else {
			startX = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_startPointX").c_str(),i-1);
			startY = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_startPointY").c_str(),i-1);
			startZ = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_startPointZ").c_str(),i-1);
			endX = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_endPointX").c_str(),i-1);
			endY = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_endPointY").c_str(),i-1);
			endZ = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_endPointZ").c_str(),i-1);
		}
		if(startZ < 0) return -9999.;
		double length = sqrt(pow(endX-startX,2) + pow(endY-startY,2) + pow(endZ-startZ,2));
		return length;
	}
	
	double CVUniverse::GetProtonCandTrackLength_0() const { return GetProtonCandTrackLength(0); }
	double CVUniverse::GetProtonCandTrackLength_1() const { return GetProtonCandTrackLength(1); }
	double CVUniverse::GetProtonCandTrackLength_2() const { return GetProtonCandTrackLength(2); }
	double CVUniverse::GetProtonCandTrackLength_3() const { return GetProtonCandTrackLength(3); }
	double CVUniverse::GetProtonCandTrackLength_4() const { return GetProtonCandTrackLength(4); }
	double CVUniverse::GetProtonCandTrackLength_5() const { return GetProtonCandTrackLength(5); }
	double CVUniverse::GetProtonCandTrackLength_6() const { return GetProtonCandTrackLength(6); }
	
	// Proton candidate angles wrt beam
	double CVUniverse::GetProtonAngle(int i) const {
		if (i==0) {
			return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_theta").c_str());
		}
		else if (GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_theta_sz").c_str()) >= i) {
			return GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_theta").c_str(),i-1);
		}
		else return -9999.;
	}
	double CVUniverse::GetPrimaryProtonAngle() const { return GetProtonAngle(0); }
	double CVUniverse::GetSecProtonAngle_1() const { return GetProtonAngle(1); }
	double CVUniverse::GetSecProtonAngle_2() const { return GetProtonAngle(2); }
	double CVUniverse::GetSecProtonAngle_3() const { return GetProtonAngle(3); }
	double CVUniverse::GetSecProtonAngle_4() const { return GetProtonAngle(4); }
	double CVUniverse::GetSecProtonAngle_5() const { return GetProtonAngle(5); }
	double CVUniverse::GetSecProtonAngle_6() const { return GetProtonAngle(6); }
	
	double CVUniverse::GetThetaProton(int i) const { /* radians w.r.t. incident nu dirn */
		if (i==0 && GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_score1").c_str())>=0) {
			double thetaX = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_thetaX").c_str());
			double thetaY = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_thetaY").c_str());
			return theta3D(thetaX,thetaY)*180/M_PI;
		}
		else if (i<=GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_thetaX_sz").c_str())) {
			double thetaX = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_thetaX").c_str(),i-1);
			double thetaY = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_thetaY").c_str(),i-1);
			return theta3D(thetaX,thetaY)*180/M_PI;
		}
		else {
			return -9999.;
		}
	}
	double CVUniverse::GetThetaProton0() const { return GetThetaProton(0); }
	double CVUniverse::GetThetaProton1() const { return GetThetaProton(1); }
	double CVUniverse::GetThetaProton2() const { return GetThetaProton(2); }
	double CVUniverse::GetThetaProton3() const { return GetThetaProton(3); }
	double CVUniverse::GetThetaProton4() const { return GetThetaProton(4); }
	double CVUniverse::GetThetaProton5() const { return GetThetaProton(5); }
	double CVUniverse::GetThetaProton6() const { return GetThetaProton(6); }
	
	
	double CVUniverse::GetMuonToPrimaryProtonAngle() const {
		if (GetProtonScore1_0() < 0) return -9999.;
		double theta1 = GetThetamu();
		double phi1 = GetPhimu();
		double theta2 = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_theta").c_str());
		double phi2 = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_phi").c_str());
		double theta = std::acos(std::sin(theta1)*std::cos(phi1)*std::sin(theta2)*std::cos(phi2) +
		                         std::sin(theta1)*std::sin(phi1)*std::sin(theta2)*std::sin(phi2) +
		                         std::cos(theta1)*std::cos(theta2));
		                         return theta*180/M_PI;
	}
	
	// Proton P (from dEdx)
	double CVUniverse::GetPProton(int i) const { 
		if (i==0) {
			return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_P_fromdEdx").c_str());
		}
		else if (i<=GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_P_fromdEdx_sz").c_str())) {
			return GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_P_fromdEdx").c_str(),i-1);
		}
		else {
			return -9999.;
		}
	}
	double CVUniverse::GetPProtonGeV0() const { return GetPProton(0)*MeVGeV; }
	double CVUniverse::GetPProtonGeV1() const { return GetPProton(1)*MeVGeV; }
	double CVUniverse::GetPProtonGeV2() const { return GetPProton(2)*MeVGeV; }
	double CVUniverse::GetPProtonGeV3() const { return GetPProton(3)*MeVGeV; }
	double CVUniverse::GetPProtonGeV4() const { return GetPProton(4)*MeVGeV; }
	double CVUniverse::GetPProtonGeV5() const { return GetPProton(5)*MeVGeV; }
	double CVUniverse::GetPProtonGeV6() const { return GetPProton(6)*MeVGeV; }
	
	// Proton Pt
	double CVUniverse::GetPperpProton(int i) const { 
		double theta = GetThetaProton(i);
		if (theta<-1000) {
			return -9999.;
		}
		else {
			return GetPProton(i)*std::sin(theta); 
		}
	}
	double CVUniverse::GetPperpProtonGeV0() const { return GetPperpProton(0)*MeVGeV; }
	double CVUniverse::GetPperpProtonGeV1() const { return GetPperpProton(1)*MeVGeV; }
	double CVUniverse::GetPperpProtonGeV2() const { return GetPperpProton(2)*MeVGeV; }
	double CVUniverse::GetPperpProtonGeV3() const { return GetPperpProton(3)*MeVGeV; }
	double CVUniverse::GetPperpProtonGeV4() const { return GetPperpProton(4)*MeVGeV; }
	double CVUniverse::GetPperpProtonGeV5() const { return GetPperpProton(5)*MeVGeV; }
	double CVUniverse::GetPperpProtonGeV6() const { return GetPperpProton(6)*MeVGeV; }
	
	// Transverse Momentum Imbalance
	double CVUniverse::GetPtImbalance() const {
		if (GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_score1").c_str()) < 0 ||
		    GetDouble(std::string(MinervaUniverse::GetTreeName()+"_muon_score").c_str()) < 0) {
			return -9999.;
		}
		else {
			double muonP = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_muon_P").c_str());
			double muonPx = muonP*std::sin(GetDouble("muon_thetaX"));
			double muonPy = muonP*std::sin(GetDouble("muon_thetaY"));
			double protonP = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_P_fromdEdx").c_str());
			double protonPx = protonP*std::sin(GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_thetaX").c_str()));
			double protonPy = protonP*std::sin(GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_thetaY").c_str()));
			double totalPx = muonPx + protonPx;
			double totalPy = muonPy + protonPy;
			
			for (int i=0; i<GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_P_fromdEdx_sz").c_str()); i++) {
				double P = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_P_fromdEdx").c_str(),i);
				double thetaX = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_thetaX").c_str(),i);
				double thetaY = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_thetaY").c_str(),i);
				double Px = protonP*std::sin(thetaX);
				double Py = protonP*std::sin(thetaY);
				totalPx += Px;
				totalPy += Py;
			}
			return sqrt(pow(totalPx,2)+pow(totalPy,2));
		}
	}
	double CVUniverse::GetPtImbalanceGeV() const {
		double imbalanceMeV = GetPtImbalance();
		if (imbalanceMeV < 0) {
			return -9999.;
		}
		else {
			return imbalanceMeV*MeVGeV;
		}
	}
	
	// Gap between interaction vertex and start of proton candidate track (mm)
	double CVUniverse::GetProtonTrackVtxGap(int i) const {
		double startX, startY, startZ;
		if(i == 0 && GetPrimaryProtonScore1() >= 0) {
			startX = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_startPointX").c_str());
			startY = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_startPointY").c_str());
			startZ = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_startPointZ").c_str());
		}
		else if(i > 0 && GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_T_fromdEdx_sz").c_str())>=i) {
			startX = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_startPointX").c_str(),i-1);
			startY = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_startPointY").c_str(),i-1);
			startZ = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_startPointZ").c_str(),i-1);
		}
		else {
			return -9999.;
		}
		
		std::vector<double> vtx = GetVec<double>("vtx");
		double gap = sqrt(pow(startX-vtx[0],2) + pow(startY-vtx[1],2) + pow(startZ-vtx[2],2));
		return gap;
	}
	double CVUniverse::GetPrimaryProtonTrackVtxGap() const { return GetProtonTrackVtxGap(0); }
	double CVUniverse::GetSecProtonTrackVtxGap_1() const { return GetProtonTrackVtxGap(1); }
	double CVUniverse::GetSecProtonTrackVtxGap_2() const { return GetProtonTrackVtxGap(2); }
	double CVUniverse::GetSecProtonTrackVtxGap_3() const { return GetProtonTrackVtxGap(3); }
	double CVUniverse::GetSecProtonTrackVtxGap_4() const { return GetProtonTrackVtxGap(4); }
	double CVUniverse::GetSecProtonTrackVtxGap_5() const { return GetProtonTrackVtxGap(5); }
	double CVUniverse::GetSecProtonTrackVtxGap_6() const { return GetProtonTrackVtxGap(6); }
	
	// Proton "TOF"
	double CVUniverse::GetPrimaryProtonTOF() const {
		double ti = GetVecElem("vtx",0);
		if (GetPrimaryProtonScore1() >= 0) {
			double tf = GetVecElem("proton_prong_tpos",0);
			return tf - ti;
		}
		else {
			return -9999.;
		}
	}
	
	// Proton candidate T from dEdx of candidate track
	double CVUniverse::GetPrimaryProtonTfromdEdx() const {
		if(GetPrimaryProtonScore1() >= 0) {
			return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_T_fromdEdx").c_str());
		}
		else return -9999.;
	}
	double CVUniverse::GetSecProtonTfromdEdx(int i) const {
		if(GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_T_fromdEdx_sz").c_str()) > i) {
			return GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_T_fromdEdx").c_str(),i);
		}
		else return -9999.;
	}
	double CVUniverse::GetSecProtonTfromdEdx_1() const { return GetSecProtonTfromdEdx(0); }
	double CVUniverse::GetSecProtonTfromdEdx_2() const { return GetSecProtonTfromdEdx(1); }
	double CVUniverse::GetSecProtonTfromdEdx_3() const { return GetSecProtonTfromdEdx(2); }
	double CVUniverse::GetSecProtonTfromdEdx_4() const { return GetSecProtonTfromdEdx(3); }
	double CVUniverse::GetSecProtonTfromdEdx_5() const { return GetSecProtonTfromdEdx(4); }
	double CVUniverse::GetSecProtonTfromdEdx_6() const { return GetSecProtonTfromdEdx(5); }
	
	// Proton candidate ratio of T from dEdX to track length
	
	double CVUniverse::ProtonRatioTdEdX2TrackLength(int i) const {
		if(i == 0 & GetPrimaryProtonScore1() >= 0) {
			double TfromdEdX = GetDouble(std::string(MinervaUniverse::GetTreeName()+"_proton_T_fromdEdx").c_str());
			double tracklength = GetProtonCandTrackLength(i);
			return TfromdEdX/tracklength;
		}
		if(GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_T_fromdEdx_sz").c_str()) >= i) {
			double TfromdEdX = GetVecElem(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_T_fromdEdx").c_str(),i-1);
			double tracklength = GetProtonCandTrackLength(i);
			return TfromdEdX/tracklength;
		}
		else return -9999.;
	}
	double CVUniverse::ProtonRatioTdEdX2TrackLength_0() const { return ProtonRatioTdEdX2TrackLength(0); }
	double CVUniverse::ProtonRatioTdEdX2TrackLength_1() const { return ProtonRatioTdEdX2TrackLength(1); }
	double CVUniverse::ProtonRatioTdEdX2TrackLength_2() const { return ProtonRatioTdEdX2TrackLength(2); }
	double CVUniverse::ProtonRatioTdEdX2TrackLength_3() const { return ProtonRatioTdEdX2TrackLength(3); }
	
	// Proton candidate total E from T in dEdX and calibrated E in clusters at end of track
	double CVUniverse::GetTotalProtonVisEnergy(int i) const {
		double dEdxT;
		double clusterVisE = GetVecElem("visE_clusters_at_end_proton_prong",i);
		int clusterVisE_sz = GetInt("visE_clusters_at_end_proton_prong_sz");
		
		if(clusterVisE_sz <= i) clusterVisE = 0;
		else 
		
		if(i == 0) dEdxT = GetPrimaryProtonTfromdEdx();
		else dEdxT = GetSecProtonTfromdEdx(i);
		 
		return dEdxT + clusterVisE;
	}
	double CVUniverse::GetTotalPrimaryProtonVisEnergy() const { return GetTotalProtonVisEnergy(0); }
	double CVUniverse::GetTotalSecProtonVisEnergy_1() const { return GetTotalProtonVisEnergy(1); }
	double CVUniverse::GetTotalSecProtonVisEnergy_2() const { return GetTotalProtonVisEnergy(2); }
	double CVUniverse::GetTotalSecProtonVisEnergy_3() const { return GetTotalProtonVisEnergy(3); }
	double CVUniverse::GetTotalSecProtonVisEnergy_4() const { return GetTotalProtonVisEnergy(4); }
	double CVUniverse::GetTotalSecProtonVisEnergy_5() const { return GetTotalProtonVisEnergy(5); }
	double CVUniverse::GetTotalSecProtonVisEnergy_6() const { return GetTotalProtonVisEnergy(6); }
	
	// Fraction of measured proton candidate energy in cone clusters
	double CVUniverse::GetProtonFractionVisEnergyInCone(int i) const {
		if( (i==0 && GetPrimaryProtonScore1()>=0) ||
		    (i>0 && GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_T_fromdEdx_sz").c_str())>=i) ) {
			double clusterVisE = GetVisEClustsProtonEnd(i);
			double totalVisE = GetTotalProtonVisEnergy(i);
			if(clusterVisE == 0) return 0.;
			else return clusterVisE/totalVisE;
		}
		else return -9999.;
	}
	double CVUniverse::GetPrimaryProtonFractionVisEnergyInCone() const { return GetProtonFractionVisEnergyInCone(0); }
	double CVUniverse::GetSecProtonFractionVisEnergyInCone_1() const { return GetProtonFractionVisEnergyInCone(1); }
	double CVUniverse::GetSecProtonFractionVisEnergyInCone_2() const { return GetProtonFractionVisEnergyInCone(2); }
	double CVUniverse::GetSecProtonFractionVisEnergyInCone_3() const { return GetProtonFractionVisEnergyInCone(3); }
	double CVUniverse::GetSecProtonFractionVisEnergyInCone_4() const { return GetProtonFractionVisEnergyInCone(4); }
	double CVUniverse::GetSecProtonFractionVisEnergyInCone_5() const { return GetProtonFractionVisEnergyInCone(5); }
	double CVUniverse::GetSecProtonFractionVisEnergyInCone_6() const { return GetProtonFractionVisEnergyInCone(6); }
	
	// Proton candidate true KE
	double CVUniverse::GetProtonTrueKE(int i) const {
		if(i == 0 && GetInt("proton_prong_PDG") == 2212) {
			return GetVecElem("proton_prong_4p",0) - MinervaUnits::M_p;
		}
		else if(GetInt("seco_protons_prong_4p_E_sz") >= i && GetProtonCandidatePDG(i) == 2212) {
			return GetVecElem("seco_protons_prong_4p_E",i-1) - MinervaUnits::M_p;
		}
		else return -9999.;
	}
	double CVUniverse::GetPrimaryProtonTrueKE() const { return GetProtonTrueKE(0); }
	double CVUniverse::GetSecProtonTrueKE_1() const { return GetProtonTrueKE(1); }
	double CVUniverse::GetSecProtonTrueKE_2() const { return GetProtonTrueKE(2); }
	double CVUniverse::GetSecProtonTrueKE_3() const { return GetProtonTrueKE(3); }
	double CVUniverse::GetSecProtonTrueKE_4() const { return GetProtonTrueKE(4); }
	double CVUniverse::GetSecProtonTrueKE_5() const { return GetProtonTrueKE(5); }
	double CVUniverse::GetSecProtonTrueKE_6() const { return GetProtonTrueKE(6); }
	
	// Proton candidate PDG
	int CVUniverse::GetProtonCandidatePDG(int i) const {
		if(i == 0) {
			return GetInt("proton_prong_PDG");
		}
		else if(GetInt("sec_protons_prong_PDG_sz") >= i) {
			return GetVecElem("sec_protons_prong_PDG",i-1);
		}
		else return -1;
	}
	int CVUniverse::GetPrimaryProtonCandidatePDG() const { return GetProtonCandidatePDG(0); }
	int CVUniverse::GetSecProtonCandidatePDG_1() const { return GetProtonCandidatePDG(1); }
	int CVUniverse::GetSecProtonCandidatePDG_2() const { return GetProtonCandidatePDG(2); }
	int CVUniverse::GetSecProtonCandidatePDG_3() const { return GetProtonCandidatePDG(3); }
	int CVUniverse::GetSecProtonCandidatePDG_4() const { return GetProtonCandidatePDG(4); }
	int CVUniverse::GetSecProtonCandidatePDG_5() const { return GetProtonCandidatePDG(5); }
	int CVUniverse::GetSecProtonCandidatePDG_6() const { return GetProtonCandidatePDG(6); }
	
	int CVUniverse::GetPrimaryProtonCandidatePDG_abs() const { return abs(GetProtonCandidatePDG(0)); }
	int CVUniverse::GetSecProtonCandidatePDG_abs_1() const { return abs(GetProtonCandidatePDG(1)); }
	int CVUniverse::GetSecProtonCandidatePDG_abs_2() const { return abs(GetProtonCandidatePDG(2)); }
	int CVUniverse::GetSecProtonCandidatePDG_abs_3() const { return abs(GetProtonCandidatePDG(3)); }
	int CVUniverse::GetSecProtonCandidatePDG_abs_4() const { return abs(GetProtonCandidatePDG(4)); }
	int CVUniverse::GetSecProtonCandidatePDG_abs_5() const { return abs(GetProtonCandidatePDG(5)); }
	int CVUniverse::GetSecProtonCandidatePDG_abs_6() const { return abs(GetProtonCandidatePDG(6)); }
	
	
	double CVUniverse::GetVisEnergyDiffTruedEdx() const {
		return GetPrimaryProtonTrueKE() - GetTotalPrimaryProtonVisEnergy();
	}
	
	int CVUniverse::GetRecoTruthIsPrimaryProton() const {
		if (GetInt("proton_prong_PDG") == 2212) return 1;
		else return 0; 
	}
	int CVUniverse::GetRecoTruthIsPrimaryPion() const {
		int pdg = GetInt("proton_prong_PDG");
		if (pdg == 211 || pdg == -211) return 1;
		else return 0; 
	}
	int CVUniverse::GetRecoTruthIsPrimaryOther() const {
		int pdg = GetInt("proton_prong_PDG");
		if (pdg == 2212 || pdg == 211 || pdg == -211) return 0;
		else return 1; 
	}
	
	int CVUniverse::GetTruthHasSingleProton() const { return GetInt("truth_reco_has_single_proton"); }

	int CVUniverse::GetAllExtraTracksProtons() const {
		if(GetMultiplicity() < 2) return 1; // NA when multiplicity is < 2
		int n_sec_proton_scores = GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores_sz").c_str());
		if(n_sec_proton_scores == 0) return 1; // NA if not secondary proton candidates

		// define and get applicable variables
		double tree_Q2 = GetQ2QEGeV();
		std::vector<double> sec_proton_scores = GetVecDouble(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores").c_str());

		int passes = GetPassAllProtonScoreCuts(sec_proton_scores,tree_Q2,n_sec_proton_scores);
		return passes;
	}	
	int CVUniverse::GetAllExtraTracksProtons1() const {
		if(GetMultiplicity() < 2) return 1; // NA when multiplicity is < 2
		int n_sec_proton_scores1 = GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1_sz").c_str());
		if(n_sec_proton_scores1 == 0) return 1; // NA if not secondary proton candidates

		// define and get applicable variables
		double tree_Q2 = GetQ2QEGeV();
		std::vector<double> sec_proton_scores1 = GetVecDouble(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1").c_str());

		int passes = GetPassAllProtonScoreCuts(sec_proton_scores1,tree_Q2,n_sec_proton_scores1);
		return passes;
	}
	
	int CVUniverse::GetProtonCount() const {
		if(GetMultiplicity() < 2) return 0;
		int count = 0;
		double tree_Q2 = GetQ2QEGeV();
		if( GetPassProtonScoreCut(0,0,tree_Q2) ) count++;
		int n_sec_proton_scores = GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores_sz").c_str());
		for ( int i=0; i<n_sec_proton_scores; i++ ) {
			if(GetPassProtonScoreCut(0,i+1,tree_Q2)) count++;
		}
		return count;
	}	
	int CVUniverse::GetProtonCount1() const {
		if(GetMultiplicity() < 2) return 0;
		int count = 0;
		double tree_Q2 = GetQ2QEGeV();
		if( GetPassProtonScoreCut(1,0,tree_Q2) ) count++;
		int n_sec_proton_scores1 = GetInt(std::string(MinervaUniverse::GetTreeName()+"_sec_protons_proton_scores1_sz").c_str());
		for ( int i=0; i<n_sec_proton_scores1; i++ ) {
			if(GetPassProtonScoreCut(1,i+1,tree_Q2)) count++;
		}
		return count;
	}

	int CVUniverse::GetTrueProtonCount() const {
		int genie_n_protons = 0;

		std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		std::vector<double> mc_FSPartE = GetVecDouble("mc_FSPartE");
		int mc_nFSPart = GetInt("mc_nFSPart");

		for(int i = 0; i < mc_nFSPart; i++){
			int pdg =  mc_FSPartPDG[i];
			double energy = mc_FSPartE[i];
			double KEp = energy - MinervaUnits::M_p;
			//if( pdg == 2212         && 
			//    KEp  > m_proton_ke_cut ) genie_n_protons++;
			if( pdg == 2212 ) genie_n_protons++;
		}

		return genie_n_protons;
	}

	// ----------------------------- Recoil Variables ----------------------------

	double CVUniverse::ApplyCaloTuning(double calRecoilE) const {
    		// for antineutrino do nothing;
    		if (m_analysis_neutrino_pdg == -14) {
        		//return AntiNu_tracker.eCorrection(calRecoilE * MeVGeV) / MeVGeV;
        		return calRecoilE;
    		} // else
    		//return Nu_tracker.eCorrection(calRecoilE * MeVGeV) / MeVGeV;
        	return calRecoilE; // also do nothing here 
	}

	double CVUniverse::GetCalRecoilEnergy() const {
		bool neutrinoMode = GetAnalysisNuPDG() > 0;
		if(neutrinoMode) {
			if(MinervaUniverse::GetTreeName()=="MasterAnaDev") {
				return (GetDouble("nonvtx_iso_blobs_energy")+GetDouble("dispr_id_energy")); // several definitions of this, be careful
			}
			else {
				return (GetDouble("nonvtx_iso_blobs_energy")+GetDouble("dis_id_energy"));
			}
		}
		else {
			//if(GetVecDouble("recoil_summed_energy").size()==0) return -999.; // protect against bad input,
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
	int CVUniverse::GetIntType() const { 
		return GetInt(std::string(MinervaUniverse::GetTreeName()+"_intType").c_str()); 
	}
	int CVUniverse::GetMCIntType() const { return GetInt("mc_intType"); }
	//  0 - no interaction
	//  1 - quasi-elastic scattering
	//  2 - resonant scattering
	//  3 - deep inelastic scattering
	//  4 - coherent scattering
	//  5 - anomalous neutrino-photon interaction
	//  6 - inverse muon decay
	//  7 - neutrino-electron elastic scattering
	//  8 - 2P2H
	//  9 - N/A
	// 10 - unknown interaction
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
			else if( energy > m_photon_energy_cut &&
			         pdg     ==   22   ) return 0; // Photons > Energy Cut
			else if( abs_pdg == 3112 ||            // Sigma- and Sigma~+      Strange Baryons
				     	 abs_pdg == 3122 ||            // Lambda0 and Lambda~0    Strange Baryons
				     	 abs_pdg == 3212 ||            // Sigma0 and Sigma~0      Strange Baryons
				     	 abs_pdg == 3222   ) return 0; // Sigma+ and Sigma~-      Strange Baryons
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
		if( ( neutrinoMode && genie_n_muons     == 0) ||
		    (!neutrinoMode && genie_n_antimuons == 0)   ) return 0;
		else return 1;
	}
	
	bool CVUniverse::GetTruthIsCCQELike_new() const {
		if (!_are_signal_truths_set) {
			if      (GetFSConstrainedParticleCount(  211) > 0) return 0; // Pion +
			else if (GetFSConstrainedParticleCount(  111) > 0) return 0; // Pion 0
			else if (GetFSConstrainedParticleCount( -211) > 0) return 0; // Pion -
			else if (GetFSConstrainedParticleCount(   22) > 0) return 0; // Gamma > 10 MeV
			else if (GetFSConstrainedParticleCount(  321) > 0) return 0; // Kaon +
			else if (GetFSConstrainedParticleCount( 3122) > 0) return 0; // Lambda 0
			else if (GetFSConstrainedParticleCount(  311) > 0) return 0; // Kaon 0
			else if (GetFSConstrainedParticleCount( 3222) > 0) return 0; // Sigma +
			else if (GetFSConstrainedParticleCount( -321) > 0) return 0; // Kaon -
			else if (GetFSConstrainedParticleCount( -311) > 0) return 0; // Kaon-bar 0
			else if (GetFSConstrainedParticleCount(  130) > 0) return 0; // Kaon_L 0
			else if (GetFSConstrainedParticleCount(-2212) > 0) return 0; // Proton-bar
			else if (GetFSConstrainedParticleCount(-2112) > 0) return 0; // Neutron-bar
			else if (GetFSConstrainedParticleCount(-3122) > 0) return 0; // Lambda-bar 0
			else if (GetFSConstrainedParticleCount( 3212) > 0) return 0; // Sigma 0
			else if (m_analysis_neutrino_pdg == 14) {                      // Neutrino Mode
				if      (GetFSConstrainedParticleCount( 13) != 1) return 0;    // 1 Muon
				else if (GetFSConstrainedParticleCount(-13)  > 0) return 0;    // No Anti-Muons
				else return 1;
			}
			else if (m_analysis_neutrino_pdg == -14) {                     // Anti-Neutrino Mode
				if      (GetFSConstrainedParticleCount(  13)  > 0) return 0;    // No Muons
				else if (GetFSConstrainedParticleCount( -13) != 1) return 0;    // 1 Anti-Muon
				else if (GetFSConstrainedParticleCount(2212)  > 0) return 0;    // No Protons > Threshold
				else return 1;
			}
			else return 0; // m_analysis_neutrino_pdg not 14 or -14?
		}
		else return GetSignalTruth("qelike");
	}
	
	bool CVUniverse::GetTruthIs1ChargedPion_new() const {
		if (!_are_signal_truths_set) {
			if      (GetFSConstrainedParticleCount( 111)  > 0) return 0; // 1+ Pion 0
			else if (GetFSConstrainedParticleCount( 211) + 
				       GetFSConstrainedParticleCount(-211) == 1) return 1; // 1 Pion +/-
			else return 0;
		}
		else return GetSignalTruth("1chargedpion");
	}
	bool CVUniverse::GetTruthIs1NeutralPion_new() const {
		if (!_are_signal_truths_set) {
			if      (GetFSConstrainedParticleCount( 211) +
				       GetFSConstrainedParticleCount(-211)  > 0) return 0; // 1+ Pion +/-
			else if (GetFSConstrainedParticleCount( 111) == 1) return 1; // 1 Pion 0
			else return 0;
		}
		else return GetSignalTruth("1neutralpion");
	}
	bool CVUniverse::GetTruthIsMultiPion_new() const {
		if (!_are_signal_truths_set) {
			if (GetFSConstrainedParticleCount( 211) +
				  GetFSConstrainedParticleCount(-211) +
				  GetFSConstrainedParticleCount( 111) > 1) return 1; // 2+ Pion +/-/0
			else return 0;
		}
		else return GetSignalTruth("multipion");
	}         

	double CVUniverse::GetMaxProtonTrueKE() const {
		
		int mc_nFSPart = GetInt("mc_nFSPart");
		std::vector<int>mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		std::vector<double>mc_FSPartE = GetVecDouble("mc_FSPartE");
		double KEmax = 0.0;
		for(int i = 0; i < mc_nFSPart; i++){
		  int pdg =  mc_FSPartPDG[i];
		  if (pdg     != 2212 ) continue;
		  double energy = mc_FSPartE[i];
		  double KEp = energy - MinervaUnits::M_p;
		  if (KEp > KEmax) KEmax = KEp;

		}
		return KEmax;
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
	
	bool CVUniverse::GetTruthIsCCQELike_old() const {  // cut hardwired for now
		if (!_are_signal_truths_set_old) {
			std::vector<int>mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
			std::vector<double>mc_FSPartE = GetVecDouble("mc_FSPartE");
			bool neutrinoMode = CVUniverse::GetTruthNuPDG() > 0;
			int mc_nFSPart = GetInt("mc_nFSPart");
			//int mc_incoming = GetInt("mc_incoming");
			//int mc_current = GetInt("mc_current");
			bool passes = ( CVUniverse::passTrueCCQELike(neutrinoMode, mc_FSPartPDG, mc_FSPartE, mc_nFSPart, m_proton_ke_cut));

			return passes;
		}
		else return GetSignalTruth_old("qelike");
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
	
	int CVUniverse::GetTruthIsQELike() const {
		if(CVUniverse::GetTruthIsCCQELikeAll() == 1 &&
		   CVUniverse::GetTruthNuPDG() == m_analysis_neutrino_pdg &&
		   CVUniverse::GetCurrent() == 1 ) return 1;
		else return 0;
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
	
	double CVUniverse::GetBlobDistance(int i) const {
		if( GetInt("nonvtx_iso_blobs_distance_in_prong_sz") > i ) {
			return GetVecElem("nonvtx_iso_blobs_distance_in_prong",i);
		}
		else {
			return -9999.;
		}
	}
	double CVUniverse::GetBlobDistance0() const { return CVUniverse::GetBlobDistance(0); }
	double CVUniverse::GetBlobDistance1() const { return CVUniverse::GetBlobDistance(1); }
	double CVUniverse::GetBlobDistance2() const { return CVUniverse::GetBlobDistance(2); }
	double CVUniverse::GetBlobDistance3() const { return CVUniverse::GetBlobDistance(3); }
	double CVUniverse::GetBlobDistance4() const { return CVUniverse::GetBlobDistance(4); }
	
	double CVUniverse::GetPionScore() const {
		return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_pion_score").c_str());
	}
	double CVUniverse::GetPionScore1() const {
		return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_pion_score1").c_str());
	}
	double CVUniverse::GetPionScore2() const {
		return GetDouble(std::string(MinervaUniverse::GetTreeName()+"_pion_score2").c_str());
	}

	// One charged pion and charged pion count and CCQE except 1+ charged pions
	
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
			if( genie_n_charged_pion >    1   ) return 0;
		}
		
		if( genie_n_charged_pion == 1 ) return 1;
		return 0; // i.e. if genie_n_charged_pion == 0
	}
	
	bool CVUniverse::GetTruthIs1ChargedPion_old() const {
		if (!_are_signal_truths_set_old) {
			int genie_n_charged_pion = 0;
			std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
			std::vector<double> mc_FSPartE = GetVecDouble("mc_FSPartE");
			int mc_nFSPart = GetInt("mc_nFSPart");

			for(int i = 0; i < mc_nFSPart; i++){
				int pdg =  mc_FSPartPDG[i];

				if(      pdg             ==  111   ) return 0; // Neutral pions
				else if( abs(pdg)        ==  211   ) genie_n_charged_pion++;
				// Intermediate check of charged pion count
				if( genie_n_charged_pion >    1   ) return 0;
			}
			
			if( genie_n_charged_pion == 1 ) return 1;
			return 0; // i.e. if genie_n_charged_pion == 0
		}
		else return GetSignalTruth_old("1chargedpion");
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
	
	int CVUniverse::GetTruthCCQELikeExceptForChargedPions() const {
		if( CVUniverse::GetTruthNuPDG() != m_analysis_neutrino_pdg ) return 0;
		if ( CVUniverse::GetCurrent() != 1 ) return 0;
		int genie_n_muons = 0;
		int genie_n_antimuons = 0;
		int genie_n_chargedpions = 0;
		double protonKECut = m_proton_ke_cut;
		bool neutrinoMode = 0;
		std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		std::vector<double> mc_FSPartE = GetVecDouble("mc_FSPartE");
		int mc_nFSPart = GetInt("mc_nFSPart");
		
		if( m_analysis_neutrino_pdg > 0 ) neutrinoMode = 1;
		
		for(int i = 0; i < mc_nFSPart; i++){
			int pdg =  mc_FSPartPDG[i];
			int abs_pdg = abs(pdg);
			double energy = mc_FSPartE[i];
			double KEp = energy - MinervaUnits::M_p;

			// implement 120 MeV KE cut, if needed
			// The photon energy cut is hard-coded at 10 MeV at present. We're happy to make it general, if the need arises !
			
			if(      abs_pdg ==  211   ) genie_n_chargedpions++;
			else if( pdg     ==  111   ) return 0; // Neutral Pions            Neutral Pions
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
		if( ( neutrinoMode && genie_n_muons     == 0) ||
		    (!neutrinoMode && genie_n_antimuons == 0) ||
		    ( genie_n_chargedpions              == 0)   ) return 0;
		else return 1;
	}

	// Michel Electrons and Neutral Pions

	int CVUniverse::GetNMichel() const { return GetInt("has_michel_vertex_type_sz"); }
	std::vector<int> CVUniverse::GetMichelVertexType() const { return GetVecInt("has_michel_vertex_type"); }
	
	int CVUniverse::GetImprovedNMichel() const { return GetInt("improved_michel_match_vec_sz"); }
	std::vector<int> CVUniverse::GetImprovedMichelMatch() const { return GetVecInt("improved_michel_match_vec"); }
	
	int CVUniverse::GetFittedNMichel() const { return GetInt("FittedMichel_michel_fitPass_sz"); }
	std::vector<int> CVUniverse::GetFittedMichelFitPass() const { return GetVecInt("FittedMichel_michel_fitPass"); }
	
	int CVUniverse::GetTrueFittedNMichel() const {
		int ntruefittedmichels = 0;
		int nfittedmichels = GetFittedNMichel();
		for (int i =0; i< nfittedmichels; i++) {
			double datafrac = GetVecElem("FittedMichel_michel_datafraction", i);
			int fitted = GetVecElem("FittedMichel_michel_fitPass", i);
			if(fitted == 0) continue;
			if(datafrac > 0.5) continue;
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
	
	int CVUniverse::GetImprovedMichel_0_Views() const {
		if(GetInt("improved_michel_view_vec_sz") >= 1) {
			std::vector<int> views_vec = GetVecInt("improved_michel_view_vec");
			return int(views_vec[0]/10);
		}
		else return 0;
	}
	int CVUniverse::GetImprovedMichel_1_Views() const {
		if(GetInt("improved_michel_view_vec_sz") >= 2) {
			std::vector<int> views_vec = GetVecInt("improved_michel_view_vec");
			return int(views_vec[1]/10);
		}
		else return 0;
	}
	int CVUniverse::GetImprovedMichel_2_Views() const {
		if(GetInt("improved_michel_view_vec_sz") >= 3) {
			std::vector<int> views_vec = GetVecInt("improved_michel_view_vec");
			return int(views_vec[2]/10);
		}
		else return 0;
	}
	int CVUniverse::GetImprovedMichel_Sum_Views() const {
		int michels = GetInt("improved_michel_view_vec_sz");
		std::vector<int> views_vec = GetVecInt("improved_michel_view_vec");
		int count = 0;
		for(int i = 0; i < michels; i++) {
			count += int(views_vec[i]/10);
		}
		return count;
	}
	double CVUniverse::GetImprovedMichel_Avg_Views() const {
		int michels = GetInt("improved_michel_view_vec_sz");
		std::vector<int> views_vec = GetVecInt("improved_michel_view_vec");
		int count = 0;
		for(int i = 0; i < michels; i++) {
			count += int(views_vec[i]/10);
		}
		if(michels == 0) {
			return 0.;
		}
		else {
			return double(count)/double(michels);
		}
	}
	
	int CVUniverse::GetMaxImprovedMichelViews() const {
		int michels = GetInt("improved_michel_view_vec_sz");
		if(michels == 0) {
			return 0.;
		}
		else {
			std::vector<int> views_vec = GetVecInt("improved_michel_view_vec");
			int views = int(views_vec[0]/10);
			for(int i = 1; i < michels; i++){
				if( int(views_vec[i]/10) > views ) {
					views = int(views_vec[i]/10);
				}
			}
			return views;
		}
	}

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
	
	bool CVUniverse::GetTruthIs1NeutralPion_old() const {
		if (!_are_signal_truths_set_old) {
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
		else return GetSignalTruth_old("1neutralpion");
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
	
	int CVUniverse::GetTrueNeutronCount() const {
		int genie_n_neutrons = 0;

		std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		int mc_nFSPart = GetInt("mc_nFSPart");

		for(int i = 0; i < mc_nFSPart; i++){
			int pdg =  mc_FSPartPDG[i];
			if( pdg == 2112 ) genie_n_neutrons++;
		}

		return genie_n_neutrons;
	}
	
	int CVUniverse::GetTrueNegMuonCount() const {
		int genie_n_negmuons = 0;

		std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		int mc_nFSPart = GetInt("mc_nFSPart");

		for(int i = 0; i < mc_nFSPart; i++){
			int pdg =  mc_FSPartPDG[i];
			if( pdg == 13 ) genie_n_negmuons++;
		}

		return genie_n_negmuons;
	}
	
	int CVUniverse::GetTrueGammaCount() const {
		int genie_n_gammas = 0;

		std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		int mc_nFSPart = GetInt("mc_nFSPart");

		for(int i = 0; i < mc_nFSPart; i++){
			int pdg =  mc_FSPartPDG[i];
			if( pdg == 22 ) genie_n_gammas++;
		}

		return genie_n_gammas;
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
	
	bool CVUniverse::GetTruthIsMultiPion_old() const {
		if (!_are_signal_truths_set_old) {
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
		else return GetSignalTruth_old("multipion");
	}
	
	bool CVUniverse::GetTruthIsOther_old() const {
		if (GetTruthIsMultiPion_old()    ||
		    GetTruthIs1ChargedPion_old() ||
		    GetTruthIs1NeutralPion_old() ||
		    GetTruthIsCCQELike()           ) {
			return 0;
		}
		else { return 1; }
	}
	
	int CVUniverse::GetTruthIsOther() const {
		if (GetTruthHasSingleChargedPion() ||
		    GetTruthHasSingleNeutralPion() ||
		    GetTruthHasMultiPion()         ||
		    GetTruthIsCCQELike()           ) {
			return 0;
		}
		else { return 1; }
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
	
	int CVUniverse::GetHasMichelOrNBlobs() const {
		if( GetInt("improved_michel_match_vec_sz") > 0 ||
		    CVUniverse::GetNBlobs() > 1 ) return 1;
		else return 0;
	}

	// Other particles
	
	int CVUniverse::GetTrueNumberOfFSParticles() const {
		return GetInt("mc_nFSPart");
	}

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
	
	std::map<int,int> CVUniverse::GetTrueFSCountsPerPDG() const {
		std::map<int,int> true_counts_per_pdg;
		std::vector<int> mc_FSPartPDG = GetVecInt("mc_FSPartPDG");
		int mc_nFSPart = GetInt("mc_nFSPart");
		for(int i = 0; i < mc_nFSPart; i++){
			if (true_counts_per_pdg.count(mc_FSPartPDG[i])) true_counts_per_pdg[i]++;
			else true_counts_per_pdg[mc_FSPartPDG[i]] = 1;
		}
		
		std::vector<int> common_pdgs = {211,-211,111,2212,2112,13,22};
		for(auto pdg:common_pdgs){
			if(!true_counts_per_pdg.count(pdg)) true_counts_per_pdg[pdg] = 0;
		}
		
		return true_counts_per_pdg;
	}

	int CVUniverse::GetMCTargetA() const { return GetInt("mc_targetA"); }
	int CVUniverse::GetMCTargetZ() const { return GetInt("mc_targetZ"); }
	int CVUniverse::GetMCTargetNucleon() const { return GetInt("mc_targetNucleon"); }

	int CVUniverse::Dummy() const { return 0; }
	
	// TMVA
	
	/*bool CVUniverse::CalculateTMVAVectorResponse() const {
		std::vector<float> response_vec;
		
		float multiplicity = GetMultiplicity();
		float proton_score1_0 = GetPrimaryProtonScore1();
		float proton_score1_1 = GetProtonScore1_1();
		float proton_score1_2 = GetProtonScore1_2();
		float proton_track_vtx_gap_0 = GetPrimaryProtonTrackVtxGap();
		float proton_track_vtx_gap_1 = GetSecProtonTrackVtxGap_1();
		float proton_track_vtx_gap_2 = GetSecProtonTrackVtxGap_2();
		float proton_T_from_dEdX_0 = GetPrimaryProtonTfromdEdx();
		float proton_T_from_dEdX_1 = GetSecProtonTfromdEdx_1();
		float proton_T_from_dEdX_2 = GetSecProtonTfromdEdx_2();
		float proton_clusters_0 = GetNumClustsPrimaryProtonEnd();
		float proton_ratio_T_to_length_0 = ProtonRatioTdEdX2TrackLength_0();
		float proton_ratio_T_to_length_1 = ProtonRatioTdEdX2TrackLength_1();
		float proton_ratio_T_to_length_2 = ProtonRatioTdEdX2TrackLength_2();
		float proton_clusters_1 = GetNumClustsSecProtonEnd_1();
		float proton_clusters_2 = GetNumClustsSecProtonEnd_2();
		float proton_fraction_vis_energy_in_cone_0 = GetPrimaryProtonFractionVisEnergyInCone();
		float proton_fraction_vis_energy_in_cone_1 = GetSecProtonFractionVisEnergyInCone_1();
		float proton_fraction_vis_energy_in_cone_2 = GetSecProtonFractionVisEnergyInCone_2();
		float sec_proton_cand_count = GetSecondaryProtonCandidateCount1();
		float muon_to_primary_proton_angle = GetMuonToPrimaryProtonAngle();
		float blob_count = GetNBlobs();
		float improved_michel_count = GetImprovedNMichel();
		float recoil = GetRecoilEnergyGeV();
		float improved_michel_1_views = GetImprovedMichel_0_Views();
		float improved_michel_2_views = GetImprovedMichel_1_Views();
		float improved_michel_3_views = GetImprovedMichel_2_Views();
		float improved_michel_sum_views = GetImprovedMichel_Sum_Views();

		std::vector<float> input_vars;
		input_vars.emplace_back(multiplicity);
		
		if (proton_score1_0 >= 0) {
			if (sec_proton_cand_count == 0) {
				
				input_vars.emplace_back(proton_score1_0);
				input_vars.emplace_back(proton_track_vtx_gap_0);
				input_vars.emplace_back(proton_ratio_T_to_length_0);
				input_vars.emplace_back(proton_clusters_0);
				input_vars.emplace_back(proton_fraction_vis_energy_in_cone_0);
				input_vars.emplace_back(blob_count);
				input_vars.emplace_back(improved_michel_count);
				input_vars.emplace_back(recoil);
				input_vars.emplace_back(improved_michel_sum_views);
				
				std::vector<float> input_vars_2track;
				response_vec = m_tmva_2track_model.Compute(input_vars_2track);
			}
			else {				
				input_vars.emplace_back(proton_score1_0);
				input_vars.emplace_back(proton_score1_1);
				input_vars.emplace_back(proton_track_vtx_gap_0);
				input_vars.emplace_back(proton_track_vtx_gap_1);
				input_vars.emplace_back(proton_ratio_T_to_length_0);
				input_vars.emplace_back(proton_ratio_T_to_length_1);
				input_vars.emplace_back(proton_clusters_0);
				input_vars.emplace_back(proton_clusters_1);
				input_vars.emplace_back(proton_fraction_vis_energy_in_cone_0);
				input_vars.emplace_back(proton_fraction_vis_energy_in_cone_1);
				input_vars.emplace_back(sec_proton_cand_count);
				input_vars.emplace_back(blob_count);
				input_vars.emplace_back(improved_michel_count);
				input_vars.emplace_back(recoil);
				input_vars.emplace_back(improved_michel_sum_views);
				if (input_vars.size() == m_tmva_3ptrack_model.GetVariableNames().size()) {
					response_vec = m_tmva_3ptrack_model.Compute(input_vars);
				}
				else {
					response_vec = {0,0,0,0,0};
					std::cout << "WARNING: INPUT VECTOR SIZE DOES NOT MATCH 3+ TRACK MODEL EXPECTATION" << std::endl;
				}
			}
		}
		else {
			input_vars.emplace_back(blob_count);
			input_vars.emplace_back(improved_michel_count);
			input_vars.emplace_back(recoil);
			input_vars.emplace_back(improved_michel_sum_views);
			if (input_vars.size() == m_tmva_1track_model.GetVariableNames().size()) {
				response_vec = m_tmva_1track_model.Compute(input_vars);
			}
			else {
				response_vec = {0,0,0,0,0};
				std::cout << "WARNING: INPUT VECTOR SIZE DOES NOT MATCH 1 TRACK MODEL EXPECTATION" << std::endl;
			}
		}

		SetVectorResponse(response_vec);
		return 1;
	}*/
	double CVUniverse::bdtgQELike() const {
		if (_is_response_vec_filled) {
			return m_response_map["qelike"];
		}
		else {
			std::cout << "WARNING: RESPONSE VECTOR NOT FILLED." << std::endl;
			return -9999.;
		}
	}
	double CVUniverse::bdtg1ChargedPion() const {
		if (_is_response_vec_filled) {
			return m_response_map["1chargedpion"];
		}
		else {
			std::cout << "WARNING: RESPONSE VECTOR NOT FILLED." << std::endl;
			return -9999.;
		}
	}
	double CVUniverse::bdtg1NeutralPion() const {
		if (_is_response_vec_filled) {
			return m_response_map["1neutralpion"];
		}
		else {
			std::cout << "WARNING: RESPONSE VECTOR NOT FILLED." << std::endl;
			return -9999.;
		}
	}
	double CVUniverse::bdtgMultiPion() const {
		if (_is_response_vec_filled) {
			return m_response_map["multipion"];
		}
		else {
			std::cout << "WARNING: RESPONSE VECTOR NOT FILLED." << std::endl;
			return -9999.;
		}
	}
	double CVUniverse::bdtgOther() const {
		if (_is_response_vec_filled) {
			return m_response_map["other"];
		}
		else {
			std::cout << "WARNING: RESPONSE VECTOR NOT FILLED." << std::endl;
			return -9999.;
		}
	}
	
	// xgboost
	
	double CVUniverse::xgboostQELike() const {
		if (_is_response_vec_filled) {
			double response = m_xgboost_response_vec[4];
			return response;
		}
		else {
			std::cout << "WARNING: RESPONSE VECTOR NOT FILLED." << std::endl;
			return 0.;
		}
	}
	double CVUniverse::xgboost1ChargedPion() const {
		if (_is_response_vec_filled) {
			double response = m_xgboost_response_vec[3];
			return response;
		}
		else {
			std::cout << "WARNING: RESPONSE VECTOR NOT FILLED." << std::endl;
			return 0.;
		}
	}
	double CVUniverse::xgboost1NeutralPion() const {
		if (_is_response_vec_filled) {
			double response = m_xgboost_response_vec[2];
			return response;
		}
		else {
			std::cout << "WARNING: RESPONSE VECTOR NOT FILLED." << std::endl;
			return 0.;
		}
	}
	double CVUniverse::xgboostMultiPion() const {
		if (_is_response_vec_filled) {
			double response = m_xgboost_response_vec[1];
			return response;
		}
		else {
			std::cout << "WARNING: RESPONSE VECTOR NOT FILLED." << std::endl;
			return 0.;
		}
	}
	double CVUniverse::xgboostOther() const {
		if (_is_response_vec_filled) {
			double response = m_xgboost_response_vec[0];
			return response;
		}
		else {
			std::cout << "WARNING: RESPONSE VECTOR NOT FILLED." << std::endl;
			return 0.;
		}
	}
	
	// Arachne
	
	void CVUniverse::PrintTrueArachneLink() const {
		int link_size = 200;
		char link[link_size];
		int run = GetInt("mc_run");
		int subrun = GetInt("mc_subrun");
		int gate = GetInt("mc_nthEvtInFile") + 1;
		int slice = GetVecElem("slice_numbers", 0);
		sprintf(link,
			      "https://minerva05.fnal.gov/Arachne/"
			      "arachne.html\?det=SIM_minerva&recoVer=v21r1p1&run=%d&subrun=%d&gate="
			      "%d&slice=%d", run, subrun, gate, slice);
		std::cout << link << std::endl;
		/*std::cout << "Lepton E: " <<  GetElepTrueGeV() << " Run " << run << "/"<<subrun << "/" << gate << "/" << slice << std::endl;
		std::cout << "Printing Available Energy " << NewEavail() << std::endl;
		std::cout << "Muon P: " << GetMuonP() << std::endl;
		std::cout << "Get Muon Pt: " << GetMuonPT() << std::endl;
		std::cout << "Get Muon Pz: " << GetMuonPz() << std::endl;
		std::cout << "Get Muon PT True " << GetMuonPTTrue() << std::endl;*/
		
	}
	
	std::string CVUniverse::StringTrueArachneLink() const {
		int link_size = 200;
		char link[link_size];
		int run = GetInt("mc_run");
		int subrun = GetInt("mc_subrun");
		int gate = GetInt("mc_nthEvtInFile") + 1;
		int slice = GetVecElem("slice_numbers", 0);
		sprintf(link,
			      "https://minerva05.fnal.gov/Arachne/"
			      "arachne.html\?det=SIM_minerva&recoVer=v21r1p1&run=%d&subrun=%d&gate="
			      "%d&slice=%d", run, subrun, gate, slice);
		return link;
		
	}

	void CVUniverse::PrintDataArachneLink() const {
		int link_size = 200;
		char link[link_size];
		int run = GetInt("ev_run");
		int subrun = GetInt("ev_subrun");
		int gate = GetInt("ev_gate");
		int slice = GetVecElem("slice_numbers", 0);
		sprintf(link,
			      "https://minerva05.fnal.gov/Arachne/"
			      "arachne.html\?det=MV&recoVer=v21r1p1&run=%d&subrun=%d&gate="
			      "%d&slice=%d", run, subrun, gate, slice);
		std::cout << link << std::endl;
		// std::cout << "Lepton E: " <<  GetMuonPT() << " Run " << run << "/"<<subrun << "/" << gate << "/" << slice << std::endl;
	}
	
	std::string CVUniverse::StringDataArachneLink() const {
		int link_size = 200;
		char link[link_size];
		int run = GetInt("ev_run");
		int subrun = GetInt("ev_subrun");
		int gate = GetInt("ev_gate");
		int slice = GetVecElem("slice_numbers", 0);
		sprintf(link,
			      "https://minerva05.fnal.gov/Arachne/"
			      "arachne.html\?det=MV&recoVer=v21r1p1&run=%d&subrun=%d&gate="
			      "%d&slice=%d", run, subrun, gate, slice);
		return link;
	}
	

	void CVUniverse::Print() const { 
		std::cout
		<< ShortName() << ", "
		<< GetRun() << ", "
		<< GetSubRun() << ", "
		<< GetGate() << ", "
		<< GetTruthNuPDG() << ","
		<< GetTruthIsCC() << ","
		<< GetTruthIsCCQELike() << ", "
		<< GetIsMinosMatchTrack() << ", "
		<< std::endl;
	}

#endif
