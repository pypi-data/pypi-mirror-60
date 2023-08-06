# -*- coding: utf-8 -*-
# * ********************************************************************* *
# *   Copyright (C) 2018 by xmz                                           *
# * ********************************************************************* *

'''
JSON Simple Config Setup

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

description = 'The simple idea to prepare configuration for your application.'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


try:
    long_description = read('README.rst')
except IOError:
    long_description = description

setup(
    name='jsonsimpleconfig',
    version='0.1',
    description=description,
    long_description=long_description,
    keywords="json configuration jsc simple config",
    author='Marcin Zelek',
    author_email='marcin.zelek@gmail.com',
    license='MIT',
    url='https://github.com/xmzxmz/jsonsimpleconfig',
    package_data={'': ['jscresources/*.template']},
    include_package_data=True,
    packages=['jsonsimpleconfig',
              'jsonsimpleconfig.jsccommon',
              'jsonsimpleconfig.jscdata',
              'jsonsimpleconfig.jscextractor',
              'jsonsimpleconfig.jschelper',
              'jsonsimpleconfig.jscparser'],
    entry_points=
    {
        'console_scripts':
        [
            'json2jsc = jsonsimpleconfig.json2jsc:main',
            'jsc2json = jsonsimpleconfig.jsc2json:main',
            'jscValue = jsonsimpleconfig.jscValue:main',
            'jscPrint = jsonsimpleconfig.jscPrint:main',
        ],
    },
    zip_safe=False
)

################################################################################
#                                End of file                                   #
################################################################################
