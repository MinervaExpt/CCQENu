import os
import sys
import subprocess

# How to run. Closure test, MnvTune v2
# python run_TransWarpExtraction_f.py
# nohup python run_TransWarpExtraction_f.py >& Tela_run_TransWarpExtraction_f.txt &

# ----------------------------
# Running TransWarpExtraction
# ----------------------------

warps_base_path = (
    "/Users/nova/git/output/Summer25Collab/eventloopout/recoilstudy_newbinning"
)
outdir_base = "/Users/nova/git/output/Summer25Collab/transwarp/recoilstudy_newbinning"

studies = [
    "recoilcut",
    "nocut",
    "lowbins",
]

samples = {
    "recoilcut": "QElike_maxrecoil",
    "nocut": "QElike",
    "lowbins": "QElike",
}

variables = [
    "recoil",
    "EAvail",
    "EAvailNoNonVtxBlobs",
    "ptmu",
    "EAvailLeadingBlob",
]

num_iter = "1,2,3,4,5,6,7,8,9,10,20,50,100"

studyname = "_".join(studies)
variablesname = "_".join(variables)
samplesname = "_".join(samples)
# exefilename = os.path.join(
#     os.environ.get("CCQEMAT"),
#     "nhv/warping/runtranswarp_%s_%s_%s_closure.sh" % (samplesname,studyname,variablesname),
# )

# print("overwriting file", exefilename)
# exefile = open(exefilename, "w")

# nowarpfile = "/Users/nova/git/output/Summer25Collab/eventloopout/MnvTunev1/scaled_combined_EAvail_recoil_warpingstudies_nonewarp_QElike_minervameCombined_MnvTunev1_AntiNu_v15_warping_grid_1.root"

output_file_list = []
for study in studies:
    outdir = os.path.join(outdir_base,study)

    nowarp_dir_list = os.listdir(os.path.join(warps_base_path,study,"MnvTunev1"))
    nowarpfile = ""
    for file_name in nowarp_dir_list:
        if "totaldatapotscaled_combined_" in file_name:
            nowarpfile = os.path.join(warps_base_path,study,"MnvTunev1",file_name)
    if nowarpfile == "":
        print("ERROR: Couldn't find nowarp file in", os.path.join(warps_base_path,study,"MnvTunev1"),"\n\tExiting.....")
        sys.exit(1)
    for var in variables:
        output_file_name = os.path.join(
            outdir,
            "TransWarpOut_Closure_%s_%s_MnvTunev1_%s.root"
            % (var,samples[study], study),
        )
        # input_file_name = "/minerva/data/users/%s/NukeHists/%s/%s/Hists_TransWarpInput_SISQ2CutAnalysis_MnvTunev2_t54_z82_%s_%s.root" % (os.getenv("USER"), os.getenv("NUKECC_TAG"), playlist, label, os.getenv("NUKECC_TAG"))
        # output_file_name = "/minerva/data/users/%s/NukeHists/%s/%s/TransWarpOutput/Hists_TransWarpOutput_SISQ2CutAnalysis_MnvTunev2_%s_f%0.3f_t54_z82_%s_%s.root" % (os.getenv("USER"), os.getenv("NUKECC_TAG"), playlist, var, f, label, os.getenv("NUKECC_TAG"))

        cmd = [
            "TransWarpExtraction",
            "--output_file",
            output_file_name,
            "--data_file",
            nowarpfile,
            "--data",
            "h___%s___qelike___%s___reconstructed" % (samples[study], var),
            "--data_truth_file",
            nowarpfile,
            "--data_truth",
            "h___%s___qelike___%s___selected_truth" % (samples[study], var),
            "--reco_file",
            nowarpfile,
            "--reco",
            "h___%s___qelike___%s___reconstructed" % (samples[study], var),
            "--truth_file",
            nowarpfile,
            "--truth",
            "h___%s___qelike___%s___selected_truth" % (samples[study], var),
            "--migration_file",
            nowarpfile,
            "--migration",
            "h___%s___qelike___%s___response_migration" % (samples[study], var),
            "--num_iter",
            num_iter,
            "--num_uni",
            "500",
            "--max_chi2",
            "50",
            "--step_chi2",
            "1",
            # " --stat_scale "
            # str(format(f, ".3f"))
        ]
        subprocess.run(cmd)

        output_file_list.append(output_file_name)

print("TransWarpOutputs written to")
for file in output_file_list:
    print(file)

# os.chdir(str(os.getenv("NUKECC_ANA")) + "/unfolding")
print("I'm in %s" % os.getcwd())
print(" All done!!")
