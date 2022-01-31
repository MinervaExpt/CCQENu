# unix version
#source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

export WHEREIPUTMYCODE=/home/gilligas/gitMinerva   # change this here if you want a different location
source $WHEREIPUTMYCODE/opt/build/setup.sh     # you have to have this

export JSONCPP_DIR=/home/gilligas/JSON/jsoncpp-build
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${JSONCPP_DIR}/lib

sed s+GIT_COMMIT_HASH+`git rev-parse --verify HEAD`+ utils/gitVersion.h.in > utils/gitVersion.h

export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists
export THEDATA=/home/gilligas/gitMinerva/data/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron
