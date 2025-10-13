import os,sys
import ROOT
from POTCounter import POTCounter

temp = POTCounter()
#fChain = ROOT.TChain("Meta")
#temp.Init(playlist, fChain)
playlist = "/Users/schellma/Dropbox/newForge/CCQENu/make_hists/playlists/local_p6/minervame5A_Data.txt"
f = open(playlist,'r')


x = temp.get_pot_from_playlist(playlist, False, -1 , False)
print (playlist,x)