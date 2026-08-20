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

# ============== onetrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdistcut/1trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# ============== twotrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
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

# ============== onetrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# ============== twotrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
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

# ============== onetrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# ============== twotrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
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

# ============== onetrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# ============== twotrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
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

# ============== onetrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# ============== twotrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
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

# ============== onetrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# ============== twotrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
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

# ============== onetrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# ============== twotrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp



# QElike
export MYSAMPLE=QElike
export MYWARP=none
export MYMODEL=MnvTunev2.0.1

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
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

# ============== onetrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# ============== twotrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
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

# ============== onetrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# ============== twotrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
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

# ============== onetrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# ============== twotrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
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

# ============== onetrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/1trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_1trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_1track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# ============== twotrack
# allblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_AllBlobs/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_AllBlobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 2dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_2donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_2dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_2dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# 3dblobs
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/August2026/blobstudy_fixed/${MYMODEL}/vtxdistcut_new1track_trackdiscut/2trackonly_3donly/twodim \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_neutronblob_plotstuff_hd_3dblobs_2trackonly \
 --mail --prescale=1 --config=nhv/config/warpingstudies/blobs/AntiNu_v15_warping_hdneut_3dblobs_2track --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
