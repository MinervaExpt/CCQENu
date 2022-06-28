Naming convention for CCQEMAT histograms

h___Sample___category___variable___type

fields are separated by ___   3 _

field 1 is h or h2d

field 2 is the reconstruction level Sample name (capitalized)

field 3 is the truth level category (lower case)

field 4 is the variable, if 2D it is var1_var2

field 5 is the data type:

reconstructed – for raw reconstruction
fitted – after sideband fits
weighted – if signal fraction weights applied
response_migration, response_reco, response_truth – for response
selected_truth for truth that reconstructed cuts
truth for all truth in the true fiducial volume 


