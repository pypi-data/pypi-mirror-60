
from ..imports.internal   import *


###
### Lib config changes go here:
###
if True:
    ### this is for jupyter notebooks only!
    # %config    IPcompleter.greedy = True
    # %matplotlib    inline
    # %matplotlib %notebook              # Zoomable version
    # warnings.filterwarnings('ignore')
    pass


### configs functions go here
def conf_jupyter_small_display():
    pd.set_option('display.width', 10000)
    pd.set_option('display.max_columns', 1200)
    pd.set_option('display.max_rows', 100)


def conf_jupyter_large_display():
    conf_df_small_display()

    #pd.set_option('display.width', 10000)
    #pd.set_option('display.max_columns', 10000)
    #pd.set_option('display.max_rows', 10000)


def conf_jupyter_expressions_verbose():
    # http://ipython.readthedocs.io/en/stable/config/options/terminal.html
    # InteractiveShell.ast_node_interactivity
    #   ‘all’, ‘last’, ‘last_expr’ or ‘none’, ‘last_expr_or_assign’

    InteractiveShell.ast_node_interactivity = "all"


def conf_jupyter_expressions_normal():
    # http://ipython.readthedocs.io/en/stable/config/options/terminal.html
    # InteractiveShell.ast_node_interactivity
    #   ‘all’, ‘last’, ‘last_expr’ or ‘none’, ‘last_expr_or_assign’
    #   Default:	'last_expr'

    InteractiveShell.ast_node_interactivity = "last_expr"


def conf_ignore_warnings():
    warnings.filterwarnings('ignore')

def conf_enable_warnings():
    warnings.filterwarnings('default')
    
    
    