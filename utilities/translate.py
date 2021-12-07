import sys,os,string
from ROOT import *
from PlotUtils import *

sampletypes = ["QElike","QElikeNP","QElikeALL"]

f = TFile.Open(sys.argv[1])

keys = []

response1D = {}
hists1D = {}
response2D = {}
hists2D = {}

samples = []
categories = []
variables = []
types = []

listofkeys = f.GetListOfKeys()

if f:

  for k in listofkeys:
    keys.append(k.GetName());
    key = k.GetName();
    #. see if 1 or 2 D  -- this is for 1 D
    print( " key " ,  k.GetName())
    parsekey = []
    
    parsekey = key.split("___")
    if (len(parsekey)< 4):
      print (" not parseable " , key)
      continue;
    
    hNd = parsekey[0];
    sample = parsekey[1];
    category = parsekey[2];
    variable = parsekey[3];
    type = parsekey[4];

    # build lists of all valid tags

    if (sample not in samples):
      samples.append(sample);
      hists1D[sample]={}
      hists2D[sample]={}
      print (" add a sample: " , sample )
    
    if (category not in categories):
      categories.append(category);
      hists1D[sample][category]={}
      hists2D[sample][category]={}
 
      print ( " add a category: " , category )
    
    if (variable not in variables):
      variables.append(variable);
      hists1D[sample][category][variable]={}
      hists2D[sample][category][variable]={}
      print ( " add a variable: " , variable )
    
    if (type not in types):
      types.append(type);
      print ( " add a type: " , type )
    
    #. get the histogram
    me = MnvH1D()
    me = f.GetKey(key);
    print ( " Done with parsing" )

    #. 1D hists
    if("h2D" not in key):
      #. if response in name its a 2D so do a cast to MnvH2D
      if("response" in key):
        continue
        hist = f.Get(key);
        if (hist != 0):
          response1D[sample][variable][type][category] = hist.Clone();
          response1D[sample][variable][type][category].Print();
          response1D[sample][variable][type][category].SetDirectory(0);
          print ( " response " , sample , " " , variable , " " , type , " " , category )
          #delete hist;
        
        else:
          print ( "could not read " , key )
          response1D[sample][variable][type][category]=0;
        
      
      #. it's normal so it's a 1D.
      else:
        print (key)
        temp = f.Get(key)
        if (temp != 0):
          hists1D[sample][variable][type][category] = temp.Clone();
          hists1D[sample][variable][type][category].Print();
          hists1D[sample][variable][type][category].SetDirectory(0);
          print ( " hist 1D " , sample , " " , variable , " " , type , " " , category )
         # delete temp;
        
        else:
          print ( "could not read " , key )
          hists1D[sample][variable][type][category]=0;
        
      
    

    #. 2D hists
    if(hNd == "h2D" or "h2D" in key):
      
      partsof2D = variable.split("_");
      hist = (f.Get(key));
      #. Check if response is in its name
      if (hist != 0):
        if("response" in key):
          continue
          response2D[sample][variable][type][category] = hist.Clone();
          response2D[sample][variable][type][category].Print();
          response2D[sample][variable][type][category].SetDirectory(0);
          print ( " 2D response " , sample , " " , variable , " " , type , " " , category )
          #delete hist;
        
        else:
          hists2D[sample][variable][type][category] = hist.Clone();
          hists2D[sample][variable][type][category].Print();
          hists2D[sample][variable][type][category].SetDirectory(0);
          print ( " hist 2D " , sample , " " , variable , " " , type , " " , category )
          #delete hist;
        
      
      else:
        print ( "could not read " , key )
        if("respone" in key):
          response2D[sample][variable][type][category]=0;
        
        else:
          hists2D[sample][variable][type][category]=0;
        
      
    
  
