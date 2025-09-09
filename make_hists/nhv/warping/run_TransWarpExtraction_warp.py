import os
import sys
import subprocess
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
excludebin = 1
# ----------------------------
# Running TransWarpExtraction
# ----------------------------


def MakePlotDir(subdir=""):
    """
    Subdir is the one for all plots that this script should ouptut. You will need to add
    any other subdirs in the script itself (e.g. based off input file name)
    """
    plotdir = ""
    base_plotdir = os.environ.get("OUTPUTLOC")
    if base_plotdir != None:
        plotdir = os.path.join(base_plotdir, month + year)
    else:
        plotdir = os.path.join("/Users/nova/git/output/", month + year)
    if not os.path.exists(plotdir):
        print("Can't find plot dir. Making it now... ", plotdir)
        os.mkdir(plotdir)
    if subdir == "":
        return plotdir
    if not os.path.exists(os.path.join(plotdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(plotdir, subdir))
        os.mkdir(os.path.join(plotdir, subdir))
    return os.path.join(plotdir, subdir)


studies = [""
    # "nocut_oldbinning",
    # "recoilcut",
    # "nocut",
    # "lowbins",
]

samples = {
    "nocut_oldbinning": "QElike",
    "recoilcut": "QElike_maxrecoil",
    "nocut": "QElike",
    "lowbins": "QElike",
}

variables = [
    "recoil",
    "EAvail",
    # "EAvailNoNonVtxBlobs",
    "ptmu",
    # "EAvailLeadingBlob",
]

warps = [
    "MnvTunev2",
    "no2p2htune"
]

uncfactors = {
    "recoil": {
        "nocut_oldbinning": 6.0,
        "recoilcut": 7.9,  # good
        "nocut": 4.9,  # good
        "lowbins": 7.2,  # good
    },
    "EAvail": {
        "nocut_oldbinning": 6.0,
        "recoilcut": 8.2,  # good
        "nocut": 6.0,  # good
        "lowbins": 9.0,  # good
    },
    "EAvailNoNonVtxBlobs": {
        "nocut_oldbinning": 6.5,
        "recoilcut": 9.0,  # good
        "nocut": 6.5,  # good
        "lowbins": 6.8,  # good
    },
    "ptmu": {
        "nocut_oldbinning": 7.9,
        "recoilcut": 6.5,  # good
        "nocut": 7.0,  # good
        "lowbins": 7.0,  # good
    },
    "EAvailLeadingBlob": {
        "recoilcut": 6.5,  # good
        "nocut": 8.1,  # good
        "lowbins": 4.5,  # good
    },
}


warps_base_path = "/Users/nova/git/output/September2025/eventloopout/warpingstudies/fullfiducial_protontracks"
outdir_base = "/Users/nova/git/output/Summer25Collab/transwarp/recoilstudy_newbinning"
outdir_base = MakePlotDir("warpingstudies/fullfiducial_protontracks")

# nowarp_base_path = os.path.join(warps_base_path, "MnvTunev1")
# mnvtunewarp_base_path = os.path.join(warps_base_path, "MnvTunev2")
# no2p2hwarp_base_path = os.path.join(warps_base_path, "no2p2htune")

# nowarpfile = os.path.join(
#     nowarp_base_path,
#     "combined_EAvail_recoil_warpingstudies_nonewarp_QElike_minervameCombined_MnvTunev1_AntiNu_v15_warping_grid_1.root",
# )
# mnvtunewarpfile = os.path.join(
#     mnvtunewarp_base_path,
#     "combined_EAvail_recoil_warpingstudies_nonewarp_QElike_minervameCombined_MnvTunev2_AntiNu_v15_warping_grid_1.root.root",
# )
# no2p2hwarpfile = os.path.join(
#     no2p2hwarp_base_path,
#     "combined_EAvail_recoil_warpingstudies_no2p2htunewarp_QElike_minervameCombined_MnvTunev1_AntiNu_v15_warping_grid_1.root",
# )
# nowarpfile = "/Users/nova/git/output/Summer25Collab/eventloopout/MnvTunev1/scaled_combined_EAvail_recoil_warpingstudies_nonewarp_QElike_minervameCombined_MnvTunev1_AntiNu_v15_warping_grid_1.root"
# mnvtunewarpfile = "/Users/nova/git/output/Summer25Collab/eventloopout/MnvTunev2/scaled_combined_EAvail_recoil_warpingstudies_nonewarp_QElike_minervameCombined_MnvTunev2_AntiNu_v15_warping_grid_1.root"
# no2p2hwarpfile = "/Users/nova/git/output/Summer25Collab/eventloopout/no2p2htune/scaled_combined_EAvail_recoil_warpingstudies_no2p2htunewarp_QElike_minervameCombined_MnvTunev1_AntiNu_v15_warping_grid_1.root"
# outdir = "/Users/nova/git/output/Summer25Collab/transwarp/warps/fullcomb/"


# warps = {"MnvTunev2": mnvtunewarpfile, "no2p2htune": no2p2hwarpfile,}
# uncfactors = {"recoil": 6.0, "EAvail": 6., "EAvailNoNonVtxBlobs": 6.5, "ptmu": 7.9,}

max_chi2 = {
    "recoil": {
        # "MnvTunev2": 350,
        "MnvTunev2": 500,
        # "no2p2htune": 1500,
        "no2p2htune": 2000,
    },
    "EAvail": {
        # "MnvTunev2": 350,
        "MnvTunev2": 350,
        # "no2p2htune": 1500,
        "no2p2htune": 2000,
    },
    "EAvailNoNonVtxBlobs": {
        # "MnvTunev2": 350,
        "MnvTunev2": 350,
        # "no2p2htune": 1500,
        "no2p2htune": 2000,
    },
    "ptmu": {
        # "MnvTunev2": 50,
        "MnvTunev2": 200,
        # "no2p2htune": 200,
        "no2p2htune": 300,
    },
    "EAvailLeadingBlob": {
        # "MnvTunev2": 350,
        "MnvTunev2": 350,
        # "no2p2htune": 1500,
        "no2p2htune": 2000,
    },
}
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
    26,
    27,
    28,
    29,
    30,
    40,
    50,
    # 60,
    # 70,
    # 80,
    # 90,
    # 100,
]
iters = str(",".join([str(iter) for iter in iters_list]))
print(iters)
num_uni = 3000

studyname = "_".join(studies)
variablesname = "_".join(variables)
samplesname = "_".join(samples)
tot_data_POT = 1.12197e21
POTScale = tot_data_POT / 3.72e21
nopotscale_hist_tag = ""
if doTransWarpPOTScale:
    nopotscale_hist_tag = "_noPOTscale"

output_file_list = []
for study in studies:
    outdir = os.path.join(outdir_base,study)
    if not os.path.exists(os.path.join(warps_base_path,study,"MnvTunev1")):
        continue
    nowarp_dir_list = os.listdir(os.path.join(warps_base_path,study,"MnvTunev1"))
    # print(nowarp_dir_list)
    print(os.path.join(warps_base_path, study, "MnvTunev1"))
    nowarp_file_name = ""
    for file_name in nowarp_dir_list:
        if "potscaled_combined_" in file_name:
            # if "potscaled_combined_" in file_name and "totaldata" not in file_name:
            # if "combined_" in file_name and "potscaled" not in file_name:
            nowarp_file_name = os.path.join(
                warps_base_path, study, "MnvTunev1", file_name
            )
            print("looking at file ", nowarp_file_name)
    if nowarp_file_name == "":
        print("ERROR: Couldn't find nowarp file in", os.path.join(warps_base_path,study,"MnvTunev1"),"\n\tExiting.....")
        sys.exit(1)
    if doTransWarpPOTScale:
        nowarpfile = ROOT.TFile(nowarp_file_name, "READONLY")

        h_POT = nowarpfile.Get("Combined_POT_Summary")
        # POTScale = h_POT.GetBinContent(3) / h_POT.GetBinContent(1)
        # Full ME data POT, avoids issue of using not the full data set
        POTScale = tot_data_POT/h_POT.GetBinContent(3)

        print("Running with -P option set to ", POTScale)

    # for warp in warps.keys():  # nubar
    for warp in warps:  # nubar
        study = ""
        warp_dir_list = os.listdir(os.path.join(warps_base_path, study, warp))
        # print(warp_dir_list)
        # for f in [1, 2, 3, 4, 4.697, 5, 6, 7, 8, 9, 10]: #nu
        warpfile = ""
        for file_name in warp_dir_list:
            # if "totaldatapotscaled_combined_" in file_name:
            if "potscaled_combined_" in file_name and "totaldata" not in file_name:
                # if "combined_" in file_name and "potscaled" not in file_name:
                warpfile = os.path.join(
                    warps_base_path, study, warp, file_name
                )
        print(warpfile)
        if warpfile == "":
            print("ERROR: Couldn't find nowarp file in", os.path.join(warps_base_path,study,warp),"\n\tExiting.....")
            sys.exit(1)
        if not os.path.exists(os.path.join(outdir, "warps")):
            os.mkdir(os.path.join(outdir, "warps"))
        print("here", os.path.join(outdir, "warps"))
        for var in variables:
            if study not in uncfactors[var].keys():
                study = "nocut"
                # continue
            if not os.path.exists(os.path.join(outdir,"warps",warp)):
                os.mkdir(os.path.join(outdir, "warps", warp))
            print("varloop", os.path.join(outdir, "warps", warp))
            output_file_name = os.path.join(
                outdir,
                "warps",
                warp,
                "TransWarpOut_Warp_%s_MnvTunev1_%s_%s_TransWarpDataPOTScale_%siters_%sunivs.root"
                % (samples[study], warp, var, str(iters_list[-1]), str(num_uni)),
            )
            if doTransWarpPOTScale:
                output_file_name = os.path.join(
                    outdir,
                    "warps",
                    warp,
                    "TransWarpOut_Warp_%s_MnvTunev1_%s_%s_TransWarpScaleP%s_%siters_%sunivs.root"
                    % (
                        samples[study],
                        warp,
                        var,
                        ("%0.2f"%POTScale).replace(".","_"),
                        str(iters_list[-1]),
                        str(num_uni),
                    ),
                )
            if doExcludebin:
                print("here")

                newtail = "_exbin"+str(excludebin)+".root"
                output_file_name = output_file_name.replace(".root", newtail)
                print(output_file_name)
            warpedtag = ""
            if warp == "no2p2htune":
                warpedtag = "_warped"
            cmd = [
                "TransWarpExtraction",
                "--output_file",
                output_file_name,
                "--data_file",
                warpfile,
                "--data",
                "h___%s%s___qelike___%s___reconstructed%s"
                % (samples[study], warpedtag, var, nopotscale_hist_tag),
                "--data_truth_file",
                warpfile,
                "--data_truth",
                "h___%s%s___qelike___%s___selected_truth%s"
                % (samples[study], warpedtag, var, nopotscale_hist_tag),
                "--reco_file",
                nowarp_file_name,
                "--reco",
                "h___%s___qelike___%s___reconstructed%s"
                % (samples[study], var, nopotscale_hist_tag),
                "--truth_file",
                nowarp_file_name,
                "--truth",
                "h___%s___qelike___%s___selected_truth%s"
                % (samples[study], var, nopotscale_hist_tag),
                "--migration_file",
                nowarp_file_name,
                "--migration",
                "h___%s___qelike___%s___response_migration%s"
                % (samples[study], var, nopotscale_hist_tag),
                "--num_iter",
                iters,
                "--num_uni",
                str(num_uni),
                "--max_chi2",
                str(max_chi2[var][warp]),
                "--step_chi2",
                "1",
                "--corr_factor",
                str(uncfactors[var][study]),
                # "-P",
                # str(POTScale),
            ]
            if doTransWarpPOTScale:
                print("Really running with -P option set to ", POTScale)
                cmd.append("-P")
                cmd.append(str(POTScale))
            if doExcludebin:
                print("WARNING: excluding bin ", excludebin)
                cmd.append("-x")
                cmd.append(str(excludebin))
            print(" ".join(cmd))
            subprocess.run(cmd)
            output_file_list.append(output_file_name)
            print("here")


print("TransWarpOutputs written to")
for file in output_file_list:
    print(file)

print(os.path.join(os.getcwd(), "nhv/warping/runtranswarp_EAvail_warps.sh"))
# os.chdir(str(os.getenv("NUKECC_ANA")) + "/unfolding")
print("I'm in %s" % os.getcwd())
print(" All done!!")
