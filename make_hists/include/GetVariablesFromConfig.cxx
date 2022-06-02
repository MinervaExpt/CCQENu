
#include "utils/NuConfig.h"
#include "GetVariablesFromConfig.h"
#include "VariableFromConfig.h"
#include "Variable2DFromConfig.h"
#include "CVUniverse.h"
#include <cassert>



//==============================================================================
// Define variables
// Hists are defined inside of the CCQENu::Variable class definition (Variable.h).
//==============================================================================
//std::vector<CCQENu::VariableFromConfig*> GetVariables(variables, tags) {
//  // variables allows you to code a lot of functions but only chose the ones with names you pick
//  // tags allows you to associate variables with groups of cuts or other selections
//  //=========================================
//  // Constructor wants: name, x-axis label,
//  //                    binning,
//  //                    CVUniverse reco and
//  //                    truth functions
//  //=========================================
//
//
//
//  example of an exclusive variable not used here...
//  // Pion kinetic energy
//  // An exclusive variable is one that corresponds to a track, cluster, michel,
//  // etc.
//  // It is one that accepts a track-identifer integer index.
//  //  std::vector<double> tpi_bins = {35., 68., 100., 133., 166., 200., 350.};
//  //  typedef ExclusiveVariable1Arg<CVUniverse, CCQENu::Variable> EVar1;
//  //  EVar1* tpi = new EVar1("tpi", "T#pi (MeV)", tpi_bins, &CVUniverse::GetTpi,
//  //                         &CVUniverse::GetTpi);
//


// version with tags you can use

typedef std::function<double(const CVUniverse&)> PointerToCVUniverseFunction;

std::map<std::string, CCQENu::VariableFromConfig*> GetVariablesFromConfig(const std::vector<std::string> vars, const std::vector<std::string> tags, NuConfig configraw) {
  //=========================================
  // Constructor wants: name, x-axis label,
  //                    binning,
  //                    CVUniverse reco and
  //                    truth functions
  //=========================================
  std::map<std::string,  CCQENu::VariableFromConfig*> allvariables;  // set this internally to span the set of variables
  std::map<std::string, CCQENu::VariableFromConfig*> variablesmap; // this is the set that actually gets returned



//  if (configfilename != "" ){
//    // NuConfig config;
//    // config.Read(configfilename);
//    NuConfig configraw;
//    configraw.Read(configfilename);
    NuConfig config;
    if(configraw.IsMember("1D")){
      config = configraw.GetValue("1D");
    } else config = configraw;
    std::vector<std::string>  keys = config.GetKeys();

    for (auto key:keys){ // this is in the Variables json file so you can define them all
      bool found = false;
      for ( auto v:vars){ // this is from the master driver file so you can skip some
        if ( v == key){
          found = true;
          allvariables[key] = new CCQENu::VariableFromConfig( config.GetValue(key));
          std::cout << "GetVariables: set up variable " << allvariables[key]->GetName() << std::endl;
        }
      }
      if(!found){
        std::cout << "GetVariables: variable " << key << " configured but not requested" << std::endl;
      }
    }
  


  // ok - have made all of the possible variables, but now let's choose based on the top level config.

  std::map<std::string,bool> amIused;

  for (auto variable:allvariables){
    amIused[variable.first]=false;
  }

  for (auto var:vars){
    bool found = false;
    for (auto variable:allvariables){
      //std::cout << var << " check " << variable.first<< std::endl;
      if(var == variable.first){
        std::cout << "GetVariables: study 1D variable " << var << std::endl;
        // this is the point where you add the tags.  Saves space this way.
        variable.second->AddTags(tags); //
        variablesmap[var] = variable.second;
        found = true;
        amIused[variable.first] = true;
        break;
      }
    }
    if (!found){
      std::cout << "GetVariablesFromConfig: Warning - have requested an unimplemented variable in GetVariablesFromConfig " << var << std::endl;
        assert(0);
    }
  }
  // clean up unused variables
  for (auto variable:allvariables){
    if (amIused[variable.first]) continue;
    std::cout << "GetVariables: remove unused variable " << variable.first << std::endl;
  }
  return variablesmap;
}

