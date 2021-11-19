source ~schellmh/conda.sh

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft
export WHEREIPUTMYCODE=/home/physics/$USER/gitMinerva   # change this here if you want a different location
source $WHEREIPUTMYCODE/opt/build/setup.sh     # you have to have this

export JSONCPP_DIR=/minerva/app/users/schellma/LocalApps/jsoncpp-build
export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists
export THEDATA=/pnfs/minerva/persistent/users/drut1186/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron
