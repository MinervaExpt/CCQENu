#ifndef BINOMIALMC
#define BINOMIALMC
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include <string>
/** 
Program that does a binomial divide on 2 weighted histograms but then rescales the binomial errors. 
**/

PlotUtils::MnvH1D* BinomialMC(PlotUtils::MnvH1D* hist1, PlotUtils::MnvH1D* hist2,  TString newname );

PlotUtils::MnvH2D* BinomialMC(PlotUtils::MnvH2D* hist1, PlotUtils::MnvH2D* hist2,  TString newname);

#endif
