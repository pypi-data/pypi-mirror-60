
from ..imports.internal   import *
from ..meta.meta   import *


## pdb tutorial: https://pymotw.com/2/pdb/




###
### Generic "meta-python" functions go here:
###
def my_raise(what=""):
    print("Error: ", what)
    #raise what
    sys.exit(1)


def warn(what=None):
    print("Warning: ", what)
    #sys.exit(1)
    #raise what
    return
    

    
def die(what=None):
    print("Error: ", what)
    sys.exit(1)
    #raise what


def my_assert(what, expected=True):
    """
    custom assert() function. It displays the actual arguments that failed

    """

    ## todo: extend from unittest. Testcase to catch the exception
    # http://stackoverflow.com/questions/129507/how-do-you-test-that-a-python-function-throws-an-exception

    if (what == expected):
        return True
    else:
        print_nl()
        print_nl()
        print("ASSERT ERROR:  Expected = %s ;      Calculated = %s " % (expected, what ))
        raise AssertionError


def varname(var, uplevels=0):
    """
    returns the variable name itself

    use higher uplevels to go deeper in the stack
    
    https://stackoverflow.com/questions/2553354/how-to-get-a-variable-name-as-a-string
    (including fix from  Emmanuel DUMAS Sep 2 '15 at 10:04)
    """

    # find frame
    frame = inspect.currentframe().f_back
    for uplevel in range(uplevels):
        frame = frame.f_back

    # frame = inspect.currentframe()
    var_id = id(var)
    for name in frame.f_locals.keys():
        try:
            if  id(eval(name, None, frame.f_locals)) == var_id:
                return (name)
        except:
            pass

    pass



def dump_values(*args, also_names=False, pre_st=None, uplevels=0):
  """
  Dumps a list of variable values
  """

  uplevels += 1

  args = ["'{}'".format(i) for i in args ]
  st = " ".join(args)
  
  if pre_st:
    st = pre_st + ":     " + st

  print(st)
    

def dump_var(*args, also_names=False, pre_st=None, uplevels=0):
  """
  Dumps a list of variables (name, value and type)
  """

  uplevels += 1

  if pre_st:
    pre_st = pre_st + ":     "

  for var in args:
    name = varname(var, uplevels)
    print("%svariable: '%s' -> '%s'      %s " % (st_collapse(pre_st), name, str(var), type(var)))


    
def debug_dump_values(debug, *args, pre_st=None, uplevels=0):
  if debug:
    uplevels += 1
    dump_values(*args, pre_st=pre_st, uplevels=uplevels)



def debug_dump_var(debug, *args, pre_st=None, uplevels=0):
  if debug:
    uplevels += 1
    dump_var(*args, pre_st=pre_st, uplevels=uplevels)
    


def get_function_name(uplevels=0):
    """
    returns the calling function name itself

    use higher uplevels to go deeper in the stack
    see: https://stackoverflow.com/questions/251464/how-to-get-a-function-name-as-a-string-in-python
    """
    uplevels += 2
    return traceback.extract_stack(None, uplevels)[0][2]


def dump_function_code(f):
    lines = inspect.getsourcelines(f)
    print("".join(lines[0]))


def get_function_parameters_and_values(uplevels=0):
    """
    returns calling function arguments as a list of tuples

    use higher uplevels to go deeper in the stack
    """

    # find frame
    frame = inspect.currentframe().f_back
    for uplevel in range(uplevels):
        frame = frame.f_back

    args, _, _, values = inspect.getargvalues(frame)
    ret = ([(i, values[i]) for i in args])
    return ret


def get_function_signature(uplevels=0):
    """
    RETURNS the calling function signature, at runtime.
    """
    uplevels += 1

    funcname = get_function_name(uplevels)
    params = get_function_parameters_and_values(uplevels)

    params = ", ".join(["{}={}".format(*i) for i in params])
    sig = "{}({})".format(funcname, params)

    return sig


def dump_function_signature(uplevels=0):
    """
    PRINTS calling function signurate, at runtime.
    """
    uplevels += 1

    sig = get_function_signature(uplevels)

    ret = " --->           {}".format(sig)
    print(ret)
    return ret


def debug_dump_function_signature(debug, uplevels=0):
    if debug:
        uplevels += 1
        dump_function_signature(uplevels)


def print_verbose(verbose, *args, **kwargs):
    print_debug(verbose, *args, **kwargs)


def print_debug(debug, *args, **kwargs):
    if debug:
        print(*args, ** kwargs)

        


def add_debug_arguments(parser):
  """
  Usage:
    parser = argparse.ArgumentParser(description="...")
    parser=add_debug_arguments(parser)
    opts = parser.parse_args()
    opts = parse_debug_arguments(opts)
  
  """

  parser.add_argument('-q', "--quiet", dest="quiet", default=False, action="store_true",
                      help='Quiet flag')
                      
  parser.add_argument('-R', "--regular", dest="regular", default=True, action="store_false",
                      help='Verbose flag')

  parser.add_argument('-v', "--verbose", dest="verbose", default=False, action="store_true",
                      help='Verbose flag')

  parser.add_argument('-d', "--debug", dest="debug", default=False, action="store_true",
                      help='Debug flag')
                      
  parser.add_argument('-D', "--very_debug", dest="very_debug", default=False, action="store_true",
                      help='Verbose flag')
  
  return parser
  
 
def parse_debug_arguments(opts):
  if opts.very_debug:
    opts.debug = True
    
  if opts.debug:
    opts.verbose = True
    
  if opts.verbose:
    opts.regular = True
    
 
  if opts.quiet:
    opts.regular = False
    opts.verbose = False
    opts.debug = False
    opts.very_debug = False
 
  return opts  
  
  
def dprint(debug, *args, **kwargs):
    if debug:
      print(*args, **kwargs)

      
      