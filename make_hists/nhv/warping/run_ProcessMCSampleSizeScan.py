import os
import sys
import subprocess

# How to run. Closure test, MnvTune v2
# python run_TransWarpExtraction_f.py
# nohup python run_TransWarpExtraction_f.py >& Tela_run_TransWarpExtraction_f.txt &

# ----------------------------
# Running TransWarpExtraction
# ----------------------------

# warps_base_path = "/Users/nova/git/output/Summer25Collab/eventloopout/recoilstudy_newbinning"
# nowarpfile = "/Users/nova/git/output/Summer25Collab/eventloopout/MnvTunev1/scaled_combined_EAvail_recoil_warpingstudies_nonewarp_QElike_minervameCombined_MnvTunev1_AntiNu_v15_warping_grid_1.root"

# outdir = "/Users/nova/git/output/Summer25Collab/transwarp/stattest"

outdir_base = "/Users/nova/git/output/Summer25Collab/transwarp/recoilstudy_newbinning/"


# variables = ["recoil", "EAvail", "EAvailNoNonVtxBlobs", "ptmu"]
# variables = ["ptmu"]

studies = [
    "recoilcut",
    # "nocut",
    # "lowbins",
]

samples = {
    "recoilcut": "QElike_maxrecoil",
    "nocut": "QElike",
    "lowbins": "QElike",
}

variables = [
    "recoil",
    # "EAvail",
    # "EAvailNoNonVtxBlobs",
    # "ptmu",
    "EAvailLeadingBlob",
]

bins = {
    "recoil": 5,
    "EAvail": 5,
    "EAvailNoNonVtxBlobs": 5,
    "ptmu": 13,
    "EAvailLeadingBlob": 5,
}
# Needs to match what went in in run_TransWarpExtraction_statunctest.py
n_uni = 500
iters = "1,2,3,4,5,6,7,8,9,10,20,50,100"


# F = 7.9
path_to_exe = os.path.join(os.environ.get("CCQEMAT"),"nhv/warping/ProcessMCSampleSizeScan.py")
cwd = os.getcwd()
f_list = [1, 2, 3, 4, 4.437, 5, 6, 7, 8, 9, 10]
uncfactors = {
    "recoil": {
        "recoilcut": 7.9, #good
        "nocut": 4.9, #good
        "lowbins": 7.2, #good
    },
    "EAvail": {
        "recoilcut": 8.2, #good
        "nocut": 6.0, #good
        "lowbins": 9.0, #good
    },
    "EAvailNoNonVtxBlobs": {
        "recoilcut": 9.0, #good
        "nocut": 6.5, #good
        "lowbins": 6.8, #good
    },
    "ptmu": {
        "recoilcut": 6.5, #good
        "nocut": 7.0, #good
        "lowbins": 7.0, #good
    },
    "EAvailLeadingBlob": {
        "recoilcut": 6.5, #good
        "nocut": 8.1, #good
        "lowbins": 4.5, #good
    },
}

for study in studies:
    outdir = os.path.join(outdir_base,study,"stattest")
    os.chdir(outdir)
    if not os.path.exists(os.path.join(outdir, "mcscan")):
        os.mkdir(os.path.join(outdir, "mcscan"))
    os.chdir(os.path.join(outdir,"mcscan"))

    for var in variables:
        F = uncfactors[var][study]
        for f in f_list:  # nubar
            # for f in [1, 2, 3, 4, 4.697, 5, 6, 7, 8, 9, 10]: #nu

            twe_file_name = os.path.join(
                outdir,
                "TransWarpOut_StatUncTest_%s_%s_MnvTunev1_%s_f%0.3f.root"
                % (var, samples[study], study, f),
            )
            print("Running on file ",twe_file_name)
            cmd = [
                "python3",
                path_to_exe,
                "--input",
                twe_file_name,
                "--n_uni",
                str(n_uni),
                "--iters",
                iters,
                "--uncfactor",
                str(F),
                "--f_option_used_transwarp",
                str(format(f, ".3f")),
            ]
            subprocess.run(cmd)
        # ----------------------------
        nbins = bins[var]
        if study=="nocut" and var!="ptmu":
            nbins+=1
        newcmd_list = [
            "python3",
            os.path.join(
                os.environ.get("CCQEMAT"), "nhv/warping/PlotMCSampleSizeScan.py"
            ),
            var,
            str(nbins),
            str(F),
        ]
        for f in f_list:
            twe_file_base_name = (
                "TransWarpOut_StatUncTest_%s_%s_MnvTunev1_%s_f%0.3f.root"
                % (var, samples[study], study, f)
            )
            infilename = os.path.join(
                outdir,
                "mcscan",
                twe_file_base_name + "_%f_%f.txt" % (float(F), float(f)),
            )
            newcmd_list.append(infilename)


        subprocess.run(newcmd_list)

        print("Done with var ",var)


# os.chdir(str(os.getenv("NUKECC_ANA")) + "/unfolding")
print("Output written to %s" % os.getcwd())

os.chdir(cwd)

print(" All done!!")
