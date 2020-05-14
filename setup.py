#!/usr/bin/env python3

import setuptools
import sys
import os
import sqlite3

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

     name='animated-memory',  

     version='0.2.3',

     scripts=['animated-memory'] ,

     author="Brian Posey",

     author_email="thebrianposey@gmail.com",

     description="A news aggregator with local training",

     long_description=long_description,

   long_description_content_type="text/markdown",

     url="https://github.com/mcpdude/animated-memory",

     packages=setuptools.find_packages(),

     install_requires=[
          'pyramid',
          'pyramid_mako',
          'transformers',
          'pandas',
          'simpletransformers',
          'torch',
          'torchvision'
      ],

     classifiers=[

         "Programming Language :: Python :: 3",

         "License :: OSI Approved :: MIT License",

         "Operating System :: OS Independent",

     ],

     data_files=[('templates', ['templates/list.mako', 'templates/layout.mako', 'templates/new.mako', 'templates/read.mako', 'templates/settings.mako']),
     			('scripts', ['scraper.py', 'train.py']),
     			('static', ['static/style.css']),
     			('sql', ['schema.sql'])]

 )