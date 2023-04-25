#ifndef ResponseHyperDWrapperMap_h
#define ResponseHyperDWrapperMap_h

#include <iostream>
#include <map>
#include <string>
#include <vector>

#include "MinervaUnfold/MnvResponse.h"
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "VariableHyperDBase.h"
// #include "utils/UniverseDecoder.h"

namespace PlotUtils {
template <typename T>

class ResponseHyperDWrapperMap : public T {
   private:
    std::map<std::string, MinervaUnfold::MnvResponse *> m_response;
    std::map<const std::string, bool> m_hasresponse;
    EAnalysisType m_analysis_type;

    std::string m_name = "NULL";

    int m_n_reco_x_linbins = 0;
    int m_n_true_x_linbins = 0;
    std::vector<double> m_reco_x_linbins;
    std::vector<double> m_true_x_linbins;
    int m_n_reco_y_bins = 0;
    int m_n_true_y_bins = 0;
    std::vector<double> m_reco_y_bins;
    std::vector<double> m_true_y_bins;

    std::map<std::string, std::vector<T *>> m_reco_univs;
    std::map<std::string, std::vector<T *>> m_true_univs;
    std::map<const std::string, int> m_response_bands;
    std::vector<std::string> m_tags;
    std::map<const T *, int> m_decoder;

   public:
    // Here's where I'll put public stuff
    // ============================CONSTRUCTORS=====================================
    // Default. Do not use.
    ResponseHyperDWrapperMap(){};

    // Initialize based off bin vecs.
    inline ResponseHyperDWrapperMap(std::string name,
                                    std::map<std::string, std::vector<T *>> reco_univs,
                                    const std::vector<double> reco_x_linbins, const std::vector<double> true_x_linbins,
                                    std::vector<std::string> tags, std::string tail = "") {
        m_name = name;
        m_reco_univs = reco_univs;
        m_reco_x_linbins = reco_x_linbins;
        m_true_x_linbins = true_x_linbins;
        m_tags = tags;

        m_n_reco_x_linbins = reco_x_linbins.size() - 1;
        m_n_true_x_linbins = true_x_linbins.size() - 1;

        m_analysis_type = k1D;

        if (m_n_reco_x_linbins > 300 || m_n_true_x_linbins > 300) {
            std::cout << "WARNING: You just tried to make a 300x300 Response (or larger!!!). You're gonna have a bad time..." << std::endl;
        }
        // Count the number of universes in each band
        std::map<std::string, int> response_bands;
        for (auto band : reco_univs) {  // Using reco_univs since that's what originally was done
            std::string name = band.first;
            std::string realname = (band.second)[0]->ShortName();
            int nuniv = band.second.size();
            response_bands[realname] = nuniv;
        }

        // Loop over tags for initializing the response
        for (auto tag : tags) {
            // the name of the histogram. The "tail" at the end should be an empty string or "_tuned".
            std::string resp_name = "hHD___" + tag + "___" + name + "___response" + tail;
            m_response[tag] = new MinervaUnfold::MnvResponse(resp_name.c_str(), resp_name.c_str(), m_n_reco_x_linbins, &reco_x_linbins[0], m_n_true_x_linbins, &true_x_linbins[0], response_bands);
            m_hasresponse[tag] = true;
        }
        m_decoder = UniverseDecoder(reco_univs);
    };

    inline ResponseHyperDWrapperMap(std::string name,
                                    std::map<std::string, std::vector<T *>> reco_univs,
                                    const std::vector<double> reco_x_linbins, const std::vector<double> true_x_linbins,
                                    const std::vector<double> reco_y_bins, const std::vector<double> true_y_bins,
                                    std::vector<std::string> tags, std::string tail = "") {
        m_name = name;
        m_reco_univs = reco_univs;
        m_reco_x_linbins = reco_x_linbins;
        m_true_x_linbins = true_x_linbins;
        m_reco_y_bins = reco_y_bins;
        m_true_y_bins = true_y_bins;
        m_tags = tags;

        m_n_reco_x_linbins = reco_x_linbins.size() - 1;
        m_n_true_x_linbins = true_x_linbins.size() - 1;

        m_n_reco_y_bins = reco_y_bins.size() - 1;
        m_n_true_y_bins = true_y_bins.size() - 1;

        m_analysis_type = k2D;

        if (m_n_reco_x_linbins > 300 || m_n_true_x_linbins > 300) {
            std::cout << "WARNING: You just tried to make a 300x300 Response (or larger!!!). You're gonna have a bad time..." << std::endl;
        }

        // Count the number of universes in each band
        // std::map<std::string, int> response_bands;
        for (auto band : reco_univs) {  // Using reco_univs since that's what originally was done
            std::string name = band.first;
            std::string realname = (band.second)[0]->ShortName();
            int nuniv = band.second.size();
            m_response_bands[realname] = nuniv;
        }

        // Loop over tags for initializing the response
        for (auto tag : tags) {
            // the name of the histogram. The "tail" at the end should be an empty string or "_tuned".
            std::string resp_name = "hHD_2D___" + tag + "___" + name + "___response" + tail;
            m_response[tag] = new MinervaUnfold::MnvResponse(resp_name.c_str(), resp_name.c_str(), m_n_reco_x_linbins, &reco_x_linbins[0], m_n_reco_y_bins, &reco_y_bins[0], m_n_true_x_linbins, &true_x_linbins[0], m_n_true_y_bins, &true_y_bins[0], m_response_bands);
            // m_response[tag] = new MinervaUnfold::MnvResponse(resp_name.c_str(), resp_name.c_str(), m_n_reco_x_linbins, &reco_x_linbins[0], m_n_reco_y_bins, &reco_y_bins[0], m_n_true_x_linbins, &true_x_linbins[0], m_n_true_y_bins, &true_y_bins[0], m_response_bands);

            m_hasresponse[tag] = true;
        }
        m_decoder = UniverseDecoder(reco_univs);
    };
    // ===============================FILL RESPONSE=================================

    inline void Fill(const std::string tag, const T *univ, const double value, const double truth, const double weight, const double scale = 1.0) {
        std::string name = univ->ShortName();
        int iuniv = m_decoder[univ];
        // std::cout << " fillresponse " << name << " " << iuniv << std::endl;
        m_response[tag]->Fill(value, truth, name, iuniv, weight * scale);
    };

    inline void Fill(const std::string tag, const T *univ, const double x_value, const double y_value, const double x_truth, const double y_truth, const double weight, const double scale = 1.0) {
        std::string name = univ->ShortName();
        int iuniv = m_decoder[univ];
        // std::cout << " fillresponse " << name << " " << iuniv << std::endl;
        m_response[tag]->Fill(x_value, y_value, x_truth, y_truth, name, iuniv, weight * scale);
    };

    // ==============================WRITE RESPONSE=================================

    void Write(const std::string tag) {
        PlotUtils::MnvH2D *h_migration;

        if (m_analysis_type == k1D) {
            // Make some blank hists to put stuff in
            PlotUtils::MnvH1D *h_reco;
            PlotUtils::MnvH1D *h_truth;

            std::cout << " GetMigrationObjects will now complain because I passed it pointers to uninitiated MnvH2D/1D to fill please ignore" << std::endl;
            // Put the response objects into the hists
            m_response[tag]->GetMigrationObjects(h_migration, h_reco, h_truth);
            std::cout << h_migration << std::endl;
            // Write hists to file
            if (h_reco->GetEntries() > 0) {
                h_migration->Write();
                h_reco->Write();
                h_truth->Write();
            }
        }

        else if (m_analysis_type == k2D) {
            // Make some blank hists to put stuff in
            PlotUtils::MnvH2D *h_reco;
            PlotUtils::MnvH2D *h_truth;

            std::cout << " GetMigrationObjects will now complain because I passed it pointers to uninitiated MnvH2D/1D to fill please ignore" << std::endl;
            // Put the response objects into the hists
            m_response[tag]->GetMigrationObjects(h_migration, h_reco, h_truth);
            std::cout << h_migration << std::endl;
            // Write hists to file
            if (h_reco->GetEntries() > 0) {
                h_migration->Write();
                h_reco->Write();
                h_truth->Write();
            }
        }
    };

    // ===================================HELPERS===================================

    inline MinervaUnfold::MnvResponse *GetResponse(const std::string tag) {
        if (m_response.count(tag) > 0) return m_response[tag];
        return 0;
    }

    inline MnvH2D *GetMigrationMatrix(const std::string tag) {
        MnvH2D *matrix;
        if (m_analysis_type == k1D) {
            MnvH1D *dummy;
            MnvH1D *dummy2;

            if (m_response.count(tag) > 0) {
#ifdef HSTDBG
                std::cout << " HistWrapperMap::Migration matrix has size " << m_response[tag]->GetMigrationMatrix()->GetErrorBandNames().size() << std::endl;
                std::cout << " HistWrapperMap::getting migration matrix " << m_response[tag]->GetMigrationMatrix()->GetName() << std::endl;
#endif
                matrix = m_response[tag]->GetMigrationMatrix();
                return matrix;
            }
        }
        if (m_analysis_type == k2D) {
            MnvH2D *dummy;
            MnvH2D *dummy2;

            if (m_response.count(tag) > 0) {
#ifdef HSTDBG
                std::cout << " HistWrapperMap::Migration matrix has size " << m_response[tag]->GetMigrationMatrix()->GetErrorBandNames().size() << std::endl;
                std::cout << " HistWrapperMap::getting migration matrix " << m_response[tag]->GetMigrationMatrix()->GetName() << std::endl;
#endif
                matrix = m_response[tag]->GetMigrationMatrix();
                return matrix;
            }
        }
        return 0;
    }

    // This is used in HistWrapperMaps as well. Maybe could just do it as separate class
    std::map<const T *, int> UniverseDecoder(const std::map<std::string, std::vector<T *>> univs) const {
        std::map<const T *, int> decoder;
        for (auto univ : univs) {
            std::string name = univ.first;
            std::vector<T *> pointers = univ.second;
            for (int i = 0; i < pointers.size(); i++) {
                decoder[pointers[i]] = i;
            }
        }
        return decoder;
    }

};  // Closing class

}  // namespace PlotUtils
#endif
