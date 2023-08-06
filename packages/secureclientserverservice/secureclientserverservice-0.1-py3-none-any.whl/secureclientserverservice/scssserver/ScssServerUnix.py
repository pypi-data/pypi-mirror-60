# -*- coding: utf-8 -*-
# * ********************************************************************* *
# *   Copyright (C) 2018 by xmz                                           *
# * ********************************************************************* *

'''
@author: Marcin Zelek (marcin.zelek@gmail.com)
         Copyright (C) xmz. All Rights Reserved.
'''

################################################################################
# Import(s)                                                                    #
################################################################################

import socket
import logging

from .ScssServer import ScssServer


################################################################################
# Module                                                                       #
################################################################################

class ScssServerUnix(ScssServer):
    path = connectionType = maxConnection = None

    def __init__(self, path, connectionType=socket.SOCK_STREAM, maxConnection=1024):
        self.path = path
        self.connectionType = connectionType
        self.maxConnection = maxConnection

################################################################################
#                                End of file                                   #
################################################################################
