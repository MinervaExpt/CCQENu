import sys,os,time


playlists = ["5A","6A","6B","6C","6D","6E","6F","6G","6H","6I","6J"]
list = '_'.join(playlists)
newdir = "../make_hists/hms/"
template = os.path.join(newdir,"AntiNu_v9_Template.json")

prescale = "1000"
#ofile = TFile.Open(list+".root",'RECREATE')
potdata ={}
potmc = {}
potcorr = {}
potmctot = {}
count = 0
filename = template

for play in playlists:
  f = open(filename,'r')
  newfilename = template.replace("Template",play)
  print (filename,newfilename)
  f_new = open(newfilename,'w')
  lines = f.readlines()
  for line in lines:
    line = line.replace("Template",play)
    f_new.write(line)
  f_new.close()
  f.close()
  
  
    
      
      
    
  
  
  
