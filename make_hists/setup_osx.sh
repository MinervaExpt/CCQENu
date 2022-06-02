# unix version
#source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

<<<<<<< HEAD
#export WHEREIPUTMYCODE=$HOME/Dropbox/TOPMAT    # change this here if you want a different location
source /Users/vaughann/gitmat/opt/build/setup.sh     # you have to have this
=======
#export WHEREIPUTMYCODE=$HOME/Dropbox/BIGMAT    # change this here if you want a different location
source $WHEREIPUTMYCODE/opt/build/setup.sh     # you have to have this
>>>>>>> cfe40dc9cfb4668d4617c134976a594ce4c58751

#export JSONCPP_DIR=$HOME/LocalApps/jsoncpp-build # need to change this probably

export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists

export DYLD_LIBRARY_PATH=${PLOTUTILSROOT}
<<<<<<< HEAD
export PYTHONPATH=${WHEREIPUTMYCODE}/MAT-MINERvA/python:${WHEREIPUTMYCODE}/MAT-MINERvA/python/PlotUtils:${CCQEMAT}/python:$PYTHONPATH
#export THEDATA=/pnfs/minerva/persistent/users/drut1186/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron
=======
export PYTHONPATH=$WHEREIPUTMYCODE/MAT-MINERvA/python:$WHEREIPUTMYCODE/MAT-MINERvA/python/PlotUtils:$PYTHONPATH
export THEDATA=/pnfs/minerva/persistent/users/drut1186/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron

sed s+GIT_COMMIT_HASH+`git rev-parse --verify HEAD`+ utils/gitVersion.h.in > utils/gitVersion.h
>>>>>>> cfe40dc9cfb4668d4617c134976a594ce4c58751
