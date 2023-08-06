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

import json
import logging

from secureclientserverservice import ScssSecurityFirewall, ScssSecurityHelper, ScssEchoServerInet


################################################################################
# Module                                                                       #
################################################################################

class ScssServerHelper:

    @staticmethod
    def instantiateEchoServer(config):
        logging.info('Server config ...')
        logging.info(json.dumps(config, indent=4))
        scssServer = ScssEchoServerInet(config['host'], config['port'])
        if scssServer:
            scssServer.setConfiguration(config)
            scssServer.setConnectionFirewall(ScssSecurityFirewall.load(config))
            scssServer.setConnectionSecurity(ScssSecurityHelper.load(config))
        return scssServer

################################################################################
#                                End of file                                   #
################################################################################
