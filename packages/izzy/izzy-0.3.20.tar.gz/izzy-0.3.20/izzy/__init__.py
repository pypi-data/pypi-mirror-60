
from .classification import *
from .datasets import *
from .defaults import *
from .eda import *
from .features import *
from .io import *
from .misc import *
from .regression import *
from .tests import *
from .version import __version__
from .viz import *

# TODO pandas.modin for speedup? Make this an option

__all__ = [
    'classification',
    'datasets',
    'eda',
    'features',
    'io',
    'misc',
    'regression',
    'set_theme',  # from defaults
    'tests',
    '__version__',
    'viz',
]
