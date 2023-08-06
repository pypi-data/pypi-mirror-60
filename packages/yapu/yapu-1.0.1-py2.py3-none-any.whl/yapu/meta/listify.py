
from ..imports.internal   import *

from ..debug.debug   import print_debug
from ..debug.debug   import print_debug



###
### STRING wrapper functions. These functions ALWAYS return copies!
###

# awk string functions: https://www.gnu.org/software/gawk/manual/html_node/String-Functions.html
# python string functions: https://docs.python.org/2/library/string.html

def is_dict(var):
    """
    is this a dict-like?
    """
    # see also  collections.Mapping
    return isinstance(var, dict)

def is_iterable(var):
    """
    is this iterable (INCLUDES str)
    """
    return isinstance(var, collections.Iterable)

def is_set(var):
    """
    is this a set
    """

    return isinstance(var, (set))

def is_list(var, *, debug=False):
    """
    is this a list or tuple? (DOES NOT include str)
    """

    print_debug(debug, "is_list: got type %s" % (type(var)))
    return isinstance(var, (list, tuple)) #, pd.core.frame.DataFrame))    #numpy.ndarray  ???  <<<<< this has a bug!


def is_str(var):
    """
    is this a string?
    """

    # python2:
    # return isinstance(var, basestring)
    return isinstance(var, str)

def is_item(var):
    """
    is this a single item
    """
    return is_str(var) or (not is_iterable(var))

def is_dataframe(var):
    """
    is this a DF?
    """
    
    raise NotImplemented
    
    return isinstance(var, (pd.core.frame.DataFrame))


def is_number(var):
    """
    is this a Number?
    """

    return isinstance(var, numbers.Number)


def is_int(var):
    """
    is this an integer (ie, not a float)? 
    """

    return isinstance(var, int)




def is_datetime(var):
    """
    is this an DT
    """

    return isinstance(var, (datetime.datetime, datetime.date))



def is_index(var):
    """
    is this a DF index?
    """

    return isinstance(var, (pd.core.indexes.base.Index))




#####

def listify_safe(what, *, debug=False):
    """
    upgrade input to a list (except if it was already a list or set)
    returns (list, original_type) to enable reversibility later

    output #1 is __ALWAYS__ a list, to enable iteration

    ---------------
    use case #1:  "None" means "no columns"
      cols = listify(cols)
      for col in cols:
          <do stuff>

    use case #2:  "None" means "all columns"
      cols = df_listify(df, cols)
      for col in cols:
          <do stuff>
    
    --------------
    TODO: expand this to be a class, with __getitem__
    """

    print_debug(debug, "listify: processing type %s" % (type(what)))
    
    if what is None:
        print_debug(debug, "listify: got None")
        return ([], 'none')
    elif is_set(what):
        print_debug(debug, "listify: got set()")
        return (list(what), 'set')
    elif is_list(what):
        print_debug(debug, "listify: got list()")
        return (list(what), 'list')         # calling list() on a list == NO ACTION
    else:
        print_debug(debug, "listify: got fallback")
        return ([what], 'item')


def listify(what, *, debug=False):
    """
    non-reversible version of listify_safe(). In this case "None" always means "no columns".
    output: list
    """
    l, _ = listify_safe(what, debug=debug)
    return l


def df_listify(df, what=None, expand_cols=True):
    if what is None:
        if expand_cols:
            return list(df.columns)
        else:
            return None
    else:
        return listify(what)



def unlistify(what, *, t):
    """
    safely reverses listify(), using the original type.
    """

    origtype = t

    if not is_list(what):
        raise ValueError("un listify_safe(): did not received a list")

    if origtype == "none":
        if what == []:
            return None
        else:
            raise ValueError("un listify_safe(): input was None, but output is not the empty list")

    elif origtype == "list":
        return what

    elif origtype == "set":
        return set(what)

    elif origtype == "item":
        if len(what) == 0:
            return None
        elif len(what) == 1:
            return what[0]
        else:
            raise ValueError("un listify_safe(): input was item, but output is multiple items")
