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



class SubSample{
private:
  std::string m_truth;
  std::string m_name;
  std::vector<std::string> m_for;
  std::vector<std::string> m_variables;
  NuConfig m_config;
public:
  SubSample(){};
  // constructor;
  SubSample(const std::string samplename, const NuConfig config){
    m_name = samplename; // this is the name of the associated sample
    m_for = config.GetStringVector("for");
    m_truth = config.GetString("true");
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
  std::string GetSampleName()const{return m_name;};
  std::string GetSubSampleName()const{return m_truth;};
  
  // this one is the tag for this Sample/SubSample pair
  std::string GetJoinedName()const{
      std::string tag= Form("%s:%s",m_name.c_str(),m_truth.c_str());
    return tag;
  }
};

class Sample{
private:
  std::string m_name;
  std::map<const std::string, SubSample> m_subsamples;
public:
  Sample( const std::string key, const NuConfig config){
    m_name = key;
    std::vector<NuConfig> subsamplelist = config.GetConfigVector();
    for (auto subsampleconfig:subsamplelist){
      SubSample subsample(key,subsampleconfig);
      m_subsamples[subsample.GetSubSampleName()] = subsample;
    }
  }
  
  std::string GetName()const{return m_name;};
  
  std::vector<std::string> GetTags()const{
  std::vector<std::string> v;
    for (auto s:m_subsamples){
      v.push_back(s.second.GetJoinedName());
    }
    return v;
  }
  std::vector<std::string> GetFor(const std::string t){
    return m_subsamples[t].GetFor();
  }
  
  bool HasFor(const std::string t, const std::string k) {
    return m_subsamples[t].HasFor(k);
  }
  
  bool HasTag(const std::string k)const{
    return IsInVector(k,GetTags());
  }
  
  std::vector<std::string> GetSubSampleNames()const{
    std::vector<std::string> keys;
    for (auto k:m_subsamples){
      keys.push_back(k.first);
    }
    return keys;
  }
  
  std::string GetJoinedName(const std::string sub){
    return m_subsamples[sub].GetJoinedName();
  }
 
};
// end of class
} // end namespace
#endif
