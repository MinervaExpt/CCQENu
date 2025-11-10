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
 * This implements a loop over the tuple that fills the histograms
 **/

#include <map>
#include <string>
#include <vector>

enum EDataMCTruth { kData,
                    kMC,
                    kTruth,
                    kNDataMCTruthTypes };

void status_bar(int i, int nentries, double& bar_progress, double& perc_progress) {
    double bar_length = 40.;  // how long you want your bar
    double perc_step = 0.1;
    if (i == 0) {  // Used to be first event, but weighters end up cutting it off
        std::cout << std::endl;
        std::cout << "   |";
        for (int j = 0; j < bar_length; j++) std::cout << "_";
        std::cout << "|   [__";
        std::cout << setprecision(-(int)log10(perc_step)) << std::fixed << perc_progress;
        std::cout << "%]";
    }
    if ((((double)(i + 1) * bar_length) / nentries) >= bar_progress + 1) {
        bar_progress += 1;
    }
    if (((double)(i + 1) * 100.) / nentries >= perc_progress + perc_step) {
        perc_progress += perc_step;
        std::cout << '\r' << std::flush << "   |";

        for (int j = 0; j < bar_progress; j++) std::cout << "\e[0;31;47m \e[0m";
        for (int j = bar_length; j > bar_progress; j--) std::cout << "_";

        std::cout << "|   [";
        if (perc_progress <= 10. - perc_step) std::cout << "_";
        if (perc_progress <= 100. - perc_step) std::cout << "_";
        std::cout << setprecision(-(int)log10(perc_step)) << std::fixed << perc_progress;
        std::cout << "%]";
        std::cout << "   ( ";
        for (int j = ((int)log10(nentries) - (int)log10(i + 1)); j > 0; j--) {
            std::cout << "_";
        }
        std::cout << i + 1 << " / " << nentries << " ) ";
    }
    if (i + 1 == nentries) {
        std::cout << '\r' << std::flush << "   |";
        for (int j = 0; j < bar_length; j++) std::cout << "\e[0;31;47m \e[0m";
        std::cout << "|   [100.0%]";
        std::cout << i + 1 << " / " << nentries << " )";
    }
}

// #define CLOSUREDETAIL

//==============================================================================
// Loop and fill
//==============================================================================
#ifndef __CINT__  // for PlotUtils::cuts_t<>
void LoopAndFillEventSelection(std::string tag,
                               const PlotUtils::MacroUtil& util,
                               std::map<std::string, std::vector<CVUniverse*> > error_bands,
                               std::vector<CCQENu::VariableFromConfig*>& variables,
                               std::vector<CCQENu::Variable2DFromConfig*>& variables2D,
                               std::vector<CCQENu::VariableHyperDFromConfig*>& variablesHD,
                               EDataMCTruth data_mc_truth,
                               PlotUtils::Cutter<CVUniverse>& selection,
                               PlotUtils::Model<CVUniverse, PlotUtils::detail::empty>& model,
                               PlotUtils::weight_MCreScale mcRescale,
                               PlotUtils::weight_warper warper,
                               bool closure = false, bool mc_reco_to_csv = false,
                               bool dostatusbar = false) {
    // Prepare loop
    MinervaUniverse::SetTruth(false);
    int nentries = -1;
    CVFunctions<CVUniverse> fund;

    TFile* myFile;
    TTree* mc_tree;
    TTree* data_tree;
    std::cout << "start of loop" << std::endl;
    // future code to dump the outputs.
    // if (data_mc_truth == kData) {
    //     myFile = TFile::Open("data.root", "RECREATE");
    //     data_tree = new TTree("digest", "data tree");
    //     fund->MakeTree(data_tree,1,0);
    // }
    // else {
    //     if (data_mc_truth == kMC) {
    //         myFile = TFile::Open("mc.root", "RECREATE");
    //         mc_tree = new TTree("digest", "mc tree");
    //     fund->MakeTree(data_tree,0,0);
    //     }
    // }

    // get ready for weights by finding cv universe pointer

    assert(!error_bands["cv"].empty() && "\"cv\" error band is empty!  Can't set Model weight.");
    auto& cvUniv = error_bands["cv"].front();

    // make a dummy event - may need to make fancier
    PlotUtils::detail::empty event;

    std::ofstream csvFile;
    if (variables.size() < 1 && variables2D.size() < 1 && variablesHD.size() < 1) {
        std::cout << " no variables to fill " << std::endl;
        return;  // don't bother if there are no variables.
    }

    // bool dowarp = false;
    bool dowarp = warper.GetDoWarp();
    std::cout << "dowarp " << dowarp << std::endl;
    if (data_mc_truth == kData) {
        nentries = util.GetDataEntries();
    } else if (data_mc_truth == kMC) {
        nentries = util.GetMCEntries();
        // dowarp = warper.GetDoWarp();
    } else {
        nentries = util.GetTruthEntries();
        MinervaUniverse::SetTruth(true);
    }

    unsigned int loc = tag.find("___") + 3;
    std::string cat(tag, loc, string::npos);
    std::string sample(tag, 0, loc - 3);
    std::cout << sample << " category " << cat << std::endl;
    std::cout << " starting loop " << data_mc_truth << " " << nentries << std::endl;
    std::cout << " tag is " << tag << std::endl;
    // If sending MC Reco values to CSV create file and add columns names
    if (data_mc_truth == kMC && mc_reco_to_csv) {
        std::string csvFileName = "mc_reco_entries_" + sample + "_" + cat + ".csv";
        csvFile.open(csvFileName);
        csvFile << "Entry";
        for (auto v : variables) {
            if (v->hasMC[tag]) {
                csvFile << ";" << v->GetName() << ";TrueValue";
            }
        }
        csvFile << ";Interaction;nFSPart;FSPDGs;FSPartEs";
        csvFile << ";run;subrun;gate;slice";
        // csvFile << ";Arachne" << std::endl;
        csvFile << std::endl;
    }

    // status bar stuff
    double bar_progress = 0.;   // how many chars has the bar progressed
    double perc_progress = 0.;  // percentage progression of entries
    // Begin entries loop
    for (int i = 0; i < nentries; i++) {
        if (data_mc_truth != kData) i += prescale - 1;

        cvUniv->SetEntry(i);

        if (data_mc_truth != kData) model.SetEntry(*cvUniv, event);

        if (data_mc_truth == kMC || data_mc_truth == kData) {
            if (!cvUniv->FastFilter()) continue;
        }
        // const double cvWeight = (data_mc_truth == kData || closure) ? 1. : model.GetWeight(*cvUniv, event);  // detail may be used for more complex things
        // TODO: Is this scaled cvWeight necessary?
        // const double cvWeightScaled = (data_mc_truth kData) ? 1. : cvWeight*mcRescale.GetScale(q2qe, "cv");
        
        if (dostatusbar) status_bar(i, nentries, bar_progress, perc_progress);

        // Loop bands and universes
        for (auto band : error_bands) {
            std::vector<CVUniverse*> error_band_universes = band.second;
            //  HMS replace with iuniv to access weights more easily
            //  HMS for (auto universe : error_band_universes) {
            std::string uni_name = (band.second)[0]->ShortName();
            for (int iuniv = 0; iuniv < error_band_universes.size(); iuniv++) {
                auto universe = error_band_universes[iuniv];

                universe->SetEntry(i);
                // if (doneutron) {
                if (data_mc_truth == kMC || data_mc_truth == kTruth) universe->SetNeutEvent(true);
                else universe->SetNeutEvent(false);
                // }
                // Process this event/universe
                // double weight = 1;
                // if (universe->ShortName() == "cv" ) weight = data_mc_truth == kData ? 1. : universe->GetWeight();

                // probably want to move this later on inside the loop
                // const double weight = (data_mc_truth == kData || closure) ? 1. : model.GetWeight(*universe, event);  // Only calculate the per-universe weight for events that will actually use it.
                // const double warp = (!dowarp || data_mc_truth == kData) ? 1. : warper.GetWarpWeight(*universe);

                const double warp = (dowarp && data_mc_truth == kMC && universe->ShortName() == "cv") ? warper.GetWarpWeight(*universe) : 1.;
                const double tmp_weight = (data_mc_truth == kData || closure) ? 1. : model.GetWeight(*universe, event);  // Only calculate the per-universe weight for events that will actually use it.
                const double weight = warp * tmp_weight;
                // PlotUtils::detail::empty event;
                // std::cout << "weight " << weight << std::endl;
                //=========================================
                // Fill
                //=========================================
                if (data_mc_truth == kMC) {
#ifdef CLOSUREDETAIL
                    if (closure && universe->ShortName() == "cv" && selection.isMCSelected(*universe, event, weight).all()) {
                        std::cout << universe->GetRun() << " " << universe->GetSubRun() << " " << universe->GetGate() << " " << universe->GetPmuGeV() << " " << weight << " " << selection.isDataSelected(*universe, event).all() << " " << selection.isMCSelected(*universe, event, weight).all() << " " << tag << selection.isSignal(*universe) << " " << universe->ShortName() << std::endl;
                        universe->Print();
                    }
#endif
                    if (selection.isMCSelected(*universe, event, weight).all() && selection.isSignal(*universe)) {
                        // if (warp!=1.) std::cout << "warp " << warp << "  tmp_weight " << tmp_weight << "   weight " << weight << std::endl;
                        // double weight = data_mc_truth == kData ? 1. : universe->GetWeight();
                        const double q2qe = universe->GetQ2QEGeV();
                        double scale = 1.0;
                        if (!closure) scale = mcRescale.GetScale(cat, q2qe, uni_name, iuniv);  // Only calculate the per-universe weight for events that will actually use it.
                        
                        // if (universe->ShortName() == "cv" && iuniv == 0) universe->PrintMADBlobs();

                        FillMC(tag, universe, weight, variables, variables2D, variablesHD, scale);
                        FillResponse(tag, universe, weight, variables, variables2D, variablesHD, scale);
                        FillResolution(tag, universe, weight, variables, variables2D, scale);
                        if (universe->ShortName() == "cv") {
                            FillType(tag, universe, weight, variables, variables2D, scale);  // only use cv and variables for now
                        }

                        // Send MC Reco value to CSV here
                        if (mc_reco_to_csv && universe->ShortName() == "cv") {
                            csvFile << i;
                            for (auto v : variables) {
                                if (v->hasMC[tag]) {
                                    if (!v->m_do_argvalue) {
                                        csvFile << ";" << v->GetRecoValue(*universe) << ";" << v->GetTrueValue(*universe);
                                        continue;
                                    }
                                    std::vector<double> fill_vals = v->GetArgRecoValue(*universe, v->GetRecoIndex(*universe));
                                    csvFile << ";{";
                                    for (int i = 0; i < fill_vals.size(); i++) {
                                        csvFile << fill_vals[i];
                                        if (i == fill_vals.size()-1) {
                                            csvFile << "};";
                                            break;
                                        }
                                        csvFile << ","; 
                                    }
                                }
                            }

                            int mcinttype = universe->GetMCIntType();
                            std::map<int, std::string> interaction;
                            interaction[1] = "QE";
                            interaction[2] = "RES";
                            interaction[3] = "DIS";
                            interaction[4] = "COH";
                            interaction[8] = "MEC";

                            csvFile << ";" << interaction[mcinttype];
                            int nFSParts = universe->GetTrueNumberOfFSParticles();
                            csvFile << ";" << universe->GetTrueNumberOfFSParticles();

                            std::vector<int> FSPartPDG = universe->GetVecInt("mc_FSPartPDG");
                            std::vector<double> mc_FSPartE = universe->GetVecDouble("mc_FSPartE");
                            csvFile << ";{";
                            for (int i = 0; i < nFSParts - 1; i++) csvFile << FSPartPDG[i] << ",";
                            csvFile << FSPartPDG[nFSParts - 1] << "};{";
                            for (int i = 0; i < nFSParts - 1; i++) csvFile << mc_FSPartE[i] << ",";
                            csvFile << mc_FSPartE[nFSParts - 1] << "}";

                            csvFile << ";" << universe->GetInt("mc_run");
                            csvFile << ";" << universe->GetInt("mc_subrun");
                            csvFile << ";" << universe->GetInt("mc_nthEvtInFile") + 1;
                            csvFile << ";" << universe->GetVecElem("slice_numbers", 0);
                            // csvFile << ";" << universe->StringTrueArachneLink() << std::endl;
                        }
                        // Done Sending MC Reco value to CSV
                    }
                } else if (data_mc_truth == kTruth) {
                    if (selection.isEfficiencyDenom(*universe, weight)) {
                        const double q2qe = universe->GetTrueQ2QEGeV();
                        double scale = 1.0;
                        if (!closure) scale = mcRescale.GetScale(cat, q2qe, uni_name, iuniv);  // Only calculate the per-universe weight for events that will actually use it.
                        if (closure) scale = 1.0;
                        FillSignalTruth(tag, universe, weight, variables, variables2D, variablesHD, scale);
                    }
                } else {  // kData
#ifdef CLOSUREDETAIL
                    if (closure && selection.isDataSelected(*universe, event).all()) {
                        std::cout << universe->GetRun() << " " << universe->GetSubRun() << " " << universe->GetGate() << " " << universe->GetPmuGeV() << " " << weight << " " << selection.isDataSelected(*universe, event).all() << " " << selection.isMCSelected(*universe, event, weight).all() << "  " << tag << "1"
                                  << " " << universe->ShortName() << std::endl;
                    }
#endif
                    if (selection.isDataSelected(*universe, event).all()) {
                        FillData(tag, universe, variables, variables2D, variablesHD);
                    }
                }
                // universe->ResetNeutEvent();
            }  // End universes
        }  // End error bands
    }  // End entries loop
    if (data_mc_truth == kMC && mc_reco_to_csv) {
        csvFile.close();
        std::string csvFileName = "mc_reco_entries_" + sample + "_" + cat + ".csv";
        std::cout << std::endl;
        std::cout << "MC Reco events for " << sample << " category " << cat << " saved to " << csvFileName;
        std::cout << std::endl;
    }
}

#endif  //__CINT__
