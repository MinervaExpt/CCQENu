/**
* @file
* @author  Heidi Schellman/Noah Vaughan/SeanGilligan
* @version 1.0 *
* @section LICENSE *
* This program is free software; you can redistribute it and/or
* modify it under the terms of the GNU General Public License as
* published by the Free Software Foundation; either version 2 of
* the License, or (at your option) any later version. *
* @section DESCRIPTION *
* Code to fill histograms
 */
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
