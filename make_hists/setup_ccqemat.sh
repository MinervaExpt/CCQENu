# unix version
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

# get the packages you need to run this
setup cmake v3_14_3 -z /cvmfs/larsoft.opensciencegrid.org/products
setup root v6_16_00 -q e17:prof -z /cvmfs/larsoft.opensciencegrid.org/products 
setup boost v1_70_0 -q e19:prof -z /cvmfs/larsoft.opensciencegrid.org/products  # do we still need this? 
setup python v3_7_2 -z /cvmfs/larsoft.opensciencegrid.org/products
setup gdb  v8_2_1 -z /cvmfs/larsoft.opensciencegrid.org/products
export BOOSTDIR=$BOOST_INC/..
#
# Set some handly locations
#
# 
#
export WHEREIPUTMYCODE=$HOME/standalone    # change this here if you want a different location
#
export JSONCPP_DIR=$HOME/LocalApps/jsoncpp-build # need to change this probably
export PLOTUTILSROOT=$WHEREIPUTMYCODE/Ana/PlotUtils
export UNFOLDUTILSROOT=$WHEREIPUTMYCODE/Ana/UnfoldUtils
export CCQEMAT=$WHEREIPUTMYCODE/Ana/PickledCCQENu/ana/make_hists
export MPARAMFILESROOT=$WHEREIPUTMYCODE/MParamFiles
export MPARAMFILES=$MPARAMFILESROOT/data
export LD_LIBRARY_PATH=${PLOTUTILSROOT}:${UNFOLDUTILSROOT}:${JSONCPP_DIR}/lib:${LD_LIBRARY_PATH}
export NSFTEST=$WHEREIPUTMYCODE/Personal/OSUTeam/schellma/NSFTest
export THEDATA=/pnfs/minerva/persistent/users/drut1186/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron
