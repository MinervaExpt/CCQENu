#export _CONDOR_SCRATCH_DIR=$PWD
#export INPUT_TAR_DIR_LOCAL=$APP

# example test batch job to run on minervagpvm01 to run CCQEMAT
# other option (not tested yet) is the EventLoop from the tutorial

# type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# here my release is in $APP/NEWMAT - your mileage may differ

# ==========

# QElike
export MYSAMPLE=QElike
export MYWARP=none


export MYMODEL=MnvTunev4.3.1
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/February2026/warping/recoil100mm500MeVcut_allblobs_fullremoval_1and2track_newmodels/${MYMODEL} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_warpingstudy \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=4000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYMODEL=MnvTunev4.3.1_no2p2htune
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/February2026/warping/recoil100mm500MeVcut_allblobs_fullremoval_1and2track_newmodels/${MYMODEL} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_warpingstudy \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_untuned --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=4000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYMODEL=MnvTunev4.3
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/February2026/warping/recoil100mm500MeVcut_allblobs_fullremoval_1and2track_newmodels/${MYMODEL} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_warpingstudy \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_untuned --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=4000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYMODEL=MnvTunev4.3_no2p2htune
# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/February2026/warping/recoil100mm500MeVcut_allblobs_fullremoval_1and2track_newmodels/${MYMODEL} \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_warpingstudy \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=4000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYMODEL=MnvTunev4.3.1_SuSA2p2h
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/February2026/warping/recoil100mm500MeVcut_allblobs_fullremoval_1and2track_newmodels/${MYMODEL} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_warpingstudy \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_untuned --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=4000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYMODEL=MnvTunev4.3._SuSA2p2h
# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/February2026/warping/recoil100mm500MeVcut_allblobs_fullremoval_1and2track_newmodels/${MYMODEL} \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_warpingstudy \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=4000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYMODEL=MnvTunev4.3.1_elastic
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/February2026/warping/recoil100mm500MeVcut_allblobs_fullremoval_1and2track_newmodels/${MYMODEL} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_warpingstudy \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_untuned --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=4000   --sample=${MYSAMPLE} #--debug --notimestamp


export MYMODEL=MnvTunev4.3.1_absorption
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/February2026/warping/recoil100mm500MeVcut_allblobs_fullremoval_1and2track_newmodels/${MYMODEL} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_warpingstudy \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_untuned --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=4000   --sample=${MYSAMPLE} #--debug --notimestamp


