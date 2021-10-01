The python script "getvars.py" attempts to identify all the variables called from a CCQENu tuple among a collection of `.h` and `.C` files identified by name or directory. To run this script, enter the folder containing "getvars.py" and enter

```
python3 getvars.py [arguments]
```

The arguments can be one of the following:

```
flist  : Tells program to extract directory and file names from ./Input_Files/files_list.txt 
         and recursively collect file names for named directories.
glist  : Tells program to only search for variables called using the list of "get's" in 
         ./Input_Files/allowed_gets.txt. The default will be to look for all "get's" with the
         exception of those listed in ./Input_Files/bad_gets.txt
/path/ : Any number of valid directory or file paths. These will be treated the same as (and 
         in addition to any) items found in ./Input_Files/files_list.txt. If there are no 
         path arguments and flist is not included ./Input_Files/files_list.txt will be 
         referenced by default.
```

