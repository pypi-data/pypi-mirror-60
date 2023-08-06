
from ..imports.internal   import *


def dt_now():
    return datetime.datetime.now()


def now_float():
    return time.time()

def exec_profile(cmd,args,do_profile=True):
  """
  run a function with optional profiling.
  for this use the bolerplarte below. Differences are:
   - comma between the function and the parenthesis
   - comma inside the parenthesis (if its a single parameter)
  
  ORIGINAL:
      df_all = do_work(conf)
  
  CHANGED:
      df_all = exec_profile(
               do_work,(conf)
               , do_profile=conf.do_profile)

  references:
    https://docs.python.org/3.5/library/profile.html
    https://docs.python.org/3.5/library/functions.html#exec
    https://stackoverflow.com/questions/701802/how-do-i-execute-a-string-containing-python-code-in-python 
  """

  import cProfile
  import re
  import cProfile, pstats, io
  pr = cProfile.Profile()

  if do_profile:
      pr.enable()
  
  ret = exec_verbose(cmd, args)
  
  if do_profile:
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
    
  return ret



def decorator_timeit(f):
  # https://stackoverflow.com/questions/1622943/timeit-versus-timing-decorator

  @wraps(f)
  def wrap(*args, **kw):
    time_start= dt_now()
    print("time started: %s" % (time_start))

    result = f(*args, **kw)

    time_end= dt_now()
    delta = time_end - time_start
    print("time end:     %s  (%0.1f seconds / %0.1f minutes)" % (time_end, delta.total_seconds, delta.total_seconds()/60.0))

    #print('func:%r args:[%r, %r] took: %2.4s sec' % \
    #  (f.__name__, args, kw, delta.total_seconds()))
    return result
  return wrap
  

#
# to use this:
#
# a) as a decorator:
#   @timeit
#   def query_impala(...)
#
# b) as a new fucntion:
#   timeit_query_impala = timeit( query_impala)
# 




def exec_verbose(cmd, args):
  st = "%s%s" % (cmd.__name__, str(args))

  debug=True
  print_debug(debug, "To Exec: %s " % (st))
  #ret = exec(st)
  ret = cmd(*args)
  return ret


  


