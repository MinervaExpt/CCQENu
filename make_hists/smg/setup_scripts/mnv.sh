export WHEREIPUTMYCODE=/exp/minerva/app/users/$USER/minerva
export BASEDIR=$WHEREIPUTMYCODE
export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists
export UTILITIES=$WHEREIPUTMYCODE/CCQENu/utilities
export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft
export JSONCPP_DIR=$WHEREIPUTMYCODE/jsoncpp-build
export LD_LIBRARY_PATH=${JSONCPP_DIR}/lib:${PLOTUTILSROOT}:${UNFOLDUTILSROOT}:${LD_LIBRARY_PATH}
export THEDATA=/pnfs/minerva/persistent/users/drut1186/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron
export SCRATCH=/pnfs/minerva/scratch/users/gilligan
export GROUP=minerva
export MPARAMFILESROOT=/cvmfs/minerva.opensciencegrid.org/minerva/CentralizedFluxAndReweightFiles/MParamFiles
export MPARAMFILES=$MPARAMFILESROOT/data

#Get PlotUtils into Python path
export PYTHONPATH=$WHEREIPUTMYCODE/MAT-MINERvA/python:$WHEREIPUTMYCODE/MAT-MINERvA/python/PlotUtils

# Same cvmfs setup/cmake/root used for MAT-MINERvA
source /cvmfs/larsoft.opensciencegrid.org/spack-packages/setup-env.sh
spack load gcc@12.2.0
spack load root@6.28.12%gcc@12.2.0
spack load cmake@3.27.7
spack load fife-utils@3.7.4
spack load metacat@4.0.0
spack load sam-web-client@3.4%gcc@12.2.0
export IFDH_CP_MAXRETRIES=0\0\0\0\0  # no retries

kx509
voms-proxy-init -rfc --voms=fermilab:/fermilab/minerva/Role=Analysis --noregen -valid 72:00
source $WHEREIPUTMYCODE/opt/bin/setup_MAT.sh
source $WHEREIPUTMYCODE/opt/bin/setup_MAT-MINERvA.sh
source $WHEREIPUTMYCODE/opt/bin/setup_UnfoldUtils.sh
export PLAYLISTDIR=$CCQEMAT/playlists/remote

#setup jobsub_client
alias jq="jobsub_q --user=$USER -G=minerva"
alias jh="jobsub_history --group=minerva --user=$USER"
alias jl="source ~/getlog.sh "
alias jrm="jobsub_rm --group=minerva "

