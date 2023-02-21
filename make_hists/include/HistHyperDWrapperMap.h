//
//  HistHyperDWrapperMap.h
//
//
//  Created by Heidi Schellman (research) on 11/4/16.
//
// Modified for HyperDim by Noah Vaughan on 2/10/23

// make a map of HistHyperDWrappers with the same name title and binning.

#ifndef HistHyperDWrapperMap_h
#define HistHyperDWrapperMap_h

//#define HSTDBG
// TODO: Do I need to amek a Hyperd HistWrapper?
#include "PlotUtils/HistWrapper.h"
// #include "HistWrapperMap.h" // TODO: Maybe could just be wrapper around regular HM?

//#include "PlotUtils/DefaultCVUniverse.h"
// #include "MinervaUnfold/MnvResponse.h"
#include <map>
#include <iostream>
#include <string>
#include <vector>
// #include "utils/UniverseDecoder.h"


namespace PlotUtils{
template <typename T>

class HistHyperDWrapperMap:public T {

private:
  // TODO: Do I need to make a HyperD HistWrapper?
  std::map<const std::string, HistWrapper<T> > m_hists;
  std::map< std::string, std::vector<T*> > m_univs;
  std::string m_name = "NULL";
  std::string m_title = "NULL";
  PlotUtils::HyperDimLinearizer* m_hyper_dim;
  // Number of linearized truth bins
  int m_n_linbins = 0;
  // Number of linearized reco bins
  int m_n_reco_linbins = 0;
  // Vectors of linearized bins, this should just be a list of indexes
  std::vector<double> m_linbins;
  std::vector<double> m_reco_linbins;
  std::map<std::string, std::vector<T *>> m_universes; // if you are using a vector need to add that <-Huh?? -NHV

  int m_nbins = 0;
  int m_nrecobins = 0;
  double m_xmin = 0.0;
  double m_xmax = 0.0;
  double m_xrecomin = 0.0;
  double m_xrecomax = 0.0;
  std::vector<double> m_bins;
  std::vector<double> m_recobins;
  bool m_fixedbins;
  int m_count;
  std::map<const std::string, bool> m_hashist;
  std::map<const std::string, bool> m_hasresponse;
  std::vector<std::string> m_tags;
  std::map<std::string,int> m_response_bands; // map that tells you how many
  std::map<const T*,int> m_decoder;

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

  HistWrapperMap(){};
  // constructor

  inline  HistWrapperMap( const std::string name, const std::string title, const Int_t nbins, const double xmin,const double xmax,  std::map< std::string,std::vector<T*>> univs, const std::vector<std::string> tags){
    // just store the config
    m_name = name;
    m_title = title;
    m_nbins = nbins;
    m_xmin = xmin;
    m_xmax = xmax;
    m_nrecobins = nbins;
    m_xrecomin = xmin;
    m_xrecomax = xmax;
    m_fixedbins = true;
    //    m_count = 0;
    m_univs = univs;
    m_tags = tags;
    for (auto tag : tags){
     std::string hist_name = "h___"+tag +"___"+ name;
     // std::string hist_name = name + "_" + tag;
      m_hists[tag] = PlotUtils::HistWrapper<T>(hist_name.c_str(), title.c_str(), nbins, xmin, xmax, univs);
      m_hashist[tag] = true;
    }
    m_decoder = UniverseDecoder(univs);
  }

  // constructor for case where you are not building a response.
  inline  HistWrapperMap( const std::string name, const std::string title, const Int_t nbins, const std::vector<double> bins,  std::map< std::string, std::vector<T*> > univs, std::vector<std::string> tags){
    // just store the config
    m_name = name;
    m_title = title;
    m_nbins = nbins;
    m_bins  = bins;
//    m_nrecobins = nbins;
//    m_recobins = bins;
    m_fixedbins = false;
    //    m_count = 0 ;
    m_univs = univs;
    m_tags = tags;
    for (auto tag : tags){
      //std::string hist_name = tag +"_"+ name;
      std::string hist_name = "h___"+tag+"___"+name;
      m_hists[tag] = PlotUtils::HistWrapper<T>(hist_name.c_str(), title.c_str(), nbins, bins, univs);
      m_hashist[tag] = true;
    }
    m_decoder = UniverseDecoder(univs);
  }

  inline void AppendName(const std::string n, const std::vector<std::string> tags){
     for (auto tag : tags){
       m_hists[tag].hist->SetName(Form("%s___%s",(m_hists[tag].hist->GetName()),n.c_str()));
     }
   }

  //  can we make this smarter?
  // For linearized "value" input (basically which bin is it going in)
  inline void Fill(const std::string tag, const T* universe, const Double_t value, const Double_t weight=1.0){
    m_hists[tag].FillUniverse(universe, value, weight);
  }

  // For input value vector in phase space
  inline void Fill(const std::string tag, const T* universe, const std::vector<Double_t> value_vec, const Double_t weight=1.0){
    double value = (m_hyper_dim->GetBin(value_vec).first) + 0.0001
    m_hists[tag].FillUniverse(universe, value, weight);
  }


  inline int GetNhists(){return m_hists.size();}

  inline MnvH1D* GetHist(const std::string tag){
    if (m_hists.count(tag)>0) return m_hists[tag].hist;
    return 0;
  };

  inline void Scale(const std::string tag, double scale){
    m_hists[tag].hist->Scale(scale);
  };

  inline void Write(const std::string tag, Int_t option = 0){
      std::cout << " look at all tags " << tag << std::endl;
      if (m_hashist[tag]){
        std::cout << " try to write hist " << tag << " " << m_hists[tag].hist->GetName() <<  std::endl;
        m_hists[tag].hist->Write();
      }
  };

  // voodoo you sometimes need
  inline void SyncCVHistos(){
    for (auto tag:m_tags){
      m_hists[tag].SyncCVHistos();
    }
  };


};
};
#endif /* HistWrapperMap_h */
