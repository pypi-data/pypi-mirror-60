from __future__ import absolute_import
from pwnlib.data.elf import relro

import os
path = os.path.dirname(__file__)

def get(x):
    return os.path.join(path, x)
