#ifndef GETCCQECUTSFromConfig_H
#define GETCCQECUTSFromConfig_H
#include "PlotUtils/Cut.h"
#include "CVUniverse.h"
#include "CutFromConfig.h"
#include "utils/NuConfig.h"


namespace config_reco {
//============================================================================
// This function instantiates each of the above cuts and adds them to a
// container, over which we'll loop during our event selection to apply the
// cuts.
//
// The return type for this function is a `cuts_t<UNIVERSE, EVENT>`, which is
// shorthand for std::vector<std::unique_ptr<PlotUtils::Cut<UNIVERSE, EVENT>>>;
//============================================================================
template <class UNIVERSE, class EVENT = PlotUtils::detail::empty>
PlotUtils::cuts_t<UNIVERSE> GetCCQECutsFromConfig(const NuConfig & config )
{
  typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseFunction;
  PlotUtils::cuts_t<UNIVERSE, EVENT> ccqe_cuts;
  std::cout << " set up the cuts" << std::endl;
  // event cuts
  //std::vector<std::string>  cuts= config.GetKeys();
  std::vector<NuConfig> cuts = config.GetConfigVector();
  CVFunctions<UNIVERSE> fun;
  // event cuts
//  ccqe_cuts.emplace_back(new NoDeadtime<UNIVERSE, EVENT>(config.GetValue("NoDeadTime")));
//  ccqe_cuts.emplace_back(new Apothem<UNIVERSE>(config.GetValue("Apothem")));
//  //ccqe_cuts.emplace_back(new ZRange<UNIVERSE>(config.GetValue("ZRange"))); // replace with generic
//  ccqe_cuts.emplace_back(new RangeFromConfig<UNIVERSE,double,&UNIVERSE::GetZVertex, EVENT>(config.GetValue("ZRange")));
//  // muon cuts
//  ccqe_cuts.emplace_back(new HasMINOSMatch<UNIVERSE, EVENT>(config.GetValue("HasMINOSMatch")));
//  //ccqe_cuts.emplace_back(new IsNeutrino<UNIVERSE, EVENT>(config.GetValue("IsNeutrino")));
//  //ccqe_cuts.emplace_back(new MaxMuonAngle<UNIVERSE, EVENT>(config.GetValue("MaxMuonAngle")));
// // ccqe_cuts.emplace_back(new MuonMomentumMin<UNIVERSE, EVENT>(config.GetValue("MuonMomentumMin")));
// // ccqe_cuts.emplace_back(new MuonMomentumMax<UNIVERSE, EVENT>(config.GetValue("MuonMomentumMax")));
//  ccqe_cuts.emplace_back(new MaximumFromConfig<UNIVERSE,double,&UNIVERSE::GetThetamuDegrees>(config.GetValue("MaxMuonAngle")));
//  ccqe_cuts.emplace_back(new MinimumFromConfig<UNIVERSE,double,&UNIVERSE::GetPmuGeV, EVENT>(config.GetValue("MuonMomentumMin")));
//  ccqe_cuts.emplace_back(new MaximumFromConfig<UNIVERSE,double,&UNIVERSE::GetPmuGeV, EVENT>(config.GetValue("MuonMomentumMax")));
//  ccqe_cuts.emplace_back(new MaximumFromConfigFunc<UNIVERSE>(config.GetConfig("MuonMomentumMax"),fun));
//  // recoil cuts
//  ccqe_cuts.emplace_back(new MaxMultiplicity<UNIVERSE, EVENT>(config.GetValue("MaxMultiplicity")));
//  ccqe_cuts.emplace_back(new GoodRecoil<UNIVERSE, EVENT>(config.GetValue("GoodRecoil")));
  for (auto cut:cuts){
    std::string key = cut.GetString("name");
    //NuConfig cut(config.GetConfig(key)); // make a subconfig
    std::string variable = cut.GetString("variable");
    std::cout << " set up cut " << key << " using variable " << variable << std::endl;
    if( cut.IsMember("equals")){
      ccqe_cuts.emplace_back( new IsSameFromConfigFunc<UNIVERSE>(cut,fun));
    }
    else{
      if (cut.IsMember("min") and cut.IsMember("max")){
        ccqe_cuts.emplace_back( new RangeFromConfigFunc<UNIVERSE>(cut,fun));
      }
      else{
        if( cut.IsMember("max")){
          ccqe_cuts.emplace_back( new MaximumFromConfigFunc<UNIVERSE>(cut,fun));
        }
        else{
          if( cut.IsMember("min")){
            ccqe_cuts.emplace_back( new MinimumFromConfigFunc<UNIVERSE>(cut,fun));
          }
          else{
            std::cout << " asked for a cut without a valid type " << key << std::endl;
            exit(8);
          }
        }
      }
    }
  }


  return ccqe_cuts;
}

// don't need this as can configure it.

//template <class UNIVERSE, class EVENT = PlotUtils::detail::empty>
//PlotUtils::cuts_t<UNIVERSE, EVENT> GetCCQENuCuts()
//{
//  PlotUtils::cuts_t<UNIVERSE, EVENT> ccqe_cuts;
//  std::cout << " set up the cuts" << std::endl;
//  // event cuts
//  ccqe_cuts.emplace_back(new NoDeadtime<UNIVERSE, EVENT>(1, "Deadtime"));
//  ccqe_cuts.emplace_back(new Apothem<UNIVERSE>(850.));
//  ccqe_cuts.emplace_back(new ZRange<UNIVERSE>("Tracker", 5980, 8422));
//  // muon cuts
//  ccqe_cuts.emplace_back(new HasMINOSMatch<UNIVERSE, EVENT>());
//  ccqe_cuts.emplace_back(new IsNeutrino<UNIVERSE, EVENT>(true));
//  ccqe_cuts.emplace_back(new MaxMuonAngle<UNIVERSE, EVENT>(20.));
//  ccqe_cuts.emplace_back(new MuonMomentumMin<UNIVERSE, EVENT>(1.5, "Minimum Pmu"));
//  ccqe_cuts.emplace_back(new MuonMomentumMax<UNIVERSE, EVENT>(20., "Maximum Pmu"));
//  // recoil cuts
//  ccqe_cuts.emplace_back(new MaxMultiplicity<UNIVERSE, EVENT>(2));
//  ccqe_cuts.emplace_back(new GoodRecoil<UNIVERSE, EVENT>());
//  return ccqe_cuts;
//}



}

namespace config_truth{
//-----------signal

template <class UNIVERSE>
PlotUtils::constraints_t<UNIVERSE> GetCCQEPhaseSpaceFromConfig(NuConfig & config)
{
 

//  signalDef.emplace_back(new MaximumConstraintFromConfig<UNIVERSE,double,&UNIVERSE::GetTrueThetamuDegrees>(config.GetValue("MaxMuonAngle")));
//  signalDef.emplace_back(new MinimumConstraintFromConfig<UNIVERSE,double,&UNIVERSE::GetTruePmuGeV>(config.GetValue("MuonMomentumMin")));
//  signalDef.emplace_back(new MaximumConstraintFromConfig<UNIVERSE,double,&UNIVERSE::GetTruePmuGeV>(config.GetValue("MuonMomentumMax")));
//  signalDef.emplace_back(new Apothem<UNIVERSE>(config.GetValue("Apothem")));
//  signalDef.emplace_back(new RangeConstraintFromConfig<UNIVERSE,double,&UNIVERSE::GetTrueZVertex>(config.GetValue("ZRange")));
//
  
    typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseFunction;
    PlotUtils::constraints_t<UNIVERSE> signalDef;
    std::cout << " set up the constraints " << std::endl;
    // event cuts
     std::vector<NuConfig> cuts = config.GetConfigVector();
    
    CVFunctions<UNIVERSE> fun;
 
  for (auto cut:cuts){
      std::string key = cut.GetString("name");
      std::string variable = cut.GetString("variable");
      std::cout << " set up phase space  " << key << " using variable " << variable << std::endl;
      if( cut.IsMember("equals")){
        signalDef.emplace_back( new IsSameConstraintFromConfigFunc<UNIVERSE>(cut,fun));
      }
      else{
        if (cut.IsMember("min") and cut.IsMember("max")){
          signalDef.emplace_back( new RangeConstraintFromConfigFunc<UNIVERSE>(cut,fun));
        }
        else{
          if( cut.IsMember("max")){
            signalDef.emplace_back( new MaximumConstraintFromConfigFunc<UNIVERSE>(cut,fun));
          }
          else{
            if( cut.IsMember("min")){
              signalDef.emplace_back( new MinimumConstraintFromConfigFunc<UNIVERSE>(cut,fun));
            }
            else{
              std::cout << " asked for a signalDef without a valid type " << key << std::endl;
              exit(8);
            }
          }
        }
      }
    }

  return signalDef;
}



// CCQELike ------------------------ // this is actually identical to the fiducial stuff

template <class UNIVERSE>
PlotUtils::constraints_t<UNIVERSE> GetCCQESignalFromConfig(NuConfig & config)
{
    typedef std::function<double(const UNIVERSE&)> PointerToCVUniverseFunction;
    PlotUtils::constraints_t<UNIVERSE> signalDef;
    std::cout << " set up the constraints " << std::endl;
    // event cuts
  std::vector<NuConfig> cuts = config.GetConfigVector();
    CVFunctions<UNIVERSE> fun;

    for (auto cut:cuts){
      std::string key = cut.GetString("name");// make a subconfig
      std::string variable = cut.GetString("variable");
      std::cout << " set up signal definition  " << key << " using variable " << variable << std::endl;
      if( cut.IsMember("equals")){
        signalDef.emplace_back( new IsSameConstraintFromConfigFunc<UNIVERSE>(cut,fun));
      }
      else{
        if (cut.IsMember("min") and cut.IsMember("max")){
          signalDef.emplace_back( new RangeConstraintFromConfigFunc<UNIVERSE>(cut,fun));
        }
        else{
          if( cut.IsMember("max")){
            signalDef.emplace_back( new MaximumConstraintFromConfigFunc<UNIVERSE>(cut,fun));
          }
          else{
            if( cut.IsMember("min")){
              signalDef.emplace_back( new MinimumConstraintFromConfigFunc<UNIVERSE>(cut,fun));
            }
            else{
              std::cout << " asked for a signalDef without a valid type " << key << std::endl;
              exit(8);
            }
          }
        }
      }
    }

  return signalDef;
}


} // end namespace
#endif
