from ROOT import *
import numpy as np

def Debinwidth(h_data):
  h_nobin=h_data.Clone()
  h_nobin.SetDirectory(0)
  n = h_data.GetNbinsX()
  for i in range(0,n+1):
    wid = h_data.GetBinWidth(i)
    h_nobin.SetBinContent(i,h_data.GetBinContent(i)*wid)
    h_nobin.SetBinError(i,h_data.GetBinError(i)*wid)
  return h_nobin

def Debinwidth2(h_data):
  h_nobin=h_data.Clone()
  h_nobin.SetDirectory(0)
  n = h_data.GetNbinsX()
  m = h_data.GetNbinsY()
  for i in range(0,n+1):
    for j in range(0,m+1):
      wid1 = h_data.GetXaxis().GetBinWidth(i)
      wid2 = h_data.GetYaxis().GetBinWidth(j)
      wid = wid1*wid2
      if wid < 0:
        wid = 0
      h_nobin.SetBinContent(i,j,h_data.GetBinContent(i,j)*wid)
      h_nobin.SetBinError(i,j,h_data.GetBinError(i,j)*wid)
  return h_nobin


def readData(h_data,diag=False):
  
  # returns a transposed list
  
  size = h_data.GetNbinsX()*h_data.GetNbinsY()
  compact = TVectorD(size);
 
  npt = h_data.GetNbinsY()+2
  npz = h_data.GetNbinsX()+2
  
  ibin = 0
  for  iy in range(1,npt-1):
    for  ix  in range(1,npz-1):
        compact[ibin] = h_data.GetBinContent(ix,iy)
        ibin += 1

  return compact;
  
def readErrors(h_data,diag=False):
 
 # returns a transposed list
 
 size = h_data.GetNbinsX()*h_data.GetNbinsY()
 compact = TVectorD(size);

 npt = h_data.GetNbinsY()+2
 npz = h_data.GetNbinsX()+2
 
 ibin = 0
 for  iy in range(1,npt-1):
   for  ix  in range(1,npz-1):
       compact[ibin] = h_data.GetBinError(ix,iy)
       ibin += 1

 return compact;

def readData1D(h_data,diag=False):
  
  # returns a transposed list
  
  size = h_data.GetNbinsX()
  compact = TVectorD(size);
  
  npz = h_data.GetNbinsX()+2
  
  ibin = 0
  
  for  ix  in range(1,npz-1):
      compact[ibin] = h_data.GetBinContent(ix)
      ibin += 1

  return compact
  
def readErrors1D(h_data,diag=False):

# returns a transposed list

  size = h_data.GetNbinsX()
  compact = TVectorD(size);

  npz = h_data.GetNbinsX()+2

  ibin = 0

  for  ix  in range(1,npz-1):
    compact[ibin] = h_data.GetBinError(ix)
    ibin += 1

  return compact

def readMatrix(covmx, h_data, diag= False,log = False):
  
  npz = h_data.GetNbinsX()+2
  npt = h_data.GetNbinsY()+2
  
  size = (npt-2)*(npz-2)
  
  compact = TMatrixD(size,size);
  ixx = -1;
  for  ix in range(npz, (npz)*(npt-1)):
    if(  ix%(npz) == 0 or ix%(npz) ==npz-1):
      continue;
  
    ixx += 1
    iyy = -1;
    for  iy  in range(npz, (npz)*(npt-1)):
      if ( iy%(npz) == 0 or iy%(npz) == npz-1):
        continue;
    
      iyy += 1
      
     
      if not log:
        compact[ixx][iyy] = covmx[ix][iy]
      else:
        compact[ixx][iyy] = covmx[ix][iy]
      
      if (diag and ixx!=iyy):
        compact[ixx][iyy] = 0;
      # special to deal with completely empty bins

  return compact

def readMatrix1D(covmx, h_data, diag= False,log = False):
  print ("READMATRIX")
  #covmx.
 
  npz = h_data.GetNbinsX()+2
 
  size = (npz-2)
  
  compact = TMatrixD(size,size);
  ixx = -1;
  for  ix in range(1,npz-1):
    ixx = ix -1
    
    for  iy  in range(1,npz-1):
      iyy = iy -1
      
      
      if not log:
        compact[ixx][iyy] = covmx[ix][iy]
      else:
        compact[ixx][iyy] = covmx[ix][iy]
      
      if (diag and ixx!=iyy):
        compact[ixx][iyy] = 0;

  #compact.Print()
  return compact
 

def compressVector(v,e):
  vnew = TVectorD(len(e))
  for i in e:
    vnew[i] = v[e[i]]
 
  return vnew

def compressMatrix(v,e):
  vnew = TMatrixD(len(e),len(e))
  for i in e:
    for j in e:
      vnew[i][j] = v[e[i]][e[j]]
  
  return vnew
  
