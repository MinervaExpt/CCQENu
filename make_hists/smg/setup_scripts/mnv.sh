export WHEREIPUTMYCODE=/minerva/app/users/$USER/minerva
export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists
export UTILITIES=$WHEREIPUTMYCODE/CCQENu/utilities
export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft
export JSONCPP_DIR=$WHEREIPUTMYCODE/jsoncpp-build 
export LD_LIBRARY_PATH=${JSONCPP_DIR}/lib:${PLOTUTILSROOT}:${UNFOLDUTILSROOT}:${LD_LIBRARY_PATH}
export THEDATA=/pnfs/minerva/persistent/users/drut1186/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron
export SCRATCH=/pnfs/minerva/scratch/users/gilligan
export GROUP=minerva

#Get PlotUtils into Python path
export PYTHONPATH=$WHEREIPUTMYCODE/MAT-MINERvA/python:$WHEREIPUTMYCODE/MAT-MINERvA/python/PlotUtils

# Same cvmfs setup/cmake/root used for MAT-MINERvA
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups
setup cmake v3_14_3 -z /cvmfs/larsoft.opensciencegrid.org/products
setup root v6_28_12 -q e20:p3915:prof -z /cvmfs/larsoft.opensciencegrid.org/products
setup python v3_7_2 -z /cvmfs/larsoft.opensciencegrid.org/products
setup gdb  v8_2_1 -z /cvmfs/larsoft.opensciencegrid.org/products
setup ifdhc -z /cvmfs/fermilab.opensciencegrid.org/products/common/db
export IFDH_CP_MAXRETRIES=0\0\0\0\0  # no retries

kx509
voms-proxy-init -rfc --voms=fermilab:/fermilab/minerva/Role=Analysis --noregen -valid 24:00
source $WHEREIPUTMYCODE/opt/build/setup.sh
source $WHEREIPUTMYCODE/TupleComparison/setup.sh
export PLAYLISTDIR=$CCQEMAT/playlists/remote

#setup jobsub_client
alias jq="jobsub_q --user=$USER"
alias jh="jobsub_history --group=minerva --user=$USER"
alias jl="source ~/getlog.sh "
alias jrm="jobsub_rm --group=minerva "

