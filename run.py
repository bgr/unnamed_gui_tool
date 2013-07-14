import sys
import os
import logging


# add packages that are imported as git submodules
# to sys module lookup path (workaround until buildout workflow is fixed)

cur_path = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(cur_path, os.pardir))

hsmpy_dir = os.path.join(project_root, 'submodules', 'hsmpy')

paths_to_insert = [hsmpy_dir]

for path in paths_to_insert:
    sys.path.insert(0, path)


# set loglevel

logging.basicConfig(level=logging.INFO)


# run app

from my_project import app
if __name__ == "__main__":
    app.run()
