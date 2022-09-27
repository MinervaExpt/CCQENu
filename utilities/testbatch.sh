#export _CONDOR_SCRATCH_DIR=$PWD
#export INPUT_TAR_DIR_LOCAL=$APP
# some setup that I use to find common directories
export BLUE=/minerva/data/users/$USER
export SCRATCH=/pnfs/minerva/scratch/users/$USER
export APP=/minerva/app/users/$USER
# example test batch job to run on minervagpvm01 to run CCQEMAT
# other option (not tested yet) is the EventLoop from the tutorial

# type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# here my release is in $APP/NEWMAT - your mileage may differ

#RUNDIR is relative to BASEDIR
#EXE and CONFIG are relative to RUNDIR
mkdir -p $SCRATCH/test
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --tag=v1 --mail --prescale=1 --config=hms/test_batch --exe=sidebands_v2 --sample=Background --setup=CCQENu/utilities/setup_batch_mat.sh --tmpdir=$BLUE/tmp --expected-lifetime=24h --memory=2000  #--debug --notimestamp
