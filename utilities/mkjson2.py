import sys,os,time


playlists = ["5A","6A","6B","6C","6D","6E","6F","6G","6H","6I","6J"]
list = '_'.join(playlists)
template = sys.argv[1]
if "Anti" not in templatename":
    playlists = ["1A","1B","1C","1D","1E","1F","1G","1L","1M","1N","1O","1O"]

    

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
  
  
    
      
      
    
  
  
  
