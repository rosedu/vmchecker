#!/usr/bin/env python
"""Try to load all needed (and non-standard) python modules.
List all modules which could not be installed.
return 0 on success and 1 on error.
"""
import sys
if __name__ == "__main__":
    modules_to_load = sys.argv[1:]
    modules_not_loaded = []
    for m in modules_to_load:
        try:
            __import__(m)
        except:
            modules_not_loaded.append(m);
    if len(modules_not_loaded) > 0:
        print ("Could not load python modules: %s"  % modules_not_loaded)
        exit(1)
    else:
        print ("All needed python modules loaded correctly.")
        exit(0)

