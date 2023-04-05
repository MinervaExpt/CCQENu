//
//  HistHyperDWrapperMap.h
//
//
// Created by Heidi Schellman (research) on 11/4/16.
//
// Modified for HyperDim by Noah Vaughan on 2/10/23

// make a map of HistWrappers (1D or 2D) with the same name title and binning.

#ifndef HistHyperDWrapperMap_h
#define HistHyperDWrapperMap_h

//#define HSTDBG
// TODO: Do I need to amek a Hyperd HistWrapper?
#include "PlotUtils/HistWrapper.h"
#include "PlotUtils/Hist2DWrapper.h"
#include "PlotUtils/VariableHyperDBase.h"

#include <map>
#include <iostream>
#include <string>
#include <vector>


namespace PlotUtils{
// enum EAnalysisType {k2D, k1D, k2D_lite, k1D_lite}
template <typename T>

class HistHyperDWrapperMap:public T {

private:
  // TODO: Do I need to make a HyperD HistWrapper?
  std::map<const std::string, HistWrapper<T> > m_hists;
  std::map<const std::string, bool> m_has_hist;
  std::map<const std::string, Hist2DWrapper<T>> m_hists_2d;
  std::map<const std::string, bool> m_has_hist_2d;

  std::map< std::string, std::vector<T*> > m_univs;
  std::string m_name = "NULL";
  std::string m_title = "NULL";
  EAnalysisType m_analysis_type = k1D;

  bool m_fixedbins;

  int m_n_linx_bins = 0;                // Number of linearized truth bins
  std::vector<double> m_linx_bins;      // Vectors of linearized bins, this should just be a list of indexes
  double m_linx_min = 0.0;
  double m_linx_max = 0.0;

  int m_n_y_bins = 0;                   // Number of truth y bins if doing 2D type 0 analysis
  std::vector<double> m_y_bins;         // Vectors of y bins if doing 2D type 0 analysis
  double m_y_min = 0.0;
  double m_y_max = 0.0;

  std::map<const T*, int> m_decoder;
  std::map<std::string, std::vector<T*>> m_universes; // if you are using a vector need to add that <-Huh?? -NHV
  std::vector<std::string> m_tags;


public:

  std::map<const T *, int> UniverseDecoder(const std::map<std::string, std::vector<T *>> univs) const
  {
    std::map<const T *, int> decoder;
    for (auto univ : univs)
    {
      std::string name = univ.first;
      std::vector<T *> pointers = univ.second;
      for (int i = 0; i < pointers.size(); i++)
      {
        decoder[pointers[i]] = i;
      }
    }
    return decoder;
  }
  
  // Default Constructor
  HistHyperDWrapperMap(){};

  //===========================================================================
  // Constuctors for 1D Type 1 analyses
  //===========================================================================
  inline HistHyperDWrapperMap(const std::string name, const std::string title,
                              const Int_t n_linx_bins, const double linx_min, const double linx_max,
                              std::map<std::string, std::vector<T *>> univs, const std::vector<std::string> tags,
                              const EAnalysisType analysis_type = k1D)
  {
    m_name = name;
    m_title = title;
    m_univs = univs;
    m_tags = tags;
    m_analysis_type = analysis_type;

    m_n_linx_bins = n_linx_bins;
    m_linx_min = linx_min;
    m_linx_max = linx_max;
    m_fixedbins = true;

    for (auto tag : tags)
    {
      std::string hist_name = "hHD___"+tag +"___"+ name;
      // std::string hist_name = name + "_" + tag;
      m_hists[tag] = PlotUtils::HistWrapper<T>(hist_name.c_str(), title.c_str(), n_linx_bins, linx_min, linx_max, univs);
      m_has_hist[tag] = true;
      m_has_hist_2d[tag] = false;
    }

    m_decoder = UniverseDecoder(univs);
  }

  inline HistHyperDWrapperMap(const std::string name, const std::string title,
                              const Int_t n_linx_bins, const std::vector<double> linx_bins,
                              std::map<std::string, std::vector<T *>> univs, std::vector<std::string> tags,
                              const EAnalysisType analysis_type = k1D)
  {
    m_name = name;
    m_title = title;
    m_univs = univs;
    m_tags = tags;
    m_analysis_type = analysis_type;

    m_n_linx_bins = n_linx_bins;
    m_linx_bins = linx_bins;
    m_fixedbins = false;

    for (auto tag : tags)
    {
      std::string hist_name = "hHD___"+tag+"___"+name;
      m_hists[tag] = PlotUtils::HistWrapper<T>(hist_name.c_str(), title.c_str(), n_linx_bins, linx_bins, univs);
      m_has_hist[tag] = true;
      m_has_hist_2d[tag] = false;
    }

    m_decoder = UniverseDecoder(univs);
  }

  //===========================================================================
  // Constuctors for 2D Type 0 analyses
  //===========================================================================
  inline HistHyperDWrapperMap(const std::string name, const std::string title,
                              const Int_t n_linx_bins, const double linx_min, const double linx_max,
                              const Int_t n_y_bins, const double y_min, const double y_max,
                              std::map<std::string, std::vector<T *>> univs, const std::vector<std::string> tags,
                              const EAnalysisType analysis_type = k2D)
  {
    m_name = name;
    m_title = title;
    m_univs = univs;
    m_tags = tags;
    m_analysis_type = analysis_type;

    m_n_linx_bins = n_linx_bins;
    m_linx_min = linx_min;
    m_linx_max = linx_max;
    m_n_y_bins = n_y_bins;
    m_y_min = y_min;
    m_y_max = y_max;
    m_fixedbins = true;

    for (auto tag : tags)
    {
      std::string hist_name = "hHD_2D___" + tag + "___" + name;
      m_hists_2d[tag] = PlotUtils::Hist2DWrapper<T>(hist_name.c_str(), title.c_str(), n_linx_bins, linx_min, linx_max, n_y_bins, y_min, y_max, univs);
      m_has_hist_2d[tag] = true;
      m_has_hist[tag] = false;
    }

    m_decoder = UniverseDecoder(univs);
  }

  inline HistHyperDWrapperMap(const std::string name, const std::string title,
                              const std::vector<double> linx_bins, const std::vector<double> y_bins,
                              std::map<std::string, std::vector<T *>> univs, std::vector<std::string> tags,
                              const EAnalysisType analysis_type = k1D)
  {
    m_name = name;
    m_title = title;
    m_univs = univs;
    m_tags = tags;
    m_analysis_type = analysis_type;

    m_linx_bins = linx_bins;
    m_y_bins = y_bins;
    m_fixedbins = false;

    for (auto tag : tags)
    {
      std::string hist_name = "hHD_2D___" + tag + "___" + name;
      m_hists_2d[tag] = PlotUtils::Hist2DWrapper<T>(hist_name.c_str(), title.c_str(), linx_bins, y_bins, univs);
      m_has_hist_2d[tag] = true;
      m_has_hist[tag] = false;
    }

    m_decoder = UniverseDecoder(univs);
  }

  //===========================================================================
  // Methods
  //===========================================================================

  inline void AppendName(const std::string n, const std::vector<std::string> tags)
  {
    for (auto tag : tags){
      if (m_has_hist[tag])
        m_hists[tag].hist->SetName(Form("%s___%s",(m_hists[tag].hist->GetName()),n.c_str()));
      else if (m_has_hist_2d[tag])
        m_hists_2d[tag].hist->SetName(Form("%s___%s", (m_hists_2d[tag].hist->GetName()), n.c_str()));
    }
  }

  //  can we make this smarter?
  // For linearized "value" input (basically which bin is it going in)
  inline void Fill(const std::string tag, const T *universe, const Double_t value, const Double_t weight=1.0)
  {
    m_hists[tag].FillUniverse(universe, value, weight);
  }

  inline void Fill(const std::string tag, const T *universe, const Double_t x_value, const Double_t y_value, const Double_t weight)
  {
    m_hists_2d[tag].FillUniverse(universe, x_value, y_value, weight);
  }

  inline int GetNhists()
  {
    if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
      return m_hists.size();
    else if (m_analysis_type == k2D|| m_analysis_type == k2D_lite)
      return m_hists_2d.size();
  }

  inline std::string GetHistName(const std::string tag)
  {
    if (m_analysis_type == k1D || m_analysis_type == k1D_lite)
      return m_hists[tag].hist->GetName();
    else if ((m_analysis_type == k2D || m_analysis_type == k2D_lite))
      return m_hists_2d[tag].hist->GetName();
    return "";
  }

  inline MnvH1D* GetHist(const std::string tag)
  {
    if (m_hists.count(tag) > 0 && (m_analysis_type == k1D || m_analysis_type == k1D_lite))
      return m_hists[tag].hist;
    return 0;
  }

  inline MnvH2D* GetHist2D(const std::string tag)
  {
    if (m_hists_2d.count(tag) > 0 && (m_analysis_type == k2D|| m_analysis_type == k2D_lite))
      return m_hists_2d[tag].hist;
    return 0;
  }

  inline void Scale(const std::string tag, double scale){
    if (m_has_hist[tag])
      m_hists[tag].hist->Scale(scale);
    else if (m_has_hist_2d[tag])
      m_hists_2d[tag].hist->Scale(scale);
  }

  inline void Write(const std::string tag, Int_t option = 0){
    std::cout << " look at all tags " << tag << std::endl;
    if (m_has_hist[tag])
    {
      std::cout << " try to write hist " << tag << " " << m_hists[tag].hist->GetName() <<  std::endl;
      m_hists[tag].hist->Write();
    }
    else if (m_has_hist_2d[tag])
    {
      std::cout << " try to write hist " << tag << " " << m_hists_2d[tag].hist->GetName() << std::endl;
      m_hists_2d[tag].hist->Write();
    }
  }

  // voodoo you sometimes need
  inline void SyncCVHistos(){
    for (auto tag:m_tags){
      if (m_has_hist[tag])
        m_hists[tag].SyncCVHistos();
      if (m_has_hist_2d[tag])
        m_hists_2d[tag].SyncCVHistos();
    }
  }

}; // Close class
}; // Close namespace
#endif /* HistWrapperMap_h */
