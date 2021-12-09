

#include "utils/NuConfig.h"
#include <vector>
#include <map>
#include <string>
#include "include/Sample.h"

using CCQENu::Sample;
using CCQENu::SubSample;

int main(){
  NuConfig config;
  config.Read("config/Samples_v3.json");
  config.Print();
  SubSample s;
  std::vector<std::string> samplenames = config.GetKeys();
  std::vector<CCQENu::Sample> samples;
  for (auto name:samplenames){
    std::cout << " sample name is " << name << std::endl;
    NuConfig data = config.GetConfig(name);
    samples.push_back(Sample(name,data));
  }
  
  for (auto sample:samples){
    
    std::vector<std::string> subsamplenames = sample.GetSubSampleNames();
    for (auto subsample:subsamplenames){
      std::cout << " subsample is named " << sample.GetJoinedName(subsample) << std::endl;
      std::vector<std::string> forvec = sample.GetFor(subsample);
      std::cout << " forvec = ";
      for (auto f:forvec){
        std::cout << f << " " ;
      }
      std::cout << std::endl;
    }
  }
  return 0;
}



