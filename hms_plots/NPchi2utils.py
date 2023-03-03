from ROOT import *
import numpy as np


ld = np.float64


def NPreadData(h_data,diag=False):
  
  # returns a transposed list
  
  size = h_data.GetNbinsX()*h_data.GetNbinsY()
  compact = []
  
  npt = h_data.GetNbinsY()+2
  npz = h_data.GetNbinsX()+2
  
  ibin = 0
  for  iy in range(1,npt-1):
    for  ix  in range(1,npz-1):
        compact.append(h_data.GetBinContent(ix,iy))
        ibin += 1

  return np.array(compact,dtype=ld)
  
def NPreadErrors(h_data,diag=False):
 
 # returns a transposed list
 
 size = h_data.GetNbinsX()*h_data.GetNbinsY()
 compact = []

 npt = h_data.GetNbinsY()+2
 npz = h_data.GetNbinsX()+2
 
 ibin = 0
 for  iy in range(1,npt-1):
   for  ix  in range(1,npz-1):
       compact.append(h_data.GetBinError(ix,iy))
       ibin += 1

 return np.array(compact,dtype=ld);

def NPreadData1D(h_data,diag=False):
  
 
  
  size = h_data.GetNbinsX()
  compact = []
  
  npz = h_data.GetNbinsX()+2
  
  ibin = 0
  
  for  ix  in range(1,npz-1):
      compact.append(h_data.GetBinContent(ix))
      ibin += 1

  return np.array(compact,dtype=ld)
  
def NPreadErrors1D(h_data,diag=False):

# returns a transposed list

  size = h_data.GetNbinsX()
  compact = []

  npz = h_data.GetNbinsX()+2

  ibin = 0

  for  ix  in range(1,npz-1):
    compact.append(h_data.GetBinError(ix))
    ibin += 1

  return np.array(compact,dtype=ld)

def NPreadMatrix(covmx, h_data, diag= False,log = False):
  
  npz = h_data.GetNbinsX()+2
  npt = h_data.GetNbinsY()+2
  
  size = (npt-2)*(npz-2)
  
  compact = TMatrixD(size,size);
  ixx = -1;
  compact = []
  for  ix in range(npz, (npz)*(npt-1)):
    
    if(  ix%(npz) == 0 or ix%(npz) ==npz-1):
      continue;
    inner = []
    ixx += 1
    iyy = -1;
    for  iy  in range(npz, (npz)*(npt-1)):
      if ( iy%(npz) == 0 or iy%(npz) == npz-1):
        continue;
    
      iyy += 1
      
     
      if not log:
        inner.append(covmx[ix][iy])
      else:
        inner.append(covmx[ix][iy])
      
      if (diag and ixx!=iyy):
        inner.append(covmx[ix][iy])
      # special to deal with completely empty bins
    compact.append(inner)
  
  return np.asmatrix(compact)

def NPreadMatrix1D(covmx, h_data, diag= False,log = False):
  print ("READMATRIX")
  #covmx.
 
  npz = h_data.GetNbinsX()+2
 
  size = (npz-2)
  
  compact = [] ;
  ixx = -1;
  for  ix in range(1,npz-1):
    ixx = ix -1
    inner = []
    for  iy  in range(1,npz-1):
      iyy = iy -1
      
      
      inner.append(covmx[ix][iy])
    compact.append(inner)

  print ("NPreadMatrix1D",np.asmatrix(compact))
  return np.asmatrix(compact)
 
  
def NPcompressVector(v,e):

  tnew = []
  print ("e is ",e,v)
  for i in e:
    tnew.append(v[e[i]])
  return np.array(tnew,dtype=ld)

def NPcompressMatrix(v,e):
   
  tnew = np.zeros(shape=(len(e),len(e)),dtype=ld)
  for i in e:
    for j in e:
      tnew[i][j] = v.item((e[i],e[j]))
    
  print (type(tnew))
  return tnew

