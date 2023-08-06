# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(
    name='MxDateTimeWrap',
    version='1.0.2',
    description=u'Wrap mx.DateTime functions using native datetime',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Sindri (Trackwell hf.)',
    author_email='sindri@trackwell.com',
    url='http://www.trackwell.com/',
    packages=find_packages('.')
)
