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

class ScssClient(ScssProtocol):
    connectionType = None
    clientSocket = None
    defaultTimeout = 10
    connectionSecurity = None

    def send(self, data):
        logging.info("Sending data ...")

    @abstractmethod
    def sendAction(self, data):
        pass

################################################################################
#                                End of file                                   #
################################################################################
