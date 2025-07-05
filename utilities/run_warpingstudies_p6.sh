#export _CONDOR_SCRATCH_DIR=$PWD
#export INPUT_TAR_DIR_LOCAL=$APP

# example test batch job to run on minervagpvm01 to run CCQEMAT
# other option (not tested yet) is the EventLoop from the tutorial

# type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# here my release is in $APP/NEWMAT - your mileage may differ
export MYWARP=none
export MYSAMPLE=QElike
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/ \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --tag=EAvailWarpFill \
 --mail --prescale=1 --config=nhv/config/warping/AntiNu_v15_warping_grid --exe=sidebands_v2 --sample=${MYSAMPLE} --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   #--debug --notimestamp

export MYWARP=no2p2htune
export MYSAMPLE=QElike
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/ \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --tag=EAvailWarpFill \
 --mail --prescale=1 --config=nhv/config/warping/AntiNu_v15_warping_grid --exe=sidebands_v2 --sample=${MYSAMPLE} --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   #--debug --notimestamp

export MYWARP=none
export MYSAMPLE=QElike
export MYMODEL=MnvTunev2

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/ \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --tag=EAvailWarpFill \
 --mail --prescale=1 --config=nhv/config/warping/AntiNu_v15_warping_grid --exe=sidebands_v2 --sample=${MYSAMPLE} --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   #--debug --notimestamp
