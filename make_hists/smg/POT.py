import os,sys
import ROOT
from POTCounter import POTCounter

temp = POTCounter()
#fChain = ROOT.TChain("Meta")
#temp.Init(playlist, fChain)
#mc_playlist = "/home/sean/Minerva/data/playlists/local/minervame1N_p4_MC.txt"
#data_playlist = "/home/sean/Minerva/data/playlists/local/minervame1N_p4_Data.txt"

playlists = ["A","B","C","D","E","F","G","L","M","N","O","P"]
#playlists = ["M"]
pots = {}

mc_pot_sum = 0
data_pot_sum = 0

for let in playlists:
	mc_playlist = "/exp/minerva/app/users/gilligan/minerva/CCQENu/make_hists/playlists/remote_open/MediumEnergy_FHC_StandardMC_Playlist1"+let+".txt"
	data_playlist = "/exp/minerva/app/users/gilligan/minerva/CCQENu/make_hists/playlists/remote_open/MediumEnergy_FHC_Data_Playlist1"+let+".txt"

	mcfile = mc_playlist.split("/")
	datafile = data_playlist.split("/")

	x_mc = temp.get_pot_from_playlist(mc_playlist, False, -1 ,False)
	x_data = temp.get_pot_from_playlist(data_playlist, False, -1 ,False)

	mc_pot_sum = mc_pot_sum+x_mc
	data_pot_sum = data_pot_sum+x_data

	pots[let] = [x_data,x_mc,x_data/x_mc]

ratio_avg = data_pot_sum/mc_pot_sum

print(".------.------------------------.------------------------.---------------------.---------------------.")
print(": ME1_ : Data POT               : MC POT                 : Ratio               : Weight              :")
print(":------:------------------------:------------------------:---------------------:---------------------:")
for let in playlists:
	print(":   ",let,"  : ",pots[let][0]," : ",pots[let][1]," : ",pots[let][2]," : ",pots[let][2]/ratio_avg,"  :",sep="")
print("'------'------------------------'------------------------'---------------------'---------------------'")

print("\\begin{center}")
print("\\begin{tabular}{|c | l | l | l | l |} ")
print("\hline")
print("ME1\_ & Data POT & MC POT & Data:MC Ratio ($r_i$) & Weight ($w_i$) \\")
print("\hline\hline")
print(":------:------------------------:------------------------:---------------------:---------------------:")
for let in playlists:
	print(let," & ",pots[let][0]," & ",pots[let][1]," & ",pots[let][2]," & ",pots[let][2]/ratio_avg," \\",sep="")
print("\hline\hline")
print("Total & ",data_pot_sum," & ",mc_pot_sum," & ",ratio_avg," \\",sep="")
print("\hline")
print("\end{tabular}")
print("\end{center}")

#print(mcfile[len(mcfile)-1].split(".")[0],": ",x_mc,sep="")
#print(datafile[len(datafile)-1].split(".")[0],": ",x_data,sep="")
#print("Ratio: ",x_data/x_mc,sep="")
#print(datafile[len(datafile)-1].split(".")[0],x_data)
#print("Ratio:",x_data/x_mc)
