#!/usr/bin/env python

import os.path
import re
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    sys.exit()


with open('README.md') as f:
    long_description = f.read()


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                    read('gspread2/__init__.py'), re.MULTILINE).group(1)


setup(
    name='gspread2',
    version=version,
    packages=['gspread2'],
    url='https://gspread2.readthedocs.io',
    license='MIT',
    author='FutuereProjects',
    author_email='nclark@riseup.net',
    description='Wrapper for gspread',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
    install_requires=['gspread==3.2.0', 'oauth2client'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
)
