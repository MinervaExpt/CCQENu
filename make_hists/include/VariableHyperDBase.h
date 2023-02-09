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

  std::string SetName(const std::string name);
  void SetAnalysisType(const EAnalysisType t2D_t1D);
  std::string GetName() const;
  std::string GetName(int axis) const;
  std::string GetAxisLabel() const;
  std::string GetAxisLabel(int axis) const;
  std::vector<std::string> GetAxisLabelVec() const;
  int GetNBins() const;
  int GetNBins(int axis) const;
  std::vector<double> GetBinVec() const;
  std::vector<double> GetBinVec(int axis) const;
  void PrintBinning() const;
  void PrintBinning(int axis) const;
  PlotUtils::HyperDimLinearizer* GetHyperDimLinearizer() const;
  double GetBinVolume(int lin_bin) const; // TODO: Maybe this belongs to hyperdim?

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
