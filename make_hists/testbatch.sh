export _CONDOR_SCRATCH_DIR=$PWD
export INPUT_TAR_DIR_LOCAL=$APP

python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test --basedir=NEWMAT --rundir=CCQENu/make_hists --playlist=minervame5A --tag=test --mail --prescale=1000 --config=testme --setup=CCQENu/make_hists/setup_batch_mat.sh #--debug --notimestamp
