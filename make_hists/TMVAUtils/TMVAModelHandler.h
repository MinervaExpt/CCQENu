

std::vector<float> GetResponse(TMVA::Experimental::RReader model,
                               CVUniverse* univ) {
	std::vector<std::string> variables = model.GetVariableNames();
	std::vector<float> inputs;
	for (auto v : variables) {
		float v_val = v->GetRecoValue(*univ, 0);
		inputs.emplace_back(v_val);
	}
}
