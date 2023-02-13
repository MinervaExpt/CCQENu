#ifndef VARIABLEHYPERDBASE_H
#define VARIABLEHYPERDBASE_H

#include <memory>

#include "PlotUtils/VariableBase.h"
#include "PlotUtils/HyperDimLinearizer.h"

namespace PlotUtils {
enum EAnalysisType {k2D,k1D};

#ifndef __CINT__
template <class UNIVERSE>
class VariableHyperDBase {
 public:
  //============================================================================
  // CTORS
  //============================================================================
  VariableHyperDBase(std::vector<const VariableBase<UNIVERSE>&> d);
  VariableHyperDBase(const std::string name,
                     std::vector<const VariableBase<UNIVERSE>&> d);

 public:
  //============================================================================
  // Setters/Getters
  //============================================================================
  // TODO: reco binning!
  std::string SetName(const std::string name);
  void SetAnalysisType(const EAnalysisType t2D_t1D); // Set hyperdim to project to 2D or 1D
  std::string GetName() const; // Get Name of linearized variable
  std::string GetName(int axis) const; // Get name of variable on an axis
  std::string GetAxisLabel() const; // Get axis label for linearzed variable
  std::string GetAxisLabel(int axis) const; // Get axis label for one variable
  std::vector<std::string> GetAxisLabelVec() const; // Get vector of all the variables in the phase space
  int GetNBins() const; // Get number of linearized bins TODO: right now just true binning
  int GetNBins(int axis) const; // Get number of bins on an axis
  int GetNRecoBins() const; // Get number of linearized reco bins
  int GetNRecoBins(int axis) const; // Get number of reco bins for a variable 
  std::vector<double> GetBinVec() const; // Get vector of linearized bin edges, should just be a list of indexes essentially
  std::vector<double> GetBinVec(int axis) const; // Get vector of bin edges for an input variable
  std::vector<double> GetRecoBinVec() const;  // Same but reco bins TODO: right now just true binning
  std::vector<double> GetRecoBinVec(int axis) const; // Same but reco bins
  void PrintBinning() const; // Print linearized binning
  void PrintBinning(int axis) const; // Print binning for one input variable
  void PrintRecoBinning() const; // Same but reco bins TODO: right now just true binning
  void PrintRecoBinning(int axis) const; // Same but reco bins
  PlotUtils::HyperDimLinearizer* GetHyperDimLinearizer() const; // Returns the hyperdim
  double GetBinVolume(int lin_bin) const; // TODO: Maybe this belongs to hyperdim?
  double GetRecoBinVolume(int lin_recobin) const; // TODO: Maybe this belongs to hyperdim?

  //============================================================================
  // Get Value
  //============================================================================
  double
  GetRecoValue(int axis, const UNIVERSE &universe, const int idx1 = -1,
               const int idx2 = -1) const;

  double GetRecoValue(const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

  double GetTrueValue(const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

  double GetTrueValue(int axis, const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

 protected:

  std::string m_lin_axis_label;



 private:
  //============================================================================
  // Member Variables
  //============================================================================
  // Name of variable, should be var1name_var2name_var3name etc
  std::string m_name;

  // Number of axes/dimensions in variable phase space
  int m_dimension;

  // Member HyperDim
  PlotUtils::HyperDimLinearizer *m_hyperdim;

  // Linearized variable
  std::unique_ptr<VariableBase<UNIVERSE>> m_lin_var;

  // Vector of component variables
  std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> m_vars_vec;

  // Vector of bins in variable phase space
  std::vector<std::vector<double>> m_vars_bins;

  // Vector of bins in bin space
  std::vector<double> m_lin_binning;

  // This sets the "Analysis type" from Hyperdim:
  // k2D: 2D leaves y axis alone, "projects" all others down to x (like Dan's analysis)
  // k1D: 1D fully linearizes, "projects" everything down to x
  EAnalysisType m_analysis_type;

  VariableHyperDBase();  // off-limits
};
#endif

}  // namespace PlotUtils

#include "VariableHyperDBase.cxx"

#endif  // VARIABLEHYPERDBASE_H
