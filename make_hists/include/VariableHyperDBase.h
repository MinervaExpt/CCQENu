#ifndef VARIABLEHYPERDBASE_H
#define VARIABLEHYPERDBASE_H

#include <memory>

#include "PlotUtils/VariableBase.h"
#include "PlotUtils/HyperDimLinearizer.h"

namespace PlotUtils {
enum EAnalysisType {k2D,k1D};

#ifndef __CINT__
// template <class UNIVERSE>
template <class UNIVERSE>
class VariableHyperDBase {
 public:
  //============================================================================
  // CTORS
  //============================================================================
   VariableHyperDBase(const std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> &d,
                      EAnalysisType t2D_t1D = k1D);
   VariableHyperDBase(const std::string name,
                      const std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> &d,
                      EAnalysisType t2D_t1D = k1D);

 public:
  //============================================================================
  // Setters/Getters
  //============================================================================
  // TODO: reco binning!
  std::string SetName(const std::string name);
  
  void SetAnalysisType(const EAnalysisType t2D_t1D); // Set hyperdim to project to 2D or 1D

  std::string GetName() const; // Get Name of linearized variable
  std::string GetName(int axis) const; // Get name of variable on an axis
  std::string GetAxisLabel() const; // Get axis label for linearzed variable
  std::string GetAxisLabel(int axis) const; // Get axis label for one variable
  std::vector<std::string> GetAxisLabelVec() const; // Get vector of all the variables in the phase space

  int GetNBins() const; // Get number of linearized bins TODO: right now just true binning
  int GetNBins(int axis) const; // Get number of bins on an axis
  std::vector<double> GetBinVec() const; // Get vector of linearized bin edges, should just be a list of indexes essentially
  std::vector<double> GetBinVec(int axis) const; // Get vector of bin edges for an input variable
  void PrintBinning() const; // Print linearized binning
  void PrintBinning(int axis) const; // Print binning for one input variable
  PlotUtils::HyperDimLinearizer* GetHyperDimLinearizer() const; // Returns the hyperdim
  double GetBinVolume(int lin_bin) const; // TODO: Maybe this belongs to hyperdimlinearizer?

  bool HasRecoBinning() const;         // Check if linearized space has reco binning (yes, if at least one input variable has reco binning, false otherwise)
  bool HasRecoBinning(int axis) const; // Check if given axis has reco binning
  int GetNRecoBins() const; // Get number of linearized reco bins
  int GetNRecoBins(int axis) const; // Get number of reco bins for a variable 
  std::vector<double> GetRecoBinVec() const;  // Same but reco bins TODO: right now just true binning
  std::vector<double> GetRecoBinVec(int axis) const; // Same but reco bins
  void PrintRecoBinning() const; // Same but reco bins TODO: right now just true binning
  void PrintRecoBinning(int axis) const; // Same but reco bins
  PlotUtils::HyperDimLinearizer* GetRecoHyperDimLinearizer();// const; // Returns the reco bins hyperdim
  double GetRecoBinVolume(int lin_recobin) const;                   // TODO: Maybe this belongs to hyperdimlinearizer?
  
  PlotUtils::VariableBase<UNIVERSE> GetLinVariable() const; // Maybe not possible/necessary

  //============================================================================
  // Get Value
  //============================================================================
  // Get value of single variable
  double GetRecoValue(int axis, const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

  double GetTrueValue(int axis, const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

  // Get value of all vars as a vec
  std::vector<double> GetRecoValue(const UNIVERSE& universe, const int idx1 = -1,
                      const int idx2 = -1) const;

  std::vector<double> GetTrueValue(const UNIVERSE& universe, const int idx1 = -1,
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

   PlotUtils::HyperDimLinearizer *m_hyperdim;                       // Member HyperDim
   PlotUtils::HyperDimLinearizer *m_reco_hyperdim;                  // Member HyperDim for reco bins

   std::unique_ptr<VariableBase<UNIVERSE>> m_lin_var;               // Linearized variable TODO: is this viable? Need input Values functions

   std::vector<std::unique_ptr<VariableBase<UNIVERSE>>> m_vars_vec; // Vector of component variables

   std::vector<std::vector<double>> m_vars_binnings;                // Vector of binnings each variable's binning in phase space
   std::vector<std::vector<double>> m_vars_reco_binnings;           // Vector of reco binnings each variable's binning in phase space

   std::vector<double> m_lin_binning;                               // Vector of bins in linearized bin space
   std::vector<double> m_lin_reco_binning;                          // Vector of reco bins in bin space, currently unused but can use a getter to get them

   VariableHyperDBase();                                            // off-limits default constructor
};
#endif

}  // namespace PlotUtils

#include "VariableHyperDBase.cxx"

#endif  // VARIABLEHYPERDBASE_H
