//
//  HistWrapperMap.h
//  
//
//  Created by Heidi Schellman (research) on 11/4/16.
//
//

// make a map of histwrappers with the same name title and binning.

#ifndef HistWrapperMap_h
#define HistWrapperMap_h

//#define HSTDBG

#include "PlotUtils/HistWrapper.h"
//#include "PlotUtils/DefaultCVUniverse.h"
#include "MinervaUnfold/MnvResponse.h"
#include <map>
#include <iostream>
#include <string>
#include <vector>


namespace PlotUtils{
template <typename T>

class HistWrapperMap:public T {
  
private:
  
  std::map<const std::string, HistWrapper<T> > m_hists;
  std::map< std::string, std::vector<T*> > m_univs;
  std::string m_name = "NULL";
  std::string m_title = "NULL";
  int m_nbins = 0;
  double m_xmin = 0.0;
  double m_xmax = 0.0;
  std::vector<double> m_bins;
  std::map< std::string, std::vector<T*> > m_universes;  // if you are using a vector need to add that
  std::map< std::string, MinervaUnfold::MnvResponse *> m_response;
  bool m_fixedbins;
  int m_count;
  std::map<const std::string, bool> m_hashist;
  std::map<const std::string, bool> m_hasresponse;
  std::vector<std::string> m_tags;
  std::map<std::string,int> m_response_bands; // map that tells you how many
  std::map<const T*,int> m_decoder;
  
public:
  
  HistWrapperMap(){};
  // constructor
  
 
   
  inline  HistWrapperMap( const std::string name, const std::string title, const Int_t nbins, const double xmin,const double xmax,  std::map< std::string,std::vector<T*>> univs, const std::vector<std::string> tags){
    // just store the config
    m_name = name;
    m_title = title;
    m_nbins = nbins;
    m_xmin = xmin;
    m_xmax = xmax;
    m_fixedbins = true;
    //    m_count = 0;
    m_univs = univs;
    m_tags = tags;
    for (auto tag : tags){
     std::string hist_name = "h___"+tag +"___"+ name;
     // std::string hist_name = name + "_" + tag;
      m_hists[tag] = PlotUtils::HistWrapper<T>(hist_name.c_str(), title.c_str(), nbins, xmin, xmax, univs);
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
  
  
  
  // constructor
  inline  HistWrapperMap( const std::string name, const std::string title, const Int_t nbins, const std::vector<double> bins,  std::map< std::string, std::vector<T*> > univs, std::vector<std::string> tags){
    // just store the config
    m_name = name;
    m_title = title;
    m_nbins = nbins;
    m_bins  = bins;
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
  
  
  // inline std::string GetName(){return m_name;}
  
  //  inline void AddHistWrapper(const std::string tag){
  //    PlotUtils::HistWrapper<T> hist;
  //    std::string hist_name = tag +"_"+ m_name;
  //    if (m_fixedbins){
  //      hist = PlotUtils::HistWrapper<T>(hist_name.c_str(), m_title.c_str(), m_nbins, m_xmin, m_xmax, m_universes);
  //    }
  //    else{
  //      hist = PlotUtils::HistWrapper<T>(hist_name.c_str(), m_title.c_str(), m_nbins, m_bins, m_universes);
  //    }
  //    m_hists[tag]=hist;
  //    m_hashist=true;
  //  };
  
  inline void AddResponse(std::vector<std::string> tags){
    
    // make a temp universe map to make Response happy
    std::map<std::string, int> response_bands;
    for (auto band : m_univs){
      std::string name = band.first;
      std::string realname = (band.second)[0]->ShortName();
      int nuniv = band.second.size();
      
      m_response_bands[realname] = nuniv;
    }
    for (auto tag:tags){
      //std::string resp_name = tag+"_response_"+m_name;
      std::string resp_name = "h___" + tag + "___"+m_name+"___response";
    
      if (m_fixedbins){
        TH1D tmp = TH1D("tmp", m_title.c_str(), m_nbins, m_xmin, m_xmax);
        std::vector<double> edges;
        for (int i = 1; i <= m_nbins+1; i++){
          edges.push_back(tmp.GetXaxis()->GetBinLowEdge(i));
        }
        m_response[tag] = new MinervaUnfold::MnvResponse(resp_name.c_str(), resp_name.c_str(), m_nbins, &edges[0],m_nbins,&edges[0], m_response_bands);
      }
      else{
        
        m_response[tag] = new MinervaUnfold::MnvResponse(resp_name.c_str(), resp_name.c_str(), m_nbins, &m_bins[0], m_nbins,&m_bins[0], m_response_bands);
      }
      m_hasresponse[tag] = true;
    }
    
    
    
    
  };
  
  inline void AppendName(const std::string n, const std::vector<std::string> tags){
     for (auto tag : tags){
       m_hists[tag].hist->SetName(Form("%s___%s",(m_hists[tag].hist->GetName()),n.c_str()));
     }
   }
     
  
  //  inline  std::vector<std::string> GetHistKeys(){
  //    std::vector<std::string> retval;
  //    for (auto  const& element : m_hists) {
  //      retval.push_back(element.first);
  //    }
  //    return retval;
  //  };
  
  //  can we make this smarter?
  inline void Fill(const std::string tag, const T* universe, const Double_t value, const Double_t weight=1.0){
    m_hists[tag].FillUniverse(universe, value, weight);
  }
  
  inline void FillResponse(const std::string tag, const T* univ, const double value, const double truth, const double weight=1.0){
    std::string name = univ->ShortName();
    int iuniv = m_decoder[univ];
    //std::cout << " fillresponse " << name << " " << iuniv << std::endl;
    m_response[tag]->Fill(value, truth, name, iuniv, weight);
  }
  
  inline int GetNhists(){return m_hists.size();}
  
  inline MnvH1D* GetHist(const std::string tag){
    if (m_hists.count(tag)>0) return m_hists[tag].hist;
    return 0;
  }
  
  inline MinervaUnfold::MnvResponse* GetResponse(const std::string tag){
    if (m_response.count(tag)>0) return m_response[tag];
    return 0;
  }
  
  inline MnvH2D* GetMigrationMatrix(const std::string tag){
    MnvH2D* matrix;
    MnvH1D* dummy;
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
        PlotUtils::MnvH1D* h_reco;
        PlotUtils::MnvH1D* h_truth;
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
#endif /* HistWrapperMap_h */
