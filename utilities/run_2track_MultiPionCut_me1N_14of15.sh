python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame1N --model=MnvTunev2 --tag=AL9-workflow \
 --mail --prescale=1 --config=smg/config/main/NuConfig_bdtg_2track_MultiPionCut_me1N_14of15 --exe=sidebands_v2 --sample=2track_MultiPionCut --setup=CCQENu/utilities/setup_batch_al9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=24h --memory=4000
