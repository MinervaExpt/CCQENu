# unix version
#source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

export WHEREIPUTMYCODE=/minerva/app/users/$USER/gitMinerva   # change this here if you want a different location
source $WHEREIPUTMYCODE/opt/build/setup.sh     # you have to have this

export JSONCPP_DIR=/home/physics/gilligas/LocalApps/jsoncpp-build

export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists

#export DYLD_LIBRARY_PATH=${PLOTUTILSROOT}

export THEDATA=/minerva/data/ME/MuonKludge_ProtonLLR_UpdatedNeutron
