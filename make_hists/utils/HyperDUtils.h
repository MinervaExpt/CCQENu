#ifndef HYPERDUTILS_H
#define HYPERDUTILS_H
#include <TFile.h>

#include "MinervaUnfold/MnvResponse.h"
#include "MinervaUnfold/MnvUnfold.h"
#include "PlotUtils/HyperDimLinearizer.h"
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "PlotUtils/MnvH3D.h"

namespace CCQENu {
namespace HyperDUtils {
// void splitObject(MnvH2D* orig, MnvH2D** histos, bool fullSplit = false);

template <class MnvHist, class MnvVertErrorBandType, class MnvLatErrorBandType>
void splitObject(MnvHist* orig, MnvHist** histos, bool fullSplit = false);

template <class MnvHist, class MnvVertErrorBandType, class MnvLatErrorBandType>
std::vector<std::shared_ptr<MnvHist>> splitObject(MnvHist* orig, bool fullSplit = false);

template <class T>
void combineObject(T* temp, MnvH2D*& target, std::string prefix, TFile* source_file, bool fullSplit = false);
}  // namespace HyperDUtils
}  // namespace CCQENu
#endif