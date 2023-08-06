# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:17:53 2020

@author: abdulkadarb
"""

from setuptools import setup

setup(name='sgaimdbpull',
      version='1.0.1',
      install_requires=['requests','bs4'],
      description='Extract IMDB data',
      #url='http://github.com/storborg/funniest',
      author='AbdulkadarBabbar',
      author_email='abdulkadar.babbar@sganalytics.com',
      license='MIT',
      packages=['sgaimdbpull'],
      long_description="Get episode Count",
      zip_safe=False)
