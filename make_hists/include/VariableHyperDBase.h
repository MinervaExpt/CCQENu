#ifndef VARIABLEHYPERDBASE_H
#define VARIABLEHYPERDBASE_H

#include <memory>

#include "PlotUtils/VariableBase.h"
#include "utilities/HyperDimLinearizer.h"
// #include "PlotUtils/HyperDimLinearizer.h"

namespace PlotUtils {
enum EAnalysisType {k2D,k1D}; // Enum used for denoting "analysis type" of hyperdim. Right now only type 1 with fully linearized 1D available.

#ifndef __CINT__
template <class UNIVERSE>
class VariableHyperDBase {
public:
  //============================================================================
  // CTORS
  //============================================================================
  VariableHyperDBase();                                               // Defualt, recommended if using derived Variable class.
  VariableHyperDBase(const std::string name);                         // Just sets name, recommended if using derived Variable class
  VariableHyperDBase(const std::vector<VariableBase<UNIVERSE> *> &d); // Build from vector of input VariableBases, can get tricky if using derived Variable class
  VariableHyperDBase(const std::string name,                          // Build from vector of input VariableBases and set a name, can get tricky if using derived Variable class
                     const std::vector<VariableBase<UNIVERSE> *> &d);

public:
  //============================================================================
  // Setters/Getters
  //============================================================================
  std::string SetName(const std::string name);
  void SetAnalysisType(const EAnalysisType t2D_t1D); // Set hyperdim to project to 2D or 1D, 2D not configured yet -NHV 2/21/23
  void AddVariable(VariableBase<UNIVERSE> &var);     // Add variables individually and setup, recommended used with default or name only ctr

private:
  void Setup(const std::string i_name = "");         // Setup a variable based off current state of input variables (e.g after adding another variable), should only be used internally for now

public:
  std::string GetName() const;                      // Get Name of linearized variable
  std::string GetName(int axis) const;              // Get name of an input Variable on an axis in phase space
  std::string GetAxisLabel() const;                 // Get axis label for linearzed variable
  std::string GetAxisLabel(int axis) const;         // Get axis label of an input Variable on an axis in phase space
  std::vector<std::string> GetAxisLabelVec() const; // Get vector of all the axis labels in the phase space

  int GetNBins() const;                                         // Get number of linearized bins
  int GetNBins(int axis) const;                                 // Get number of bins of an input Variable on an axis in phase space
  std::vector<double> GetBinVec() const;                        // Get vector of linearized bin edges, should just be a list of indexes essentially
  std::vector<double> GetBinVec(int axis) const;                // Get vector of bin edges of an input Variable on an axis in phase space
  void PrintBinning() const;                                    // Print linearized binning
  void PrintBinning(int axis) const;                            // Print binning of an input Variable on an axis in phase space
  PlotUtils::HyperDimLinearizer* GetHyperDimLinearizer() const; // Returns the hyperdim
  double GetBinVolume(int lin_bin) const;                       // TODO: Maybe this belongs to HyperDimLinearizer?
  std::vector<int> GetUnderflow(int axis) const;                // Gives indexes of underflow bins TODO: Maybe belongs to HyperDimLinearizer?
  std::vector<int> GetOverflow(int axis) const;                 // Gives indexes of overflow bins TODO: Maybe belongs to HyperDimLinearizer?

  bool HasRecoBinning() const;                                      // Check if linearized space has reco binning (true if at least one input variable has reco binning, false otherwise)
  bool HasRecoBinning(int axis) const;                              // Check if an input Variable on an axis in phase space has reco binning
  int GetNRecoBins() const;                                         // Get number of linearized reco bins
  int GetNRecoBins(int axis) const;                                 // Get number of reco bins of an input Variable on an axis in phase space
  std::vector<double> GetRecoBinVec() const;                        // Same as before but reco bins
  std::vector<double> GetRecoBinVec(int axis) const;                // Same as before but reco bins
  void PrintRecoBinning() const;                                    // Same as before but reco bins
  void PrintRecoBinning(int axis) const;                            // Same as before but reco bins
  PlotUtils::HyperDimLinearizer* GetRecoHyperDimLinearizer() const; // Returns the reco bins hyperdim
  double GetRecoBinVolume(int lin_recobin) const;                   // TODO: Maybe this belongs to HyperDimLinearizer?
  std::vector<int> GetRecoUnderflow(int axis) const;                // Gives indexes of underflow reco bins TODO: Maybe belongs to HyperDimLinearizer?
  std::vector<int> GetRecoOverflow(int axis) const;                 // Gives indexes of overflow reco bins TODO: Maybe belongs to HyperDimLinearizer?
  //============================================================================
  // Get Value
  //============================================================================
  // Get value in bin space (plus 0.0001 offset so it's not exactly on a bin edge)
  double GetRecoValue(const UNIVERSE &universe, const int idx1 = -1,
                                   const int idx2 = -1) const;

  double GetTrueValue(const UNIVERSE &universe, const int idx1 = -1,
                                   const int idx2 = -1) const;

  // Get value of single variable in variable space
  double GetRecoValue(int axis, const UNIVERSE &universe, const int idx1 = -1,
                      const int idx2 = -1) const;

  double GetTrueValue(int axis, const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

  // Get value of all vars as a vec
  std::vector<double> GetRecoValueVec(const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

  std::vector<double> GetTrueValueVec(const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

protected:

  std::string m_lin_axis_label;

private:
  //============================================================================
  // Member Variables
  //============================================================================
  std::string m_name;                                              // Name of variable, should be var1name_var2name_var3name etc

  int m_dimension;                                                 // Number of axes/dimensions in variable phase space
  EAnalysisType m_analysis_type;                                   // This sets the "Analysis type" from Hyperdim: k2D (not configured yet) is type 0, k1D (default) is type 1
  bool m_has_reco_binning;                                         // Bool to note if there's separate reco binning or not

  PlotUtils::HyperDimLinearizer* m_hyperdim;                       // Member HyperDim
  PlotUtils::HyperDimLinearizer* m_reco_hyperdim;                  // Member HyperDim for reco bins

  std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> m_vars_vec; // Vector of component variables

  std::vector<std::vector<double>> m_vars_binnings;                // Vector of binnings each variable's binning in phase space
  std::vector<std::vector<double>> m_vars_reco_binnings;           // Vector of reco binnings each variable's binning in phase space

  std::vector<double> m_lin_binning;                               // Vector of bins in linearized bin space
  std::vector<double> m_lin_reco_binning;                          // Vector of reco bins in bin space, currently unused but can use a getter to get them

}; // Class def
#endif

}  // namespace PlotUtils

#include "VariableHyperDBase.cxx"

#endif  // VARIABLEHYPERDBASE_H
