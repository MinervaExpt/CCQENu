import sys,os,time
from ROOT import TFile, TH1D, TH2D
from PlotUtils import MnvH1D, MnvH2D

DEBUG=False
samples = ["QElike","BlobSideband","MichelSideBand","MicBlobSideBand"]
playlists = ["1A","1B","1C","1D","1E","1F","1G","1L","1M","1N","1O","1P"]
list = '_'.join(playlists)
template = "1B_MnvTunev2_QElike_1Track_Nu_p8_run_1.root"
if len(sys.argv) > 1: 
  template = sys.argv[1]
prescale = "1000"
#ofile = TFile.Open(list+".root",'RECREATE')
potdata ={}
potmc = {}
potcorr = {}
potmctot = {}
count = 0
tracks = ["1Track","2Track"]


for play in playlists:
  for track in tracks:
    #for sample in samples:
      thefilename = template.replace("1B",play).replace("1Track",track)#.replace("QElike",sample)
      if not os.path.exists(thefilename): continue
      filepath  = os.path.dirname(thefilename)
      if not os.path.exists("scaled"):
        os.mkdir("scaled")
      newfilename = os.path.join(filepath,"scaled","scaled_"+os.path.basename(thefilename)).replace("QElike","All")
      if os.path.exists(newfilename):
        print (thefilename,"already exists, skipping")
        continue
      f_out = TFile.Open(newfilename,"RECREATE")
      print ("newfilename",newfilename)
      for sample in samples:
        count += 1
        filename = thefilename.replace("QElike",sample)
        print ("filename = ", filename)
        if not os.path.exists(filename): 
          sys.exit(0)
        
        #newfilename = os.path.join(filepath,"scaled_"+os.path.basename(filename))
        #print ("newfilename",newfilename)
        
        f_root = TFile.Open(filename,'READONLY')

        if not f_root: continue
        
        
        h_POT = f_root.Get("POT_summary")
        h_POT.Print("ALL")
        potdata[play] = h_POT.GetBinContent(1)
        potmctot[play] = h_POT.GetBinContent(2)
        potmc[play] = h_POT.GetBinContent(3)
        potcorr[play] = potdata[play]/potmc[play]
        h_POT.SetBinContent(2,h_POT.GetBinContent(2)*potcorr[play])
        h_POT.SetBinContent(3,h_POT.GetBinContent(3)*potcorr[play])
        print ("file ", filename, " had ",potdata[play],potmc[play]," pot")
        keys = {}
        keylist = f_root.GetListOfKeys();
        for k in keylist:
          name = k.GetName()
          if "types" in name: continue
          keys[name]=f_root.Get(name)
          if "data" in name or "POT" in name or ("h__" not in name and "h2D" not in name):
            f_out.cd()
            keys[name].Write()
            if DEBUG: keys[name].Print()
          else:
            keys[name].Scale(potcorr[play])
            f_out.cd()
            keys[name].Write()
            if DEBUG: keys[name].Print()
          f_root.cd()
        f_root.Close()
      f_out.Close()
  
    
      
      
    
  
  
  
