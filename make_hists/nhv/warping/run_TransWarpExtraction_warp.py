import os
import sys
import subprocess

from functools import partial
from multiprocessing.dummy import Pool
from subprocess import call

import ROOT
from PlotUtils import MnvH1D, MnvH2D 
import datetime
mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")

# How to run. Closure test, MnvTune v2
# python run_TransWarpExtraction_f.py
# nohup python run_TransWarpExtraction_f.py >& Tela_run_TransWarpExtraction_f.txt &
doTransWarpPOTScale = False

doExcludebin = False

doClosure = False 
do1D = True
do2D = False
dotuned = True

excludebin = 1

excludebins = [
    1,
]

unfolding_model = "MnvTune4.3.1"

exclude_models = [
    # "MnvTunev4.3",
    # "MnvTunev4.3.1_SuSA2p2h",
    # "MnvTunev4.3.1_elastic",
    # "MnvTunev4.3.1_absorption",
    # "MnvTunev4.3.1_no2p2htune",
    # "MnvTunev1.0.1",
    # "MnvTunev1.0.1_elastic",
    # "MnvTunev1.0.1_absorption",
]

catstodo = [
    "qelike"
]


iters_list = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    # 26,
    # 27,
    # 28,
    # 29,
    # 30,
    # 40,
    # 50,
    # 60,
    # 70,
    # 80,
    # 90,
    # 100,
]
iters = str(",".join([str(iter) for iter in iters_list]))
print(iters)
num_uni = 3000

uncfactors = {
    "recoil": 5.6,
    "EAvail": 10.5,
    "EAvailoldbins":10.5,
    "EAvailoldbinscutoff":10.5,
    "ptmu": 5.6
}

# ----------------------------
# Running TransWarpExtraction
# ----------------------------


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
        os.mkdir(plotdir)
    if subdir == "":
        return plotdir
    if not os.path.exists(os.path.join(plotdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(plotdir, subdir))
        os.mkdir(os.path.join(plotdir, subdir))
    return os.path.join(plotdir, subdir)

def MakeOutputDir(subdir=""):
    """
    Subdir is the one for all output root files that this script should ouptut. You will need to add
    any other subdirs in the script itself (e.g. based off input file name)
    """
    outputdir = ""
    base_outputdir = os.environ.get("OUTPUTLOC")
    if base_outputdir != None:
        outputdir = os.path.join(base_outputdir, month + year)
    else:
        outputdir = os.path.join("/Users/nova/git/output/", month + year)
    if not os.path.exists(outputdir):
        print("Can't find output dir. Making it now... ", outputdir)
        os.mkdir(outputdir)
    if subdir == "":
        return outputdir
    if not os.path.exists(os.path.join(outputdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(outputdir, subdir))
        os.mkdir(os.path.join(outputdir, subdir))
    return os.path.join(outputdir, subdir)

studytag = "allblobs_fullremoval_1and2track_newmodels"
if len(sys.argv) == 1:
    print("python3 run_TransWarpExtraction_warp.py <studytag subdir> <unfolding model>")
    print("enter study tag and unfolding model as optional argument. Defaulting to studytag ", studytag, "\t unfolding_model", unfolding_model)
if len(sys.argv)> 2:
    studytag = sys.argv[1]
if len(sys.argv) == 2:
    print("enter unfolding model as optional argument. Defaulting to ", unfolding_model)
if len(sys.argv) == 3:
    unfolding_model = sys.argv[2]

# This is where warping studies files should live
warping_outdirbase = MakeOutputDir("warpingstudies")

study_outdirbase = os.path.join(warping_outdirbase, studytag)
if not os.path.exists(study_outdirbase):
    print("WARNING: having to make study dir, this will throw an error in a sec. Study dir is:\n\t",study_outdirbase)
    os.mkdir(study_outdirbase)
# This is for input root files 
eventloopout_dirbase = os.path.join(study_outdirbase,"eventloopout")
if not os.path.exists(eventloopout_dirbase):
    print("ERROR: eventloop out dir does not exist. Looked for it here:\n\t", eventloopout_dirbase)
    sys.exit(1)

unfoldingmodel_input_dirbase = os.path.join(eventloopout_dirbase,unfolding_model)
if not os.path.exists(unfoldingmodel_input_dirbase):
    print("ERROR: unfoldingmodel eventloop out dir does not exist. Looked for it here:\n\t", unfoldingmodel_input_dirbase)
    sys.exit(1)

model_list = [model for model in os.listdir(eventloopout_dirbase) if (os.path.isdir(os.path.join(eventloopout_dirbase,model)) and model not in exclude_models)]
print(model_list)


# This is for the outputs of this script
warp_outdirbase = os.path.join(study_outdirbase,"warps")
if not os.path.exists(warp_outdirbase):
    print(warp_outdirbase)
    os.mkdir(warp_outdirbase)

nowarp_dir_list = os.listdir(unfoldingmodel_input_dirbase)
nowarp_file_name = ""
for file_name in nowarp_dir_list:
    if "potscaled_combined_FullSample" in file_name:
        nowarp_file_name = os.path.join(unfoldingmodel_input_dirbase, file_name)
        print("looking at unfolding model file ", nowarp_file_name)
if nowarp_file_name == "":
    print("ERROR: Couldn't find nowarp file in",unfoldingmodel_input_dirbase,"\n\tExiting.....")
    sys.exit(1)
nowarpfile = ROOT.TFile(nowarp_file_name, "READONLY")
if doTransWarpPOTScale:
    h_POT = nowarpfile.Get("Combined_POT_Summary")
    # Full ME data POT, avoids issue of using not the full data set
    POTScale = tot_data_POT/h_POT.GetBinContent(3)
    print("Running with -P option set to ", POTScale)

# Get list of variables to do warping over, it should have reconstructed, selected_truth, and migration
nowarpfile = ROOT.TFile(nowarp_file_name, "READONLY")
keys = nowarpfile.GetListOfKeys()

# Walk through hist names to get vars to do
nowarp_hist_name_dict = {}
for k in keys:
    name = k.GetName()
    if "___" not in name:
        continue
    parse = name.split("___")
    if len(parse) < 5: continue

    histdim = parse[0]
    sample = parse[1]
    cat = parse[2]
    variable = parse[3]
    recotrutype = parse[4]

    if "types" in recotrutype: continue
    if "simulfit" in recotrutype: continue
    if "tuned" in recotrutype and not dotuned: continue
    if dotuned and "tuned" not in recotrutype: continue
    if "noPOTscale" in cat and not doTransWarpPOTScale: continue
    if "noPOTscale" not in cat and doTransWarpPOTScale: continue
    
    if sample not in ["QElike", "QElike_warped"]: continue

    if cat not in catstodo: continue # basically just qelike
    dim = ""
    if histdim == "h":
        dim = "1D"
    else:
        dim = histdim.replace("h","")

    if dim not in nowarp_hist_name_dict:
        nowarp_hist_name_dict[dim] = {}
    if variable not in nowarp_hist_name_dict[dim]:
        nowarp_hist_name_dict[dim][variable] = {}
    if recotrutype not in nowarp_hist_name_dict[dim][variable]:
        nowarp_hist_name_dict[dim][variable][recotrutype] = {}

    nowarp_hist_name_dict[dim][variable][recotrutype] = name
tunedtag = ""
if dotuned:
    tunedtag="_tuned"  

recotrutypelist = [
    "reconstructed%s"%(tunedtag), 
    "selected_truth%s"%(tunedtag),
    "response%s_migration"%(tunedtag)
]
tuned_recotrutypelist = [
    "reconstructed_tuned", 
    "selected_truth_tuned",
    "response_tuned_migration"
]

for a_dim in nowarp_hist_name_dict.keys():
    num_dim = 1
    if a_dim in ["1D","HD"]:
        num_dim = 1
    elif a_dim in ["2D"]:
        num_dim = 2

    skipped_vars = []
    for b_variable in nowarp_hist_name_dict[a_dim].keys():
        foundtypes = True
        # for testtype in recotrutypelist:
        #     if not dotuned and (testtype not in nowarp_hist_name_dict[a_dim][b_variable].keys()):
        #         foundtypes = False
        #         break
        # for testtype in tuned_recotrutypelist:
        #     if dotuned and (testtype not in nowarp_hist_name_dict[a_dim][b_variable].keys()):
        #         foundtypes = False
        #         break        
        for testtype in tuned_recotrutypelist:
            if testtype not in nowarp_hist_name_dict[a_dim][b_variable].keys():
                foundtypes = False
                break
        if not foundtypes:
            skipped_vars.append(b_variable)
            continue
    for var in skipped_vars:
        print("skipping ", var)
        nowarp_hist_name_dict[a_dim].pop(var)

      
# Loop over all the models now?
commands= []

output_file_list = []
# for model in model_list:
#     if model == unfolding_model:
#         continue
#     warp_model_input_dirbase = os.path.join(eventloopout_dirbase, model)

#     tmp_warp_dir_list = os.listdir(warp_model_input_dirbase)
#     tmp_warp_file_name = ""
#     for file_name in tmp_warp_dir_list:
#         if "potscaled_combined_FullSample" in file_name:
#             tmp_warp_file_name = os.path.join(warp_model_input_dirbase, file_name)
#             print("looking at warp model", model, " file ", tmp_warp_file_name)
#     if tmp_warp_file_name == "":
#         print("Warning: Couldn't find eventloop file in",warp_model_input_dirbase,"\n\t Skipping warp model "+model+".....")
#         continue
#     tmp_warp_file = ROOT.TFile(tmp_warp_file_name, "READONLY")
#     warp_keys = tmp_warp_file.GetListOfKeys()

for a_dim in nowarp_hist_name_dict:
    num_dim = "1"
    if a_dim in ["1D","HD"]:
        num_dim = "1"
        if not do1D:
            continue
    elif a_dim in ["2D"]:
        if not do2D:
            continue
        num_dim = "2"
    for b_variable in nowarp_hist_name_dict[a_dim].keys():
        print("Looking at variable ", b_variable)


        for model in model_list:
            unfold_reco_hist = nowarp_hist_name_dict[a_dim][b_variable]["reconstructed%s"%(tunedtag)]
            unfold_true_hist = nowarp_hist_name_dict[a_dim][b_variable]["selected_truth%s"%(tunedtag)]
            unfold_resp_hist = nowarp_hist_name_dict[a_dim][b_variable]["response%s_migration"%(tunedtag)]
            tmp_num_uni = num_uni
            if model == unfolding_model:
                if not doClosure:
                    continue
                warp_reco_hist = unfold_reco_hist
                warp_true_hist = unfold_true_hist

                if not doClosure:
                    continue
                tmp_output_dir_name =  os.path.join(
                    warp_outdirbase,
                    "%sunfold%s_closure" % (tunedtag.replace("_",""),unfolding_model)
                )
                if not os.path.exists(tmp_output_dir_name):
                    os.mkdir(tmp_output_dir_name)
                
                output_file_name = os.path.join(
                    tmp_output_dir_name,
                    "TransWarpOut_Warp_%s_%sunfold%s_closure_%s_TransWarpDataPOTScale_%siters_%sunivs.root"
                    % ("QElike",tunedtag.replace("_",""), unfolding_model, b_variable, str(iters_list[-1]), str(num_uni)),
                )
                tmp_num_uni = 100

            else:
                warp_model_input_dirbase = os.path.join(eventloopout_dirbase, model)

                tmp_warp_dir_list = os.listdir(warp_model_input_dirbase)
                tmp_warp_file_name = ""
                for file_name in tmp_warp_dir_list:
                    if "potscaled_combined_FullSample" in file_name:
                        tmp_warp_file_name = os.path.join(warp_model_input_dirbase, file_name)
                        print("looking at warp model", model, " file ", tmp_warp_file_name)
                if tmp_warp_file_name == "":
                    print("Warning: Couldn't find eventloop file in",warp_model_input_dirbase,"\n\t Skipping warp model "+model+".....")
                    continue
                
                tmp_warp_file = ROOT.TFile(tmp_warp_file_name, "READONLY")
                warp_keys = tmp_warp_file.GetListOfKeys()

                tmp_warp_hist_name_dict = {}
                foundtypes = True
                for c_type in nowarp_hist_name_dict[a_dim][b_variable]:
                    nowarp_histname = nowarp_hist_name_dict[a_dim][b_variable][c_type]
                    print("nowarp_histname ", nowarp_histname)
                    test_nowarp_histname = nowarp_histname.replace("_tuned","")
                    if test_nowarp_histname not in warp_keys:
                        print("Can't find hist %s for model %s in %s"%(test_nowarp_histname, model, tmp_warp_file_name))
                        foundtypes = False
                        break
                    tmp_warp_hist_name_dict[c_type.replace("_tuned","")] = test_nowarp_histname
                if not foundtypes:
                    print("Can't find all the hists for variable %s in  warp %s. Skipping this model..."%(b_variable, model))
                    continue


                warp_reco_hist = tmp_warp_hist_name_dict["reconstructed"]
                warp_true_hist = tmp_warp_hist_name_dict["selected_truth"]

                tmp_output_dir_name =  os.path.join(
                    warp_outdirbase,
                    "%sunfold%s_warp%s" % (tunedtag.replace("_",""),unfolding_model, model)
                    )
                if not os.path.exists(tmp_output_dir_name):
                    os.mkdir(tmp_output_dir_name)
                
                output_file_name = os.path.join(
                    tmp_output_dir_name,
                    "TransWarpOut_Warp_%s_%sunfold%s_warp%s_%s_TransWarpDataPOTScale_%siters_%sunivs.root"
                    % ("QElike",tunedtag.replace("_",""), unfolding_model, model, b_variable, str(iters_list[-1]), str(num_uni)),
                )
            if doExcludebin:
                exbinfile_string = str("_".join([str(exbin) for exbin in exclude_bins]))
                output_file_name.replace(".root","%s.root"%(exbinfile_string))
            cmd = [
                "TransWarpExtraction",
                "--output_file",
                output_file_name,
                "--data_file",
                tmp_warp_file_name,
                "--data",
                warp_reco_hist,
                "--data_truth_file",
                tmp_warp_file_name,
                "--data_truth",
                warp_true_hist,
                "--reco_file",
                nowarp_file_name,
                "--reco",
                unfold_reco_hist,
                "--truth_file",
                nowarp_file_name,
                "--truth",
                unfold_true_hist,
                "--migration_file",
                nowarp_file_name,
                "--migration",
                unfold_resp_hist,
                "--num_iter",
                iters,
                "--num_uni",
                str(tmp_num_uni),
                "--max_chi2",
                "5000",
                "--step_chi2",
                "1",
                "--num_dim",
                num_dim,
                # "--dolite",
            ]
            if b_variable in uncfactors and model != unfolding_model:
                cmd.append("--corr_factor")
                cmd.append(str(uncfactors[b_variable]))
            if doTransWarpPOTScale:
                print("Really running with -P option set to ", POTScale)
                cmd.append("-P")
                cmd.append(str(POTScale))
            if doExcludebin:
                print("WARNING: excluding bin ", excludebin)
                cmd.append("-x")
                exbincmd_string = str(",".join([str(exbin) for exbin in exclude_bins]))
                cmd.append(str(exbincmd_string))
            print(" ".join(cmd))
            commands.append(cmd)
            # subprocess.run(cmd)
            output_file_list.append(output_file_name)
            print("here")

if not do2D:
    pool = Pool(3)
    for i, returncode in enumerate(pool.imap(partial(call), commands)):
        if returncode != 0:
            print("%d command failed: %d" % (i, returncode))
else:
    for cmd in commands:
        subprocess.run(cmd)
print(
    "Done with warps using unfolding model %s and warps %s"%(
        unfolding_model, 
        str(" ".join([str(model) for model in model_list]))
        )
    )

print("TransWarpOutputs written to")
for file in output_file_list:
    print(file)

# os.chdir(str(os.getenv("NUKECC_ANA")) + "/unfolding")
print("I'm in %s" % os.getcwd())
print(" All done!!")


# studies = [
#     "",
#     # "nocut_oldbinning",
#     # "recoilcut",
#     # "nocut",
#     # "lowbins",
# ]

# samples = {
#     "": "QElike",
#     "nocut_oldbinning": "QElike",
#     "recoilcut": "QElike_maxrecoil",
#     "nocut": "QElike",
#     "lowbins": "QElike",
# }

# variables = [
#     "recoil",
#     "EAvail",
#     # "EAvailNoNonVtxBlobs",
#     "ptmu",
#     # "EAvailLeadingBlob",
# ]

# warps = [
#     "MnvTunev2",
#     "no2p2htune"
# ]

# uncfactors = {
#     "recoil": {
#         "": 5.6,
#         "nocut_oldbinning": 6.0,
#         "recoilcut": 7.9,  # good
#         "nocut": 4.9,  # good
#         "lowbins": 7.2,  # good
#     },
#     "EAvail": {
#         "": 10.5,
#         "nocut_oldbinning": 6.0,
#         "recoilcut": 8.2,  # good
#         "nocut": 6.0,  # good
#         "lowbins": 9.0,  # good
#     },
#     "EAvailNoNonVtxBlobs": {
#         "nocut_oldbinning": 6.5,
#         "recoilcut": 9.0,  # good
#         "nocut": 6.5,  # good
#         "lowbins": 6.8,  # good
#     },
#     "ptmu": {
#         "": 5.6,
#         "nocut_oldbinning": 7.9,
#         "recoilcut": 6.5,  # good
#         "nocut": 7.0,  # good
#         "lowbins": 7.0,  # good
#     },
#     "EAvailLeadingBlob": {
#         "recoilcut": 6.5,  # good
#         "nocut": 8.1,  # good
#         "lowbins": 4.5,  # good
#     },
# }

# warps_base_path = (
#     "/Users/nova/git/output/October2025/eventloopout/allblobs_fullremoval_1and2track/"
# )

# # if len(sys.argv) == 1:
# #     print("python3 run_TransWarpExtraction.py <dir with subdirs for warps> <TODO: optional base warp, default MnvTunev1>")
# #     print("going with default: ", warps_base_path)
# # else:
# #     warps_base_path = sys.argv[1]

# output_basename = os.path.basename(warps_base_path)
# outdir_base = MakePlotDir(os.path.join("warpingstudies/", output_basename))

# # nowarp_base_path = os.path.join(warps_base_path, "MnvTunev1")
# # mnvtunewarp_base_path = os.path.join(warps_base_path, "MnvTunev2")
# # no2p2hwarp_base_path = os.path.join(warps_base_path, "no2p2htune")

# # nowarpfile = os.path.join(
# #     nowarp_base_path,
# #     "combined_EAvail_recoil_warpingstudies_nonewarp_QElike_minervameCombined_MnvTunev1_AntiNu_v15_warping_grid_1.root",
# # )
# # mnvtunewarpfile = os.path.join(
# #     mnvtunewarp_base_path,
# #     "combined_EAvail_recoil_warpingstudies_nonewarp_QElike_minervameCombined_MnvTunev2_AntiNu_v15_warping_grid_1.root.root",
# # )
# # no2p2hwarpfile = os.path.join(
# #     no2p2hwarp_base_path,
# #     "combined_EAvail_recoil_warpingstudies_no2p2htunewarp_QElike_minervameCombined_MnvTunev1_AntiNu_v15_warping_grid_1.root",
# # )
# # nowarpfile = "/Users/nova/git/output/Summer25Collab/eventloopout/MnvTunev1/scaled_combined_EAvail_recoil_warpingstudies_nonewarp_QElike_minervameCombined_MnvTunev1_AntiNu_v15_warping_grid_1.root"
# # mnvtunewarpfile = "/Users/nova/git/output/Summer25Collab/eventloopout/MnvTunev2/scaled_combined_EAvail_recoil_warpingstudies_nonewarp_QElike_minervameCombined_MnvTunev2_AntiNu_v15_warping_grid_1.root"
# # no2p2hwarpfile = "/Users/nova/git/output/Summer25Collab/eventloopout/no2p2htune/scaled_combined_EAvail_recoil_warpingstudies_no2p2htunewarp_QElike_minervameCombined_MnvTunev1_AntiNu_v15_warping_grid_1.root"
# # outdir = "/Users/nova/git/output/Summer25Collab/transwarp/warps/fullcomb/"


# # warps = {"MnvTunev2": mnvtunewarpfile, "no2p2htune": no2p2hwarpfile,}
# # uncfactors = {"recoil": 6.0, "EAvail": 6., "EAvailNoNonVtxBlobs": 6.5, "ptmu": 7.9,}

# max_chi2 = {
#     "recoil": {
#         # "MnvTunev2": 350,
#         "MnvTunev2": 500,
#         # "no2p2htune": 1500,
#         "no2p2htune": 2000,
#     },
#     "EAvail": {
#         # "MnvTunev2": 350,
#         "MnvTunev2": 350,
#         # "no2p2htune": 1500,
#         "no2p2htune": 2000,
#     },
#     "EAvailNoNonVtxBlobs": {
#         # "MnvTunev2": 350,
#         "MnvTunev2": 350,
#         # "no2p2htune": 1500,
#         "no2p2htune": 2000,
#     },
#     "ptmu": {
#         # "MnvTunev2": 50,
#         "MnvTunev2": 200,
#         # "no2p2htune": 200,
#         "no2p2htune": 300,
#     },
#     "EAvailLeadingBlob": {
#         # "MnvTunev2": 350,
#         "MnvTunev2": 350,
#         # "no2p2htune": 1500,
#         "no2p2htune": 2000,
#     },
# }
# iters_list = [
#     1,
#     2,
#     3,
#     4,
#     5,
#     6,
#     7,
#     8,
#     9,
#     10,
#     11,
#     12,
#     13,
#     14,
#     15,
#     16,
#     17,
#     18,
#     19,
#     20,
#     21,
#     22,
#     23,
#     24,
#     25,
#     # 26,
#     # 27,
#     # 28,
#     # 29,
#     # 30,
#     # 40,
#     # 50,
#     # 60,
#     # 70,
#     # 80,
#     # 90,
#     # 100,
# ]
# iters = str(",".join([str(iter) for iter in iters_list]))
# print(iters)
# num_uni = 3000

# studyname = "_".join(studies)
# variablesname = "_".join(variables)
# samplesname = "_".join(samples)
# tot_data_POT = 1.12197e21
# POTScale = tot_data_POT / 3.72e21
# nopotscale_hist_tag = ""
# if doTransWarpPOTScale:
#     nopotscale_hist_tag = "_noPOTscale"

# output_file_list = []
# for study in studies:
#     outdir = os.path.join(outdir_base,study)
#     if not os.path.exists(os.path.join(warps_base_path,study,"MnvTunev1")):
#         continue
#     nowarp_dir_list = os.listdir(os.path.join(warps_base_path,study,"MnvTunev1"))
#     # print(nowarp_dir_list)
#     print(os.path.join(warps_base_path, study, "MnvTunev1"))
#     nowarp_file_name = ""
#     for file_name in nowarp_dir_list:
#         if "potscaled_combined_" in file_name:
#             # if "potscaled_combined_" in file_name and "totaldata" not in file_name:
#             # if "combined_" in file_name and "potscaled" not in file_name:
#             nowarp_file_name = os.path.join(
#                 warps_base_path, study, "MnvTunev1", file_name
#             )
#             print("looking at file ", nowarp_file_name)
#     if nowarp_file_name == "":
#         print("ERROR: Couldn't find nowarp file in", os.path.join(warps_base_path,study,"MnvTunev1"),"\n\tExiting.....")
#         sys.exit(1)
#     if doTransWarpPOTScale:
#         nowarpfile = ROOT.TFile(nowarp_file_name, "READONLY")

#         h_POT = nowarpfile.Get("Combined_POT_Summary")
#         # POTScale = h_POT.GetBinContent(3) / h_POT.GetBinContent(1)
#         # Full ME data POT, avoids issue of using not the full data set
#         POTScale = tot_data_POT/h_POT.GetBinContent(3)

#         print("Running with -P option set to ", POTScale)

#     # for warp in warps.keys():  # nubar
#     for warp in warps:  # nubar
#         study = ""
#         warp_dir_list = os.listdir(os.path.join(warps_base_path, study, warp))
#         # print(warp_dir_list)
#         # for f in [1, 2, 3, 4, 4.697, 5, 6, 7, 8, 9, 10]: #nu
#         warpfile = ""
#         for file_name in warp_dir_list:
#             # if "totaldatapotscaled_combined_" in file_name:
#             if "potscaled_combined_" in file_name and "totaldata" not in file_name:
#                 # if "combined_" in file_name and "potscaled" not in file_name:
#                 warpfile = os.path.join(
#                     warps_base_path, study, warp, file_name
#                 )
#         print(warpfile)
#         if warpfile == "":
#             print("ERROR: Couldn't find nowarp file in", os.path.join(warps_base_path,study,warp),"\n\tExiting.....")
#             sys.exit(1)
#         if not os.path.exists(os.path.join(outdir, "warps")):
#             os.mkdir(os.path.join(outdir, "warps"))
#         print("here", os.path.join(outdir, "warps"))
#         for var in variables:
#             if study not in uncfactors[var].keys():
#                 study = "nocut"
#                 # continue
#             if not os.path.exists(os.path.join(outdir,"warps",warp)):
#                 os.mkdir(os.path.join(outdir, "warps", warp))
#             print("varloop", os.path.join(outdir, "warps", warp))
#             output_file_name = os.path.join(
#                 outdir,
#                 "warps",
#                 warp,
#                 "TransWarpOut_Warp_%s_MnvTunev1_%s_%s_TransWarpDataPOTScale_%siters_%sunivs.root"
#                 % (samples[study], warp, var, str(iters_list[-1]), str(num_uni)),
#             )
#             if doTransWarpPOTScale:
#                 output_file_name = os.path.join(
#                     outdir,
#                     "warps",
#                     warp,
#                     "TransWarpOut_Warp_%s_MnvTunev1_%s_%s_TransWarpScaleP%s_%siters_%sunivs.root"
#                     % (
#                         samples[study],
#                         warp,
#                         var,
#                         ("%0.2f"%POTScale).replace(".","_"),
#                         str(iters_list[-1]),
#                         str(num_uni),
#                     ),
#                 )
#             if doExcludebin:
#                 print("here")

#                 newtail = "_exbin"+str(excludebin)+".root"
#                 output_file_name = output_file_name.replace(".root", newtail)
#                 print(output_file_name)
#             warpedtag = ""
#             if warp == "no2p2htune":
#                 warpedtag = "_warped"
#             cmd = [
#                 "TransWarpExtraction",
#                 "--output_file",
#                 output_file_name,
#                 "--data_file",
#                 warpfile,
#                 "--data",
#                 "h___%s%s___qelike___%s___reconstructed%s"
#                 % (samples[study], warpedtag, var, nopotscale_hist_tag),
#                 "--data_truth_file",
#                 warpfile,
#                 "--data_truth",
#                 "h___%s%s___qelike___%s___selected_truth%s"
#                 % (samples[study], warpedtag, var, nopotscale_hist_tag),
#                 "--reco_file",
#                 nowarp_file_name,
#                 "--reco",
#                 "h___%s___qelike___%s___reconstructed%s"
#                 % (samples[study], var, nopotscale_hist_tag),
#                 "--truth_file",
#                 nowarp_file_name,
#                 "--truth",
#                 "h___%s___qelike___%s___selected_truth%s"
#                 % (samples[study], var, nopotscale_hist_tag),
#                 "--migration_file",
#                 nowarp_file_name,
#                 "--migration",
#                 "h___%s___qelike___%s___response_migration%s"
#                 % (samples[study], var, nopotscale_hist_tag),
#                 # "h___%s___qelike___%s___response_migration_noPOTscale"
#                 # % (samples[study], var),
#                 "--num_iter",
#                 iters,
#                 "--num_uni",
#                 str(num_uni),
#                 "--max_chi2",
#                 str(max_chi2[var][warp]),
#                 "--step_chi2",
#                 "1",
#                 "--corr_factor",
#                 str(uncfactors[var][study]),
#                 # "--exclude_bins",
#                 # "4,5"
#                 # "-P",
#                 # str(POTScale),
#             ]
#             if doTransWarpPOTScale:
#                 print("Really running with -P option set to ", POTScale)
#                 cmd.append("-P")
#                 cmd.append(str(POTScale))
#             if doExcludebin:
#                 print("WARNING: excluding bin ", excludebin)
#                 cmd.append("-x")
#                 cmd.append(str(excludebin))
#             print(" ".join(cmd))
#             subprocess.run(cmd)
#             output_file_list.append(output_file_name)
#             print("here")


# # print("TransWarpOutputs written to")
# # for file in output_file_list:
# #     print(file)

# # print(os.path.join(os.getcwd(), "nhv/warping/runtranswarp_EAvail_warps.sh"))
# # # os.chdir(str(os.getenv("NUKECC_ANA")) + "/unfolding")
# # print("I'm in %s" % os.getcwd())
# # print(" All done!!")
