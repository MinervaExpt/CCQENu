python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame1E --model=MnvTunev2 --tag=AL9-workflow \
 --mail --prescale=1 --config=smg/config/main/NuConfig_bdtg_2track_MultiPionCut_me1E_5of10 --exe=sidebands_v2 --sample=2track_MultiPionCut --setup=CCQENu/utilities/setup_batch_al9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=48h --memory=4000
