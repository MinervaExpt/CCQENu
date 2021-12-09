#ifndef SAMPLE_H
#define SAMPLE_H

#include "utils/NuConfig.h"
#include <vector>
#include <map>
#include <string>
#include <iostream>
#include "TText.h"

bool IsInVector(const std::string  what, const std::vector<std::string>  &vec)
{
  return std::find(vec.begin(),vec.end(),what)!=vec.end();
};

namespace CCQENu{
// helper function

//bool IsInVector(const std::string  what, const std::vector<const std::string>  &vec)
//{
//  return std::find(vec.begin(),vec.end(),what)!=vec.end();
//};



class Component{
private:
  std::string m_truth;
  std::string m_name;
  std::vector<std::string> m_for;
  std::string m_phase_space;
  bool m_is_signal;
  NuConfig m_config;
public:
  Component(){};
  // constructor;
  Component(const std::string samplename, const NuConfig config){
    m_name = samplename; // this is the name of the associated sample
    m_for = config.GetStringVector("for");
    m_is_signal = config.GetInt("signal");
    
    m_config = config;
  }
  
  // return list of data types this is for
  std::vector<std::string> GetFor()const {
    return m_for;
  }
  
  // return if key s is in for
  bool HasFor(const std::string s) const{
    return IsInVector(s,m_for);
  }
  // get various name back
  std::string GetName()const{return m_name;};
  std::string GetPhaseSpace()const{return m_phase_space;};
  bool IsSignal()const{return m_is_signal;}
};

class Sample{
private:
  std::string m_name;
  std::string m_reco;
  std::map<const std::string, Component> m_components;
  m_phase_space = config.GetString("phase_space");
public:
  Sample( const std::string key, const NuConfig config){
    m_name = key;
    m_reco = config.GetString("reco");
    NuConfig components = config.GetConfig("components");
    std::vector<std::string> Componentlist = components.GetKeys();
    for (auto key:Componentlist){
      Component newcomponent(key,components.GetConfig(key));
      m_components[newcomponent.GetComponentName()] = newomponent;
    }
  }
  
  std::string GetName()const{return m_name;};
  
  std::vector<std::string> GetTags()const{
  std::vector<std::string> v;
    for (auto s:m_Components){
      v.push_back(s.second.GetName());
    }
    return v;
  }
  std::vector<std::string> GetFor(const std::string t){
    return m_Components[t].GetFor();
  }
  
  bool HasFor(const std::string t, const std::string k) {
    return m_Components[t].HasFor(k);
  }
  
  bool HasTag(const std::string k)const{
    return IsInVector(k,GetTags());
  }
  
  std::vector<std::string> GetComponentNames()const{
    std::vector<std::string> keys;
    for (auto k:m_Components){
      keys.push_back(k.first);
    }
    return keys;
  }
  
  std::string GetJoinedName(const std::string sub){
    return m_Components[sub].GetName();
  }
 
};
// end of class
} // end namespace
#endif
