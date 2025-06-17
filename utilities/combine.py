import sys,os,time
from ROOT import TFile, TH1D, TH2D
from PlotUtils import MnvH1D, MnvH2D

playlists = ["5A","6A","6B","6C","6D","6E","6F","6G","6H","6I","6J"]
list = '_'.join(playlists)
template = sys.argv[1]
prescale = "1000"
#ofile = TFile.Open(list+".root",'RECREATE')
potdata ={}
potmc = {}
potcorr = {}
potmctot = {}
count = 0

for play in playlists:
  count += 1
  filename = template.replace("5A",play)
  filepath  = os.path.dirname(filename)
  print ("filename = ", filename)
  newfilename = os.path.join(filepath,"scaled_"+os.path.basename(filename))
  print ("newfilename",newfilename)
  f_out = TFile.Open(newfilename,"RECREATE")
  f_root = TFile.Open(filename,'READONLY')
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
    keys[name]=f_root.Get(name)
    if "data" in name or "POT" in name or ("h__" not in name and "h2D" not in name):
      f_out.cd()
      keys[name].Write()
      keys[name].Print()
    else:
      keys[name].Scale(potcorr[play])
      f_out.cd()
      keys[name].Write()
      keys[name].Print()
    f_root.cd()
  f_root.Close()
  f_out.Close()
  
    
      
      
    
  
  
  
