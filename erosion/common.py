# -*- coding: utf-8 -*-

import os
import sys

from os.path import dirname

_CUR_PATH = os.path.dirname(os.path.abspath(__file__))
_PROJECTS_PATH = dirname(dirname(_CUR_PATH))
sys.path.append(_PROJECTS_PATH + '/clastic')
sys.path.insert(0, _PROJECTS_PATH + '/strata')

try:
    import clastic
except ImportError:
    print "couldn't import clastic"
    print "make sure you've got werkzeug and other dependencies installed"
    sys.exit(0)
