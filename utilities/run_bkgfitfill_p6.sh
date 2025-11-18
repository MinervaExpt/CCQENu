#export _CONDOR_SCRATCH_DIR=$PWD
#export INPUT_TAR_DIR_LOCAL=$APP

# example test batch job to run on minervagpvm01 to run CCQEMAT
# other option (not tested yet) is the EventLoop from the tutorial

# type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# here my release is in $APP/NEWMAT - your mileage may differ

# ==========

# QElike
# export MYSAMPLE=QElike
export MYWARP=none
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/bkgfitting/eventloopout/November2025/fitfill_bkgfit_newprotonscore_recoil0mm_fullsyst \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=bkgfitting_recoil0mm \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_bkgsub --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=36h --memory=5000   #--sample=${MYSAMPLE} #--debug --notimestamp