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

class Category{
private:
  std::string m_name;
  std::vector<std::string> m_for;

  NuConfig m_config;
public:
  Category(){};
  // constructor;
  Category(const std::string key, const NuConfig config){
    
    m_name = key;
    m_for = config.GetStringVector("for");
    
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
  std::string GetName()const
    {return m_name;
    };
};

class Sample{
private:
  std::string m_name;
  std::string m_reco;
  NuConfig m_config;
  std::string m_phase_space;
  std::map<const std::string, Category> m_categories;
  std::vector<std::string> m_signals;
  std::vector<std::string> m_backgrounds;
public:
  Sample( const NuConfig config){
    m_config = config;
    m_name = config.GetString("name");
    m_reco = config.GetString("reco");
    m_signals = config.GetStringVector("signal");
    m_backgrounds = config.GetStringVector("background");
    NuConfig categories = config.GetConfig("categories");
    std::vector<std::string> Categorylist = categories.GetKeys();
    m_phase_space = config.GetString("phase_space");
    for (auto key:Categorylist){
      Category newcategory(key,categories.GetConfig(key));
      m_categories[key] = newcategory;
    }
  }
  
  std::string GetName()const{return m_name;};
  
  std::vector<std::string> GetTags()const{
  std::vector<std::string> v;
    for (auto s:m_categories){
      v.push_back(s.second.GetName());
    }
    return v;
  }
  
  std::string GetPhaseSpace()const{return m_phase_space;};
  
  bool HasTag(const std::string k)const{
    return IsInVector(k,GetTags());
  }
  
  std::string GetReco()const{
    return m_reco;
  }
  
  std::vector<std::string> GetCategoryNames()const{
    std::vector<std::string> keys;
    for (auto k:m_categories){
      keys.push_back(k.first);
    }
    return keys;
  }
  
  std::string GetName(const std::string sub){
    const std::string local = sub;
    return m_categories[local].GetName();
  }
  
  const Category GetCategory(const std::string sub){
    const std::string local = sub;
    return m_categories[local];
  }
  std::map<const std::string, Category> GetCategories(){
    return m_categories;
  }
 
};
// end of class
} // end namespace
#endif
