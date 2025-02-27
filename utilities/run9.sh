#export _CONDOR_SCRATCH_DIR=$PWD
#export INPUT_TAR_DIR_LOCAL=$APP

# example test batch job to run on minervagpvm01 to run CCQEMAT
# other option (not tested yet) is the EventLoop from the tutorial

# type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# here my release is in $APP/NEWMAT - your mileage may differ

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame1N --model=MnvTunev2 --tag=AL9 \
 --tardir=/exp/minerva/data/users/gilligan/tars --mail \
 --prescale=1000 --config=smg/config/main/NuConfig_2track  --exe=./sidebands_v2 --sample=2track --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=4000  #--debug --notimestamp
