# batch version to run - assumes you are in the unfolded CCQEMAT directory
# BASEDIR needs to be the directory that contains your MAT/MAT-MINERvA/UnfoldUtils/Analysis code
# RUNDIR is where your analysis executable actually lie, in this case in $BASEDIR/CCQENu/make_hists

#source /cvmfs/larsoft.opensciencegrid.org/spack-packages/setup-env.sh
# gives you access to root and cmake …
source /cvmfs/larsoft.opensciencegrid.org/spack-v0.22.0-fermi/setup-env.sh

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

# get the packages you need to run this
spack load root@6.28.12 arch=linux-almalinux9-x86_64_v3
spack load cmake arch=linux-almalinux9-x86_64_v3
spack load gcc@12.2.0
spack load ifdhc-config@2.6.20%gcc@11.4.1 arch=linux-almalinux9-x86_64_v2
#spack load fife-utils@3.7.4
spack load py-pip@23.1.2 arch=linux-almalinux9-x86_64_v3
htgettoken -a htvaultprod.fnal.gov -i minerva
export IFDH_CP_MAXRETRIES=0\0\0\0\0  # no retries
# set up the MAT
#use to be source $BASEDIR/opt/build/setup.sh
export WHEREIPUTMYCODE=/exp/minerva/app/users/schellma/MNV9
export WHEREIPUTTHEMAT=${WHEREIPUTTHECODE}
export BASEDIR=${WHEREIPUTMYCODE}
export CCQEMAT=${BASEDIR}/CCQENu/make_hists
export UTILITIES=${BASEDIR}/CCQENu/utilities
OLD_PATH=${PATH}

OLD_LIBS=${LD_LIBRARY_PATH}
export INSTALL_DIR=$BASEDIR/opt
source ${INSTALL_DIR}/bin/setup_MAT.sh
source ${INSTALL_DIR}/bin/setup_MAT-MINERvA.sh
source ${INSTALL_DIR}/bin/setup_UnfoldUtils.sh
# get the MINERvA utils
#export PATH=${OLD_PATH}:${HOME}/.local/bin
export PATH=${OLD_PATH}:${INSTALL_DIR}/bin
export PLOTUTILSROOT=${BASEDIR}/opt/lib  # need this for weights?
export LD_LIBRARY_PATH=${OLD_LIBS}:${INSTALL_DIR}/lib
export MPARAMFILESROOT=/cvmfs/minerva.opensciencegrid.org/minerva/CentralizedFluxAndReweightFiles/MParamFiles
export MPARAMFILES=$MPARAMFILESROOT/data
# CCQEMAT special setup
export JSONCPP_DIR=$BASEDIR/jsoncpp-build # need to change this probably
export LD_LIBRARY_PATH=$RUNDIR:$JSONCPP_DIR/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$RUNDIR/python:$BASEDIR/MAT-MINERvA/python:$BASEDIR/MAT-MINERvA/python/PlotUtils:$PYTHONPATH
export DATALOC=remote
#setup jobsub_client
alias jq="jobsub_q --user=$USER -G=minerva"
alias jh="jobsub_history --group=minerva --user=$USER"
alias jl="source ~/getlog.sh "
alias jrm="jobsub_rm --group=minerva "
export BOOSTDIR=$BOOST_INC/..
export BLUE=/exp/minerva/data/users/$USER
export APP=/exp/minerva/app/users/$USER
export SCRATCH=/pnfs/minerva/scratch/users/$USER
export MYPLAYLIST=minervame5A
export PRESCALE=100
export DATALOC=remote
export MYSAMPLE=QElike
export MYMODEL=MnvTunev1
#env
