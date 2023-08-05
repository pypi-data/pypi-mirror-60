import datafaucet as dfc
from datafaucet.decorators import add_method

from pandas import DataFrame

# monkey patching: try to limit to a minimum

# 2 methods and 3 attributes in total
# df.save, df.datafaucet
# df.rows, df.cols, df.data

DataFrame.save = dfc.io.save

@add_method(DataFrame)
def datafaucet(self):
    return {'object': 'dataframe', 'type': 'pandas', 'version':dfc.__version__}

from .rows import *
from .cols import *
from .data import *
