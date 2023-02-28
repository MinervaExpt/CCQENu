#ifndef GET2DVariablesFromConfig_H
#define GET2DVariablesFromConfig_H
#include <vector>
#include "CVUniverse.h"
#include "PlotUtils/PhysicsVariables.h"

namespace CCQENu
{
  class VariableFromConfig;
  class Variable2DFromConfig;
}
std::vector<std::string> intersection(std::vector<std::string> &v1, std::vector<std::string> &v2); // tool used to find "for" for x and y
// std::map<std::string, CCQENu::Variable2DWithMap*> GetMapOfVariables2D( std::map<std::string,CCQENu::VariableWithMap*> variablesmap, const std::vector<std::string> tags, const NuConfig & configfile); //"old way" 3/16/21
std::map<std::string, CCQENu::Variable2DFromConfig*> Get2DVariablesFromConfig( std::vector<std::string> vars2D, std::map<std::string,CCQENu::VariableFromConfig*> variablesmap, const std::vector<std::string> tags, NuConfig );
std::vector<CCQENu::Variable2DFromConfig*> Get2DVariablesFromConfig( std::vector<std::string> vars2D, std::vector<CCQENu::VariableFromConfig*> variablesvec, const std::vector<std::string> tags, NuConfig );

#endif
