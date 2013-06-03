import os
from setuptools import setup, find_packages

# def read(fname):
#     return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "jython_test_project",
    version = "0.0.1",
    description = ("My Jython Test Project"),
    author = "bgr",
    author_email = "bgrgyk@gmail.com",
    url = "",
    packages = find_packages(),
    install_requires = [
        #"pytest >= 2.3.5",
    ]

)
