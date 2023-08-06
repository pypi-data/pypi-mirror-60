# -*- coding: utf-8 -*-

# from distutils.core import setup
from setuptools import setup, find_packages

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

import augmentedtree

setup(
    name="augmentedtree",
    version=augmentedtree.__version__,
    author="David Scheliga",
    author_email="david.scheliga@ivw.uni-kl.de",
    url="https://gitlab.uni-kl.de/scheliga/augmentedtree",
    description="Easy navigation within nested data of mappings (dict, ...) and "
    "sequences (list, ...). Easy access of values via single keys within"
    " these nested data structures. Enables different (human accessable)"
    " representation of nested data structures.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GNU General Public License v3 (GPLv3)",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
    ],
    keywords="dictionary, mapping, list, sequence, nested, handling, navigation, selection",
    python_requires=">=3.6",
    packages=find_packages(),
    requires=["pandas", 'numpy'],
)
