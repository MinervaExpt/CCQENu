#ifndef VARIABLEHYPERDBASE_H
#define VARIABLEHYPERDBASE_H

#include <memory>

#include "PlotUtils/VariableBase.h"
#include "PlotUtils/HyperDimLinearizer.h"

namespace PlotUtils {

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
  std::string GetName() const;
  std::string GetName(int axis) const;
  std::string GetAxisLabel() const;
  std::string GetAxisLabel(int axis) const;
  std::vector GetAxisLabelVec() const;
  int GetNBins() const;
  int GetNBins(int axis) const;
  std::vector<double> GetBinVec() const;
  std::vector<double> GetBinVec(int axis) const;
  void PrintBinning() const;
  void PrintBinning(int axis) const;
  PlotUtils::HyperDimLinearizer GetHyperDimLinearizer() const;


  //============================================================================
  // Get Value
  //============================================================================
  double GetRecoValue(int axis, const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

  double GetRecoValue(const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

  double GetTrueValue(const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

  double GetTrueValue(int axis, const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

 protected:
  std::vector<std::string> m_axis_label_vec;
  std::string m_lin_axis_label;
 private:
  //============================================================================
  // Member Variables
  //============================================================================
  std::string m_name;

  // Number of axes/dimensions in variable phase space
  int n_dimension;

  // Member HyperDim
  PlotUtils::HyperDimLinearizer m_hyperdim;

  // Linearized variable
  std::unique_ptr<VariableBase<UNIVERSE>> m_lin_var;

  // Vector of component variables
  std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> m_var_vec;

  // Vector of bins in variable phase space
  std::vector<std::vector<double>> m_varbins;

  // Bector of bins in bin space
  std::vector<double> m_lin_binning;

  VariableHyperDBase();  // off-limits
};
#endif

}  // namespace PlotUtils

#include "VariableHyperDBase.cxx"

#endif  // VARIABLEHYPERDBASE_H
