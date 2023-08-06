# -*- coding: utf-8 -*-
# * ********************************************************************* *
# *   Copyright (C) 2018 by xmz                                           *
# * ********************************************************************* *

'''
Secure Client-Server Service Setup

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

description = 'Secure client-server service library.'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


try:
    long_description = read('README.rst')
except IOError:
    long_description = description

setup(
    name='secureclientserverservice',
    version='0.1',
    description=description,
    long_description=long_description,
    keywords="secure client server service",
    author='Marcin Zelek',
    author_email='marcin.zelek@gmail.com',
    license='MIT',
    url='https://github.com/xmzxmz',
    packages=['secureclientserverservice',
              'secureclientserverservice.scsscommon',
              'secureclientserverservice.scssprotocol',
              'secureclientserverservice.scsshelper',
              'secureclientserverservice.scsssecurity',
              'secureclientserverservice.scssclient',
              'secureclientserverservice.scssserver'],
    entry_points=
    {
        'console_scripts':
        [
            'scssEchoServer = secureclientserverservice.scssEchoServer:main',
            'scssEchoClient = secureclientserverservice.scssEchoClient:main',
        ],
    },
    zip_safe=False
)

################################################################################
#                                End of file                                   #
################################################################################
