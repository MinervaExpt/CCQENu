# Noah's hep01 version
#source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups

export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

# export WHEREIPUTMYCODE=/home/physics/vaughann/git   # change this here if you want a different location
source ${WHEREIPUTMYCODE}/opt/build/setup.sh     # you have to have this

# export JSONCPP_DIR=/exp/minerva/app/users/schellma/LocalApps/jsoncpp-build

export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists

#export DYLD_LIBRARY_PATH=${PLOTUTILSROOT}
export PYTHONPATH=$CCQEMAT/python:$WHEREIPUTMYCODE/MAT-MINERvA/python:$WHEREIPUTMYCODE/MAT-MINERvA/python/PlotUtils:$PYTHONPATH
export PLAYLISTROOT=${CCQEMAT}/playlists/hep01
export MYMODEL=MnvTunev1
export MYPLAYLIST=minervame6A
export MYSAMPLE=QElike
echo "export MYMODEL=MnvTunev1"
echo "export MYPLAYLIST=minervame6A"
echo "export MYSAMPLE=QElike"