#export _CONDOR_SCRATCH_DIR=$PWD
#export INPUT_TAR_DIR_LOCAL=$APP

# example test batch job to run on minervagpvm01 to run CCQEMAT
# other option (not tested yet) is the EventLoop from the tutorial

# type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# here my release is in $APP/NEWMAT - your mileage may differ

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer24Collab \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=MnvTunev1 --tag=AL9 \
 --mail --prescale=1 --config=nhv/config/Summer24Collab/AntiNu_v15_SBStudy_grid --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=24h --memory=4000   #--debug --notimestamp
