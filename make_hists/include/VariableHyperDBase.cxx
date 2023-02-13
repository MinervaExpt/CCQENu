#ifndef VARIABLEHYPERDBASE_CXX
#define VARIABLEHYPERDBASE_CXX

#include "VariableHyperDBase.h"
#include "PlotUtils/HyperDimLinearizer.h"

using namespace PlotUtils;

// TODO reco binning
//==============================================================================
//
// Variable HyperD Base
//
//==============================================================================
//==============================================================================
// CTORS
//==============================================================================
  template <class UNIVERSE>
  VariableHyperDBase<UNIVERSE>::VariableHyperDBase(std::vector<const VariableBase<UNIVERSE>&> d) {
    std::string name;
    std::string lin_axis_label;
    std::vector<std::string> axis_label_vec;
    std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> var_vec;
    int n_lin_bins = 1;
    std::vector<std::vector<double>> vars_bins;
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

      // Make vector of binnings, count number of bins
      std::vector<double> var_binning = d[i]->GetBinVec();
      var_bins.push_back(var_binning);
      // Need to add underflow and overflow bins (+2) and take out one from bin edges (-1) => var_binning.size()+1
      n_lin_bins*=(var_binning.size()+1);
    }
    
    m_name = name;
    m_lin_axis_label = lin_axis_label;
    m_vars_vec = var_vec;
    m_vars_bins = vars_bins;

    m_analysis_type = k1D;
    // Initialize a hyperdim with that binning
    m_hyperdim = new HyperDimLinearizer(var_bins,m_analysis_type); 

    // Make a binning in bin space
    std::vector<double> lin_binning;
    for(int i=0;i<n_lin_bins;i++) lin_binning.push_back(i);
    m_lin_binning = lin_binning;

    m_lin_var = new VariableBase<UNIVERSE>(m_name,m_lin_axis_label,m_lin_binning);
    
    // TODO: store volume/bin width in bin space? 
  }


  template <class UNIVERSE>
  VariableHyperDBase<UNIVERSE>::VariableHyperDBase(const std::string name, std::vector<const VariableBase<UNIVERSE> &> d) {
    std::string lin_axis_label;
    std::vector<std::string> axis_label_vec;
    std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> var_vec;
    std::vector<std::vector<double>> var_bins;
    m_dimension = d.size();
    int n_lin_bins = 1;

    for (int i = 0; i < d.size(); i++)
    {
      // Make vector of input variables
      var_vec.push_back(new VariableBase<UNIVERSE>(d[i]));

      // Make name for variable, axis
      lin_axis_label += d[i].GetAxisLabel();
      if (i < (d.size() - 1)) lin_axis_label += ", ";

      // Make vector of binnings, count number of bins
      std::vector<double> var_binning = d[i]->GetBinVec();
      vars_bins.push_back(var_binning);
      n_lin_bins *= (var_binning.size() + 1); // includes under/over flow (total bins = size of bin edges - 1 (high edge) + 2 (under/overflow))
    }

    m_name = name;
    m_lin_axis_label = lin_axis_label;
    m_vars_vec = var_vec;
    m_vars_bins = vars_bins;

    m_analysis_type = k1D;

    // Initialize a hyperdim with that binning
    m_hyperdim = new HyperDimLinearizer(var_bins, m_analysis_type);

    // Make a vector in bin space
    std::vector<double> lin_binning;
    for (int i = 0; i < n_lin_bins; i++)
      lin_binning.push_back(i);
    m_lin_binning = lin_binning;

    // Make the linearized variable TODO: Is this necessary?
    m_lin_var = new VariableBase<UNIVERSE>(m_name, m_lin_axis_label, m_lin_binning);
  }
  //==============================================================================
  // Set/Get
  //==============================================================================
  template <class UNIVERSE>
  std::string VariableHyperDBase<UNIVERSE>::SetName(const std::string name)
  {
    return m_name = name;
  }

  template <class UNIVERSE>
  void VariableHyperDBase<UNIVERSE>::SetAnalysisType(const EAnalysisType t2D_t1D)
  {
    m_analysis_type = t2D_t1D;
    std::cout << "VariableHyperDBase: WARNING you may be changing your analysis type." << std::endl;
    m_hyperdim = new HyperDimLinearizer(m_vars_bins, t2D_t1D);
  }

  template <class UNIVERSE>
  std::string VariableHyperDBase<UNIVERSE>::GetName() const
  {
    return m_name;
  }

  template <class UNIVERSE>
  std::string VariableHyperDBase<UNIVERSE>::GetName(const int axis) const
  {
    return m_vars_vec[axis]->GetName();
  }

  template <class UNIVERSE>
  std::string VariableHyperDBase<UNIVERSE>::GetAxisLabel() const
  {
    return m_lin_axis_label;
  }

  template <class UNIVERSE>
  std::string VariableHyperDBase<UNIVERSE>::GetAxisLabel(const int axis) const
  {
    return m_axis_label_vec[axis];
  }

  template <class UNIVERSE>
  std::vector<std::string> VariableHyperDBase<UNIVERSE>::GetAxisLabelVec() const
  {
    return m_axis_label_vec;
  }

  // Used to get the number of linearized bins
  template <class UNIVERSE>
  int VariableHyperDBase<UNIVERSE>::GetNBins() const
  {
    return m_lin_var->GetNBins(); // TODO: is this calculation correct? It will include under/overflow bins...
    // return m_lin_binning.size() - 1;

    // This will not count under/overflow bins that are interspersed in the bins of the lin variable
    // int nbins = (m_lin_var->GetNBins())-2*d;
    // return nbins;
  }

  // Used to get the number of bins in a given axis
  template <class UNIVERSE>
  int VariableHyperDBase<UNIVERSE>::GetNBins(const int axis) const
  {
    return m_vars_vec[axis]->GetNBins();
  }

  template <class UNIVERSE>
  int VariableHyperDBase<UNIVERSE>::GetNRecoBins() const
  {
    return m_lin_var->GetNBins();
    // TODO: Right now just returns true binning. Is it worth storing a second hyperdim?
  }

  template <class UNIVERSE>
  int VariableHyperDBase<UNIVERSE>::GetNRecoBins(const int axis) const
  {
    return m_lin_var[axis]->GetNRecoBins();
    // Returns the reco binning for one of the input variables
  }

  // Used to get the linearized bin edges
  template <class UNIVERSE>
  std::vector<double> VariableHyperDBase<UNIVERSE>::GetBinVec() const
  {
    return m_lin_var->GetBinVec();
    // return m_lin_binning;
  }

  // Used to get the bin edges of a given axis
  template <class UNIVERSE>
  std::vector<double> VariableHyperDBase<UNIVERSE>::GetBinVec(const int axis) const
  {
    return m_vars_vec[axis]->GetBinVec();
  }

  // Used to get the linearized reco bin edges
  template <class UNIVERSE>
  std::vector<double> VariableHyperDBase<UNIVERSE>::GetRecoBinVec() const
  {
    return m_lin_var->GetBinVec();
    // TODO: Right now just returns true binning
    // return m_lin_binning;
  }

  // Used to get the reco bin edges of a given axis
  template <class UNIVERSE>
  std::vector<double> VariableHyperDBase<UNIVERSE>::GetRecoBinVec(const int axis) const
  {
    return m_vars_vec[axis]->GetRecoBinVec();
  }

  // Print the linearized binning
  template <class UNIVERSE>
  void VariableHyperDBase<UNIVERSE>::PrintBinning() const
  {
    m_lin_var->PrintBinning();
  }

  // Print the binning of an axis
  template <class UNIVERSE>
  void VariableHyperDBase<UNIVERSE>::PrintBinning(const int axis) const
  {
    m_vars_vec[axis]->PrintBinning();
  }

  // Print the linearized binning
  template <class UNIVERSE>
  void VariableHyperDBase<UNIVERSE>::PrintRecoBinning() const
  {
    m_lin_var->PrintBinning();
    // TODO: right now just returns true binning
  }

  // Print the binning of an axis
  template <class UNIVERSE>
  void VariableHyperDBase<UNIVERSE>::PrintRecoBinning(const int axis) const
  {
    m_vars_vec[axis]->PrintRecoBinning();
  }

  // Return the hyperdim
  template <class UNIVERSE>
  PlotUtils::HyperDimLinearizer *VariableHyperDBase<UNIVERSE>::GetHyperDimLinearizer() const
  {
    return m_hyperdim;
  }

  // Return the phase space volume for a given linearized bin // TODO: Maybe this belongs to hyperdim?
  template <class UNIVERSE>
  double VariableHyperDBase<UNIVERSE>::GetBinVolume(int lin_bin) const
  {
    // Given the linearized bin number, get corresponding bin number in phase space coordinates
    double ps_bin_vol = 1;
    std::vector<int> ps_coords = m_hyperdim.GetValues(lin_bin);
    for (int i = 0; i < ps_coords.size(); i++)
    {
      std::int var_bin = ps_coords[i] std::vector<double> var_binning = m_vars_vec[i]->GetBinVec();
      double bin_width = var_binning[var_bin + 1] - var_binning[var_bin];
      if (bin_width <= 0)
      {
        std::cout << "VariableHyperDBase: GetBinVolumeVec(): WARNING, negative or zero binwidth" << std::endl;
      }
      ps_bin_vol *= bin_width;
    }
    return ps_bin_vol;
  }

  // TODO: Make Axis label vector getter.

  //==============================================================================
  // GetValues
  //==============================================================================

  template <class UNIVERSE>
  double VariableHyperDBase<UNIVERSE>::GetRecoValue(const UNIVERSE &universe,
                                                    const int idx1,
                                                    const int idx2) const
  {
    return m_lin_var->GetRecoValue(universe, idx1, idx2);
  }

  template <class UNIVERSE>
  double VariableHyperDBase<UNIVERSE>::GetRecoValue(const int axis, const UNIVERSE &universe,
                                                    const int idx1,
                                                    const int idx2) const
  {
    return m_vars_vec[axis]->GetRecoValue(universe, idx1, idx2);
  }

  template <class UNIVERSE>
  double VariableHyperDBase<UNIVERSE>::GetTrueValue(const UNIVERSE &universe,
                                                    const int idx1,
                                                    const int idx2) const
  {
    return m_lin_var->GetTrueValue(universe, idx1, idx2);
  }

  template <class UNIVERSE>
  double VariableHyperDBase<UNIVERSE>::GetTrueValue(const int axis, const UNIVERSE &universe,
                                                    const int idx1,
                                                    const int idx2) const
  {
    return m_vars_vec[axis]->GetTrueValue(universe, idx1, idx2);
  }


#endif  // VARIABLEHYPERDBASE_CXX
