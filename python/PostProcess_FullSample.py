import sys, os, time
import ROOT

# from ROOT import TFile, TH1D, TH2D
from PlotUtils import MnvH1D, MnvH2D

ROOT.TH1.AddDirectory(ROOT.kFALSE)


base_playlists = ["5A", "6A", "6B", "6C", "6D", "6E", "6F", "6G", "6H", "6I", "6J"]
template = sys.argv[1]
prescale = "1000"
potdata = {}
potmc = {}
potcorr = {}
potmctot = {}
count = 0

templatepath = os.path.dirname(template)

if templatepath != "":
    dir_list = os.listdir(templatepath)
else:
    dir_list = os.listdir()
playlists = []
for play in base_playlists:
    for file_name in dir_list:
        playname = "minervame" + play
        if playname in file_name and playname not in playlists:
            print(file_name)
            playlists.append(play)
        # elif playname in playlists:
        #     print("Duplicate file for playlist",playname,":",file_name)


list = "_".join(playlists)
# First find the list of hists that are in each playlist
# Check the first template file (should be the 5A one) to get a list of hists
f_template = ROOT.TFile.Open(template, "READONLY")
template_keys = f_template.GetListOfKeys()

# misc is things like pot, configs, etc
key_dir = {"misc": [], "hists": []}
for key in template_keys:
    keyname = key.GetName()
    if "___" not in keyname:
        key_dir["misc"].append(keyname)
        # print("template_key_dir added ", keyname, " to 'misc'")
    else:
        key_dir["hists"].append(keyname)
        # print("hists.append(",keyname, ")")

# print("Template list includes")
# for name in key_dir["hists"]:
#     print(name)

# f_template.Close()
file_dict = {"5A": f_template}
# Now lets check if that hist is in every playlist, ignoring the misc hists. Also make a collection of all the files
for play in playlists:
    tmp_filename = template.replace("5A", play)
    print("Looking at file ", tmp_filename)
    f_play_tmp = ROOT.TFile.Open(tmp_filename, "READONLY")
    tmp_keys = f_play_tmp.GetListOfKeys()
    tmp_found_dict = {}
    # Make a found list, default to false
    for histname in key_dir["hists"]:
        tmp_found_dict[histname] = False

    for key in tmp_keys:
        keyname = key.GetName()
        # don't worry about the non-hist objects, those will all get added for each playlist
        if "___" not in keyname:
            # print("___ not in ", keyname)
            continue
        # Skip hists that aren't already in the list, since these aren't in all the playlists
        if keyname not in key_dir["hists"]:
            # print("Hist ", keyname, " in playlist ", play, " not in key_dir, skipping...")
            continue
        # If it is in the list, mark it as found
        else:
            tmp_found_dict[keyname] = True
    # Now remove any thing that wasn't found yet...
    # print("tmp_found_dict", tmp_found_dict.keys())
    for found_key in tmp_found_dict.keys():
        if not tmp_found_dict[found_key]:
            # print("Coundn't find ", found_key, "from key_dir in playlist ", play, ", removing from key_dir...")
            key_dir["hists"].remove(found_key)

    # f_play_tmp.Close()
    file_dict[play] = f_play_tmp


print("Will combine the following hists:")
for name in key_dir["hists"]:
    print("\t", name)


# Now start combining the hists

# structure of these dicts will be "<name written to file>": <object>
out_misc_dict = {}
tot_h_POT = ROOT.TH1D()
tot_potdata = 0.0
tot_potmctot = 0.0
tot_potmc = 0.0

# Global total for all ME RHC playlists
global_tot_datapot = 1.2e21


for play in playlists:
    print("starting on playlist", play)
    tmp_filename = template.replace("5A", play)
    # print("    Looking at file ", tmp_filename)
    # f_play_tmp = ROOT.TFile.Open(tmp_filename, "READONLY")
    # print("after open")

    file_dict[play].cd()

    # Make copies of all the playlist specific config and misc files
    # for key in f_play_tmp.GetListOfKeys():
    for key in file_dict[play].GetListOfKeys():
        keyname = key.GetName()
        if "___" not in keyname:
            # this will be the new name for the object for this playlist
            new_keyname = keyname + "_" + play
            # out_misc_dict[new_keyname] = f_play_tmp.Get(keyname).Clone()
            out_misc_dict[new_keyname] = file_dict[play].Get(keyname).Clone()

    # Get the POT info
    # h_POT = f_play_tmp.Get("POT_summary")
    h_POT = file_dict[play].Get("POT_summary")
    potdata[play] = h_POT.GetBinContent(1)
    potmctot[play] = h_POT.GetBinContent(2)
    potmc[play] = h_POT.GetBinContent(3)
    potcorr[play] = potdata[play] / potmc[play]

    tot_potdata += potdata[play]
    tot_potmctot += potmctot[play]
    tot_potmc += potmc[play]

    # Make a total POT hist
    if play == playlists[0]:
        tot_h_POT = h_POT.Clone()
    else:
        tot_h_POT.Add(h_POT)

print("Total combined data pot: ", tot_potdata)
print("Total combined mctot pot: ", tot_potmctot)
print("Total combined mc pot: ", tot_potmc)

scaled_comb_hist_dict = {}
combined_hist_dict = {}
global_scaled_comb_hist_dict = {}
for play in playlists:
    print("Total Sample Data POT scale: ", global_tot_datapot / potmc[play])
    for histname in key_dir["hists"]:
        # print("histname ", histname)

        # tmp_hist = f_play_tmp.Get(histname).Clone(histname+"_noPOTscale")
        tmp_hist = file_dict[play].Get(histname).Clone(histname)

        # If it's the first one, just make the base hist
        if play == playlists[0]:
            # If it's data, don't POT scale it
            if "data" in histname:
                scaled_comb_hist_dict[histname] = tmp_hist.Clone()
                combined_hist_dict[histname] = tmp_hist.Clone()
                global_scaled_comb_hist_dict[histname] = tmp_hist.Clone()
                continue
            # TODO: If it's migration, make an unscaled copy? not sure if makes sense...
            if "migration" in histname:
                scaled_comb_hist_dict[histname + "_noPOTscale"] = tmp_hist.Clone(
                    histname + "_noPOTscale"
                )
                global_scaled_comb_hist_dict[histname + "_noPOTscale"] = tmp_hist.Clone(
                    histname + "_noPOTscale"
                )
            # Scale all mc hists
            combined_hist_dict[histname + "_noPOTscale"] = tmp_hist.Clone(
                histname + "_noPOTscale"
            )
            scaled_tmphist = tmp_hist.Clone(histname)
            scaled_tmphist.Scale(potcorr[play])
            scaled_comb_hist_dict[histname] = scaled_tmphist
            global_scaled_tmphist = tmp_hist.Clone(histname)
            global_scaled_tmphist.Scale(
                potcorr[play] * global_tot_datapot / tot_potdata
            )
            global_scaled_comb_hist_dict[histname] = global_scaled_tmphist
        # do the same all the other playlists and add them to the first
        else:
            if "data" in histname:
                # scaled_comb_hist_dict[histname] =
                scaled_comb_hist_dict[histname].Add(tmp_hist)
                # combined_hist_dict[histname] =
                combined_hist_dict[histname].Add(tmp_hist)
                # global_scaled_comb_hist_dict[histname] =
                global_scaled_comb_hist_dict[histname].Add(tmp_hist)
                continue

            if "migration" in histname:
                # scaled_comb_hist_dict[histname + "_noPOTscale"] =
                scaled_comb_hist_dict[histname + "_noPOTscale"].Add(tmp_hist)
                # global_scaled_comb_hist_dict[histname + "_noPOTscale"] =
                global_scaled_comb_hist_dict[histname + "_noPOTscale"].Add(tmp_hist)

            # combined_hist_dict[histname + "_noPOTscale"] =
            combined_hist_dict[histname + "_noPOTscale"].Add(tmp_hist)
            scaled_tmphist = tmp_hist.Clone()
            scaled_tmphist.Scale(potcorr[play])
            # scaled_comb_hist_dict[histname] =
            scaled_comb_hist_dict[histname].Add(scaled_tmphist)
            global_scaled_tmphist = tmp_hist.Clone(histname)
            global_scaled_tmphist.Scale(
                potcorr[play] * global_tot_datapot / tot_potdata
            )
            # global_scaled_comb_hist_dict[histname] =
            global_scaled_comb_hist_dict[histname].Add(global_scaled_tmphist)
    print("    done with this playlist ", play)

# Make a new file to write out everything. It'll include the combined hists,
filename = template.replace("5A", "Combined")
filepath = os.path.dirname(filename)
outfilename = os.path.join(
    filepath, "potscaled_combined_" + list + os.path.basename(filename)
)
raw_outfilename = os.path.join(
    filepath, "combined_" + list + os.path.basename(filename)
)
globalscale_outfilename = os.path.join(
    filepath, "totaldatapotscaled_combined_" + list + os.path.basename(filename)
)
f_out = ROOT.TFile.Open(outfilename, "RECREATE")
f_out_raw = ROOT.TFile.Open(raw_outfilename, "RECREATE")
f_out_global = ROOT.TFile.Open(globalscale_outfilename, "RECREATE")

print("writing out misc files...")
for key in out_misc_dict.keys():
    f_out.cd()
    f_out.WriteTObject(out_misc_dict[key], key)
    f_out_raw.cd()
    f_out_raw.WriteTObject(out_misc_dict[key], key)
    f_out_global.cd()
    f_out_global.WriteTObject(out_misc_dict[key], key)
    # print("\t",key," written to file")

f_out.cd()
f_out.WriteTObject(tot_h_POT, "Combined_POT_Summary")
f_out_raw.cd()
f_out_raw.WriteTObject(tot_h_POT, "Combined_POT_Summary")
f_out_global.cd()
f_out_global.WriteTObject(tot_h_POT, "Combined_POT_Summary")

# print("\t Combined_POT_Summary written to file")

for key in scaled_comb_hist_dict.keys():
    f_out.cd()
    f_out.WriteTObject(scaled_comb_hist_dict[key], key)
for key in combined_hist_dict.keys():
    f_out_raw.cd()
    f_out_raw.WriteTObject(combined_hist_dict[key], key)
for key in global_scaled_comb_hist_dict.keys():
    f_out_global.cd()
    f_out_global.WriteTObject(global_scaled_comb_hist_dict[key], key)

    # print("\t",key," written to file")
# for key in combined_hist_dict.keys():

print("Done writing POTscaled to file ", outfilename)
print("Done writing non-POTscaled to file ", raw_outfilename)
print("Done writing total data POTscaled to file ", globalscale_outfilename)
