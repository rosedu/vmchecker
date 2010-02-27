#!/usr/bin/env python
"""Try to load all needed (and non-standard) python modules.
List all modules which could not be installed.
return 0 on success and 1 on error.
"""
import sys

def check_modules_loading(modules_to_load):
    """Check modules loading correctly."""
    modules_not_loaded = []
    for module in modules_to_load:
        try:
            __import__(module)
        except ImportError:
            modules_not_loaded.append(module)
    if len(modules_not_loaded) > 0:
        print ("Could not load python modules: %s"  % modules_not_loaded)
        exit(1)
    else:
        print ("All needed python modules loaded correctly.")
        exit(0)

if __name__ == "__main__":
    check_modules_loading(sys.argv[1:])
