from __future__ import absolute_import
import sys
from sys import  stderr
from importlib import reload
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)



__version__ = '0.3.6'
stderr.write('trident {0}\n'.format(__version__))
import threading
from .backend import *

from .models import *
from .callbacks  import *

