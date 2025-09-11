import os,sys
import ROOT
from POTCounter import POTCounter

temp = POTCounter()
#fChain = ROOT.TChain("Meta")
#temp.Init(playlist, fChain)
mc_playlist = "/home/sean/Minerva/data/playlists/local/minervame1N_p4_MC.txt"
data_playlist = "/home/sean/Minerva/data/playlists/local/minervame1N_p4_Data.txt"

mcfile = mc_playlist.split("/")
datafile = data_playlist.split("/")

x_mc = temp.get_pot_from_playlist(mc_playlist, False, -1 ,False)
x_data = temp.get_pot_from_playlist(data_playlist, False, -1 ,False)


print(mcfile[len(mcfile)-1].split(".")[0],": ",x_mc," - ",datafile[len(datafile)-1].split(".")[0],": ",x_data," - Ratio: ",x_data/x_mc,sep="")
#print(datafile[len(datafile)-1].split(".")[0],x_data)
#print("Ratio:",x_data/x_mc)
