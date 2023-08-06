
from .imports.base   import *

from .dict       import *
from .list       import *



# datastructure: list of dicts
# (can also be odict of dicts)
#
# creation:
#
#    conf = Map(odict[
#       "a":
#         { "s1":1, "s2": 2},
#       "b":
#         { "s1":11, "s2": 22},
#    ])
#






def db_get_field(db, field, *, flatten=True, remove_nones=False):
  """
    return list of values from db
  """

  my_assert(is_str(field))
  
  ret = [ db[i][field] for i in db ]
  
  if flatten:
    ret = list_flatten(ret, remove_nones)
    
  return ret


def db_set_field(db, field, data=None, *, strict=False, debug=False):
  """
    set all values from db
    data: 
     None/value - set all entries to value
     list - list of ordered values to add
    
    strict: list must be exact; else, Nones are added
  """

  my_assert(is_str(field))
  
  #debug=True
  len_db = len(db)
  
  if data is None:
    data = [None]*len_db
  elif not is_list(data):
    data = [data]*len_db
  else:
    pass
  
  print_debug(debug, "a:%d b:%d" % (len(db), len(data)))
  
  if len(db) == len(data):
    print_debug(debug, "same lenght")
    pass
  else:
    if strict:
      my_raise("db_set_field() needs list of the same size")
     
    data = list_make_same_len(data, db)
    print_debug(debug, data)
    
  #for i in range(len(db)):
  #  db[i][field] = data[i]
  
  for i, (k,v) in enumerate(db.items()):
    print_debug(debug, i, k, field, data[i])
    db[k][field] = data[i]
    
  return db



