

from .imports.internal   import *


###
### LIST wrapper functions. These functions ALWAYS return copies!
###

# https://wiki.python.org/moin/Powerful%20Python%20One-Liners

"""
Standard list functions

https://docs.python.org/2/tutorial/datastructures.html

list.append(x)
    a[len(a):] = [x].
list.extend(L)
    a[len(a):] = L.
list.insert(i, x)
    a.insert(0, x) inserts at the front 
    a.insert(len(a), x) is equivalent to a.append(x).
list.remove(x)
    Remove the first item from the list whose value is x
list.pop([i])
    Remove the item at the given position in the list, and return it
    
list.index(x)
  Return the index in the list of the first item whose value is x
list.count(x)
  Return the number of times x appears in the list.
list.sort(cmp=None, key=None, reverse=False)
  Sort the items of the list in place 
list.reverse()
  Reverse the elements of the list, in place.    
 
return values:
 Methods like insert, remove or sort that only modify the list  return the default None.
 http://openbookproject.net/thinkcs/python/english3e/lists.html
"""

# def any(iterable):
#     for element in iterable:
#         if element:
#             return True
#     return False



def list_group_by(lst, n=2):
    """
    group([0,3,4,10,2,3], 2) => [(0,3), (4,10), (2,3)]
    
    Group a list into consecutive n-tuples. Incomplete tuples are
    discarded e.g.
    
    >>> group(range(10), 3)
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    
    http://code.activestate.com/recipes/303060-group-a-list-into-sequential-n-tuples/
    """
    return list(zip(*[lst[i::n] for i in range(n)]))





def list_break(l, n=2):
  """
  Group a list into consecutive n-tuples. Incomplete tuples are NOT discarded

  list_break([1,2,3,4,5], 2)  => [[1, 2], [3, 4], [5]]
  list_break([1,2,3,4,5], 6)  => [[1, 2, 3, 4, 5]]


  https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
  """
  n = max(1, n)  
  ret = [l[x:x+n] for x in range(0, len(l),n)]
  return ret


def list_chunks(l, n=2):
  """
  splits the list in 2x parts. 
  Last list is not padded if too few elements. 
  
  list_chunks([1,2,3,4,5], 2)  => [[1, 2, 3], [4, 5]]
  list_chunks([1,2,3,4,5], 6)  => [[1], [2], [3], [4], [5], []]
  
  
  """
  ret = np.array_split(l, n)
  ret = [ list(i) for i in ret ]
  return ret






def list_move_to_front(_list, cols):
  _list = list_remove_items(_list, cols)
  new = cols + _list
  return new


def list_remove_items(_list, items, only_first=False):
    """
    removes several items from a list
    use only_first to limit it
    """
  
    _list = list_copy(_list)
    for item in items:
        _list = list_remove_item(_list, item, only_first=only_first)
    return _list

def list_remove_item(_list, item, only_first=False):
    """
    removes all occurences of an item from a list
    use only_first to limit it
    """
  
    _list = list_copy(_list)
    while list_item_inside(_list, item):
        _list.remove(item)
    return _list


def list_dump(l, st = None, sort=False):
    """
    dumps list elements with optional prefix and sort
    
    """
    
    if st:
        print ('Dumping List %s' % st)

    if sort:
        l = sorted(l)
        
    for i in l:
        print("\t", i)
        
def list_item_inside(_list, item):
    """
    is item in a list?
    """
    return (item in _list)

def list_any_items_inside(_list, *items):
    """
    is ANY of these items in a list?
    """
    return any([x in _list for x in items])

def list_all_items_inside(_list, *items):
    """
    is ALL of these items in a list?
    """
    return all([x in _list for x in items])

def list_count_item_occurences(_list, item):
    """
    how many times item appears in list?
    """
    return _list.count(item)

def list_item_first_index(_list, item):
    """
    returns the FIRST index of an item (or None if not there)
    """
    if list_item_inside(_list, item):
        return _list.index(item)
    else:
        return None
    
def list_item_last_index(_list, item):
    """
    returns the LAST index of an item (or None if not there)
    """
    if list_item_inside(_list, item):
        return len(_list) - 1 - _list[::-1].index(item)
    else:
        return None
    
def list_item_indexes(_list, item):
    """
    returns all indexes where an item appears in a list
    """
    ret = []
    for (i, val) in enumerate(_list):
        if val == item:
            ret.append(i)
    return ret

##############
def list_len(_list):
    """
    list length
    """
    return len(_list)


def list_reverse(_list):
    """
    reverse a copy of the list
    """
    _list = list_copy(_list)
    _list.reverse()
    return _list


def list_sort(_list):
    """
    sorts a copy of the list
    """
    _list = list_copy(_list)
    _list.sort()
    return _list


def list_equal(_list1, _list2):
    """
    are 2x lists equal (deep check)
    """
    return len(_list1) == len(_list2) and sorted(_list1) == sorted(_list2)


def list_copy(_list):
    """
    copy a list
    """

    # http://stackoverflow.com/questions/2612802/how-to-clone-or-copy-a-list
    #new_list = l[:]
    return list(_list)    

##############
# concat: multiple lists
# extend: multiple lists
# append: multiple items
# pre_something: do it in front, on the given 
def list_pre_append_items(_list, *items):
    """
    pre-appends items to a list
    
    example:
      list_pre_append_items([1,2], 99,98)  
      [99, 98, 1, 2]
    """

    return list_concat(items, _list)

#def prepend(item, list):
    #return list.insert(0,item)



def list_append_items(_list, *items):
    """
    appends items to a list
    
    example:
      list_append_items([1,2], 99,98)  
      [1, 2, 99, 98]
    """

    return list_concat(_list, items)

def list_pre_extend_lists(_list, *to_add):
    """
    pre-extends lists together
    
    example:
      list_pre_extend_lists([1,2],[7,8], ...)
      [7,8, 1, 2]
    """
    
    return list_concat(*to_add, _list)

def list_extend_lists(_list, *to_add):
    """
    extends lists together
    
    example:
      list_extend_lists([1,2],[7,8], ...)
      [7,8, ... , 1, 2]
    """
  
    return list_concat(_list, *to_add)
    
# note: this is the only base method we always use!
def list_concat(*lists):
    """
    joins multiple lists into a single list. Always returns a copy.
    
    """
  
    # base python: lists are concatenated with "+"
    ret = list()
    for l in lists:
        ret.extend(l)
    return ret


def list_make_same_len(a, b, value=None):
    """
    extends "a" to be the same size as "b", by adding value at the end
    """

    l_a = len(a)
    l_b = len(b)

    if l_a < l_b:
        missing = l_b - l_a
        a = list_append_items(a, *[value]*missing)
      
    if l_a > l_b:
        a = a[0:l_b]
      

    return a


def list_same_len(*lists):
    """
    confirm all lists have the same length
    """
  
    n = len(lists[0])
    return all(len(x) == n for x in lists)




def list_split_item(_list, item, method="first"):
  """
  splits a list in two. returns a tuple
  
  """
  
  list_start = 0
  list_end = list_len(_list)
  
  pos = list_item_first_index(_list, item)
  a = list_item_first_index(_list, item)
  b = list_item_last_index(_list, item)

  if method == "first":
      pos = a
  elif method == "last":
      pos = b
  else:
    my_raise("Unk method %s " % (method))

  ret_a = list_slice(_list, lisT_start, pos)
  ret_b = list_slice(_list, pos+1, list_end)
  
  return (ret_a, ret_b)


def list_split_pos(_list, pos):
  """
  splits a list in two. returns a tuple
  
  """
  
  list_start = 0
  list_end = list_len(_list)
  
  ret_a = list_slice(_list, list_start, pos)
  ret_b = list_slice(_list, pos+1, list_end)
  
  return (ret_a, ret_b)


def list_slice_item(_list, item, method="from_first+inclusive", *, debug=False):
    """
    slice list per location of item

    returns:
      a list, potentially empty

    use cases:
      12034056 0 [  ->    34056
      12034056 0 (  ->   034056
      12034056 0 ]  -> 12034
      12034056 0 )  -> 120340

      12034056 9 (  -> []

      12034056 0 [[ ->       56
      12034056 0 (( ->      056
      12034056 0 ]] -> 12
      12034056 0 )) -> 120

    """

    debug = True
    debug = False

    list_start = 0
    list_end = list_len(_list)

    first = list_item_first_index(_list, item)
    last = list_item_last_index(_list, item)

    print_debug(debug, "==> %s() " % (get_function_name()), item, method, first, last)

    if first is None:
        return []

    if False:
        pass

    elif method == "(" or method == "from_first+inclusive":
        a = first
        b = list_end
    elif method == "[" or method == "from_first+exclusive":
        a = first + 1
        b = list_end
    elif method == ")" or method == "until_last+inclusive":
        a = list_start
        b = last + 1
    elif method == "]" or method == "until_last+exclusive":
        a = list_start
        b = last


    elif method == "((" or method == "from_last+inclusive":
        a = last
        b = list_end
    elif method == "[[" or method == "from_last+exclusive":
        a = last + 1
        b = list_end
    elif method == "))" or method == "until_first+inclusive":
        a = list_start
        b = first + 1
    elif method == "]]" or method == "until_first+exclusive":
        a = list_start
        b = first

    else:
        my_raise("Unk method %s " % (method))

    a = max(a, list_start)
    b = min(b, list_end)

    ret = list_slice(_list, a, b)
    return ret



def list_slice(_list, start=None, end=None):
    """
    slice list, per index.
    see specialized functions below
    
    """
    list_start=0
    list_end=len(_list)
    
    if start is None:
        start = 0
    if end is None:
        end = list_end
    
    start = max(start, list_start)
    end = min(end, list_end)
        
    if end < start:
        end = start
        #print('empty')

    return _list[start:end]



def list_remove_first_elements(_list, n=1):
    start=n
    end=len(_list)
    return list_slice(_list, start=start, end=end)


def list_keep_first_elements(_list, n=1):
    start=0
    end=n
    return list_slice(_list, start=start, end=end)


def list_remove_last_elements(_list, n=1):
    start=0
    end=len(_list)
    end=end-n
    return list_slice(_list, start=start, end=end)


def list_keep_last_elements(_list, n=1):
    end=len(_list)
    start=end-n
    return list_slice(_list, start=start, end=end)


def list_remove_all_element_occurences(_list, elem):
    ret = [x for x in _list if x is not elem]
    return ret




def list_sort_by_elements_count(l):
  l = [list(x) for x in l]
  l.sort(key=lambda x: len(x), reverse=False)
  return l



def list_remove_nones(x):
    ret = []
    for el in x:
        if not (el is None):
            ret.append(el)
    return ret



def list_flatten(x, remove_nones=True):
    """
    flattens all elements presents in any possible sub-lists
    removes nones by default
    
    """
    ret = []
    for el in x:
        if hasattr(el, "__iter__") and not is_str(el):
            ret.extend(list_flatten(el))
        else:
            ret.append(el)

    if remove_nones:
      ret = list_remove_all_nones(ret)

    return ret


def list_diff(a,b, verbose=False):
  a = set(a)
  b = set(b)
  
  only_on_a = list(a - b)
  on_both = list(a.intersection(b))
  only_on_b = list(b - a)
  
  only_on_a = sorted(only_on_a)
  on_both = sorted(on_both)
  only_on_b = sorted(only_on_b)
  
  
  if verbose:
    print("\nOnly_on_a:\n\n", only_on_a)
    print("\nOn_both  :\n\n", on_both)
    print("\nOnly_on_b:\n\n", only_on_b)
    print("\n\n")
    
  return (only_on_a, on_both, only_on_b)


def list_diff_verbose(a,b, verbose=True):
    return list_diff(a,b,verbose=verbose)


def list_diff__only_a(a,b):
  return list_diff(a,b)[0]

def list_diff__intersection(a,b):
  return list_diff(a,b)[1]

def list_diff__only_b(a,b):
  return list_diff(a,b)[2]

  
  
      
def list_union(a,b):
    return list(set(a).union(b))

def list_intersection(a,b):
    return list(set(a).intersection(b))
  



  
def list_one_every_n(lst, n=2, end=None, start=None):
  if start and end:
    lst = lst[start:end]
  if start and not end:
    lst = lst[start:end]
  if not start and end:
    lst = lst[:end]
    
  lst = lst[::n] 
  return lst




def list_keep_duplicates(values):
  return list_remove_duplicates(values, invert=True)


def list_remove_duplicates(values, invert=False):
  output = []
  seen = set()
  for value in values:
    if (value not in seen) and (invert == False):
      output.append(value)
    if (value in seen) and (invert == True):
      output.append(value)
    seen.add(value)
  return output

  
def list_has_duplicates(values):
  """
  https://www.dotnetperls.com/duplicates-python
  """
  # For each element, check all following elements for a duplicate.
  for i in range(0, len(values)):
    for x in range(i + 1, len(values)):
      if values[i] == values[x]:
        return True
  return False
  

def list_assert_no_duplicates(values):
  if list_has_duplicates(values):
    my_raise("List has duplicates")
  return None



# we basically want all functions with support for remaing Nones. eg, append_ignore_nones, len_in, etc

def list_remove_all_nones(_list):
    return list_remove_all_element_occurences(_list, None)


def min_nones(*args):
    """
    min(), ignoring nones
    """
    ret = min(v for v in args if v is not None)
    return ret


def max_nones(*args):
    """
    max(), ignoring nones
    """
    ret = max(v for v in args if v is not None)
    return ret



def list_strictly_increasing(L):
    return all(x<y for x, y in zip(L, L[1:]))

def list_strictly_decreasing(L):
    return all(x>y for x, y in zip(L, L[1:]))

def list_non_increasing(L):
    return all(x>=y for x, y in zip(L, L[1:]))

def list_non_decreasing(L):
    return all(x<=y for x, y in zip(L, L[1:]))

def list_monotonic(L):
    return list_non_decreasing(L) or list_non_increasing(L)

    
    
    
