#ifndef VARIABLEHYPERDBASE_CXX
#define VARIABLEHYPERDBASE_CXX

#include "VariableHyperDBase.h"
#include "utilities/HyperDimLinearizer.h"
// #include "PlotUtils/HyperDimLinearizer.h"

using namespace PlotUtils;

//==============================================================================
//
// Variable HyperD Base
//
//==============================================================================
//==============================================================================
// CTORS
//==============================================================================
// Default. Recommended if using a derived Variable class
template <class UNIVERSE>
VariableHyperDBase<UNIVERSE>::VariableHyperDBase() 
{
  m_analysis_type = k1D; // default, 2D not set up yet
  // You will need to add variables, etc.
}

// Default but set the name too. Recommended if using a derived Variable class
template <class UNIVERSE>
VariableHyperDBase<UNIVERSE>::VariableHyperDBase(std::string name)
{
  m_name = name;
  m_analysis_type = k1D; // default,  2D not set up yet
  // You will need to add variables, etc.
}

// Constructor with vector of input variables, will likely have issues if using derived Variable class
template <class UNIVERSE>
VariableHyperDBase<UNIVERSE>::VariableHyperDBase(const std::vector<VariableBase<UNIVERSE>*> &d)
{
  m_vars_vec = d;
  m_analysis_type = k1D;
  for (int i = 0;i < d.size(); i++)
  {
    if (d[i]->HasRecoBinning()) m_has_reco_binning = true;
  }

  Setup();
}

// Constructor with user designated name & vector of input variables, will likely have issues if using derived Variable class
template <class UNIVERSE>
VariableHyperDBase<UNIVERSE>::VariableHyperDBase(std::string name, const std::vector<VariableBase<UNIVERSE> *> &d)
{
  m_name = name;
  m_vars_vec = d;
  m_analysis_type = k1D;
  for (int i = 0; i < d.size(); i++)
  {
    if (d[i]->HasRecoBinning()) m_has_reco_binning = true;
  }

  Setup(name);
}

//==============================================================================
// Set
//==============================================================================

// Change the name
template <class UNIVERSE>
std::string VariableHyperDBase<UNIVERSE>::SetName(const std::string name)
{
return m_name = name;
}

// Change the analysis type. Right now it is fixed to 1D, or "type 1"
template <class UNIVERSE>
void VariableHyperDBase<UNIVERSE>::SetAnalysisType(const EAnalysisType t2D_t1D)
  {
    m_analysis_type = t2D_t1D;
    if (t2D_t1D==k2D)
    { 
      // Dan uses 2D/type 0, but most people will probably be fine with 1D/type 1. I don't plan on implimenting 2D anytime soon -NHV 2/22/23
      std::cout << "VariableHyperDBase: WARNING, type 0, 2D analysis not configured yet. Setting to type 1, 1D..." <<std::endl;
      m_analysis_type = k1D; 
    }
    std::cout << "VariableHyperDBase: WARNING you may be changing your analysis type." << std::endl;
    m_hyperdim = new HyperDimLinearizer(m_vars_binnings, m_analysis_type);
    
    //Now do reco
    if (m_has_reco_binning)
    {
      m_reco_hyperdim = new HyperDimLinearizer(m_vars_reco_binnings, m_analysis_type);
    }
  }

// Add another variable, useful if using default constructor and derived Variable class
template <class UNIVERSE>
void VariableHyperDBase<UNIVERSE>::AddVariable(VariableBase<UNIVERSE> &var)
{
  // If using derived, you'll need to get all the info you want out beforehand.
  m_vars_vec.emplace_back(new VariableBase<UNIVERSE>(var));

  if (var.HasRecoBinning()) m_has_reco_binning = true;

  // Reset everything given new vars. 
  Setup();
}

// Setup variable. This is private and should only be used internally for now.
template <class UNIVERSE>
void VariableHyperDBase<UNIVERSE>::Setup(const std::string i_name) // i_name defaults to "" and it will build a name for you instead
{
  m_dimension = m_vars_vec.size();

  std::string name;
  std::string lin_axis_label;

  std::vector<std::vector<double>> vars_bins;       // List of the bin edges lists for each variable to feed into hyperdim
  int n_lin_bins = 1;                               // Number of linearized bins
  std::vector<std::vector<double>> vars_reco_bins;  // Same for reco if you have separate reco binning
  int n_lin_reco_bins = 1;

  for (int i = 0; i < m_dimension; i++)
  {
    // Make the name and axis label
    name += m_vars_vec[i]->GetName();
    std::cout << name << std::endl;
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

    // If recobinning is set (should happen at initialization or setup), do this too
    if (m_has_reco_binning)
    {
      // Make vector of binnings, count number of bins
      std::vector<double> var_reco_binning = m_vars_vec[i]->GetRecoBinVec();
      vars_reco_bins.push_back(var_reco_binning);
      // Add underflow and overflow bins (+2) and take out one from bin edges (-1) => var_binning.size()+1
      n_lin_reco_bins *= (var_reco_binning.size() + 1);
    }
  }
  
  // If there's an input name, it will use that one, otherwise it'll use the one it just made
  if (i_name.size()>0) m_name = i_name;
  else m_name = name;
  // Store axis label, list of input binnings 
  m_lin_axis_label = lin_axis_label;
  m_vars_binnings = vars_bins;

  // Initialize a hyperdim with that binning
  m_hyperdim = new HyperDimLinearizer(vars_bins, m_analysis_type);

  // Make a bin vector in linearized bin index space
  std::vector<double> lin_binning;
  for (int i = 0; i < n_lin_bins + 1; i++) lin_binning.push_back(i);
  m_lin_binning = lin_binning;

  // If you have reco binning, do that here too
  if (m_has_reco_binning)
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

// Get name of linearized variable
template <class UNIVERSE>
std::string VariableHyperDBase<UNIVERSE>::GetName() const
{
  return m_name;
}

// Get name of a component variable
template <class UNIVERSE>
std::string VariableHyperDBase<UNIVERSE>::GetName(int axis) const
{
  return m_vars_vec[axis]->GetName();
}

// Get axis label of linearized variable
template <class UNIVERSE>
std::string VariableHyperDBase<UNIVERSE>::GetAxisLabel() const
{
  return m_lin_axis_label;
}

// Get axis label of a component variable
template <class UNIVERSE>
std::string VariableHyperDBase<UNIVERSE>::GetAxisLabel(int axis) const
{
  return m_vars_vec[axis]->GetAxisLabel();
}

// Get a vector of the axis labels of all component variables
template <class UNIVERSE>
std::vector<std::string> VariableHyperDBase<UNIVERSE>::GetAxisLabelVec() const
{
  std::vector<std::string> axis_label_vec = {};    
  for (const auto var:m_vars_vec)
  {
    axis_label_vec.push_back(var->GetAxisLabel());
  }
  return axis_label_vec;
}

// Get the number of linearized bins
template <class UNIVERSE>
int VariableHyperDBase<UNIVERSE>::GetNBins() const
{
  return m_lin_binning.size()-1;
  // Linearized binning has under/overflow bins in phase space spread throughout, so this number may seem bigger than expected.
}

// Get the number of bins in a given axis
template <class UNIVERSE>
int VariableHyperDBase<UNIVERSE>::GetNBins(int axis) const
{
  return m_vars_vec[axis]->GetNBins();
}

// Get the linearized bin edges
template <class UNIVERSE>
std::vector<double> VariableHyperDBase<UNIVERSE>::GetBinVec() const
{
  return m_lin_binning;
}

// Get the bin edges of a given axis
template <class UNIVERSE>
std::vector<double> VariableHyperDBase<UNIVERSE>::GetBinVec(int axis) const
{
  return m_vars_vec[axis]->GetBinVec();
}

// Print linearized binning, should just be list of indexes
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

// Get the hyperdim
template <class UNIVERSE>
PlotUtils::HyperDimLinearizer *VariableHyperDBase<UNIVERSE>::GetHyperDimLinearizer() const
{
  return m_hyperdim;
}

// Get the phase space volume for a given linearized bin // TODO: Maybe this belongs to hyperdim?
template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetBinVolume(int lin_bin) const
{
  double ps_bin_vol = 1.;
  // Given the linearized bin number, get corresponding bin index in phase space coordinates
  std::vector<int> ps_coords = m_hyperdim->GetValues(lin_bin);
  for (int i = 0; i < ps_coords.size(); i++)
  {
    int var_bin = ps_coords[i];
    // Get the binning for that axis
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

template <class UNIVERSE>
std::vector<int> PlotUtils::VariableHyperDBase<UNIVERSE>::GetUnderflow(int axis) const
{
  // TODO
  std::cout << "WARNING: VariableHyperDBase::GetUnderflow() not set up yet... " << std::endl;
  return std::vector<int>();
}

template <class UNIVERSE>
std::vector<int> PlotUtils::VariableHyperDBase<UNIVERSE>::GetOverflow(int axis) const
{
  // TODO
  std::cout << "WARNING: VariableHyperDBase::GetOverflow() not set up yet... " << std::endl;
  return std::vector<int>();
}

//==============================================================================
// Reco Getters
//==============================================================================

// Check if there's reco binning set. If set to false reco getters will return true things
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
  if (!m_has_reco_binning) return m_lin_binning.size() - 1;

  return m_lin_reco_binning.size() - 1;
  // Linearized binning has under/overflow bins in phase space spread throughout, so this number may seem bigger than expected.
}

template <class UNIVERSE>
int VariableHyperDBase<UNIVERSE>::GetNRecoBins(int axis) const
{
  return m_vars_vec[axis]->GetNRecoBins(); // If variable has no reco binning, will return truth instead
}

// Get the linearized reco bin edges
template <class UNIVERSE>
std::vector<double> VariableHyperDBase<UNIVERSE>::GetRecoBinVec() const
{
  if (!m_has_reco_binning) return m_lin_binning;

  return m_lin_reco_binning;
}

// Get the reco bin edges of a given axis
template <class UNIVERSE>
std::vector<double> VariableHyperDBase<UNIVERSE>::GetRecoBinVec(int axis) const
{
  return m_vars_vec[axis]->GetRecoBinVec(); // If variable has no reco binning, will return truth instead
}

// Print linearized reco binning, should just be list of indexes
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

// Print the reco binning of an axis
template <class UNIVERSE>
void VariableHyperDBase<UNIVERSE>::PrintRecoBinning(int axis) const
{
  m_vars_vec[axis]->PrintRecoBinning(); // If variable has no reco binning, will return truth instead
}

// Get the reco hyperdim
template <class UNIVERSE>
PlotUtils::HyperDimLinearizer* VariableHyperDBase<UNIVERSE>::GetRecoHyperDimLinearizer() const
{
  if (!m_has_reco_binning)
  {
    return m_hyperdim;
  }
  return m_reco_hyperdim;
}

// Get the phase space volume for a given linearized reco bin // TODO: Maybe this belongs to hyperdim?
template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetRecoBinVolume(int lin_bin) const
{
  if (!m_has_reco_binning) // If there's no reco binning, just return truth instead
  {
    return GetBinVolume(lin_bin);
  }
  // Given the linearized bin number, get corresponding bin number in phase space coordinates
  double ps_bin_vol = 1.;
  std::vector<int> ps_coords;
  if (!m_reco_hyperdim) ps_coords = GetRecoHyperDimLinearizer();
  else{ps_coords = m_reco_hyperdim->GetValues(lin_bin);} 
  
  for (int i = 0; i < ps_coords.size(); i++)
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

template <class UNIVERSE>
std::vector<int> PlotUtils::VariableHyperDBase<UNIVERSE>::GetRecoUnderflow(int axis) const
{
  // TODO: Get a vector of indices in of bins linearized space that are underflow bins in phase space
  std::cout << "WARNING: VariableHyperDBase::GetRecoUnderflow() not set up yet... " << std::endl;
  return std::vector<int>();
}

template <class UNIVERSE>
std::vector<int> PlotUtils::VariableHyperDBase<UNIVERSE>::GetRecoOverflow(int axis) const
{
  // TODO: Get a vector of indices in of bins linearized space that are overflow bins in phase space
  std::cout << "WARNING: VariableHyperDBase::GetRecoOverflow() not set up yet... " << std::endl;
  return std::vector<int>();
}

//==============================================================================
// GetValues
//==============================================================================

// Return bin index value in linearized bin space, ie which bin an event goes in
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
  if (!m_has_reco_binning)
  {
    return (m_hyperdim->GetBin(val_vec).first) + 0.0001; // 0.0001 offset to so value isn't exactly on a bin edge and fillers can put it in that bin
  }
  else {
    return (m_reco_hyperdim->GetBin(val_vec).first) + 0.0001; // If there's reco binning, use that hyperdim
  }
}

// Return bin index value in linearized bin space, ie which an bin event goes in
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
  return (m_hyperdim->GetBin(val_vec).first) + 0.0001; // 0.0001 offset to so fillers can put it in that bin
}

// Return phase space value of a single component variable
template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetRecoValue(const int axis, 
                                                  const UNIVERSE& universe,
                                                  const int idx1,
                                                  const int idx2) const
{
  return m_vars_vec[axis]->GetRecoValue(universe, idx1, idx2);
}

// Return phase space value of a single component variable
template <class UNIVERSE>
double VariableHyperDBase<UNIVERSE>::GetTrueValue(const int axis,
                                                  const UNIVERSE &universe,
                                                  const int idx1,
                                                  const int idx2) const
{
  return m_vars_vec[axis]->GetTrueValue(universe, idx1, idx2);
}

// Return phase space values of every component variable as a vector
template <class UNIVERSE>
std::vector<double> VariableHyperDBase<UNIVERSE>::GetRecoValueVec(const UNIVERSE& universe,
                                                                  const int idx1,
                                                                  const int idx2) const
{
  std::vector<double> value_vec;
  for (int i = 0; i < m_dimension; i++) 
  {
    value_vec.push_back(m_vars_vec[i]->GetRecoValue(universe, idx1, idx2));
  }
  return value_vec;
}

// Return phase space values of every component variable as a vector
template <class UNIVERSE>
std::vector<double> VariableHyperDBase<UNIVERSE>::GetTrueValueVec(const UNIVERSE &universe,
                                                                  const int idx1,
                                                                  const int idx2) const
{
  std::vector<double> value_vec;
  for (int i = 0;i < m_dimension; i++)
  {
    value_vec.push_back(m_vars_vec[i]->GetTrueValue(universe, idx1, idx2));
  }
  return value_vec;
}


#endif  // VARIABLEHYPERDBASE_CXX
