
from ..imports.internal   import *


#from .trace     import *


def decorator_with_arguments(argument):
    """
    https://stackoverflow.com/questions/5929107/decorators-with-parameters
    """
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            funny_stuff()
            something_with_argument(argument)
            result = function(*args, **kwargs)
            more_funny_stuff()
            return result
        return wrapper
    return real_decorator


def decorator_autogen_code(original_func, decorator, new_func=None):
  """
  auto generates code to create decorated functions with NEW NAMES
  
  """
  
  if new_func is None:
    new_func = "%s_verbose" % (original_func)
    
  #short_name = short_name.__name__
  #decorator = decorator.__name__
    
  print("""
 
#
# decorator_autogen_code("{original_func}", "{decorator}", '{new_func}' )  
#
@{decorator}
def {new_func}(*args, **kwargs):
   return {func}(*args, **kwargs)
   
  """.format(decorator=decorator, func=original_func,  new_func=new_func, original_func=original_func))





"""
debugable function decorator

ddef f(a,b):
  print("running f")
  print(a+b)
  

@skip_if_not_debug
ddef debug_f(debug, *args, **kwargs):
  f(*args, **kwargs)
  
debug=True
debug_f(debug, 1,2)
"""


def decorator_skip_if_not_debug(func):

  @wraps(func)
  def decorated(*args):
    g_debug = False
    try:
      if debug:
        g_debug = debug
    except:
      pass
        
    if g_debug:
      return func(*args)
    else:
      #print("skipping function")
      pass

  return decorated



def static_vars(**kwargs):
    """
    Decorator to add static variables to functions.

    usage:
      @static_vars(counter=0)
      def foo():
          foo.counter += 1
          print()"Counter is %d" % foo.counter)

    https://stackoverflow.com/qfrom functools import wrapsuestions/279561/what-is-the-python-equivalent-of-static-variables-inside-a-function
    """

    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate

  
def try_decorator(error_ret=None):
  """
  Decorator that tries something, OR returns a safe_value if failure happens (and continues)

  usage:
    @try_or_return_none
    def foo():
        if rand() > 0.9:
            raise Error
        else:
            return rand()
  """
  
  def real_decorator(function):
    
    @wraps(function)
    def wrapper(*args, **kwargs):
      try:
        ret = function(*args, **kwargs)
        return ret

      except (Exception) as e:
        print("")
        print("try_decorator: got an execution error. Below is the stack trace.")
        print("try_docorator: Will continue, and return '%s' instead" % (error_ret))
        print_exception_stack(*sys.exc_info())
        return error_ret

    
    return wrapper
  
  return real_decorator


def try_decorator_return_none():
  return try_decorator(error_ret=None)

def try_decorator_return_empty():
  return try_decorator(error_ret=[])


 

_ = """
To discourage global variable lookup, move your function into another module. 
Unless it inspects the call stack or imports your calling module explicitly; 
it won't have access to the globals from the module that calls it.

In practice, move your code into a main() function, to avoid creating unnecessary 
global variables.

If you use globals because several functions need to manipulate shared state then 
move the code into a class.
"""


def current_imports():
    for name, val in globals().items():
        # module imports
        if isinstance(val, types.ModuleType):
            yield name, val
        # functions / callables
        if hasattr(val, '__call__'):
            yield name, val

# no global decorator
noglobal = lambda fn: types.FunctionType(fn.__code__, dict(current_imports()))


_ = """
a = 1

@noglobal
def f():
    print(a)
 
f()
"""




def debugged(func):
  def call(*args,**kwargs):
    print("Calling %s" % func.__name__)
    result = func(*args,**kwargs)
    print("%s returning %r" % (func.__name__, result)) 
    return result
    
  return call

"""
def ensure(func):
  # Extract annotation data
  return_check = func.__annotations__.get('return',None) 
  arg_checks = [(name,func.__annotations__.get(name))
  
  for name in func.__code__.co_varnames:
    # Create a wrapper that checks argument values and the return # result using the functions specified in annotations
    def assert_call(*args,**kwargs):
      for (name,check),value in zip(arg_checks,args):
"""

  