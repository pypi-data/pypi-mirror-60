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

import logging

from abc import abstractmethod
from secureclientserverservice import ScssProtocol


################################################################################
# Module                                                                       #
################################################################################

class ScssServer(ScssProtocol):
    connectionSecurityFirewall = None
    connectionSecurity = None
    connectionType = None
    maxConnection = None

    def start(self):
        logging.info("Starting server ...")

    @abstractmethod
    def clientAction(self, connection, ip, port):
        pass

################################################################################
#                                End of file                                   #
################################################################################
