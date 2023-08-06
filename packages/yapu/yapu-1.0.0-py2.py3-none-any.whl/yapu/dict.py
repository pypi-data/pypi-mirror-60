
from .imports.internal   import *




def dict_copy(d):
    """
    copies a dict.
    """

    return d.copy()


def dict_compare(d1, d2):
    """
    compares all differences between 2x dicts.
    returns sub-dicts: "added", "removed", "modified", "same"
    """

    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o: (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return added, removed, modified, same


def dict_same(d1, d2):
    """
    returns if 2x dicts have the same contents (deep inpection)
    """

    added, removed, modified, same = dict_compare(d1, d2)

    if False:
        print(added, removed, modified, same)
        print(added == set())
        print(removed == set())
        print(same == set(d1.keys()))
    return (added == set()) & (removed == set()) & (same == set(d1.keys()))


def dict_get(d, key, default=None):
    """
    exactly the same as standard python. this is to remind that get() never raises an exception

    https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
    """
    return d.get(key, default)


def dict_remove_key(d, key, default=None):
    """
    removes a key from dict __WITH__ side effects
    Returns the found value if it was there (default=None). It also modifies the original dict.

    """
    return d.pop(key, default)


def dict_remove_key_safe(d, key, default=None):
    """
    removes a key from dict __WITHOUT__ side effects

    Returns:
     - copy of dict, without key
     - value (if it was there)
    """

    d = d.copy()
    value = d.pop(key, default)
    return (d, value)


def dict_sorted_items(d):
    """
    returns an iterator for the sorted dict.
    see also Ordered_dict()
    """

    return iter(sorted(d.items()))


def swap(a, b):
    return (b, a)


def dict_swap_keys(d, key1, key2):
    """
    swaps the values of 2x keys of a dict
    returns a new dict
    """

    d = d.copy()
    tmp1 = dict_remove_key(d, key1)
    tmp2 = dict_remove_key(d, key2)

    d[key1] = tmp2
    d[key2] = tmp1
    return d




#class dotdict(dict):
     #"""dot.notation access to dictionary attributes"""
     #def __getattr__(self, attr):
         #return self.get(attr)
     #__setattr__= dict.__setitem__
     #__delattr__= dict.__delitem__


#class BunchDict(dict):
    #def __init__(self,**kw):
        #dict.__init__(self,kw)
        #self.__dict__.update(kw)



def dict_invert_mapping(conv):
  """
  input: dictionary of lists
  output: dictionary of values: keys
  """
  
  ret = {v2: k1 for k1, v1 in conv.items() for v2 in v1}
  return ret


  
  
class Map(OrderedDict):
    """
    recursive OrderedDict-like class constructor that support full "dot" access (read and write).

    Example:
      m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'], sub_map = Map({'attribute_a':1, 'attribute_b':2}))
      m = Map({'first_name': 'Eduardo', 'last_name'='Pool', 'age':24, 'sports'=['Soccer'], 'sub_map': Map({'attribute_a':1, 'attribute_b':2}))

    source: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    comment: Recommend adding getstate and setstate so that deep copy and other systems can support it.


    """

    """
    options for "dotdict":
    Map(dict)
      - https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
      - recursive (with minor modification)
      - accepts dict and **kwargs


    dotmap
      - https://github.com/drgrib/dotmap

    Bunch
      - https://pypi.python.org/pypi/bunch


    argparse.namespace:
      - needs **dict at constructor
      - not recursive!

    namedtuple:
      - meta-method: creates "classes" dynamically
      - not recursive

    dataframes:
      access pattern:  df.col.index
        not recursive


    ####
    To force a sequence on the constructor:
      https://stackoverflow.com/questions/7878933/override-the-notation-so-i-get-an-ordereddict-instead-of-a-dict?answertab=votes#tab-top
      https://pypi.python.org/pypi/odictliteral/
        from odictliteral import odict
        x = odict[1:2,3:4]

    ####
    to support slicing:
      https://stackoverflow.com/questions/30975339/slicing-a-python-ordereddict
      https://stackoverflow.com/questions/21062781/shortest-way-to-get-first-item-of-ordereddict-in-python-3

        # from collections import OrderedDict
        from odict import OrderedDict as odict
        p = odict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])
        print( p[1:3])

    #####
    combined:

    d = Map(odict[
       "a":
         { "s1":1, "s2": 2},
       "b":
         { "s1":11, "s2": 22},
    ])

    """

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        v = Map(v)
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        if attr not in self:
            raise AttributeError(attr)
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]

    """
        Usage examples:
        m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
        # Add new key
        m.new_key = 'Hello world!'
        # Or
        m['new_key'] = 'Hello world!'
        print( m.new_key)
        print(m['new_key'])
        # Update values
        m.new_key = 'Yay!'
        # Or
        m['new_key'] = 'Yay!'
        # Delete key
        del m.new_key
        # Or
        del m['new_key']
    """

    