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
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=no2p2htune
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=none
export MYMODEL=MnvTunev2

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# ==========
# QElike recoil cut
export MYSAMPLE=QElike_maxrecoil
export MYWARP=none
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=no2p2htune
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=none
export MYMODEL=MnvTunev2

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# ==========
# QElike no recoil cut
export MYWARP=none
export MYSAMPLE=QElike
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=no2p2htune
# export MYSAMPLE=QElike
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=none
# export MYSAMPLE=QElike
export MYMODEL=MnvTunev2

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame5A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp


 # ================================================================================================================================================================
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
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=no2p2htune
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=none
export MYMODEL=MnvTunev2

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# ==========
# QElike recoil cut
export MYSAMPLE=QElike_maxrecoil
export MYWARP=none
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=no2p2htune
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=none
export MYMODEL=MnvTunev2

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# ==========
# QElike no recoil cut
export MYWARP=none
export MYSAMPLE=QElike
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=no2p2htune
# export MYSAMPLE=QElike
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=none
# export MYSAMPLE=QElike
export MYMODEL=MnvTunev2

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6A --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp


 # ================================================================================================================================================================
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
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=no2p2htune
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=none
export MYMODEL=MnvTunev2

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# ==========
# QElike recoil cut
export MYSAMPLE=QElike_maxrecoil
export MYWARP=none
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=no2p2htune
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=none
export MYMODEL=MnvTunev2

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# ==========
# QElike no recoil cut
export MYWARP=none
export MYSAMPLE=QElike
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=no2p2htune
# export MYSAMPLE=QElike
export MYMODEL=MnvTunev1

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

export MYWARP=none
# export MYSAMPLE=QElike
export MYMODEL=MnvTunev2

python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
 --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6B --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
 --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp






#  # ================================================================================================================================================================
# #export _CONDOR_SCRATCH_DIR=$PWD
# #export INPUT_TAR_DIR_LOCAL=$APP

# # example test batch job to run on minervagpvm01 to run CCQEMAT
# # other option (not tested yet) is the EventLoop from the tutorial

# # type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# # here my release is in $APP/NEWMAT - your mileage may differ

# # ==========

# # QElike
# export MYSAMPLE=QElike
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike recoil cut
# export MYSAMPLE=QElike_maxrecoil
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike no recoil cut
# export MYWARP=none
# export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6C --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp


#  # ================================================================================================================================================================
# #export _CONDOR_SCRATCH_DIR=$PWD
# #export INPUT_TAR_DIR_LOCAL=$APP

# # example test batch job to run on minervagpvm01 to run CCQEMAT
# # other option (not tested yet) is the EventLoop from the tutorial

# # type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# # here my release is in $APP/NEWMAT - your mileage may differ

# # ==========

# # QElike
# export MYSAMPLE=QElike
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike recoil cut
# export MYSAMPLE=QElike_maxrecoil
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike no recoil cut
# export MYWARP=none
# export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6D --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp


#  # ================================================================================================================================================================
# #export _CONDOR_SCRATCH_DIR=$PWD
# #export INPUT_TAR_DIR_LOCAL=$APP

# # example test batch job to run on minervagpvm01 to run CCQEMAT
# # other option (not tested yet) is the EventLoop from the tutorial

# # type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# # here my release is in $APP/NEWMAT - your mileage may differ

# # ==========

# # QElike
# export MYSAMPLE=QElike
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike recoil cut
# export MYSAMPLE=QElike_maxrecoil
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike no recoil cut
# export MYWARP=none
# export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6E --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp


#  # ================================================================================================================================================================
# #export _CONDOR_SCRATCH_DIR=$PWD
# #export INPUT_TAR_DIR_LOCAL=$APP

# # example test batch job to run on minervagpvm01 to run CCQEMAT
# # other option (not tested yet) is the EventLoop from the tutorial

# # type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# # here my release is in $APP/NEWMAT - your mileage may differ

# # ==========

# # QElike
# export MYSAMPLE=QElike
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike recoil cut
# export MYSAMPLE=QElike_maxrecoil
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike no recoil cut
# export MYWARP=none
# export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6F --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp


#  # ================================================================================================================================================================
# #export _CONDOR_SCRATCH_DIR=$PWD
# #export INPUT_TAR_DIR_LOCAL=$APP

# # example test batch job to run on minervagpvm01 to run CCQEMAT
# # other option (not tested yet) is the EventLoop from the tutorial

# # type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# # here my release is in $APP/NEWMAT - your mileage may differ

# # ==========

# # QElike
# export MYSAMPLE=QElike
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike recoil cut
# export MYSAMPLE=QElike_maxrecoil
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike no recoil cut
# export MYWARP=none
# export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6G --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp


#  # ================================================================================================================================================================
# #export _CONDOR_SCRATCH_DIR=$PWD
# #export INPUT_TAR_DIR_LOCAL=$APP

# # example test batch job to run on minervagpvm01 to run CCQEMAT
# # other option (not tested yet) is the EventLoop from the tutorial

# # type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# # here my release is in $APP/NEWMAT - your mileage may differ

# # ==========

# # QElike
# export MYSAMPLE=QElike
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike recoil cut
# export MYSAMPLE=QElike_maxrecoil
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike no recoil cut
# export MYWARP=none
# export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6H --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp


#  # ================================================================================================================================================================
# #export _CONDOR_SCRATCH_DIR=$PWD
# #export INPUT_TAR_DIR_LOCAL=$APP

# # example test batch job to run on minervagpvm01 to run CCQEMAT
# # other option (not tested yet) is the EventLoop from the tutorial

# # type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# # here my release is in $APP/NEWMAT - your mileage may differ

# # ==========

# # QElike
# export MYSAMPLE=QElike
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike recoil cut
# export MYSAMPLE=QElike_maxrecoil
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike no recoil cut
# export MYWARP=none
# export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6I --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp


#  # ================================================================================================================================================================
# #export _CONDOR_SCRATCH_DIR=$PWD
# #export INPUT_TAR_DIR_LOCAL=$APP

# # example test batch job to run on minervagpvm01 to run CCQEMAT
# # other option (not tested yet) is the EventLoop from the tutorial

# # type python $APP/NEWMAT/CCQENu/utilities/SubmitJobsToGrid_MAT.py to see the option descriptions
# # here my release is in $APP/NEWMAT - your mileage may differ

# # ==========

# # QElike
# export MYSAMPLE=QElike
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike recoil cut
# export MYSAMPLE=QElike_maxrecoil
# export MYWARP=none
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_recoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_recoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# # ==========
# # QElike no recoil cut
# export MYWARP=none
# export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=no2p2htune
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev1

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp

# export MYWARP=none
# # export MYSAMPLE=QElike
# export MYMODEL=MnvTunev2

# python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/Summer25Collab/eventloopout/recoilstudy_newbinning \
#  --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=minervame6J --model=${MYMODEL} --warp=${MYWARP} --tag=recoilstudy_newbinning_norecoilcut \
#  --mail --prescale=1 --config=nhv/config/warpingstudies/AntiNu_v15_warping_grid_norecoilcut --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat9.sh \
#  --tmpdir=$SCRATCH/tmp --expected-lifetime=4h --memory=5000   --sample=${MYSAMPLE} #--debug --notimestamp


#  # ================================================================================================================================================================
