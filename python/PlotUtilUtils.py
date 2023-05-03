import PlotUtils

def makeChainWrapper(playlist=None, name="CCQENu"):

    chw =  PlotUtils.ChainWrapper(name);
    nfiles = chw.Add(playlist);
    
    print ("Added " , nfiles , " files from playlist " , playlist )
    
    return chw;

#def __main__():

x = makeChainWrapper("/Users/schellma/data/playlists/MC/CCQENu_mc_AnaTuple_run00123010.root","CCQENu")
print ("I got here")
print (x.GetInt("mc_subrun",11))
