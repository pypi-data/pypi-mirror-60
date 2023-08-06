
from .imports.internal   import *



#from .string import *

from subprocess import Popen, PIPE, STDOUT

    

def bash(cmd, prnt=True, wait=True):
    """
    Run a command via bash. Optionally prints results and waits for completion.
    return: stdout
    """
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    if wait:
        p.wait()
    while True and prnt:
        line = p.stdout.readline()
        if line:
            print(line)
        else:
            break

    return (p)



def run_sed_inplace(filename, textToSearch, textToReplace, sep="/"):
    """
    runs the external SED command on a file, inplace.
    this is very useful to patch files

    note that SED accepts any custom seperator (default = "/" )
    """

    if st_st_present(textToSearch, sep):
        raise ValueError("cannot use sep %s in TO_SEARCH" % sep)
    if st_st_present(textToReplace, sep):
        raise ValueError("cannot use sep %s in TO_REPLACE" % sep)

    # https://stackoverflow.com/questions/17140886/how-to-search-and-replace-text-in-a-file-using-python
    cmd = "sed -i 's{sep}{textToSearch}{sep}{textToReplace}{sep}g' {filename}".format(**locals())
    print(cmd)
    bash(cmd)
    
    

