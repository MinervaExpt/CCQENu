#ifndef DOTHEFIT_h
#define DOTHEFIT_h
#include <map>
#include <vector>

#include "PlotUtils/MnvH1D.h"
#include "fits/MultiScaleFactors.h"

namespace fit {

int DoTheFit(std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> fitHists,
             const std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> unfitHists,
             const std::map<const std::string, PlotUtils::MnvH1D*> dataHist,
             const std::map<const std::string, bool> includeInFit,
             const std::vector<std::string> categories,
             const fit_type type = kML,
             const int lowBin = 1, const int hiBin = -1,
             const bool binbybin = false,
             const std::string outputDir = ".");

int DoTheFit(std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> fitHists,
             PlotUtils::MnvH1D* parameters, 
             const std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> unfitHists,
             const std::map<const std::string, PlotUtils::MnvH1D*> dataHist,
             const std::map<const std::string, bool> includeInFit,
             const std::vector<std::string> categories,
             const fit_type type = kML,
             const int lowBin = 1, const int hiBin = -1,
             const bool binbybin = false,
             const std::string outputDir = ".",
             const int fitbin = 0);

// int DoTheFit(std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> fitHists,
//              std::vector<PlotUtils::MnvH1D*> parameters, PlotUtils::MnvH12D* covariance, PlotUtils::MnvH1D* fcn,
//              const std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> unfitHists,
//              const std::map<const std::string, PlotUtils::MnvH1D*> dataHist,
//              const std::map<const std::string, bool> includeInFit,
//              const std::vector<std::string> categories,
//              const fit_type type = kML,
//              const int lowBin = 1, const int hiBin = -1,
//              const bool binbybin = false,
//              const std::string outputDir = ".",
//              const int fitbin = 0);
// };
};
#endif
