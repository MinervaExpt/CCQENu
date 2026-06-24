import sys, os, time
import ROOT

# from ROOT import TFile, TH1D, TH2D
from PlotUtils import MnvH1D, MnvH2D

ROOT.TH1.AddDirectory(ROOT.kFALSE)

# # Get file names from the arguments, these should all be in the same dir
# filenames = []
# for name in sys.argv[1::]:
#     filenames.append(name)

# basepath = os.path.dirname(filenames[0])

# This is the string it looks for preceding each file
template_string = "potscaled_combined_"
# This is the file you start with, it should be in the same dir as the other 
# files you want to stick together
template = sys.argv[1]
templatepath = os.path.dirname(template)
# This will list all the other files in the dir
dir_list = []
if templatepath != "":
    dir_list = os.listdir(templatepath)
else:
    dir_list = os.listdir()
# Get all the files
files_to_combine = []
for file_name in dir_list:
    if template_string not in file_name:
        continue
    files_to_combine.append(file_name)

out_dict = {}
for file_name in files_to_combine:
    print("Looking at file %s"%(os.path.basename(file_name)))
    with ROOT.TFile.Open(file_name, "READONLY") as tmp_file:
        keys = tmp_file.GetListOfKeys()
        for key in keys:
            name = key.GetName()
            print(key, name)
            if name in out_dict:
                print("\tAlready have %s\tSkipping..."%(name))
                continue
            print("\tStoring %s..."%(name))
            out_dict[name] = tmp_file.Get(name).Clone()
print("=-=-=-=-=-=-=-=-= Done looking through files =-=-=-=-=-=-=-=-=")
outfilename = os.path.join(templatepath, "allcategories_combined_"+os.path.basename(template))
print("Overwriting the file %s"%(os.path.basename(outfilename)))
f_out = ROOT.TFile.Open(outfilename,"RECREATE")

print("writing out all the objects")
for key in out_dict.keys():
    f_out.cd()
    f_out.WriteTObject(out_dict[key], key)
print("Done!")
print("written to ", outfilename)

