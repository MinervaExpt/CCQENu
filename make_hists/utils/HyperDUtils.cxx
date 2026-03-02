#ifndef SPLITHYPERDHIST_h
#define SPLITHYPERDHIST_h

#include "utils/HyperDUtils.h"
#include "HyperDUtils.h"

namespace CCQENu {
template <class MnvHist, class MnvVertErrorBandType, class MnvLatErrorBandType>
void HyperDUtils::splitObject(MnvHist* orig, MnvHist** histos, bool fullSplit) {
    if (!fullSplit) {
        // loop over vert and transfer
        std::vector<std::string> vert_names = orig->GetVertErrorBandNames();
        for (uint i = 0; i < vert_names.size(); i++) {
            histos[i] = new MnvHist(orig->GetCVHistoWithStatError());
            std::string name = orig->GetName();
            name += "_vert_";
            name += vert_names[i];
            histos[i]->SetName(name.c_str());
            std::cout << "I am transferring " << name << "\t" << std::endl;
            std::cout << orig->TransferVertErrorBand(histos[i], vert_names[i], true) << std::endl;
            // Strip sumw from universes
            std::cout << "I am working on " << name << "\t" << std::endl;
            int n_uni = histos[i]->GetVertErrorBand(vert_names[i])->GetNHists();
            std::cout << name << " has " << n_uni << std::endl;
            for (int j = 0; j < n_uni; j++)
                histos[i]->GetVertErrorBand(vert_names[i])->GetHist(j)->Sumw2(false);
        }

        // loop over lat and transfer
        std::vector<std::string> lat_names = orig->GetLatErrorBandNames();
        for (uint i = 0; i < lat_names.size(); i++) {
            histos[i + vert_names.size()] = new MnvH2D(orig->GetCVHistoWithStatError());
            std::string name = orig->GetName();
            name += "_lat_";
            name += lat_names[i];
            histos[i + vert_names.size()]->SetName(name.c_str());
            std::cout << "I am transferring " << name << "\t" << std::endl;
            std::cout << orig->TransferLatErrorBand(histos[i + vert_names.size()], lat_names[i], true) << std::endl;
            std::cout << "I am working on " << name << std::endl;
            // Strip sumw from universes
            int n_uni = histos[i + vert_names.size()]->GetLatErrorBand(lat_names[i])->GetNHists();
            std::cout << name << " has " << n_uni << std::endl;
            for (int j = 0; j < n_uni; j++) histos[i + vert_names.size()]->GetLatErrorBand(lat_names[i])->GetHist(j)->Sumw2(false);
        }
    } else {
        // In this mode every single universe is saved individually.
        std::vector<std::string> vert_names = orig->GetVertErrorBandNames();
        std::vector<std::string> lat_names = orig->GetLatErrorBandNames();
        int counter = 0;
        // Save the CV histogram!!
        histos[counter] = new MnvHist(orig->GetCVHistoWithStatError());
        histos[counter]->SetName(orig->GetName());
        counter += 1;
        for (uint i = 0; i < vert_names.size(); i++) {
            MnvVertErrorBand* err = orig->GetVertErrorBand(vert_names[i]);
            int n_uni = err->GetNHists();
            for (int j = 0; j < n_uni; j++) {
                TH2D* uni_hist = err->GetHist(j);
                std::string name = orig->GetName();
                name += "_vert_";
                name += vert_names[i];
                name += Form("_%d", j);
                histos[counter] = new MnvHist(*uni_hist);
                histos[counter]->SetName(name.c_str());
                histos[counter]->Sumw2(false);
                // std::vector<TH2D*> simple;
                // simple.push_back(uni_hist);
                // histos[counter]->AddVertErrorBand(vert_names[i],simple);
                counter += 1;
            }  // End loop over universes
        }  // End loop over vert
        for (uint i = 0; i < lat_names.size(); i++) {
            MnvLatErrorBand* err = orig->GetLatErrorBand(lat_names[i]);
            int n_uni = err->GetNHists();
            for (int j = 0; j < n_uni; j++) {
                TH2D* uni_hist = err->GetHist(j);
                std::string name = orig->GetName();
                name += "_lat_";
                name += lat_names[i];
                name += Form("_%d", j);
                histos[counter] = new MnvHist(*uni_hist);
                histos[counter]->SetName(name.c_str());
                histos[counter]->Sumw2(false);
                // std::vector<TH2D*> simple;
                // simple.push_back(uni_hist);
                // histos[counter]->AddLatErrorBand(vert_names[i],simple);
                counter += 1;
            }  // End loop over universes
        }  // End loop over vert
    }
}

template void HyperDUtils::splitObject<MnvH1D, MnvVertErrorBand, MnvLatErrorBand>(MnvH1D* original, MnvH1D** histso, bool fullSplit);
template void HyperDUtils::splitObject<MnvH2D, MnvVertErrorBand2D, MnvLatErrorBand2D>(MnvH2D* original, MnvH2D** histso, bool fullSplit);

template <class MnvHist, class MnvVertErrorBandType, class MnvLatErrorBandType>
std::vector<std::shared_ptr<MnvHist>> HyperDUtils::splitObject(MnvHist* orig, bool fullSplit) {
    std::vector<std::string> vert_names = orig->GetVertErrorBandNames();
    std::vector<std::string> lat_names = orig->GetLatErrorBandNames();
    std::vector<std::shared_ptr> split_hists = {};
    
    if (!fullSplit) {
    } else {

    }
    return std::vector<std::shared_ptr<MnvHist>>();
}

template std::vector<std::shared_ptr<MnvHist>> HyperDUtils::splitObject<MnvH1D, MnvVertErrorBand, MnvLatErrorBand>(MnvH1D* original, bool fullSplit);
template std::vector<std::shared_ptr<MnvHist>> HyperDUtils::splitObject<MnvH2D, MnvVertErrorBand2D, MnvLatErrorBand2D>(MnvH2D* original, bool fullSplit);

template <class T>
void HyperDUtils::combineObject(T* temp, MnvH2D*& target, std::string prefix, TFile* source_file, bool fullSplit) {
    std::cout << "Start Combining Objects" << std::endl;
    std::cout << "prefix\t" << prefix << std::endl;
    std::cout << "source_file\t" << source_file << std::endl;
    std::cout << "Temp\t" << temp << std::endl;
    std::cout << "target\t" << target << std::endl;
    std::vector<std::string> vert_names = temp->GetVertErrorBandNames();
    std::cout << "Temp verts" << vert_names.size() << std::endl;
    std::vector<std::string> lat_names = temp->GetLatErrorBandNames();
    std::cout << "Temp latss" << lat_names.size() << std::endl;
    if (!fullSplit) {
        for (uint i = 0; i < vert_names.size(); i++) {
            std::string name = prefix + "_vert_" + vert_names[i];
            std::cout << "vert: " << name << std::endl;
            MnvH2D* src = (MnvH2D*)source_file->Get(name.c_str());
            if (i == 0) {
                target = new MnvH2D(*src);
                target->SetName(prefix.c_str());
                target->SetTitle(prefix.c_str());
            } else
                src->TransferVertErrorBand(target, vert_names[i], false);
        }
        for (uint i = 0; i < lat_names.size(); i++) {
            std::string name = prefix + "_lat_" + lat_names[i];
            std::cout << "lat: " << name << std::endl;
            MnvH2D* src = (MnvH2D*)source_file->Get(name.c_str());
            src->TransferLatErrorBand(target, lat_names[i], false);
        }
    } else {  // This block creates vectors of universe histograms
        target = new MnvH2D(*(MnvH2D*)source_file->Get(prefix.c_str()));
        target->SetName(prefix.c_str());
        target->SetTitle(prefix.c_str());
        for (uint i = 0; i < vert_names.size(); i++) {
            std::vector<TH2D*> verthists;
            std::cout << vert_names[i] << std::endl;
            //      if(vert_names[i]=="Flux") continue;
            int n_hists = temp->GetVertErrorBand(vert_names[i])->GetNHists();
            for (int j = 0; j < n_hists; j++) {  // Now construct all those histograms and pull them into the vector;
                std::string name = prefix + "_vert_" + vert_names[i] + Form("_%d", j);
                std::cout << name << std::endl;
                MnvH2D* src = (MnvH2D*)source_file->Get(name.c_str());  // CV + single universe
                verthists.push_back(new TH2D(src->GetCVHistoWithStatError()));
            }  // End loop over universes
            std::cout << "DONE with building vector " << vert_names[i] << "\t" << verthists.size() << " end" << std::endl;
            target->AddVertErrorBand(vert_names[i], verthists);
            std::cout << "DONE" << std::endl;
        }  // End loop over verts

        for (uint i = 0; i < lat_names.size(); i++) {
            std::vector<TH2D*> lathists;
            int n_hists = temp->GetLatErrorBand(lat_names[i])->GetNHists();
            std::cout << lat_names[i] << std::endl;
            for (int j = 0; j < n_hists; j++) {  // Now construct all those histograms and pull them into the vector;
                std::string name = prefix + "_lat_" + lat_names[i] + Form("_%d", j);
                std::cout << name << std::endl;
                MnvH2D* src = (MnvH2D*)source_file->Get(name.c_str());  // CV + single universe
                std::cout << src << std::endl;
                lathists.push_back(new TH2D(src->GetCVHistoWithStatError()));
            }  // End loop over universes
            target->AddLatErrorBand(lat_names[i], lathists);
        }  // End loop over latss
    }
}

template void HyperDUtils::combineObject(MnvH1D* temp, MnvH2D*& target, std::string prefix, TFile* source_file, bool fullSplit);

template void HyperDUtils::combineObject(MnvH2D* temp, MnvH2D*& target, std::string prefix, TFile* source_file, bool fullSplit);

}  // namespace CCQENu
#endif