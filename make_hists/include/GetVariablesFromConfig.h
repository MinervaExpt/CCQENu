#ifndef GetVariablesFromConfig_H
#define GetVariablesFromConfig_H
#include <vector>
#include "CVUniverse.h"
#include "VariableFromConfig.h"
#include "PlotUtils/PhysicsVariables.h"

//namespace CCQENu
//{
//  class VariableFromConfig;
//}

std::map<std::string, CCQENu::VariableFromConfig*> GetVariablesFromConfig(const std::vector<std::string> variables, const std::vector<std::string> tags, NuConfig , const bool doresolution=false);


#endif
