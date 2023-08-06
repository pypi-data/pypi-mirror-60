
from .imports.internal   import *
from .string import *
from .list import *



#
# FUNCTIONS FOR MULTILINE AND LIST_OF_STRINGS
#
#
# functions:
#   ml_function = input is multiline string, with "\n" in the middle
#   st_function = input is a STRING __or__ a LIST_OF_STRINGS
#
# conversions:
#   def st_to_ml(what):
#   def ml_to_st(ml, end=None, start=None, clean=True):
#   def ml_to_df(ml, clean=True, **kwargs):
#
# function parameters:
#   ml         = multiline string. THIS IS ONLY USED AS INPUT
#   line       = single string
#   lines      = list of strings
#   what       = either STRING  or LINES   (unlistify-style)
#
#

#
# pandas:
#  pandas.to_numeric -  Return type depends on input. Series if Series, otherwise ndarray
#  pandas.to_datetime  -  Return type depends on input:
#   list-like: DatetimeIndex
#   Series: Series of datetime64 dtype
#   scalar: Timestamp


############

def st_to_ml(what):
    return st_joinlines(what)

def ml_to_st(ml, end=None, start=None, clean=True):
    return ml_splitlines(ml, end=end, start=start, clean=clean)


def ml_to_df_whitespace(ml, clean=True, **kwargs):
  return ml_to_df(ml, clean=clean, delim_whitespace=True, **kwargs)




def ml_to_df(ml, clean=True, **kwargs):
  """
  https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html
  """
  
    
  if clean:
    ml = ml_clean(ml)
  
  return pd.read_csv(StringIO(ml), **kwargs)

#########



def ml_strip_words(ml):
    """
    removes whitespace in all words
    """

    words = ml.split()
    words = [word.strip() for word in words]

    return words
    

def st_strip_lines(what):
    """
    removes whitespace in a multi-line var
    """

    lines, t = listify_safe(what)
    lines = [line.strip() for line in lines]
    what = unlistify(lines, t=t)

    return what


def st_remove_chars(what, chars=""):
    """
    removes empty lines in a multi-line var
    """

    lines, t = listify_safe(what)
    lines = [line for line in lines if line.strip()]
    what = unlistify(lines, t=t)

    return what


def st_remove_empty_lines(what):
    """
    removes empty lines in a multi-line var
    """

    lines, t = listify_safe(what)
    lines = [line for line in lines if line.strip()]
    what = unlistify(lines, t=t)

    return what


def st_remove_comment_lines(what):
    """
    removes comments from a multi-line var
    """

    lines, t = listify_safe(what)
    lines = [line for line in lines if not st_is_comment(line)]
    what = unlistify(lines, t=t)

    return what


def st_clean(what, remove_empty_lines=True, strip_lines=True, remove_comments=True, remove_chars=None):
    lines, t = listify_safe(what)

    if remove_chars:
        lines = st_remove_chars(lines)

    if remove_comments:
        lines = st_remove_comment_lines(lines)

    if strip_lines:
        lines = st_strip_lines(lines)

    if remove_empty_lines:
        lines = st_remove_empty_lines(lines)

    what = unlistify(lines, t=t)
    return what


def ml_clean(ml):
    st = ml_splitlines(ml, clean=True)
    return st_joinlines(st)


#############


def ml_splitlines(ml, end=None, start=None, clean=True):
    """
    wrapper to splitlines, with optional start and end lines.
    
    
    input:  MULTILINE STRING
    output: LIST STRINGS
    
    start/end: integer line positions
    """

    # print(ml)

    if is_list(ml):
        raise ValueError("passed a list to ml_splitlines")

    lines = ml.splitlines()

    if clean:
        lines = st_clean(lines)

    lines = lines[start:end]
    return lines


def st_joinlines(what):
    """
    wrapper to splitlines, with optional start and end lines.
    output: multiline
    """

    lines = listify(what)
    ml = "\n".join(lines)
    return ml



#####
def grep_1(items, st, rev=False):
    items = listify_safe(items)
      
    if not rev:
        return [i for i in items if st in i]
    else:
        return [i for i in items if st not in i]
    
    # regexp:
    #  [i for i in a if re.search("^df_", i) ]

    
def grep_not(needle, haystack):
    return grep(needle, haystack, rev=True)


def grep(needle, haystack, rev=False, verbose=False, regexp=True):
    """
    finds 'items' in 'to_find'.
    Either can be an item or whole lists
    """
    #raise NotImplemented()

    print(needle, haystack, type(needle))

    
    to_find = needle
    items = haystack
    
    items,t = listify_safe(items)
    to_find = listify(to_find)
    
    if verbose:
        print(items, "\n", to_find)
    
    ret =  [i for i in items if any(j in i for j in to_find) ]

    ret  = unlistify(ret,t=t)
    
    if verbose:
        print(ret)
        
    return ret


def st_grep_on_off(what, to_find_on=None, to_find_off=None, n=1, rev=False, verbose=False):
  """
  filter a list of strings for groups delimited by "on" /"off"
  input:  list of strings
  output: list of strings
  
  use n to select how many groups to return
  
  warning: does not accept word_only yet!
  """
  
  lines,t = listify_safe(what)

  ret = []

  count_groups =0
  inside = False

  if to_find_on is None:
    inside = True


  for line in lines:
    if inside is False:
      if to_find_on and st_st_present(line, to_find_on):
        inside = True

        count_groups = count_groups + 1
        if n and count_groups > n:
          break   

    elif inside is True:
      if to_find_off and st_st_present(line, to_find_off):
        inside = False


    if inside:
      ret.append(line)

  ret = unlistify(ret,t=t)
  return ret

 

def ml_print(ml):
    for line in ml.splitlines():
        print(line)




def ml_grep_on_off(ml, *args, **kwargs):
    st = ml_to_st(ml, end=None, start=None, clean=False)

    st = st_grep_on_off(st, *args, **kwargs)
    ml = st_to_ml(st)
    return st
  
def ml_group_by(ml, n=2, end=None, start=None, clean=False, sep="      "):
    st = ml_to_st(ml, end=end, start=start, clean=clean)
    st = list_group_by(st, n=n)
    
    st = [ sep.join(i) for i in st ]
    return st
  
  
def ml_one_every_n(ml, n=2, end=None, start=None, clean=False):
    st = ml_to_st(ml, end=end, start=start, clean=clean)
    st = list_one_every_n(st, n)
    return st
  
  
    



import sys
#from error_exit import error_exit

def error_exit(what):
    die(what)


class Tee(object):
    def __init__(self, tee_filename):
        try:
            self.tee_fil = open(tee_filename, "w")
        except IOError as ioe:
            error_exit("Caught IOError: {}".format(repr(ioe)))
        except Exception as e:
            error_exit("Caught Exception: {}".format(repr(e)))

    def write(self, s):
        sys.stdout.write(s)
        self.tee_fil.write(s)

    def writeln(self, s):
        self.write(s + '\n')

    def close(self):
        try:
            self.tee_fil.close()
        except IOError as ioe:
            error_exit("Caught IOError: {}".format(repr(ioe)))
        except Exception as e:
            error_exit("Caught Exception: {}".format(repr(e)))
            


def test_tee():
    tee = Tee("test_tee.ttxt")
    tee.write("abc.\n")
    tee.writeln("abc")
    tee.close()
    
    
    
    
