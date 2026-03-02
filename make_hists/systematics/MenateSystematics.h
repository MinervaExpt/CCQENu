#ifndef MENATESystematics_h
#define MENATESystematics_h

//==============================================================================
// Get Several standard MINERvA systematics
//==============================================================================

#include "PlotUtils/GenericVerticalSystematic.h"
#include "PlotUtils/NeutronInelasticReweighter.h"
#include "include/CVUniverse.h"

typedef std::map<std::string, std::vector<CVUniverse*>> UniverseMap;

std::map<int, TString> NeutRWCategs = {{11, "sigQE"},
                                       {18, "sig2p2h"},
                                       {19, "sigOther"},
                                       {1, "1chargePi"},
                                       {2, "1neutPi"},
                                       {3, "NPi"},
                                       {4, "SubThresh"},
                                       {5, "TrackableProt"},
                                       {-999, "Other"}};

class MENATEUniverse : public CVUniverse {
   public:
    MENATEUniverse(PlotUtils::ChainWrapper* chw, double nsigma) : CVUniverse(chw, nsigma) {
        if (nsigma == 0) {
            LoadNeutronReweightHistos();
        }
    }

    std::map<int, TH2D*> m_NeutRWHists;

    virtual ~MENATEUniverse() = default;

    std::string ShortName() const override {
        return "MENATEUniverse";
    }

    std::string LatexName() const override {
        return "TEST MENATE Uncertainties";
    }

    double GetNeutronNormWeight() const {
        double ret = 1.0;
        int categ = GetNeutronReweightCategory(10.0);
        TH2D* reweightHist = m_NeutRWHists.at(categ);
        if (!reweightHist) return ret;
        int binX = reweightHist->GetXaxis()->FindBin(CVUniverse::GetTruePperpMuGeV());
        int binY = reweightHist->GetYaxis()->FindBin(GetMaxFSNeutronKE());
        double val = reweightHist->GetBinContent(binX, binY);
        ret = std::max(0.0, val);
        if (ret == 0.0) ret = 1.0;
        return ret;
    }

    double GetWeightRatioToCV() const override {
        double weight = 1.0;

        return weight;
    }

    void LoadNeutronReweightHistos() {
        for (auto Categ : NeutRWCategs) {
            m_NeutRWHists[Categ.first] = nullptr;
        }

        try {
            std::string weightFileName = "";
            // if(std::getenv("PLOTUTILSROOT")) weightFileName = std::string(std::getenv("PLOTUTILSROOT")) + "/../etc/extraWeightFiles/BURP.root";
            // if(std::getenv("PLOTUTILSROOT")) weightFileName = std::string(std::getenv("PLOTUTILSROOT")) + "/../etc/extraWeightFiles/test.root";
            if (std::getenv("PLOTUTILSROOT")) weightFileName = std::string(std::getenv("PLOTUTILSROOT")) + "/../etc/extraWeightFiles/NeutronRenorm_" + GetPlaylist() + ".root";
            std::unique_ptr<TFile> weightFile(TFile::Open(weightFileName.c_str()));

            for (auto Categ : NeutRWCategs) {
                TH2D* hist = (TH2D*)(weightFile->Get("NeutronRenormWeight_" + Categ.second));
                if (hist) m_NeutRWHists[Categ.first] = hist;
            }
        } catch (const ROOT::warning& /*w*/) {
            std::cout << "No Neutron Renormalization File. Doing without" << std::endl;
        }
    }

    virtual int GetNeutronReweightCategory(double neutKE) const {
        int ret = -999;

        /*
          std::map<int, std::string> Categs = {{11, "sigQE"},
          {18, "sig2p2h"},
          {19, "sigOther"},
          {1, "1chargePi"},
          {2, "1neutPi"},
          {3, "NPi"},
          {4, "SubThresh"},
          {5, "TrackableProt"}};
        */

        if (GetTruthNuPDG() != -14 || GetCurrent() != 1) return ret;

        int genie_n_muons = 0;
        int genie_n_piPM = 0;
        int genie_n_pi0 = 0;
        int genie_n_mesons = 0;
        int genie_n_heavy_baryons = 0;
        int genie_n_photons = 0;
        int genie_n_protons_above = 0;
        int genie_n_neutrons = 0;
        int genie_n_neutrons_above = 0;

        std::vector<int> PDGs = GetFSPartPDG();
        std::vector<double> Es = GetFSPartE();

        for (unsigned int i = 0; i < PDGs.size(); ++i) {
            int pdg = PDGs.at(i);
            double energy = Es.at(i);
            double proton_E = M_p + 120.0;  // Trackable Protons at 120 MeV T_p
            double neutron_E = M_n + neutKE;
            if (abs(pdg) == 13)
                genie_n_muons++;
            else if (pdg == 22 && energy > 10)
                genie_n_photons++;
            else if (abs(pdg) == 211)
                genie_n_piPM++;
            else if (pdg == 111)
                genie_n_pi0++;
            else if (abs(pdg) == 321 || abs(pdg) == 323 || pdg == 130 || pdg == 310 || pdg == 311 || pdg == 313) {
                genie_n_mesons++;
            } else if (pdg == 3112 || pdg == 3122 || pdg == 3212 || pdg == 3222 || pdg == 4112 || pdg == 4122 || pdg == 4222 || pdg == 411 || pdg == 421) {
                genie_n_heavy_baryons++;
            } else if (pdg == 2212 && energy > proton_E)
                genie_n_protons_above++;
            else if (pdg == 2112) {
                if (energy > M_n) genie_n_neutrons++;
                if (energy > neutron_E) genie_n_neutrons_above++;
            }
        }

        if (genie_n_muons == 1 &&
            genie_n_piPM == 0 &&
            genie_n_pi0 == 0 &&
            genie_n_mesons == 0 &&
            genie_n_heavy_baryons == 0 &&
            genie_n_photons == 0 &&
            genie_n_protons_above == 0 &&
            genie_n_neutrons_above > 0) {
            ret = 10;
            ret += GetInteractionType();
            if (ret != 11 && ret != 18) ret = 19;
        } else if ((genie_n_piPM + genie_n_pi0) > 1)
            ret = 3;
        else if (genie_n_piPM == 1)
            ret = 1;
        else if (genie_n_pi0 == 1)
            ret = 2;
        else if (genie_n_heavy_baryons == 0 && genie_n_photons == 0 && genie_n_mesons == 0 && genie_n_muons == 1) {
            if (genie_n_protons_above > 0)
                ret = 5;
            else if (genie_n_neutrons > 0)
                ret = 4;
        }

        return ret;
    }
};

UniverseMap GetMENATESystematicMap(PlotUtils::ChainWrapper* chain) {
    UniverseMap error_bands;

    error_bands["NeutronInelasticReweight"].push_back(new MENATEUniverse(chain, 0));
    error_bands["NeutronInelasticReweight"].push_back(new MENATEUniverse(chain, 1));
    error_bands["NeutronInelasticReweight"].push_back(new MENATEUniverse(chain, 2));
    error_bands["NeutronInelasticReweight"].push_back(new MENATEUniverse(chain, 3));
    error_bands["NeutronInelasticReweight"].push_back(new MENATEUniverse(chain, 4));
    error_bands["NeutronInelasticReweight"].push_back(new MENATEUniverse(chain, 5));
    error_bands["NeutronInelasticReweight"].push_back(new MENATEUniverse(chain, 6));

    return error_bands;
}


#endif  // MONASystematics_h