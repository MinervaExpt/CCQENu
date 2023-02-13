#ifndef GET2DVariablesFromConfig_H
#define GET2DVariablesFromConfig_H
#include <vector>
#include "CVUniverse.h"
#include "PlotUtils/PhysicsVariables.h"

namespace CCQENu
{
  class VariableFromConfig;
  class VariableHyperDFromConfig;
}
// std::map<std::string, CCQENu::Variable2DWithMap*> GetMapOfVariables2D( std::map<std::string,CCQENu::VariableWithMap*> variablesmap, const std::vector<std::string> tags, const NuConfig & configfile); //"old way" 3/16/21
std::map<std::string, CCQENu::VariableHyperDFromConfig*> GetHyperDVariablesFromConfig( std::vector<std::string> varsHD, std::map<std::string,CCQENu::VariableFromConfig*> variablesmap, const std::vector<std::string> tags, NuConfig );

#endif
