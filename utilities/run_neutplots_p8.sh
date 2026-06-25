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
export MYMODEL=MnvTunev2.0.1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/June2026/blobstudy/${MYMODEL}/1and2track_AllBlobs/twodim \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/June2026/blobstudy/${MYMODEL}/1and2track_AllBlobs/onedim \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_1d_AllBlobs \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_1dneut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/June2026/blobstudy/${MYMODEL}/1and2track_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/June2026/blobstudy/${MYMODEL}/1and2track_2donly/onedim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_1d_2dblobs \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_1dneut_2dblobs --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/June2026/blobstudy/${MYMODEL}/1and2track_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/June2026/blobstudy/${MYMODEL}/1and2track_3donly/onedim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_1d_3dblobs \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_1dneut_3dblobs --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
