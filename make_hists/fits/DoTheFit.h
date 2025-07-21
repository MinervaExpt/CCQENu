#ifndef DOTHEFIT_h
#define DOTHEFIT_h
#include "PlotUtils/MnvH1D.h"
#include "fits/MultiScaleFactors.h"
#include <map>
#include <vector>

namespace fit{

int DoTheFit(std::map<const std::string, std::vector< PlotUtils::MnvH1D*>> fitHists, 
             const std::map<const std::string, std::vector< PlotUtils::MnvH1D*>> unfitHists, 
             const std::map<const std::string, PlotUtils::MnvH1D*>  dataHist, 
             std::map<const std::string, std::map<const std::string, std::vector< PlotUtils::MnvH1D*>>> addFitHists, 
             const std::map<const std::string, std::map<const std::string, std::vector< PlotUtils::MnvH1D*>>> addUnfitHists, 
             const std::map<const std::string, std::map<const std::string, PlotUtils::MnvH1D*>>  addDataHist, 
             const std::map<const std::string, bool> includeInFit, const std::vector<std::string> categories, const fit_type type = kML, 
             const int lowBin = 1, const int hiBin = -1, const std::map<const std::string, int> addHiBin = std::map<const std::string, int>(), 
             const double upperLimit=1000., const bool binbybin=false);

int DoTheFitSlices(std::map<const int, std::map<const std::string, std::vector< PlotUtils::MnvH1D*>>> fitHists, 
                   std::map<const int, std::map<const std::string, std::vector< PlotUtils::MnvH1D*>>> unfitHists, 
                   const std::map<const int, std::map<const std::string, PlotUtils::MnvH1D*>>  dataHist,
	               std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> fitHists_combined,
	               std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> unfitHists_combined,
                   const std::map<const std::string, PlotUtils::MnvH1D*> dataHist_combined,
                   const std::map<const std::string, bool> includeInFit, const std::vector<std::string> categories, const fit_type type = kML, 
                   const int lowBin = 1, const int hiBin = -1, 
                   const double upperLimit=1000., const bool binbybin=false);
};
#endif
