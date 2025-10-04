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
 * Fillers actually fills the histograms, called from Loops
 * one addition is units of GeV and degrees where the base classes use MeV and radians
 */

// include at top of your loop code

// includes just to keep lint happy
#include <string>
#include <map>
#include <vector>
#include "CVUniverse.h"



//==============================================================================
// Fill Data or MC histograms
//==============================================================================
void FillData(std::string tag, CVUniverse *univ,
              std::vector<CCQENu::VariableFromConfig *> variables,
              std::vector<CCQENu::Variable2DFromConfig *> variables2D,
              std::vector<CCQENu::VariableHyperDFromConfig *> variablesHD) {
    for (auto v : variables) {
        if (v->hasData[tag]) {
            if (v->m_do_argvalue) {
                std::vector<double> fill_vals = v->GetArgRecoValue(*univ, v->GetRecoIndex(*univ));
                v->m_selected_data.Fill(tag, univ, fill_vals);
                continue;
            }
            double fill_val = v->GetRecoValue(*univ);
            v->m_selected_data.Fill(tag, univ, fill_val);
            v->FillForFit(tag, univ, fill_val);
        }
    }
    for (auto v2 : variables2D) {
        if (v2->hasData[tag]) {
            if (v2->m_do_argvalue_x || v2->m_do_argvalue_y) {
                int maxindex = v2->GetRecoIndex(*univ);
                std::vector<double> fill_vals_x = v2->GetArgRecoValueX(*univ, maxindex);
                std::vector<double> fill_vals_y = v2->GetArgRecoValueY(*univ, maxindex);
                v2->m_selected_data.Fill2D(tag, univ, fill_vals_x, fill_vals_y);
                continue;
            }
            double fill_val_x = v2->GetRecoValueX(*univ, 0);
            double fill_val_y = v2->GetRecoValueY(*univ, 0);
            v2->m_selected_data.Fill2D(tag, univ, fill_val_x, fill_val_y);
            v2->FillForFit2D(tag, univ, fill_val_x, fill_val_y); 
        }
    }
    for (auto vHD : variablesHD) {
        if (vHD->hasData[tag]) {
            if (vHD->m_do_argvalue) {
                int index = vHD->GetRecoIndex(*univ);
                std::vector<double> fill_vals_lin_x = vHD->GetArgRecoValue(*univ, index);
                if (vHD->GetAnalysisType() == k1D || vHD->GetAnalysisType() == k1D_lite) {
                    vHD->m_selected_data.Fill(tag, univ, fill_vals_lin_x);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                } else if (vHD->GetAnalysisType() == k2D || vHD->GetAnalysisType() == k2D_lite) {
                    std::vector<double> fill_vals_y = vHD->GetArgRecoValue(1, *univ, index);
                    double weight = 1.0;  // Needed for this method. Since data, weight is 1
                    vHD->m_selected_data.Fill(tag, univ, fill_vals_lin_x, fill_vals_y, weight);
                }
                continue;
            }
            double fill_val_lin_x = vHD->GetRecoValue(*univ, 0);
            if (vHD->GetAnalysisType() == k1D || vHD->GetAnalysisType() == k1D_lite) {
                vHD->m_selected_data.Fill(tag, univ, fill_val_lin_x);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            } else if (vHD->GetAnalysisType() == k2D || vHD->GetAnalysisType() == k2D_lite) {
                double fill_val_y = vHD->GetRecoValue(1, *univ, 0);
                double weight = 1.0;  // Needed for this method. Since data, weight is 1
                vHD->m_selected_data.Fill(tag, univ, fill_val_lin_x, fill_val_y, weight);
            }
        }
    }
}

void FillMC(std::string tag, CVUniverse *univ, double weight,
            std::vector<CCQENu::VariableFromConfig *> variables,
            std::vector<CCQENu::Variable2DFromConfig *> variables2D,
            std::vector<CCQENu::VariableHyperDFromConfig *> variablesHD,
            double scale = -1.) {
    for (auto v : variables) {
        if (v->m_do_argvalue) {
            if (v->hasMC[tag]) {
                std::vector<double> fill_vals = v->GetArgRecoValue(*univ, v->GetRecoIndex(*univ));
                if (v->m_tunedmc != "tuned") {
                    v->m_selected_mc_reco.Fill(tag, univ, fill_vals, weight);
                }
                if (v->hasTunedMC[tag] && scale >= 0.) {
                    v->m_tuned_selected_mc_reco.Fill(tag, univ, fill_vals, scale * weight);
                }
            }
            if (v->hasSelectedTruth[tag]) {
                std::vector<double> true_vals = v->GetArgTrueValue(*univ, v->GetTrueIndex(*univ));
                if (v->m_tunedmc != "tuned") {
                    v->m_selected_mc_truth.Fill(tag, univ, true_vals, weight);
                }
                if (v->hasTunedMC[tag] && scale >= 0.) {
                    v->m_tuned_selected_mc_truth.Fill(tag, univ, true_vals, scale * weight);
                }
            }
            continue;
        }
        if (v->hasMC[tag]) {
            double fill_val = v->GetRecoValue(*univ, 0);
            if (v->m_tunedmc != "tuned") {
                v->m_selected_mc_reco.Fill(tag, univ, fill_val, weight);
                v->FillForFit(tag, univ, fill_val, weight);
            }
            if (v->hasTunedMC[tag] && scale >= 0.) {
                v->m_tuned_selected_mc_reco.Fill(tag, univ, fill_val, scale * weight);
                v->FillForFit(tag, univ, fill_val, weight, scale);
            }
        }
        if (v->hasSelectedTruth[tag]) {
            double true_val = v->GetTrueValue(*univ, 0);
            if (v->m_tunedmc != "tuned") {
                v->m_selected_mc_truth.Fill(tag, univ, true_val, weight);
            }
            if (v->hasTunedMC[tag] && scale >= 0.) {
                v->m_tuned_selected_mc_truth.Fill(tag, univ, true_val, scale * weight);
            }
        }
    }
    for (auto v2 : variables2D) {
        if (v2->m_do_argvalue_x || v2->m_do_argvalue_y) {
            if (v2->hasMC[tag]) {
                int maxindex = v2->GetRecoIndex(*univ);
                std::vector<double> fill_vals_x = v2->GetArgRecoValueX(*univ, maxindex);
                std::vector<double> fill_vals_y = v2->GetArgRecoValueY(*univ, maxindex);
                if (v2->m_tunedmc != "tuned") {
                    v2->m_selected_mc_reco.Fill2D(tag, univ, fill_vals_x, fill_vals_y, weight);
                }
                if (v2->hasTunedMC[tag] && scale >= 0.) {
                    v2->m_tuned_selected_mc_reco.Fill2D(tag, univ, fill_vals_x, fill_vals_y, scale * weight);
                    // v2->FillForFit2D(tag, univ, fill_vals_x, fill_vals_y, scale * weight);
                }
            }
            if (v2->hasSelectedTruth[tag]) {
                int maxindex = v2->GetTrueIndex(*univ);
                std::vector<double> true_vals_x = v2->GetArgTrueValueX(*univ, maxindex);
                std::vector<double> true_vals_y = v2->GetArgTrueValueY(*univ, maxindex);
                if (v2->m_tunedmc != "tuned") {
                    v2->m_selected_mc_truth.Fill2D(tag, univ, true_vals_x, true_vals_y, weight);
                }
                if (v2->hasTunedMC[tag] && scale >= 0.) {
                    v2->m_tuned_selected_mc_truth.Fill2D(tag, univ, true_vals_x, true_vals_y, scale * weight);
                }
            }
            continue;
        }
        if (v2->hasMC[tag]) {
            double fill_val_x = v2->GetRecoValueX(*univ, 0);
            double fill_val_y = v2->GetRecoValueY(*univ, 0);
            if (v2->m_tunedmc != "tuned") {
                v2->m_selected_mc_reco.Fill2D(tag, univ, fill_val_x, fill_val_y, weight);
                v2->FillForFit2D(tag, univ, fill_val_x, fill_val_y, weight); 
            }
            if (v2->hasTunedMC[tag] && scale >= 0.) {
                v2->m_tuned_selected_mc_reco.Fill2D(tag, univ, fill_val_x, fill_val_y, scale * weight);
                v2->FillForFit2D(tag, univ, fill_val_x, fill_val_y, scale * weight); 
            }
        }
        if (v2->hasSelectedTruth[tag]) {
            double true_val_x = v2->GetTrueValueX(*univ, 0);
            double true_val_y = v2->GetTrueValueY(*univ, 0);
            if (v2->m_tunedmc != "tuned") {
                v2->m_selected_mc_truth.Fill2D(tag, univ, true_val_x, true_val_y, weight);
            }
            if (v2->hasTunedMC[tag] && scale >= 0.) {
                v2->m_tuned_selected_mc_truth.Fill2D(tag, univ, true_val_x, true_val_y, scale * weight);
            }
        }
    }
    for (auto vHD : variablesHD) {
        if (vHD->m_do_argvalue){
            if (vHD->hasMC[tag]) {
                int maxindex = vHD->GetRecoIndex(*univ);
                std::vector<double> fill_vals_lin_x = vHD->GetArgRecoValue(*univ, maxindex);
                if (vHD->GetAnalysisType() == k1D || vHD->GetAnalysisType() == k1D_lite) {
                    if (vHD->m_tunedmc != "tuned")                                        // TODO: still need to set up tuned stuff for HyperD
                        vHD->m_selected_mc_reco.Fill(tag, univ, fill_vals_lin_x, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                    if (vHD->hasTunedMC[tag] && scale >= 0.)
                        vHD->m_tuned_selected_mc_reco.Fill(tag, univ, fill_vals_lin_x, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                } else if (vHD->GetAnalysisType() == k2D) {
                    std::vector<double> fill_vals_y = vHD->GetArgRecoValue(1, *univ, maxindex);
                    if (vHD->m_tunedmc != "tuned")                                                    // TODO: still need to set up tuned stuff for HyperD
                        vHD->m_selected_mc_reco.Fill(tag, univ, fill_vals_lin_x, fill_vals_y, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                    if (vHD->hasTunedMC[tag] && scale >= 0.)
                        vHD->m_tuned_selected_mc_reco.Fill(tag, univ, fill_vals_lin_x, fill_vals_y, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                }
            }
            if (vHD->hasSelectedTruth[tag]) {
                int maxindex = vHD->GetTrueIndex(*univ);
                std::vector<double> true_vals_lin_x = vHD->GetArgTrueValue(*univ, maxindex);
                if (vHD->GetAnalysisType() == k1D || vHD->GetAnalysisType() == k1D_lite) {
                    if (vHD->m_tunedmc != "tuned")
                        vHD->m_selected_mc_truth.Fill(tag, univ, true_vals_lin_x, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                    if (vHD->hasTunedMC[tag] && scale >= 0.)
                        vHD->m_tuned_selected_mc_truth.Fill(tag, univ, true_vals_lin_x, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                } else if (vHD->GetAnalysisType() == k2D || vHD->GetAnalysisType() == k2D_lite) {
                    std::vector<double> true_vals_y = vHD->GetArgTrueValue(1, *univ, maxindex);
                    if (vHD->m_tunedmc != "tuned")                                                      // TODO: still need to set up tuned stuff for HyperD
                        vHD->m_selected_mc_truth.Fill(tag, univ, true_vals_lin_x, true_vals_y, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                    if (vHD->hasTunedMC[tag] && scale >= 0.)
                        vHD->m_tuned_selected_mc_truth.Fill(tag, univ, true_vals_lin_x, true_vals_y, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                }
            }
            continue;
        }
        if (vHD->hasMC[tag]) {
            double fill_val_lin_x = vHD->GetRecoValue(*univ);
            if (vHD->GetAnalysisType() == k1D || vHD->GetAnalysisType() == k1D_lite) {
                if (vHD->m_tunedmc != "tuned")                                        // TODO: still need to set up tuned stuff for HyperD
                    vHD->m_selected_mc_reco.Fill(tag, univ, fill_val_lin_x, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                if (vHD->hasTunedMC[tag] && scale >= 0.)
                    vHD->m_tuned_selected_mc_reco.Fill(tag, univ, fill_val_lin_x, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            } else if (vHD->GetAnalysisType() == k2D) {
                double fill_val_y = vHD->GetRecoValue(1, *univ);
                if (vHD->m_tunedmc != "tuned")                                                    // TODO: still need to set up tuned stuff for HyperD
                    vHD->m_selected_mc_reco.Fill(tag, univ, fill_val_lin_x, fill_val_y, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                if (vHD->hasTunedMC[tag] && scale >= 0.)
                    vHD->m_tuned_selected_mc_reco.Fill(tag, univ, fill_val_lin_x, fill_val_y, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            }
        }
        if (vHD->hasSelectedTruth[tag]) {
            double true_val_lin_x = vHD->GetTrueValue(*univ);
            if (vHD->GetAnalysisType() == k1D || vHD->GetAnalysisType() == k1D_lite) {
                if (vHD->m_tunedmc != "tuned")
                    vHD->m_selected_mc_truth.Fill(tag, univ, true_val_lin_x, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                if (vHD->hasTunedMC[tag] && scale >= 0.)
                    vHD->m_tuned_selected_mc_truth.Fill(tag, univ, true_val_lin_x, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            } else if (vHD->GetAnalysisType() == k2D || vHD->GetAnalysisType() == k2D_lite) {
                double true_val_y = vHD->GetTrueValue(1, *univ);
                if (vHD->m_tunedmc != "tuned")
                    vHD->m_selected_mc_truth.Fill(tag, univ, true_val_lin_x, true_val_y, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                if (vHD->hasTunedMC[tag] && scale >= 0.)
                    vHD->m_tuned_selected_mc_truth.Fill(tag, univ, true_val_lin_x, true_val_y, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            }
        }
    }
}

void FillResolution(std::string tag, CVUniverse *univ, double weight,
                    std::vector<CCQENu::VariableFromConfig *> variables,
                    std::vector<CCQENu::Variable2DFromConfig *> variables2D,
                    double scale = -1.) {
    for (auto v : variables) {
        // if (v->hasResponse[tag]) {
        if (v->hasResponse[tag] && !v->m_do_argvalue) {
            double reco_val = v->GetRecoValue(*univ);
            double true_val = v->GetTrueValue(*univ);
            // This will fill both tuned and untuned
            v->FillResolution(tag, univ, reco_val, true_val, weight, scale);
        }
    }
}

void FillType(std::string tag, CVUniverse *univ, double weight,
              std::vector<CCQENu::VariableFromConfig *> variables,
              std::vector<CCQENu::Variable2DFromConfig *> variables2D,
              double scale) {
    for (auto v : variables) {
        if (v->m_do_argvalue) continue; // TODO
        if (v->hasType[tag]) {
            // double reco_val = v->GetRecoValue(*univ, 0);
            int type = univ->GetMCIntType();
            for (int i = 0; i < v->GetRecoIndex(*univ); i++) {
                double reco_val = v->GetRecoValue(*univ, i);
                // This will fill both tuned and untuned
                v->FillType(tag, type, reco_val, weight, scale);
            }
        }
    }
}

void FillResponse(std::string tag, CVUniverse *univ, double weight,
                  std::vector<CCQENu::VariableFromConfig *> variables,
                  std::vector<CCQENu::Variable2DFromConfig *> variables2D,
                  std::vector<CCQENu::VariableHyperDFromConfig *> variablesHD,
                  double scale = -1.) {
    for (auto v : variables) {
        if (v->m_do_argvalue) continue; //TODO
        if (v->hasResponse[tag] && !v->m_do_argvalue) {
            double reco_val = v->GetRecoValue(*univ, 0);
            double true_val = v->GetTrueValue(*univ, 0);
            // This will fill both tuned and untuned
            v->FillResponse(tag, univ, reco_val, true_val, weight, scale);
        }
    }
    for (auto v2 : variables2D) {
        if (v2->m_do_argvalue_x || v2->m_do_argvalue_y) continue; // TODO
        if (v2->hasResponse[tag]) {
            double reco_val_x = v2->GetRecoValueX(*univ, 0);
            double reco_val_y = v2->GetRecoValueY(*univ, 0);
            double true_val_x = v2->GetTrueValueX(*univ, 0);
            double true_val_y = v2->GetTrueValueY(*univ, 0);
            v2->FillResponse2D(tag, univ, reco_val_x, reco_val_y, true_val_x, true_val_y, weight, scale);
        }
    }
    for (auto vHD : variablesHD) {
        if (vHD->m_do_argvalue) continue; // TODO
        if (vHD->hasResponse[tag]) {
            double reco_val_lin_x = vHD->GetRecoValue(*univ, 0);
            double true_val_lin_x = vHD->GetTrueValue(*univ, 0);
            if (vHD->GetAnalysisType() == k1D) {
                vHD->FillResponse(tag, univ, reco_val_lin_x, true_val_lin_x, weight, scale);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            } else if (vHD->GetAnalysisType() == k2D || vHD->GetAnalysisType() == k2D_lite) {
                double reco_val_y = vHD->GetRecoValue(1, *univ, 0);
                double true_val_y = vHD->GetTrueValue(1, *univ, 0);
                vHD->FillResponse(tag, univ, reco_val_lin_x, reco_val_y, true_val_lin_x, true_val_y, weight, scale);
            }
        }
    }
}

void FillSignalTruth(std::string tag, CVUniverse *univ, double weight,
                     std::vector<CCQENu::VariableFromConfig *> variables,
                     std::vector<CCQENu::Variable2DFromConfig *> variables2D,
                     std::vector<CCQENu::VariableHyperDFromConfig *> variablesHD,
                     double scale = -1.) {
    int run = univ->GetTrueRun();
    int subrun = univ->GetTrueSubRun();
    int gate = univ->GetTrueGate();
    // if (run == 123000 && subrun == 288) return;
    for (auto v : variables) {
        if (v->hasTruth[tag]) {
            if (v->m_do_argvalue) {
                std::vector<double> true_vals = v->GetArgTrueValue(*univ, v->GetTrueIndex(*univ));
                // if (univ->ShortName() == "cv" ) std::cout << v->GetName() << " " << univ->GetEventID() << " " << run << " " << subrun << " "  <<  " "  << true_val << " " << weight << std::endl;
                if (v->m_tunedmc != "tuned") {
                    v->m_signal_mc_truth.Fill(tag, univ, true_vals, weight);
                }
                if (v->hasTunedMC[tag] && scale >= 0.) {
                    v->m_tuned_signal_mc_truth.Fill(tag, univ, true_vals, scale * weight);
                }
                continue;
            }
            double true_val = v->GetTrueValue(*univ);
            // if (univ->ShortName() == "cv" ) std::cout << v->GetName() << " " << univ->GetEventID() << " " << run << " " << subrun << " "  <<  " "  << true_val << " " << weight << std::endl;
            if (v->m_tunedmc != "tuned") {
                v->m_signal_mc_truth.Fill(tag, univ, true_val, weight);
            }
            if (v->hasTunedMC[tag] && scale >= 0.) {
                v->m_tuned_signal_mc_truth.Fill(tag, univ, true_val, scale * weight);
            }
        }
    }
    for (auto v2 : variables2D) {
        if (v2->hasTruth[tag]) {
            if (v2->m_do_argvalue_x || v2->m_do_argvalue_y) {
                int maxindex = v2->GetTrueIndex(*univ);
                std::vector<double> true_vals_x = v2->GetArgTrueValueX(*univ, maxindex);
                std::vector<double> true_vals_y = v2->GetArgTrueValueY(*univ, maxindex);
                // if (univ->ShortName() == "cv" ) std::cout << v->GetName() << " " << univ->GetEventID() << " " << run << " " << subrun << " "  <<  " "  << true_val << " " << weight << std::endl;
                if (v2->m_tunedmc != "tuned") {
                    v2->m_signal_mc_truth.Fill2D(tag, univ, true_vals_x, true_vals_y, weight);
                }
                if (v2->hasTunedMC[tag] && scale >= 0.) {
                    v2->m_tuned_signal_mc_truth.Fill2D(tag, univ, true_vals_x, true_vals_y, scale * weight);
                }
                continue;
            }
            double true_val_x = v2->GetTrueValueX(*univ);
            double true_val_y = v2->GetTrueValueY(*univ);
            // if (univ->ShortName() == "cv" ) std::cout << v->GetName() << " " << univ->GetEventID() << " " << run << " " << subrun << " "  <<  " "  << true_val << " " << weight << std::endl;
            if (v2->m_tunedmc != "tuned") {
                v2->m_signal_mc_truth.Fill2D(tag, univ, true_val_x, true_val_y, weight);
            }
            if (v2->hasTunedMC[tag] && scale >= 0.) {
                v2->m_tuned_signal_mc_truth.Fill2D(tag, univ, true_val_x, true_val_y, scale * weight);
            }
        }
    }
    for (auto vHD : variablesHD) {
        if (vHD->hasTruth[tag]) {
            if (vHD->m_do_argvalue) {
                int maxindex = vHD->GetTrueIndex(*univ);
                std::vector<double> true_vals_lin = vHD->GetArgTrueValue(*univ, maxindex);
                // if (univ->ShortName() == "cv" ) std::cout << v->GetName() << " " << univ->GetEventID() << " " << run << " " << subrun << " "  <<  " "  << true_val << " " << weight << std::endl;
                if (vHD->GetAnalysisType() == k1D || vHD->GetAnalysisType() == k1D_lite) {
                    if (vHD->m_tunedmc != "tuned")
                        vHD->m_signal_mc_truth.Fill(tag, univ, true_vals_lin, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                    if (vHD->hasTunedMC[tag] && scale >= 0.)
                        vHD->m_tuned_signal_mc_truth.Fill(tag, univ, true_vals_lin, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                } else if (vHD->GetAnalysisType() == k2D || vHD->GetAnalysisType() == k2D_lite) {
                    std::vector<double> true_vals_y = vHD->GetArgTrueValue(1, *univ, maxindex);
                    if (vHD->m_tunedmc != "tuned")
                        vHD->m_signal_mc_truth.Fill(tag, univ, true_vals_lin, true_vals_y, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                    if (vHD->hasTunedMC[tag] && scale >= 0.)
                        vHD->m_tuned_signal_mc_truth.Fill(tag, univ, true_vals_lin, true_vals_y, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                }
                continue;
            }
            double true_val_lin = vHD->GetTrueValue(*univ);
            // if (univ->ShortName() == "cv" ) std::cout << v->GetName() << " " << univ->GetEventID() << " " << run << " " << subrun << " "  <<  " "  << true_val << " " << weight << std::endl;
            if (vHD->GetAnalysisType() == k1D || vHD->GetAnalysisType() == k1D_lite) {
                if (vHD->m_tunedmc != "tuned")
                    vHD->m_signal_mc_truth.Fill(tag, univ, true_val_lin, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                if (vHD->hasTunedMC[tag] && scale >= 0.)
                    vHD->m_tuned_signal_mc_truth.Fill(tag, univ, true_val_lin, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            } else if (vHD->GetAnalysisType() == k2D || vHD->GetAnalysisType() == k2D_lite) {
                double true_val_y = vHD->GetTrueValue(1, *univ);
                if (vHD->m_tunedmc != "tuned")
                    vHD->m_signal_mc_truth.Fill(tag, univ, true_val_lin, true_val_y, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                if (vHD->hasTunedMC[tag] && scale >= 0.)
                    vHD->m_tuned_signal_mc_truth.Fill(tag, univ, true_val_lin, true_val_y, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            }
        }
    }
}
