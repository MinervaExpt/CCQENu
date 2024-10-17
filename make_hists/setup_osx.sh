# osx version
#source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft
#export WHEREIPUTMYCODE=$HOME/Dropbox/MNV9
#export WHEREIPUTMYCODE=$HOME/Dropbox/BIGMAT    # change this here if you want a different location
source $WHEREIPUTMYCODE/opt/build/setup.sh     # you have to have this

export JSONCPP_DIR=$HOME/LocalApps/jsoncpp-build # need to change this probably

export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists

export DYLD_LIBRARY_PATH=${PLOTUTILSROOT}
export PYTHONPATH=$CCQEMAT/python:$WHEREIPUTMYCODE/MAT-MINERvA/python:$WHEREIPUTMYCODE/MAT-MINERvA/python/PlotUtils:$PYTHONPATH
export THEDATA=/pnfs/minerva/persistent/users/drut1186/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron

sed s+GIT_COMMIT_HASH+`git rev-parse --verify HEAD`+ utils/gitVersion.h.in > utils/gitVersion.h
export MYPLAYLIST=minervame5A
export PRESCALE=100
export DATALOC=local
export MYMODEL=MnvTunev1
