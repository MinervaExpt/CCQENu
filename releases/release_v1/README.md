This directory contains csv files for the MINERvA anti-neutrino CCQE-like measurements
There are two subdirectories:

- **fixed** is fixed format cross section scaled by 1E39
- **full** is full double precision

data and model files are stored as follows

filenames are:

MINERvA_AntiNeutrino_CCQElike_VAR_TYPE_MODEL_CONTENT_DIM.csv

**VAR** can be Enu, EnuQE, q2, pzmu, ptmu or pzmu_ptmu

**TYPE** can be Data or MC

**MODEL** refers to the GENIE2.12.6 variation:

- GENIE2.12.6 = default GENIE
- 2p2h = replaces the GENIE RPA with our tuned 2p2h
- rpa = adds RPA
- piontune = adds pion tune (negligible  effect)
- MINERvA_v1 = MINERvA v1 tune (used for extraction)
- MINERvA_v2 = MINERvA v2 tune
- Meas is for data

**CONTENT** can be:

- meta, some description of the files, including scaling, binwidth corrections... 
- values, the cross section values - in the Fixed directory these are scaled by 1E39.
- bins, the bins, low edges are listed with the last # being the high end of the last bin 
- staterrors, statistical errors
- systerrors, systematic errors
- errors, combined statistical and systematic
- covariance, the full covariance matrix
- correlation, the full correlation matrix
- vertdump, a dump of all the separate fractional uncertainties due to individual sources

**DIM** can be:

- px_1d  the px and py are there because these are projections of 2-d histograms
- py_1d
- 2d  

In the 2d files, the ordering is column is increasing x-view (pzmu), row is increasing y-view (ptmu).    
In the covariance and correlation matrix the ordering is pzbin + ptbin*(Npzbin)
