#ifndef GETVariablesHyperDFromConfig_H
#define GETVariablesHyperDFromConfig_H
#include <vector>
#include "CVUniverse.h"
#include "PlotUtils/PhysicsVariables.h"

namespace CCQENu
{
  class VariableFromConfig;
  class VariableHyperDFromConfig;
}
std::vector<std::string> intersection(std::vector<std::string> &v1, std::vector<std::string> &v2); // tool used to find "for" for x and y
// std::map<std::string, CCQENu::VariableHyperDWithMap*> GetMapOfVariablesHyperD( std::map<std::string,CCQENu::VariableWithMap*> variablesmap, const std::vector<std::string> tags, const NuConfig & configfile); //"old way" 3/16/21
std::map<std::string, CCQENu::VariableHyperDFromConfig*> GetHyperDVariablesFromConfig( std::vector<std::string> varsHyperD, std::map<std::string,CCQENu::VariableFromConfig*> variablesmap, const std::vector<std::string> tags, NuConfig );

#endif
