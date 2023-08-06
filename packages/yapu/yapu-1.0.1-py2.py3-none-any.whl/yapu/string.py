

from .imports.internal   import *


# python string functions: https://docs.python.org/3.7/library/string.html
#

##
## SINGLE STRING functions
##

def st_trim(st):
    return st.strip()


def st_crop(st):
    return st.strip()


def st_reverse(st):
    # https://stackoverflow.com/questions/931092/reverse-a-string-in-python

    assert is_str(st)
    return st[::-1]


def st_splitchars(what, seps=None, maxsplit=-1):
    """
    like split(), but accepts multiple separators

    https://stackoverflow.com/questions/1059559/split-strings-with-multiple-delimiters
    https://docs.python.org/3.7/library/string.html
    https://docs.python.org/3.7/library/stdtypes.html#str.split


    ########### oficial documenation follwos

    str.split(sep=None, maxsplit=-1)

    Return a list of the words in the string, using sep as the delimiter string.
    If maxsplit is given, at most maxsplit splits are done (thus, the list will have at most maxsplit+1 elements).
    If maxsplit is not specified or -1, then there is no limit on the number of splits (all possible splits are made).

    If sep is given, consecutive delimiters are not grouped together and are deemed to delimit empty strings (
    for example, '1,,2'.split(',') returns ['1', '', '2']). The sep argument may consist of multiple characters
    (for example, '1<>2<>3'.split('<>') returns ['1', '2', '3']). Splitting an empty string with a
    specified separator returns [''].

    For example:
    >>>
    >>> '1,2,3'.split(',')
    ['1', '2', '3']
    >>> '1,2,3'.split(',', maxsplit=1)
    ['1', '2,3']
    >>> '1,2,,3,'.split(',')
    ['1', '2', '', '3', '']

    If sep is not specified or is None, a different splitting algorithm is applied: runs of consecutive whitespace are
    regarded as a single separator, and the result will contain no empty strings at the start or end if the string has
    leading or trailing whitespace. Consequently, splitting an empty string or a string consisting of just whitespace
    with a None separator returns [].

    For example:
    >>> '1 2 3'.split()
    ['1', '2', '3']
    >>> '1 2 3'.split(maxsplit=1)
    ['1', '2 3']
    >>> '   1   2   3   '.split()
    ['1', '2', '3']
    """

    def st_splitchars_1(st, seps=None, maxsplit=-1):
        seps = listify(seps)
        magic = seps[0]  # fixme...

        for sep in seps:
            st = st.replace(sep, magic)

        return st.split(magic, maxsplit=maxsplit)

    lines, t = listify_safe(what)
    lines = [st_splitchars_1(line, seps=seps, maxsplit=maxsplit) for line in lines]
    return unlistify(lines, t=t)



def st_join_enumerate(items, sep="SEP", comma=","):
    """
    joins strings using an sequential seperator

    example:
      st_join_enumerate(["a","b","c"])
      'a,SEP1,b,SEP2,c'
    """

    ret = ""
    for (a, b) in enumerate(items):
        if a == 0:
            ret = b
        else:
            ret += comma + sep + str(a) + comma + b
    return ret


def st_st_present(st, needle):
    """
    is a substring present in a string?

    example:
      st_st_present("abcd", "bc")
      True
    """
    assert is_str(st)

    return st.find(needle) != -1


def st_replace(st, old, new=None, maxreplace=None):
    """
    wrapper to string replace, with optional "New" and "maxreplace"
    old supports "listify()"

    example:
      st_replace("123--67--90", "--", "__", 1)
      '123__67--90'
    """

    assert is_str(st)

    old_l = listify(old)

    for old in old_l:
        # print(st, old)
        if maxreplace:
            st = st.replace(old, new, maxreplace)
        else:
            st = st.replace(old, new)

    return st


def st_remove(st, old, maxreplace=None):
    """
    remove a substring from a string
    """

    assert is_str(st)

    return st_replace(st, old, new="", maxreplace=maxreplace)


def st_substitute(st, do_print=False, locals=None, globals=None, **kwargs):
    """
    wrapper to "Template", to use "${variable}" perl style
    raises assertions if variables have typos

    example:
      template = "hello $name "
      name ="pedro"
      st_substitute(template, **locals())
    """

    assert is_str(st)

    st = string.Template(st)

    if locals is None:
        ret = st.substitute(**kwargs)
    else:
        ret = st.substitute(**(locals + kwargs))

    if do_print:
        print(ret)

    return ret




#############
def int2str(f, leading_zeros=0):
    total_digits = leading_zeros
    ret = '{:d}'.format(int(f)).zfill(total_digits)
    return ret


def float2str(f, fractional_digits=1, leading_zeros=0):
    total_digits = leading_zeros + 1 + fractional_digits
    ret = '{:.0{}f}'.format(f, fractional_digits).zfill(total_digits)
    return ret


def float2float(f, fractional_digits=1, leading_zeros=0):
    return float(float2str(f, fractional_digits, leading_zeros))


def rchop(thestring, ending):
    if thestring.endswith(ending):
        return thestring[:-len(ending)]
    return thestring





# regular expressions go here
# http://pythex.org/ 

# test regular expressions
# https://regex101.com/

def is_word(st):
  return re.match(r"[a-zA-Z][a-zA-Z_]*", st.strip())
  
  


# regular expression editor: http://pythex.org/
def st_is_comment(st):
    """
    matches if a string is a comment. it ignores whitespace at the front
    also matches SQL comments
    """

    assert is_str(st)

    st = st.strip()

    return re.match("#.*", st) or re.match("--.*", st)
  


def st_clean_prefix(st, prefix, *, reverse=False, format_output="dict"):
  """
  from a list of strings:
    - filters the ones that start with a prefix
    - for these, removes the prefix
  
  both string and prefix can be lists.
  
  returns a dictionary for conversion.
  
  Can also return 2x lists: 
    - the filtered list with the prefix in every string 
    - the filtered list without the prefix in every string
  """
  
  out1 = []
  out2 = []
  
  st_list = listify(st, debug=False)
  prefix_list = listify(prefix)
  
  for st in st_list:
    for prefix in prefix_list:
      if ((    st.startswith(prefix) and (reverse == False)) or 
         (not st.startswith(prefix) and (reverse == True))):
          out1.append(st) 
          new_st = st[len(prefix):]
          out2.append(new_st)
          break
  
  
  if format_output=="2_lists":
    return (out1, out2 )
  elif format_output=="dict":
    # https://stackoverflow.com/questions/23030645/create-dictionary-from-2-lists
    # see also: #dict(zip(list1, chain(list2, repeat(None))))
    d = dict(zip(out1,out2))
    
    
    return d
  else:
    my_raise("unk out format")
    
    
    
    
class about_string_prefixes(str):
  """
  Custom mutable string class, with built-in regular expressions.
  
  other:
    https://stackoverflow.com/questions/10572624/mutable-strings-in-python
    https://stackoverflow.com/questions/7255655/how-to-subclass-str-in-python

  collections.userstring:
  """
    
  """  
  list of lexical prefixes:
    https://docs.python.org/3.6/reference/lexical_analysis.html#string-and-bytes-literals
  
  https://stackoverflow.com/questions/52360537/i-know-of-f-strings-but-what-are-r-strings-are-there-others
      strings: "\n" is a new line
    f-strings: format strings: "hello {name}"
    r-strings: raw literals:   "\n" is a backslash and the character 'n'
    b-strings: binary literals
    u-strings: unicode literals
  
  """
  


class RString(collections.UserString):
  """
  Implements mutable strings with regex methods. Suitable for chaining regexs.
  Also has built in debug.
  
  ----
  Mutable strings in python:
    question:  https://stackoverflow.com/questions/10572624/mutable-strings-in-python
    answer:    https://stackoverflow.com/questions/50875028/python-how-to-pass-an-instance-variable-to-method-as-implicit-argument-general/50878149#50878149
    code:      https://github.com/python/cpython/blob/e2e7ff0d0378ba44f10a1aae10e4bee957fb44d2/Lib/collections/__init__.py#L1098
    other:     https://stackoverflow.com/questions/7255655/how-to-subclass-str-in-python
    
  Regular Expressions:
    functions:    https://docs.python.org/2/library/re.html#re.sub
    simulator1:   https://regex101.com/
    simulator2:   https://pythex.org/

  Flags:
    re.DEBUG
    re.VERBOSE          Allows comments and whitespace 

    re.IGNORECASE       (ASCCII only)
    re.MULTILINE        '^' matches beginning of string + each neline; same for '$'
    re.DOTALL           '.' matches '\n'
    
    re.LOCALE
    re.UNICODE          \w, \W, \b, \B, \d, \D, \s, \S depends on locale/unicaode
  """
  
  def __init__(self, string, debug=False):
      super().__init__(string)
      self.debug = debug
        
        
  def re_sub_front(*args, **kwargs):
    self.re_sub(*args, front=False, **kwargs)

  
  def re_sub(self, pattern, repl="", count=0, flags=0, front=False):
    """
    wrapper to regex substitution
    #https://docs.python.org/2/library/re.html#re.sub
    """
    
    extra_help="""
    Return the string obtained by replacing the leftmost non-overlapping occurrences of pattern in string by the 
    replacement repl. If the pattern isn’t found, string is returned unchanged. 
    repl can be a string or a function; if it is a string, any backslash escapes in it are processed. 
    That is, \n is converted to a single newline character, \r is converted to a carriage return, and so forth. 
    Unknown escapes such as \j are left alone. Backreferences, such as \6, are replaced with the 
    substring matched by group 6 in the pattern.

    If repl is a function, it is called for every non-overlapping occurrence of pattern. 
    The function takes a single match object argument, and returns the replacement string. 

    The pattern may be a string or an RE object.

    The optional argument count is the maximum number of pattern occurrences to be replaced; 
    count must be a non-negative integer. If omitted or zero, all occurrences will be replaced. 
    Empty matches for the pattern are replaced only when not adjacent to a previous match, 
    so sub('x*', '-', 'abc') returns '-a-b-c-'.

    In string-type repl arguments, in addition to the character escapes and backreferences described above, 
    \g<name> will use the substring matched by the group named name, as defined by the (?P<name>...) syntax. 
    \g<number> uses the corresponding group number; \g<2> is therefore equivalent to \2, but isn’t ambiguous 
    in a replacement such as \g<2>0. \20 would be interpreted as a reference to group 20, not a reference to 
    group 2 followed by the literal character '0'. The backreference \g<0> substitutes in the entire substring 
    matched by the RE.
    """
    
    if self.debug:
      print("re_sub before: %s" % (self.data))
    
    pat_list = listify(pattern)
    
    for pat in pat_list:
      if front:
        pt = "^%s" % (pat)
    
      self.data = re.sub(pat, repl, self.data, count, flags)
      
    
    if self.debug:
      print("re_sub after: %s" % (self.data))
    
    return self
    
    
  def re_subn(self, pattern, repl, count=0, flags=0):
    """
    Perform the same operation as sub(), but return a tuple (new_string, number_of_subs_made).
    """
    
    self.data, number_of_subs = re.subn(pattern, repl, self.data, count, flags)
    
    return (self.data, number_of_subs)
    

  def re_debug_match(self, function, pattern, ret):
    if self.debug:
      print("%s result: %s %s" % ( function, pattern,  "[found]" if ret else "[not found]" ))
    
    
  def re_search(self, pattern, flags=0):
    """
    Scan through string looking for the first location where the regular expression pattern produces a match,
    and return a corresponding MatchObject instance. 
    Return None if no position in the string matches the pattern
    """
    
    ret = re.search(pattern, self.data, flags)
    
    self.re_debug_match("re_search", pattern, ret)
    
    return ret

    
  def re_match(self, pattern, flags=0):
    """   
    If zero or more characters at the beginning of string match the regular expression pattern, 
    return a corresponding MatchObject instance. Return None if the string does not match the pattern; 
    """

    ret = re.match(pattern, self.data, flags)
    
    self.re_debug_match("re_match", pattern, ret)
    
    return ret

    
  def re_split(self, pattern, maxsplit=0, flags=0):
    """
    Split string by the occurrences of pattern. 
    
    If capturing parentheses are used in pattern, then the text of all groups in the pattern are also 
    returned as part of the resulting list. 
    If maxsplit is nonzero, at most maxsplit splits occur, and the remainder of the string is 
    returned as the final element of the list. 
    """
    
    ret = re.split(pattern, self.data, maxsplit, flags)
    
    if debug:
      print("re_split return: %d slices" % (len(ret)))
      
    return ret    
    
    
  def re_findall(self, pattern, flags=0):
    """
    Return all non-overlapping matches of pattern in string, as a list of strings. 
    The string is scanned left-to-right, and matches are returned in the order found. 
    If one or more groups are present in the pattern, return a list of groups; 
    this will be a list of tuples if the pattern has more than one group. 
    Empty matches are included in the result.
    """
    
    ret = re.findall(pattern, self.data, flags)
    
    if debug:
      print("re_findall: return %d slices" % (len(ret)))
      
    return ret  
    
    
  def re_finditer(self, pattern, flags=0):
    """
    Return an iterator yielding MatchObject instances over all non-overlapping matches for the RE pattern in string. 
    The string is scanned left-to-right, and matches are returned in the order found. 
    Empty matches are included in the result. See also the note about findall().
    """
    
    ret = re.finditer(pattern, self.data, flags)
    
    if debug:
      pass
      #print("re_split: return %d slices" % (len(ret)))
      
    return ret  
    

  def re_escape(self):
    """
    Escape all the characters in pattern except ASCII letters and numbers. 
    This is useful if you want to match an arbitrary literal string that may have regular expression 
    metacharacters in it. 
    """
  
    self.data = re.escape(self.data)

    if debug:
      print("re_esacle return: %s" % (self.data))
    
    return self
    
    
  def re_remove_words(self, words):
    words = listify(words)
    
    for word in words:
      tokens = [i for i in self.data.split() if i != word ]
      self.data = " ".join(tokens) 
      
    return self
    
    
  def len(self):
    """
    A string length method. This enables writing left-to-right expressions.
    """
    
    return len(self.data)
  
  
  def strip3(self):
    """
    A string length method. This enables writing left-to-right expressions.
    """
    
    self.data = self.data.strip()
    return self

  
  def empty(self, strip=True):
    """
    checks if string is empty. Strips by default
    """
    
    if strip:
      self.strip()
      
    return self.len() == 0  
  
  
  def unicode_clean(self):
    """
    see also https://ftfy.readthedocs.io/en/latest/
    """
    #self.data = 
    self.data = self.data.replace('\u2013', "-")
    return self
    
    
class RStringD(RString):
  def __init__(self, string, debug=True):
      super().__init__(string, debug)

    
    
def unittest_String():
  #print( RString('dede dededd').re_sub('\s'))
  #print( RString('dede dededd').re_sub('\s').len())
  assert( RString('dede dededd').re_sub('\s').len() == 10 )
    
    
#unittest_String()

    