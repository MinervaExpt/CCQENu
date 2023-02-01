import sys
import re
import glob
import os.path

    
# Check arguments for where to get files to check and what sort of "Get's"
# to ignore or look for

filesFile = 0
allowedGets = 0
fileList = list()

for arg in sys.argv[1:]:
    if arg == 'flist':
        filesFile = 1
    elif arg == 'glist':
        allowedGets = 1
    elif os.path.isfile(arg):
        if arg[-2]+arg[-1]=='.C' or arg[-2]+arg[-1]=='.h':
            fileList.append(arg)
        else:
            print('Searched files need to end in .C or .h. Ignoring argument '+arg)
    elif os.path.exists(arg) and not os.path.isfile(arg):
        fileList += glob.glob(arg+'/**/*.C', recursive=True)
        fileList += glob.glob(arg+'/**/*.cxx', recursive=True)
        fileList += glob.glob(arg+'/**/*.h', recursive=True)
        fileList += glob.glob(arg+'/*.C', recursive=True)
        fileList += glob.glob(arg+'/*.cxx', recursive=True)
        fileList += glob.glob(arg+'/*.h', recursive=True)

# Get files       
if filesFile or len(fileList) == 0:
    if os.path.isfile('Input_Files/files_list.txt'):
        filesListFile = open('Input_Files/files_list.txt','r')
        for path in filesListFile:
            path = path.split()[0]
            if os.path.exists(path) and not os.path.isfile(path):
                fileList += glob.glob(path+'/**/*.C', recursive=True)
                fileList += glob.glob(path+'/**/*.cxx', recursive=True)
                fileList += glob.glob(path+'/**/*.h', recursive=True)
                fileList += glob.glob(path+'/*.C', recursive=True)
                fileList += glob.glob(path+'/*.cxx', recursive=True)
                fileList += glob.glob(path+'/*.h', recursive=True)
            elif os.path.isfile(path):
                fileList.append(path)
            else:
                print(path+' does not exist within this machine. Ignoring.')
    else:
        print('\n Error: ./Input_Files/files_list.txt does not exist.\n')
        quit()

        
fileList = list(set(fileList)) # Removes repeats
        
# Get "Got's" filter
if allowedGets:
    if os.path.isfile('Input_Files/allowed_gets.txt'):
        goodGetsFile = open('Input_Files/allowed_gets.txt','r')
        goodGets = list()
        for get in goodGetsFile:
            get = get.split()[0]
            goodGets.append(get)
    else:
        print('\n Error: ./Input_Files/allowed_gets.txt does not exist.\n')
        quit()
else: # Default
    if os.path.isfile('Input_Files/bad_gets.txt'):
        badGetsFile = open('Input_Files/bad_gets.txt','r')
        badGets = list()
        for get in badGetsFile:
            get = get.split()[0]
            badGets.append(get)
    else:
        print('\n Error: ./Input_Files/bad_gets.txt does not exist.\n')
        quit()


# Get list of all variables in CCQENu tuple
if not os.path.isfile('Input_Files/allCCQENu.csv'):
    print('\n Error: ./Input_Files/allCCQENu.csv does not exist.\n')
    quit()
allFile = open('Input_Files/allCCQENu.csv','r')
allTypes = list()
allVars = list()

for line in allFile:
    columns = re.split(',',line)
    if columns[0] == 'Index': continue
   
    allTypes.append(''.join(re.split('_t',columns[1])))
    allVars.append(columns[2])
    


# Make empty lists
types = list()       # Variable data types
typeLengths = list()
variables = list()   # Variable names
varLengths = list()
varPaths = list()    # List of files containing variable
varPathLengths = list()
varLine = list()     # Line content of code where variable called
varLineNo = list()   # Line number of code where variable called
varPart = list()

maybes = list()
maybeLengths = list()
maybePaths = list()
maybePathLengths = list()
maybeLine = list()
maybeLineNo = list()
maybePart = list()

for fileName in fileList:
    file = open(fileName,'r')
    lineNo = 1
    for line in file:
        lineText = line.lstrip() # Remove leading space for each line
        if 'Get' not in line: 
            lineNo += 1
            continue # Only consider lines containing "Get"
        if lineText[0] == '/': 
            lineNo += 1
            continue # If line is a comment ignore
        
        lineText2 = lineText
        if allowedGets:
            skip = 1
            for get in goodGets:
                if get in lineText:
                    skip = 0
                    continue
            if skip: 
                lineNo += 1
                continue
        else:
            rmGet = 0
            for get in badGets:
                if get in lineText: # Remove N/A "Get's"
                    getReplace = get.replace('Get','G_E_T')
                    lineText2 = lineText2.replace(get,getReplace)
                    rmGet = 1
            if rmGet and 'Get' not in lineText2: 
                lineNo += 1
                continue
        
        parts = re.split('Get',lineText2) # Splits line into sections between "Get's"
        parts = parts[1:] # Only look at sections of line after first a "Get"
        
        for part in parts:
            if '"' not in part: continue # Variables called in quotes
            word = re.findall(r'\"(.+?)\"',part) # Finds text enclosed by quotes
            if word == None or len(word) == 0: continue
            word = word[0] # First quoted text after "Get"
            badchar = 0
            for char in [' ','#',';',':','%','/','.']: 
                if char in list(word): # variable should not include
                    badchar = 1
            if word[-1] == '_': badchar = 1 # Last character is a "_"
            if badchar: continue
            if word[0] == '_': word = 'CCQENu'+word # First character is a "_"
            
            if word in allVars:
                #print(word)
                types.append(allTypes[allVars.index(word)])
                typeLengths.append(len(allTypes[allVars.index(word)]))
                variables.append(word)
                varLengths.append(len(word))
                varPaths.append(fileName)
                varPathLengths.append(len(fileName))
                varLine.append(lineText)
                varLineNo.append(lineNo)
                varPart.append(part)
            else:
                maybes.append(word)
                maybeLengths.append(len(word))
                maybePaths.append(fileName)
                maybePathLengths.append(len(fileName))
                maybeLine.append(lineText)
                maybeLineNo.append(lineNo)
                maybePart.append(part)
                
        lineNo += 1

# likely missed variables
maybeMissed = ['muon_thetaX','muon_thetay','truth_genie_wgt_AGKYxF1pi','truth_genie_wgt_AhtBY']
maybeMissedTypes = ['double','double','double','double']
maybeMissedLengths = [11,11,25,21]
maybeMissedPaths = ["NA","NA","NA","NA"]
maybeMissedPathLengths = [2,2,2,2]
maybeMissedLine = ["NA","NA","NA","NA"]
maybeMissedLineNo = [0,0,0,0]
maybeMissedPart = ["NA","NA","NA","NA"]

variables = variables + maybeMissed
varLengths = varLengths + maybeMissedLengths
varPaths = varPaths + maybeMissedPaths
varPathLengths = varPathLengths + maybeMissedPathLengths
varLine = varLine + maybeMissedLine
varLineNo = varLineNo + maybeMissedLineNo
varPart = varPart + maybeMissedPart

# variables and files per variable
varsSorted = list(set(variables))
varsSorted = sorted(varsSorted, key=str.lower)       
varsFile = open('Output_Files/ccqenu_variables.txt','w')
filePerVar = open('Output_Files/files_per_variable.txt','w')
filePartPerVar = open('Output_Files/file_get_per_variable.txt','w')
for var in varsSorted:
    varsFile.write(var+'\n')
    filePerVar.write(var+'\n\n')
    filePartPerVar.write(var+'\n')
    
    varfiles = list()
    varparts = list()
    for i in [index for index, value in enumerate(variables) if value == var]:
        varfiles.append(varPaths[i])
        if varLineNo[i] < 10: spaces = '          '
        elif varLineNo[i] < 100: spaces = '         '
        elif varLineNo[i] < 1000: spaces = '        '
        else: spaces = '       '
        word = re.findall(r'\"(.+?)\"',varPart[i])
        word = word[0]
        varparts.append(spaces+str(varLineNo[i])+'  ... Get'+varPart[i][0:varPart[i].index(word)+len(word)+2])
    
    varfilesSorted = list(set(varfiles))
    varfilesSorted = sorted(varfilesSorted, key=str.lower)
    for path in varfilesSorted:
        filePerVar.write('    '+path+'\n')
        filePartPerVar.write('\n    '+path+'\n\n')   
        for i in [index for index, value in enumerate(varfiles) if value == path]:
            filePartPerVar.write(varparts[i]+'\n')

    filePerVar.write('\n')
    filePartPerVar.write('\n')
    
varsFile.close()
filePerVar.close()
filePartPerVar.close()

maybesSorted = list(set(maybes))
maybesSorted = sorted(maybesSorted, key=str.lower)
maybesFile = open('Output_Files/almost_variables.txt','w')
filePerMaybe = open('Output_Files/files_per_almost.txt','w')
for may in maybesSorted:
    maybesFile.write(may+'\n')
    filePerMaybe.write(may+'\n\n')
    
    mayfiles = list()
    for i in [index for index, value in enumerate(maybes) if value == may]:
        mayfiles.append(maybePaths[i])
    
    for path in mayfiles:
        filePerMaybe.write('    '+path+'\n')
    filePerMaybe.write('\n')
maybesFile.close()
filePerMaybe.close()


# variables path file
                
varPathsSorted = list(set(varPaths))
varPathsSorted = sorted(varPathsSorted, key=str.lower)
varsPerFile = open('Output_Files/variables_per_file.txt','w')
linesPerFile = open('Output_Files/lines_per_file.txt','w')
for path in varPathsSorted:
    varsPerFile.write(path+'\n\n')
    linesPerFile.write(path+'\n\n')
    
    filevars = list()
    filelinenos = list()
    filelines = list()
    
    for j in [index for index, value in enumerate(varPaths) if value == path]:
        filevars.append(variables[j])
        filelinenos.append(varLineNo[j])
        filelines.append(varLine[j])
    
    filevarsSort = list(set(filevars))
    filevarsSort = sorted(filevarsSort, key=str.lower)
    for var in filevarsSort:
        varsPerFile.write('    '+var)
        linesPerFile.write('    '+var+'\n')
        
        varlinenos = list()
        varlines = list()
        
        for k in [index for index, value in enumerate(filevars) if value == var]:
            varlinenos.append(filelinenos[k])
            varlines.append(filelines[k])
        
        i = 0
        while i < len([index for index, value in enumerate(filevars) if value == var]):
            if varlinenos[i] < 10: 
                linesPerFile.write('         '+str(varlinenos[i])+'  '+varlines[i])
            elif varlinenos[i] < 100: 
                linesPerFile.write('        '+str(varlinenos[i])+'  '+varlines[i])
            elif varlinenos[i] < 1000: 
                linesPerFile.write('       '+str(varlinenos[i])+'  '+varlines[i])
            elif varlinenos[i] < 10000: 
                linesPerFile.write('      '+str(varlinenos[i])+'  '+varlines[i])
            i += 1
            
        varsPerFile.write('\n')
        linesPerFile.write('\n')
        
    varsPerFile.write('\n')
    linesPerFile.write('\n')

varsPerFile.close()
linesPerFile.close()

maybePathsSorted = list(set(maybePaths))
maybePathsSorted = sorted(maybePathsSorted, key=str.lower)
maybesPerFile = open('Output_Files/almosts_per_file.txt','w')
maylinesPerFile = open('Output_Files/almost_lines_per_file.txt','w')
for path in maybePathsSorted:
    maybesPerFile.write(path+'\n\n')
    maylinesPerFile.write(path+'\n\n')
    
    mayfilevars = list()
    mayfilelinenos = list()
    mayfilelines = list()
    
    for j in [index for index, value in enumerate(maybePaths) if value == path]:
        mayfilevars.append(maybes[j])
        mayfilelinenos.append(maybeLineNo[j])
        mayfilelines.append(maybeLine[j])
    
    mayfilevarsSort = list(set(mayfilevars))
    mayfilevarsSort = sorted(mayfilevarsSort, key=str.lower)
    for may in mayfilevarsSort:
        maybesPerFile.write('    '+may)
        maylinesPerFile.write('    '+may+'\n')
        
        maylinenos = list()
        maylines = list()
        
        for k in [index for index, value in enumerate(mayfilevars) if value == may]:
            maylinenos.append(mayfilelinenos[k])
            maylines.append(mayfilelines[k])
        
        i = 0
        while i < len([index for index, value in enumerate(mayfilevars) if value == may]):
            if maylinenos[i] < 10: 
                maylinesPerFile.write('         '+str(maylinenos[i])+'  '+maylines[i])
            elif maylinenos[i] < 100: 
                maylinesPerFile.write('        '+str(maylinenos[i])+'  '+maylines[i])
            elif maylinenos[i] < 1000: 
                maylinesPerFile.write('       '+str(maylinenos[i])+'  '+maylines[i])
            elif maylinenos[i] < 10000: 
                maylinesPerFile.write('      '+str(maylinenos[i])+'  '+maylines[i])
            i += 1
            
        maybesPerFile.write('\n')
        maylinesPerFile.write('\n')
        
    maybesPerFile.write('\n')
    maylinesPerFile.write('\n')

maybesPerFile.close()
maylinesPerFile.close()

print('\nNothing broke. Check ./Output_Files/ for lists.\n')
