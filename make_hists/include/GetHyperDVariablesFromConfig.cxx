#include "utils/NuConfig.h"
#include "GetHyperDVariablesFromConfig.h"
#include "VariableFromConfig.h"
#include "VariableHyperDFromConfig.h"
#include "CVUniverse.h"
#include <cassert>

template <class CVUniverse> // TODO: This may be a hack that doesn't work. Need to tell a later VariableBase what template it is.
std::map<std::string, CCQENu::VariableHyperDFromConfig*> GetHyperDVariablesFromConfig(std::vector<std::string> varsHD, std::map<std::string, CCQENu::VariableFromConfig*> variablesmap, const std::vector<std::string> tags, const NuConfig configraw)
{
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
  // this is the HyperD set that actually gets returned
  std::map<std::string, CCQENu::VariableHyperDFromConfig*> variablesHDmap; 

  // configraw.Print();
  // Get the configs for *all* hyperD variables in your Variables config
  NuConfig config;
  if(configraw.IsMember("HyperD")){
    config = configraw.GetValue("HyperD");
  } else{
    std::cout << "GetHyperDVariablesFromConfig: Warning: No HyperD variables configured." << std::endl;
    exit(1);
  }
  // Get the configs for all 1D variables in your Variables config (these likely contain more info than hyperD that you need)
  NuConfig config1D;
  if(configraw.IsMember("1D")){
    config1D = configraw.GetValue("1D");
  } else{
    std::cout << "GetHyperDVariablesFromConfig: Warning: No 1D variables configured." << std::endl;
  }

  // Now loop over all the hyperD variables in your Variables config 
  std::vector<std::string>  keys = config.GetKeys();
  for (auto key:keys){ // keys here is the list labelled "HyperD" in the Variables json file so you can define them all
    
    bool found = false; // This is a bool to check that the variable you configured in your *Main* config are found
    NuConfig varconfig; // This is the config for one HyperD variable from your Variable config
    for ( auto v:varsHD){ // varsHD is the list from the Main config
      if ( v == key){ // Only work on the vars configured in Variable config that are selected in your Main config
        found = true; 

        // Get the config for the hyperD variable and pull out various info about it
        varconfig = config.GetValue(v);
        std::string nameHD = varconfig.GetString("name"); // should be format xvar_yvar_zvar_..._dvar, matching names of vars in 1D
        std::vector<std::string> axisvarnamevec = varconfig.GetStringVector("vars"); // Should each match names in 1D vars
        int dim = axisvarnamevec.size(); // The dimension of the hyperD variable is number of axes it has
        std::vector<std::string> fors = {}; // What you want to fill hists of (e.g. data, selected_reco), defaults to all<-TODO in VariableHyperDFromConfig
        if(varconfig.IsMember("for")){
          fors.push_back(varconfig.GetString("for"));}

        // Make a bool vector to use to check that you have the corresponding 1D variable configured for each axis
        std::map<int, bool> foundvec; 
        for(int i = 0; i < dim ; i++){
          foundvec[dim]=false;
        }

        // Initialize vectors containing  configs,"fors", and their VariableFromConfigs for each axis
        std::vector<NuConfig> axisvarconfigvec;
        std::vector<std::vector<std::string>> axisforsvec; //TODO
        // This is the vector that gets passed to VariableHyperDim constructor, which needs somethign that looks like a vector of VariableBase. 
        // Unique pointers hopefully let you put in a VariableFromConfig without getting a conversion error or data slicing
        std::vector<std::unique_ptr<PlotUtils::VariableBase<CVUniverse> > > axisvars;

        // Loop over each axis
        for (auto axisname : axisvarnamevec) {
          NuConfig axisvarconfig = config1D.GetValue(axisname);
          // Store the config
          axisvarconfigvec.push_back(axisvarconfig);
          // Initialize a vector to put the fors for this axis
          std::vector<std::string> axisfor = {};
          if(axisvarconfig.IsMember("for")){ axisfor.push_back(axisvarconfig.GetString("for"));}
          axisforsvec.push_back(axisfor);
          // TODO: figure out the intersection of "fors" of all axes? For now just configuring it like a 1D variable to have its own set of "fors"

          // Find each variable in input map and store the ones you need to build the HyperD variable
          int i = 0; //TODO: Find a better thing than this hack?
          for( auto var:variablesmap) {
            std::string varname = var.first;
            // Check that name of axis is a name of an input variable
            if(axisname == varname){
              // Put that input variable into vector to feed VarHyperD constructor, emplace_back (vs push_back) is used because its smarter idfk
              axisvars.emplace_back(variablesmap[varname]);
              foundvec[i]= true;
              i += 1;
            }
          }
        }
        // Double check every axis got found. May not be necessary.
        for(int i = 0; i < dim; i++){
          if (foundvec[i] == false) {
            std::cout << " GetHyperDVariablesFromConfig: Warning - have requested an unimplimented 1D variable." << std::endl;
            assert(0);
          }
        }
        // Initialize new hyper d variable and add the tags
        CCQENu::VariableHyperDFromConfig* varHDfromconfig = new CCQENu::VariableHyperDFromConfig(nameHD, axisvars, fors);
        varHDfromconfig->AddTags(tags);
        std::cout << "GetHyperDVariablesFromConfig: set up HyperDim variable " << nameHD << " of dimension " << dim << std::endl;
        // Add it to the map
        variablesHDmap[nameHD] = varHDfromconfig;
      }
    }
    // Check that your hyperD variable existed...
    if(!found){
      std::cout << "GetHyperDVariablesFromConfig: HyperD variable " << key << " configured but not requested in main config" << std::endl;
        
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
