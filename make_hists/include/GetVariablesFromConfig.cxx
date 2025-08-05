
#include "GetVariablesFromConfig.h"

#include <cassert>
#include <map>
#include <string>
#include <vector>

#include "CVUniverse.h"
#include "Variable2DFromConfig.h"
#include "VariableFromConfig.h"
#include "utils/NuConfig.h"

//==============================================================================
// Define variables
// Hists are defined inside of the CCQENu::Variable class definition (Variable.h).
//==============================================================================
// std::vector<CCQENu::VariableFromConfig*> GetVariables(variables, tags) {
//  // variables allows you to code a lot of functions but only chose the ones with names you pick
//  // tags allows you to associate variables with groups of cuts or other selections
//  //=========================================
//  // Constructor wants: name, x-axis label,
//  //                    binning,
//  //                    CVUniverse reco and
//  //                    truth functions
//  //=========================================
//
//
//
//  example of an exclusive variable not used here...
//  // Pion kinetic energy
//  // An exclusive variable is one that corresponds to a track, cluster, michel,
//  // etc.
//  // It is one that accepts a track-identifer integer index.
//  //  std::vector<double> tpi_bins = {35., 68., 100., 133., 166., 200., 350.};
//  //  typedef ExclusiveVariable1Arg<CVUniverse, CCQENu::Variable> EVar1;
//  //  EVar1* tpi = new EVar1("tpi", "T#pi (MeV)", tpi_bins, &CVUniverse::GetTpi,
//  //                         &CVUniverse::GetTpi);
//

// version with tags you can use

typedef std::function<double(const CVUniverse &)> PointerToCVUniverseFunction;

std::map<std::string, CCQENu::VariableFromConfig *> GetVariablesFromConfig(const std::vector<std::string> vars, const std::vector<std::string> tags, NuConfig configraw, const bool doresolution, const bool dotypes, const std::string tunedmc, const std::vector<std::string> fitsamples) {
    //=========================================
    // Constructor wants: name, x-axis label,
    //                    binning,
    //                    CVUniverse reco and
    //                    truth functions
    //=========================================
    std::map<std::string, CCQENu::VariableFromConfig *> variablesmap;  // this is the set that actually gets returned

    NuConfig config;
    if (configraw.IsMember("1D")) {
        config = configraw.GetValue("1D");
    } else
        config = configraw;

    for (auto v: vars) {
        if (config.IsMember(v)) {
            variablesmap[v] = new CCQENu::VariableFromConfig(config.GetValue(v));
            variablesmap[v]->SetDoResolution(doresolution);
            variablesmap[v]->SetDoTypes(dotypes);
            variablesmap[v]->SetTunedMC(tunedmc);
            variablesmap[v]->SetFitSamples(fitsamples);
            variablesmap[v]->AddTags(tags);
            std::cout << "    set up " << variablesmap[v]->GetName() << std::endl;
        } else {
            std::cout << "GetVariablesFromConfig: ERROR - have requested an unimplemented variable in GetVariablesFromConfig " << v << std::endl;
            assert(0);
        }
    }
    return variablesmap;
}