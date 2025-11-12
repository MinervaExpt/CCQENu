# batch version to run - assumes you are in the unfolded CCQEMAT directory
# BASEDIR needs to be the directory that contains your MAT/MAT-MINERvA/UnfoldUtils/Analysis code
# RUNDIR is where your analysis executable actually lie, in this case in $BASEDIR/CCQENu/make_hists
echo " this uses a spack 1.0 setup"
echo "setup-batch_al9_v1.sh"
source /cvmfs/dune.opensciencegrid.org/spack/setup-env.sh
echo "Activate dune-workflow"
spack env activate dune-workflow
echo "load GCC and CMAKE so don't use system"
echo "GCC"
spack load gcc@12.5.0 arch=linux-almalinux9-x86_64_v2 
#echo "CMAKE"
#spack load cmake 
export IFDH_CP_MAXRETRIES=0\0\0\0\0  # no retries
echo "which root"
which root
root --version
echo "which gcc"
which gcc
gcc --version
echo "which python"
which python
python --version
echo "which cmake"
which cmake
cmake --version
# set up the MAT
#use to be source $BASEDIR/opt/build/setup.sh
#export WHEREIPUTMYCODE=/exp/minerva/app/users/schellma/MNV9
#export WHEREIPUTTHEMAT=${WHEREIPUTTHECODE}
#export BASEDIR=${WHEREIPUTMYCODE}
export CCQEMAT=${BASEDIR}/CCQENu/make_hists
export UTILITIES=${BASEDIR}/CCQENu/utilities
OLD_PATH=${PATH}

OLD_LIBS=${LD_LIBRARY_PATH}
export INSTALL_DIR=$BASEDIR/opt
source ${INSTALL_DIR}/bin/setup_MAT.sh
source ${INSTALL_DIR}/bin/setup_MAT-MINERvA.sh
source ${INSTALL_DIR}/bin/setup_UnfoldUtils.sh
# get the MINERvA utils
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

#source $HOME/Alma9/test-paths.sh
# test-paths.sh
echo "which root"
which root
root --version
echo "which gcc"
which gcc
gcc --version
echo "which python"
which python
python --version
echo "which cmake"
which cmake
cmake --version