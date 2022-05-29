# batch version to run - assumes you are in the unfolded CCQEMAT directory
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

# get the packages you need to run this
setup cmake v3_14_3 -z /cvmfs/larsoft.opensciencegrid.org/products
setup root v6_16_00 -q e17:prof -z /cvmfs/larsoft.opensciencegrid.org/products 
setup boost v1_70_0 -q e19:prof -z /cvmfs/larsoft.opensciencegrid.org/products  # do we still need this? 
setup python v3_7_2 -z /cvmfs/larsoft.opensciencegrid.org/products
setup gdb  v8_2_1 -z /cvmfs/larsoft.opensciencegrid.org/products

#export WHEREIPUTMYCODE=$PWD    # change this here if you want a different location
export MPARAMFILESROOT=/cvmfs/minerva.opensciencegrid.org/minerva/CentralizedFluxAndReweightFiles/MParamFiles
export MPARAMFILES=$MPARAMFILESROOT/data
#
export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists
export JSONCPP_DIR=$WHEREIPUTMYCODE/jsoncpp-build # need to change this probably
export LD_LIBRARY_PATH=$JSONCPP_DIR/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$CCQEMAT/python:$WHEREIPUTMYCODE/MAT-MINERvA/python:$WHEREIPUTMYCODE/MAT-MINERvA/python/PlotUtils:$PYTHONPATH
