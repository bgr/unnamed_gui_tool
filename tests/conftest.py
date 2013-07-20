import logging
logging.basicConfig(level=logging.DEBUG)

# add packages that are imported as git submodules to sys module path:

import os

cur_path = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(cur_path, os.pardir, os.pardir))

hsmpy_dir = os.path.join(project_root, 'submodules', 'hsmpy')

paths_to_insert = [hsmpy_dir]

import sys
for path in paths_to_insert:
    sys.path.insert(0, path)
