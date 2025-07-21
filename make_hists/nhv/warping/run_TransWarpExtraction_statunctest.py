import os
import sys
import ROOT 
import subprocess 
from PlotUtils import MnvH1D, MnvH2D
# How to run. Closure test, MnvTune v2
# python run_TransWarpExtraction_f.py
# nohup python run_TransWarpExtraction_f.py >& Tela_run_TransWarpExtraction_f.txt &

# ----------------------------
# Running TransWarpExtraction
# ----------------------------

# scaled_tag = "_noPOTscale"
scaled_tag = ""
warps_base_path = (
    "/Users/nova/git/output/Summer25Collab/eventloopout/recoilstudy_newbinning"
)
outdir_base = "/Users/nova/git/output/Summer25Collab/transwarp/recoilstudy_newbinning"

studies = ["recoilcut", "nocut", "lowbins"]

samples = {"recoilcut": "QElike_maxrecoil", "nocut": "QElike", "lowbins": "QElike"}

variables = ["recoil", "EAvail", "EAvailNoNonVtxBlobs", "ptmu", "EAvailLeadingBlob"]

num_iter = "1,2,3,4,5,6,7,8,9,10,20,50,100"
num_uni = 500
max_chi2 = 200

studyname = "_".join(studies)
variablesname = "_".join(variables)
samplesname = "_".join(samples)
exefilename = os.path.join(
    os.environ.get("CCQEMAT"),
    "nhv/warping/runtranswarp_%s_%s_%s_statunctest.sh"
    % (samplesname, studyname, variablesname),
)

print("overwriting file", exefilename)
exefile = open(exefilename, "w")

output_file_list = []
for study in studies:
    outdir = os.path.join(outdir_base,study,"stattest")

    nowarp_dir_list = os.listdir(os.path.join(warps_base_path,study,"MnvTunev1"))
    nowarpfile_name = ""
    for file_name in nowarp_dir_list:
        # if "combined_" in file_name and "potscaled_" not in file_name:
        if "totaldatapotscaled_combined_" in file_name:
            nowarpfile_name = os.path.join(
                warps_base_path, study, "MnvTunev1", file_name
            )
            print("Looking at file",nowarpfile_name)
    if nowarpfile_name == "":
        print("ERROR: Couldn't find nowarp file in", os.path.join(warps_base_path,study,"MnvTunev1"),"\n\tExiting.....")
        sys.exit(1)

    # nowarpfile = ROOT.TFile(nowarpfile_name,"READONLY")

    # h_POT = nowarpfile.Get("Combined_POT_Summary")
    # # pot_factor = h_POT.GetBinContent(3) / h_POT.GetBinContent(1)
    # # Full ME data POT, avoids issue of using not the full data set
    # mctodata_pot_factor = h_POT.GetBinContent(3) / 1.2e21

    # factors = []
    # for i in range(1,11):
    #     if i - mctodata_pot_factor > 0 and i - mctodata_pot_factor < 1:
    #         factors.append(mctodata_pot_factor)
    #     factors.append(i)
    factors = [1, 2, 3, 4, 4.437, 5, 6, 7, 8, 9, 10]
    print(factors)
    for var in variables:

        for f in factors:  # nubar
            # for f in [1, 2, 3, 4, 4.437, 5, 6, 7, 8, 9, 10]:  # nubar
            # for f in [1, 2, 3, 4, 4.697, 5, 6, 7, 8, 9, 10]: #nu
            output_file_basename = (
                "TransWarpOut_StatUncTest_%s_%s_MnvTunev1_%s_f%0.3f.root"
                % (var, samples[study], study, f)
            )
            output_file_name = os.path.join(outdir, output_file_basename)
            # input_file_name = "/minerva/data/users/%s/NukeHists/%s/%s/Hists_TransWarpInput_SISQ2CutAnalysis_MnvTunev2_t54_z82_%s_%s.root" % (os.getenv("USER"), os.getenv("NUKECC_TAG"), playlist, label, os.getenv("NUKECC_TAG"))
            # output_file_name = "/minerva/data/users/%s/NukeHists/%s/%s/TransWarpOutput/Hists_TransWarpOutput_SISQ2CutAnalysis_MnvTunev2_%s_f%0.3f_t54_z82_%s_%s.root" % (os.getenv("USER"), os.getenv("NUKECC_TAG"), playlist, var, f, label, os.getenv("NUKECC_TAG"))

            cmd = [
                "TransWarpExtraction",
                "--output_file",
                output_file_name,
                "--data_file",
                nowarpfile_name,
                "--data",
                "h___%s___qelike___%s___reconstructed%s"
                % (samples[study], var, scaled_tag),
                "--data_truth_file",
                nowarpfile_name,
                "--data_truth",
                "h___%s___qelike___%s___selected_truth%s"
                % (samples[study], var, scaled_tag),
                "--reco_file",
                nowarpfile_name,
                "--reco",
                "h___%s___qelike___%s___reconstructed%s"
                % (samples[study], var, scaled_tag),
                "--truth_file",
                nowarpfile_name,
                "--truth",
                "h___%s___qelike___%s___selected_truth%s"
                % (samples[study], var, scaled_tag),
                "--migration_file",
                nowarpfile_name,
                "--migration",
                "h___%s___qelike___%s___response_migration%s"
                % (samples[study], var, scaled_tag),
                "--num_iter",
                "1,2,3,4,5,6,7,8,9,10,20,50,100 ",
                "--num_uni",
                "500",
                "--max_chi2",
                "200",
                "--step_chi2",
                "1",
                "--stat_scale",
                str(format(f, ".3f")),
                # "--data_pot_norm",
                # str(format(1 / mctodata_pot_factor, ".4f")),
            ]
            # for arg in cmd:
            print(" ".join(cmd))
            subprocess.run(cmd)
            # cmd = (
            #     "TransWarpExtraction"
            #     + " --output_file "
            #     + output_file_name
            #     + " --data_file "
            #     + nowarpfile_name
            #     + " --data "
            #     + "h___%s___qelike___%s___reconstructed" % (samples[study], var)
            #     + " --data_truth_file "
            #     + nowarpfile_name
            #     + " --data_truth "
            #     + "h___%s___qelike___%s___selected_truth" % (samples[study], var)
            #     + " --reco_file "
            #     + nowarpfile_name
            #     + " --reco "
            #     + "h___%s___qelike___%s___reconstructed" % (samples[study], var)
            #     + " --truth_file "
            #     + nowarpfile_name
            #     + " --truth "
            #     + "h___%s___qelike___%s___selected_truth" % (samples[study], var)
            #     + " --migration_file "
            #     + nowarpfile_name
            #     + " --migration "
            #     + "h___%s___qelike___%s___response_migration" % (samples[study], var)
            #     + " --num_iter "
            #     + "1,2,3,4,5,6,7,8,9,10,20,50,100 "
            #     + " --num_uni "
            #     + "500"
            #     + " --max_chi2 "
            #     + "200"
            #     + " --step_chi2 "
            #     + "1"
            #     + " --stat_scale "
            #     + str(format(f, ".3f"))
            # )
            # print(cmd)
            # with open(exefilename, "a") as file:
            #     file.write(cmd + "\n")
            # print("transwarp output will be written to", output_file_name)
            output_file_list.append(output_file_name)

# exitcmd = 'echo "TransWarpOutputs written to" \n'
# for file in output_file_list:
#     exitcmd += 'echo "' + file + '"' + "\n"
# # exitcmd += '"\n'
# with open(exefilename, "a") as file:
#     file.write(exitcmd)
# os.system(
#     "source "
#     + os.path.join(
#         os.environ.get("CCQEMAT"), "nhv/warping/runtranswarp_EAvail_statunctest.sh"
#     )
# )
# ----------------------------

# print("running the script ",exefilename)
# subprocess.run(["zsh", exefilename])

# os.chdir(str(os.getenv("NUKECC_ANA")) + "/unfolding")
print("I'm in %s" % os.getcwd())
print(" All done!!")
