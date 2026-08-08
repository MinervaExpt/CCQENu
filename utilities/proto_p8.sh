#export _CONDOR_SCRATCH_DIR=$PWD
export INPUT_TAR_DIR_LOCAL=/exp/minerva/data/users/$USER

# example test batch job to run on minervagpvm01 to run CCQEMAT
# other option (not tested yet) is the EventLoop from the tutorial

# type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# here my release is in $APP/NEWMAT - your mileage may differ


python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=5A --model=MnvTunev2 --tag=AL9-p8 \
 --mail --prescale=100 --config=p8_run --exe=sidebands_v2 --sample=QElike --setup=CCQENu/utilities/setup_batch_al9_proto.sh \
 --tmpdir=/exp/minerva/data/users/$USER/tmp --expected-lifetime=4h --memory=3000   #--debug --notimestamp
