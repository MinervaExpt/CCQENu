#include "GetHyperDVariablesFromConfig.h"

#include <cassert>

#include "CVUniverse.h"
#include "VariableFromConfig.h"
#include "VariableHyperDFromConfig.h"
#include "utils/NuConfig.h"

std::vector<std::string> splitHD(std::string s, std::string delimiter) {
    size_t pos_start = 0, pos_end, delim_len = delimiter.length();
    std::string token;
    std::vector<std::string> res;

    while ((pos_end = s.find(delimiter, pos_start)) != std::string::npos) {
        token = s.substr(pos_start, pos_end - pos_start);
        pos_start = pos_end + delim_len;
        res.push_back(token);
    }

    res.push_back(s.substr(pos_start));
    return res;
}


// return a vector instead of a map (which is unneeded nowadays)
std::map<std::string, CCQENu::VariableHyperDFromConfig *> GetHyperDVariablesFromConfig(std::vector<std::string> varsHD, std::map<std::string, CCQENu::VariableFromConfig *> variablesmap, const std::vector<std::string> tags, const NuConfig configraw) {
    //=========================================
    // Constructor wants: name,
    //                    vector 1D VariableFromConfig's,
    //                    fors
    //
    // variablesmap is the output of from GetMapOfVariables
    // config is the whole config file since I need to loop over a vector of HyperDimensional
    // variables to analyze, which I need to pull from the config file
    // Might change what the constructor wants to just take in both that vector
    // and then the config.GetValue("AnalyzeHyperDVariables")
    //=========================================

    // this is the HyperD set that actually gets returned
    std::map<std::string, CCQENu::VariableHyperDFromConfig *> variablesHDmap;

    // configraw.Print();
    // Get the configs for *all* hyperD variables in your Variables config
    NuConfig config;
    if (configraw.IsMember("HyperD")) {
        config = configraw.GetValue("HyperD");
    } else {
        std::cout << "GetHyperDVariablesFromConfig: Warning: No HyperD variables configured." << std::endl;
        exit(1);
    }
    // Get the configs for all 1D variables in your Variables config (these likely contain more info than hyperD that you need)
    NuConfig config1D;
    if (configraw.IsMember("1D")) {
        config1D = configraw.GetValue("1D");
    } else {
        std::cout << "GetHyperDVariablesFromConfig: Warning: No 1D variables configured." << std::endl;
    }

    // Now loop over all the hyperD variables in your Variables config
    std::vector<std::string> keys = config.GetKeys();
    for (auto key : keys) {  // keys here is the list labelled "HyperD" in the Variables json file so you can define them all

        bool found = false;      // This is a bool to check that the variable you configured in your *Main* config are found
        NuConfig varconfig;      // This is the config for one HyperD variable from your Variable config
        for (auto v : varsHD) {  // varsHD is the list from the Main config
            if (v == key) {      // Only work on the vars configured in Variable config that are selected in your Main config
                found = true;

                // Get the config for the hyperD variable and pull out various info about it
                varconfig = config.GetValue(v);
                std::string nameHD = varconfig.GetString("name");                             // should be format xvar_yvar_zvar_..._dvar, matching names of vars in 1D
                std::vector<std::string> axisvarnamevec = varconfig.GetStringVector("vars");  // Should each match names in 1D vars
                int dim = axisvarnamevec.size();                                              // The dimension of the hyperD variable is number of axes it has
                std::vector<std::string> fors = {};                                           // What you want to fill hists of (e.g. data, selected_reco), defaults to all<-TODO in VariableHyperDFromConfig

                if (varconfig.IsMember("for"))
                    fors = varconfig.GetStringVector("for");

                EAnalysisType analysis_type = k1D;
                if (varconfig.IsMember("analysistype"))
                    analysis_type = (EAnalysisType)varconfig.GetInt("analysistype");

                // Make a bool vector to use to check that you have the corresponding 1D variable configured for each axis
                std::map<int, bool> foundvec;
                for (int i = 0; i < dim; i++)
                    foundvec[dim] = false;

                // Initialize vectors containing  configs,"fors", and their VariableFromConfigs for each axis
                std::vector<NuConfig> axisvarconfigvec;
                // std::vector<std::vector<std::string>> axisforsvec;  // TODO
                std::vector<CCQENu::VariableFromConfig *> axisvars;

                // Loop over each axis
                int i = 0;  // TODO: Find a better thing than this hack?
                for (auto axisname : axisvarnamevec) {
                    NuConfig axisvarconfig = config1D.GetValue(axisname);
                    // Store the config
                    axisvarconfigvec.push_back(axisvarconfig);
                    // Find each variable in input map and store the ones you need to build the HyperD variable
                    for (auto var : variablesmap) {
                        std::string varname = var.first;
                        // Check that name of axis is a name of an input variable
                        if (axisname == varname) {
                            // Put that input variable into vector to feed VarHyperD constructor, emplace_back (vs push_back) is used because its smarter idfk
                            // tmp_axisvars.emplace_back(variablesmap[varname]);
                            axisvars.emplace_back(variablesmap[varname]);

                            foundvec[i] = true;
                            i += 1;
                            std::cout << " GetHyperDVariablesFromConfig: added 1D var " << varname << std::endl;
                        }
                    }
                }
                // Double check every axis got found. May not be necessary.
                for (int i = 0; i < dim; i++) {
                    if (foundvec[i] == false) {
                        std::cout << " GetHyperDVariablesFromConfig: Warning - have requested an unimplimented 1D variable " << axisvarnamevec[i] << std::endl;
                        assert(0);
                    }
                }
                // const std::vector<CCQENu::VariableFromConfig*> axisvars = tmp_axisvars;
                // Initialize new hyper d variable and add the tags
                CCQENu::VariableHyperDFromConfig *varHDfromconfig = new CCQENu::VariableHyperDFromConfig(nameHD, axisvars, fors, analysis_type);
                varHDfromconfig->AddTags(tags);
                std::cout << "GetHyperDVariablesFromConfig: set up HyperDim variable " << nameHD << " of dimension " << dim << std::endl;
                // Add it to the map
                variablesHDmap[nameHD] = varHDfromconfig;
            }
        }
        // Check that your hyperD variable existed...
        // if (!found) {
        //     std::cout << "GetHyperDVariablesFromConfig: HyperD variable " << key << " configured but not requested in main config" << std::endl;
        // }
    }

    // check that all requested variables are defined.
    for (auto v : varsHD) {
        bool found = false;
        for (auto key : keys) {
            if (v == key) {
                found = true;
                break;
            }
        }
        if (!found) {
            std::cout << "GetHyperDVariablesFromConfig: Warning - have requested an unimplemented variable in GetHyperDVariablesFromConfig " << v << std::endl;
            assert(0);
        }
    }

    return variablesHDmap;
}

std::map<std::string, CCQENu::VariableHyperDFromConfig *> GetHyperDVariablesFromConfig(std::vector<std::string> varsHD, const std::vector<std::string> tags, const NuConfig configraw, const bool doresolution, const bool dotypes, const std::string tunedmc, const std::vector<std::string> fitsamples) {
    std::map<std::string, CCQENu::VariableHyperDFromConfig *> variablesHDmap;

    NuConfig configHD = Json::Value::null;
    if (configraw.IsMember("HyperD")) {
        configHD = configraw.GetValue("HyperD");
    } else {
        // std::cout << "GetHyperDVariablesFromConfig: Warning: No HyperD variables configured." << std::endl;
        std::cout << "GetHyperDVariablesFromConfig: Warning: No HyperD variables configured. Will try to build from 1D vars.." << std::endl;
        // exit(1);
    }
    // Get the configs for all 1D variables in your Variables config (these likely contain more info than hyperD that you need)
    NuConfig config1D = Json::Value::null;
    if (configraw.IsMember("1D")) {
        config1D = configraw.GetValue("1D");
    } else {
        std::cout << "GetHyperDVariablesFromConfig: Warning: No 1D variables configured." << std::endl;
        assert(0);
    }

    std::vector<std::string> keys = configHD.GetKeys();
    for (auto v : varsHD) {
        std::string nameHD = "";
        std::vector<std::string> axisvarnamevec = {};
        EAnalysisType analysis_type = k1D;
        bool _found_config = false;
        NuConfig varconfig = Json::Value::null;
        std::vector<std::string> fors = {};
        // if (!configHD.IsMember(v)) {
        // std::cout << "GetHDVariablesFromConfig: ERROR - have requested an unimplemented HyperDim variable in GetHDVariablesFromConfig " << v << std::endl;
        // assert(configHD.IsMember(v));
        // } else {
        if (configHD.IsMember(v)) {
            varconfig = configHD.GetValue(v);
            // std::string nameHD = varconfig.GetString("name");
            // std::vector<std::string> axisvarnamevec = varconfig.GetStringVector("vars");
            nameHD = varconfig.GetString("name");
            axisvarnamevec = varconfig.GetStringVector("vars");
            // int dim = axisvarnamevec.size();

            // EAnalysisType analysis_type = k1D;
            if (varconfig.IsMember("analysistype")) analysis_type = (EAnalysisType)varconfig.GetInt("analysistype");
            _found_config = true;
        } else {
            nameHD = v;
            axisvarnamevec = splitHD(nameHD, "_");
        }

        int dim = axisvarnamevec.size();
        if (dim == 0) {
            std::cout << "ERROR: didn't set up HD var correctly " << nameHD << std::endl;
            assert(0);
        }
        std::vector<CCQENu::VariableFromConfig *> vars1D = {};
        std::vector<std::string> tmp_fors = {};  // What you want to fill hists of (e.g. data, selected_reco), defaults to all<-TODO in VariableHyperDFromConfig

        for (auto var1D_name : axisvarnamevec) {
            if (!config1D.IsMember(var1D_name)) {
                std::cout << "GetHDVariablesFromConfig: ERROR - have requested an unimplemented 1D variable in GetHDVariablesFromConfig " << var1D_name << std::endl;
                assert(0);
            }
            CCQENu::VariableFromConfig *tmp_var1D = new CCQENu::VariableFromConfig(config1D.GetValue(var1D_name));

            tmp_var1D->SetDoResolution(doresolution);
            tmp_var1D->SetDoTypes(dotypes);
            tmp_var1D->SetTunedMC(tunedmc);
            tmp_var1D->SetFitSamples(fitsamples);
            tmp_var1D->AddTags(tags);

            for (auto f : tmp_var1D->m_for) {
                if (std::count(tmp_fors.begin(), tmp_fors.end(), f) == 0) {
                    tmp_fors.push_back(f);
                }
            }
            vars1D.emplace_back(tmp_var1D);
        }
        // Need to go back over to erase the fors that aren't shared between each 1D variable
        std::vector<std::string> new_fors = tmp_fors;  // What you want to fill hists of (e.g. data, selected_reco), defaults to all<-TODO in VariableHyperDFromConfig

        for (auto var : vars1D) {
            std::vector<std::string> var1d_fors = var->m_for;
            for (auto f : tmp_fors) {
                if (std::count(var1d_fors.begin(), var1d_fors.end(), f) == 0){
                    new_fors.erase(std::find(new_fors.begin(), new_fors.end(), f));
                }
            }
        }
        // for (auto var1D_name : axisvarnamevec) {
        //     CCQENu::VariableFromConfig *tmp_var1D = new CCQENu::VariableFromConfig(config1D.GetValue(var1D_name));
        //     std::vector<std::string> var1d_fors = tmp_var1D->m_for;
        //     for (auto f : tmp_fors) {
        //         if (std::find(var1d_fors.begin(), var1d_fors.end(), f) != var1d_fors.end())
        //             tmp_fors.erase(std::find(tmp_fors.begin(), tmp_fors.end(), f));
        //     }
        // }
        fors = new_fors;
        // std::vector<std::string> fors = {};  // What you want to fill hists of (e.g. data, selected_reco), defaults to all<-TODO in VariableHyperDFromConfig
        if (_found_config) fors = varconfig.IsMember("for") ? varconfig.GetStringVector("for"): tmp_fors;
        std::cout << ">>>>>>> fors found: ";
        for (auto f : fors) std::cout << "\t" << f;
        std::cout << std::endl;
        CCQENu::VariableHyperDFromConfig *varHD = new CCQENu::VariableHyperDFromConfig(nameHD, vars1D, fors, analysis_type);
        varHD->AddTags(tags);
        std::cout << "GetHyperDVariablesFromConfig: set up HyperDim variable " << nameHD << " of dimension " << dim << std::endl;
        variablesHDmap[nameHD] = varHD;
        for (auto var1D: vars1D) {
            delete var1D;
        }
    }
    return variablesHDmap;
}
