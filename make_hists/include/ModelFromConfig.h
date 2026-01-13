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
#include "weighters/FluxAndCVReweighter.h"
#include "weighters/GENIEReweighter.h"
#include "weighters/LowQ2PiReweighter.h"
#include "weighters/LowRecoil2p2hReweighter.h"
#include "weighters/MINOSEfficiencyReweighter.h"
#include "weighters/RPAReweighter.h"

namespace CCQENu {
typedef std::vector<PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>*> TuneVec;
typedef std::map<std::string, PlotUtils::Reweighter<CVUniverse, PlotUtils::detail::empty>*> TuneMap;

class ModelFromConfig {
    TuneVec MnvTuneVec;
    TuneMap MnvTuneMap; 

   public:
    ModelFromConfig(const NuConfig config) {
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
            MnvTuneVec.emplace_back(new PlotUtils::RPAReweighter<CVUniverse, PlotUtils::detail::empty>());
        }
        if (config.IsMember("GENIE")) {
            bool useNonResPi = config.GetConfig("GENIE").GetBool("useNonResPi");                    // set to true for almost everything
            bool useDeuteriumPionTune = config.GetConfig("GENIE").GetBool("useDeuteriumPionTune");  // set to true for v4 only
            
            std::cout << "ModelFromConfig: set up GENIE Reweighter";
            if (useNonResPi) std::cout << " with NonResPi turned ON";
            if (useDeuteriumPionTune) std::cout << " with DeuteriumPionTune turned ON";
            std::cout << std::endl;

            MnvTuneVec.emplace_back(new PlotUtils::GENIEReweighter<CVUniverse, PlotUtils::detail::empty>(useNonResPi, useDeuteriumPionTune));
        }
        if (config.IsMember("LowRecoil2p2h")) {
            std::string variation = config.GetString("LowRecoil2p2h");
            std::cout << "ModelFromConfig: set up LowRecoil2p2h Reweighter ";

            if (variation == "CV") {
                // Default value 0, used in all tunes
                std::cout << "with default CV variation" << std::endl;
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

        // Low Q2 pion stuff for v2 and v4
        if (config.IsMember("LowQ2Pi")) {
            // "JOINT for v2, "MENU1PI" for v4
            std::string fittype = config.GetString("LowQ2Pi");
            std::cout << "ModelFromConfig: set up LowQ2Pi Reweighter with fittype " << fittype << std::endl;

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
    };

    TuneVec GetModelTunesFromConfig() const {
        // std::cout << ">>>>>>>>>> MnvTuneVec vec size is \t" << MnvTuneVec.size() << std::endl;
        return MnvTuneVec;
    };
};
}  // namespace CCQENu

#endif  // MODELFROMCONFIG_H