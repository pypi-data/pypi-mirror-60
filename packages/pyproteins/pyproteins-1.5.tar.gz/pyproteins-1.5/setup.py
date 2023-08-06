#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

setup(
  name = 'pyproteins',
  version = '1.5',
  license='BSD',
  description = 'Toolbox to manipulate protein sequence data',
  author = 'Guillaume Launay & Cecile Hilpert',
  author_email = 'pitooon@gmail.com',
  url = 'https://github.com/glaunay/pyproteins', # use the URL to the github repo
  packages=find_packages('src'),
  package_dir={'': 'src'},
  include_package_data=True,
  zip_safe=False,
  py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
  download_url = 'https://github.com/glaunay/pyproteins/tarball/1.4', # I'll explain this in a second
  keywords = ['protein', 'sequence'], # arbitrary keywords
  classifiers = [],
  install_requires=[
          'bs4', 'biopython', 'numpy','lxml'
      ],
   package_data = {
   'pyproteins': ['conf/confModule1.json','bin/module1.py', 'external/*']
   },
  #data_files=[
  #          ('external', ['external/pathos.tar.bz']),
  #          ('bin', ['bin/module1.py']),
  #          ('conf',['conf/confModule1.json'])
  #    ]
  #  dependency_links = [
  #      "http://dev.danse.us/trac/pathos"
  #  ]
)
