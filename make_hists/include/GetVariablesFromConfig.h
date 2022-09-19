#ifndef GetVariablesFromConfig_H
#define GetVariablesFromConfig_H
#include <vector>
#include "include/CVUniverse.h"
#include "include/VariableFromConfig.h"
#include "PlotUtils/PhysicsVariables.h"

//namespace CCQENu
//{
//  class VariableFromConfig;
//}

std::map<std::string, CCQENu::VariableFromConfig*> GetVariablesFromConfig(const std::vector<std::string> variables, const std::vector<std::string> tags, NuConfig );


#endif
