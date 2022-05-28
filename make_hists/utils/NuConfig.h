#ifndef NUCONFIG_H
#define NUCONFIG_H
#include <string>
#include "json/json.h"
#include <fstream>
#include <iostream>
#include <cassert>
#include <vector>
#include <memory>

class NuConfig{

public:
  std::string f_filename;
  std::string f_buffer;
  Json::Value f_config;


public:

  NuConfig(){};
  // copy constructor
  NuConfig(const NuConfig& f){
    f_filename = "fromConfig";
    f_config = f.f_config;
  }

  bool Read(const std::string filename){
    f_filename  = filename;
    Json::CharReaderBuilder rbuilder;
    // Configure the Builder, then ...
    std::ifstream f_buffer(f_filename, std::ifstream::binary);
    std::string errs;
    bool parsingSuccessful = Json::parseFromStream(rbuilder, f_buffer, &f_config, &errs);
    if (!parsingSuccessful)
      {
      // report to the user the failure and their locations in the document.
      std::cout  << "Failed to parse configuration\n"
      << errs;
      return false;
      }

    std::cout << "read in configuration file " << f_filename << std::endl;
    return true;
  };
  
  bool ReadFromString(const std::string inputstring){
    JSONCPP_STRING err;
    //Json::CharReader reader;
    
//    f_filename  = filename;
//    Json::CharReaderBuilder rbuilder;
//    // Configure the Builder, then ...
//    std::ifstream f_buffer(f_filename, std::ifstream::binary);
//    std::string errs;
    //https://github.com/open-source-parsers/jsoncpp/blob/master/example/readFromString/readFromString.cpp  says to use this somewhat cumbersome method instead the old one
    Json::CharReaderBuilder builder;
    const std::unique_ptr<Json::CharReader> reader(builder.newCharReader());
        if (!reader->parse(inputstring.c_str(), inputstring.c_str()+ inputstring.length(), &f_config,
                           &err)) {
          std::cout << "error" << err << std::endl;
        
          return EXIT_FAILURE;
        }

    return true;
  };

  NuConfig(const Json::Value value){  // can read in a value from the file and then use that read in a subconfig
    f_config = value;
  };

  bool CheckMember(std::string key)const{

    // std::cout << " check Member" << f_config.type() << " " << f_config.isObject()  << " " <<  f_config.isMember(key) << std::endl;
    if (not f_config.isObject() || not  f_config.isMember(key)){
      std::cerr << "NuConfig: " << key << " is not a valid member of " << f_filename <<  " maybe you have a default? " << std::endl;
      return false;
    }
    return true;
  };

  // gentler version of CheckMember to use to see if you need to stick with a default.

  bool IsMember(std::string key)const{
    if (not f_config.isObject() || not  f_config.isMember(key)){
      return false;
    }
    return true;
  };

  void Print() const{
    std::cout << "config " <<  f_filename << " " << f_config << std::endl;
  };

  std::string ToString() const{
    return f_config.toStyledString();
  }

  double GetDouble(const std::string key)const{
    assert(CheckMember(key));
    return f_config.get(key,-9999.).asDouble();
  };
  int GetInt(const std::string key)const{
    assert(CheckMember(key));
    return f_config.get(key,-9999).asInt();
  };
  bool GetBool(const std::string key)const{
    assert(CheckMember(key));
    return f_config.get(key,false).asBool();
  };
  std::string GetString(const std::string key)const{
    assert(CheckMember(key));
    return f_config.get(key,"None").asString();
  };

  std::vector <std::string> GetStringVector(const std::string key)const{
    assert(CheckMember(key));
    std::vector<std::string>  a;
    Json::Value array = f_config.get(key,0);
    for (const auto &el  : array){
      if (el.isString()){
        a.push_back(el.asString());
      }
    }
    return a;
  };

  // can't compile on some machines.  Avoid vectors of const.

//  std::vector <const std::string> GetConstStringVector(const std::string key)const{
//    assert(CheckMember(key));
//    std::vector<const std::string>  a;
//    Json::Value array = f_config.get(key,0);
//    for (const auto &el  : array){
//      if (el.isString()){
//        a.push_back(el.asString());
//      }
//    }
//    return a;
//  };

  std::vector <double> GetDoubleVector(const std::string key)const{
    assert(CheckMember(key));
    std::vector<double>  a;
    Json::Value array = f_config.get(key,0);
    for (const auto &el  : array){
      if (el.isDouble()){
        a.push_back(el.asDouble());
      }
    }
    return a;
  };

  // get a vector of subconfigs

  std::vector<NuConfig> GetConfigVector(std::string key)const{
    assert(CheckMember(key));
    std::vector<NuConfig>  a;
    Json::Value array = f_config.get(key,0);
    for (const auto &el  : array){
        a.push_back(el);
    }
    return a;
  };
  

  // do this when you already have the vector of configs in hand
  std::vector<NuConfig> GetConfigVector()const{

    std::vector<NuConfig>  a;
    Json::Value array = f_config;
    for (const auto &el  : array){
        a.push_back(el);
    }
    return a;
  };

  Json::Value GetValue(const std::string key)const{
    assert(CheckMember(key));
    return f_config.get(key,0);
  };

  NuConfig GetConfig(const std::string key)const{
    assert(CheckMember(key));
    return NuConfig(f_config.get(key,0));
  };

  std::vector<std::string> GetKeys()const{

    // from https://github.com/open-source-parsers/jsoncpp/issues/288
    std::vector<std::string> result;
    for (Json::ValueConstIterator it = f_config.begin(); it != f_config.end(); ++it){
      result.push_back(it.name());
    }
    return result;
  };

  template <class var_t>
  var_t GetNumber(const std::string key){
    return typeid(var_t) == typeid(double)?GetDouble(key):GetInt(key);
  }

  NuConfig GetConfigVariable(std::string variable){
    NuConfig varsconfig;
    NuConfig config1D;
    NuConfig config2D;
    NuConfig outconfig;

    if(IsMember("varsFile")){
      std::string varsFile = f_config.get("varsFile","None").asString();
      varsconfig.Read(varsFile);
    } else{
      varsconfig = f_config;
    }

    // Get the variable config

    // Get 1D and 2D
    if(varsconfig.IsMember("1D")){
      config1D = varsconfig.GetValue("1D");
      if(config1D.IsMember(variable)){
        // NuConfig var1D;
        outconfig = config1D.GetValue(variable);
        // return var1D;
        std::cout << " NC: found 1D variable config for " << variable << std::endl; // print statement for debugging
      }
    }
    if(varsconfig.IsMember("2D")){
      config2D = varsconfig.GetValue("2D");
      if(config2D.IsMember(variable)){
        // NuConfig var2D;
        outconfig = config2D.GetValue(variable);
        // return var2D;
        std::cout << " NC: found 2D variable config for " << variable << std::endl; // print statement for debugging

      }
    } else {
      std::cout << " NuConfig: 1D or 2D variables not found" << std::endl; // print statement for debugging
      // assert(varsconfig.CheckMember(variable));
    }
    return outconfig;
  }

};

#endif
