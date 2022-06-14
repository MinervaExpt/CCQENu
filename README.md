# CCQENUMAT - MAT implementation of CCCQENU

This repository will contain the MAT hist creation and analysis codes

utilities/ useful utililties for analysis

here is how to build CCQEMAT using the new MAT

setup root, CVSROOT and get the MAT code installed using the documentation in [github.com/MinervaExpt/MAT-MINERvA](https://github.com/MinervaExpt/MAT-MINERvA)

pro tip - if you are not on a machine with cvmfs, find a place to put flux and weight files and add 

` -DFLUX_FILE_DIR=<location of flux files>` to your cmake command

that avoids duplicating 2GB of files locally

then... 

```
export WHEREMIPUTMYCODE=<directory where MAT code is> 
source $WHEREIPUTMYCODE/opt/build/setup.sh

# now get the CCQEMAT code
cd $WHEREMIPUTMYCODE
git clone https://github.com/MinervaExpt/CCQENu

export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists

# on mac's you need to:

export DYLD_LIBRARY_PATH=${PLOTUTILSROOT}

or 

source $CCQEMAT/setup_osx.sh #on osx

source $CCQEMAT/setup_unx.sh #on unix

If you get json related errors install jsoncpp on your machine or on fnal machines.  I think you can get this with conda or on fnal Machines by doing. 

export JSONCPP_DIR=/minerva/app/users/schellma/LocalApps/jsoncpp-build

cd $CCQEMAT
# I haven't figured out how to do Andrew style builds yet so this builds on the source directory. But there is a MAT compatible cmake now.  



cmake v_08 # for the new version 8 with multiple signal components for Sean

cmake fits # adds in independent code that can do fits for backgrounds across multiple sample
```
then type make

The code now supports using environmentals to set values in json files so you can have one file which then has ${MYPLAYLIST} to switch among playlists

And the utilities directory now has scripts that support running on the grid. 

