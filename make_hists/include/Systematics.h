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
#include "PlotUtils/GenericVerticalSystematic.h"
#include "PlotUtils/GenieSystematics.h"
#include "PlotUtils/MinosEfficiencySystematics.h"
#include "PlotUtils/MnvTuneSystematics.h"
#include "PlotUtils/MuonResolutionSystematics.h"
#include "PlotUtils/MuonSystematics.h"
// #include "PlotUtils/NeutronInelasticReweighter.h"
#include "PlotUtils/ResponseSystematics.h"
#include "utils/NuConfig.h"

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

    // CV
    error_bands[std::string("cv")].push_back(new CVUniverse(chain));

    // HMS 4-20-2024 - make systematics version configurable
    std::string responseSystematicsVersion = "CCQENu";
    if (config.IsMember("responseSystematicsVersion")) {
        responseSystematicsVersion = config.GetString("responseSystematicsVersion");
    }
    // #ifndef NOFLUX
    if (std::find(flags.begin(), flags.end(), "Flux") != flags.end()) {
        //========================================================================
        // FLUX
        //========================================================================
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
        std::cout << " do standard GENIE systematcs " << std::endl;
        UniverseMap bands_genie = PlotUtils::GetStandardGenieSystematicsMap<CVUniverse>(chain);
        error_bands.insert(bands_genie.begin(), bands_genie.end());
    } else {
        std::cout << "Warning:  GENIE systematics are turned off" << std::endl;
    }

    if (std::find(flags.begin(), flags.end(), "GenieRvx1pi") != flags.end()) {
        std::cout << " do GenieRvx1pi systematics " << std::endl;
        // Pion final state normalization
        UniverseMap bands_pi_fs_norm = PlotUtils::GetGenieRvx1piSystematicsMap<CVUniverse>(chain);
        error_bands.insert(bands_pi_fs_norm.begin(), bands_pi_fs_norm.end());
    } else {
        std::cout << "Warning:  GenieRvx1pi systematics are turned off" << std::endl;
    }

    //========================================================================
    // MnvTunes
    //========================================================================
    // RPA

    if (std::find(flags.begin(), flags.end(), "RPA") != flags.end()) {
        std::cout << " do RPA systematics " << std::endl;
        UniverseMap bands_rpa = PlotUtils::GetRPASystematicsMap<CVUniverse>(chain);
        error_bands.insert(bands_rpa.begin(), bands_rpa.end());
    } else {
        std::cout << "Warning:  RPA systematics are turned off" << std::endl;
    }

    if (std::find(flags.begin(), flags.end(), "2p2h") != flags.end()) {
        // 2P2H
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

    if (std::find(flags.begin(), flags.end(), "MuonMINOS") != flags.end()) {
        std::cout << " do muon MINOS energy systematics" << std::endl;

        UniverseMap bands_muon_minos =
            PlotUtils::GetMinosMuonSystematicsMap<CVUniverse>(chain);
        error_bands.insert(bands_muon_minos.begin(), bands_muon_minos.end());
    } else {
        std::cout << "Warning:  MuonMINOS systematics are turned off" << std::endl;
    }

    if (std::find(flags.begin(), flags.end(), "MuonResolution") != flags.end()) {
        std::cout << " do muon resolution systematics" << std::endl;

        // Muon resolution
        UniverseMap muonR_systematics = PlotUtils::GetMuonResolutionSystematicsMap<CVUniverse>(chain, NSFDefaults::muonResolution_Err);
        error_bands.insert(muonR_systematics.begin(), muonR_systematics.end());
    } else {
        std::cout << "Warning:  MuonResolution systematics are turned off" << std::endl;
    }

    if (std::find(flags.begin(), flags.end(), "MINOSEfficiency") != flags.end()) {
        std::cout << " do MINOS efficiency systematics" << std::endl;

        // MINOS EFFICIENCY
        UniverseMap bands_minoseff = PlotUtils::GetMinosEfficiencySystematicsMap<CVUniverse>(chain);
        error_bands.insert(bands_minoseff.begin(), bands_minoseff.end());
    } else {
        std::cout << "Warning:  MINOSEffiency systematics are turned off" << std::endl;
    }

    if (std::find(flags.begin(), flags.end(), "Angle") != flags.end()) {
        // Angle
        std::cout << " do make angle systematics" << std::endl;

        UniverseMap angle_systematics = PlotUtils::GetAngleSystematicsMap<CVUniverse>(chain, NSFDefaults::beamThetaX_Err, NSFDefaults::beamThetaY_Err);
        error_bands.insert(angle_systematics.begin(), angle_systematics.end());
    } else {
        std::cout << "Warning:  Angle systematics are turned off" << std::endl;
    }

    // GeantHadronUniverse constructor
    // GeantHadronUniverse<T>::GeantHadronUniverse( typename T::config_t chw, double nsigma, int pdg )
    if (std::find(flags.begin(), flags.end(), "geant4") != flags.end()) {
        UniverseMap geant4_systematics = PlotUtils::GetGeantHadronSystematicsMap<CVUniverse>(chain);
        error_bands.insert(geant4_systematics.begin(), geant4_systematics.end());
        std::cout << " do make geant4 systematics" << std::endl;
    } else {
        std::cout << "Warning:  geant4 systematics are turned off" << std::endl;
    }

    // Response systematics (which also have recoil syst)
    // Stole this from Andrew's code
    if (std::find(flags.begin(), flags.end(), "response") != flags.end()) {
        bool use_ID = false;
        bool use_OD = false;
        std::string name_tag = "allNonMuonClusters";
        bool neutron = false;
        bool part_response = false;
        bool proton = false;
        bool use_nucl = false;
        bool use_tracker = true;
        bool use_ecal = false;
        bool use_hcal = false;

        UniverseMap response_systematics;
        std::cout << " using version " << responseSystematicsVersion << " of response systematics" << std::endl;
        if (responseSystematicsVersion == "CCQENu") {
            response_systematics = PlotUtils::GetResponseSystematicsMap<CVUniverse>(chain, neutron, part_response, proton);  // Not totally sure what the args do here
        } else {
            if (responseSystematicsVersion == "2024") {
                response_systematics = PlotUtils::GetResponseSystematicsMap<CVUniverse>(chain, use_ID, use_OD, name_tag, neutron, part_response, proton, use_nucl, use_tracker, use_ecal, use_hcal);  // Not totally sure what the args do here
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

    // // MoNA reweight systematic universe
    // if (std::find(flags.begin(), flags.end(), "MoNANeutronInelastic") != flags.end()) {
    //     std::map<std::string, std::vector<int>> MonaMapDefault = {{"nGamma", {1000060120, 2112}},
    //                                                               {"threeAlpha", {1000020040, 100002040, 100002040, 2112}},
    //                                                               {"Bnp", {1000050110, 2112, 2212}}};

    //     UniverseMap mona_systematics;
    //     // mona_systematics["NeutronInelasticsReweight"].push_back(new PlotUtils::GenericVerticalUniverse<CVUniverse, PlotUtils::detail::empty>(chain, std::unique_ptr<PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>>(new NeutronInelasticReweighter<CVUniverse>(MonaMapDefault)), 1.0));
    //     // mona_systematics["NeutronInelasticsReweight"].push_back(new PlotUtils::GenericVerticalUniverse<CVUniverse, PlotUtils::detail::empty>(chain, std::unique_ptr<PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>>(new NeutronInelasticReweighter<CVUniverse>(MonaMapDefault)), -1.0));
    //     mona_systematics["NeutronInelasticsReweight"].push_back(new PlotUtils::GenericVerticalUniverse<CVUniverse, PlotUtils::detail::empty>(chain, std::unique_ptr<PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>>(new NeutronInelasticReweighter<CVUniverse>(MonaMapDefault)), 1.0));
    //     mona_systematics["NeutronInelasticsReweight"].push_back(new PlotUtils::GenericVerticalUniverse<CVUniverse, PlotUtils::detail::empty>(chain, std::unique_ptr<PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>>(new NeutronInelasticReweighter<CVUniverse>(MonaMapDefault)), -1.0));
    //     error_bands.insert(mona_systematics.begin(), mona_systematics.end());
    //     std::cout << " do MoNA systematics " << std::endl;

    // } else {
    //     std::cout << "WARNING: MoNA systematic turned off" << std::endl;
    // }

    // at the end
    return error_bands;

    //  std::cout << "Warning: still need to implement response systematics " << std::endl;
}

}  // namespace systematics

#endif  // Systematics_h
