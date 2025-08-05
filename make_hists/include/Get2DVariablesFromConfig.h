#ifndef GET2DVariablesFromConfig_H
#define GET2DVariablesFromConfig_H
#include <cassert>
#include <map>
#include <string>
#include <vector>

#include "CVUniverse.h"
#include "PlotUtils/PhysicsVariables.h"
#include "VariableFromConfig.h"
#include "Variable2DFromConfig.h"
#include "utils/NuConfig.h"

// namespace CCQENu {
// class VariableFromConfig;
// class Variable2DFromConfig;
// }  // namespace CCQENu
std::vector<std::string> intersection(std::vector<std::string> &v1, std::vector<std::string> &v2);  // tool used to find "for" for x and y
std::map<std::string, CCQENu::Variable2DFromConfig *> Get2DVariablesFromConfig(std::vector<std::string> vars2D, std::map<std::string, CCQENu::VariableFromConfig *> variablesmap, const std::vector<std::string> tags, const NuConfig configraw);
std::map<std::string, CCQENu::Variable2DFromConfig *> Get2DVariablesFromConfig(std::vector<std::string> vars2D, const std::vector<std::string> tags, const NuConfig configraw, const bool doresolution, const bool dotypes, const std::string tunedmc, const std::vector<std::string> fitsamples);
#endif
