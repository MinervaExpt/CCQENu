// include at top of your loop code


//==============================================================================
// Fill Data or MC histograms
//==============================================================================
void FillData(std::string tag, CVUniverse* univ,
              std::vector<CCQENu::VariableFromConfig*> variables,
              std::vector<CCQENu::Variable2DFromConfig*> variables2D) {
  for (auto v : variables) {
    if (v->hasData[tag]){
      double fill_val = v->GetRecoValue(*univ, 0);
      v->m_selected_data.Fill(tag, univ, fill_val);
    }
  }
  for (auto v2 : variables2D) {
    if (v2->hasData[tag]){
      double fill_val_x = v2->GetRecoValueX(*univ, 0);
      double fill_val_y = v2->GetRecoValueY(*univ, 0);
      v2->m_selected_data.Fill2D(tag, univ, fill_val_x, fill_val_y);
    }
  }
}



void FillMC(std::string tag, CVUniverse* univ, double weight,
            std::vector<CCQENu::VariableFromConfig*> variables,
            std::vector<CCQENu::Variable2DFromConfig*> variables2D,
            double scale == 1) {
  for (auto v : variables) {
    if (v->hasMC[tag]){
      double fill_val = v->GetRecoValue(*univ, 0);
      v->m_selected_mc_reco.Fill(tag, univ, fill_val, weight);
      if(v->hasTunedMC[tag]){
        double scaled_weight = scale*weight;
        // std::string tuned_tag = tag+"_tuned";
        v->m_tuned_mc_reco.Fill(tag, univ, fill_val, scaled_weight);
      }
    }
    if (v->hasSelectedTruth[tag]){
      double true_val = v->GetTrueValue(*univ, 0);
      v->m_selected_mc_truth.Fill(tag, univ, true_val, weight);
    }
  }
  for (auto v2 : variables2D) {
    if (v2->hasMC[tag]){
      double fill_val_x = v2->GetRecoValueX(*univ, 0);
      double fill_val_y = v2->GetRecoValueY(*univ, 0);
      v2->m_selected_mc_reco.Fill2D(tag, univ, fill_val_x, fill_val_y, weight);
      if(v2->hasTunedMC[tag]){
        double scaled_weight = scale*weight;
        // std::string rs_tag = tag+"_tuned";
        v2->m_tuned_mc_reco.Fill2D(tag, univ, fill_val_x, fill_val_y, scaled_weight);
      }
    }
    if (v2->hasSelectedTruth[tag]){
      double true_val_x = v2->GetTrueValueX(*univ, 0);
      double true_val_y = v2->GetTrueValueY(*univ, 0);
      v2->m_selected_mc_truth.Fill2D(tag, univ, true_val_x, true_val_y, weight);
    }
  }
}

void FillResponse(std::string tag,CVUniverse* univ, double weight,
            std::vector<CCQENu::VariableFromConfig*> variables,
            std::vector<CCQENu::Variable2DFromConfig*> variables2D) {
  for (auto v : variables) {
    if (v->hasResponse[tag]){
      double reco_val = v->GetRecoValue(*univ, 0);
      double true_val = v->GetTrueValue(*univ, 0);
      v->FillResponse(tag,univ,reco_val,true_val,weight);
    }
  }
  for (auto v2 : variables2D) {
    if (v2->hasResponse[tag]){
      double reco_val_x = v2->GetRecoValueX(*univ, 0);
      double reco_val_y = v2->GetRecoValueY(*univ, 0);
      double true_val_x = v2->GetTrueValueX(*univ, 0);
      double true_val_y = v2->GetTrueValueY(*univ, 0);
      v2->FillResponse2D(tag,univ,reco_val_x,reco_val_y,true_val_x,true_val_y,weight);
    }
  }
}



void FillSignalTruth(std::string tag, CVUniverse* univ, double weight,
               std::vector<CCQENu::VariableFromConfig*> variables,
               std::vector<CCQENu::Variable2DFromConfig*> variables2D) {
  int run = univ->GetTrueRun();
  int subrun = univ->GetTrueSubRun();
  int gate = univ->GetTrueGate();
  //if (run == 123000 && subrun == 288) return;
  for (auto v : variables) {
    if (v->hasTruth[tag]){
      double true_val = v->GetTrueValue(*univ, 0);
     // if (univ->ShortName() == "cv" ) std::cout << v->GetName() << " " << univ->GetEventID() << " " << run << " " << subrun << " "  <<  " "  << true_val << " " << weight << std::endl;
      v->m_signal_mc_truth.Fill(tag,univ, true_val, weight);
    }
  }
  for (auto v2 : variables2D) {
    if (v2->hasTruth[tag]){
      double true_val_x = v2->GetTrueValueX(*univ, 0);
      double true_val_y = v2->GetTrueValueY(*univ, 0);
     // if (univ->ShortName() == "cv" ) std::cout << v->GetName() << " " << univ->GetEventID() << " " << run << " " << subrun << " "  <<  " "  << true_val << " " << weight << std::endl;
      v2->m_signal_mc_truth.Fill2D(tag,univ, true_val_x, true_val_y, weight);
    }
  }
}

// Potentially deprecated 2D fillers
void FillData2D(std::string tag, CVUniverse* univ,
              std::vector<CCQENu::Variable2DFromConfig*> variables2D) {
  for (auto v : variables2D) {
    if (v->hasData[tag]){
    double fill_val_x = v->GetRecoValueX(*univ, 0);
    double fill_val_y = v->GetRecoValueY(*univ, 0);
    v->m_selected_data.Fill2D(tag, univ, fill_val_x, fill_val_y);
    }
  }
}

void FillMC2D(std::string tag, CVUniverse* univ, double weight,
            std::vector<CCQENu::Variable2DFromConfig*> variables2D) {
  for (auto v : variables2D) {
    if (v->hasMC[tag]){
      double fill_val_x = v->GetRecoValueX(*univ, 0);
      double fill_val_y = v->GetRecoValueY(*univ, 0);
      v->m_selected_mc_reco.Fill2D(tag, univ, fill_val_x, fill_val_y, weight);
    }
    if (v->hasSelectedTruth[tag]){
      double true_val_x = v->GetTrueValueX(*univ, 0);
      double true_val_y = v->GetTrueValueY(*univ, 0);
      v->m_selected_mc_truth.Fill2D(tag, univ, true_val_x, true_val_y, weight);
    }
  }
}

void FillResponse2D(std::string tag,CVUniverse* univ, double weight,
            std::vector<CCQENu::Variable2DFromConfig*> variables2D) {
  for (auto v : variables2D) {
    if (v->hasResponse[tag]){
    double reco_val_x = v->GetRecoValueX(*univ, 0);
    double reco_val_y = v->GetRecoValueY(*univ, 0);
    double true_val_x = v->GetTrueValueX(*univ, 0);
    double true_val_y = v->GetTrueValueY(*univ, 0);
    v->FillResponse2D(tag,univ,reco_val_x,reco_val_y,true_val_x,true_val_y,weight);
    }
  }
}

void FillSignalTruth2D(std::string tag, CVUniverse* univ, double weight,
               std::vector<CCQENu::Variable2DFromConfig*> variables2D) {
  int run = univ->GetTrueRun();
  int subrun = univ->GetTrueSubRun();
  int gate = univ->GetTrueGate();
  //if (run == 123000 && subrun == 288) return;
  for (auto v : variables2D) {
    if (v->hasTruth[tag]){
      double true_val_x = v->GetTrueValueX(*univ, 0);
      double true_val_y = v->GetTrueValueY(*univ, 0);
     // if (univ->ShortName() == "cv" ) std::cout << v->GetName() << " " << univ->GetEventID() << " " << run << " " << subrun << " "  <<  " "  << true_val << " " << weight << std::endl;
      v->m_signal_mc_truth.Fill2D(tag,univ, true_val_x, true_val_y, weight);
    }
   }
}
