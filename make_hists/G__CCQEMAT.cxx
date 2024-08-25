// Do NOT change. Changes will be lost next time file is generated

#define R__DICTIONARY_FILENAME G__CCQEMAT
#define R__NO_DEPRECATION

/*******************************************************************/
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#define G__DICTIONARY
#include "ROOT/RConfig.hxx"
#include "TClass.h"
#include "TDictAttributeMap.h"
#include "TInterpreter.h"
#include "TROOT.h"
#include "TBuffer.h"
#include "TMemberInspector.h"
#include "TInterpreter.h"
#include "TVirtualMutex.h"
#include "TError.h"

#ifndef G__ROOT
#define G__ROOT
#endif

#include "RtypesImp.h"
#include "TIsAProxy.h"
#include "TFileMergeInfo.h"
#include <algorithm>
#include "TCollectionProxyInfo.h"
/*******************************************************************/

#include "TDataMember.h"

// Header files passed as explicit arguments
#include "include/Sample.h"
#include "include/CutFromConfig.h"
#include "include/CVFunctions.h"
#include "include/CVUniverse.h"
#include "include/GetCCQECutsFromConfig.h"
#include "include/GetVariablesFromConfig.h"
#include "include/Get2DVariablesFromConfig.h"
#include "include/GetStacked.h"
#include "include/Hist2DWrapperMap.h"
#include "include/HistWrapperMap.h"
#include "include/Systematics.h"
#include "include/Variable2DFromConfig.h"
#include "include/VariableFromConfig.h"
#include "include/plotting_pdf.h"
#include "include/weight_MCreScale.h"
#include "fits/ScaleFactors.h"
#include "fits/MultiScaleFactors.h"
#include "fits/DoTheFit.h"
#include "fits/DoTheFitBinByBin.h"
#include "utils/SyncBands.h"

// Header files passed via #pragma extra_include

// The generated code does not explicitly qualify STL entities
namespace std {} using namespace std;

namespace {
  void TriggerDictionaryInitialization_libCCQEMAT_Impl() {
    static const char* headers[] = {
"include/Sample.h",
"include/CutFromConfig.h",
"include/CVFunctions.h",
"include/CVUniverse.h",
"include/GetCCQECutsFromConfig.h",
"include/GetVariablesFromConfig.h",
"include/Get2DVariablesFromConfig.h",
"include/GetStacked.h",
"include/Hist2DWrapperMap.h",
"include/HistWrapperMap.h",
"include/Systematics.h",
"include/Variable2DFromConfig.h",
"include/VariableFromConfig.h",
"include/plotting_pdf.h",
"include/weight_MCreScale.h",
"fits/ScaleFactors.h",
"fits/MultiScaleFactors.h",
"fits/DoTheFit.h",
"fits/DoTheFitBinByBin.h",
"utils/SyncBands.h",
nullptr
    };
    static const char* includePaths[] = {
"/Users/schellma/miniforge3/envs/my_root_env/include",
"/Users/schellma/Dropbox/FORGE/CCQENu/make_hists",
"/Users/schellma/Dropbox/FORGE/CCQENu/make_hists/include",
"/Users/schellma/Dropbox/FORGE/opt/lib/../include",
"/Users/schellma/Dropbox/FORGE/opt/lib/../include/PlotUtils",
"/Users/schellma/Dropbox/FORGE/opt/lib/../include/UnfoldUtils",
"/Users/schellma/Dropbox/FORGE/opt/lib/../include/RooUnfold",
"/Users/schellma/LocalApps/jsoncpp-build/include",
"/Users/schellma/Dropbox/FORGE/opt/lib",
"/Users/schellma/Dropbox/FORGE/opt/lib/PlotUtils",
"/Users/schellma/Dropbox/FORGE/CCQENu/make_hists/fits",
"/Users/schellma/miniforge3/envs/my_root_env/include/",
"/Users/schellma/Dropbox/FORGE/CCQENu/make_hists/",
nullptr
    };
    static const char* fwdDeclCode = R"DICTFWDDCLS(
#line 1 "libCCQEMAT dictionary forward declarations' payload"
#pragma clang diagnostic ignored "-Wkeyword-compat"
#pragma clang diagnostic ignored "-Wignored-attributes"
#pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
extern int __Cling_AutoLoading_Map;
)DICTFWDDCLS";
    static const char* payloadCode = R"DICTPAYLOAD(
#line 1 "libCCQEMAT dictionary payload"

#ifndef __ROOFIT_NOBANNER
  #define __ROOFIT_NOBANNER 1
#endif
#ifndef _LIBCPP_DISABLE_AVAILABILITY
  #define _LIBCPP_DISABLE_AVAILABILITY 1
#endif
#ifndef FORM
  #define FORM 1
#endif
#ifndef HAZMAT
  #define HAZMAT 1
#endif
#ifndef MNVROOT6
  #define MNVROOT6 1
#endif
#ifndef PLOTUTILS_STANDALONE
  #define PLOTUTILS_STANDALONE 1
#endif
#ifndef COMPILED
  #define COMPILED 1
#endif

#define _BACKWARD_BACKWARD_WARNING_H
// Inline headers
#include "include/Sample.h"
#include "include/CutFromConfig.h"
#include "include/CVFunctions.h"
#include "include/CVUniverse.h"
#include "include/GetCCQECutsFromConfig.h"
#include "include/GetVariablesFromConfig.h"
#include "include/Get2DVariablesFromConfig.h"
#include "include/GetStacked.h"
#include "include/Hist2DWrapperMap.h"
#include "include/HistWrapperMap.h"
#include "include/Systematics.h"
#include "include/Variable2DFromConfig.h"
#include "include/VariableFromConfig.h"
#include "include/plotting_pdf.h"
#include "include/weight_MCreScale.h"
#include "fits/ScaleFactors.h"
#include "fits/MultiScaleFactors.h"
#include "fits/DoTheFit.h"
#include "fits/DoTheFitBinByBin.h"
#include "utils/SyncBands.h"

#undef  _BACKWARD_BACKWARD_WARNING_H
)DICTPAYLOAD";
    static const char* classesHeaders[] = {
nullptr
};
    static bool isInitialized = false;
    if (!isInitialized) {
      TROOT::RegisterModule("libCCQEMAT",
        headers, includePaths, payloadCode, fwdDeclCode,
        TriggerDictionaryInitialization_libCCQEMAT_Impl, {}, classesHeaders, /*hasCxxModule*/false);
      isInitialized = true;
    }
  }
  static struct DictInit {
    DictInit() {
      TriggerDictionaryInitialization_libCCQEMAT_Impl();
    }
  } __TheDictionaryInitializer;
}
void TriggerDictionaryInitialization_libCCQEMAT() {
  TriggerDictionaryInitialization_libCCQEMAT_Impl();
}
