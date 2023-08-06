
from imports.internal   import *
from .dict           import *
from .pandas         import *



###
### source of these ideas: https://dsaber.com/2016/10/02/a-dramatic-tour-through-pythons-data-visualization-landscape-including-ggplot-and-altair/
###

def figsize_mpl_2_sns(figsize):
    size   = figsize[0]
    aspect = figsize[0]/figsize[1]
    
    return (size, aspect)


def internal_seaborn_facetgrid_myfunc(y, kind, **kwargs):
    data = kwargs.pop('data')
    #x = dict_remove_key(kwargs, 'x')
    ax = plt.gca()
    serie = data[y]

    if len(serie) == 0:
        print("WARNING: no data for CDF seaborn plot")
        print(y,kind)
      

    if kind == "cdf":
        serie_sorted = np.sort(serie)
        p = 1.0 * np.arange(len(serie)) / (len(serie) - 1)
        plt.plot(serie_sorted, p, **kwargs)
    elif kind == "dist":
        sns.distplot(serie, norm_hist=True, hist=False, kde=True)
    else:
        raise  ValueError('seaborn_FacetGridplot: unknown Kind')



def seaborn_FacetGridplot(data, y, kind="cdf"                 # args required 
                          , replace_NAs=True
                          , title="", figsize=None            # args SETTED to final grid
                          , xlim=None, ylim=None              # args SETTED to all subplots
                          , size=3, aspect=2, col_wrap=2      # args PASSED to aLL subplots
                          , sort_lines=True
                          , **kwargs):
    
    """
    main wrapper to FacetGrid.
    Please see options in https://seaborn.pydata.org/generated/seaborn.FacetGrid.html#seaborn.FacetGrid
    
    """


    #### NA problems:
    
    # fix:
    #    this function should remove all columns not useful to the breakdowns
    #    in this step, also check for typos on columns definitions
    #
    # quick-fix:
    #    instead, we just run fillna() on a copy of the dataframe
    if df_has_NAs(data):
        print_nonl("Warning: NAs found in given data (maybe in some unrelated columns). ")
        if replace_NAs:
            print("These will all be replaced by 0!")
            data = data.fillna(0, inplace=False) 
        else:
            print("NO ACTION TAKEN. Expect problems!")
            
    ####
    # adds defaults to kwargs
    #kwargs['col_wrap'] = col_wrap
    kwargs['size']   = size
    kwargs['aspect'] = aspect
    
    
    ### support breakdown lists by making the powerset on the fly
    ### https://seaborn.pydata.org/generated/seaborn.FacetGrid.html
    x              = dict_remove_key(kwargs, 'x')
    data, x        = df_melt_breakdown(data, x)
    kwargs['x']    = x

    hue            = dict_remove_key(kwargs, 'hue')
    data, hue      = df_melt_breakdown(data, hue)
    kwargs['hue']  = hue

    col            = dict_remove_key(kwargs, 'col')
    data, col      = df_melt_breakdown(data, col)
    kwargs['col']  = col

    row            = dict_remove_key(kwargs, 'row')
    data, row      = df_melt_breakdown(data, row)
    kwargs['row']  = row


        
    #df_assert_col_exists(data, [col, row, hue])

    if not (kind == "count"):
      assert(y)
      df_assert_col_exists(data, [y])


    ### force hues to be sorted
    # todo: do cols and rows as well
    x          = dict_remove_key(kwargs, 'x')
    hue        = dict_remove_key(kwargs, 'hue')
    hue_order  = dict_remove_key(kwargs, 'hue_order')

    # all the above are optional. Provide defaults in this case
    if (hue is None):
        hue = x
    if (x is None):
        x = hue
    if (hue is not None) and (hue_order is None):
        hue_order = np_unique_unsorted(data[hue], format_output="series")

    kwargs['hue']       = hue
    kwargs['hue_order'] = hue_order
    #############
    
    
    if (kind == "count"):
        # https://seaborn.pydata.org/generated/seaborn.catplot.html
        
        assert(y is None)

        y          = dict_remove_key(kwargs, 'y')

        hue        = dict_remove_key(kwargs, 'hue')
        hue_order  = dict_remove_key(kwargs, 'hue_order')
    
        if x is None:
          my_raise("countplot: need to specify either 'x' or 'hue'")

        g = sns.catplot(data=data, y=x, x=None, kind="count", **kwargs)
        
    elif (kind == "line") or (kind == "point"):
        hue_order = dict_remove_key(kwargs, 'hue_order')
        
        assert(x is not None)  # <<<<< IMPROVE THIS
        
        if (kind == "line"):
          sub_plt = plt.plot
          if sort_lines:
            data = data.sort_values(x)
        elif (kind == "point"):
          sub_plt = plt.scatter
        
        #x          = dict_remove_key(kwargs, 'x')
          
        g = sns.FacetGrid(data, **kwargs)
        g.map(sub_plt, x, y).add_legend()
      
    elif (kind == "box") or (kind=="bar"):
        # from https://seaborn.pydata.org/generated/seaborn.boxplot.html
        # "Using factorplot() is safer than using FacetGrid directly, as it ensures synchronization of variable order across facets"
        
        x_order  = dict_remove_key(kwargs, 'hue_order')   ## TODO!
        if x is None:
          x = dict_remove_key(kwargs, 'hue')
        
        g = sns.factorplot(x=x, y=y, data=data, kind=kind, **kwargs)


        
    else:
        # swap xlim - even if they dont exist!
        #kwargs = dict_swap_keys(kwargs, 'xlim', 'ylim')
        
        xlim, ylim = swap(xlim, ylim)
        
        g = sns.FacetGrid(data=data, **kwargs)
        g = g.map_dataframe(internal_seaborn_facetgrid_myfunc, y, kind)

    #sns.factorplot(data=df, x="extra", y='sepal_length', col="extra", sharey=True, kind='point', size=6, aspect=1.5).set_xticklabels(rotation=90).fig.suptitle("dede", y=1.02)  
    
    g.add_legend()
    set_kwargs = dict(xlim=xlim, ylim=ylim) #, figsize=figsize)
    g.set(**set_kwargs).fig.suptitle(title, y=1.05)
        
    return g
  


def seaborn_countplot(data, *, y=None, count_ylim=None, **kwargs):
    """
    Wrapper to catplot(kind="count")
    Note that "y" is always ignored, to keep compatibility with the CDFPLOT. Use "hue" or "x" instead!

    Please see seaborn_FacetGridplot() for parameter list
    """
    
    if not (y is None):
      print("Warning: specified 'y' parameter '%s'. CountPlot() always ignores this " % (y))

    return seaborn_FacetGridplot(data, y=None, kind="count", **kwargs)
    #ret = sns.catplot(data=data, y=None, x=x, hue=None, kind="count", ylim=count_ylim, **kwargs)


def seaborn_cdfplot_with_count(data, *, y=None, **kwargs):
    """
    shows two plots simultaneously (CDF + count)

    Please see seaborn_FacetGridplot() for parameter list
    """
    
    seaborn_cdfplot(data=data, y=y, **kwargs)
    seaborn_countplot(data=data, y=y, **kwargs)
    
    

def seaborn_cdfplot(data, y, **kwargs):
    """
    Wrapper to CDF calculated by hand.

    Please see seaborn_FacetGridplot() for parameter list
    """
    return seaborn_FacetGridplot(data, y, kind="cdf", **kwargs)







def seaborn_distplot(data, y, **kwargs):
    """
    Wrapper to sns.distplot(norm_hist=True, hist=False, kde=True)
    
    Please see seaborn_FacetGridplot() for parameter list
    """
    return seaborn_FacetGridplot(data, y, kind="dist", **kwargs)


def seaborn_boxplot(data, y, **kwargs):
    """
    Wrapper to sns.factorplot(kind="box")
    
    Please see seaborn_FacetGridplot() for parameter list
    """
    return seaborn_FacetGridplot(data, y, kind="box", **kwargs)


def seaborn_barplot(data, y, **kwargs):
    """
    Wrapper to sns.factorplot(kind="bar")
    
    Please see seaborn_FacetGridplot() for parameter list
    """

    # todo: warn on >30 row dataframes! 
    # pandas.plot.bar(x="date", y="something", figsize=(18,6), ylim=(0,1e5))
    return seaborn_FacetGridplot(data, y, kind="bar", **kwargs)


def seaborn_lineplot(data, y, **kwargs):
    """
    Wrapper to sns.FacetGrid().map(plt.plot)
    
    Please see seaborn_FacetGridplot() for parameter list
    """

    return seaborn_FacetGridplot(data, y, kind="line", **kwargs)


def seaborn_pointplot(data, y, **kwargs):
    """
    Wrapper to sns.FacetGrid().map(plt.scatter)
    
    Please see seaborn_FacetGridplot() for parameter list
    """
    return seaborn_FacetGridplot(data, y, kind="point", **kwargs)




def seaborn_tsplot(data, y, hue, time_col=None, **kwargs):
  """
  y: which columns to plot. They are melted automatically
  hue: column has the series names (=lines). The melted columns are added automatically
  time: which column has the time information. Default is to get it from the index
  """
  
  if time_col is None:
    time_col = data.index.name
  
  y = listify(y)
  hue = listify(hue)
  if len(y) > 0:
    data = df_melt(data, cols=y, key_name="key", val_name="value")
    y = "value"
    hue = list_append_items(hue, "key")
    
  data = data.reset_index()
  return seaborn_FacetGridplot(data, y=y, x=time_col, hue=hue, kind="line", **kwargs)


    
def mpl_get_ax_values(ax, serie=0):
    line = ax.lines[serie]
    return list(zip(line.get_xdata(), line.get_ydata()))
