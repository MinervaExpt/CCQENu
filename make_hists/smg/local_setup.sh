# unix version
#source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

export WHEREIPUTMYCODE=/home/gilligas/gitMinerva   # change this here if you want a different location
source $WHEREIPUTMYCODE/opt/build/setup.sh     # you have to have this

export JSONCPP_DIR=/home/gilligas/JSON/jsoncpp-build

export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists

#export DYLD_LIBRARY_PATH=${PLOTUTILSROOT}

export THEDATA=/home/gilligas/gitMinerva/data/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron
