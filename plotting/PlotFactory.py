import inspect
from re import L
import sys,os
import ROOT
ROOT.gROOT.SetBatch(True) # Run in batch mode
import numpy as np
from ROOT import (
    gROOT,
    gStyle, 
    TFile,
    THStack,
    TH1D,
    TH2D,
    TCanvas, 
    TColor,
    TObjArray,
    TH2F,
    THStack,
    TLegend,
    TLatex, 
    TString,
    TPad
)
# import PlotUtils
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter, HyperDimLinearizer, GridCanvas, MnvHist
import datetime
import ctypes
import math
import json, re
from optparse import OptionParser

mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")

varinfo_dict = {
    "x": {
        "shortname": "Eavail",
        "shortitle": "E_{Avail}^",
        "longtitle": "Available Energy",
        "units": "GeV",
        "logx": False,
        "logy": True,
    },
    "y": {
        "shortname": "ptmu",
        "shortitle": "p_{T}^",
        "longtitle": "Muon Transverse Momentum",
        "units": "GeV/c",
        "logx": False,
        "logy": False,
    },
    "xy": {
        "title": "Counts"
    }
}


def MakeTotalMCsInCCQENuDict(hist_dict):
    sig_cats = [
        "qelike_proton",
        "qelike_neutron"
    ]
    bkg_cats = [
        "chargedpion",
        "neutralpion",
        "other",
        "multipion",
    ]
    sig_tot_name = "qelike"
    bkg_tot_name = "qelikenot"
    mc_tot_name = "mctot"
    for a_hist in hist_dict:
        for b_sample in hist_dict[a_hist]:
            for c_var in hist_dict[a_hist][b_sample]:
                for d_stage in hist_dict[a_hist][b_sample][c_var]:
                    stage_dict = hist_dict[a_hist][b_sample][c_var][d_stage]
                    # TODO make total signal, total background, total mc

                    found_bkgs = True                    
                    if sig_tot_name not in stage_dict:
                        sig_type_dict = {}
                        first_type = True
                        for f_inttype in stage_dict[sig_cats[0]]:
                            if f_inttype not in sig_type_dict:
                                sig_type_dict[f_inttype] = {}
                            for e_cat in sig_cats:
                                if first_type:
                                    tmp_name = stage_dict[e_cat][f_inttype].GetName().replace(e_cat, sig_tot_name)
                                    sig_type_dict[f_inttype] = stage_dict[e_cat][f_inttype].Clone(tmp_name)
                                else:
                                    sig_type_dict[f_inttype].Add(stage_dict[e_cat][f_inttype])
                            first_type = False
                        hist_dict[a_hist][b_sample][c_var][d_stage][sig_tot_name] = sig_type_dict
                    if bkg_tot_name not in stage_dict:
                        bkg_type_dict = {}
                        first_type = True
                        for f_inttype in stage_dict[bkg_cats[0]]:
                            if f_inttype not in bkg_type_dict:
                                bkg_type_dict[f_inttype] = {}
                            for e_cat in bkg_cats:
                                if first_type:
                                    tmp_name = stage_dict[e_cat][f_inttype].GetName().replace(e_cat, bkg_tot_name)
                                    bkg_type_dict[f_inttype] = stage_dict[e_cat][f_inttype].Clone(tmp_name)
                                else:
                                    bkg_type_dict[f_inttype].Add(stage_dict[e_cat][f_inttype])
                            first_type = False
                        hist_dict[a_hist][b_sample][c_var][d_stage][bkg_tot_name] = bkg_type_dict
                    if mc_tot_name not in stage_dict:
                        mctot_type_dict = {}
                        for f_inttype in hist_dict[a_hist][b_sample][c_var][d_stage][bkg_tot_name]:
                            tmp_name = hist_dict[a_hist][b_sample][c_var][d_stage][bkg_tot_name].GetName().replace(bkg_tot_name, "mctot")
                            mctot_type_dict[f_inttype] = hist_dict[a_hist][b_sample][c_var][d_stage][bkg_tot_name].Clone(tmp_name)
                            mctot_type_dict[f_inttype].Add(hist_dict[a_hist][b_sample][c_var][d_stage][sig_tot_name])
                        hist_dict[a_hist][b_sample][c_var][d_stage]["mctot"] = mctot_type_dict
    return hist_dict


def MakePlotDir(subdir=""):
    """
    Subdir is the one for all plots that this script should ouptut. You will need to add
    any other subdirs in the script itself (e.g. based off input file name)
    """
    plotdir = ""
    base_plotdir = os.environ.get("PLOTSLOC")
    if base_plotdir != None:
        plotdir = os.path.join(base_plotdir, month + year)
    else:
        plotdir = os.path.join("/Users/nova/git/plots/", month + year)
    if not os.path.exists(plotdir):
        print("Can't find plot dir. Making it now... ", plotdir)
        os.makedirs(plotdir)
    if subdir == "":
        return plotdir
    if not os.path.exists(os.path.join(plotdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(plotdir, subdir))
        os.makedirs(os.path.join(plotdir, subdir))
    return os.path.join(plotdir, subdir)

def MakeThesisPlotDir(subdir = ""):
    plotdir = ""
    base_plotdir = os.environ.get("THESISPLOTDIR")
    if base_plotdir == None:
        return plotdir
    plotdir = base_plotdir
    if not os.path.exists(plotdir):
        print("Can't find plot dir. Making it now... ", plotdir)
        os.makedirs(plotdir)
    if subdir == "":
        return plotdir
    if not os.path.exists(os.path.join(plotdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(plotdir, subdir))
        os.makedirs(os.path.join(plotdir, subdir))
    return os.path.join(plotdir, subdir)


class PlotFactory:
    dummy_varinfo = {
            "shortname": "",
            "shorttitle": "",
            "longtitle": "",
            "units": "units",
            "logx": False,
            "logy": False
    }
    def __init__(self, main_config, samplestodo = "QElike" ):
        # Set the mainconfig. This does a whole lot under the hood.
        self.SetMainConfig(main_config)

        # set up the hists
        self.hist_list = self.GetInputHistList()

        # Sets up the vars to do based on input hists and what you say you want
        self.SetVarsToDo()
        self.SetSamplesToDo()

        self.do_modelcomp = False
        self.do_datacomp = False

    def __contains__(self, attribute_name):
        # Helper to check if something is stored in this
        return hasattr(self, attribute_name)

    def SetMainConfig(self, i_driver_config):
        """
        Set up the main config
        """
        if type(i_driver_config) == str:
            print("PlotFactory: Opening main config %s"%i_driver_config)
            # driver_config = json.loads(re.sub("//.*", "", i_driver_config, flags = re.MULTILINE))
            with open(os.path.expandvars(i_driver_config), "r",encoding="utf-8") as file:
                file_data = file.read()
                driver_config = json.loads(re.sub("//.*", "", file_data, flags = re.MULTILINE))
        elif type(i_driver_config) == dict:
            print("PlotFactory: Reading main config")
            driver_config = i_driver_config
        else:
            print("ERROR: main config looks like the wrong type. Exiting...")
            sys.exit(1)

        self.driver_config = driver_config

        # TODO maybe check these too, e.g. in case you're doing warping studies
        if "catgroupstodo" in driver_config:
            self.catgroupstodo = driver_config["catgroupstodo"]
        else:
            self.catgroupstodo = ["normal"]

        if "typecatgroupstodo" in driver_config:
            self.typecatgroupstodo = driver_config["typecatgroupstodo"]
        else:
            self.typecatgroupstodo = ["sigbkg"]

        if "stagestodo" in driver_config:
            self.stagestodo = driver_config["stagestodo"]
        else:
            self.stagestodo = ["reconstructed"]
        
        if "plotstyleconfigFile" in driver_config:
            plotstyle_config_path = driver_config["plotstyleconfigFile"]
            self.SetPlotStyleConfig(os.path.expandvars(plotstyle_config_path))

        self.base_model = "MnvTunev2.0.1"
        if "basemodel" in driver_config:
            self.base_model = driver_config["basemodel"]

        self.ratio_ref = "mctot"
        if "ratioref" in driver_config:
            self.ratio_ref = driver_config["ratioref"]

        self.typestacks = driver_config["typestacks"]
        self.catstacks = driver_config["catstacks"]
        self.ratiostacks = driver_config["ratiostacks"]
        
        if "inputfiles" in driver_config:
            inputfiles_dict_list = driver_config["inputfiles"]
            if len(inputfiles_dict_list) != 0:
                self.inputfiles_dict_list = inputfiles_dict_list

        if "mccatconfigFile" in driver_config:
            mccat_config_path = driver_config["mccatconfigFile"]
            self.SetMCCatConfig(os.path.expandvars(mccat_config_path))
        if "particlecatFile" in driver_config:
            particlecat_config_path = driver_config["particlecatconfigFile"]
            self.SetParticleCatConfig(os.path.expandvars(particlecat_config_path))
        if "stageconfigFile" in driver_config:
            stage_config_path = driver_config["stageconfigFile"]
            self.SetStageConfig(os.path.expandvars(stage_config_path))
        if "variableconfigFile" in driver_config:
            variable_config_path = driver_config["variableconfigFile"]
            self.SetVariableConfig(os.path.expandvars(variable_config_path))
        
        if "modelcompfilelist" in driver_config:
            self.modelcomp_path_list = driver_config["modelcompfilelist"]
            if "modelcompconfigFile" in driver_config:
                modelcomp_config_path = driver_config["modelcompconfigFile"]
            else:
                self.do_modelcomp = False
            if "modelcomptodo" in driver_config:
                self.modelcomptodo = driver_config["modelcomptodo"]
                if len(self.modelcomptodo) != 0:
                    self.do_modelcomp = True
        if "datacompfilelist" in driver_config:
            self.datacomp_path_list = driver_config["datacompfilelist"]
            # self.do_datacomp = True
            if "datacomptodo" in driver_config:
                self.datacomptodo = driver_config["datacomptodo"]
                if len(self.datacomptodo) != 0:
                    self.do_datacomp = True
        
        if "errorsumm" in driver_config:
            self.errorsumm = driver_config["errorsumm"]
            if len(self.errorsumm) != 0:
                self.do_errorsumm = True

        # TODO
        errorsumm_config_path = driver_config["particlecatconfigFile"]


    def SetMCCatConfig(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            file_data = file.read()
            config = json.loads(re.sub("//.*", "", file_data, flags = re.MULTILINE))
        
        catgroups = config["groups"]
        typecatgroups = config["groups"]
        self.catgroups = {key: value for key, value in catgroups.items() if key in self.catgroupstodo}
        self.typecatgroups = {key: value for key, value in typecatgroups.items() if key in self.typecatgroupstodo} 

        self.signalcats = config["signalcats"]
        self.backgroundcats = config["backgroundcats"]

        self.catnames = config["catnames"]
        self.catscolors = config["catscolors"]

        self.typesnames = {int(key): value for key, value in config["typesnames"].items()}
        self.typescolors = {int(key): value for key, value in config["typescolors"].items()}
        self.typesorder = [int(inttype) for inttype in config["typesorder"]]
        
        self.samplenames = config["samplenames"]

    # TODO
    def SetParticleCatConfig(self, file_path):
        return

    def SetStageConfig(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            file_data = file.read()
            config = json.loads(re.sub("//.*", "", file_data, flags = re.MULTILINE))
        # The raw dicts
        stages_dict = config["stages"]
        mcstages_dict = config["mcstages"]
        datastages_dict = config["datastages"]
        stagetuning_dict = config["stagetunecombo"]

        # The same dicts with only the stages you want to do
        # This is all the stages with information about them
        self.stages_dict = {key: value for key, value in stages_dict.items() if key in self.stagestodo}
        # These are the stages that need data
        self.mcstages_dict = {key: value for key, value in mcstages_dict.items() if key in self.stagestodo}
        # These are the stages that need mc
        self.datastages_dict = {key: value for key, value in datastages_dict.items() if key in self.stagestodo}
        # This is the combinations of tuned/untuned data and mc that you use
        self.stagetuning_dict = {key: value for key, value in stagetuning_dict.items() if key in self.stagestodo}
    
    def SetVariableConfig(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            file_data = file.read()
            config = json.loads(re.sub("//.*", "", file_data, flags = re.MULTILINE))
        self.varinfo_config = config["vars"]
        return

    # TODO
    def SetModelCompConfig(self, file_path):
        return
    
    # TODO
    def SetErrorSummConfig(self, file_path):
        return

    def SetPlotStyleConfig(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            file_data = file.read()
            config = json.loads(re.sub("//.*", "", file_data, flags = re.MULTILINE))
        self.plotstyle_config = config
        
        self.typesnames = {int(key): value for key, value in config["typesnames"].items()}
        self.typescolors = {int(key): value for key, value in config["typescolors"].items()}
        self.catnames = config["catnames"]
        self.catscolors = config["catscolors"]
        self.samplenames = config["samplenames"]
        
        if "1D" in config:
            self.line_width_1d = config["1D"]["linewidth"]
            self.data_marker_size_1d = config["1D"]["datamarkersize"]
            self.end_error_size_1d = config["1D"]["enderrorsize"]
        if "2D" in config:
            self.line_width_2d = config["2D"]["linewidth"]
            self.data_marker_size_2d = config["2D"]["datamarkersize"]
            self.end_error_size_2d = config["2D"]["enderrorsize"]
            

        self.band_alphalevel = 0.3
        if "bandalpha" in config:
            self.band_alphalevel = config["bandalpha"]

    def SetSamplesToDo(self):
        
        available_samples = []
        for histdict in self.hist_list:
            if histdict["sample"] not in available_samples:
                available_samples.append(histdict["sample"])
        
        tmp_samplestodo = []
        if "samplestodo" in self.driver_config:
            tmp_samplestodo = self.driver_config["samplestodo"]

        # if len(tmp_samplestodo) == 0:
        #     self.samplestodo = available_samples
        #     return
        
        samplestodo = [sample for sample in tmp_samplestodo if sample in available_samples]
        if len(samplestodo) == 0:
            samplestodo = available_samples
        self.samplestodo = samplestodo
        print("samplestodo: ", samplestodo)
        
    def SetVarsToDo(self):
        """
        Find the vars you want to do and the vars you can do based on members. Assign a list of the intersection of those.
        """
        print("PlotFactory: \tFinding what vars to do")
        # First find the vars available to you
        available_vars = []
        for histdict in self.hist_list:
            if histdict["var"] not in available_vars:
                available_vars.append(histdict["var"])
        
        tmp_varstodo = []
        if "varstodo" in self.driver_config:
            if len(self.driver_config["varstodo"]) != 0:
                tmp_varstodo = self.driver_config["varstodo"]
        elif 'varstodo' in self:
            tmp_varstodo = self.varstodo
                    
        # for var in tmp_varstodo:
        #     if var not in available_vars:
        #         print("\tRequested var %s not in available vars, will not do it"%var)
        # for var in available_vars:
        #     if var not in tmp_varstodo:
        #         print("\tAvailable var %s not in requested vars, will not do it"%var)
        varstodo = [var for var in available_vars if var in tmp_varstodo]
        if len(varstodo) == 0:
            varstodo = available_vars
        self.varstodo = varstodo
        print("varstodo: ", self.varstodo)

        master_varinfo_dict = {}
        for var in self.varstodo:
            varlist = [var]
            if "_" in var:
                varlist = var.split("_")
            tmp_varinfo_dict = {}
            for i in range(len(varlist)):
                if i == 0: axis = "x"
                elif i == 1: axis = "y"
                # elif i == 2: axis = "z"
                else: 
                    print("something wrong, bad var has too many _ %s"%varlist[i])
                    sys.exit(1)
                if varlist[i] in self.varinfo_config:
                    tmp_varinfo_dict[axis] = self.varinfo_config[varlist[i]]
                else:
                    print(">>>>>>>>>>>>>> Missing var %s in varconfig. Using dummy for now."%varlist[i])
                    tmp_dummy_varinfo = self.dummy_varinfo
                    tmp_dummy_varinfo["shortname"] = varlist[i]
                    tmp_dummy_varinfo["shorttitle"] = varlist[i]
                    tmp_dummy_varinfo["longtitle"] = varlist[i]
                    tmp_varinfo_dict[axis] = tmp_dummy_varinfo
            master_varinfo_dict[var] = tmp_varinfo_dict
        self.master_varinfo_dict = master_varinfo_dict        
    
    def GetInputHistList(self, i_file_dict_list = []):
        """
        This looks at files in a dict, with the path, the model used, and "istuned" set for analyze hists.
        This expects hists to have CCQENu style hist naming or anlyze style. You can use this for modelcomp and datacomp too maybe
        """
        tmp_file_dict_list = i_file_dict_list
        if len(tmp_file_dict_list) == 0:
            tmp_file_dict_list = self.inputfiles_dict_list
        
        # If you're looping over multiple files, ROOT wants you to put them somewhere. 
        # Just make a copy of the dict with the file in it
        # file_dict_list = []
        # for file_dict in tmp_file_dict_list:
        #     tmp_dict = {}
        #     tmp_dict["file"] = TFile.Open(file_dict["file"], "READONLY")
        #     for key in file_dict:
        #         if key == "file": continue
        #         tmp_dict[key] = file_dict[key]
        #     file_dict_list.append(tmp_dict)
        
        # Now build the list, will take multiple inputs 
        hist_dict_list = []
        for file_dict in tmp_file_dict_list:
            if "model" in file_dict:
                model = file_dict["model"]
            if "tune" in file_dict:
                model = file_dict["tune"]
            if "MnvTune" in file_dict:
                model = file_dict["MnvTune"]
            opts = ["dotuned", "dountuned"]
            if "istuned" in file_dict:
                istuned = file_dict["istuned"]
                if istuned: opts = ["dotuned"]
                else: opts = ["dountuned"]
            POTScale = -1.0
            if "analyze9" in file_dict["file"] or  "potscaled" in file_dict["file"]:
                POTScale = -1.0
            # else:

            # print(type(file_dict["file"]))
            # This builds the list for the file. Hopefully there are no repeats
            # with ROOT.TFile.Open(file_dict["file"], "READONLY") as tmpfile:
            #     print(type(tmpfile))
            #     tmp_dict_list = self.MakeHistDictListFromFile(
            #         i_file = tmpfile, 
            #         model = model, 
            #         opts = opts,
            #     )
            # print(file_dict["file"])
            tmp_dict_list = self.MakeHistDictListFromFile(
                i_file = file_dict["file"], 
                model = model, 
                POTScale = POTScale,
                opts = opts,
            )
            hist_dict_list += tmp_dict_list
        # Return it
        return hist_dict_list

    def MakeHistDictListFromFile(self, i_file, model = "MnvTunev2.0.1", POTScale = -1.0, opts = ["dotuned", "dountuned"]):
        """
        Set up the list of hists with a dict of info about them 

        Args:
            i_file (TFile)
            model (str)
            opts (list of str): set dotuned if you want tuned hists, set dountuned to do those

        """
        hist_dict_list = []
        with ROOT.TFile.Open(i_file, "READONLY") as tmp_file:
            # keys = i_file.GetListOfKeys()
            keys = tmp_file.GetListOfKeys()
            for k in keys:
                name = k.GetName()
                inttype = 0
                if "___" in name:
                    parse = name.split("___")
                    if len(parse) < 5: 
                        continue
                    hist = parse[0]
                    sample = parse[1]
                    cat = parse[2]
                    variable = parse[3]
                    stage = parse[4] # equivalent to recotrutype
                    if "tuned" in stage:
                        if "dotuned" not in opts: continue
                        tuned = "tuned"
                        stage.replace("_tuned","")
                    else:
                        if "dountuned" not in opts: continue
                        tuned = "untuned"
                    if "types" in stage:
                        if int(stage.split("_")[-1]) == 0: continue
                        inttype = int(stage.split("_")[-1])
                        stage = stage.replace("_types_%s"%(parse[4].split("_")[-1]), "")
                    if "response" in stage:
                        if "migration" in stage:
                            stage = "migration"
                        else:
                            continue
                    # if cat != "data" and stage != whichmcstage:
                    #     continue
                    # if cat == "data" and stage != whichdatastage:
                    #     continue
                # Do the analyze hists
                elif "_" in name:
                    # No way to check for analyze hists if they're tuned other than knowing before hand
                    if "dotuned" in opts: 
                        tuned = "tuned"
                    if "dountuned" in opts: 
                        tuned = "untuned"
                    if name in ["flux_dewidthed" "POT_summary"]: continue
                    if "POT_Summary" in name or "POT_summary" in name: continue
                    # if type(i_file.Get(name)) not in [type(MnvH1D()), type(MnvH2D()), type(TH1D()), type(TH2D())]:
                    if type(tmp_file.Get(name)) not in [type(MnvH1D()), type(MnvH2D()), type(TH1D()), type(TH2D())]:
                        continue
                    parse = name.split("_")
                    if len(parse) < 3: continue
                    hist = parse[0]
                    sample = parse[1]
                    variable = parse[2]
                    shift = 0
                    if hist=="h2D":
                        variable+="_"+parse[3]
                        shift = 1
                    # TODO need to figure out if mc_tot, mc_bkg_tot, signalfraction, bkgfraction ,etc should be kept...
                    # if parse[3+shift] in ["mc","signalfraction", "bkgfraction",]:
                    #     continue
                    elif parse[3+shift] in ["efficiency", "sigmaMC","mc","signalfraction", "bkgfraction",]:
                        cat = "qelike"
                    else:
                        cat = "data"
                    typeshift = 0
                    if "types" in parse:
                        if int(parse[-1]) == 0: continue
                        inttype = int(parse[-1])
                        typeshift = 2

                    stage = parse[len(parse) - typeshift - 1]
                    if "unfold" in stage and "unfolded" not in stage: 
                        stage.replace("unfold","unfolded") # maybe this has been fixed...
                    tmp_POTScale = -1.0
                    is_analyze = True
                else:
                    continue
                # if type(i_file.Get(name)) not in [
                if type(tmp_file.Get(name)) not in [
                    type(MnvH1D()), type(MnvH2D()), type(TH1D()), type(TH2D())
                ]:
                    continue
                
                # h = i_file.Get(name).Clone()
                h = tmp_file.Get(name).Clone()
                h.SetDirectory(ROOT.nullptr)
                if h.GetEntries() <= 0:
                    if inttype%10 in [4]:
                        h.Print()
                    else:
                        continue
                h = self.MakeHistPretty(
                    i_hist = h,
                    cat = cat,
                    inttype = inttype
                )
                print("found hist %s"%name)
                tmp_dict = {
                    "hist": h,
                    "sample": sample,
                    "cat": cat,
                    "var": variable,
                    "inttype": inttype,
                    "tuned": tuned,
                    "stage": stage,
                    "model": model,
                }
                hist_dict_list.append(tmp_dict)
        return hist_dict_list

    def MakeInputDataHistDict(self, whichsample, whichvar, whichstage = "reconstructed", dotuned = "tuned"):
        out_dict = {}
        for hist_dict in self.hist_list:
            if hist_dict["cat"] != "data":
                continue
            if hist_dict["var"] != whichvar:
                continue
            if hist_dict["stage"] != whichstage:
                continue
            if hist_dict["sample"] != whichsample:
                continue
            # if dotuned and hist_dict["tuned"] != "tuned":
            if dotuned != hist_dict["tuned"]:
                continue
            hist = hist_dict["hist"].Clone()
            if hist_dict["model"] == self.base_model:
                out_dict["base"] = self.MakeHistPretty(
                    i_hist = hist,
                    cat = "data",
                    datacomp = ""
                )
            elif self.do_datacomp:
                out_dict[hist_dict["model"]] = self.MakeHistPretty(
                    i_hist = hist,
                    cat = "data",
                    datacomp = hist_dict["model"]
                )

        return out_dict

    def MakeInputMCHistDict(self, whichsample, whichvar, whichstage = "reconstructed", dotuned = "tuned", catgroup = [], dotypes = False):
        if len(catgroup) == 0:
            if dotypes: catgroup = sigbkg
            else: catgroup = normal
        # This is helpful for later
        tmp_dict = {}
        # First loop through the list and grab the hists
        for hist_dict in self.hist_list:
            if hist_dict["cat"] == "data":
                continue
            if hist_dict["cat"] not in catgroup:
                continue
            if hist_dict["sample"] != whichsample:
                continue
            if hist_dict["var"] != whichvar:
                continue
            if hist_dict["stage"] != whichstage:
                continue
            if dotuned != hist_dict["tuned"]:
                continue
            # if dotuned and hist_dict["tuned"] != "tuned":
            #     continue
            # if not dotuned and hist_dict["tuned"] != "untuned":
            #     continue
            # If not doing types, only look at the total hist for the cat and key outdict to the cat
            if not dotypes:
                if hist_dict["inttype"] != 0:
                    continue
                key = hist_dict["cat"]
            # If doing types, ignore total cat hists except for mctot
            else:
                if hist_dict["inttype"] == 0 and hist_dict["cat"] != "mctot":
                    continue
                # key to the inttype and increment the key for each separate cat
                key = hist_dict["inttype"]
                key += 10 * catgroup.index(hist_dict["cat"])
            tmp_hist = self.MakeHistPretty(
                i_hist = hist_dict["hist"].Clone(),
                cat = hist_dict["cat"],
                inttype = hist_dict["inttype"]
            )
            
            # tmp_dict[key] = hist_dict["hist"].Clone()
            tmp_dict[key] = tmp_hist
        # print(tmp_dict)
        # If you're doing types, order these based on the inttype
        if dotypes:
            # First, make a new types order that you can extend for each cat's increment
            tmp_typesorder = [0]
            for i in range(len(catgroup)):
                for inttype in self.typesorder:
                    inc_inttype = inttype + i * 10
                    if inc_inttype not in tmp_dict: continue
                    tmp_typesorder.append(inc_inttype)
            out_dict = {}
            for key in tmp_typesorder:
                # rename the total mc hist
                if key == 0 and key in tmp_dict and "mctot" not in tmp_dict:
                    out_dict["mctot"] = tmp_dict[key]
                    continue
                # skip the cat total hists
                elif key%10 == 0:
                    continue
                out_dict[key] = tmp_dict[key]
        # If doing cats, order these based on your catgroup order
        else:
            out_dict = {}
            if "mctot" in tmp_dict:
                out_dict["mctot"] = tmp_dict["mctot"].Clone()
            for key in catgroup:
                if key not in tmp_dict: continue
                if key == "mctot": continue
                out_dict[key] = tmp_dict[key].Clone()
        if len(out_dict) == 0:
            return out_dict
        if "mctot" not in out_dict:
            first = True
            mctot = out_dict[list(out_dict.keys())[0]].Clone(out_dict[key].GetName().replace(key, "mctot"))
            for key in out_dict:
                if first:
                    # mctot = out_dict[key].Clone(out_dict[key].GetName().replace(key, "mctot"))
                    first = False
                else:
                    mctot.Add(out_dict[key])
            mctot = self.MakeHistPretty(mctot, "mctot")
            out_dict["mctot"] = mctot
        return out_dict

    def MakeInputHistDict(self, whichsample, whichvar, whichstage, dodatatuned = "untuned", domctuned = "untuned", catgroup = [], dotypes = False):
        out_input_dict = {}
        if whichstage in self.datastages_dict:
            data_stage = self.datastages_dict[whichstage]
            data_dict = self.MakeInputDataHistDict(
                whichsample = whichsample, 
                whichvar = whichvar,
                whichstage = data_stage,
                dotuned = dodatatuned 
            )
            if len(data_dict) != 0:
                out_input_dict["data"] = data_dict
        if whichstage in self.mcstages_dict:
            mc_stage = self.mcstages_dict[whichstage]
            mc_dict = self.MakeInputMCHistDict(
                whichsample = whichsample, 
                whichvar = whichvar,
                whichstage = mc_stage,
                dotuned = domctuned,
                catgroup = catgroup,
                dotypes = dotypes
            )
            if len(mc_dict) != 0:
                out_input_dict["mc"] = mc_dict
        # TODO modelcomp
        return out_input_dict

    def MakePlotHist(self, whichsample, whichvar, whichstage, dodatatuned = "tuned", domctuned = "untuned", catgroup = [], dotypes = False):
        input_dict = self.MakeInputHistDict(
            whichsample = whichsample,
            whichvar = whichvar,
            whichstage = whichstage,
            dodatatuned = dodatatuned,
            domctuned = domctuned,
            catgroup = catgroup, 
            dotypes = dotypes
        )
        if whichstage in self.datastages_dict and "data" not in input_dict:
            return False
        if whichstage in self.mcstages_dict and "mc" not in input_dict:
            return False

        dim = "1d"
        for datamc in input_dict:
            # print("found %s"%datamc)
            for key in input_dict[datamc]:
                # print("found %s"%key)
                if type(input_dict[datamc][key]) in [type(MnvH1D()), type(TH1D())]:
                    dim = "1d"
                elif type(input_dict[datamc][key]) in [type(MnvH2D()), type(TH2D())]:
                    dim = "2d"
                else:
                    print("PlotFactory.MakePlotHist: \tERROR: hists aren't hist in this dict")
                    sys.exit(1)
        plothist_list = []
        if dim == "2d":
            tmp_plothist = PlotHist2D(
                i_hist_dict = input_dict,
                title = "",
                i_varinfo_dict = self.master_varinfo_dict[whichvar],
                opts = []
            )
            tmp_plothist.SetGridCanvas()
            tmp_plothist.DrawPanelsOnGridCanvas()
        else: # if dim == "1d":
            tmp_plothist = PlotHist1D(
                i_hist_dict = input_dict,
                title = "",
                i_varinfo_dict = self.master_varinfo_dict[whichvar],
                opts = []
            )            
        return tmp_plothist

    def MakeAllPlotHists(self):
        plothist_list = []
        for sample in self.samplestodo:
            for var in self.varstodo:
                for stage in self.stagestodo:
                    for tunecombo in self.stagetuning_dict[stage]:
                        dodatatuned = "untuned"
                        if "data" in tunecombo:
                            dodatatuned = tunecombo["data"]
                        domctuned = "untuned"
                        if "mc" in tunecombo:
                            domctuned = tunecombo["mc"]
                        for catgroup in self.catgroupstodo:
                            plothist = self.MakePlotHist(
                                whichsample = sample,
                                whichvar = var,
                                whichstage = stage,
                                dodatatuned = dodatatuned,
                                domctuned = domctuned,
                                catgroup = self.catgroups[catgroup],
                                dotypes = False,
                            )
                            if plothist:
                                plothist_list.append(plothist)
                        for catgroup in self.typecatgroupstodo:
                            plothist = self.MakePlotHist(
                                whichsample = sample,
                                whichvar = var,
                                whichstage = stage,
                                dodatatuned = dodatatuned,
                                domctuned = domctuned,
                                catgroup = self.typecatgroups[catgroup],
                                dotypes = True,
                            )
                            if plothist:
                                plothist_list.append(plothist)
        self.plothist_list = plothist_list

    # TODO
    def FixHyperDParticleStacks(self):
        """
        This is meant to take stack hists like blob histograms and 
        """
        return

    def SetHist(self, i_hist, stage = "reconstructed", cat = "", type = 0, shortname = "", longname = "", opts = []):
        """ 
        Set a generic eventrate or xsec hist. Will assign it to the various internal histdicts

        Args:
            i_hist (TH1D, TH2D, MnvH1D, MnvH2D): the hist object
            stage (string): the stage of the hist, will group hists of different cats/types to plot together.
            cat (string): the cat of the hist, will apply different drawopts depending on if data, mc, whatever
            type (int): inttype (0-20) for the hist, if it exists
            shortname (str): this is the internal name, may be mapped to other info for plotting (e.g. name, drawopts, etc.)
            longname (str): this is the longname you will print on labels and legends on the actual plot (e.g. for legends)
            opt (list of strings): include "issig" or "isbkg" if signal or bkg, "istuned" if its tuned, "isref" if it's the ref hist for ratios
        Returns:
            None
        """
        # TODO: deal with shortname and longname info
        hist = i_hist.Clone()
        # If the stage doesn't have tuned in it, but "istuned" is in the opts, tack it on
        if "istuned" in opts and "_tuned" not in stage:
            stage += "_tuned"

        if cat == "data":
            data_hist_stage_dict[stage] = hist
            return
        # TODO all the other hists and 

    # def SetRefHistByName(self, name, stage = "reconstructed", cat = "mctot", shortname = ""):
    def SetRefHist(self, i_hist, stage = "reconstructed", cat = "mctot", shortname = "", longname = "", opts = []):
        """
        Set a hist to be used as a reference hist. Notice a copy might already 
        exist somewhere in the histdicts. Depending on the kind of hist it is,
        it will apply different things later on

        Args:
            i_hist (TH1D, TH2D, MnvH1D, MnvH2D): the hist object
            stage (string): the stage of the hist, will group hists of different cats/types to plot together.
            cat (string): the cat of the hist, will apply different drawopts depending on if data, mc, whatever
            shortname (str): this is the internal name, may be mapped to other info for plotting (e.g. name, drawopts, etc.)
            longname (str): this is the longname you will print on labels and legends on the actual plot (e.g. for legends)
            opt (list of strings):  "istuned" if its tuned, "ismisc" if it's a misc hist?
        Returns: 
            None
        """
        if stage in self.ref_hist_stage_dict:
            print("PlotFactory.SetRefHist \t WARNING refhist already set. Might be changing it...")

        if i_hist.GetEntries() <= 0: 
            print("PlotFactory.SetRefHist \t WARNING input refhist has no entries. Will not set it and ratios will not be made.")
            # self.is_refhist_set_stage_dict[stage] = False
            return
        
        # TODO: something about making it pretty for the ratio?
        self.ref_hist_stage_dict[stage] = i_hist.Clone()

    # TODO
    def SetMiscHist(self, i_hist, stage = "reconstructed", cat = "cat", shortname = "", longname = "", opt = []):
        """
        Set a miscellaneous hist that you might want to compare e.g., model 
        comparisons, different data comparisons, etc.

        Args:
            i_hist (TH1D, TH2D, MnvH1D, MnvH2D): the hist object
            stage (string): the stage of the hist, will group hists of different cats/types to plot together.
            cat (string): the cat of the hist, will apply different drawopts depending on if data, mc, whatever
            shortname (str): this is the internal name, may be mapped to other info for plotting (e.g. name, drawopts, etc.)
            longname (str): this is the longname you will print on labels and legends on the actual plot (e.g. for legends)
            opt (list of strings):  "istuned" if its tuned, "ismisc" if it's a misc hist?
        Returns:
            None
        """
        return

    # TODO
    def MakeHistPretty(self, i_hist, cat = "data", inttype = 0, modelcomp = "", datacomp = ""):
        """
        Make a hists pretty based on what they are. It will directly 
        change hists inside the member hist dicts

        Args:
            opts (list of str): options
        Returns:
            None
        """
        color = self.catscolors[cat]
        if inttype != 0:
            color = self.typescolors[inttype]

        linewidth = self.line_width_1d
        markersize = self.data_marker_size_1d
        enderrorsize = self.end_error_size_1d #TODO, this is set externally to gPad
        if type(i_hist) in [type(TH1D()), type(MnvH1D())]:
            linewidth = self.line_width_2d
            markersize = self.data_marker_size_2d
            enderrorsize = self.end_error_size_2d

        hist = i_hist.Clone()
        # If it's data, do data things and return
        if cat == "data" and datacomp != "":
            hist.SetLineColor(color)
            hist.SetMarkerColor(color)
            hist.SetLineWidth(linewidth)
            # hist.SetFillColor(0)
            hist.SetFillStyle(0)
            hist.SetMarkerSize(markersize)
            hist.SetMarkerStyle(20)
            return hist

        hist.SetFillColor(color)
        hist.SetLineColor(ROOT.TColor.GetColorDark(color))
        hist.SetLineStyle(1)
        hist.SetLineWidth(linewidth)
        if cat in self.backgroundcats:
            hist.SetFillStyle(3244)
        elif cat in self.signalcats:
            hist.SetFillStyle(1001)
        else: 
            hist.SetFillStyle(0)

        return hist

    # TODO
    def CopyHistStyle(self, target_hist, styleref_hist, opts = []):
        """
        Handy helper to copy the style from one hist onto another

        Args:
            target_hist (TH1D, TH2D, MnvH1D, MnvH2D): the hist you want to apply the style to
            "styleref_hist (TH1D, TH2D, MnvH1D, MnvH2D): the hist you want to copy the style of
        
        Returns:
            out_hist (TH1D, TH2D, MnvH1D, MnvH2D): copy of target hist, you might need to replace the original wherever it was with this new hist
        """
        out_hist = target_hist.Clone()
        if "notcolor" in opts:
            print("")
        # if "to2d" in opts:
        #     # Make everything smaller
        # if "to1d" in opts:
        #     # Make everything bigger
        
        
        return out_hist
    
    # TODO
    def MakeLegends(self):
        """
        Make the various legends for each stage. TODO: May need individual helper functions for this e.g. types leg, cats leg, warping study leg

        Returns:
            None: assigns member legends
        """
        return
    
class PlotHist:
    canvas_counter = 0
    stack_counter = 0
    allhist_testtypes = [type(MnvH1D()), type(TH1D()), type(MnvH2D()), type(TH2D()),type(THStack())]
    # def __init__(self, i_hist_dict, title = "", do_pinkstat = False):
    @classmethod
    def increment_canvas(cls):
        cls.canvas_counter += 1
    @classmethod
    def increment_stack(cls):
        cls.stack_counter += 1
    def __init__(self, i_hist_dict, title = "", i_varinfo_dict = {}, i_plotinfo_dict = {}, opts = []):
        self.title = title
        self.opts = opts

        # Set up the opts? TODO:
        self.opts = opts
        self.is_sigma = False
        if "issigma" in opts:
            self.is_sigma = True

        # preset all of these so you can check things later?
        self.varinfo_set = False
        self.x_info_set = False
        self.y_info_set = False
        self.xy_info_set = False
        # This sets all the info for the variables
        self.SetVarInfo(i_varinfo_dict)

        # self.SetPlotInfo(i_plotinfo_dict)
        # self.do_pinkstat = do_pinkstat
        self.do_pinkstat = False
        if "dopinkstat" in opts:
            self.do_pinkstat = True
        if "datamisc" in opts:
            self.misc_is_data = True
        if "mcmisc" in opts:
            self.misc_is_mc = True
        self.bkgfillstyle = 3244
        histdict_attrname_list = []
        hist_attrname_list = []
        # Look for data list, if only a hist, clone it and put it in a list
        if "data" in i_hist_dict:
            print("found data hists")
            self.SetDataHists(i_hist_dict["data"])
            print("done with data hists")
        # If you have mc's take those in and put them in a dict
        if "mc" in i_hist_dict:
            print("found mc hists")
            self.SetMCHists(i_hist_dict["mc"])
            print("done with mc hists")
        # Same for misc
        if "misc" in i_hist_dict:
            print("found misc hists")
            self.SetMiscHists(i_hist_dict["misc"])
            print("done with misc hists")

        # Clone a ref hist if it's there
        self.FindAndSetRefHist(i_hist_dict)
        # if "ref" in i_hist_dict:
        #     self.ref_hist = i_hist_dict["ref"].Clone()
        #     hist_attrname_list.append("ref_hist")
        #     self.ref_histtype = "mc"
        # elif 'mctot_mnv' in self:
        #     self.ref_hist = self.mctot_mnv.Clone()
        #     hist_attrname_list.append("ref_hist")
        #     self.ref_histtype = "mc"

        # elif 'data_mnv_dict' in self:
        #     if "data" in self.data_mnv_dict:
        #         self.ref_hist = self.data_mnv_dict["data"].Clone()
        #         hist_attrname_list.append("ref_hist")
        #         self.ref_histtype = "data"
        # if 'ref_hist' in self:
        #     if self.ref_histtype == "data":
        #         self.ref_line, self.ref_cv = self.GetDataSystAndStat(
        #             i_data_hist = self.ref_hist
        #         )
        #     if self.ref_histtype == "mc":
        #         self.ref_cv = self.GetMCCVAndBand(
        #             i_mc_hist = self.ref_hist
        #         )
        print("done setting up hists")
        # Make all the ratios TODO: does this need to be in the parent?
        # self.SetRatioHists()

        self.my_mnvplt = MnvPlotter(8)

    def SetDummyHist(self, i_hist, reset = False):
        if 'dummy_hist' in self:
            return
        axis_ndivs = 505
        axis_labelsize = 0.03

        dummy_hist = i_hist.Clone("dummy_hist")
        dummy_hist.GetXaxis().SetNdivisions(axis_ndivs)
        dummy_hist.GetXaxis().SetLabelSize(axis_labelsize)
        dummy_hist.GetYaxis().SetNdivisions(axis_ndivs)
        dummy_hist.GetYaxis().SetLabelSize(axis_labelsize)
    
        # dummy_hist.Reset("ICESM")
        self.dummy_hist = dummy_hist

    def SetDataHists(self, i_data_hist_dict):
        """
        Set up all the data hists, including stat and systematics

        Args:
            i_data_hist_dict (dict of hists): should be like i_hist_dict["data"] in normal plothist
        """

        data_mnv_dict = {}
        # if type(i_data_hist_dict) == list:
        #     datatag = 0
        #     for hist in i_data_hist_dict:
        #         data_mnv_dict["data%02d"%datatag] = hist.Clone()
        #         datatag += 1
        # elif type(i_data_hist_dict) in [type(MnvH1D()), type(TH1D()), type(MnvH2D()), type(TH2D())]:
        #     data_mnv_dict = {"data": i_data_hist_dict.Clone()}
        # else:
        for key in i_data_hist_dict:
            data_mnv_dict[key] = i_data_hist_dict[key].Clone()
        
        for key in data_mnv_dict:
            if key in ["ref", "refhist", "ref_hist"]:
                self.ref_hist = i_data_hist_dict[key].Clone()
                self.ref_histtype = "data"
                data_mnv_dict.pop(key)
        self.data_mnv_dict = data_mnv_dict
        for key in data_mnv_dict:
            tmp_hist = data_mnv_dict[key].Clone()
            if 'hist_testtypes' in self:
                if type(tmp_hist) not in self.hist_testtypes: 
                    print("PlotHist.__init__ \t ERROR: data has mismatched type")
                    print(tmp_hist.GetName())
                    print(type(tmp_hist))
                    sys.exit(1)
            else:
                if type(tmp_hist) in [type(MnvH1D()), type(TH1D())]:
                    self.hist_testtypes = [type(MnvH1D()), type(TH1D())]
                elif type(tmp_hist) in [type(MnvH2D()), type(TH2D())]:
                    self.hist_testtypes = [type(MnvH2D()), type(TH2D())]
        
        data_syst_dict = {}
        data_stat_dict = {}
        for key in data_mnv_dict:
            tmp_hist = data_mnv_dict[key].Clone()
            data_syst_dict[key], data_stat_dict[key] = self.GetDataSystAndStat(
                i_data_hist = tmp_hist
            )
        self.data_syst_dict = data_syst_dict
        self.data_stat_dict = data_stat_dict

        if 'dummy_hist' not in self:
            for key in self.data_mnv_dict:
                self.SetDummyHist(self.data_mnv_dict[key].Clone("dummy_hist"))
                break

    def SetMCHists(self, i_mc_hist_dict):
        """
        Set up all the MC hists, including mctot and cv and bands. It will build an mctot if you don't have one, but be weary it might not have the right errors

        Args:
            i_mc_hist_dict (dict of hists): should be like i_hist_dict["mc"] in normal plothist
        """

        mc_mnv_dict = {}
        # Loop over all of them, assign mctot separately
        if "mctot" in i_mc_hist_dict:
            self.mctot_mnv = i_mc_hist_dict["mctot"].Clone()
        for key in i_mc_hist_dict:
            if key == "mctot":
                continue
            if key in ["ref", "refhist", "ref_hist"] and 'ref_hist' not in self:
                self.ref_hist = i_mc_hist_dict[key]
                self.ref_histtype = "mc"
                continue
            mc_mnv_dict[key] = i_mc_hist_dict[key].Clone()
        self.mc_mnv_dict = mc_mnv_dict
        # test_mctot = i_mc_hist_dict[list(i_mc_hist_dict.keys())[0]].Clone("test_mctot")
        first_mc = True
        for key in mc_mnv_dict:
            if first_mc:
                test_mctot = mc_mnv_dict[key].Clone(mc_mnv_dict[key].GetName().replace(key, "test_mctot"))
                first_mc = False
                continue
            test_mctot.Add(mc_mnv_dict[key].Clone())
        print("done copying mc")

        # Make sure your test mctot matches mctot
        if 'mctot_mnv' in self:
            # if self.mctot_mnv.GetMaximum() != test_mctot.GetMaximum():
            # This could be done more precisely using integral, not an exact equal bc machine precision can mess with things here...
            if self.mctot_mnv.GetMaximum() - test_mctot.GetMaximum() > self.mctot_mnv.GetMaximum()*0.0001:
                print("PlotHist.__init__ \t ERROR: mctot doesn't match the sum of the mc's. exiting...")
                for key in mc_mnv_dict:
                    mc_mnv_dict[key].Print()
                self.mctot_mnv.Print()
                test_mctot.Print()
                canvas = TCanvas()
                canvas.Draw()
                test_ratio = test_mctot.Clone()
                test_ratio.Divide(test_ratio,self.mctot_mnv,1.,1.)
                tot_ratio = self.mctot_mnv.Clone()
                tot_ratio.Divide(self.mctot_mnv,self.mctot_mnv,1.,1.)
                tot_ratio.SetLineColor(ROOT.kRed)
                test_ratio.SetLineColor(ROOT.kBlue)
                tot_ratio.Draw("hist")
                test_ratio.Draw("hist same")
                canvas.Print("bad.pdf")
                print(self.mctot_mnv.GetMaximum(),test_mctot.GetMaximum())
                print(tot_ratio.GetMaximum(),test_ratio.GetMaximum())
                sys.exit(1)
        else:
            print("PlotHist: \tBuilding mctot for you...")
            self.mctot_mnv = test_mctot.Clone(test_mctot.GetName().replace("test_mctot", "mctot"))
        # This gets the bands useful for plotting TODO: move this to when you need it bc this takes forever for 2D when you have a lot of systs
        # self.mctot_cv, self.mctot_band = self.GetMCCVAndBand(self.mctot_mnv)

        # Check that it matches the test type or use this as the baseline for the test types
        if 'hist_testtypes' in self:
            if type(self.mctot_mnv) not in self.hist_testtypes: 
                print("PlotHist.__init__ \t ERROR: mc has mismatched type")
                print(type(self.mctot_mnv))
                print(self.mctot_mnv.GetName())
                sys.exit(1)
        else:
            if type(self.mctot_mnv) in [type(MnvH1D()), type(TH1D())]:
                self.hist_testtypes = [type(MnvH1D()), type(TH1D())]
            elif type(self.mctot_mnv) in [type(MnvH2D()), type(TH2D())]:
                self.hist_testtypes = [type(MnvH2D()), type(TH2D())]
        if 'dummy_hist' not in self:
            for key in self.mc_mnv_dict:
                self.SetDummyHist(self.mc_mnv_dict[key].Clone("dummy_hist"))
                break

    def SetMiscHists(self, i_misc_hist_dict):
        misc_mnv_dict = {}
        for key in i_misc_hist_dict:
            tmp_hist = i_misc_hist_dict[key].Clone()
            if 'hist_testtypes' in self:
                if type(tmp_hist) not in self.hist_testtypes: 
                    print("PlotHist.__init__ \t ERROR: misc has mismatched type")
                    print(tmp_hist.GetName())
                    print(type(tmp_hist))
                    sys.exit(1)
            else:
                if type(tmp_hist) in [type(MnvH1D()), type(TH1D())]:
                    self.hist_testtypes = [type(MnvH1D()), type(TH1D())]
                elif type(tmp_hist) in [type(MnvH2D()), type(TH2D())]:
                    self.hist_testtypes = [type(MnvH2D()), type(TH2D())]
            misc_mnv_dict[key] = tmp_hist
        self.misc_mnv_dict = misc_mnv_dict
        
        if 'dummy_hist' not in self:
            for key in self.misc_mnv_dict:
                self.SetDummyHist(self.misc_mnv_dict[key].Clone("dummy_hist"))
                break

    def FindAndSetRefHist(self, i_hist_dict):
        """
        Set up the reference hist. If you don't have one, set it to mctot or base data

        Args:
            i_hist_dict (dict dicts of hists): should be the whole i_hist_dict in normal plothist
        """
        if "ref" in i_hist_dict:
            self.ref_hist = i_hist_dict["ref"].Clone()
            self.ref_histtype = "mc"
        elif 'mctot_mnv' in self:
            self.ref_hist = self.mctot_mnv.Clone()
            self.ref_histtype = "mc"
        elif 'data_mnv_dict' in self:
            if "base" in self.data_mnv_dict:
                self.ref_hist = self.data_mnv_dict["base"].Clone()
                self.ref_histtype = "data"
            elif "data" in self.data_mnv_dict:
                self.ref_hist = self.data_mnv_dict["data"].Clone()
                self.ref_histtype = "data"
        # if 'ref_hist' in self:
        #     if self.ref_histtype == "data":
        #         self.ref_line, self.ref_cv = self.GetDataSystAndStat(
        #             i_data_hist = self.ref_hist
        #         )
        #     if self.ref_histtype == "mc":
        #         self.ref_cv = self.GetMCCVAndBand(
        #             i_mc_hist = self.ref_hist
        #         )

    def __contains__(self, attribute_name):
        """
        Helper to check if something is stored in this. Allows you to do:
            if <str of attr name> in self:
        """
        return hasattr(self, attribute_name)

    def GetDataSystAndStat(self, i_data_hist):
        hist = i_data_hist.Clone()
        # hist = self.data_mnv_dict[key].Clone()
        data_syst = hist.GetCVHistoWithError()
        data_syst.SetMarkerColor(hist.GetMarkerColor())
        data_syst.SetLineWidth(hist.GetLineWidth())
        data_syst.SetLineColor(hist.GetLineColor())
        data_syst.SetMarkerSize(hist.GetMarkerSize())
        data_syst.SetMarkerStyle(hist.GetMarkerStyle())
        # data_syst_dict[key] = data_syst

        data_stat = hist.GetCVHistoWithStatError()
        data_stat.SetMarkerColor(hist.GetMarkerColor())
        # end_error_size
        data_stat.SetLineWidth(hist.GetLineWidth())
        data_stat.SetLineColor(hist.GetLineColor())
        if self.do_pinkstat:
            data_stat.SetLineWidth(4)
            band_alphalevel = 0.3
            data_stat.SetLineColorAlpha(ROOT.kPink, band_alphalevel) #mnvh.GetLineColor())
            data_stat.SetFillColorAlpha(ROOT.kPink, band_alphalevel)
        data_stat.SetMarkerSize(0)
        data_stat.SetMarkerStyle(1)
        # data_stat_dict[key] = data_stat

        return data_syst, data_stat

    def GetMCCVAndBand(self, i_mc_hist):
        hist = self.mctot_mnv.Clone()
        if type(hist) in [type(MnvH1D()), type(MnvH2D())]:
            # print("getting histo with error")
            mctot_cv = hist.GetCVHistoWithError(includeStat = True, cov_area_normalize = False)
            mctot_band = hist.GetCVHistoWithError(includeStat = True, cov_area_normalize = False)
            # print("done getting histo with error")
        else:
            mctot_cv = hist.Clone("mctot_cv")
            mctot_band = hist.Clone("mctot_band")

        color = hist.GetFillColor()
        mctot_cv.SetFillColor(0)
        mctot_cv.SetLineColor(hist.GetFillColor())
        band_alphalevel = 0.3
        mctot_band.SetFillStyle(1001)
        mctot_band.SetFillColorAlpha(hist.GetFillColor(), band_alphalevel)
        mctot_band.SetLineColor(hist.GetFillColor())
        mctot_band.SetMarkerStyle(0)

        mctot_cv.SetTitle(hist.GetTitle())
        mctot_band.SetTitle(hist.GetTitle())

        return mctot_cv, mctot_band

    def GetHistWithErrorMax(self, i_hist):
        """
        Get the maximum of the hist, including it's errors, so it will sit neatly in the pad

        Args:
            i_hist (MnvH1D, TH1D): hist you're finding max for
        Returns:
            maximum (float): max of 0.0, the regular GetMaximum call, or the max value including errors
        """
        hist = i_hist.Clone()
        if type(i_hist) in [type(MnvH1D()),type(MnvH2D())]:
            hist = i_hist.Clone().GetCVHistoWithError()
        hist_max = i_hist.GetMaximum()
        histanderror_max = 0.0
        if type(i_hist) != type(THStack()):
            max([hist.GetBinContent(i) + hist.GetBinError(i) for i in range(1, hist.GetNbinsX() + 1)])
        return max(0.0, hist_max, histanderror_max)

    def SetVarInfo(self, i_varinfo_dict, vert_shortittle = "Counts"):
        """
        Sets a bunch of things used for titles n such

        Args:
            i_varinfo_dict (dict): dict with info on x, y variables
            vert_shorttitle (str): title for vertical axis. if "sigma" is in the name, it will make the cross section one
        """
        self.varinfo_dict = i_varinfo_dict
        self.vert_shortittle = vert_shortittle

        if "x" in i_varinfo_dict:
            self.x_info_set = True
            self.x_shortname = i_varinfo_dict["x"]["shortname"]
            self.x_shorttitle = i_varinfo_dict["x"]["shorttitle"]
            self.x_longtitle = i_varinfo_dict["x"]["longtitle"]
            self.x_units = i_varinfo_dict["x"]["units"]
            self.x_logx = i_varinfo_dict["x"]["logx"]
            self.x_logy = i_varinfo_dict["x"]["logy"]

            x_title = self.x_shorttitle
            x_vert_title = vert_shortittle
            if self.x_units != "":
                x_title += " #lower[-0.25]{#scale[0.6]{[%s]}}"%(self.x_units)
                x_vert_title += " / %s"%(self.x_units)
            if "sigma" in vert_shortittle or self.is_sigma:
                self.is_sigma = True
                if "issigma" not in self.opts:
                    self.opts.append("issigma")
                x_vert_title = "d#it{#sigma}/^{}d#it{%s}#lower[-0.15]{#scale[0.7]{ [cm^{2}/^{}%s/^{}Nucleon]}}"%(self.x_shorttitle ,self.x_units)
            self.x_title = x_title
            self.x_vert_title = x_vert_title

        if "y" in i_varinfo_dict:
            self.y_info_set = True
            self.y_shortname = i_varinfo_dict["y"]["shortname"]
            self.y_shorttitle = i_varinfo_dict["y"]["shorttitle"]
            self.y_longtitle = i_varinfo_dict["y"]["longtitle"]
            self.y_units = i_varinfo_dict["y"]["units"]
            self.y_logx = i_varinfo_dict["y"]["logx"]
            self.y_logy = i_varinfo_dict["y"]["logy"]
            
            y_title = self.y_shorttitle
            y_vert_title = self.vert_shortittle
            if self.y_units != "":
                y_title += " #lower[-0.25]{#scale[0.6]{[%s]}}"%(self.y_units)
                y_vert_title += " / [%s]"%(self.y_units)
            if "sigma" in vert_shortittle or self.is_sigma:
                self.is_sigma = True
                if "issigma" not in self.opts:
                    self.opts.append("issigma")
                y_vert_title = "d#it{#sigma}/^{}d#it{%s}#lower[-0.15]{#scale[0.7]{ [cm^{2}/^{}%s/^{}Nucleon]}}"%(self.y_shorttitle, self.y_units)
            self.y_title = y_title
            self.y_vert_title = y_vert_title

        if self.x_info_set and self.y_info_set:
            self.xy_info_set = True
            xy_vert_title = vert_shortittle
            if self.x_units != "":
                xy_vert_title += " / %s"%(self.x_units)
            if self.y_units != "":
                xy_vert_title += " / %s"%(self.y_units)
            if "sigma" in vert_shortittle or self.is_sigma:
                self.is_sigma = True
                if "issigma" not in self.opts:
                    self.opts.append("issigma")
                xy_vert_title = "d^{2}#it{#sigma}/^{}d#it{%s}d#it{%s}#lower[-0.15]{#scale[0.7]{ [cm^{2}/%s/%s/Nucleon]}}"%(self.x_shorttitle, self.y_shorttitle, self.x_units, self.y_units)
            self.xy_vert_title = xy_vert_title

    # plotinfo_dict = {
    #     "sample": "QElike",
    #     "datatuned": False,
    #     "mctuned": False,
    #     "var": "Eavail_ptmu",
    #     "outdir": "dir",
    #     "dummycanvas": "dummy.pdf",
    #     "outname": "plot",
    #     "outfiletypes": [
    #         "pdf",
    #         "png",
    #         "C"
    #     ],
    # }
    def SetPlotInfo(self, i_plotinfo_dict):
        self.sample = i_plotinfo_dict["sample"],
        self.datatuned = i_plotinfo_dict["datatuned"],
        self.mctuned = i_plotinfo_dict["mctuned"],
        self.outdir = i_plotinfo_dict["outdir"]
        
        if "dummycanvas" in i_plotinfo_dict:
            self.dummy_canvas_name = i_plotinfo_dict["dummycanvas"]
        


    def SetCanvasBaseName(self, basename):
        """
        Set a basename for canvases. It's good practice to have unique names for each canvas globally, so you will need to add a tag to these.
        """
        if 'canvas_basename' in self:
            print("PlotHist.SetCanvasBaseName(): \tWARNING canvas_basename already set. Changing from %s to %s"%(self.canvas_basename, basename))
        self.canvas_basename = basename

    def MakeUniqueCanvasName(self, i_basename = ""):
        """
        Makes a unique canvas basename so you can avoid pyroots issues with multiple canvases with the same name
        """
        basename = i_basename
        if i_basename == "":
            if 'canvas_basename' not in self:
                basename = "canvas"
            else:
                basename = self.canvas_basename
        uniq_name = "%s_canvas%03d"%(basename, self.canvas_counter)
        self.increment_canvas()
        return uniq_name


    # TODO other generic methods?

class PlotHist1D(PlotHist):
    # Count the number of stacks, used for naming, which might keep things from going haywire?
    def __init__(self, i_hist_dict, title = "", i_varinfo_dict = {}, opts = []):
        super().__init__(i_hist_dict = i_hist_dict, title = title, i_varinfo_dict = i_varinfo_dict, opts = opts)

        if self.x_info_set:
            self.varinfo_set = True

        if 'mc_mnv_dict' in self:
            self.mc_stack = self.MakeStack(
                i_hist_dict = self.mc_mnv_dict,
            )
            self.mc_stack_nofill = self.MakeStack(
                i_hist_dict = self.mc_mnv_dict,
                opts = ["nofill"]
            )

    def GetPadMax(self, isratio = False):
        """
        Get the maximum of all the hists in the pad

        Args:
            isratio (bool): TODO
        Returns:
            padmax (float): if nothing is bigger than 0.0, it will return 1.0
        """

        pad_max = 0.0
        if 'data_mnv_dict' in self and 'data_syst_dict' not in self:
            data_syst_dict = {}
            data_stat_dict = {}
            for key in data_mnv_dict:
                tmp_hist = data_mnv_dict[key].Clone()
                data_syst_dict[key], data_stat_dict[key] = self.GetDataSystAndStat(
                    i_data_hist = tmp_hist
                )
            self.data_syst_dict = data_syst_dict
            self.data_stat_dict = data_stat_dict
        if 'data_syst_dict' in self:
            data_max = max([self.GetHistWithErrorMax(self.data_syst_dict[key]) for key in list(self.data_syst_dict.keys())])
            if data_max > pad_max: pad_max = data_max
        elif 'data_stat_dict' in self:
            data_max = max([self.GetHistWithErrorMax(self.data_stat_dict[key]) for key in list(self.data_stat_dict.keys())])
            if data_max > pad_max: pad_max = data_max
        if 'mctot_mnv' in self:
            if 'mctot_cv' not in self:
                self.mctot_cv, self.mctot_band = self.GetMCCVAndBand(self.mctot_mnv)
            mc_max = self.GetHistWithErrorMax(self.mctot_cv)
            if mc_max > pad_max: pad_max = mc_max
        elif 'misc_mnv_dict' in self:
            misc_max = -1.0
            for key in self.misc_mnv_dict:
                tmp_hist = self.misc_mnv_dict[key].Clone()
                # if type(tmp_hist) == type(MnvH1D()):
                #     tmp_hist = self.misc_mnv_dict[key].GetCVHistoWithError()
                tmp_misc_max = self.GetHistWithErrorMax(tmp_hist)
                misc_max = max(misc_max, tmp_misc_max)
            if misc_max > pad_max: pad_max = misc_max
        # if there's nothing in the pad, set it to 1 so things don't freak out
        if pad_max == 0.0: 
            print("PlotHist1D.GetPadMax \t WARNING: hists in pad have a max of 0, returning 1.0 so math will work")
            pad_max = 1.0
        return pad_max

    def GetRatioMax(self):
        """
        Get the maximum of the ratio hists only
        """
        ratio_max = 2.0
        for name, value in members:
            if 'ratio' not in name: continue
            if type(getattr(self, name)) in self.allhist_testtypes:
                tmp_max = self.GetHistWithErrorMax(getattr(self, name))
                ratio_max = max(tmp_max, ratio_max)
            if type(getattr(self, name)) == dict:
                for key in getattr(self, name):
                    if type(getattr(self, name)[key]) not in self.allhist_testtypes:
                        continue
                    tmp_max = self.GetHistWithErrorMax(getattr(self, name)[key])
                    ratio_max = max(tmp_max, ratio_max)
        return ratio_max

    def Scale(self, value = -1.0, opts = "", multipstring = False, onemember = ''):
        """
        Scale all the hists in here by some value. 

        Args:
            value (float): by a user set value, defaults to -1.0,
            opts (str): different options like those you can use in root hist 
                Scale() method
            multipstring (bool): set to true, makes the multiplier string for this pad (useful for panel plots).
            onemember (str): name of attr in object if you want to only scale a
                single hist in here
            Returns:
                None***
        """
        if value < 0: return
        pad_scale = value
        if multipstring and onemember == '':
            # This shortens it to 2 sig figs
            multip_string = "#times {:g}".format(float('{:.{p}g}'.format(pad_scale, p=2)))
            self.multip_string = multip_string
        if value == 1.0:
            return
        members = inspect.getmembers(self)
        foundonemember = False
        for name, value in members:
            if "ratio" in name:
                continue
            if onemember != '':
                if name != onemember:
                    continue
                else:
                    foundonemember = True
            if type(getattr(self, name)) == dict:
                # tmp_baddict = False
                for key in getattr(self, name):
                    if type(getattr(self, name)[key]) not in self.hist_testtypes:
                        break
                    getattr(self, name)[key].Scale(pad_scale, opts)
                if foundonemember: break
                continue
            if type(getattr(self, name)) not in self.hist_testtypes:
                if foundonemember: break
                continue
            getattr(self, name).Scale(pad_scale, opts)
            if foundonemember: break
        if not foundonemember and onemember != '':
            print("PlotHist1D.Scale \tWARNING: could not find single member %s"%onemember)
        else:
            self.SetMaximum()

    def SetMaximum(self, value = -1.0, headroom_scale = -1.0, isratio = False):
        """
        Set the maximum for everything in the pad including headroom

        Args:
            value (float): default -1.0, if not default, will use this as user 
                specified max. If default, will find the padmax and use that 
                instead.
            headroom_scale (float): factor applied to give headroom to things 
                in the pad. If default, will apply 1.2 as headroom, 2.0 if logy set
            isratio (bool): set if you want to do the ratio ones only

        """
        if isratio:
            if value < 0.0: return
            self.ratio_max = value
            for name, value in members:
                if 'ratio' not in name: continue
                if type(getattr(self, name)) in self.allhist_testtypes:
                    getattr(self, name).SetMaximum(ratio_max)
                if type(getattr(self, name)) == dict:
                    for key in getattr(self, name):
                        if type(getattr(self, name)[key]) not in self.allhist_testtypes:
                            continue
                        getattr(self, name)[key].SetMaximum(ratio_max)

        # This gives some headroom above the hist, if it's already set, just use that one
        if 'headroom_scale' in self:
            headroom_scale = self.headroom_scale
        elif headroom_scale < 0.:
            headroom_scale = 1.2
        # If there's a log axis, give yourself a little more headroom
        elif self.logy:
            headroom_scale = 2.0
        # if it's set by the user, set that one so it sticks for any other changes made
        else:
            self.headroom_scale = headroom_scale
        # Get the max for the pad from the user set, if not use the calculated one
        padmax = value
        if value < 0.0:
            padmax = self.GetPadMax()
        self.padmax = padmax
        
        # Set the maxes of all the hists
        members = inspect.getmembers(self)
        for name, value in members:
            if 'ratio' in name: continue
            if type(getattr(self, name)) in self.allhist_testtypes:
                getattr(self, name).SetMaximum(headroom_scale * padmax)
            if type(getattr(self, name)) == dict:
                for key in getattr(self, name):
                    if type(getattr(self, name)[key]) not in self.allhist_testtypes:
                        continue
                    getattr(self, name)[key].SetMaximum(headroom_scale * padmax)

        # If you're doing ratio hists, figure that out here too (useful for )

    def SetRatioHists(self):
        """
        Make all the ratio histograms based on the reference hist
        """
        if 'ref_hist' not in self:
            return
        ref_hist = self.ref_hist.Clone()
        
        ref_mnv_ratio = ref_hist.Clone()
        ref_mnv_ratio.ClearAllErrorBands()
        ref_mnv_ratio.AddMissingErrorBandsAndFillWithCV()
        ref_mnv_ratio.Divide(ref_mnv_ratio,ref_mnv_ratio,1.0,1.0)
        if self.ref_histtype == "data":
            self.ref_ratio_line, self.ref_ratio_band = GetDataSystAndStat(ref_mnv_ratio)
            self.ref_ratio_line.GetYaxis().SetTitle("Ratio to data")
            self.ref_ratio_band.GetYaxis().SetTitle("Ratio to data")
            self.ref_ratio_line_drawopts = "9 E1 X0"
            self.ref_ratio_band_drawopts = "9 E1 X0"
        else:
            self.ref_ratio_line, self.ref_ratio_band = GetMCCVAndBand(ref_mnv_ratio)
            self.ref_ratio_line.GetYaxis().SetTitle("Ratio to MC")
            self.ref_ratio_band.GetYaxis().SetTitle("Ratio to MC")
            self.ref_ratio_line_drawopts = "9 E2 ]["
            self.ref_ratio_band_drawopts = "9 hist ]["
        self.ref_ratio_line.GetXaxis().SetTitle(self.x_title)
        self.ref_ratio_band.GetXaxis().SetTitle(self.x_title)
        self.ref_mnv_ratio = ref_mnv_ratio
        ratio_max = 2.0
        ratio_min = 0.0001

        # First make the ratio "line"
        if 'data_mnv_dict' in self:
            tmp_data_mnv_ratio_dict
            self.data_mnv_ratio_dict = self.GetRatioHists(
                i_dict_or_hist = self.data_mnv_dict,
                i_ref_hist = ref_hist,
            )
            data_syst_ratio_dict = {}
            data_stat_ratio_dict = {}
            for key in self.data_mnv_ratio_dict:
                tmp_hist = self.data_mnv_ratio_dict[key].Clone()
                tmp_data_syst_ratio_dict[key], tmp_data_stat_ratio_dict[key] = self.GetDataSystAndStat(
                    i_data_hist = tmp_hist
                )
            # for key in self.data_mnv_ratio_dict:
                tmp_max = self.GetHistWithErrorMax(self.data_mnv_ratio_dict[key])
                ratio_max = max(tmp_max, ratio_max)
            self.data_syst_ratio_dict = data_syst_ratio_dict
            self.data_stat_ratio_dict = data_stat_ratio_dict
            
        if 'mc_mnv_dict' in self:
            self.mc_mnv_ratio_dict = self.GetRatioHists(
                i_dict_or_hist = self.mc_mnv_dict,
                i_ref_hist = ref_hist,
            )
            for key in self.mc_mnv_ratio_dict:
                color = self.mc_mnv_dict[key].GetFillColor()
                self.mc_mnv_ratio_dict[key].SetLineColor(color)
                self.mc_mnv_ratio_dict[key].SetFillStyle(0)

            # TODO: figure out all the stacking that needs to be done here (e.g. for types)
            # This is old, maybe try something like
            # if dotypes: and then check if bkgs are in it
            if 11 in mc_mnv_dict:
                mc_ratio_doublestack_dict = {}
                for key in mc_mnv_dict:
                    if key > 10: continue
                    tmp_stack = THStack("mc_ratio_doublestack_type%02d_%02d"%(str(key), self.stack_counter), "")
                    # ROOT.SetOwnership(tmp_stack, True)
                    # self.stack_counter += 1
                    self.increment_stack()
                    tmp_bkg_hist = mc_mnv_dict[key+10].Clone()
                    tmp_bkg_hist.SetLineStyle(2)
                    tmp_stack.Add(tmp_bkg_hist)
                    if key in mc_mnv_dict:
                        tmp_sig_hist = mc_mnv_dict[key].Clone()
                        if tmp_sig_hist.GetEntries() == 0:
                            tmp_sig_hist.SetLineStyle(2)
                        tmp_stack.Add(tmp_sig_hist)                            
                    else:
                        mc_ratio_doublestack_dict[key] = tmp_bkg_hist
                    mc_ratio_doublestack_dict[key] = tmp_stack
                self.mc_ratio_doublestack_dict = mc_ratio_doublestack_dict
            
            self.mctot_mnv_ratio = self.GetRatioHists(
                i_dict_or_hist = self.mctot_mnv,
                i_ref_hist = ref_hist,
            )
            self.mctot_cv_ratio, self.mctot_band_ratio = self.GetMCCVAndBand(
                i_data_dict = self.mctot_mnv_ratio,
                isratio = True,
            )
            tmp_max = self.GetHistWithErrorMax(self.mctot_mnv_ratio)
            ratio_max = max(tmp_max, ratio_max)

        if 'misc_mnv_dict' in self:
            self.misc_mnv_ratio_dict = self.GetRatioHists(
                i_dict_or_hist = self.misc_mnv_dict,
                i_ref_hist = ref_hist,
            )
            for key in self.misc_mnv_ratio_dict:
                tmp_max = self.GetHistWithErrorMax(self.misc_mnv_ratio_dict[key])
                ratio_max = max(tmp_max, ratio_max)
            # CV and band is like data syst and stat here
            # misc_cv_ratio_dict = {}
            # misc_band_ratio_dict = {}
            # if self.ref_histtype == "data":
            #     for key in self.misc_mnv_ratio_dict:
            #         tmp_hist = self.misc_mnv_ratio_dict[key].Clone()
            #         tmp_misc_cv_ratio_dict[key], tmp_misc_band_ratio_dict[key] = self.GetDataSystAndStat(
            #             i_data_hist = tmp_hist
            #         )
            # elif self.ref_histtype == "mc":
            #     for key in self.misc_mnv_ratio_dict:
            #         tmp_hist = self.misc_mnv_ratio_dict[key].Clone()
            #         tmp_misc_cv_ratio_dict[key], tmp_misc_band_ratio_dict[key] = self.GetMCCVAndBand(
            #             i_mc_hist = tmp_hist  
            #         )


            # # TODO: some misc hists are datalike, others are not... This might not be the move
            # self.mc_syst_ratio_dict, self.mc_stat_ratio_dict = self.GetDataSystAndStat(
            #     i_data_dict = self.mc_mnv_ratio_dict,
            #     isratio = True,
            # )
        
        # Now get them all evened out
        if ratio_max > 5.0: ratio_max = 5.0
        self.ratio_max = ratio_max
        self.ratio_min = ratio_min
        for name, value in members:
            if 'ratio' not in name: continue
            if type(getattr(self, name)) in self.allhist_testtypes:
                getattr(self, name).SetMaximum(ratio_max)
                getattr(self, name).SetMinimum(ratio_min)
            if type(getattr(self, name)) == dict:
                for key in getattr(self, name):
                    if type(getattr(self, name)[key]) not in self.allhist_testtypes:
                        continue
                    getattr(self, name)[key].SetMaximum(ratio_max)
                    getattr(self, name).SetMinimum(ratio_min)

    def GetRatioHists(self, i_dict_or_hist, i_ref_hist, opts = []):
        """
        Get the ratio hists for a given dict of hists
        Args:
            i_dict (dict of hists): the hists you want to get ratios of
            i_ref_hist (hist): the hist you are using as a reference for the ratio
            opts (list of str): include "types" if types, "doublestack" if double stacking?
        Return:
            ratio_dict (dict of hists): output dict with same structure as the input one
        """

        ref_hist = i_ref_hist.Clone()
        ref_is_mnv = False
        if type(ref_hist) in [type(MnvH1D()), type(MnvH2D())]:
            ref_is_mnv = True
            ref_hist.ClearAllErrorBands()
        if type(i_dict_or_hist) in self.hist_testtypes:
            tmp_name = "%s_ratioto_%s"%(i_dict_or_hist.Getname(),i_ref_hist.GetName())
            tmp_ratio = i_dict_or_hist.Clone(name)
            ratio_is_mnv = False
            if tmp_ratio in [type(MnvH1D()), type(MnvH2D())]:
                ratio_is_mnv = True
            if ref_is_mnv and ratio_is_mnv:
                ref_hist.AddMissingErrorBandsAndFillWithCV(tmp_ratio)
            tmp_ratio.Divide(tmp_ratio, ref_hist, 1.0, 1.0)
            return tmp_ratio
        
        ratio_dict = {}
        for key in i_dict_or_hist:
            if key not in ratio_dict: ratio_dict[key] = {}
            if type(i_dict_or_hist[key]) not in self.hist_testtypes: continue
            tmp_name = "%s_ratioto_%s"%(i_dict_or_hist[key].Getname(),i_ref_hist.GetName())
            tmp_ratio = i_dict_or_hist[key].Clone(name)
            ratio_is_mnv = False
            if tmp_ratio in [type(MnvH1D()), type(MnvH2D())]:
                ratio_is_mnv = True
            if ref_is_mnv and ratio_is_mnv:
                ref_hist.AddMissingErrorBandsAndFillWithCV(tmp_ratio)
            tmp_ratio.Divide(tmp_ratio, ref_hist, 1.0, 1.0, "B")
            ratio_dict[key] = tmp_ratio

    def MakeStack(self, i_hist_dict, i_stack = 0, i_order = [], opts = []):
        """
        Make a stack of input histograms in reverse order of the input dict?
        
        Args:
            i_hist_dict (dict of hists): dicitonary of histograms. Order matters here.
            i_order (list of str): list of the keys in the dict in the order you want to put them in. Allows for subset of keys in the dict to be used.
            opts (list of str): options:
                "nofill": remove any fill in the hists, so they are just lines
                "noreverse": do not reverse the input hists
                "doublestack": useful for ratios with sig and bkg, only works if you have two hists or i_order is two
                "isbackground": if it's a background, make the fill style hashed
                "issignal": if it's signal, make the fill style solid
        Returns:
            A THStack

        """
        order = []
        if len(i_order) != 0:
            order = i_order
        if "noreverse" in opts:
            order = list(i_hist_dict.keys())
        else:
            order = reversed(list(i_hist_dict.keys()))

        if "doublestack" in opts and len(order) != 2:
            print("PlotHist1D.MakeStack \tWARNING: double stack requested, but more than two hists. Defaulting to all hists in dict.")
        
        stackname = "stack_%s_%03d"%("_".join(opts), self.stack_counter)
        self.increment_stack()
        stack = THStack(stackname, stackname)
        if i_stack != 0:
            stack = i_stack.Clone()
        first = True
        for key in order:
            tmp_hist = i_hist_dict[key].Clone()
            # tmp_hist = i_hist_dict[key].Clone()
            # if type(tmp_hist) == type(MnvH2D()):
            #     tmp_hist = tmp_hist.GetCVHistoWithError()
            if "nofill" in opts or "doublestack" in opts:
                tmp_hist.SetLineColor(tmp_hist.GetFillColor())
                tmp_hist.SetFillStyle(0)
                if "isbackground" in opts:
                    tmp_hist.SetLineStyle(2)
                if "issignal" in opts:
                    tmp_hist.SetLineStyle(1)
            elif "issignal" in opts:
                tmp_hist.SetFillStyle(1001)
            elif "isbackground" in opts:
                tmp_hist.SetFillStyle(self.bkgfillstyle)
            # else:
            #     tmp_hist.SetFillStyle(1001)
            if "doublestack" in opts:
                # Background is on the bottom
                if first:
                    tmp_hist.SetLineStyle(2)
                # If signal has no entries, make the line the same
                elif tmp_hist.GetEntries() >= 0:
                    tmp_hist.SetLineStyle(2)
                # If signal has entries, keep line solid
                else:
                    tmp_hist.SetLineStyle(1)
            stack.Add(tmp_hist)
            first = False
        # stack.BuildPrimitives()
        # ROOT.SetOwnership(stack, True)
        return stack

    def DrawDummyHistOnPad(self, i_pad):
        """
        Hack to be able to draw something on all the pads
        """
        i_pad.cd()
        i_pad.Draw()
        self.dummy_hist.Draw("axis")
        
        return i_pad

    def DrawHistsOnPad(self, i_pad, withstack = True, opts = []):
        """
        Draw the histograms on a given pad

        Args:
            i_pad (TPad or TCanvas): pad to draw the hist on
            opts (list of str): options e.g. nodata, nomc, nomisc
        """
        dodata = False
        docompdata = False
        domc = False
        dobreakdown = False
        domisc = False
        if "nodata" not in opts and 'data_mnv_dict' in self:
            dodata = True
            if "docompdata" in opts:
                docompdata = True
        if "nomc" not in opts and 'mc_mnv_dict' in self:
            domc = True
            if "nobreakdown" not in opts:
                dobreakdown = True
        if "domisc" in opts and 'misc_mnv_dict' in self:
            domisc = True

        i_pad.cd()
        i_pad.Draw()

        first_hist = True
        self.dummy_hist.Draw("axis")

        if domc:
            if 'mctot_cv' not in self:
                self.mctot_cv, self.mctot_band = self.GetMCCVAndBand(self.mctot_mnv)
            if dobreakdown:
                if "unstack" in opts:
                    self.mc_stack_nofill.Draw("9 nostack noclear ][ same")
                else:
                    self.mc_stack.Draw("9 hist ][ same")
            else:
                self.mctot_cv.Draw("9 hist ][ same")
            self.mctot_band.Draw("9 E2 ][ same")

        if domisc:
            for key in self.misc_mnv_dict:
                self.misc_mnv_dict.Draw("9 hist ][ same")
        
        if dodata:
            # Your first data should be the main one, so it goes on top
            if docompdata:
                for key in reversed(list(self.data_syst_dict.keys())):
                    self.data_stat_dict[key].Draw("9 E1 X0 same")
                    self.data_syst_dict[key].Draw("9 E1 X0 same")
                    first_data = False
            else:
                self.data_stat_dict[list(self.data_stat_dict.keys())[0]].Draw("9 E1 X0 same")
                self.data_syst_dict[list(self.data_syst_dict.keys())[0]].Draw("9 E1 X0 same")
        self.dummy_hist.Draw("axis same")
        # i_pad.Modified()
        # i_pad.Update()

        # TODO: need to do this?
        return i_pad

    def DrawRatiosOnPad(self, i_pad, opts = []):
        """
        Draw the histograms on a given pad

        Args:
            opts (list of str): options e.g. nodata, nomc, nomisc
        """
        if 'ref_hist' not in self:
            print("PlotHist1D.DrawRatiosOnPad \tWARNING: tried to draw a ratio with no ref_hist set. Returning the pad I got.")
            return i_pad
        
        dodata = False
        docompdata = False
        domc = False
        dobreakdown = False
        dodoublestack = False
        domisc = False
        if "nodata" not in opts and 'data_mnv_ratio_dict' in self:
            dodata = True
            if "docompdata" in opts:
                docompdata = True
        if "nomc" not in opts and 'mc_mnv_ratio_dict' in self:
            domc = True
            if "nobreakdown" not in opts:
                dobreakdown = True
            if "dodoublestack" in opts and 'mc_ratio_doublestack_dict' in self:
                dodoublestack = True
        if "domisc" in opts and 'misc_mnv_dict' in self:
            domisc = True

        i_pad.cd()
        i_pad.Draw()

        self.ref_ratio_band.Draw("axis")
        self.ref_ratio_band.Draw("%s same"%(self.ref_ratio_band_drawopts))
        self.ref_ratio_line.Draw("%s same"%(self.ref_ratio_line_drawopts))
        
        if domc:
            if dobreakdown:
                if "dodoublestack" in opts:
                    for key in mc_ratio_doublestack_dict:
                        self.mc_ratio_doublestack_dict[key].Draw("9 hist noclear ][ same")
                else:
                    for key in mc_mnv_ratio_dict:
                        self.mc_mnv_ratio_dict[key].Draw("9 hist same")

        if domisc:
            for key in self.misc_mnv_ratio_dict:
                misc_mnv_dict.Draw("9 hist ][ same")
        
        if dodata:
            # first_data = True
            # Your first data should be the main one, so it goes on top
            if docompdata:
                for key in reversed(list(self.data_syst_ratio_dict.keys())):
                    data_stat_ratio_dict[key].Draw("9 E1 X0 same")
                    data_syst_ratio_dict[key].Draw("9 E1 X0 same")
            else:
                data_stat_ratio_dict[list(self.data_stat_ratio_dict.keys())[0]].Draw("9 E1 X0 same")
                data_syst_ratio_dict[list(self.data_syst_ratio_dict.keys())[0]].Draw("9 E1 X0 same")
        
        i_pad.Modified()
        i_pad.Update()

        # TODO: need to do this?
        return i_pad

    def Print1DHistAndRatio(self, withstack = True, hist_opts = [], ratio_opts = []):
        """
        Print 1D hists and ratios out
        """
        canvas_name = self.MakeUniqueCanvasName()
        canvas_title = "title"

        canvas = ROOT.TCanvas(canvas_name, canvas_title, 3200, 2700)
        ratio_frac = 0.3
        top = ROOT.TPad("hist%02d"%self.canvas_counter, "hist", 0, ratio_frac, 1.0, 1.0)
        # top.SetRightMargin(tmp_pad_rmarg)
        # top.SetLeftMargin(pad_lmarg)
        # top.SetTopMargin(tmp_topmarj)
        top.SetBottomMargin(0)
        top.SetFrameLineWidth(1)
        
        bottom = ROOT.TPad("Ratio%02d"%self.canvas_counter, "Ratio", 0, 0, 1.0, ratio_frac)
        # bottom.SetRightMargin(tmp_pad_rmarg)
        # bottom.SetLeftMargin(pad_lmarg)
        # bottom.SetBottomMargin(bottommarg)
        bottom.SetTopMargin(0)
        bottom.SetFrameLineWidth(1)

        # self.canvas_counter += 1
        self.increment_canvas()

        top.Draw()
        bottom.Draw()

        bottom_area = bottom.GetWNDC() * bottom.GetHNDC()
        top_area = top.GetWNDC() * top.GetHNDC()
        pads_area_scale = top_area / bottom_area

        top.cd()

        top = self.DrawHistsOnPad(
            i_pad = top,
            withstack = withstack,
            opts = hist_opts,
        )
        # TODO legend, other texts
        top.Modified()
        top.Update()

        bottom.cd()
        bottom = self.DrawRatiosOnPad(
            i_pad = bottom,
            opts = ratio_opts,
        )
        bottom.Modified()
        bottom.Update()

        top.cd()

        canvas.cd()
        canvas.Modified()
        canvas.Update()
        # TODO figure out printing

        # TODO do i need to do this clean up manually?

        top.Clear()
        bottom.Clear()
        top.Modified()
        top.Update()
        bottom.Modified()
        bottom.Update()

        canvas.cd()
        canvas.Clear()
        canvas.Modified()
        canvas.Update()



    def SetRangeString(self, i_range_str):
        """
        Sets the bin range string for panel plots

        Args:
            i_range_str (str): the string you put in
        Returns:
            None (sets member attr for tlatex of bin range and rangestring)
        """

        self.range_str = i_range_str

        # TODO: set the tlatex up for this too?

class PlotHist2D(PlotHist):
    def __init__(self, i_hist_dict, title = "", i_varinfo_dict = {}, opts = ["do1D", "do2D"]):
        print("PlotHist2D: \tMaking a 2D hist")
        super().__init__(i_hist_dict = i_hist_dict, title = title, i_varinfo_dict = i_varinfo_dict, opts = opts)
        # Get the number of x and y bins in these hists and check they are all the same, useful for doing things later
        first = True
        n_xbins = 0
        n_ybins = 0
        for a_key in i_hist_dict:
            for b_key in i_hist_dict[a_key]:
                tmp_n_xbins = i_hist_dict[a_key][b_key].GetNbinsX()
                tmp_n_ybins = i_hist_dict[a_key][b_key].GetNbinsY()
                if not first:
                    if tmp_n_xbins != n_xbins:
                        print("PlotHist2D.__init__ \t ERROR: input hists have different number of x bins")
                        sys.exit(1)
                    elif tmp_n_ybins != n_ybins:
                        print("PlotHist2D.__init__ \t ERROR: input hists have different number of y bins")
                        sys.exit(1)
                    else:
                        continue
                n_xbins = tmp_n_xbins
                n_ybins = tmp_n_ybins
                first = False
        self.n_xbins = n_xbins
        self.n_ybins = n_ybins

        # TODO maybe do something with this?
        self.opts_panelproj = opts
        self.opts_totalproj = opts

        # Useful check val to see if global scaling has been done already multiple times
        self.panelsarescaled = False

        if self.x_info_set and self.y_info_set and self.xy_info_set:
            self.varinfo_set = True

        # TODO
        self.SetPanelProjPlotHist1DList()
        self.SetTotalProjPlotHist1Ds()

    def SetPanelProjHists(self):
        """
        Sets member attr for the hist dicts for panels in both x and y projections. Remember these are not width normalized at all
        """

        # print("PlotHist2D.SetPanelProjHists(): \tSetting the list of dicts for projections of hists for each panel")
        panelprojx_inputdict = {}
        panelprojy_inputdict = {}
        # First do data
        if 'data_mnv_dict' in self:
            data_mnv_panelprojx_dict = {}
            data_mnv_panelprojy_dict = {}
            for key in self.data_mnv_dict:
                tmp_hist = self.data_mnv_dict[key].Clone()
                tmp_projx_list, tmp_projy_list = self.GetPanelProjHists(tmp_hist)
                data_mnv_panelprojx_dict[key] = tmp_projx_list
                data_mnv_panelprojy_dict[key] = tmp_projy_list
            # self.data_mnv_panelprojx_dict = data_mnv_panelprojx_dict
            # self.data_mnv_panelprojy_dict = data_mnv_panelprojy_dict
            panelprojx_inputdict["data"] = data_mnv_panelprojx_dict
            panelprojy_inputdict["data"] = data_mnv_panelprojy_dict
        # Now do MC, including "mctot"
        if 'mc_mnv_dict' in self:
            mc_mnv_panelprojx_dict = {}
            mc_mnv_panelprojy_dict = {}
            for key in self.mc_mnv_dict:
                tmp_hist = self.mc_mnv_dict[key].Clone()
                tmp_hist.Print()
                tmp_projx_list, tmp_projy_list = self.GetPanelProjHists(tmp_hist)
                mc_mnv_panelprojx_dict[key] = tmp_projx_list
                mc_mnv_panelprojy_dict[key] = tmp_projy_list
            self.mc_mnv_panelprojx_dict = mc_mnv_panelprojx_dict
            self.mc_mnv_panelprojy_dict = mc_mnv_panelprojy_dict
            mctot_mnv_panelprojx_list, mctot_mnv_panelprojy_list = self.GetPanelProjHists(self.mctot_mnv)
            mc_mnv_panelprojx_dict["mctot"] = mctot_mnv_panelprojx_list
            mc_mnv_panelprojy_dict["mctot"] = mctot_mnv_panelprojy_list
            panelprojx_inputdict["mc"] = mc_mnv_panelprojx_dict
            panelprojy_inputdict["mc"] = mc_mnv_panelprojy_dict

        # Now do any miscellaneous hists
        if 'misc_mnv_dict' in self:
            misc_mnv_panelprojx_dict = {}
            misc_mnv_panelprojy_dict = {}
            for key in self.misc_mnv_dict:
                tmp_hist = self.misc_mnv_dict[key].Clone()
                tmp_projx_list, tmp_projy_list = self.GetPanelProjHists(tmp_hist)
                misc_mnv_panelprojx_dict[key] = tmp_projx_list
                misc_mnv_panelprojy_dict[key] = tmp_projy_list
            self.misc_mnv_panelprojx_dict = misc_mnv_panelprojx_dict
            self.misc_mnv_panelprojy_dict = misc_mnv_panelprojy_dict
            panelprojx_inputdict["misc"] = misc_mnv_panelprojx_dict
            panelprojy_inputdict["misc"] = misc_mnv_panelprojy_dict

        # Now do the reference hist
        if 'ref_hist' in self:
            ref_hist_panelprojx_list, ref_hist_panelprojy_list = self.GetPanelProjHists(self.ref_hist)
            panelprojx_inputdict["ref"] = ref_hist_panelprojx_list
            panelprojy_inputdict["ref"] = ref_hist_panelprojy_list
        
        # Now invert the proj dicts so you get a list of dicts to use as input for PlotHist1D's
        panelprojx_inputdict_list = []
        for ybin in range(self.n_ybins):
            tmp_dict = {}
            for datamc in panelprojx_inputdict:
                if datamc not in tmp_dict: tmp_dict[datamc] = {}
                if datamc == "ref":
                    tmp_dict[datamc] = panelprojx_inputdict[datamc][ybin]
                    continue
                for key in panelprojx_inputdict[datamc]:
                    tmp_dict[datamc][key] = panelprojx_inputdict[datamc][key][ybin]
            panelprojx_inputdict_list.append(tmp_dict)

        panelprojy_inputdict_list = []
        for xbin in range(self.n_xbins):
            tmp_dict = {}
            for datamc in panelprojy_inputdict:
                if datamc not in tmp_dict: tmp_dict[datamc] = {}
                if datamc == "ref":
                    tmp_dict[datamc] = panelprojy_inputdict[datamc][xbin]
                    continue
                for key in panelprojy_inputdict[datamc]:
                    tmp_dict[datamc][key] = panelprojy_inputdict[datamc][key][xbin]
            panelprojy_inputdict_list.append(tmp_dict)

        self.panelprojx_inputdict_list = panelprojx_inputdict_list
        self.panelprojy_inputdict_list = panelprojy_inputdict_list

    def GetPanelProjHists(self, i_hist):
        """
        Make the projections for the panel plot
        
        Args:
            i_hist (hist)
        Return:
            two lists TODO
        """
        # print("PlotHist2D.GetPanelProjHists(): \tMaking the panel projections for hist %s"%i_hist.GetName())
        x_hist_list = []
        y_hist_list = []
        x_rangestring_list = []
        y_rangestring_list = []
        x_binwidth_list = []
        y_binwidth_list = []
        hist = i_hist.Clone()
        hist.Scale(1.0, "width")
        tmp_title = hist.GetTitle()
        for i in range(1, hist.GetNbinsY()+1):
            tmp_proj_name = "%s_projX_%s"%(hist.GetName().replace("h2D", "h"), str(i))
            tmp_proj = hist.ProjectionX(tmp_proj_name, i, i)
            # TODO not sure I need this
            # tmp_proj.SetTitle(tmp_title)
            # tmp_proj.GetXaxis().SetTitle(self.x_title)
            # tmp_proj.GetXaxis().CenterTitle()
            # tmp_proj.GetYaxis().SetTitle(self.xy_vert_title)
            # tmp_proj.GetYaxis().CenterTitle()
            tmp_proj.SetLineColor(hist.GetLineColor())
            tmp_proj.SetLineStyle(hist.GetLineStyle())
            tmp_proj.SetLineWidth(hist.GetLineWidth())
            tmp_proj.SetFillColor(hist.GetFillColor())
            tmp_proj.SetFillStyle(hist.GetFillStyle())
            tmp_proj.SetMarkerStyle(hist.GetMarkerStyle())
            tmp_proj.SetMarkerSize(hist.GetMarkerSize())
            tmp_proj.SetMarkerColor(hist.GetMarkerColor())

            x_hist_list.append(tmp_proj)
            upedge = hist.GetYaxis().GetBinUpEdge(i)
            loedge = hist.GetYaxis().GetBinLowEdge(i)
            tmp_range_string = "{min} < {var} < {max}".format(
                min = round(loedge,4), 
                var = self.y_title, 
                max = round(upedge,4)
            )
            x_rangestring_list.append(tmp_range_string)
            x_binwidth_list.append(upedge - loedge)

        for i in range(1, hist.GetNbinsX()+1):
            tmp_proj_name = "%s_projY_%s"%(hist.GetName().replace("h2D", "h"), str(i))
            tmp_proj = hist.ProjectionY(tmp_proj_name, i, i)

            # TODO not sure I need this
            # tmp_proj.SetTitle(tmp_title)
            # tmp_proj.GetXaxis().SetTitle(self.y_title)
            # tmp_proj.GetXaxis().CenterTitle()
            # tmp_proj.GetYaxis().SetTitle(self.xy_vert_title)
            # tmp_proj.GetYaxis().CenterTitle()
            tmp_proj.SetLineColor(hist.GetLineColor())
            tmp_proj.SetLineStyle(hist.GetLineStyle())
            tmp_proj.SetLineWidth(hist.GetLineWidth())
            tmp_proj.SetFillColor(hist.GetFillColor())
            tmp_proj.SetFillStyle(hist.GetFillStyle())
            tmp_proj.SetMarkerStyle(hist.GetMarkerStyle())
            tmp_proj.SetMarkerSize(hist.GetMarkerSize())
            tmp_proj.SetMarkerColor(hist.GetMarkerColor())

            y_hist_list.append(tmp_proj)
            upedge = hist.GetXaxis().GetBinUpEdge(i)
            loedge = hist.GetXaxis().GetBinLowEdge(i)
            tmp_range_string = "{min} < {var} < {max}".format(
                min = round(loedge,4), 
                var = self.x_title, 
                max = round(upedge,4)
            )
            y_rangestring_list.append(tmp_range_string)
            y_binwidth_list.append(upedge - loedge)
        if 'x_rangestring_list' not in self:
            self.x_rangestring_list = x_rangestring_list
        if 'y_rangestring_list' not in self:
            self.y_rangestring_list = y_rangestring_list
        if 'x_binwidth_list' not in self:
            self.x_binwidth_list = x_binwidth_list
        if 'y_binwidth_list' not in self:
            self.y_binwidth_list = y_binwidth_list
        return x_hist_list, y_hist_list

    def SetTotalProjHists(self):
        """
        Set the member total projection hists
        """
        # print("Plot2D.SetTotalProjHists(): \tSetting the list of dicts for total projections of hists")
        totalprojx_inputdict = {}
        totalprojy_inputdict = {}

        if 'data_mnv_dict' in self:
            data_mnv_totalprojx_dict = {}
            data_mnv_totalprojy_dict = {}
            for key in self.data_mnv_dict:
                tmp_hist = self.data_mnv_dict[key].Clone()
                tmp_projx, tmp_projy = self.GetTotalProjHists(tmp_hist)
                data_mnv_totalprojx_dict[key] = tmp_projx
                data_mnv_totalprojy_dict[key] = tmp_projy
            self.data_mnv_totalprojx_dict = data_mnv_totalprojx_dict
            self.data_mnv_totalprojy_dict = data_mnv_totalprojy_dict
            totalprojx_inputdict["data"] = data_mnv_totalprojx_dict
            totalprojy_inputdict["data"] = data_mnv_totalprojy_dict
        if 'mc_mnv_dict' in self:
            mc_mnv_totalprojx_dict = {}
            mc_mnv_totalprojy_dict = {}
            for key in self.mc_mnv_dict:
                tmp_hist = self.mc_mnv_dict[key].Clone()
                tmp_projx_list, tmp_projy_list = self.GetTotalProjHists(tmp_hist)
                mc_mnv_totalprojx_dict[key] = tmp_projx_list
                mc_mnv_totalprojy_dict[key] = tmp_projy_list
            self.mc_mnv_totalprojx_dict = mc_mnv_totalprojx_dict
            self.mc_mnv_totalprojy_dict = mc_mnv_totalprojy_dict
            mctot_mnv_totalprojx_list, mctot_mnv_totalprojy_list = self.GetTotalProjHists(self.mctot_mnv)
            mc_mnv_totalprojx_dict["mctot"] = mctot_mnv_totalprojx_list
            mc_mnv_totalprojy_dict["mctot"] = mctot_mnv_totalprojy_list
            totalprojx_inputdict["mc"] = mc_mnv_totalprojx_dict
            totalprojy_inputdict["mc"] = mc_mnv_totalprojy_dict

        if 'misc_mnv_dict' in self:
            misc_mnv_totalprojx_dict = {}
            misc_mnv_totalprojy_dict = {}
            for key in self.misc_mnv_dict:
                tmp_hist = self.misc_mnv_dict[key].Clone()
                tmp_projx_list, tmp_projy_list = self.GetTotalProjHists(tmp_hist)
                misc_mnv_totalprojx_dict[key] = tmp_projx_list
                misc_mnv_totalprojy_dict[key] = tmp_projy_list
            self.misc_mnv_totalprojx_dict = misc_mnv_totalprojx_dict
            self.misc_mnv_totalprojy_dict = misc_mnv_totalprojy_dict
            totalprojx_inputdict["mc"] = misc_mnv_totalprojx_dict
            totalprojy_inputdict["mc"] = misc_mnv_totalprojy_dict
        
        if 'ref_hist' in self:
            ref_hist_totalprojx_list, ref_hist_totalprojy_list = self.GetTotalProjHists(self.ref_hist)
            totalprojx_inputdict["ref"] = ref_hist_totalprojx_list
            totalprojy_inputdict["ref"] = ref_hist_totalprojy_list
        
        self.totalprojx_inputdict = totalprojx_inputdict
        self.totalprojy_inputdict = totalprojy_inputdict
        
    def GetTotalProjHists(self, i_hist):
        """
        Make the projections for the panel plot
        """
        # print("PlotHist2D.GetTotalProjHists(): \tNow making the total projections of hist %s"%i_hist.GetName())
        hist = i_hist.Clone()
        tmp_projx = hist.ProjectionX("%s_TotalProjX_%s"%(hist.GetName().replace("h2D","h"), self.x_title), 0, -1)
        tmp_projx.SetTitle(hist.GetTitle())
        tmp_projx.GetXaxis().SetTitle(self.y_title)
        tmp_projx.GetXaxis().CenterTitle()
        tmp_projx.GetYaxis().SetTitle(self.y_vert_title)
        tmp_projx.GetYaxis().CenterTitle()

        tmp_projy = hist.ProjectionY("%s_TotalProjY_%s"%(hist.GetName().replace("h2D","h"), self.y_title), 0, -1)
        tmp_projy.SetTitle(hist.GetTitle())
        tmp_projx.GetXaxis().SetTitle(self.x_title)
        tmp_projx.GetXaxis().CenterTitle()
        tmp_projx.GetYaxis().SetTitle(self.x_vert_title)
        tmp_projx.GetYaxis().CenterTitle()
        return tmp_projx, tmp_projy

    def SetPanelProjPlotHist1DList(self):
        """
        Make a list of PlotHist1D objects for each panel and assign to self. Also assigns maxes from each pad

        """
        # print("PlotHist2D.SetPanelProjPlotHist1DList(): Making a list of PlotHist1D objects for the panel plot.")
        if 'panelprojy_inputdict_list' not in self or 'panelprojx_inputdict_list' not in self:
            self.SetPanelProjHists()
        panelprojy_plothist1d_list = []
        panelprojx_plothist1d_list = []

        projy_global_max = 0.0
        for i in range(self.n_xbins):
            tmp_dict = self.panelprojy_inputdict_list[i]
            tmp_plothist1d = PlotHist1D(
                i_hist_dict = tmp_dict,
                title = "title",
                i_varinfo_dict = {"x":self.varinfo_dict["y"]},
                opts = self.opts,
            )
            tmp_pad_max = tmp_plothist1d.GetPadMax()
            projy_global_max = max(tmp_pad_max, projy_global_max)
            panelprojy_plothist1d_list.append(tmp_plothist1d)
        projx_global_max = 0.0
        for i in range(self.n_ybins):
            tmp_dict = self.panelprojx_inputdict_list[i]
            tmp_plothist1d = PlotHist1D(
                i_hist_dict = tmp_dict,
                title = "title",
                i_varinfo_dict = {"x":self.varinfo_dict["x"]},
                opts = self.opts,
            )
            tmp_pad_max = tmp_plothist1d.GetPadMax()
            projx_global_max = max(tmp_pad_max, projx_global_max)
            panelprojx_plothist1d_list.append(tmp_plothist1d)
        
        self.projy_global_max = projy_global_max
        self.projx_global_max = projx_global_max
        self.panelprojy_plothist1d_list = panelprojy_plothist1d_list
        self.panelprojx_plothist1d_list = panelprojx_plothist1d_list
    
    def SetTotalProjPlotHist1Ds(self):
        """
        Make a list of PlotHist1D objects for each panel and assign to self. Also assigns maxes from each pad

        """
        # print("PlotHist2D.SetPanelProjPlotHist1DList(): Making a list of PlotHist1D objects for the panel plot.")
        if 'totalprojy_inputdict_list' not in self or 'totalprojx_inputdict_list' not in self:
            self.SetTotalProjHists()
        totalprojy_plothist1d_list = []
        totalprojx_plothist1d_list = []

        totalprojy_plothist1d_list = PlotHist1D(
            i_hist_dict = self.totalprojy_inputdict,
            title = "title",
            i_varinfo_dict = {"x":self.varinfo_dict["y"]},
            opts = self.opts,
        )
        totalprojx_plothist1d_list = PlotHist1D(
            i_hist_dict = self.totalprojx_inputdict,
            title = "title",
            i_varinfo_dict = {"x":self.varinfo_dict["x"]},
            opts = self.opts,
        )
        
        self.totalprojy_plothist1d_list = totalprojy_plothist1d_list
        self.totalprojx_plothist1d_list = totalprojx_plothist1d_list

    def RescalePanelPads(self, do_maxpad = True, do_dataareascale = False, opts = []):
        """
        Scale all the plothist1ds for the panel plot

        Args:
            do_maxpad (bool): use the panel with the largest max and scale other pads to match
            do_dataareascale (bool): area scale the mc in each panel to the data in that panel
            opts (list of str): use opts like those used in PlotHist1D.Scale, but separated as list? TODO

        Returns:
            None
        """
        # print("PlotHist2D.RescalePanelPads: Scaling all pads")
        
        # TODO, will need to find new x and y max after this
        if do_dataareascale or "dataareascale" in opts:
            print("WARNING: areascale not set up")

            # Reset the global maxes
            projy_global_max = 0.0
            for plothist1d in panelprojy_plothist1d_list:
                tmp_max = plothist1d.GetPadMax()
                projy_global_max = max(tmp_max, projy_global_max)
            self.projy_global_max = projy_global_max
            projx_global_max = 0.0
            for plothist1d in panelprojx_plothist1d_list:
                tmp_max = plothist1d.GetPadMax()
                projx_global_max = max(tmp_max, projx_global_max)
            self.projx_global_max = projx_global_max

        projy_global_max = 0.0

        if do_maxpad or "maxpad" in opts and not self.panelsarescaled:
            projy_pad_scales = []
            for plothist1d in self.panelprojy_plothist1d_list:
                plothist1d.GetPadMax()
                tmp_pad_scale = 1.0
                if tmp_pad_max > 0:
                    tmp_pad_scale = eval('{:.{p}g}'.format(self.projy_global_max / tmp_pad_max, p=3)) # This shortens it to 3 sigfigs?
                # This will scale by that and make a multiplier string
                plothist1d.Scale(value = tmp_pad_scale, multipstring = True) 
                projy_pad_scales.append(tmp_pad_scale)
            
            projx_pad_scales = []
            for plothist1d in self.panelprojx_plothist1d_list:
                plothist1d.GetPadMax()
                tmp_pad_scale = 1.0
                if tmp_pad_max > 0:
                    tmp_pad_scale = eval('{:.{p}g}'.format(self.projx_global_max / tmp_pad_max, p=3)) # This shortens it to 3 sigfigs?
                # This will scale by that and make a multiplier string
                plothist1d.Scale(value = tmp_pad_scale, multipstring = True)
                projx_pad_scales.append(tmp_pad_scale)
            
            self.panelsarescaled = True
            self.projy_pad_scales = projy_pad_scales
            self.projx_pad_scales = projx_pad_scales
        if "undomaxpad" in opts and self.panelsarescaled:
            for i in range(len(self.panelprojy_plothist1d_list)):
                tmp_plothist1d = self.panelprojy_plothist1d_list[i].Scale(value = 1/projy_pad_scales[i])
            for i in range(len(self.panelprojx_plothist1d_list)):
                tmp_plothist1d = self.panelprojx_plothist1d_list[i].Scale(value = 1/projx_pad_scales[i])
            self.panelsarescaled = False

    def GetPanelGridValues(self, n_panels = 3, grid_option = "square", set_grid_x = 0):
        """
        Finds the number of x and y panels for a panel plot, and the number of 
        buffer panels left. It ensures there is at least one buffer panel

        Args:
            n_panels (int): the number of panels you need for your panel plot, 3 is really the minimum that makes sense
            grid_option (string): the style of grid. 'square' gets it as square as possible, good for talks and single
                column papers. 'tall' makes it 2 or 3 panels wide, good for double column papers. 'singlecolumn' makes it 
                really long, with one hist in each row, good for something idk
            set_grid_x (int): manual override for the number of columns, will figure out the rest for you if set to > 0
        Returns:
            grid_x (int): number number of panels in horizontal
            grid_y (int): number of panels in vertical direction
            n_buffer_panels (int): number of empty panels that will be left
        """
        # This assigns member values grid_x grid_y and n_buffer_panels
        # You can use these to figure out how to build your panel canvas
        grid_x = 1
        grid_y = 1
        n_buffer_panels = 0
        if n_panels <= 3:
            print("Plot2D: \tWarning: trying to do 3 or less panels for a panel plot. Defaulting to single column...")
            grid_option = "singlecolumn"
            # sys.exit(1)
        # This option tries to get it as evenly as possible for x and y grid
        if grid_option == "square":
            # New way of doing it?
            tmp_grid_x = math.ceil(math.sqrt(n_panels))
            tmp_grid_y = tmp_grid_x
            n_buffer_panels = tmp_grid_x * tmp_grid_y - n_panels
            
            req_buffer = 2
            if tmp_grid_y > 3: req_buffer = 3
            if n_buffer_panels > tmp_grid_x:
                tmp_grid_y -= math.floor(n_buffer_panels/tmp_grid_x)
                n_buffer_panels = tmp_grid_x * tmp_grid_y - n_panels
            while n_buffer_panels%tmp_grid_x == 0:
                if tmp_grid_y == 1: break
                tmp_grid_x += 1
                n_buffer_panels = tmp_grid_x * tmp_grid_y - n_panels
                if n_buffer_panels > tmp_grid_x:
                    tmp_grid_y -= math.floor(n_buffer_panels/tmp_grid_x)
                    n_buffer_panels = tmp_grid_x * tmp_grid_y - n_panels
            grid_x = tmp_grid_x 
            grid_y = tmp_grid_y
        # This makes a longer version prioritizing a narrower plot (maybe better for 2 (text) column publication)
        elif grid_option == "tall":
            tmp_grid_x = 2
            tmp_grid_y = math.ceil(n_panels/tmp_grid_x)
            while tmp_grid_y > 6:
                if tmp_grid_x >= 4: break
                tmp_grid_x += 1
                tmp_grid_y = math.ceil(n_panels/tmp_grid_x)
            grid_x = tmp_grid_x
            grid_y = tmp_grid_y
            n_buffer_panels = grid_x * grid_y - n_panels
        # This makes really wide hists in a single column
        elif grid_option == "singlecolumn":
            grid_x = 1
            grid_y = n_panels
            n_buffer_panels = 0
        # If you're manually setting the grid_x, just do that
        if set_grid_x > 0:
            grid_x = set_grid_x
            grid_y = math.ceil(n_panels/grid_x)
            n_buffer_panels = grid_x * grid_y - n_panels
        grid_x = grid_x
        grid_y = grid_y
        n_buffer_panels = n_buffer_panels
        return grid_x, grid_y, n_buffer_panels

    def SetGridCanvas(self, name = "", grid_option = "square", set_grid_x = 0):
        """
        Make a grid canvas for the x and y panel projections. A single set are set for each instance of PlotHist2D, and can be reused

        Args:
            name (string): name for each canvas. it's good practice to use a unique name for each canvas you make globally
            grid_option (string): figures out how to arrange the panels, see GetPanelGridValues
            set_grid_x (int): manual override for how wide you set your grid, see GetPanelGridValues
        Returns:
            None, but sets various functions 
        """

        self.projx_gridcanvas = self.GetGridCanvas(axis = "x", name = name, grid_option = grid_option, set_grid_x = set_grid_x)
        self.projy_gridcanvas = self.GetGridCanvas(axis = "y", name = name, grid_option = grid_option, set_grid_x = set_grid_x)

    def GetGridCanvas(self, axis = "x", name = "", grid_option = "square", set_grid_x = 0):
        """
        Get the grid canvas for x or y panel projections
        
        Args:
            TODO

        Returns:
            A grid canvas
        """
        print("PlotHist2D: Making the grid canvases")
        if axis == "x":
            if 'projx_gridcanvas' in self:
                return self.projx_gridcanvas
            n_proj_panels = self.n_ybins
            hor_title = self.x_title
        if axis == "y":
            if 'projy_gridcanvas' in self:
                return self.projy_gridcanvas
            n_proj_panels = self.n_xbins
            hor_title = self.y_title

        grid_x, grid_y, n_buffer_panels = self.GetPanelGridValues(
            n_panels = n_proj_panels, 
            grid_option = grid_option, 
            set_grid_x = set_grid_x
        )

        projcanvas_basename = ""
        if name != "":
            projcanvas_basename = name
        elif 'canvas_basename' in self:
            projcanvas_basename = self.canvas_basename
        else:
            projcanvas_basename = self.MakeUniqueCanvasName()
        width = 3680
        height = 2700
        proj_gridcanvas = GridCanvas(
            name = "%s_proj%s_panel"%(projcanvas_basename, axis.capitalize()),
            nPadsX = grid_x,
            nPadsY = grid_y,
            ww = width,
            wh = height
        )
        proj_gridcanvas.ResetPads()
        axistitle_size = 0.06
        proj_gridcanvas.SetTitleSize(height * axistitle_size)
        proj_gridcanvas.SetXTitle(hor_title)
        proj_gridcanvas.SetYTitle(self.xy_vert_title)
        proj_gridcanvas.SetTitle(self.title)

        if axis == "x":
            self.projx_grid_x = grid_x
            self.projx_grid_y = grid_y
            self.projx_n_buffer_panels = n_buffer_panels

            # self.projx_gridcanvas = proj_gridcanvas
        if axis == "y":
            self.projy_grid_x = grid_x
            self.projy_grid_y = grid_y
            self.projy_n_buffer_panels = n_buffer_panels

            # self.projy_gridcanvas = proj_gridcanvas
        proj_gridcanvas.SetRightMargin(0.025)
        proj_gridcanvas.SetLeftMargin(0.12)
        proj_gridcanvas.SetTopMargin(0.05)
        proj_gridcanvas.SetBottomMargin(0.1)
        
        proj_gridcanvas.SetInterpadSpace(0.0)
        return proj_gridcanvas

    def DrawPanelsOnGridCanvas(self):
        # gridcanvas = self.projx_gridcanvas.Clone(self.MakeUniqueCanvasName())
        self.projx_gridcanvas.cd()
        self.projx_gridcanvas.Draw()
        for i in range(1,self.n_ybins+1):
            pad = self.projx_gridcanvas.cd(i)
            pad.SetFrameLineWidth(2)
            pad.Draw()
            pad = self.panelprojx_plothist1d_list[i-1].DrawDummyHistOnPad(pad)
            pad.Modified()
        for i in range(1,self.n_ybins+1):
            pad = self.projx_gridcanvas.cd(i)
            # pad.SetFrameLineWidth(2)
            pad.Draw()
            pad = self.panelprojx_plothist1d_list[i-1].DrawHistsOnPad(pad)
            pad.Modified()
            # pad.Update()
        self.projx_gridcanvas.cd()

        outname = str("test%03dX.pdf"%(self.canvas_counter))
        print(outname)
        # sys.exit(1)
        self.projx_gridcanvas.Print(outname)
        self.projx_gridcanvas.ResetPads()
        
        self.projy_gridcanvas.cd()
        self.projy_gridcanvas.Draw()
        for i in range(1,self.n_xbins+1):
            pad = self.projy_gridcanvas.cd(i)
            pad.SetFrameLineWidth(2)
            pad.Draw()
            pad = self.panelprojy_plothist1d_list[i-1].DrawDummyHistOnPad(pad)
            pad.Modified()
        for i in range(1,self.n_xbins+1):
            pad = self.projy_gridcanvas.cd(i)
            # pad.SetFrameLineWidth(2)
            pad.Draw()
            pad = self.panelprojy_plothist1d_list[i-1].DrawHistsOnPad(pad)
            pad.Modified()
            # pad.Update()
        self.projy_gridcanvas.cd()

        outname = str("test%03dY.pdf"%(self.canvas_counter))
        print(outname)
        # sys.exit(1)
        self.projy_gridcanvas.Print(outname)
        self.projy_gridcanvas.ResetPads()

    def SetPlotHist1DPanelList(self):
        """
        Set the lists of PlotHist1D objects for the panel plots

        Returns:
            None (sets two lists of PlotHist1D objects)
        """
        if 'panelprojx_inputdict_list' not in self or 'panelprojy_inputdict_list' not in self:
            print("PlotHist2D.SetPlotHist1DPanelList: \tWARNING could not find projection hist lists, trying to them now...")
            self.SetPanelProjHists()
        
        # Loop over the lists for each projection
        for proj in ["x", "y"]:
            tmp_projdict_list = []
            hor_axis_title = self.x_title
            vert_axis_title = self.xy_vert_title
            logx = self.x_logx
            logy = self.x_logy
            rangestring_list = self.x_rangestring_list
            tmp_varinfo_dict = {"x": self.varinfo_dict["x"]}
            
            if proj == "x":
                tmp_projdict_list = self.panelprojx_inputdict_list
            else: #if proj == "y":
                tmp_varinfo_dict = {"y": self.varinfo_dict["y"]}
                tmp_projdict_list = self.panelprojy_inputdict_list
                hor_axis_title = self.y_title
                logx = self.y_logx
                logy = self.y_logy
                rangestring_list = self.y_rangestring_list

            if len(rangestring_list) != len(tmp_projdict_list):
                print("PlotHist2D.SetPlotHist1DPanelList: \tERROR hists are not matched to range string lists. exiting...")
                sys.exit(1)
            tmp_plothist1d_list = []
            for i in range(len(tmp_projdict_list)):
                tmp_plothist1d = PlotHist1D(
                    i_hist_dict = tmp_projdict_list[i],
                    title = "", 
                    i_varinfo_dict = tmp_varinfo_dict,
                    opts = self.opts_panelproj,
                )
                # TODO: maybe range string gets handled internally with drawing pads?
                tmp_plothist1d.SetRangeString(rangestring_list[i])
                
                tmp_plothist1d_list.append(tmp_plothist1d)

            if proj == "x":
                self.panelprojx_plothist1d_list = tmp_plothist1d_list
            else: # if proj == "y"
                self.panelprojy_plothist1d_list = tmp_plothist1d_list

    def SetPlotHist1DTotalProj(self):
        """
        Set the PlotHist1D objects for the total projection plots

        Returns:
            None (sets two PlotHist1D objects)
        """
        if 'totalprojx_inputdict' not in self or 'totalprojy_inputdict' not in self:
            print("PlotHist2D.SetPlotHist1DPanelList: \tWARNING could not find total projection hists, trying to them now...")
            self.SetTotalProjHists()

        # Loop over the lists for each projection
        for proj in ["x", "y"]:
            tmp_projdict = {}
            hor_axis_title = self.x_title
            vert_axis_title = self.x_vert_title
            logx = self.x_logx
            logy = self.x_logy
            tmp_varinfo_dict = {"x": self.varinfo_dict["x"]}

            if proj == "x":
                tmp_projdict = self.totalprojx_inputdict
            else: #if proj == "y":
                tmp_projdict = self.totalprojy_inputdict
                hor_axis_title = self.y_title
                vert_axis_title = self.y_vert_title
                logx = self.y_logx
                logy = self.y_logy
                tmp_varinfo_dict = {"y": self.varinfo_dict["y"]}

            tmp_plothist1d = PlotHist1D(
                i_hist_dict = tmp_projdict,
                title = "", 
                i_varinfo_dict = tmp_varinfo_dict, 
                opts = self.opts_totalproj,
            )
            if proj == "x":
                self.totalprojx_plothist1d = tmp_plothist1d
            else: # if proj == "y":
                self.totalprojy_plothist1d = tmp_plothist1d


    # TODO something about arranging panel texts based on where bin contents are?
    # TODO bin width normalizations for panels (check xsecplots on how to do that)


def main():
    ROOT.TH1.AddDirectory(ROOT.kFALSE)
    colors = {
        "kP8Blue": ROOT.kP8Blue,
        "kP8Orange": ROOT.kP8Orange,
        "kP8Pink": ROOT.kP8Pink,
        "kP8Red": ROOT.kP8Red,
    }
    for key in colors:
        print("\"%s\": %s,"%(key, str(colors[key])))    

    factory = PlotFactory("/Users/nova/git/CCQENu/plotting/config/plotdriver_plotconfig.json")
    factory.MakeAllPlotHists()
if __name__ == "__main__":
    main()
