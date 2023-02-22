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
VariableHyperDBase<UNIVERSE>::VariableHyperDBase()
{
  m_analysis_type = k1D; // default, 2D not set up yet
  // You will need to add variables, etc.
}

template <class UNIVERSE>
VariableHyperDBase<UNIVERSE>::VariableHyperDBase(std::string name)
{
  m_name = name;
  m_analysis_type = k1D; // default,  2D not set up yet
  // You will need to add variables, etc.
}

template <class UNIVERSE>
VariableHyperDBase<UNIVERSE>::VariableHyperDBase(const std::vector<VariableBase<UNIVERSE>*> &d)
{
  m_vars_vec = d;
  m_analysis_type = k1D;
  for(int i; i < d.size(); i++)
  {
    if (d[i]->HasRecoBinning()) m_has_reco_binning = true;
  }

  Setup();
}

template <class UNIVERSE>
VariableHyperDBase<UNIVERSE>::VariableHyperDBase(std::string name, const std::vector<VariableBase<UNIVERSE> *> &d)
{
  m_name = name;
  m_vars_vec = d;
  m_analysis_type = k1D;
  for (int i; i < d.size(); i++)
  {
    if (d[i]->HasRecoBinning()) m_has_reco_binning = true;
  }

  Setup(name);
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
    if(t2D_t1D==k2D)
    { 
      // Dan uses 2D/type 0, but most people will probably be fine with 1D/type 1. I don't plan on implimenting 2D anytime soon -NHV 2/22/23
      std::cout << "VariableHyperDBase: WARNING, type 0, 2D analysis not configured yet. Setting to type 1, 1D..." <<std::endl;
      m_analysis_type = k1D; 
    }
    std::cout << "VariableHyperDBase: WARNING you may be changing your analysis type." << std::endl;
    m_hyperdim = new HyperDimLinearizer(m_vars_binnings, m_analysis_type);
    
    //Now do reco
    if(m_has_reco_binning)
    {
      m_reco_hyperdim = new HyperDimLinearizer(m_vars_reco_binnings, m_analysis_type);
    }
  }

template <class UNIVERSE>
void VariableHyperDBase<UNIVERSE>::AddVariable(VariableBase<UNIVERSE> &var)
{
  // Be sure new variable is base class, not derived.
  VariableBase<UNIVERSE>* newvar = new VariableBase<UNIVERSE>(var);
  m_vars_vec.emplace_back(newvar);
  if(newvar->HasRecoBinning()) m_has_reco_binning = true;

  // Reset everything given new vars.
  Setup();
}

template <class UNIVERSE>
void VariableHyperDBase<UNIVERSE>::Setup(const std::string i_name)
{
  m_dimension = m_vars_vec.size();

  std::string name;
  std::string lin_axis_label;
  std::vector<std::vector<double>> vars_bins;
  int n_lin_bins = 1;

  std::vector<std::vector<double>> vars_reco_bins;
  int n_lin_reco_bins = 1;

  for (int i; i < m_dimension; i++)
  {
    name += m_vars_vec[i]->GetName();
    lin_axis_label += m_vars_vec[i]->GetAxisLabel();
    if (i < (m_dimension - 1))
    {
      name += "_";
      lin_axis_label += ", ";
    }
    // Make vector of binnings, count number of bins
    std::vector<double> var_binning = m_vars_vec[i]->GetBinVec();
    vars_bins.push_back(var_binning);
    // Need to add underflow and overflow bins (+2) and take out one from bin edges (-1) => var_binning.size()+1
    n_lin_bins *= (var_binning.size() + 1);

    // If recobinning is set, do this too
    if(m_has_reco_binning)
    {
      // Make vector of binnings, count number of bins
      std::vector<double> var_reco_binning = m_vars_vec[i]->GetRecoBinVec();
      vars_reco_bins.push_back(var_reco_binning);
      // Need to add underflow and overflow bins (+2) and take out one from bin edges (-1) => var_binning.size()+1
      n_lin_reco_bins *= (var_reco_binning.size() + 1);
    }
  }
  
  if(i_name.size()>0) m_name = i_name;
  else m_name = name;
  
  m_lin_axis_label = lin_axis_label;
  m_vars_binnings = vars_bins;

  // Initialize a hyperdim with that binning
  m_hyperdim = new HyperDimLinearizer(vars_bins, m_analysis_type);

  // Make a vector in bin space
  std::vector<double> lin_binning;
  for (int i = 0; i < n_lin_bins + 1; i++) lin_binning.push_back(i);
  m_lin_binning = lin_binning;

  // If you have reco binning, do that here too
  if(m_has_reco_binning)
  {
    m_vars_reco_binnings = vars_reco_bins;
    m_reco_hyperdim = new HyperDimLinearizer(vars_reco_bins, m_analysis_type);

    std::vector<double> lin_reco_binning;
    for (int i = 0; i < n_lin_reco_bins + 1; i++) lin_reco_binning.push_back(i);
    m_lin_reco_binning = lin_reco_binning;
  }
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
  for(const auto var:m_vars_vec)
  {
    axis_label_vec.push_back(var->GetAxisLabel());
  }
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

  return m_lin_reco_binning.size() - 1;
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

  return m_lin_reco_binning;
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
  if (!m_has_reco_binning)
  {
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
PlotUtils::HyperDimLinearizer* VariableHyperDBase<UNIVERSE>::GetRecoHyperDimLinearizer() const
{
  if(!m_has_reco_binning)
  {
    return m_hyperdim;
  }
  return m_reco_hyperdim;
}

// Return the phase space volume for a given linearized bin // TODO: Maybe this belongs to hyperdim?
template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetRecoBinVolume(int lin_bin) const
{
  if(!m_has_reco_binning)
  {
    return GetBinVolume(lin_bin);
  }
  // Given the linearized bin number, get corresponding bin number in phase space coordinates
  double ps_bin_vol = 1.;
  std::vector<int> ps_coords;
  if(!m_reco_hyperdim) ps_coords = GetRecoHyperDimLinearizer();
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

// Return value in linearized bin space, ie which bin event goes in
template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetRecoValue(const UNIVERSE &universe,
                                                  const int idx1,
                                                  const int idx2) const
{
  std::vector<double> val_vec;
  for (int i = 0; i < m_dimension; i++) 
  {
    val_vec.push_back(m_vars_vec[i]->GetRecoValue(universe, idx1, idx2));
  }
  if(!m_has_reco_binning)
  {
    return m_hyperdim->GetBin(val_vec).first+0.0001; // 0.0001 offset to so value isn't exactly on a bin edge and fillers can put it in that bin
  }
  else {
    return m_reco_hyperdim->GetBin(val_vec).first+0.0001; // Requires initialization of reco hyperdim TODO: automatically intialize this
  }
}

// Return value in linearized bin space, ie which bin event goes in
template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetTrueValue(const UNIVERSE &universe,
                                                  const int idx1,
                                                  const int idx2) const
{
  std::vector<double> val_vec;
  for (int i = 0; i < m_dimension; i++) 
  {
    val_vec.push_back(m_vars_vec[i]->GetTrueValue(universe, idx1, idx2));
  }
  return m_hyperdim->GetBin(val_vec).first + 0.0001; // 0.0001 offset to so fillers can put it in that bin
}

// Return values of a single component variable
template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetRecoValue(const int axis, 
                                                  const UNIVERSE& universe,
                                                  const int idx1,
                                                  const int idx2) const
{
  return m_vars_vec[axis]->GetRecoValue(universe, idx1, idx2);
}

// Return values of a single component variable
template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetTrueValue(const int axis,
                                                  const UNIVERSE &universe,
                                                  const int idx1,
                                                  const int idx2) const
{
  return m_vars_vec[axis]->GetTrueValue(universe, idx1, idx2);
}

// Return values of every component variable in a vector
template <class UNIVERSE>
std::vector<double> VariableHyperDBase<UNIVERSE>::GetRecoValueVec(const UNIVERSE& universe,
                                                                  const int idx1,
                                                                  const int idx2) const
{
  std::vector<double> value_vec;
  for (int i; i < m_dimension; i++) 
  {
    value_vec.push_back(m_vars_vec[i]->GetRecoValue(universe, idx1, idx2));
  }
  return value_vec;
}

// Return values of every component variable in a vector
template <class UNIVERSE>
std::vector<double> VariableHyperDBase<UNIVERSE>::GetTrueValueVec(const UNIVERSE &universe,
                                                                  const int idx1,
                                                                  const int idx2) const
{
  std::vector<double> value_vec;
  for (int i; i < m_dimension; i++)
  {
    value_vec.push_back(m_vars_vec[i]->GetTrueValue(universe, idx1, idx2));
  }
  return value_vec;
}


#endif  // VARIABLEHYPERDBASE_CXX
