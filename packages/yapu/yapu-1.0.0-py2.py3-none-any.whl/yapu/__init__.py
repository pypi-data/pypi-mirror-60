# https://stackoverflow.com/questions/44834/can-someone-explain-all-in-python
#   It's a list of public objects of that module, as interpreted by import *.
#   It overrides the default of hiding everything that begins with an underscore.

# https://stackoverflow.com/questions/1093322/how-do-i-check-what-version-of-python-is-running-my-script

import sys
assert sys.version_info >= (3,4)


#from .imports_base   import *
#from .imports_local  import *


_ = """

Structure of this library:

yapu/
  __init__.py
  
  string.py
    func1
    func2
    
  list.py
    func1
    func2

    
  imports/external.py:
    import re, os, pandas, ...
    
  imports/base.py:
    from .imports.external       import *
    from .meta                   import *
    
  imports/all.py:
    import .imports.base
    from .FILE1                  import *
    from .FILE2                  import *
    
    
tests/yapu_tests
  unittests.py
    from imports_all import *
    def test_whole_library():
      ...
      ...
      
"""


def setsane_defaults():
    # http://stackoverflow.com/questions/372365/set-timeout-for-xmlrpclib-serverproxy
    socket.setdefaulttimeout(1)
    
    # force unbuffered stdout, to see the verbose messages
    sys.stdout = fdopen(sys.stdout.fileno(), 'w', 0)


#setsane_defaults


