# POTChecker.py

import os,sys
from ROOT import TFile, TTree

playlists = ["5A","6A","6B","6C","6D","6E","6F","6G","6H","6I","6J"]

playlisthead = "/pnfs/minerva/persistent/DataPreservation/pXXX/Data"
#playlistpath = "/Users/schellma/Dropbox/newpub/CCQENu/make_hists/playlists/local_p6/"

POT_All_Used={}
for version in ["8","9"]:
    POT_All_Used[version] = 0     

for play in playlists:
    POT_Used = {}
    POT_Total = {}
    Total_Rec = {}
    
    for version in ["8","9"]:
        
        playlistpath = playlisthead.replace("XXX",version)
            
        name = os.path.join(playlistpath,f"P{version}_Playlist{play}_Data.txt")
        
        if not os.path.exists(name):
            print (" no such playlist",name)
            continue
        files = open(name,'r').readlines()
        
        POT_Used[version] = 0.0
        POT_Total[version] = 0.0
        Total_Rec[version] = 0.0

        for file in files:
            f = TFile.Open(file.strip(),"READONLY")
            t = f.Get("Meta")
            #t.Scan()
            for entry in t:
                POT_Used[version] += entry.POT_Used
                POT_Total[version] += entry.POT_Total
                POT_All_Used[version] += entry.POT_Used
                
                
                #Total_Rec += entry.Total_Rec
        
        print (f"P{version} {play} POT_Used: {POT_Used[version]:.6e}, POT_Total: {POT_Total[version]:.6e}, Total_Rec: {Total_Rec[version]}" )
    rat = POT_Used["9"]/POT_Used["8"]
    print (f"p9/p8 ratio {play}, {rat:.6f}")
rat = POT_All_Used["9"]/POT_All_Used["8"]
print (f"Total ratio {rat:.6f}, P9 {POT_All_Used['9']:.6e}, P8 {POT_All_Used['8']:.6e}")