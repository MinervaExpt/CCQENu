#export _CONDOR_SCRATCH_DIR=$PWD
#export INPUT_TAR_DIR_LOCAL=$APP

# example test batch job to run on minervagpvm01 to run CCQEMAT
# other option (not tested yet) is the EventLoop from the tutorial

# type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# here my release is in $APP/NEWMAT - your mileage may differ

# ==========

# QElike
export MYSAMPLE=QElike
export MYWARP=none
export MYMODEL=MnvTunev2.0.1
# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/July2026/xsec/DPF26/newfitting_p8_multipion_100flux/${MYMODEL}/datareco/ \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_xsec_xtract_multipion_reco \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_npi --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=36h --memory=6000   --sample=${MYSAMPLE} #--debug --notimestamp

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/JunJuly2026e2026/xsec/DPF26/newfitting_p8_multipion_100flux/${MYMODEL}/truth/ \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_xsec_xtract_multipion_truth \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_truth_npi --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=36h --memory=4000   --sample=${MYSAMPLE} #--debug --notimestamp

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/July2026/xsec/removal_noqeband_100flux/${MYMODEL}/datareco/ \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_xsec_xtract_nonpi_reco \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=36h --memory=6000   --sample=${MYSAMPLE} #--debug --notimestamp

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/July2026/xsec/removal_noqeband_100flux/${MYMODEL}/truth/ \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_xsec_xtract_nonpi_truth \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_truth --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=36h --memory=4000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYMODEL=MnvTunev4.3.1
# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/July2026/xsec/DPF26/newfitting_p8_multipion_100flux/${MYMODEL}/datareco/ \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_xsec_xtract_multipion_reco \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_npi --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=36h --memory=6000   --sample=${MYSAMPLE} #--debug --notimestamp

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/July2026/xsec/DPF26/newfitting_p8_multipion_100flux/${MYMODEL}/truth/ \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_xsec_xtract_multipion_truth \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_truth_npi --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=36h --memory=4000   --sample=${MYSAMPLE} #--debug --notimestamp

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/July2026/xsec/removal_noqeband_100flux/${MYMODEL}/datareco/ \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_xsec_xtract_nonpi_reco \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=36h --memory=6000   --sample=${MYSAMPLE} #--debug --notimestamp

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/July2026/xsec/removal_noqeband_100flux/${MYMODEL}/truth/ \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_xsec_xtract_nonpi_truth \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_truth --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=36h --memory=4000   --sample=${MYSAMPLE} #--debug --notimestamp

