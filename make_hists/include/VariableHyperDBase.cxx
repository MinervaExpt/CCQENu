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
VariableHyperDBase<UNIVERSE>::VariableHyperDBase(std::string name, const std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> &d, EAnalysisType t2D_t1D)
{
  m_name = name;
  m_vars_vec = d;
  m_dimension = d.size();

  std::string lin_axis_label;
  // std::vector<std::string> axis_label_vec; TODO: needed?

  std::vector<std::vector<double>> vars_bins;
  int n_lin_bins = 1;

  for (int i = 0; i < d.size(); i++)
  {
    // Make name for variable, axis
    lin_axis_label += d[i].GetAxisLabel();
    if (i < (d.size() - 1))
    {
      lin_axis_label += ", ";
    }

    // Make vector of binnings, count number of bins
    std::vector<double> var_binning = d[i]->GetBinVec();
    vars_bins.push_back(var_binning);
    n_lin_bins *= (var_binning.size() + 1); // includes under/over flow (total bins = size of bin edges - 1 (high edge) + 2 (under/overflow))
   
    if (d[i]->HasRecoBinning()) m_has_reco_binning = true; // if any input vars has reco binning, it will set this off
  }

  m_lin_axis_label = lin_axis_label;
  m_vars_binnings = vars_bins;
  m_analysis_type = t2D_t1D; // Default analysis type for now

  // Initialize a hyperdim with that binning
  m_hyperdim = new HyperDimLinearizer(vars_bins, m_analysis_type);

  // Make a vector in bin space
  std::vector<double> lin_binning;
  for (int i = 0; i < n_lin_bins+1; i++) lin_binning.push_back(i);
  m_lin_binning = lin_binning;

  // Make the linearized variable TODO: Need to figure out how to work out Get Values methods will work here...
  // m_lin_var = new VariableBase<UNIVERSE>(m_name, m_lin_axis_label, m_lin_binning);
}

template <class UNIVERSE>
VariableHyperDBase<UNIVERSE>::VariableHyperDBase(const std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> &d, EAnalysisType t2D_t1D) 
{
  m_vars_vec = d;
  m_dimension = d.size();

  std::string name;
  std::string lin_axis_label;
  // std::vector<std::string> axis_label_vec;

  std::vector<std::vector<double>> vars_bins;
  int n_lin_bins = 1;

  for (int i = 0; i < d.size(); i++)
  {
    // Make name for variable, axis
    name += d[i].GetName();
    lin_axis_label += d[i].GetAxisLabel();
    if (i < (d.size() - 1))
    {
      name += "_";
      lin_axis_label += ", ";
    }

    // Make vector of binnings, count number of bins
    std::vector<double> var_binning = d[i]->GetBinVec();
    vars_bins.push_back(var_binning);
    // Need to add underflow and overflow bins (+2) and take out one from bin edges (-1) => var_binning.size()+1
    n_lin_bins *= (var_binning.size() + 1);

    if (d[i]->HasRecoBinning()) m_has_reco_binning = true; // if any input vars has reco binning, it will set this off
  }

  m_name = name;
  m_lin_axis_label = lin_axis_label;
  m_vars_binnings = vars_bins;
  m_analysis_type = t2D_t1D;

  // Initialize a hyperdim with that binning
  m_hyperdim = new HyperDimLinearizer(vars_bins, m_analysis_type);

  // Make a binning in bin space
  std::vector<double> lin_binning;
  for (int i = 0; i < n_lin_bins; i++) lin_binning.push_back(i);
  m_lin_binning = lin_binning;

  // Make the linearized variable TODO: Need to figure out how to work out Get Values methods will work here...
  // m_lin_var = new VariableBase<UNIVERSE>(m_name, m_lin_axis_label, m_lin_binning);
}

  //==============================================================================
  // Set
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
    if(t2D_t1D==k2D){ //TODO: Add this, although general use 1D is usually fine.
      std::cout << "VariableHyperDBase: WARNING, type 0, 2D analysis not configured yet. Setting to type 1, 1D..." <<std::endl;
      m_analysis_type = k1D; 
    }
    std::cout << "VariableHyperDBase: WARNING you may be changing your analysis type." << std::endl;
    m_hyperdim = new HyperDimLinearizer(m_vars_binnings, m_analysis_type);
    
    // TODO: Now do reco
    // if(m_has_reco_binning){
    //   std::vector<double> vars_reco_bins;
    //   for (const auto var : m_vars_vec)
    //   {
    //     vars_reco_bins.push_back(var->GetRecoBinVec());
    //   }
    //   m_vars_reco_binnings = vars_reco_bins;
    //   m_reco_hyperdim = new HyperDimLinearizer(m_vars_reco_binnings, m_analysis_type);
    // }
  }

  //==============================================================================
  // Gets (truth binning, reco further down)
  //==============================================================================

  template <class UNIVERSE>
  std::string VariableHyperDBase<UNIVERSE>::GetName() const
  {
    return m_name;
  }

  template <class UNIVERSE>
  std::string VariableHyperDBase<UNIVERSE>::GetName(int axis) const
  {
    return m_vars_vec[axis]->GetName();
  }

  template <class UNIVERSE>
  std::string VariableHyperDBase<UNIVERSE>::GetAxisLabel() const
  {
    return m_lin_axis_label;
  }

  template <class UNIVERSE>
  std::string VariableHyperDBase<UNIVERSE>::GetAxisLabel(int axis) const
  {
    return m_vars_vec[axis]->GetAxisLabel();
  }

  template <class UNIVERSE>
  std::vector<std::string> VariableHyperDBase<UNIVERSE>::GetAxisLabelVec() const
  {
    std::vector<std::string> axis_label_vec = {};    
    for(const auto var:m_vars_vec){ axis_label_vec.push_back(var->GetAxisLabel());}
    return axis_label_vec;
  }

  // Used to get the number of linearized bins
  template <class UNIVERSE>
  int VariableHyperDBase<UNIVERSE>::GetNBins() const
  {
    return m_lin_binning.size()-1;
  }

  // Used to get the number of bins in a given axis
  template <class UNIVERSE>
  int VariableHyperDBase<UNIVERSE>::GetNBins(int axis) const
  {
    return m_vars_vec[axis]->GetNBins();
  }

  // Used to get the linearized bin edges
  template <class UNIVERSE>
  std::vector<double> VariableHyperDBase<UNIVERSE>::GetBinVec() const
  {
    return m_lin_binning;
  }

  // Used to get the bin edges of a given axis
  template <class UNIVERSE>
  std::vector<double> VariableHyperDBase<UNIVERSE>::GetBinVec(int axis) const
  {
    return m_vars_vec[axis]->GetBinVec();
  }

  // Print the linearized binning
  template <class UNIVERSE>
  void VariableHyperDBase<UNIVERSE>::PrintBinning() const
  {
    std::cout << GetName() << " binning: ";
    for (const auto b : m_lin_binning) std::cout << b << " ";
    std::cout << "\n";
  }

  // Print the binning of an axis
  template <class UNIVERSE>
  void VariableHyperDBase<UNIVERSE>::PrintBinning(int axis) const
  {
    m_vars_vec[axis]->PrintBinning();
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
    std::vector<int> ps_coords = m_hyperdim->GetValues(lin_bin);
    for (int i = 1; i < ps_coords.size()+1; i++)
    {
    int var_bin = ps_coords[i];
    std::vector<double> var_binning = m_vars_vec[i]->GetBinVec();
    double bin_width = var_binning[var_bin] - var_binning[var_bin-1];
    if (bin_width < 0)
      std::cout << "VariableHyperDBase: WARNING, negative binwidth, will affect bin volume" << std::endl;
    else if (bin_width == 0)
      std::cout << "VariableHyperDBase: WARNING, 0 binwidth, will affect bin volume" << std::endl;
    ps_bin_vol *= bin_width;
    }
    return ps_bin_vol;
  }
  
  // TODO: This might not actually be feasible, since we don't have seperate value functions that variable base wants
  // TODO: Figure out the lin variable. Not sure about the Get Value methods
  // template <class UNIVERSE>
  // PlotUtils::VariableBase<UNIVERSE> VariableHyperDBase<UNIVERSE>::GetLinVariable() const
  // {
  //   if (!m_lin_var)
  //     m_lin_var = new VariableBase<UNIVERSE>(m_name, m_lin_axis_label, m_lin_binning);
  //   return m_lin_var;
  // }

  //==============================================================================
  // Reco Getters
  //==============================================================================

  // TODO: Need to add HasRecoBining to header defs
  template <class UNIVERSE>
  bool VariableHyperDBase<UNIVERSE>::HasRecoBinning() const
  {
    return m_has_reco_binning;
  }

  template <class UNIVERSE>
  bool VariableHyperDBase<UNIVERSE>::HasRecoBinning(int axis) const
  {
    return m_vars_vec[axis]->HasRecoBinning();
  }

  template <class UNIVERSE>
  int VariableHyperDBase<UNIVERSE>::GetNRecoBins() const
  {
    if(!m_has_reco_binning) return m_lin_binning.size() - 1;
    
    int n_lin_bins = 1;
    // for (const auto var : m_vars_vec)
    // {
    // n_lin_bins *= (var->GetNRecoBins() + 1); // This should return reco binning if var has it, true binning if it doesn't
    // }
    for (int i = 0; i < m_dimension; i++)
    {
      n_lin_bins *= (m_vars_vec[i]->GetNRecoBins() + 1); // This should return reco binning if var has it, true binning if it doesn't
    }
    return n_lin_bins;
  }

  template <class UNIVERSE>
  int VariableHyperDBase<UNIVERSE>::GetNRecoBins(int axis) const
  {
    return m_vars_vec[axis]->GetNRecoBins();
    // Returns the reco binning for one of the input variables
  }

  // Used to get the linearized reco bin edges
  template <class UNIVERSE>
  std::vector<double> VariableHyperDBase<UNIVERSE>::GetRecoBinVec() const
  {
    if(!m_has_reco_binning) return m_lin_binning;

    std::vector<double> lin_reco_binning;
    for (int i = 0; i < GetNRecoBins() + 1; i++) lin_reco_binning.push_back(double(i));
    // m_lin_reco_binning = lin_reco_binning;
    return lin_reco_binning;
    // return m_lin_reco_binning;
    // return m_lin_binning;
  }

  // Used to get the reco bin edges of a given axis
  template <class UNIVERSE>
  std::vector<double> VariableHyperDBase<UNIVERSE>::GetRecoBinVec(int axis) const
  {
    return m_vars_vec[axis]->GetRecoBinVec();
  }

  // Print the linearized binning
  template <class UNIVERSE>
  void VariableHyperDBase<UNIVERSE>::PrintRecoBinning() const
  {
    if (!m_has_reco_binning){
      std::cout << GetName() << " reco binning same as true: ";
      for (const auto b : m_lin_binning) {std::cout << b << " ";}
      std::cout << "\n";
    }
    else {
      std::cout << GetName() << " reco binning: ";
      for (const auto b : GetRecoBinVec()) {std::cout << b << " ";}
      std::cout << "\n";
    }
  }

  // Print the binning of an axis
  template <class UNIVERSE>
  void VariableHyperDBase<UNIVERSE>::PrintRecoBinning(int axis) const
  {
    m_vars_vec[axis]->PrintRecoBinning();
  }

  // TODO: separate initialization from Getter
  // Return the hyperdim
  template <class UNIVERSE>
  PlotUtils::HyperDimLinearizer* VariableHyperDBase<UNIVERSE>::GetRecoHyperDimLinearizer()
  {
    if(!m_has_reco_binning){
      return m_hyperdim;
    }

    std::vector<std::vector<double>> vars_reco_bins;
    // for (const auto var : m_vars_vec)
    // {
    //   std::vector<double> var_binning = var->GetRecoBinVec();
    //   vars_reco_bins.push_back(var_binning);
    // }
    for (int i = 0; i < m_dimension; i++)
    {
      std::vector<double> var_binning = m_vars_vec[i]->GetRecoBinVec();
      vars_reco_bins.push_back(var_binning);
    }
    m_vars_reco_binnings = vars_reco_bins;
    m_reco_hyperdim = new HyperDimLinearizer(m_vars_reco_binnings, m_analysis_type);
    return m_reco_hyperdim;
  }

  // Return the phase space volume for a given linearized bin // TODO: Maybe this belongs to hyperdim?
  template <class UNIVERSE>
  double VariableHyperDBase<UNIVERSE>::GetRecoBinVolume(int lin_bin) const
  {
    if(!m_has_reco_binning){
      return GetBinVolume(lin_bin);
    }
    // Given the linearized bin number, get corresponding bin number in phase space coordinates
    double ps_bin_vol = 1.;
    std::vector<int> ps_coords;
    if(!m_reco_hyperdim){ps_coords = GetRecoHyperDimLinearizer();}
    else{ps_coords = m_reco_hyperdim->GetValues(lin_bin);} // Not good to do a member variable without making sure it's initialized first.
    
    for (int i = 1; i < ps_coords.size()+1; i++)
    {
      int var_bin = ps_coords[i];
      std::vector<double> var_binning = m_vars_vec[i]->GetRecoBinVec();
      double bin_width = var_binning[var_bin] - var_binning[var_bin-1];

      if (bin_width < 0)
        std::cout << "VariableHyperDBase: WARNING, negative binwidth, will affect bin volume" << std::endl;
      else if (bin_width == 0)
        std::cout << "VariableHyperDBase: WARNING, 0 binwidth, will affect bin volume" << std::endl;

      ps_bin_vol *= bin_width;
    }
    return ps_bin_vol;
  }


  //==============================================================================
  // GetValues
  //==============================================================================

  // These will return values in bin space
  template <class UNIVERSE>
  double VariableHyperDBase<UNIVERSE>::GetRecoValue(const UNIVERSE &universe,
                                                       const int idx1,
                                                       const int idx2) const
  {
    std::vector<double> val_vec;
    for (auto var:m_vars_vec) {val_vec.push_back(var->GetRecoValue(universe, idx1, idx2));}
    if(!m_has_reco_binning){
      return m_hyperdim->GetBin(val_vec).first+0.0001; // 0.0001 offset to so fillers can put it in that bin
    }
    else {
      return m_reco_hyperdim->GetBin(val_vec).first+0.0001; // Requires initialization of reco hyperdim TODO: automatically intialize this
    }
  }

  template <class UNIVERSE>
  double VariableHyperDBase<UNIVERSE>::GetTrueValue(const UNIVERSE &universe,
                                                       const int idx1,
                                                       const int idx2) const
  {
    std::vector<double> val_vec;
    for (auto var : m_vars_vec){val_vec.push_back(var->GetRecoValue(universe, idx1, idx2));}
    return m_hyperdim->GetBin(val_vec).first + 0.0001; // 0.0001 offset to so fillers can put it in that bin
  }

  // These return values of single vars 
  template <class UNIVERSE>
  double VariableHyperDBase<UNIVERSE>::GetRecoValue(const int axis, const UNIVERSE& universe,
                                                    const int idx1,
                                                    const int idx2) const
  {
    return m_vars_vec[axis]->GetRecoValue(universe, idx1, idx2);
  }

  template <class UNIVERSE>
  double VariableHyperDBase<UNIVERSE>::GetTrueValue(const int axis, const UNIVERSE& universe,
                                                    const int idx1,
                                                    const int idx2) const
  {
    return m_vars_vec[axis]->GetTrueValue(universe, idx1, idx2);
  }

  // These return values of all vars in one vector
  template <class UNIVERSE>
  std::vector<double> VariableHyperDBase<UNIVERSE>::GetRecoValueVec(const UNIVERSE& universe,
                                                    const int idx1,
                                                    const int idx2) const
  {
    std::vector<double> value_vec;
    for(auto var : m_vars_vec)
    {
      value_vec.push_back(var->GetRecoValue(universe, idx1, idx2));
    }
    return value_vec;
  }

  template <class UNIVERSE>
  std::vector<double> VariableHyperDBase<UNIVERSE>::GetTrueValueVec(const UNIVERSE& universe,
                                                                 const int idx1,
                                                                 const int idx2) const
  {
    std::vector<double> value_vec;
    for (auto var : m_vars_vec)
    {
      value_vec.push_back(var->GetTrueValue(universe, idx1, idx2));
    }
    return value_vec;
  }


#endif  // VARIABLEHYPERDBASE_CXX
