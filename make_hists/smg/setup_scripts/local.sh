# unix version
#source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

export WHEREIPUTMYCODE=$HOME/Minerva   # change this here if you want a different location
source $WHEREIPUTMYCODE/opt/build/setup.sh     # you have to have this
#source $WHEREIPUTMYCODE/TupleComparison/setup.sh  # for TupleComparison stuff
export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists
export PLAYLISTDIR=$WHEREIPUTMYCODE/data/playlists/local

#Get PlotUtils into Python path
#export PYTHONPATH=$WHEREIPUTMYCODE/MAT-MINERvA/python:$WHEREIPUTMYCODE/MAT-MINERvA/python/PlotUtils

export JSONCPP_DIR=/usr/include/jsoncpp/
#JSONCPP_DIR=$HOME/Minerva/jsoncpp-build/
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$JSONCPP_DIR/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$JSONCPP_DIR
