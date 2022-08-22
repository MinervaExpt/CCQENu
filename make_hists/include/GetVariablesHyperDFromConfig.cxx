d#include "utils/NuConfig.h"
#include "GetVariablesHyperDFromConfig.h"
#include "VariableFromConfig.h"
#include "VariableHyperDFromConfig.h"
#include "CVUniverse.h"
#include <cassert>

std::vector<std::string> intersection(std::vector<std::string> &v1, std::vector<std::string> &v2){
    std::vector<std::string> v3;
    std::sort(v1.begin(), v1.end());
    std::sort(v2.begin(), v2.end());
    std::set_intersection(v1.begin(),v1.end(),v2.begin(),v2.end(),back_inserter(v3));
    return v3;
}

std::map<std::string, CCQENu::VariableHyperDFromConfig*> GetHyperDVariablesFromConfig( std::vector<std::string> varsHyperD, std::map< std::string, CCQENu::VariableFromConfig* > variablesmap, const std::vector<std::string> tags, const NuConfig configraw) {
  //=========================================
  // Constructor wants: name,
  //                    x VariableFromConfig, y VariableFromConfig
  //
  // variablesmap is the output of from GetMapOfVariables
  // config is the whole config file since I need to loop over a vector of HyperD
  // variables to analyze, which I need to pull from the config file
  // Might change what the constructor wants to just take in both that vector
  // and then the config.GetValue("AnalyzeHyperDVariables")
  //=========================================
  bool isHyperD = false;
  std::map<std::string, CCQENu::VariableHyperDFromConfig*> variablesHyperDmap; // this is the HyperD set that actually gets returned

  configraw.Print();
  NuConfig config;
  if(configraw.IsMember("HyperD")){
    config = configraw.GetValue("HyperD");
  } else{
    std::cout << "No HyperD variables configured." << std::endl;
    exit(1);
  }
  NuConfig config1D;
  if(configraw.IsMember("1D")){
    config1D = configraw.GetValue("1D");
  } else{
    std::cout << "No 1D variables configured." << std::endl;
  }

  std::vector<std::string>  keys = config.GetKeys();
  for (auto key:keys){ // this is in the Variables json file so you can define them all
    bool found = false;
    NuConfig varconfig;
    for ( auto v:varsHyperD){ // this is from the master driver file so you can skip some
      if ( v == key){
        found = true;
        bool foundx = false;
        bool foundy = false;
        varconfig = config.GetValue(v);
        std::string nameHyperD = varconfig.GetString("name");
        std::string xvarname = varconfig.GetString("xvar");
        std::string yvarname = varconfig.GetString("yvar");

        NuConfig xvarconfig = config1D.GetValue(xvarname);
        std::vector<std::string> xfor = {};
        if(xvarconfig.IsMember("for")){
          xfor = xvarconfig.GetStringVector("for");
        }
        NuConfig yvarconfig = config1D.GetValue(yvarname);
        std::vector<std::string> yfor = {};
        if(yvarconfig.IsMember("for")){
          yfor = yvarconfig.GetStringVector("for");
        }
        std::vector<std::string> fors = {};
        if(xfor.size()==0){fors = yfor;}
        else if(yfor.size()==0){fors = xfor;}
        else if(xfor.size()>0 && yfor.size()>0){fors = intersection(xfor, yfor);}

        CCQENu::VariableFromConfig* xvar;
        CCQENu::VariableFromConfig* yvar;
        // CCQENu::VariableHyperDFromConfig* varHyperDfromconfig;

        for( auto var:variablesmap ){
          std::string varname = var.first;
          if( xvarname == varname ){
            xvar = variablesmap[xvarname];
            foundx = true;
          }
          if( yvarname == varname ){
            yvar = variablesmap[yvarname];
            foundy = true;
          }
        }
        if ( foundx && foundy ){
          // varHyperDfromconfig = new CCQENu::VariableHyperDFromConfig(nameHyperD,*xvar,*yvar,varconfig);
          // varHyperDfromconfig = new CCQENu::VariableHyperDFromConfig(nameHyperD,*xvar,*yvar,fors);
          CCQENu::VariableHyperDFromConfig* varHyperDfromconfig = new CCQENu::VariableHyperDFromConfig(nameHyperD,*xvar,*yvar,fors);
          varHyperDfromconfig->AddTags(tags);
          std::cout << "GetVariablesHyperDFromConfig: set up HyperD variable " << nameHyperD << std::endl;
          variablesHyperDmap[nameHyperD] = varHyperDfromconfig;
        }
        else if( !foundx ) {
          std::cout << " Warning - have requested an unimplemented 1D variable in GetHyperDVariablesFromConfig " << xvarname << std::endl;
            assert(0);
        }
        else if( !foundy ){
          std::cout << " Warning - have requested an unimplemented 1D variable in GetHyperDVariablesFromConfig " << xvarname << std::endl;
            assert(0);
        }
      }
    }
    if(!found){
      std::cout << "GetHyperDVariablesFromConfig: HyperD variable " << key << " configured but not requested in main config" << std::endl;

    }
  }

// check that all requested variables are defined.
  for (auto v:varsHyperD){
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

  return variablesHyperDmap;
}
