#include "utils/NuConfig.h"
#include "Get2DVariablesFromConfig.h"
#include "VariableFromConfig.h"
#include "Variable2DFromConfig.h"
#include "CVUniverse.h"
#include <cassert>

std::vector<std::string> intersection(std::vector<std::string> &v1, std::vector<std::string> &v2) {
    std::vector<std::string> v3;
    std::sort(v1.begin(), v1.end());
    std::sort(v2.begin(), v2.end());
    std::set_intersection(v1.begin(), v1.end(), v2.begin(), v2.end(), back_inserter(v3));
    return v3;
}

std::map<std::string, CCQENu::Variable2DFromConfig *> Get2DVariablesFromConfig(std::vector<std::string> vars2D, std::map<std::string, CCQENu::VariableFromConfig *> variablesmap, const std::vector<std::string> tags, const NuConfig configraw) {
    //=========================================
    // Constructor wants: name,
    //                    x VariableFromConfig, y VariableFromConfig
    //
    // variablesmap is the output of from GetMapOfVariables
    // config is the whole config file since I need to loop over a vector of 2D
    // variables to analyze, which I need to pull from the config file
    // Might change what the constructor wants to just take in both that vector
    // and then the config.GetValue("Analyze2DVariables")
    //=========================================
    bool is2D = false;
    std::map<std::string, CCQENu::Variable2DFromConfig *> variables2Dmap;  // this is the 2D set that actually gets returned

    // configraw.Print();
    NuConfig config;
    if (configraw.IsMember("2D")) {
        config = configraw.GetValue("2D");
    } else {
        std::cout << "No 2D variables configured." << std::endl;
        exit(1);
    }
    NuConfig config1D;
    if (configraw.IsMember("1D")) {
        config1D = configraw.GetValue("1D");
    } else {
        std::cout << "No 1D variables configured." << std::endl;
    }

    std::vector<std::string> keys = config.GetKeys();
    for (auto key : keys) {  // this is in the Variables json file so you can define them all
        bool found = false;
        NuConfig varconfig;
        for (auto v : vars2D) {  // this is from the master driver file so you can skip some
            if (v == key) {
                found = true;
                bool foundx = false;
                bool foundy = false;
                varconfig = config.GetValue(v);
                std::string name2D = varconfig.GetString("name");
                std::string xvarname = varconfig.GetString("xvar");
                std::string yvarname = varconfig.GetString("yvar");

                NuConfig xvarconfig = config1D.GetValue(xvarname);
                std::vector<std::string> xfor = {};
                if (xvarconfig.IsMember("for")) {
                    xfor = xvarconfig.GetStringVector("for");
                }
                NuConfig yvarconfig = config1D.GetValue(yvarname);
                std::vector<std::string> yfor = {};
                if (yvarconfig.IsMember("for")) {
                    yfor = yvarconfig.GetStringVector("for");
                }
                std::vector<std::string> fors = {};
                if (xfor.size() == 0) {
                    fors = yfor;
                } else if (yfor.size() == 0) {
                    fors = xfor;
                } else if (xfor.size() > 0 && yfor.size() > 0) {
                    fors = intersection(xfor, yfor);
                }

                CCQENu::VariableFromConfig *xvar;
                CCQENu::VariableFromConfig *yvar;

                for (auto var : variablesmap) {
                    std::string varname = var.first;
                    if (xvarname == varname) {
                        xvar = variablesmap[xvarname];
                        foundx = true;
                    }
                    if (yvarname == varname) {
                        yvar = variablesmap[yvarname];
                        foundy = true;
                    }
                }
                if (foundx && foundy) {
                    CCQENu::Variable2DFromConfig *var2Dfromconfig = new CCQENu::Variable2DFromConfig(name2D, *xvar, *yvar, fors);
                    var2Dfromconfig->AddTags(tags);
                    std::cout << "GetVariables2DFromConfig: set up 2D variable " << name2D << std::endl;
                    variables2Dmap[name2D] = var2Dfromconfig;
                } else if (!foundx) {
                    std::cout << " Warning - have requested an unimplemented 1D variable in Get2DVariablesFromConfig " << xvarname << std::endl;
                    assert(0);
                } else if (!foundy) {
                    std::cout << " Warning - have requested an unimplemented 1D variable in Get2DVariablesFromConfig " << yvarname << std::endl;
                    assert(0);
                }
            }
        }
        // if (!found) {
        //     std::cout << "Get2DVariablesFromConfig: 2D variable " << key << " configured but not requested in main config" << std::endl;
        // }
    }

    // check that all requested variables are defined.
    for (auto v : vars2D) {
        bool found = false;
        for (auto key : keys) {
            if (v == key) {
                found = true;
                break;
            }
        }

        if (!found) {
            std::cout << "Get2DVariablesFromConfig: Warning - have requested an unimplemented variable in Get2DVariablesFromConfig " << v << std::endl;
            assert(0);
        }
    }

    return variables2Dmap;
}

// std::vector<CCQENu::Variable2DFromConfig *> Get2DVariablesVecFromConfig(std::vector<std::string> vars2D, std::vector<CCQENu::VariableFromConfig *> variablesvec, const std::vector<std::string> tags, const NuConfig configraw) {
//     //=========================================
//     // Constructor wants: name,
//     //                    x VariableFromConfig, y VariableFromConfig
//     //
//     // variablesvec is the output of from this
//     // config is the whole config file since I need to loop over a vector of 2D
//     // variables to analyze, which I need to pull from the config file
//     // Might change what the constructor wants to just take in both that vector
//     // and then the config.GetValue("Analyze2DVariables")
//     //=========================================
//     bool is2D = false;
//     // std::map<std::string, CCQENu::Variable2DFromConfig *> variables2Dmap; // this is the 2D set that actually gets returned
//     std::vector<CCQENu::Variable2DFromConfig *> variables2Dvec;  // this is the 2D set that actually gets returned

//     // configraw.Print();
//     NuConfig config;
//     if (configraw.IsMember("2D")) {
//         config = configraw.GetValue("2D");
//     } else {
//         std::cout << "No 2D variables configured." << std::endl;
//         exit(1);
//     }
//     NuConfig config1D;
//     if (configraw.IsMember("1D")) {
//         config1D = configraw.GetValue("1D");
//     } else {
//         std::cout << "No 1D variables configured." << std::endl;
//     }

//     std::vector<std::string> keys = config.GetKeys();
//     for (auto key : keys) {  // this is in the Variables json file so you can define them all
//         bool found = false;
//         NuConfig varconfig;
//         for (auto v : vars2D) {  // this is from the master driver file so you can skip some
//             if (v == key) {
//                 found = true;
//                 bool foundx = false;
//                 bool foundy = false;
//                 varconfig = config.GetValue(v);
//                 std::string name2D = varconfig.GetString("name");
//                 std::string xvarname = varconfig.GetString("xvar");
//                 std::string yvarname = varconfig.GetString("yvar");

//                 NuConfig xvarconfig = config1D.GetValue(xvarname);
//                 std::vector<std::string> xfor = {};
//                 if (xvarconfig.IsMember("for")) {
//                     xfor = xvarconfig.GetStringVector("for");
//                 }
//                 NuConfig yvarconfig = config1D.GetValue(yvarname);
//                 std::vector<std::string> yfor = {};
//                 if (yvarconfig.IsMember("for")) {
//                     yfor = yvarconfig.GetStringVector("for");
//                 }
//                 std::vector<std::string> fors = {};
//                 if (xfor.size() == 0) {
//                     fors = yfor;
//                 } else if (yfor.size() == 0) {
//                     fors = xfor;
//                 } else if (xfor.size() > 0 && yfor.size() > 0) {
//                     fors = intersection(xfor, yfor);
//                 }

//                 CCQENu::VariableFromConfig *xvar;
//                 CCQENu::VariableFromConfig *yvar;
//                 // CCQENu::Variable2DFromConfig* var2Dfromconfig;

//                 // for (auto var : variablesmap)
//                 for (int i = 0; i < variablesvec.size(); i++) {
//                     // std::string varname = var.first;
//                     std::string varname = variablesvec[i]->GetName();
//                     if (xvarname == varname) {
//                         // xvar = variablesmap[xvarname];
//                         xvar = variablesvec[i];
//                         foundx = true;
//                     }
//                     if (yvarname == varname) {
//                         // yvar = variablesmap[yvarname];
//                         yvar = variablesvec[i];
//                         foundy = true;
//                     }
//                 }
//                 if (foundx && foundy) {
//                     // var2Dfromconfig = new CCQENu::Variable2DFromConfig(name2D,*xvar,*yvar,varconfig);
//                     // var2Dfromconfig = new CCQENu::Variable2DFromConfig(name2D,*xvar,*yvar,fors);
//                     CCQENu::Variable2DFromConfig *var2Dfromconfig = new CCQENu::Variable2DFromConfig(name2D, *xvar, *yvar, fors);
//                     var2Dfromconfig->AddTags(tags);
//                     std::cout << "GetVariables2DFromConfig: set up 2D variable " << name2D << std::endl;
//                     // variables2Dmap[name2D] = var2Dfromconfig;
//                     variables2Dvec.emplace_back(var2Dfromconfig);
//                 } else if (!foundx) {
//                     std::cout << " Warning - have requested an unimplemented 1D variable in Get2DVariablesFromConfig " << xvarname << std::endl;
//                     assert(0);
//                 } else if (!foundy) {
//                     std::cout << " Warning - have requested an unimplemented 1D variable in Get2DVariablesFromConfig " << yvarname << std::endl;
//                     assert(0);
//                 }
//             }
//         }
//         // if (!found) {
//         //     std::cout << "Get2DVariablesFromConfig: 2D variable " << key << " configured but not requested in main config" << std::endl;
//         // }
//     }

//     // check that all requested variables are defined.
//     for (auto v : vars2D) {
//         bool found = false;
//         for (auto key : keys) {
//             if (v == key) {
//                 found = true;
//                 break;
//             }
//         }

//         if (!found) {
//             std::cout << "Get2DVariablesFromConfig: Warning - have requested an unimplemented variable in Get2DVariablesFromConfig " << v << std::endl;
//             assert(0);
//         }
//     }

//     // return variables2Dmap;
//     return variables2Dvec;
// }
