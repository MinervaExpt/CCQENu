import sys,os,string

# attempt at translation code.

from ROOT import *
from PlotUtils import *

sampletypes = ["QElike","QElikeNP","QElikeALL"]

f = TFile.Open(sys.argv[1],"READONLY")

keys = []

response1D = {}
hists1D = {}
response2D = {}
hists2D = {}

samples = []
categories = []
variables = []
types = []
fsamples = {}

listofkeys = f.GetListOfKeys()

if f:

  for k in listofkeys:
    keys.append(k.GetName());
    key = k.GetName();
    if "___" in key:
      continue
    #. see if 1 or 2 D  -- this is for 1 D
    print( " key " ,  k.GetName())
    parsekey = []
    
    parsekey = key.split("_")
    if (len(parsekey)< 4):
      print (" not parseable " , key)
      continue;
    
    hNd = parsekey[0];
    sample = parsekey[1];
    #category = parsekey[2];
    variable = parsekey[2];
    type = "_".join(parsekey[3:])
    

    # build lists of all valid tags
    
    if (sample not in hists1D):
      fsamples[sample] = TFile.Open(sample+".root","RECREATE")
      samples.append(sample)
      hists1D[sample]={}
      hists2D[sample]={}
      print (" add a sample: " , sample )
    
#    if (category not in categories):
#      categories.append(category);
#      hists1D[sample]={}
#      hists2D[sample]={}
#
#      print ( " add a category: " , category )
    
    if (variable not in hists1D[sample]):
      variables.append(variable)
      hists1D[sample][variable]={}
      hists2D[sample][variable]={}
      print ( " add a variable: " , sample, variable )
    
    if (type not in types):
      types.append(type);
      print ( " add a type: " , type )
    
    
    #. get the histogram
    me = MnvH1D()
    me = f.GetKey(key);
    print ( " Done with parsing" )
    print (key)
    print (variables)
    print (samples)
    print (types)
   
    print (sample,variable,type)

    #. 1D hists
    if("h2D" not in key):
      #. if response in name its a 2D so do a cast to MnvH2D
      if("response" in key):
        continue
              
      
      #. it's normal so it's a 1D.
      else:
        print (key)
        temp = f.Get(key)
        if (temp != 0):
          hists1D[sample][variable][type] = temp.Clone();
          hists1D[sample][variable][type].Print();
          hists1D[sample][variable][type].SetDirectory(0);
          fsamples[sample].cd()
          newname = key.replace("_"+sample,"")
          hists1D[sample][variable][type].SetName(newname)
          hists1D[sample][variable][type].Write()
          print ( " hist 1D " , sample , " " , variable , " " , type )
         # delete temp;
        
        else:
          print ( "could not read " , key )
          hists1D[sample][variable][type]=0;
        
      
    
    
    #. 2D hists
    if(hNd == "h2D" or "h2D" in key):
      continue
      partsof2D = variable.split("_");
      hist = (f.Get(key));
      #. Check if response is in its name
      if (hist != 0):
        if("response" in key):
          continue
          response2D[sample][variable][type] = hist.Clone();
          response2D[sample][variable][type].Print();
          response2D[sample][variable][type].SetDirectory(0);
          print ( " 2D response " , sample , " " , variable , " " , type  )
          #delete hist;
        
        else:
          hists2D[sample][variable][type] = hist.Clone();
          hists2D[sample][variable][type].Print();
          hists2D[sample][variable][type].SetDirectory(0);
          print ( " hist 2D " , sample , " " , variable , " " , type  )
          #delete hist;
        
      
      else:
        print ( "could not read " , key )
        if("respone" in key):
          response2D[sample][variable][type]=0;
        
        else:
          hists2D[sample][variable][type]=0;
        
for sample in fsamples:
  
  sample.Close()
    
  
