export APP=/minerva/app/users/$USER
export SCRATCH=/pnfs/minerva/scratch/users/$USER
export BLUE=/minerva/data/users/$USER
export DATALOC=remote

python $APP/minerva/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test --basedir=$APP/minerva --rundir=CCQENu/make_hists --playlist=minervame5A --tag=ccqe --mail --prescale=100 --config=hms/test_recoil --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat.sh --tmpdir=$BLUE/tmp --expected-lifetime=12h --memory=2000  #--debug --notimestamp 
