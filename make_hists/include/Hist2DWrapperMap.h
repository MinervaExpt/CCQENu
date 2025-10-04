/**
* @file
* @author  Heidi Schellman/Noah Vaughan/SeanGilligan
* @version 1.0 *
* @section LICENSE *
* This program is free software; you can redistribute it and/or
* modify it under the terms of the GNU General Public License as
* published by the Free Software Foundation; either version 2 of
* the License, or (at your option) any later version. *
* @section DESCRIPTION *
* Code to fill histograms
 */
//
//  Hist2DWrapperMap.h
//
//
//  Created by Heidi Schellman (research) on 11/4/16.
//  Modified by Noah Vaughan for 2D, 1/12/21
//

// make a map of histwrappers with the same name title and binning.

#ifndef Hist2DWrapperMap_h
#define Hist2DWrapperMap_h

#define HSTDBG
#include <map>
#include <iostream>
#include <string>
#include <vector>

#include "PlotUtils/Hist2DWrapper.h"
//#include "PlotUtils/DefaultCVUniverse.h"
// #include "MinervaUnfold/MnvResponse.h" //need to check on this



namespace PlotUtils{
template <typename T>

class Hist2DWrapperMap:public T {

private:

  std::map<const std::string, Hist2DWrapper<T> > m_hists;
  std::map< std::string, std::vector<T*> > m_univs;
  std::string m_name = "NULL";
  std::string m_title = "NULL";
  int m_nxbins = 0;
  double m_xmin = 0.0;
  double m_xmax = 0.0;
  std::vector<Double_t> m_xbins;
  int m_nybins = 0;
  double m_ymin = 0.0;
  double m_ymax = 0.0;
  std::vector<Double_t> m_ybins;
  int m_nxrecobins = 0;
  double m_xrecomin = 0.0;
  double m_xrecomax = 0.0;
  std::vector<Double_t> m_xrecobins;
  int m_nyrecobins = 0;
  double m_yrecomin = 0.0;
  double m_yrecomax = 0.0;
  std::vector<Double_t> m_yrecobins;
  std::map< std::string, std::vector<T*> > m_universes;  // if you are using a vector need to add that
  // std::map< std::string, MinervaUnfold::MnvResponse *> m_response; //Need to check how 2D response is done

  bool m_fixedbins;
  int m_count;
  std::map<const std::string, bool> m_hashist;
  // std::map<const std::string, bool> m_hasresponse;
  std::vector<std::string> m_tags;
  // std::map<const std::string,int> m_response_bands; // map that tells you how many
  std::map<const T*,int> m_decoder;

public:
  // map that helps you find the index of a universe.
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

  Hist2DWrapperMap(){};
  // constructor
  //fixed bins
  inline Hist2DWrapperMap( const std::string name, const std::string title, const Int_t nxbins, const double xmin, const double xmax, const Int_t nybins, const double ymin, const double ymax, std::map< std::string,std::vector<T*>> univs, const std::vector<std::string> tags){
    // just store the config
#ifdef HSTDBG
      std::cout << " standard constructor" << std::endl;
#endif
    m_name = name;
    m_title = title;
    m_nxbins = nxbins;
    m_xmin = xmin;
    m_xmax = xmax;
    m_nybins = nxbins;
    m_ymin = ymin;
    m_ymax = ymax;

    m_nxrecobins = nxbins;
    m_xrecomin = xmin;
    m_xrecomax = xmax;
    m_nyrecobins = nxbins;
    m_yrecomin = ymin;
    m_yrecomax = ymax;
    m_fixedbins = true;
    //    m_count = 0;
    m_univs = univs;
    m_tags = tags;
    for (auto tag : tags){
     // std::string hist_name = tag +"_"+ name;
      std::string hist_name =  "h2D___"+tag + "___"+ name;
      m_hists[tag] = PlotUtils::Hist2DWrapper<T>(hist_name.c_str(), title.c_str(), nxbins, xmin, xmax, nybins, ymin, ymax, univs);
    }
    m_decoder = UniverseDecoder(univs);

  }


  // constructor
  // variable bins
  inline Hist2DWrapperMap( const std::string name, const std::string title, const std::vector<double> xbins,  const std::vector<double> ybins, std::map< std::string, std::vector<T*> > univs, std::vector<std::string> tags){ //2DWrapper doesn't need number of bins for variable bin width
    // just store the config
    m_name = name;
    m_title = title;
    m_xbins  = xbins;
    m_ybins  = ybins;
    m_xrecobins  = xbins;
    m_yrecobins  = ybins;
    m_fixedbins = false;
    //    m_count = 0 ;
    m_univs = univs;
    m_tags = tags;
    for (auto tag : tags){
      //std::string hist_name = name+"_"+ tag;
      std::string hist_name = "h2D___"+tag + "___" + name;
      m_hists[tag] = PlotUtils::Hist2DWrapper<T>(hist_name.c_str(), title.c_str(), xbins, ybins, univs);
      m_hashist[tag] = true;
    }
    m_decoder = UniverseDecoder(univs);
  }


    // constructor
    //fixed bins
    // constructor  This one is special for reconstructed/tuned MC so you can build a response.
    inline Hist2DWrapperMap( const std::string name, const std::string title, const Int_t nxbins, const double xmin, const double xmax, const Int_t nybins, const double ymin, const double ymax, const Int_t nxrecobins, const double xrecomin, const double xrecomax, const Int_t nyrecobins, const double yrecomin, const double yrecomax, std::map< std::string,std::vector<T*>> univs, const std::vector<std::string> tags){
      // just store the config
      m_name = name;
      m_title = title;
      m_nxbins = nxbins;
      m_xmin = xmin;
      m_xmax = xmax;
      m_nybins = nxbins;
      m_ymin = ymin;
      m_ymax = ymax;
        m_nxrecobins = nxrecobins;
        m_xrecomin = xrecomin;
        m_xrecomax = xrecomax;
        m_nyrecobins = nxrecobins;
        m_yrecomin = yrecomin;
        m_yrecomax = yrecomax;
      m_fixedbins = true;
      //    m_count = 0;
      m_univs = univs;
      m_tags = tags;
      for (auto tag : tags){
       // std::string hist_name = tag +"_"+ name;
        std::string hist_name =  "h2D___"+tag + "___"+ name;
        m_hists[tag] = PlotUtils::Hist2DWrapper<T>(hist_name.c_str(), title.c_str(), nxbins, xmin, xmax, nybins, ymin, ymax, univs);
      }
      m_decoder = UniverseDecoder(univs);

    }


    // constructor
    // variable bins
    // constructor  This one is special for reconstructed/tuned MC so you can build a response.
    inline Hist2DWrapperMap( const std::string name, const std::string title, const std::vector<double> xbins,  const std::vector<double> ybins, std::vector<double> xrecobins,  const std::vector<double> yrecobins, std::map< std::string, std::vector<T*> > univs, std::vector<std::string> tags){ //2DWrapper doesn't need number of bins for variable bin width
      // just store the config
      m_name = name;
      m_title = title;
      m_xbins  = xbins;
      m_ybins  = ybins;
      m_xrecobins  = xrecobins;
      m_yrecobins  = yrecobins;

      m_fixedbins = false;
      //    m_count = 0 ;
      m_univs = univs;
      m_tags = tags;
      for (auto tag : tags){
        //std::string hist_name = name+"_"+ tag;
        std::string hist_name = "h2D___"+tag + "___" + name;
        m_hists[tag] = PlotUtils::Hist2DWrapper<T>(hist_name.c_str(), title.c_str(), xrecobins, yrecobins, univs);
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
  inline void Fill2D(const std::string tag, const T *universe, const Double_t x_value, const Double_t y_value, const Double_t weight = 1.0) {
      m_hists[tag].FillUniverse(universe, x_value, y_value, weight);
  }

  inline void Fill2D(const std::string tag, const T *universe, const std::vector<Double_t> x_values, const std::vector<Double_t> y_values, const Double_t weight = 1.0) {
    assert(x_values.size() == y_values.size());
    for (int i = 0; i < x_values.size(); i++)  
      m_hists[tag].FillUniverse(universe, x_values[i], y_values[i], weight);
  }

  inline int GetNhists(){return m_hists.size();}

  inline MnvH2D* GetHist(const std::string tag){
    if (m_hists.count(tag)>0) return m_hists[tag].hist;
    return 0;
  }





  inline void Scale(const std::string tag, double scale){
    m_hists[tag].hist->Scale(scale);
  }

  inline void Write(const std::string tag, Int_t option = 0){

      std::cout << " look at all tags " << tag << std::endl;
      if (m_hashist[tag]){
        std::cout << " try to write hist " << tag << " " << m_hists[tag].hist->GetName() <<  std::endl;
        m_hists[tag].hist->Write();

      }
      else{
        std::cout << " could not find " << " " << m_hashist[tag] << std::endl;
      }


      // if(m_hasresponse[tag]){
      //   std::cout << " try to write response " << tag << " " << m_hists[tag].hist->GetName()  << std::endl;
      //   PlotUtils::MnvH2D* h_migration;
      //   PlotUtils::MnvH2D* h_reco;
      //   PlotUtils::MnvH2D* h_truth;
      //   //        h_migration->SetDirectory(0);
      //   //        h_reco->SetDirectory(0);
      //   //        h_truth->SetDirectory(0);
      //   std::cout << " GetMigrationObjects will now complain because I passed it pointers to uninitiated MnvH2D/1D to fill please ignore" << std::endl;
      //   m_response[tag]->GetMigrationObjects( h_migration, h_reco, h_truth);
      //   std::cout << h_migration << std::endl;
      //   if (h_reco->GetEntries() > 0){
      //     h_migration->Write();
      //     h_reco->Write();
      //     h_truth->Write();
      //   }
      //
      // }

  };


  // voodoo you sometimes need
  inline void SyncCVHistos(){
    for (auto tag:m_tags){
      m_hists[tag].SyncCVHistos();
    }
  };


};
};
#endif /* Hist2DWrapperMap_h */
