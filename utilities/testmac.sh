export APP=$WHEREIPUTMYCODE/..
export _CONDOR_SCRATCH_DIR=$PWD
export INPUT_TAR_DIR_LOCAL=$APP
export SCRATCH=$HOME/tmp/

# example test batch job to run on minervagpvm01 to run CCQEMAT
# other option (not tested yet) is the EventLoop from the tutorial

# type python $APP/TOPMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# here my release is in $APP/TOPMAT - your mileage may differ

python $APP/TOPMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test --basedir=$APP/TOPMAT --rundir=CCQENu/make_hists --playlist=minervame5A --tag=test --mail --prescale=100 --exe=sidebands_v2 --config=./hms/testmac --setup=CCQENu/utilities/setup_batch_osx.sh --tardir=$HOME/tmp/test --tmpdir=$HOME/tmp/ #--debug --notimestamp
