#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import open
from setuptools import setup

version = '0.0.1'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='make-sure',
    version=version,

    author='python273',
    author_email='make-sure@python273.pw',

    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/python273/make-sure',
    download_url='https://github.com/python273/make-sure/archive/v{}.zip'.format(
        version
    ),

    license='MIT',

    packages=['make_sure'],

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
