# -*- coding: utf-8 -*-
# * ********************************************************************* *
# *   Copyright (C) 2018 by xmz                                           *
# * ********************************************************************* *

'''
Secure Client-Server Service

@author: Marcin Zelek (marcin.zelek@gmail.com)
         Copyright (C) xmz. All Rights Reserved.
'''

################################################################################
# Import(s)                                                                    #
################################################################################

from .scsscommon import ScssCommon, ScssConfig
from .scsssecurity import ScssSecurityFirewall, ScssSecurityType, ScssSecurityHelper
from .scssprotocol import ScssProtocol
from .scssclient import ScssClient, ScssClientInet, ScssEchoClientInet
from .scssserver import ScssServer, ScssServerInet, ScssEchoServerInet, ScssServerUnix
from .scsshelper import ScssServerHelper, ScssClientHelper


################################################################################
# Module                                                                       #
################################################################################

def startServer(serverConfig):
    return False


def connectClient(connectionConfig):
    return False


__all__ = ('ScssCommon',
           'ScssConfig',
           'ScssProtocol',
           'ScssSecurityFirewall',
           'ScssSecurityType',
           'ScssSecurityHelper',
           'ScssClient',
           'ScssClientInet',
           'ScssEchoClientInet',
           'ScssServer',
           'ScssServerInet',
           'ScssEchoServerInet',
           'ScssServerUnix',
           'ScssServerHelper',
           'ScssClientHelper')

################################################################################
#                                End of file                                   #
################################################################################
