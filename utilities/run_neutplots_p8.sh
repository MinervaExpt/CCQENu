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
export MYBLOBSELECTION=noselection

# 1dplots
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplots1d/blobs2d/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYSAMPLE}_thesis_blobplots1d_2d \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobs1D_2d --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplots1d/blobs3d/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYSAMPLE}_thesis_blobplots1d_3d \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobs1D_3d --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplots1d/blobsall/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYSAMPLE}_thesis_blobplots1d_all \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobs1D_all --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# hdplots
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplotshd/blobs2d/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYSAMPLE}_thesis_blobplots1d_2d \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobsHD_2d --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplotshd/blobs3d/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYSAMPLE}_thesis_blobplots1d_3d \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobsHD_3d --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplotshd/blobsall/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYSAMPLE}_thesis_blobplots1d_all \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobsHD_all --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ============== onetrack
# 1dplots
export MYSAMPLE=QElike1track
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplots1d/blobs2d/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYSAMPLE}_thesis_blobplots1d_2d \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobs1D_2d --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplots1d/blobs3d/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYSAMPLE}_thesis_blobplots1d_3d \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobs1D_3d --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplots1d/blobsall/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYSAMPLE}_thesis_blobplots1d_all \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobs1D_all --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# hdplots
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplotshd/blobs2d/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYSAMPLE}_thesis_blobplots1d_2d \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobsHD_2d --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplotshd/blobs3d/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYSAMPLE}_thesis_blobplots1d_3d \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobsHD_3d --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplotshd/blobsall/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYSAMPLE}_thesis_blobplots1d_all \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobsHD_all --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp


# ============== twotrack
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplots1d/blobs2d/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_thesis_blobplots1d_2d \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobs1D_2d --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplots1d/blobs3d/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_thesis_blobplots1d_3d \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobs1D_3d --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplots1d/blobsall/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_thesis_blobplots1d_all \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobs1D_all --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp

# hdplots
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplotshd/blobs2d/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_thesis_blobplots1d_2d \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobsHD_2d --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplotshd/blobs3d/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_thesis_blobplots1d_3d \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobsHD_3d --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/eventloopout/thesis/blobs/${MYBLOBSELECTION}/blobplotshd/blobsall/${MYSAMPLE} \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=${MYMODEL}_thesis_blobplots1d_all \
 --mail --prescale=1 --config=nhv/config/thesis/AntiNu_v15_thesis_grid_blobsHD_all --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9_p8.sh \
 --tmpdir=/exp/minerva/data/users/nvaughan/tmp --expected-lifetime=4h --memory=3000   --sample=${MYSAMPLE} #--debug --notimestamp
