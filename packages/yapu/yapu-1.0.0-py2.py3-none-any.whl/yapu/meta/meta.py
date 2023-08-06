
from ..imports.internal   import *
from ..meta.listify   import *


###
### very generic wrappers go here
###

def percentage(a,b=None, digits=1):
    if b is None:
        b=1.0

    ret = (float(a) * 100.0) / float(b)
    return ret
    

def st_percent(a, b=None, digits=1):
    """
    form1: a= 0..1
    form2: a=0..1000, b=0..1000
    """
    
    ret = percentage(a, b, digits=digits)
  
    fmt_st = "%%0.%df" % (digits)
    ret = fmt_st % (ret)
    ret = ret + "%"
    return ret
  

def st_percentage(a, b, digits=0):
    return "%7s   (%s of %s)" % (a, st_percent(a, b, digits), b)


def st_collapse(st, sep=","):
    """
    collapses "None" to the empty string
    collapes a list of strings by joining them
    """
    l = listify(st)
    return sep.join(l)



# http://stackoverflow.com/questions/31683959/the-zip-function-in-python-3
def zip_python3(*args):
    return list(zip(*args))


def tuple_swap(t):
    return (tuple(reversed(t)))


def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in xrange(ord(c1), ord(c2) + 1):
        yield chr(c)

        

def irange(a, b=None, c=None):
    """
    same signature as range(). However, starts at "1" + its always inclusive of the last element.

    original documentation:
        range(stop) -> range object
        range(start, stop[, step]) -> range object

        Return an object that produces a sequence of integers from start (inclusive)
        to stop (exclusive) by step.  range(i, j) produces i, i+1, i+2, ..., j-1.
        start defaults to 0, and stop is omitted!  range(4) produces 0, 1, 2, 3.
        These are exactly the valid indices for a list of 4 elements.
        When step is given, it specifies the increment (or decrement).
    """

    if c is None:
        c = 1

    if b is None:
        all = list(range(a))
        for i in all:
            yield (i + 1)

    else:
        if c > 0:
            all = list(range(a, b + 1, c))
        else:
            all = list(range(a, b - 1, c))
            
        for i in all:
            yield (i)



def irange_count(a, n=0, step=None):
  """
  from a given number, count n elements around it (up or down)
  step is optional and always positive (even if n<0)
  
  """
  if step is None:
    step = 1
    
  if n >= 0:
    all = list(irange(a, a+n, step))
  else:
    step = step * -1
    all = list (irange(a, a+n, step))

  for i in all:
      yield (i)
      


def print_nls(how_many=1):
    """
    prints NLs
    """
    
    for i in range(how_many):
      print_nl()
    

def print_nl(what=None):
    """
    prints lists with one element 
    """
    #what = listify(what)
    if what is None:
      what = ""
      
    print(what, sep="\n")


def print_nonl(*args, **kwargs):
    """
    print(value, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

    Prints the values to a stream, or to sys.stdout by default.
    Optional keyword arguments:
      file:  a file-like object (stream); defaults to the current sys.stdout.
      sep:   string inserted between values, default a space.
      end:   string appended after the last value, default a newline.
      flush: whether to forcibly flush the stream.
    """
    print(*args, end="", ** kwargs)



def print_as_list(what):
    what = list(what) 
    for i in what:
      print(i)
      

      