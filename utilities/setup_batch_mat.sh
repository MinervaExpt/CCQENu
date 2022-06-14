# batch version to run - assumes you are in the unfolded CCQEMAT directory
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

# get the packages you need to run this
setup cmake v3_14_3 -z /cvmfs/larsoft.opensciencegrid.org/products
setup root v6_16_00 -q e17:prof -z /cvmfs/larsoft.opensciencegrid.org/products 
setup boost v1_70_0 -q e19:prof -z /cvmfs/larsoft.opensciencegrid.org/products  # do we still need this? 
setup python v3_7_2 -z /cvmfs/larsoft.opensciencegrid.org/products
setup gdb  v8_2_1 -z /cvmfs/larsoft.opensciencegrid.org/products
setup ifdhc -z /cvmfs/fermilab.opensciencegrid.org/products/common/db
export IFDH_CP_MAXRETRIES=0\0\0\0\0  # no retries
# set up the MAT
#use to be source $BASEDIR/opt/build/setup.sh
OLD_PATH=${PATH}
OLD_LIBS=${LD_LIBRARY_PATH}
export INSTALL_DIR=$BASEDIR/opt
source ${INSTALL_DIR}/bin/setup_MAT.sh
source ${INSTALL_DIR}/bin/setup_MAT-MINERvA.sh
source ${INSTALL_DIR}/bin/setup_UnfoldUtils.sh
#source ${INSTALL_DIR}/bin/setup_MAT_IncPions.sh
#source ${INSTALL_DIR}/bin/setup_GENIEXSecExtract.sh

#Don't repeat a lot of copies of INSTALL_DIR on PATH and LD_LIBRARY_PATH.
#WARNING: This is very specific to the tutorial.  Don't copy this blindly!
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
