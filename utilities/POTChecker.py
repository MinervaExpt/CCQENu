# POTChecker.py

import os,sys
from ROOT import TFile, TTree

playlists = ["5A","6A","6B","6C","6D","6E","6F","6G","6H","6I","6J"]

playlistpath = "/pnfs/minerva/persistent/DataPreservation/pXX/Data"
playlistpath = "/Users/schellma/Dropbox/newpub/CCQENu/make_hists/playlists/local_p6/"

for version in ["6","8","9"]:
    playlistpath = playlistpath.replace("XX",version)
    
    POT = {"POT_Used":{},"POT_Total":{},"Total_Rec":{}}
    for play in playlists:
        #print ("Playlist is:", play)
        name = os.path.join(playlistpath,f"P{version}_Playlist{play}_Data.txt")
        
        if not os.path.exists(name):
            #print (" no such playlist",name)
            continue
        files = open(name,'r').readlines()
        
        POT["POT_Used"][play] = 0.0
        POT["POT_Total"][play] = 0.0
        POT["Total_Rec"][play] = 0.0
        for file in files:
            f = TFile.Open(file.strip(),"READONLY")
            t = f.Get("Meta")
            #t.Scan()
            for entry in t:
                POT["POT_Used"][play] += entry.POT_Used
                POT["POT_Total"][play] += entry.POT_Total
                #POT["Total_Rec"][play] += entry.Total_Rec
            
        print (f"P{version} {play} POT_Used: {POT["POT_Used"][play]}, POT_Total: {POT["POT_Total"][play]}, TotalRec: {POT["Total_Rec"][play]}" )