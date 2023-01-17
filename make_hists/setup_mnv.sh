# unix version
#source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

export WHEREIPUTMYCODE=/minerva/app/users/$USER/NEWMAT   # change this here if you want a different location
source $WHEREIPUTMYCODE/opt/build/setup.sh     # you have to have this

export JSONCPP_DIR=$WHEREIPUTMYCODE/jsoncpp-build

export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists

#export DYLD_LIBRARY_PATH=${PLOTUTILSROOT}
export PYTHONPATH=$CCQEMAT/python:$WHEREIPUTMYCODE/MAT-MINERvA/python:$WHEREIPUTMYCODE/MAT-MINERvA/python/PlotUtils:$PYTHONPATH
sed s+GIT_COMMIT_HASH+`git rev-parse --verify HEAD`+ utils/gitVersion.h.in > utils/gitVersion.h
export THEDATA=/pnfs/minerva/persistent/users/drut1186/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron
