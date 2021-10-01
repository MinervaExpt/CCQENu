# CCQENUMAT - MAT implementation of CCCQENU

This repository contains the MAT hist creation and analysis codes

utilities/ useful utililties for analysis

here is how to build CCQEMAT using the new MAT

setup root, CVSROOT and get the MAT code installed using the documentation in [github.com/MinervaExpt/MAT-MINERvA](https://github.com/MinervaExpt/MAT-MINERvA)

pro tip - if you do this multiple times, you might want to 
```
  cd opt
  ln -s $OLDMATINSTALL/opt/etc $WHEREMATPUTISITCODE/opt/etc 
  ```
that avoids duplicating 2GB of files locally

then... 

```
export WHEREMATPUTSITSCODE=<directory where MAT code is> 
source $WHEREMATPUTSITSCODE/opt/build/setup.sh

# now get the CCQEMAT code out of CVS
cd $WHEREMATPUTSITSCODE
export WHEREIPUTMYCODE=$WHEREMATPUTSITSCODE
cvs co Ana/PickledCCQENu
export CCQEMAT=$WHEREIPUTMYCODE/Ana/PickledCCQENu/ana/make_hists

cd $CCQEMAT
# I haven't figured out how to do Andrew style builds yet so this builds on the source directory. But there is a MAT compatible cmake now.  

cmake mat  
make
```

Note -  you can find how to modify an old cmake file to this setup by doing  diff build/CMakelist.txt mat/CMakelist.txt
