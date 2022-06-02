# unix version
#source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

#export WHEREIPUTMYCODE=$HOME/Dropbox/TOPMAT    # change this here if you want a different location
source /Users/vaughann/gitmat/opt/build/setup.sh     # you have to have this

#export JSONCPP_DIR=$HOME/LocalApps/jsoncpp-build # need to change this probably

export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists

export DYLD_LIBRARY_PATH=${PLOTUTILSROOT}
export PYTHONPATH=${WHEREIPUTMYCODE}/MAT-MINERvA/python:${WHEREIPUTMYCODE}/MAT-MINERvA/python/PlotUtils:${CCQEMAT}/python:$PYTHONPATH
#export THEDATA=/pnfs/minerva/persistent/users/drut1186/CCQENu_Anatuples/MuonKludge_ProtonLLR_UpdatedNeutron
