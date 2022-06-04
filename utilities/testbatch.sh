#export _CONDOR_SCRATCH_DIR=$PWD
#export INPUT_TAR_DIR_LOCAL=$APP

# example test batch job to run on minervagpvm01 to run CCQEMAT
# other option (not tested yet) is the EventLoop from the tutorial

# type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# here my release is in $APP/NEWMAT - your mileage may differ

python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test --basedir=$APP/NEWMAT --rundir=CCQENu/make_hists --playlist=minervame5A --tag=test --mail --prescale=1000 --config=$CCQEMAT/testme --setup=CCQENu/utilities/setup_batch_mat.sh --tmpdir=$BLUE/tmp #--debug --notimestamp
