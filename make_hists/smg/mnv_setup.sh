export WHEREIPUTMYCODE=/minerva/app/users/$USER/minerva
export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists
export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft
export JSONCPP_DIR=/minerva/app/users/$USER/LocalApps/jsoncpp-build
export LD_LIBRARY_PATH=${JSONCPP_DIR}/lib:${PLOTUTILSROOT}:${UNFOLDUTILSROOT}:${LD_LIBRARY_PATH}
export THEDATA=/pnfs/minerva/persistent/users/drut1186/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron

# Same cvmfs setup/cmake/root used for MAT-MINERvA
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups
setup cmake v3_14_3 -z /cvmfs/larsoft.opensciencegrid.org/products
setup root v6_16_00 -q e17:prof -z /cvmfs/larsoft.opensciencegrid.org/products

kx509
voms-proxy-init -rfc --voms=fermilab:/fermilab/minerva/Role=Analysis --noregen -valid 24:00

source $WHEREIPUTMYCODE/opt/build/setup.sh

