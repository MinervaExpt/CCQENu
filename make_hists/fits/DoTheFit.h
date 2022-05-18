#ifndef DOTHEFIT_h
#define DOTHEFIT_h
#include "PlotUtils/MnvH1D.h"
#include "fits/MultiScaleFactors.h"
#include <map>
#include <vector>

namespace fit{

int DoTheFit(std::map<const std::string, std::vector< PlotUtils::MnvH1D*>> fitHists, const std::map<const std::string, std::vector< PlotUtils::MnvH1D*> > unfitHists, const std::map<const std::string, PlotUtils::MnvH1D*>  dataHist, const std::map<const std::string, bool> includeInFit, const std::vector<std::string> categories, const fit_type type = kML, const int lowBin = 1, const int hiBin = -1);
};
#endif
