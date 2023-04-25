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

//==============================================================================
// Fill Data or MC histograms
//==============================================================================
void FillData(std::string tag, CVUniverse *univ,
              std::vector<CCQENu::VariableFromConfig *> variables,
              std::vector<CCQENu::Variable2DFromConfig *> variables2D,
              std::vector<CCQENu::VariableHyperDFromConfig *> variablesHD) {
    for (auto v : variables) {
        if (v->hasData[tag]) {
            double fill_val = v->GetRecoValue(*univ, 0);
            v->m_selected_data.Fill(tag, univ, fill_val);
        }
    }
    for (auto v2 : variables2D) {
        if (v2->hasData[tag]) {
            double fill_val_x = v2->GetRecoValueX(*univ, 0);
            double fill_val_y = v2->GetRecoValueY(*univ, 0);
            v2->m_selected_data.Fill2D(tag, univ, fill_val_x, fill_val_y);
        }
    }
    for (auto vHD : variablesHD) {
        if (vHD->hasData[tag]) {
            double fill_val_lin_x = vHD->GetRecoValue(*univ, 0);
            if (vHD->GetAnalysisType() == k1D)
                vHD->m_selected_data.Fill(tag, univ, fill_val_lin_x);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            else if (vHD->GetAnalysisType() == k2D) {
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
        if (v->hasMC[tag]) {
            double fill_val = v->GetRecoValue(*univ, 0);
            if (v->m_tunedmc != 1) {
                v->m_selected_mc_reco.Fill(tag, univ, fill_val, weight);
            }
            if (v->hasTunedMC[tag] && scale >= 0.) {
                v->m_tuned_selected_mc_reco.Fill(tag, univ, fill_val, scale * weight);
            }
        }
        if (v->hasSelectedTruth[tag]) {
            double true_val = v->GetTrueValue(*univ, 0);
            if (v->m_tunedmc != 1) {
                v->m_selected_mc_truth.Fill(tag, univ, true_val, weight);
            }
            if (v->hasTunedMC[tag] && scale >= 0.) {
                v->m_tuned_selected_mc_truth.Fill(tag, univ, true_val, scale * weight);
            }
        }
    }
    for (auto v2 : variables2D) {
        if (v2->hasMC[tag]) {
            double fill_val_x = v2->GetRecoValueX(*univ, 0);
            double fill_val_y = v2->GetRecoValueY(*univ, 0);
            if (v2->m_tunedmc != 1) {
                v2->m_selected_mc_reco.Fill2D(tag, univ, fill_val_x, fill_val_y, weight);
            }
            if (v2->hasTunedMC[tag] && scale >= 0.) {
                v2->m_tuned_selected_mc_reco.Fill2D(tag, univ, fill_val_x, fill_val_y, scale * weight);
            }
        }
        if (v2->hasSelectedTruth[tag]) {
            double true_val_x = v2->GetTrueValueX(*univ, 0);
            double true_val_y = v2->GetTrueValueY(*univ, 0);
            if (v2->m_tunedmc != 1) {
                v2->m_selected_mc_truth.Fill2D(tag, univ, true_val_x, true_val_y, weight);
            }
            if (v2->hasTunedMC[tag] && scale >= 0.) {
                v2->m_tuned_selected_mc_truth.Fill2D(tag, univ, true_val_x, true_val_y, scale * weight);
            }
        }
    }
    for (auto vHD : variablesHD) {
        if (vHD->hasMC[tag]) {
            double fill_val_lin_x = vHD->GetRecoValue(*univ, 0);
            if (vHD->GetAnalysisType() == k1D) {
                if (vHD->m_tunedmc != 1)                                              // TODO: still need to set up tuned stuff for HyperD
                    vHD->m_selected_mc_reco.Fill(tag, univ, fill_val_lin_x, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                if (vHD->hasTunedMC[tag] && scale >= 0.)
                    vHD->m_tuned_selected_mc_reco.Fill(tag, univ, fill_val_lin_x, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            } else if (vHD->GetAnalysisType() == k2D) {
                double fill_val_y = vHD->GetRecoValue(1, *univ, 0);
                if (vHD->m_tunedmc != 1)                                                          // TODO: still need to set up tuned stuff for HyperD
                    vHD->m_selected_mc_reco.Fill(tag, univ, fill_val_lin_x, fill_val_y, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                if (vHD->hasTunedMC[tag] && scale >= 0.)
                    vHD->m_tuned_selected_mc_reco.Fill(tag, univ, fill_val_lin_x, fill_val_y, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            }
        }
        if (vHD->hasSelectedTruth[tag]) {
            double true_val_lin_x = vHD->GetTrueValue(*univ, 0);
            if (vHD->GetAnalysisType() == k1D) {
                if (vHD->m_tunedmc != 1)
                    vHD->m_selected_mc_truth.Fill(tag, univ, true_val_lin_x, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                if (vHD->hasTunedMC[tag] && scale >= 0.)
                    vHD->m_tuned_selected_mc_truth.Fill(tag, univ, true_val_lin_x, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            } else if (vHD->GetAnalysisType() == k2D) {
                double true_val_y = vHD->GetTrueValue(1, *univ, 0);
                if (vHD->m_tunedmc != 1)
                    vHD->m_selected_mc_truth.Fill(tag, univ, true_val_lin_x, true_val_y, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                if (vHD->hasTunedMC[tag] && scale >= 0.)
                    vHD->m_tuned_selected_mc_truth.Fill(tag, univ, true_val_lin_x, true_val_y, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            }
        }
    }
  }
}

void FillResolution(std::string tag, CVUniverse* univ, double weight,
            std::vector<CCQENu::VariableFromConfig*> variables,
            std::vector<CCQENu::Variable2DFromConfig*> variables2D,
            double scale=-1.) {
  for (auto v : variables) {
    if (v->hasResponse[tag]){
      double reco_val = v->GetRecoValue(*univ, 0);
      double true_val = v->GetTrueValue(*univ, 0);
      // This will fill both tuned and untuned
      v->FillResolution(tag,univ,reco_val,true_val,weight,scale);

    }
  }
}

void FillResponse(std::string tag, CVUniverse *univ, double weight,
                  std::vector<CCQENu::VariableFromConfig *> variables,
                  std::vector<CCQENu::Variable2DFromConfig *> variables2D,
                  std::vector<CCQENu::VariableHyperDFromConfig *> variablesHD,
                  double scale = -1.) {
    for (auto v : variables) {
        if (v->hasResponse[tag]) {
            double reco_val = v->GetRecoValue(*univ, 0);
            double true_val = v->GetTrueValue(*univ, 0);
            // This will fill both tuned and untuned
            v->FillResponse(tag, univ, reco_val, true_val, weight, scale);

            // if(v->m_tunedmc!=1){
            //   v->FillResponse(tag,univ,reco_val,true_val,weight);
            // }
            // if(v->hasTunedMC[tag] && scale>=0.){
            //   v->FillResponse(tag,univ,reco_val,true_val,scale*weight);
            // }
        }
    }
    for (auto v2 : variables2D) {
        if (v2->hasResponse[tag]) {
            double reco_val_x = v2->GetRecoValueX(*univ, 0);
            double reco_val_y = v2->GetRecoValueY(*univ, 0);
            double true_val_x = v2->GetTrueValueX(*univ, 0);
            double true_val_y = v2->GetTrueValueY(*univ, 0);
            v2->FillResponse2D(tag, univ, reco_val_x, reco_val_y, true_val_x, true_val_y, weight, scale);
            // if(v2->m_tunedmc!=1){
            //   v2->FillResponse2D(tag,univ,reco_val_x,reco_val_y,true_val_x,true_val_y,weight);
            // }
            // if(v2->hasTunedMC[tag] && scale>=0.){
            //   v2->FillResponse2D(tag,univ,reco_val_x,reco_val_y,true_val_x,true_val_y,scale*weight);
            // }
        }
    }
    for (auto vHD : variablesHD) {
        if (vHD->hasResponse[tag]) {
            double reco_val_lin_x = vHD->GetRecoValue(*univ, 0);
            double true_val_lin_x = vHD->GetTrueValue(*univ, 0);
            if (vHD->GetAnalysisType() == k1D)
                vHD->FillResponse(tag, univ, reco_val_lin_x, true_val_lin_x, weight, scale);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            else if (vHD->GetAnalysisType() == k2D) {
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
            double true_val = v->GetTrueValue(*univ, 0);
            // if (univ->ShortName() == "cv" ) std::cout << v->GetName() << " " << univ->GetEventID() << " " << run << " " << subrun << " "  <<  " "  << true_val << " " << weight << std::endl;
            if (v->m_tunedmc != 1) {
                v->m_signal_mc_truth.Fill(tag, univ, true_val, weight);
            }
            if (v->hasTunedMC[tag] && scale >= 0.) {
                v->m_tuned_signal_mc_truth.Fill(tag, univ, true_val, scale * weight);
            }
        }
    }
    for (auto v2 : variables2D) {
        if (v2->hasTruth[tag]) {
            double true_val_x = v2->GetTrueValueX(*univ, 0);
            double true_val_y = v2->GetTrueValueY(*univ, 0);
            // if (univ->ShortName() == "cv" ) std::cout << v->GetName() << " " << univ->GetEventID() << " " << run << " " << subrun << " "  <<  " "  << true_val << " " << weight << std::endl;
            if (v2->m_tunedmc != 1) {
                v2->m_signal_mc_truth.Fill2D(tag, univ, true_val_x, true_val_y, weight);
            }
            if (v2->hasTunedMC[tag] && scale >= 0.) {
                v2->m_tuned_signal_mc_truth.Fill2D(tag, univ, true_val_x, true_val_y, scale * weight);
            }
        }
    }
    for (auto vHD : variablesHD) {
        if (vHD->hasTruth[tag]) {
            double true_val_lin = vHD->GetTrueValue(*univ, 0);
            // if (univ->ShortName() == "cv" ) std::cout << v->GetName() << " " << univ->GetEventID() << " " << run << " " << subrun << " "  <<  " "  << true_val << " " << weight << std::endl;
            if (vHD->GetAnalysisType() == k1D) {
                if (vHD->m_tunedmc != 1)
                    vHD->m_signal_mc_truth.Fill(tag, univ, true_val_lin, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                if (vHD->hasTunedMC[tag] && scale >= 0.)
                    vHD->m_tuned_signal_mc_truth.Fill(tag, univ, true_val_lin, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            } else if (vHD->GetAnalysisType() == k2D) {
                double true_val_y = vHD->GetTrueValue(1, *univ, 0);
                if (vHD->m_tunedmc != 1)
                    vHD->m_signal_mc_truth.Fill(tag, univ, true_val_lin, true_val_y, weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
                if (vHD->hasTunedMC[tag] && scale >= 0.)
                    vHD->m_tuned_signal_mc_truth.Fill(tag, univ, true_val_lin, true_val_y, scale * weight);  // TODO: right now this is 1D HistWrapperMap method, may make HyperD it's own thing
            }
        }
    }
}
