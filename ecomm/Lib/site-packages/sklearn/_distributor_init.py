
'''
Helper to preload the OpenMP dll to prevent "dll not found"
errors.
Once a DLL is preloaded, its namespace is made available to any
subsequent DLL. This file originated in the scikit-learn-wheels
github repo, and is created as part of the scripts that build the
wheel.
'''
import os
import os.path as op
from ctypes import WinDLL


if os.name == 'nt':
    # Pre-load the DLL stored in sklearn/.libs by convention.
    dll_path = op.join(op.dirname(__file__), '.libs', 'vcomp140.dll')
    WinDLL(op.abspath(dll_path))

