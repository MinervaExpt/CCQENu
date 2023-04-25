#ifndef GETVariablesHyperDFromConfig_H
#define GETVariablesHyperDFromConfig_H
#include <vector>

#include "CVUniverse.h"
#include "PlotUtils/PhysicsVariables.h"

namespace CCQENu {
class VariableFromConfig;
class VariableHyperDFromConfig;
}  // namespace CCQENu
std::map<std::string, CCQENu::VariableHyperDFromConfig*> GetHyperDVariablesFromConfig(std::vector<std::string> varsHyperD, std::map<std::string, CCQENu::VariableFromConfig*> variablesmap, const std::vector<std::string> tags, NuConfig);

#endif
