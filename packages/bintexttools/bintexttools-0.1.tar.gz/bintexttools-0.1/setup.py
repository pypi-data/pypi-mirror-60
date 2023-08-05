# -*- coding: utf-8 -*-
# * ********************************************************************* *
# *   Copyright (C) 2018 by xmz                                           *
# * ********************************************************************* *

'''
Tools for binary and text data

@author: Marcin Zelek (marcin.zelek@gmail.com)
         Copyright (C) xmz. All Rights Reserved.
'''

################################################################################
# Import(s)                                                                    #
################################################################################

import os

from setuptools import setup

################################################################################
# Module                                                                       #
################################################################################

description = 'Tools for Binary and Text data.'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


try:
    long_description = read('README.rst')
except IOError:
    long_description = description

setup(
    name='bintexttools',
    version='0.1',
    description=description,
    long_description=long_description,
    keywords="binary ascii text hex base64 convert tools",
    author='Marcin Zelek',
    author_email='marcin.zelek@gmail.com',
    license='MIT',
    url='https://www.linkedin.com/in/marcin-zelek/',
    packages=['bintexttools',
              'bintexttools.bintextcommon',
              'bintexttools.bintexthelper'],
    entry_points=
    {
        'console_scripts':
        [
            'bin2text = bintexttools.bin2text:main',
            'text2bin = bintexttools.text2bin:main',
        ],
    },
    zip_safe=False
)

################################################################################
#                                End of file                                   #
################################################################################
