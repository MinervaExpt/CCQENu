#ifndef Systematics_h
#define Systematics_h

// #define NOGENIE
// #define NOFLUX
//==============================================================================
//  systematics namespace
//  * GetStandardSystematics function which get ALL of the generally applicable
//    PU systematics
//==============================================================================
#include <map>
#include <string>
#include <vector>

#include "CVUniverse.h"
#include "PlotUtils/AngleSystematics.h"
#include "PlotUtils/ChainWrapper.h"
#include "PlotUtils/FluxSystematics.h"
#include "PlotUtils/GeantHadronSystematics.h"
// #include "PlotUtils/GenericVerticalSystematic.h"
#include "PlotUtils/GenieSystematics.h"
#include "PlotUtils/MinosEfficiencySystematics.h"
#include "PlotUtils/MnvTuneSystematics.h"
#include "PlotUtils/MuonResolutionSystematics.h"
#include "PlotUtils/MuonSystematics.h"
// #include "PlotUtils/NeutronInelasticReweighter.h"
#include "PlotUtils/ResponseSystematics.h"
#include "include/MonaSystematics.h"
#include "utils/NuConfig.h"
#include "include/ModelFromConfig.h"

namespace systematics {

typedef std::map<std::string, std::vector<CVUniverse*>> UniverseMap;

//============================================================================
// Get Standard PU MAT Systematics
//============================================================================
UniverseMap GetStandardSystematics(PlotUtils::ChainWrapper* chain, const NuConfig config, bool is_truth = false) {
    // return map
    UniverseMap error_bands;
    // unsigned int kNFluxUniverses = config.GetInt("fluxUniverses");
    //  get a list of systematics to turn on from systematics
    std::vector<std::string> flags = config.GetStringVector("systematics");

    NuConfig modeltune_config;
    std::string tunename = "MnvTunev1";
    if (config.IsMember("modeltuneFile")) {
        std::string modeltunefilename = config.GetString("modeltuneFile");
        modeltune_config.Read(modeltunefilename);
        if (modeltune_config.IsMember("name")) tunename = modeltune_config.GetString("name");
    }

    // CV
    error_bands[std::string("cv")].push_back(new CVUniverse(chain));

    // HMS 4-20-2024 - make systematics version configurable
    std::string responseSystematicsVersion = "CCQENu";
    if (config.IsMember("responseSystematicsVersion")) {
        responseSystematicsVersion = config.GetString("responseSystematicsVersion");
    }
    
    // #ifndef NOFLUX
    //========================================================================
    // FLUX
    //========================================================================

    if (std::find(flags.begin(), flags.end(), "Flux") != flags.end()) {
        std::cout << " do standard Flux systematics " << std::endl;
        int kNFluxUniverses = MinervaUniverse::GetNFluxUniverses();
        UniverseMap bands_flux = PlotUtils::GetFluxSystematicsMap<CVUniverse>(chain, kNFluxUniverses);
        error_bands.insert(bands_flux.begin(), bands_flux.end());
    } else {
        std::cout << "Warning:  Flux systematics are turned off" << std::endl;
    }
    // #endif

    // #ifndef NOGENIE
    //========================================================================
    //  GENIE
    //========================================================================
    //  Standard
    if (std::find(flags.begin(), flags.end(), "GENIE") != flags.end()) {
        // std::cout << " do standard GENIE systematcs " << std::endl;
        // UniverseMap bands_genie = PlotUtils::GetStandardGenieSystematicsMap<CVUniverse>(chain);
        std::cout << " do GENIE systematcs " << std::endl;
        UniverseMap bands_genie = PlotUtils::GetGenieSystematicsMap<CVUniverse>(chain);
        
        // if you're doing the elastic bug fix, need to get rid of one of these universes bc it breaks under the tune
        if (modeltune_config.IsMember("FSI")) {
            if (modeltune_config.GetConfig("FSI").GetBool("useElastic")) {
                std::cout << "\telastic FSI bug fix implemented, removing GENIE_FrElas_N band..." << std::endl;
                UniverseMap tmp_bands_genie;
                for (auto band : bands_genie) {
                    if ((band.first).find("FrElas_N")!=std::string::npos) {
                        std::cout << "found band " << band.first << " and removing..." << std::endl;
                        continue;
                    }
                    tmp_bands_genie[band.first] = band.second;
                }
                bands_genie = tmp_bands_genie;
            }
        }
        error_bands.insert(bands_genie.begin(), bands_genie.end());
    } else {
        std::cout << "Warning:  GENIE systematics are turned off" << std::endl;
    }

    // Part of the GetGenieSystematicsMap
    // if (std::find(flags.begin(), flags.end(), "GenieRvx1pi") != flags.end()) {
    //     std::cout << " do GenieRvx1pi systematics " << std::endl;
    //     // Pion final state normalization
    //     UniverseMap bands_pi_fs_norm = PlotUtils::GetGenieRvx1piSystematicsMap<CVUniverse>(chain);
    //     error_bands.insert(bands_pi_fs_norm.begin(), bands_pi_fs_norm.end());
    // } else {
    //     std::cout << "Warning:  GenieRvx1pi systematics are turned off" << std::endl;
    // }

    //========================================================================
    // MnvTunes
    //========================================================================

    // These are part of nearly all minerva tunes
    // RPA
    if (std::find(flags.begin(), flags.end(), "RPA") != flags.end()) {
        std::cout << " do RPA systematics " << std::endl;
        UniverseMap bands_rpa = PlotUtils::GetRPASystematicsMap<CVUniverse>(chain);
        error_bands.insert(bands_rpa.begin(), bands_rpa.end());
    } else {
        std::cout << "Warning:  RPA systematics are turned off" << std::endl;
    }

    // 2P2H
    if (std::find(flags.begin(), flags.end(), "2p2h") != flags.end()) {
        std::cout << " do 2p2h systematics " << std::endl;
        UniverseMap bands_2p2h = PlotUtils::Get2p2hSystematicsMap<CVUniverse>(chain);
        error_bands.insert(bands_2p2h.begin(), bands_2p2h.end());
    } else {
        std::cout << "Warning:  2p2h systematics are turned off" << std::endl;
    }

    // Geant
    if (std::find(flags.begin(), flags.end(), "geant4") != flags.end()) {
        std::cout << " do geant4 systematics " << std::endl;
        UniverseMap bands_geant = PlotUtils::GetGeantHadronSystematicsMap<CVUniverse>(chain);
        error_bands.insert(bands_geant.begin(), bands_geant.end());
    } else {
        std::cout << "Warning:  geant4 systematics are turned off" << std::endl;
    }

    // This is for v2 and v4
    if (std::find(flags.begin(), flags.end(), "LowQ2Pi") != flags.end()) {
        if (modeltune_config.IsMember("LowQ2Pi")) {
            std::cout << " do LowQ2Pi tune systematics with channel " << modeltune_config.GetString("LowQ2Pi") << std::endl;
            UniverseMap bands_lowQ2pi = PlotUtils::GetLowQ2PiSystematicsMap<CVUniverse>(chain, modeltune_config.GetString("LowQ2Pi"));
            error_bands.insert(bands_lowQ2pi.begin(), bands_lowQ2pi.end());
        } else {
            std::cout << " Warning: lowq2pion systematics requested but not implemented for model " << tunename << std::endl;
        }
    } else {
        std::cout << "Warning:  lowq2pion systematics are turned off" << std::endl;
    }

    //========================================================================
    // Muons
    //========================================================================
    // MUON - MINERvA
    if (std::find(flags.begin(), flags.end(), "MuonMinerva") != flags.end()) {
        std::cout << " do muon MINERvA energy systematics" << std::endl;

        UniverseMap bands_muon_minerva = PlotUtils::GetMinervaMuonSystematicsMap<CVUniverse>(chain);
        error_bands.insert(bands_muon_minerva.begin(), bands_muon_minerva.end());

    } else {
        std::cout << "Warning:  MuonMinerva systematics are turned off" << std::endl;
    }

    // MUON - MINOS
    if (std::find(flags.begin(), flags.end(), "MuonMINOS") != flags.end()) {
        std::cout << " do muon MINOS energy systematics" << std::endl;

        UniverseMap bands_muon_minos =
            PlotUtils::GetMinosMuonSystematicsMap<CVUniverse>(chain);
        error_bands.insert(bands_muon_minos.begin(), bands_muon_minos.end());
    } else {
        std::cout << "Warning:  MuonMINOS systematics are turned off" << std::endl;
    }

    // Muon resolution
    if (std::find(flags.begin(), flags.end(), "MuonResolution") != flags.end()) {
        std::cout << " do muon resolution systematics" << std::endl;
        UniverseMap muonR_systematics = PlotUtils::GetMuonResolutionSystematicsMap<CVUniverse>(chain, NSFDefaults::muonResolution_Err);
        error_bands.insert(muonR_systematics.begin(), muonR_systematics.end());
    } else {
        std::cout << "Warning:  MuonResolution systematics are turned off" << std::endl;
    }

    // MINOS EFFICIENCY
    if (std::find(flags.begin(), flags.end(), "MINOSEfficiency") != flags.end()) {
        std::cout << " do MINOS efficiency systematics" << std::endl;
        UniverseMap bands_minoseff = PlotUtils::GetMinosEfficiencySystematicsMap<CVUniverse>(chain);
        error_bands.insert(bands_minoseff.begin(), bands_minoseff.end());
    } else {
        std::cout << "Warning:  MINOSEffiency systematics are turned off" << std::endl;
    }

    // Angle
    if (std::find(flags.begin(), flags.end(), "Angle") != flags.end()) {
        std::cout << " do make angle systematics" << std::endl;
        UniverseMap angle_systematics = PlotUtils::GetAngleSystematicsMap<CVUniverse>(chain, NSFDefaults::beamThetaX_Err, NSFDefaults::beamThetaY_Err);
        error_bands.insert(angle_systematics.begin(), angle_systematics.end());
    } else {
        std::cout << "Warning:  Angle systematics are turned off" << std::endl;
    }

    // Response systematics (which also have recoil syst)
    // Stole this from Andrew's code
    if (std::find(flags.begin(), flags.end(), "response") != flags.end()) {
        bool use_ID = false;
        bool use_OD = false;
        // std::string name_tag = CVUniverse::GetRecoilBranchName();
        std::string name_tag = "allNonMuonClusters";
        bool neutron = false;
        bool part_response = false;
        bool proton = false;
        bool use_nucl = false;
        bool use_tracker = true;
        bool use_ecal = false;
        bool use_hcal = false;
        bool use_p4 = true;

        UniverseMap response_systematics;
        std::cout << " using version " << responseSystematicsVersion << " of response systematics" << std::endl;
        if (responseSystematicsVersion == "CCQENu") {
            response_systematics = PlotUtils::GetResponseSystematicsMap<CVUniverse>(chain, neutron, part_response, proton);  // Not totally sure what the args do here
        } else {
            if (responseSystematicsVersion == "2024") {
                response_systematics = PlotUtils::GetResponseSystematicsMap<CVUniverse>(chain, use_ID, use_OD, name_tag, neutron, part_response, proton, use_nucl, use_tracker, use_ecal, use_hcal);  // Not totally sure what the args do here
                // response_systematics = PlotUtils::GetResponseSystematicsMap<CVUniverse>(chain, name_tag);  // Not totally sure what the args do here
            } else {
                std::cout << " unknown responseSystematicsVersion set; will not do response " << responseSystematicsVersion << std::endl;
                assert(0);
            }
        }
        error_bands.insert(response_systematics.begin(), response_systematics.end());
        std::cout << " do make response systematics " << std::endl;
    } else {
        std::cout << "Warning: response systematics are turned off" << std::endl;
    }

    // MoNA reweight systematic universe
    if (std::find(flags.begin(), flags.end(), "MoNANeutronInelastic") != flags.end()) {
        std::map<std::string, std::vector<int>> MonaMapDefault = {{"nGamma", {1000060120, 2112}},
                                                                  {"threeAlpha", {1000020040, 100002040, 100002040, 2112}},
                                                                  {"Bnp", {1000050110, 2112, 2212}}};

        UniverseMap mona_systematics;
        // // // mona_systematics["NeutronInelasticsReweight"].push_back(new PlotUtils::GenericVerticalUniverse<CVUniverse, PlotUtils::detail::empty>(chain, std::unique_ptr<PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>>(new NeutronInelasticReweighter<CVUniverse>(MonaMapDefault)), 1.0));
        // // // mona_systematics["NeutronInelasticsReweight"].push_back(new PlotUtils::GenericVerticalUniverse<CVUniverse, PlotUtils::detail::empty>(chain, std::unique_ptr<PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>>(new NeutronInelasticReweighter<CVUniverse>(MonaMapDefault)), -1.0));
        // // mona_systematics["NeutronInelasticsReweight"].push_back(new PlotUtils::GenericVerticalUniverse<CVUniverse, PlotUtils::detail::empty>(chain, std::unique_ptr<PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>>(new NeutronInelasticReweighter<CVUniverse>(MonaMapDefault)), 1.0));
        // // mona_systematics["NeutronInelasticsReweight"].push_back(new PlotUtils::GenericVerticalUniverse<CVUniverse, PlotUtils::detail::empty>(chain, std::unique_ptr<PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>>(new NeutronInelasticReweighter<CVUniverse>(MonaMapDefault)), -1.0));

        // // This mode sets up NeutronInealsticReweighter according to David's scheme, using 0 for Tracker, 1 for targets.
        // int mode = 0;
        // mona_systematics["NeutronInelasticsReweight"].push_back(new PlotUtils::GenericVerticalUniverse<CVUniverse, PlotUtils::detail::empty>(chain, std::unique_ptr<PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>>(new NeutronInelasticReweighter<CVUniverse>(MonaMapDefault, 1)), 1.0));
        // this uses the old version of the inelastic reweighter
        mona_systematics["NeutronInelasticsReweight"].push_back(new PlotUtils::GenericVerticalUniverse<CVUniverse, PlotUtils::detail::empty>(chain, std::unique_ptr<PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>>(new NeutronInelasticReweighter<CVUniverse>(MonaMapDefault)), 1.0));
        // UniverseMap mona_systematics = GetMonaSystematicMap(chain);
        error_bands.insert(mona_systematics.begin(), mona_systematics.end());
        // std::cout << " do MoNA systematics with mode " << std::to_string(mode) << std::endl;
        std::cout << " do MoNA systematics " << std::endl;

    } else {
        std::cout << "WARNING: MoNA systematic turned off" << std::endl;
    }

    // TODO: MENATE
    // if (std::find(flags.begin(), flags.end(), "MENATE") != flags.end()) {
    // }
    // at the end
    return error_bands;

    //  std::cout << "Warning: still need to implement response systematics " << std::endl;
}

}  // namespace systematics

#endif  // Systematics_h
