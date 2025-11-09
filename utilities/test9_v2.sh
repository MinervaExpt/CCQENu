#export _CONDOR_SCRATCH_DIR=$PWD
#export INPUT_TAR_DIR_LOCAL=$APP

# example test batch job to run on minervagpvm01 to run CCQEMAT
# other option (not tested yet) is the EventLoop from the tutorial

# type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# here my release is in $APP/NEWMAT - your mileage may differ

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=MnvTunev2 --tag=AL9 \
 --mail --prescale=100 --config=p6_run --exe=sidebands_v2 --sample=QElike --setup=CCQENu/utilities/setup_batch_al9_v2.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   #--debug --notimestamp
