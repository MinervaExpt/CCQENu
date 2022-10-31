#export _CONDOR_SCRATCH_DIR=$PWD
#export INPUT_TAR_DIR_LOCAL=$APP

# example test batch job to run on minervagpvm01 to run CCQEMAT
# other option (not tested yet) is the EventLoop from the tutorial

# type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# here my release is in $APP/NEWMAT - your mileage may differ

python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test --basedir=$APP/NEWMAT --rundir=CCQENu/make_hists --playlist=minervame5A --model=MnvTunev1 --tag=ccqe --mail --prescale=1 --config=hms/test_batch --exe=sidebands_v2 --sample=QElike --setup=CCQENu/utilities/setup_batch_mat.sh --tmpdir=$BLUE/tmp --expected-lifetime=24h --memory=4000  #--debug --notimestamp
