

#include "utils/NuConfig.h"
#include <vector>
#include <map>
#include <string>
#include "include/Sample.h"

using CCQENu::Sample;
using CCQENu::Category;

int main(){
  NuConfig config;
  config.Read("hms/AntiNuSamples_v8.json");
  config.Print();
  
  std::vector<std::string> samplenames = config.GetKeys();
  std::vector<CCQENu::Sample> samples;
  for (auto name:samplenames){
    std::cout << " sample name is " << name << std::endl;
    NuConfig sample_config = config.GetConfig(name);
    samples.push_back(Sample(sample_config));
  }
  
  for (auto sample:samples){
    
    std::vector<std::string> categorynames = sample.GetCategoryNames();
    for (auto category:categorynames){
      std::cout << " Category is named " << sample.GetCategory(category).GetName() << std::endl;
      std::vector<std::string> forvec = sample.GetCategory(category).GetFor();
      std::cout << " forvec = ";
      for (auto f:forvec){
        std::cout << f << " " ;
      }
      std::cout << std::endl;
    }
  }
  return 0;
}



