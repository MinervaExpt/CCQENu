#ifndef VARIABLE3DBASE_H
#define VARIABLE3DBASE_H

#include <memory>

#include "PlotUtils/VariableBase.h"

namespace PlotUtils {

#ifndef __CINT__
template <class UNIVERSE>
class Variable3DBase {
 public:
  //============================================================================
  // CTORS
  //============================================================================
  Variable3DBase(const VariableBase<UNIVERSE>& x,
                 const VariableBase<UNIVERSE>& y,
                 const VariableBase<UNIVERSE>& z);
  Variable3DBase(const std::string name,
                 const VariableBase<UNIVERSE>& x,
                 const VariableBase<UNIVERSE>& y,
                 const VariableBase<UNIVERSE>& z);

 public:
  //============================================================================
  // Setters/Getters
  //============================================================================
  std::string SetName(const std::string name);
  std::string GetXAxisLabel() const;
  std::string GetYAxisLabel() const;
  std::string GetZAxisLabel() const;
  std::string GetName() const;
  std::string GetNameX() const;
  std::string GetNameY() const;
  std::string GetNameZ() const;
  int GetNBinsX() const;
  int GetNBinsY() const;
  int GetNBinsZ() const;
  std::vector<double> GetBinVecX() const;
  std::vector<double> GetBinVecY() const;
  std::vector<double> GetBinVecZ() const;
  void PrintBinningX() const;
  void PrintBinningY() const;
  void PrintBinningZ() const;

  //============================================================================
  // Get Value
  //============================================================================
  double GetRecoValueX(const UNIVERSE& universe, const int idx1 = -1,
                              const int idx2 = -1) const;
  double GetRecoValueY(const UNIVERSE& universe, const int idx1 = -1,
                              const int idx2 = -1) const;
  double GetRecoValueZ(const UNIVERSE& universe, const int idx1 = -1,
                              const int idx2 = -1) const;
  double GetTrueValueX(const UNIVERSE& universe, const int idx1 = -1,
                              const int idx2 = -1) const;
  double GetTrueValueY(const UNIVERSE& universe, const int idx1 = -1,
                              const int idx2 = -1) const;
  double GetTrueValueZ(const UNIVERSE& universe, const int idx1 = -1,
                              const int idx2 = -1) const;

 protected:
  std::string m_xaxis_label;
  std::string m_yaxis_label;
  std::string m_zaxis_label;

 private:
  //============================================================================
  // Member Variables
  //============================================================================
  std::string m_name;

  std::unique_ptr<VariableBase<UNIVERSE>> m_var_x;
  std::unique_ptr<VariableBase<UNIVERSE>> m_var_y;
  std::unique_ptr<VariableBase<UNIVERSE>> m_var_z;

  Variable3DBase();  // off-limits
};
#endif

}  // namespace PlotUtils

#include "Variable3DBase.cxx"

#endif  // VARIABLE3DBASE_H
