#ifndef GETHyperDVariablesFromConfig_H
#define GETHyperDVariablesFromConfig_H
#include <vector>
#include "CVUniverse.h"
#include "PlotUtils/PhysicsVariables.h"
#include "PlotUtils/VariableBase.h"

namespace CCQENu
{
  class VariableFromConfig;
  class VariableHyperDFromConfig;
}
// template <class CVUniverse>
// std::map<std::string, CCQENu::Variable2DWithMap*> GetMapOfVariables2D( std::map<std::string,CCQENu::VariableWithMap*> variablesmap, const std::vector<std::string> tags, const NuConfig & configfile); //"old way" 3/16/21
// std::map<std::string, CCQENu::VariableHyperDFromConfig *> GetHyperDVariablesFromConfig(std::vector<std::string> varsHD, std::map<std::string, CCQENu::VariableFromConfig *> variablesmap, const std::vector<std::string> tags, NuConfig);
// std::map<std::string, CCQENu::VariableHyperDFromConfig *> GetHyperDVariablesFromConfig(std::vector<std::string> varsHD, std::map<std::string, PlotUtils::VariableBase<CVUniverse> *> variablesmap, const std::vector<std::string> tags, NuConfig);
std::vector<CCQENu::VariableHyperDFromConfig *> GetHyperDVariablesFromConfig(std::vector<std::string> varsHD, std::map<std::string, CCQENu::VariableFromConfig *> variablesmap, const std::vector<std::string> tags, NuConfig);

#endif
