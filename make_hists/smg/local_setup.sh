# unix version
#source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

export WHEREIPUTMYCODE=/home/sean/Minerva   # change this here if you want a different location
source $WHEREIPUTMYCODE/opt/build/setup.sh     # you have to have this

export JSONCPP_DIR=/usr/
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${JSONCPP_DIR}/lib

export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists
export THEDATA=/home/sean/Minerva/data/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron
