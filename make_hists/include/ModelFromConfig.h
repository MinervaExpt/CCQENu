#ifndef MODELFROMCONFIG_H
#define MODELFROMCONFIG_H

#include <string>
#include <vector>

#include "PlotUtils/MichelSystematics.h"
#include "PlotUtils/MnvTuneSystematics.h"
#include "PlotUtils/Model.h"
#include "PlotUtils/Reweighter.h"
#include "PlotUtils/TargetMassSystematics.h"
#include "PlotUtils/WeightFunctions.h"
#include "include/CVUniverse.h"
#include "include/Systematics.h"
#include "utils/CoherentPiReweighter.h"
#include "utils/DiffractiveReweighter.h"
#include "utils/NuConfig.h"
#include "weighters/BodekRitchieReweighter.h"
#include "weighters/FSIReweighter.h"
#include "weighters/FluxAndCVReweighter.h"
#include "weighters/GENIEReweighter.h"
#include "weighters/GeantNeutronCVReweighter.h"
#include "weighters/LowQ2PiReweighter.h"
#include "weighters/LowRecoil2p2hReweighter.h"
#include "weighters/MINOSEfficiencyReweighter.h"
#include "weighters/RPAReweighter.h"
#include "weighters/SuSAFromValencia2p2hReweighter.h"

namespace CCQENu {
typedef std::vector<PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>*> TuneVec;
typedef std::map<std::string, PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>*> TuneMap;

class ModelFromConfig {
   private:
    TuneVec MnvTuneVec;
    TuneMap MnvTuneMap; 
    std::string m_tunename = "";
    int m_tunex = 0;
    int m_tuney = 0;
    int m_tunez = 0;

   public:
    // systematics stuff
    bool m_do2p2hsyst = false;
    bool m_doRPAsyst = false;
    bool m_doLowQ2Pisyst = false;
    // bool m_dosyst = false;

    std::string m_LowQ2fittype;

    ModelFromConfig(const NuConfig config) {
        if (config.IsMember("name")) m_tunename = config.GetString("name");
        std::string tunever;
        if (m_tunename.find("MnvTunev") != std::string::npos)
            tunever = m_tunename.erase(0, 8);
        std::vector<std::string> tunelist;
        size_t pos = 0;
        std::string token;

        while ((pos = tunever.find(".")) != std::string::npos) {
            token = tunever.substr(0, pos);
            tunelist.push_back(token);
            tunever.erase(0, pos + 1);
        }

        tunelist.push_back(tunever);
        while (tunelist.size() != 3) {
            tunelist.push_back("0");
        }
        m_tunex = stoi(tunelist[0]);
        m_tuney = stoi(tunelist[1]);
        m_tunez = stoi(tunelist[2]);

        // This is used for everymodel. This should be applied to reco and truth (eff denominator)
        if (config.IsMember("GeantNeutronCV")) {
            std::cout << "ModelFromConfig: set up GeantNeutronCV Reweighter" << std::endl;
            MnvTuneVec.emplace_back(new PlotUtils::GeantNeutronCVReweighter<CVUniverse, PlotUtils::detail::empty>());
        } else {
            std::cout << "WARNING: ModelFromConfig did not set up GeantNeutronCV. You need this for most models..." << std::endl;
        }

        // Base tune stuff, included in v1, v2, and v4. v4 has some variation. Warps vary things too
        if (config.IsMember("FluxAndCV")) {
            std::cout << "ModelFromConfig: set up FluxAndCV Reweighter" << std::endl;
            MnvTuneVec.emplace_back(new PlotUtils::FluxAndCVReweighter<CVUniverse, PlotUtils::detail::empty>());
        }
        if (config.IsMember("MINOSEfficiency")) {
            std::cout << "ModelFromConfig: set up MINOSEfficiency Reweighter" << std::endl;
            MnvTuneVec.emplace_back(new PlotUtils::MINOSEfficiencyReweighter<CVUniverse, PlotUtils::detail::empty>());
        }
        if (config.IsMember("RPA")) {
            std::cout << "ModelFromConfig: set up RPA Reweighter" << std::endl;
            m_doRPAsyst = true;
            MnvTuneVec.emplace_back(new PlotUtils::RPAReweighter<CVUniverse, PlotUtils::detail::empty>());
        }
        if (config.IsMember("GENIE")) {
            bool useNonResPi = config.GetConfig("GENIE").GetBool("useNonResPi");                    // set to true for almost everything
            bool useDeuteriumPionTune = config.GetConfig("GENIE").GetBool("useDeuteriumPionTune");  // set to true for v4 only

            std::cout << "ModelFromConfig: set up GENIE Reweighter";
            useNonResPi ? std::cout << " with useNonResPi turned ON" : std::cout << " with useNonResPi turned OFF";
            useDeuteriumPionTune ? std::cout << " and useDeuteriumPionTune turned ON" : std::cout << " and useDeuteriumPionTune turned OFF";
            std::cout << std::endl;
            if (useDeuteriumPionTune) { PlotUtils::MinervaUniverse::SetDeuteriumGeniePiTune(true); }

            MnvTuneVec.emplace_back(new PlotUtils::GENIEReweighter<CVUniverse, PlotUtils::detail::empty>(useNonResPi, useDeuteriumPionTune));
        }
        if (config.IsMember("LowRecoil2p2h")) {
            std::string variation = config.GetString("LowRecoil2p2h");
            std::cout << "ModelFromConfig: set up LowRecoil2p2h Reweighter ";

            if (variation == "CV") {
                // Default value 0, used in all tunes
                std::cout << "with default CV variation" << std::endl;
                m_do2p2hsyst = true;
                MnvTuneVec.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, PlotUtils::detail::empty>());
            } else if (variation == "nnpp") {
                std::cout << "with nn + pp variation" << std::endl;
                MnvTuneVec.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, PlotUtils::detail::empty>(1));
            } else if (variation == "np") {
                std::cout << "with np variation" << std::endl;
                MnvTuneVec.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, PlotUtils::detail::empty>(2));
            } else if (variation == "qe1p1h") {
                std::cout << "with qe 1p1h" << std::endl;
                MnvTuneVec.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, PlotUtils::detail::empty>(3));
            } else if (variation == "wgt1") {
                std::cout << "with wgt 1" << std::endl;
                MnvTuneVec.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, PlotUtils::detail::empty>(4));
            }
        }

        // SuSA 2p2h, not compatible with LowRecoil2p2h (Valencia), part of v3?
        if (config.IsMember("SuSAFromValencia2p2h")){
            std::cout << "ModelFromConfig: set up SuSAFromValencia2p2h Reweighter" << std::endl;
            MnvTuneVec.emplace_back(new PlotUtils::SuSAFromValencia2p2hReweighter<CVUniverse, PlotUtils::detail::empty>());
        }

        // Bodek-Ritchie Enhancement to QE, part of v3
        if (config.IsMember("BodekRitchie")) {
            std::cout << "ModelFromConfig: set up BodekRitchie Reweighter" << std::endl;
            MnvTuneVec.emplace_back(new PlotUtils::BodekRitchieReweighter<CVUniverse, PlotUtils::detail::empty>(1));
        }
        // v3 also includes a 25MeV EAvail removal for pion events

        // Low Q2 pion stuff for v2 and vX.3
        if (config.IsMember("LowQ2Pi")) {
            // "JOINT for v2, "MENU1PI" for vX.3
            std::string fittype = config.GetString("LowQ2Pi");
            std::cout << "ModelFromConfig: set up LowQ2Pi Reweighter with fittype " << fittype << std::endl;
            m_doLowQ2Pisyst = true;
            m_LowQ2fittype = fittype;
            MnvTuneVec.emplace_back(new PlotUtils::LowQ2PiReweighter<CVUniverse, PlotUtils::detail::empty>(fittype));
        }

        // Diffractive stuff, for vX.2
        if (config.IsMember("CoherentPi")) {
            std::cout << "ModelFromConfig: set up CoherentPi Reweighter" << std::endl;
            MnvTuneVec.emplace_back(new CoherentPiReweighter<CVUniverse, PlotUtils::detail::empty>);
        }
        if (config.IsMember("Diffractive")) {
            std::cout << "ModelFromConfig: set up Diffractive Reweighter" << std::endl;
            MnvTuneVec.emplace_back(new DiffractiveReweighter<CVUniverse, PlotUtils::detail::empty>);
        }

        // FSI bug fix stuff, for vX.Y.1
        if (config.IsMember("FSI")) {        
            bool useElastic = config.GetConfig("FSI").GetBool("useElastic");
            bool useAbsorption = config.GetConfig("FSI").GetBool("useAbsorption");
            std::cout << "ModelFromConfig: set up FSI Reweighter";
            useElastic ? std::cout << " with useElastic turned ON" : std::cout << " with useElastic turned OFF";
            useAbsorption ? std::cout << " and useAbsorption turned ON" : std::cout << " and useAbsorption turned OFF";
            std::cout << std::endl;
            MnvTuneVec.emplace_back(new PlotUtils::FSIReweighter<CVUniverse, PlotUtils::detail::empty>(useElastic, useAbsorption));
        }
    };

    TuneVec GetModelTunesFromConfig() const {
        // std::cout << ">>>>>>>>>> MnvTuneVec vec size is \t" << MnvTuneVec.size() << std::endl;
        return MnvTuneVec;
    };
};
}  // namespace CCQENu

#endif  // MODELFROMCONFIG_H