htgettoken -i minerva --vaultserver htvaultprod.fnal.gov #:8200
export BEARER_TOKEN_FILE=/run/user/`id -u`/bt_u`id -u`
echo "---------------------------------------- "
echo "see what the token is"
htdecodetoken 
echo "---------------------------------------- "
# test-paths.sh

echo "which root"
which root
root --version
echo "---------------------------------------- "
echo "which root python version"
root-config --python-version
echo "---------------------------------------- "
echo "which gcc"
which gcc
gcc --version
echo "---------------------------------------- "
echo "which python"
which python
python --version
echo "---------------------------------------- "
echo "which cmake"
which cmake
cmake --version
echo "---------------------------------------- "
which "xrootd"
which xrootd
xrootd -v 
echo "---------------------------------------- "

export location="root://fndca1.fnal.gov:1094/pnfs/fnal.gov/usr/minerva/persistent/DataPreservation/p6/p6PrimeData/Merged_data_ana_me5A_DualVertex_P6Prime13FebDSECalFix/MasterAnaDev_data_AnaTuple_run00019500_Playlist.root"

echo "location: $location"
echo "---------------------------------------- "
echo "test root"

export pointer=`root -b -q $location`
echo "pointer: $pointer"

#spack find --loaded



