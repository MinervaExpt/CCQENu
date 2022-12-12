#ifndef modelfromconfig_h
#define modelfromconfig_h

#include <fstream>  //ifstream
#include <iostream> //cout

#include <TString.h>
// #include <TH3D.h>
// #include <TH2D.h>
#include "utils/NuConfig.h"

#include "weighters/Model.h"
#include "weighters/FluxAndCVReweighter.h"
#include "weighters/GENIEReweighter.h"
#include "weighters/LowRecoil2p2hReweighter.h"
#include "weighters/RPAReweighter.h"
#include "weighters/MINOSEfficiencyReweighter.h"
#include "weighters/LowQ2PiReweighter.h"

#include "include/CVUniverse.h"


namespace PlotUtils{
// template <typename T>
  class ModelFromConfig{
  public:
    ModelFromConfig();

    NuConfig m_config; // Should be the main config
    std::string m_tunename;

    PlotUtils::Model<CVUniverse, PlotUtils::detail::empty> m_model; // This is what you should return

    PlotUtils::Model<CVUniverse, PlotUtils::detail::empty> GetModelFromConfig(NuConfig config){
      m_config = config;
      m_tunename = m_config.GetString("MinervaModel");
      if(m_tunename=="MnvTunev1"||m_tunename=="MnvTunev2"){
        m_tune.emplace_back(new PlotUtils::FluxAndCVReweighter<CVUniverse, PlotUtils::detail::empty>());
          bool NonResPiReweight = true;
          bool DeuteriumGeniePiTune = false; // Deut should be 0? for v1?
        m_tune.emplace_back(new PlotUtils::GENIEReweighter<CVUniverse,PlotUtils::detail::empty>(NonResPiReweight,DeuteriumGeniePiTune));  // Deut should be 0? for v1?
        m_tune.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, PlotUtils::detail::empty>());
        m_tune.emplace_back(new PlotUtils::MINOSEfficiencyReweighter<CVUniverse, PlotUtils::detail::empty>());
        m_tune.emplace_back(new PlotUtils::RPAReweighter<CVUniverse, PlotUtils::detail::empty>());
      }
      if(m_tunename=="MnvTunev2"){
        m_tune.emplace_back(new PlotUtils::LowQ2PiReweighter<CVUniverse, PlotUtils::detail::empty>("JOINT"));
      }
      m_model = = model(std::move(m_tune));
      return m_model;
    }


  private:
    std::vector<std::unique_ptr<PlotUtils::Reweighter<CVUniverse,PlotUtils::detail::empty>>> m_tune; // This is what you add all the reweights to
  }
}


#endif
