import os,sys
from subprocess import call,run
from datetime import datetime, timezone
from ROOT import TFile

def pnfs2xrootd(filename):
    return filename.replace("/pnfs/","root://fndca1.fnal.gov:1094//pnfs/fnal.gov/usr/")

def xrootd2pnfs(filename):
    tmp = filename.split("/usr/")
    return os.path.join("/pnfs/",tmp[1])

def checkFile(filepath,debug):
    f = 0
    try:
        f = TFile.Open(filepath,"READONLY")
        if debug: print("could open",filepath)
        return True
    except Exception as e:
        print ("could not open",filepath,e)
        return False

def makeTimeStamp():
    'make a timestamp'
    t = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    return t

def makeLocalCopy(locationlist=None,cache="cache",debug=False):
    if not os.path.exists(cache):
        try:
            os.mkdir(cache)
        except Exception as e:
            print ("WARNING: No local cache could be defined",cache)
            return [],1
    local = []
    if debug:
        print ("locationlist",locationlist)
    for location in locationlist:
        location = location.strip()
        if cache in location or os.path.exists(os.path.join(cache,os.path.basename(location))):
            if debug: print("using local copy",location)
            local.append(os.path.join(cache,os.path.basename(location)))
        else:
            if "pnfs" in location[0:10]:
    
                location = (pnfs2xrootd(location)).strip()
            print ("the location",location)
            cp_args = ["xrdcp",location,cache]
            print ("cp command", cp_args)
            try:
                completed_process = run(cp_args, capture_output=True, text=True)
                print("Error code:", completed_process.returncode)
                print("Error:", completed_process.stderr)
                print("Output:", completed_process.stdout)
                if debug: print (completed_process)       
            except Exception as e:
                print ("WARNING: error doing copy",e,location)
                continue
            local.append(os.path.join(cache,os.path.basename(location)))
    retcode = len(locationlist)-len(local)
    return local,retcode

def cleanup(local,debug=False):
    for file in local:       
        if debug: print ("removing",file)
        os.remove(file)

if __name__ == "__main__":

    
    locations = "/Users/schellma/Dropbox/ccqe/p8/nu/1B.txt"
    if len(sys.argv) > 0:
        locations = sys.argv[1]
    locationlist = open(locations,'r').readlines()
    print (locationlist)
    cache = "/Users/schellma/tmp/"
    if len(sys.argv) > 0 :
        cache = sys.argv[2]

    makeLocalCopy(locationlist=locationlist,cache=cache,debug=False)