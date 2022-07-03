#ifndef UniverseUtils_H
#define UniverseUtils_H
#include "PlotUtils/MnvH1D.h"
double GetUnivVal(const PlotUtils::MnvH1D* m,const std::string band, const int univ, const double val){
    const TH1D*  hist = m-> GetVertErrorBand(band)->GetHist(univ);
      int xbin = hist->GetXaxis()->FindBin(val);
      return  hist->GetBinContent(xbin);
}

#endif
