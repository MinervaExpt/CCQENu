# batch version to run - assumes you are in the unfolded CCQEMAT directory
# BASEDIR needs to be the directory that contains your MAT/MAT-MINERvA/UnfoldUtils/Analysis code
# RUNDIR is where your analysis executable actually lie, in this case in $BASEDIR/CCQENu/make_hists

# setup for alma9

uname -a 

#source /cvmfs/larsoft.opensciencegrid.org/spack-packages/setup-env.sh

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

# # get the packages you need to run this
# setup cmake v3_14_3 -z /cvmfs/larsoft.opensciencegrid.org/products
# # update root version
# setup root v6_22_08d -q e20:p392:prof -z /cvmfs/larsoft.opensciencegrid.org/products
# # update python version
# setup python v3_9_2 -z /cvmfs/larsoft.opensciencegrid.org/products

# get the packages you need to run this
#source /cvmfs/larsoft.opensciencegrid.org/spack-v0.22.0-fermi/setup-env.sh
source ${BASEDIR}/CCQENu/utilities/setup_spack.sh
# source /cvmfs/larsoft.opensciencegrid.org/spack-fnal-develop/spack_env/setup-env.sh
# export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

# # get the packages you need to run this - this is a total hack of guesswork
# spack load root@6.28.12/rqkcbbm
# spack load cmake@3.20.2 arch=linux-almalinux9-x86_64_v2 %gcc@11.5.0
# spack load gcc@12.4.0
# spack load ifdhc@2.8.0
# spack load ifdhc-config                          
# spack load py-pip
#setup gdb  v8_2_1 -z /cvmfs/larsoft.opensciencegrid.org/products
#setup ifdhc -z /cvmfs/fermilab.opensciencegrid.org/products/common/db
export IFDH_CP_MAXRETRIES=0\0\0\0\0  # no retries
# set up the MAT
#use to be source $BASEDIR/opt/build/setup.sh
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
echo "------------ CHECK THE VOMS PROXY and the X509"
voms-proxy-info --all
echo $X509_USER_PROXY
env
