# add packages that are imported as git submodules
# to sys module lookup path (workaround until buildout workflow is fixed)
import sys
import os

cur_path = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(cur_path, os.pardir, os.pardir))

submodule_dirs = ['hsmpy', 'quadpy']

for dirname in submodule_dirs:
    path = os.path.join(project_root, 'submodules', dirname)
    sys.path.insert(0, path)
