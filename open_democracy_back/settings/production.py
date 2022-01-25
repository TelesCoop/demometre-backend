from .base import *

# SECURITY WARNING: define the correct hosts in production!

DEBUG = False

try:
    from .local import *
except ImportError:
    pass
