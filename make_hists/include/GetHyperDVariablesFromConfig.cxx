#include "utils/NuConfig.h"
#include "GetHyperDVariablesFromConfig.h"
#include "VariableFromConfig.h"
#include "VariableHyperDFromConfig.h"
#include "CVUniverse.h"
#include <cassert>

std::map<std::string, CCQENu::VariableHyperDFromConfig*> GetHyperDVariablesFromConfig( std::vector<std::string> varsHD, std::map< std::string, CCQENu::VariableFromConfig* > variablesmap, const std::vector<std::string> tags, const NuConfig configraw) {
  //=========================================
  // Constructor wants: name,
  //                    vector 1D VariableFromConfig's,
  //                    fors
  //
  // variablesmap is the output of from GetMapOfVariables
  // config is the whole config file since I need to loop over a vector of HyperDimensional
  // variables to analyze, which I need to pull from the config file
  // Might change what the constructor wants to just take in both that vector
  // and then the config.GetValue("AnalyzeHyperDVariables")
  //=========================================
  // bool isHD = false; // TODO: necessary?
  std::map<std::string, CCQENu::VariableHyperDFromConfig*> variablesHDmap; // this is the HyperD set that actually gets returned

  //configraw.Print();
  NuConfig config;
  if(configraw.IsMember("HyperD")){
    config = configraw.GetValue("HyperD");
  } else{
    std::cout << "GetHyperDVariablesFromConfig: Warning: No HyperD variables configured." << std::endl;
    exit(1);
  }
  NuConfig config1D;
  if(configraw.IsMember("1D")){
    config1D = configraw.GetValue("1D");
  } else{
    std::cout << "GetHyperDVariablesFromConfig: Warning: No 1D variables configured." << std::endl;
  }

  std::vector<std::string>  keys = config.GetKeys();
  for (auto key:keys){ // keys here is the list labelled "HyperD" in the Variables json file so you can define them all
    bool found = false;
    NuConfig varconfig;
    for ( auto v:varsHD){ // varsHD is the list from the master driver file so you can skip some
      if ( v == key){
        found = true; // Used later to make sure you actually configured the variable

        // Get the config for the hyperD variable and pull out various info about it
        varconfig = config.GetValue(v);
        std::string nameHD = varconfig.GetString("name");
        std::vector<std::string> axisvarnamevec = varconfig.GetStringVec("vars");
        std::vector<std::string> fors = {}
        if(varconfig.IsMember("for")){fors = varconfig.GetString("for");}
        int d = axisvarnamevec.size(); // The dimension of the hyperD variable is number of axes it has

        // Make a bool vector to use to check that you have a variable for each axis
        std::vector<bool> foundvec; 
        for(int i = 0; i < d ; i++){ foundvec.push_back(false)}

        // Initialize vectors for each axis containing their configs, their "fors", and their VariableFromConfigs
        std::vector<NuConfig> axisvarconfigvec;
        std::vector<std::vector<std::string>> axisforsvec;
        std::vector<CCQENu::VariableFromConfig *> axisvars;

        // Loop over each axis
        for (auto axis : axisvarnamevec){
          NuConfig axisvarconfig = config1D.GetValue(axis);
          // Store the config
          axisvarconfigvec.push_back(axisvarconfig);
          // Initialize a vector to put the fors for this axis
          std::vector<std::string> axisfor = {};
          if(axisvarconfig.IsMember("for")){ axisfor = axisvarconfig.GetString("for");}
          axisforsvec.push_back(axisfor);
          // TODO: figure out the intersection of "fors" of all axes? For now just configuring it like a 1D variable to have its own set of "fors"

          // Find each variable in input map and store the ones you need to build the HyperD variable
          for (int i = 0; i < variablesmap.size(); i++){
            std::string varname = variablesmap[i].first;
            if (axis == varname){
              axisvars.push_back(variablesmap[i].second);
              foundvec[i] = true; 
            }
          }
        }

        // Double check everything got found. May not be necessary.
        for(int i = 0; i < d; i++){
          if (foundvec[i]==false){
            std::cout << " GetHyperDVariablesFromConfig: Warning - have requested an unimplimented 1D variable." assert(0);
          }
        }
        // Initialize new hyper d variable
        CCQENu::VariableHyperDFromConfig* varHDfromconfig = new CCQENu::VariableHyperDFromConfig(nameHD, axisvars, fors);
        varHDfromconfig->AddTags(tags);

        std::cout "GetHyperDVariablesFromConfig: set up HyperDim variable " << nameHD << " of dimension " << d << std::endl;
        // Add it to the map
        variablesHDmap[nameHD] = varHDfromconfig;
      }
    }
    if(!found){
      std::cout << "GetHyperDVariablesFromConfig: 2D variable " << key << " configured but not requested in main config" << std::endl;
        
    }
  }
    
// check that all requested variables are defined.
  for (auto v:varsHD){
      bool found = false;
      for (auto key:keys){
          if (v == key){
              found = true;
              break;
          }
        }
      if (!found){
        std::cout << "GetHyperDVariablesFromConfig: Warning - have requested an unimplemented variable in GetHyperDVariablesFromConfig " << v << std::endl;
          assert(0);
      }
    }

  return variablesHDmap;
}
