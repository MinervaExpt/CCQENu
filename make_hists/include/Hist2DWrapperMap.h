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

#include "PlotUtils/Hist2DWrapper.h"
//#include "PlotUtils/DefaultCVUniverse.h"
#include "MinervaUnfold/MnvResponse.h" //need to check on this
#include <map>
#include <iostream>
#include <string>
#include <vector>


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
  std::map< std::string, MinervaUnfold::MnvResponse *> m_response; //Need to check how 2D response is done
  
  bool m_fixedbins;
  int m_count;
  std::map<const std::string, bool> m_hashist;
  std::map<const std::string, bool> m_hasresponse;
  std::vector<std::string> m_tags;
  std::map<const std::string,int> m_response_bands; // map that tells you how many
  std::map<const T*,int> m_decoder;

public:

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


  // map that helps you find the index of a universe.
  std::map<const T*,int> UniverseDecoder(const std::map< std::string, std::vector<T*> > univs)const{
    std::map<const T*, int> decoder;
    for(auto univ:univs){
      std::string name = univ.first;
      std::vector<T*> pointers = univ.second;
      for (int i = 0; i < pointers.size(); i++){
        decoder[pointers[i]] = i;
      }
    }
    return decoder;
  }



  inline void AppendName(const std::string n, const std::vector<std::string> tags){
      for (auto tag : tags){
        m_hists[tag].hist->SetName(Form("%s___%s",(m_hists[tag].hist->GetName()),n.c_str()));
      }
  }

  inline void AddResponse2D(std::vector<std::string> tags, std::string tail=""){ //TODO: This name okay?

    // make a temp universe map to make Response happy
    std::map<std::string, int> response_bands; // necessary?
    for (auto band : m_univs){
      std::string name = band.first;
      const std::string realname = (band.second)[0]->ShortName();
      int nuniv = band.second.size();

      m_response_bands[realname] = nuniv;
    }
    for (auto tag:tags){
      //std::string resp_name = tag+"_response_"+m_name;
      std::string resp_name = "h2D___"+ tag + "___"+m_name+"___response"+tail;

      if (m_fixedbins){
        TH2D tmp = TH2D("tmp", m_title.c_str(), m_nxbins, m_xmin, m_xmax, m_nybins, m_ymin, m_ymax);
        TH2D recotmp = TH2D("recotmp", m_title.c_str(), m_nxrecobins, m_xrecomin, m_xrecomax, m_nyrecobins, m_yrecomin, m_yrecomax);
          
        std::vector<Double_t> xedges;
        std::vector<Double_t> yedges;
        std::vector<Double_t> xrecoedges;
        std::vector<Double_t> yrecoedges;
        for (int i = 1; i <= m_nxbins+1; i++){
          xedges.push_back(tmp.GetXaxis()->GetBinLowEdge(i));
        }
        for (int i = 1; i <= m_nybins+1; i++){
          yedges.push_back(tmp.GetYaxis()->GetBinLowEdge(i));
        }
        for (int i = 1; i <= m_nxrecobins+1; i++){
            xrecoedges.push_back(recotmp.GetXaxis()->GetBinLowEdge(i));
        }
        for (int i = 1; i <= m_nyrecobins+1; i++){
            yrecoedges.push_back(recotmp.GetYaxis()->GetBinLowEdge(i));
        }
        m_response[tag] = new MinervaUnfold::MnvResponse(resp_name.c_str(), resp_name.c_str(), m_nxrecobins, &xrecoedges[0], m_nyrecobins, &yrecoedges[0], m_nxbins, &xedges[0], m_nybins, &yedges[0], m_response_bands);
        //Reco is first set of bin params, truth is second set
      }
      else{
        m_nxbins = m_xbins.size()-1;
        m_nybins = m_ybins.size()-1;
        m_nxrecobins = m_xrecobins.size()-1;
        m_nyrecobins = m_yrecobins.size()-1;
        m_response[tag] = new MinervaUnfold::MnvResponse(resp_name.c_str(), resp_name.c_str(), m_nxrecobins, &m_xrecobins[0], m_nyrecobins, &m_yrecobins[0], m_nxbins, &m_xbins[0], m_nybins, &m_ybins[0], m_response_bands);
      }
      m_hasresponse[tag] = true;
    }




  };

 

  //  can we make this smarter?
  inline void Fill2D(const std::string tag, const T* universe, const Double_t x_value, const Double_t y_value, const Double_t weight=1.0){

    m_hists[tag].FillUniverse(universe, x_value, y_value, weight);
  }

  inline void FillResponse2D(const std::string tag, const T* univ, const double x_value, const double y_value, const double x_truth, const double y_truth, const double weight=1.0){ //TODO
    std::string name = univ->ShortName();

    int iuniv = m_decoder[univ];
    //std::cout << " fillresponse " << name << " " << iuniv << std::endl;
    
    m_response[tag]->Fill(x_value, y_value, x_truth, y_truth, name, iuniv, weight);
    
  }

  inline int GetNhists(){return m_hists.size();}

  inline MnvH2D* GetHist(const std::string tag){
    if (m_hists.count(tag)>0) return m_hists[tag].hist;
    return 0;
  }

  inline MinervaUnfold::MnvResponse* GetResponse(const std::string tag){
    if (m_response.count(tag)>0) return m_response[tag];
    return 0;
  }

  inline MnvH2D* GetMigrationMatrix(const std::string tag){
    MnvH2D* matrix;
    MnvH1D* dummy; //why are these here?
    MnvH1D* dummy2;

    if (m_response.count(tag)>0){
#ifdef HSTDBG
      std::cout << " HistWrapperMap::Migration matrix has size " << m_response[tag]->GetMigrationMatrix()->GetErrorBandNames().size() << std::endl;
      std::cout << " HistWrapperMap::getting migration matrix " << m_response[tag]->GetMigrationMatrix()->GetName() << std::endl;
#endif
      matrix = m_response[tag]->GetMigrationMatrix();
      return matrix;
    }
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


      if(m_hasresponse[tag]){
        std::cout << " try to write response " << tag << " " << m_hists[tag].hist->GetName()  << std::endl;
        PlotUtils::MnvH2D* h_migration;
        PlotUtils::MnvH2D* h_reco;
        PlotUtils::MnvH2D* h_truth;
        //        h_migration->SetDirectory(0);
        //        h_reco->SetDirectory(0);
        //        h_truth->SetDirectory(0);
        std::cout << " GetMigrationObjects will now complain because I passed it pointers to uninitiated MnvH2D/1D to fill please ignore" << std::endl;
        m_response[tag]->GetMigrationObjects( h_migration, h_reco, h_truth);
        std::cout << h_migration << std::endl;
        if (h_reco->GetEntries() > 0){
          h_migration->Write();
          h_reco->Write();
          h_truth->Write();
        }

      }

  };


  inline void DeleteResponse(){
    for (auto resp: m_response){
      std::cout << "delete migration matrix" << resp.second->GetMigrationMatrix()->GetName() ;
      delete resp.second;
    }
  }

  // voodoo you sometimes need
  inline void SyncCVHistos(){
    for (auto tag:m_tags){
      m_hists[tag].SyncCVHistos();
    }
  };


};
};
#endif /* Hist2DWrapperMap_h */
