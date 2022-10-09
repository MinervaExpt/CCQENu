#ifndef Response2DWrapperMap_h
#define Response2DWrapperMap_h

#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "MinervaUnfold/MnvResponse.h"

#include <map>
#include <iostream>
#include <string>
#include <vector>
// #include "utils/UniverseDecoder.h"


namespace PlotUtils{
template <typename T>

class Response2DWrapperMap:public T {

private:
  std::map<std::string, MinervaUnfold::MnvResponse *> m_response;

  std::string m_name = "NULL";
  int m_n_xrecobins = 0;
  int m_n_xtruebins = 0;
  std::vector<double> m_xrecobins;
  std::vector<double> m_xtruebins;
  int m_n_yrecobins = 0;
  int m_n_ytruebins = 0;
  std::vector<double> m_yrecobins;
  std::vector<double> m_ytruebins;
  std::map< std::string, std::vector<T*> > m_reco_univs;
  std::map< std::string, std::vector<T*> > m_true_univs;
  std::map<const std::string, int> m_response_bands;
  std::vector<std::string> m_tags;
  std::map< const T*,int> m_decoder;
  std::map<const std::string, bool> m_hasresponse;

public:
  // Here's where I'll put public stuff
// ============================CONSTRUCTORS=====================================
  // Default. Do not use.
  Response2DWrapperMap(){};

  // Initialize based off bin vecs.
  inline Response2DWrapperMap(std::string name,
                            std::map< std::string, std::vector<T*> > reco_univs,
                            const std::vector<double> xrecobins, const std::vector<double> xtruebins,
                            const std::vector<double> yrecobins, const std::vector<double> ytruebins,
                            std::vector<std::string> tags, std::string tail=""){
    m_name = name;
    m_reco_univs = reco_univs;
    m_xrecobins = xrecobins;
    m_yrecobins = yrecobins;
    m_xtruebins = xtruebins;
    m_ytruebins = ytruebins;
    m_tags = tags;

    m_n_xrecobins = xrecobins.size()-1;
    m_n_yrecobins = yrecobins.size()-1;
    m_n_xtruebins = xtruebins.size()-1;
    m_n_ytruebins = ytruebins.size()-1;

    // Count the number of universes in each band
    for (auto band : m_reco_univs){ // Using reco_univs since that's what originally was done
      std::string name = band.first;
      std::string realname = (band.second)[0]->ShortName();
      int nuniv = band.second.size();
      // m_response_bands[realname] = nuniv;
      m_response_bands[realname] = nuniv;
    }

    // Loop over tags for initializing the response
    for(auto tag:tags){
      // the name of the histogram. The "tail" at the end should be an empty string or "_tuned".
      std::string resp_name = "h2D___" + tag + "___" + name + "___response" + tail;
      m_response[tag] = new MinervaUnfold::MnvResponse(resp_name.c_str(), resp_name.c_str(), m_n_xrecobins, &xrecobins[0], m_n_yrecobins, &yrecobins[0], m_n_xtruebins, &xtruebins[0], m_n_ytruebins, &ytruebins[0], m_response_bands);
      m_hasresponse[tag] = true;
    }
    m_decoder = UniverseDecoder(reco_univs);

  };
// ===============================FILL RESPONSE=================================

  inline void Fill2D(const std::string tag, const T* univ, const double x_value, const double y_value, const double x_truth, const double y_truth, const double weight=1.0, const double scale=1.0){
    std::string name = univ->ShortName();
    int iuniv = m_decoder[univ];
    //std::cout << " fillresponse " << name << " " << iuniv << std::endl;
    m_response[tag]->Fill(x_value, y_value, x_truth, y_truth, name, iuniv, weight*scale);
  };


// ==============================WRITE RESPONSE=================================

  void Write(const std::string tag){
    // Make some blank hists to put stuff in
    PlotUtils::MnvH2D* h_migration;
    PlotUtils::MnvH2D* h_reco;
    PlotUtils::MnvH2D* h_truth;

    std::cout << " GetMigrationObjects will now complain because I passed it pointers to uninitiated MnvH2D/1D to fill please ignore" << std::endl;
    // Put the response objects into the hists
    m_response[tag]->GetMigrationObjects( h_migration, h_reco, h_truth);
    std::cout << h_migration << std::endl;
    // Write hists to file
    if (h_reco->GetEntries() > 0){
      h_migration->Write();
      h_reco->Write();
      h_truth->Write();
    }
  };

// ===================================HELPERS===================================
  //
  // std::map<std::string, int>& GetResponseBands(std::map< std::string, std::vector<T*> > reco_univs){
  //   std::map<std::string, int> response_bands;
  //
  //   for (auto band : m_reco_univs){ // Using reco_univs since that's what originally was done
  //     std::string name = band.first;
  //     std::string realname = (band.second)[0]->ShortName();
  //     int nuniv = band.second.size();
  //     // m_response_bands[realname] = nuniv;
  //     response_bands[realname] = nuniv;
  //   }
  //   return response_bands&;
  // }


  inline MinervaUnfold::MnvResponse* GetResponse(const std::string tag){
    if (m_response.count(tag)>0) return m_response[tag];
    return 0;
  }

  inline MnvH2D* GetMigrationMatrix(const std::string tag){
    MnvH2D* matrix;

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

  // This is used in HistWrapperMaps as well. Maybe could just do it as separate class
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

}; // Closing class


}//Closing namespace
#endif
