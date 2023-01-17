#ifndef VARIABLEHYPERDBASE_CXX
#define VARIABLEHYPERDBASE_CXX

#include "PlotUtils/VariableHyperDBase.h"

using namespace PlotUtils;

//==============================================================================
//
// Variable HyperD Base
//
//==============================================================================
//==============================================================================
// CTORS
//==============================================================================
template <class UNIVERSE>
VariableHyperDBase<UNIVERSE>::VariableHyperDBase(std::vector<const VariableBase<UNIVERSE>&> d){
  std::string name;
  std::vector<std::string> axis_label_vec;
  std::vector<std::unique_ptr<VariableBase<UNIVERSE>> var_vec;

  for(int i=0; i<d.size(); i++){
    name+=d[i].GetName();
    i<d.size()-1? name+="_";
    axis_label_vec.push_back(d[i].GetAxisLabel());
    var_vec.pushback(new VariableBase<UNIVERSE>(d[i]));
  }
  m_name = name;
  m_axis_label_vec = axis_label_vec;
  m_var_vec = var_vec;
}

template <class UNIVERSE>
VariableHyperDBase<UNIVERSE>::VariableHyperDBase(const std::string name, std::vector<const VariableBase<UNIVERSE>&> d){
  std::vector<std::string> axis_label_vec;
  std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> var_vec;

  for(auto variable:d){
    axis_label_vec.push_back(variable.GetAxisLabel());
    var_vec.push_back(new VariableBase<UNIVERSE>(variable));
  }
  m_name = name;
  m_axis_label_vec = axis_label_vec;
  m_var_vec = var_vec;
}
//==============================================================================
// Set/Get
//==============================================================================
template <class UNIVERSE>
std::string VariableHyperDBase<UNIVERSE>::SetName(const std::string name) {
  return m_name = name;
}

template <class UNIVERSE>
std::string VariableHyperDBase<UNIVERSE>::GetName() const {
  return m_name;
}

template <class UNIVERSE>
std::string VariableHyperDBase<UNIVERSE>::GetAxisLabel(const int axis) const {
  return m_axis_label_vec[axis];
}

template <class UNIVERSE>
std::string VariableHyperDBase<UNIVERSE>::GetAxisName(const int axis) const {
  return m_var_vec[axis]->GetName();
}

// Used to get the number of linearized bins
template <class UNIVERSE>
int VariableHyperDBase<UNIVERSE>::GetNBins() const {
  return m_lin_var->GetNBins();
}

// Used to get the number of bins in a given axis
template <class UNIVERSE>
int VariableHyperDBase<UNIVERSE>::GetNBins(const int axis) const {
  return m_var_vec[axis]->GetNBins();
}

// Used to get the linearized bin edges
template <class UNIVERSE>
std::vector<double> VariableHyperDBase<UNIVERSE>::GetBinVec() const {
  return m_lin_var->GetBinVec();
}

// Used to get the bin edges of a given axis
template <class UNIVERSE>
std::vector<double> VariableHyperDBase<UNIVERSE>::GetBinVec(const int axis) const {
  return m_var_vec[axis]->GetBinVec();
}

// Print the linearized binning
template <class UNIVERSE>
void VariableHyperDBase<UNIVERSE>::PrintBinning() const {
  m_lin_var->PrintBinning();
}

// Print the binning of an axis
template <class UNIVERSE>
void VariableHyperDBase<UNIVERSE>::PrintBinning(const int axis) const {
  m_var_vec[axis]->PrintBinning();
}

//==============================================================================
// GetValues
//==============================================================================

template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetRecoValue(const UNIVERSE& universe,
                                                  const int idx1,
                                                  const int idx2) const {
  return m_lin_var->GetRecoValue(universe, idx1, idx2);
}

template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetRecoValue(const int axis, const UNIVERSE& universe,
                                                  const int idx1,
                                                  const int idx2) const {
  return m_var_vec[axis]->GetRecoValue(universe, idx1, idx2);
}

template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetTrueValue(const UNIVERSE& universe,
                                                  const int idx1,
                                                  const int idx2) const {
  return m_lin_var->GetTrueValue(universe, idx1, idx2);
}

template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetTrueValue(const int axis, const UNIVERSE& universe,
                                                  const int idx1,
                                                  const int idx2) const {
  return m_var_vec[axis]->GetTrueValue(universe, idx1, idx2);
}


#endif  // VARIABLEHYPERDBASE_CXX
