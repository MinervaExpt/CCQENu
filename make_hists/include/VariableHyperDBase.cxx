#ifndef VARIABLEHYPERDBASE_CXX
#define VARIABLEHYPERDBASE_CXX

#include "VariableHyperDBase.h"
#include "PlotUtils/HyperDimLinearizer.h"

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
  std::string lin_axis_label;
  std::vector<std::string> axis_label_vec;
  std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> var_vec;
  int n_lin_bins = 1;
  std::vector<std::vector<double>> var_bins;
  m_dimension = d.size();

  for(int i=0; i<d.size(); i++){
    // Make vector of input variables
    var_vec.push_back(new VariableBase<UNIVERSE>(d[i]));

    // Make name for variable, axis
    name+=d[i].GetName();
    lin_axis_label+=d[i].GetAxisLabel();

    if(i<(d.size()-1)){ 
      name+="_" ;
      lin_axis_label+=", ";
    }

    // // Make vector of axis labels TODO: Necessary?
    // axis_label_vec.push_back(d[i].GetAxisLabel());

    // Make vector of binnings, count number of bins
    std::vector<double> var_binning = d[i]->GetBinVec();
    var_bins.push_back(var_binning);
    n_lin_bins*=(var_binning.size()+1); // includes under/over flow (total bins = size of bin edges -1 (high edge) + 2 (under/overflow))
  }

  m_name = name;
  m_lin_axis_label = lin_axis_label;
  // m_axis_label_vec = axis_label_vec; //TODO: Necessary?
  m_var_vec = var_vec;


  // Initialize a hyperdim with that binning
  m_hyperdim = new HyperDimLinearizer(var_bins,0);

  // Make a binning in bin space
  std::vector<double> lin_binning;
  for(int i=0;i<n_lin_bins;i++) lin_binning.push_back(i);
  m_lin_binning = lin_binning;

  // Make the linearized variable TODO: Is this necessary?
  m_lin_var = new VariableBase<UNIVERSE>(m_name,m_lin_axis_label,m_lin_binning);

}

template <class UNIVERSE>
VariableHyperDBase<UNIVERSE>::VariableHyperDBase(const std::string name, std::vector<const VariableBase<UNIVERSE>&> d){
  std::string lin_axis_label;
  std::vector<std::string> axis_label_vec;
  std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> var_vec;
  std::vector<std::vector<double>> var_bins;
  int n_lin_bins = 1;
  m_dimension = d.size();

  for(int i=0; i<d.size(); i++){
    // Make vector of input variables
    var_vec.push_back(new VariableBase<UNIVERSE>(d[i]));

    // Make name for variable, axis
    lin_axis_label+=d[i].GetAxisLabel();

    if(i<(d.size()-1)){ 
      lin_axis_label+=", ";
    }

    // // Make vector of axis labels // TODO: Necessary?
    // axis_label_vec.push_back(d[i].GetAxisLabel());

    // Make vector of binnings, count number of bins
    std::vector<double> var_binning = d[i]->GetBinVec();
    var_bins.push_back(var_binning);
    n_lin_bins*=(var_binning.size()+1); // includes under/over flow (total bins = size of bin edges -1 (high edge) + 2 (under/overflow))
  }
  
  m_name = name;
  m_lin_axis_label = lin_axis_label;
  // m_axis_label_vec = axis_label_vec; //TODO: Necessary?
  m_var_vec = var_vec;

  // Place holder to manipulate

  // Initialize a hyperdim with that binning
  m_hyperdim = new HyperDimLinearizer(var_bins,0);

  // Make a vector in bin space
  std::vector<double> lin_binning;
  for(int i=0;i<n_lin_bins;i++) lin_binning.push_back(i);
  m_lin_binning = lin_binning;

  // Make the linearized variable TODO: Is this necessary?
  m_lin_var = new VariableBase<UNIVERSE>(m_name,m_lin_axis_label,m_lin_binning);
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
std::string VariableHyperDBase<UNIVERSE>::GetName(const int axis) const {
  return m_var_vec[axis]->GetName();
}

template <class UNIVERSE>
std::string VariableHyperDBase<UNIVERSE>::GetAxisLabel() const {
  return m_lin_axis_label;
}

template <class UNIVERSE>
std::string VariableHyperDBase<UNIVERSE>::GetAxisLabel(const int axis) const {
  return m_axis_label_vec[axis];
}

template <class UNIVERSE>
std::vector<std::string> VariableHyperDBase<UNIVERSE>::GetAxisLabelVec() const {
  return m_axis_label_vec;
}

// Used to get the number of linearized bins
template <class UNIVERSE>
int VariableHyperDBase<UNIVERSE>::GetNBins() const {
  return m_lin_var->GetNBins();  //TODO: is this calculation correct? It will include under/overflow bins...
  // return m_lin_binning.size() - 1; 

  // This will not count under/overflow bins that are interspersed in the bins of the lin variable
  // int nbins = (m_lin_var->GetNBins())-2*d;
  // return nbins;
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
  // return m_lin_binning;
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

template <class UNIVERSE>
PlotUtils::HyperDimLinearizer* VariableHyperDBase<UNIVERSE>::GetHyperDimLinearizer() const {
  return m_hyperdim;
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
