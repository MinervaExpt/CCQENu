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
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/warpingtest/eventloopout/September2025/fullfiducial_protontracks_pscore_03_allcands_all12MeV/MnvTunev1 \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYWARP}_neutronblob_warpingstudy \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=no2p2htune
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/warpingtest/eventloopout/September2025/fullfiducial_protontracks_pscore_03_allcands_all12MeV/no2p2htune \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYWARP}_neutronblob_warpingstudy \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=none
export MYMODEL=MnvTunev2

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/warpingtest/eventloopout/September2025/fullfiducial_protontracks_pscore_03_allcands_all12MeV/MnvTunev2 \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYWARP}_neutronblob_warpingstudy \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
