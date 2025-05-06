//==============================================================================
// Adapted from the MINERvA Analysis Toolkit Example
// Compared to previous examples, this script is a more faithful attempt to
// perform a realistic event selection for the cross section pipeline.
//
// It attempts to use all/most of the new MAT tools as of 2020-09.
// These include:
// * CVUniverse + Histwrapper
// * PlotUtils::MacroUtil
// * Variable class
// * PlotUtils::Cutter
//
// This script follows the canonical event-looping structure:
// Setup (I/O, variables, histograms, systematics)
// Loop events
//   loop universes
//     make cuts
//     loop variables
//       fill histograms
// Plot and Save
//==============================================================================
#include <iostream>
#include <vector>
#include "utils/NuConfig.h"
//#include "utils/gitVersion.h"
#include "PlotUtils/MacroUtil.h"
#include "include/CVUniverse.h"

#include "include/Systematics.h"  // GetStandardSystematics
#ifndef __CINT__
#include "PlotUtils/Cut.h"
#include "PlotUtils/Cutter.h"
#include "include/Get2DVariablesFromConfig.h"
#include "include/GetCCQECutsFromConfig.h"
#include "include/GetHyperDVariablesFromConfig.h"
#include "include/GetVariablesFromConfig.h"
#include "include/Variable2DFromConfig.h"
#include "include/VariableHyperDFromConfig.h"
#include "include/weight_MCreScale.h"
#include "include/weight_warper.h"
#include "utils/CoherentPiReweighter.h"
#include "utils/DiffractiveReweighter.h"
// #include "include/plotting_pdf.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TError.h"
#include "TNamed.h"
#endif
#ifndef HAZMAT
#include "PlotUtils/reweighters/Model.h"
#include "PlotUtils/reweighters/FluxAndCVReweighter.h"
#include "PlotUtils/reweighters/GENIEReweighter.h"
#include "PlotUtils/reweighters/LowRecoil2p2hReweighter.h"
#include "PlotUtils/reweighters/RPAReweighter.h"
#include "PlotUtils/reweighters/MINOSEfficiencyReweighter.h"
#include "PlotUtils/reweighters/LowQ2PiReweighter.h"
#else
#include "weighters/Model.h"
#include "weighters/FluxAndCVReweighter.h"
#include "weighters/GENIEReweighter.h"
#include "weighters/LowRecoil2p2hReweighter.h"
#include "weighters/RPAReweighter.h"
#include "weighters/MINOSEfficiencyReweighter.h"
#include "weighters/LowQ2PiReweighter.h"
#endif
#include "include/Fillers.h"
#include "include/Sample.h"
// #include <filesystem>

// needs to be global
int prescale;

template <typename T> bool IsInVector(const T & what, const std::vector<T> & vec)
{
    return std::find(vec.begin(),vec.end(),what)!=vec.end();
}


// Forward declare my variables because we're hiding the header.
namespace CCQENu {
  class VariableFromConfig;
  class Variable2DFromConfig;
  class VariableHyperDFromConfig;
}

#include "include/Loops.h"

// This is just so all the headers aren't filling up space in the real script here

#include "runsamplesMain.C"
// #include "runsamplesMain_lightweight.C"
