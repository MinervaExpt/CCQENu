#ifndef VARIABLE3DBASE_CXX
#define VARIABLE3DBASE_CXX

#include "PlotUtils/Variable3DBase.h"

using namespace PlotUtils;

//==============================================================================
//
// Variable 3D Base
//
//==============================================================================
//==============================================================================
// CTORS
//==============================================================================
template <class UNIVERSE>
Variable3DBase<UNIVERSE>::Variable3DBase(const VariableBase<UNIVERSE>& x,
                                         const VariableBase<UNIVERSE>& y,
                                         const VariableBase<UNIVERSE>& z)
    : m_name(x.GetName() + "_" + y.GetName() + "_" + z.GetName()),
      m_xaxis_label(x.GetAxisLabel()),
      m_yaxis_label(y.GetAxisLabel()),
      m_zaxis_label(z.GetAxisLabel()),
      m_var_x(new VariableBase<UNIVERSE>(x)),
      m_var_y(new VariableBase<UNIVERSE>(y)),
      m_var_z(new VariableBase<UNIVERSE>(z)) {}

template <class UNIVERSE>
Variable3DBase<UNIVERSE>::Variable3DBase(const std::string name,
                                         const VariableBase<UNIVERSE>& x,
                                         const VariableBase<UNIVERSE>& y,
                                         const VariableBase<UNIVERSE>& z)
    : m_name(name),
      m_xaxis_label(x.GetAxisLabel()),
      m_yaxis_label(y.GetAxisLabel()),
      m_zaxis_label(z.GetAxisLabel()),
      m_var_x(new VariableBase<UNIVERSE>(x)),
      m_var_y(new VariableBase<UNIVERSE>(y)),
      m_var_z(new VariableBase<UNIVERSE>(z)) {}

//==============================================================================
// Set/Get
//==============================================================================
template <class UNIVERSE>
std::string Variable3DBase<UNIVERSE>::SetName(const std::string name) {
  return m_name = name;
}

template <class UNIVERSE>
std::string Variable3DBase<UNIVERSE>::GetName() const {
  return m_name;
}

template <class UNIVERSE>
std::string Variable3DBase<UNIVERSE>::GetXAxisLabel() const {
  return m_xaxis_label;
}

template <class UNIVERSE>
std::string Variable3DBase<UNIVERSE>::GetYAxisLabel() const {
  return m_yaxis_label;
}

template <class UNIVERSE>
std::string Variable3DBase<UNIVERSE>::GetZAxisLabel() const {
  return m_zaxis_label;
}

template <class UNIVERSE>
std::string Variable3DBase<UNIVERSE>::GetNameX() const {
  return m_var_x->GetName();
}

template <class UNIVERSE>
std::string Variable3DBase<UNIVERSE>::GetNameY() const {
  return m_var_y->GetName();
}

template <class UNIVERSE>
std::string Variable3DBase<UNIVERSE>::GetNameZ() const {
  return m_var_z->GetName();
}

template <class UNIVERSE>
int Variable3DBase<UNIVERSE>::GetNBinsX() const {
  return m_var_x->GetNBins();
}

template <class UNIVERSE>
int Variable3DBase<UNIVERSE>::GetNBinsY() const {
  return m_var_y->GetNBins();
}

template <class UNIVERSE>
int Variable3DBase<UNIVERSE>::GetNBinsZ() const {
  return m_var_z->GetNBins();
}

template <class UNIVERSE>
std::vector<double> Variable3DBase<UNIVERSE>::GetBinVecX() const {
  return m_var_x->GetBinVec();
}

template <class UNIVERSE>
std::vector<double> Variable3DBase<UNIVERSE>::GetBinVecY() const {
  return m_var_y->GetBinVec();
}

template <class UNIVERSE>
std::vector<double> Variable3DBase<UNIVERSE>::GetBinVecZ() const {
  return m_var_z->GetBinVec();
}

template <class UNIVERSE>
void Variable3DBase<UNIVERSE>::PrintBinningX() const {
  m_var_x->PrintBinning();
}

template <class UNIVERSE>
void Variable3DBase<UNIVERSE>::PrintBinningY() const {
  m_var_y->PrintBinning();
}

template <class UNIVERSE>
void Variable3DBase<UNIVERSE>::PrintBinningZ() const {
  m_var_z->PrintBinning();
}

//==============================================================================
// GetValues
//==============================================================================
template <class UNIVERSE>
double Variable3DBase<UNIVERSE>::GetRecoValueX(const UNIVERSE& universe,
                                               const int idx1,
                                               const int idx2) const {
  return m_var_x->GetRecoValue(universe, idx1, idx2);
}

template <class UNIVERSE>
double Variable3DBase<UNIVERSE>::GetRecoValueY(const UNIVERSE& universe,
                                               const int idx1,
                                               const int idx2) const {
  return m_var_y->GetRecoValue(universe, idx1, idx2);
}

template <class UNIVERSE>
double Variable3DBase<UNIVERSE>::GetRecoValueZ(const UNIVERSE& universe,
                                               const int idx1,
                                               const int idx2) const {
  return m_var_z->GetRecoValue(universe, idx1, idx2);
}

template <class UNIVERSE>
double Variable3DBase<UNIVERSE>::GetTrueValueX(const UNIVERSE& universe,
                                               const int idx1,
                                               const int idx2) const {
  return m_var_x->GetTrueValue(universe, idx1, idx2);
}

template <class UNIVERSE>
double Variable3DBase<UNIVERSE>::GetTrueValueY(const UNIVERSE& universe,
                                               const int idx1,
                                               const int idx2) const {
  return m_var_y->GetTrueValue(universe, idx1, idx2);
}

template <class UNIVERSE>
double Variable3DBase<UNIVERSE>::GetTrueValueZ(const UNIVERSE& universe,
                                               const int idx1,
                                               const int idx2) const {
  return m_var_z->GetTrueValue(universe, idx1, idx2);
}

#endif  // VARIABLE3DBASE_CXX
