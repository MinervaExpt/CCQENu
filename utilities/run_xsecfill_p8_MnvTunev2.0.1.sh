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

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/June2026/xsec/newfitting_p8/${MYMODEL}/no_multipion/truth/ \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_xsec_xtract \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_truth --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=36h --memory=6000   --sample=${MYSAMPLE} #--debug --notimestamp

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/June2026/xsec/newfitting_p8/${MYMODEL}/no_multipion/truth_multipion/ \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_xsec_xtract \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_truth_npi --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=36h --memory=6000   --sample=${MYSAMPLE} #--debug --notimestamp

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/June2026/xsec/newfitting_p8/${MYMODEL}/no_multipion/datareco/ \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_xsec_xtract \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=36h --memory=6000   --sample=${MYSAMPLE} #--debug --notimestamp

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/June2026/xsec/newfitting_p8/${MYMODEL}/no_multipion/datareco_multipion/ \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_xsec_xtract \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_npi --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=36h --memory=6000   --sample=${MYSAMPLE} #--debug --notimestamp
