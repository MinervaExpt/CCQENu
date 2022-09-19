python /Users/schellma/Dropbox/BIGMAT/MAT/test/MnvH2D_viewer.py $1.root h2D_QElike_pzmu_ptmu_bkgsub_unfold_effcorr_sigma
python /Users/schellma/Dropbox/BIGMAT/MAT/test/MnvH1D_viewer.py $1.root h_QElike_ptmu_bkgsub_unfolded_effcorr_sigma
head $1_csvdump/*ptmu*values_1d*

