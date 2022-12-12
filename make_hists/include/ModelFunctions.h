#ifndef modelfunctions_h
#define modelfunctions_h

#include <iostream>

#include "include/CVUniverse.h"
#include "weighters/Model.h"
#include "weighters/Reweighter.h"

#include "weighters/FluxAndCVReweighter.h"
#include "weighters/GENIEReweighter.h"
#include "weighters/LowRecoil2p2hReweighter.h"
#include "weighters/RPAReweighter.h"
#include "weighters/MINOSEfficiencyReweighter.h"
#include "weighters/LowQ2PiReweighter.h"

#include <string>
#include <map>
#include <vector>
#include <functional>
#include <cassert>


template <class CVUNIVERSE, class EVENT = PlotUtils::detail::empty>
class ModelFunctions{

  // typedef std::function<double(const CVUNIVERSE&)> PointerToWeighter;
  typedef std::function<Reweighter(const CVUNIVERSE&,EVENT)> PointerToWeighter;
  std::map<const std::string, PointerToWeighter> reweighterfunctions;



public:
  ModelFunctions(){
    // MnvTunev1 & v2
    reweighterfunctions["FluxAndCV"] = &PlotUtils::FluxAndCVReweighter;
    reweighterfunctions["GENIE"] = &PlotUtils::GENIEReweighter;
    reweighterfunctions["LowRecoil2p2h"] = &PlotUtils::LowRecoil2p2hReweighter;
    reweighterfunctions["MINOSEfficiency"] = &PlotUtils::MINOSEfficiencyReweighter;
    reweighterfunctions["RPA"] = &PlotUtils::RPAReweighter;

    // MnvTune v2
    reweighterfunctions["LowQ2Pi"] = &PlotUtils::LowQ2PiReweighter;

    // TODO: MnvTune v3 goes HERE


    // TODO: MnvTune v4 goes HERE


    //TODO: how to add in arguments?
    std::vector<std::unique_ptr<PlotUtils::Reweighter<CVUniverse,PlotUtils::detail::empty>>> m_tune;


    m_tune.emplace_back(new PlotUtils::FluxAndCVReweighter<CVUniverse, PlotUtils::detail::empty>());
      bool NonResPiReweight = true;
      bool DeuteriumGeniePiTune = false; // Deut should be 0? for v1?
    m_tune.emplace_back(new PlotUtils::GENIEReweighter<CVUniverse,PlotUtils::detail::empty>(NonResPiReweight,DeuteriumGeniePiTune));  // Deut should be 0? for v1?
    m_tune.emplace_back(new PlotUtils::LowRecoil2p2hReweighter<CVUniverse, PlotUtils::detail::empty>());
    m_tune.emplace_back(new PlotUtils::MINOSEfficiencyReweighter<CVUniverse, PlotUtils::detail::empty>());
    m_tune.emplace_back(new PlotUtils::RPAReweighter<CVUniverse, PlotUtils::detail::empty>());

    m_tune.emplace_back(new PlotUtils::LowQ2PiReweighter<CVUniverse, PlotUtils::detail::empty>("JOINT"));

  }
}
// This is a list of functions that ModelFromConfig uses to find which weighters are needed for new
#endif
