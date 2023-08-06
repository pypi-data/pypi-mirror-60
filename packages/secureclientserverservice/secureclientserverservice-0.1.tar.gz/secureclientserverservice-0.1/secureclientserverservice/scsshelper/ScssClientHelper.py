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

from secureclientserverservice import ScssEchoClientInet, ScssSecurityHelper


################################################################################
# Module                                                                       #
################################################################################

class ScssClientHelper:

    @staticmethod
    def connect(config):
        logging.info('Client config ...')
        logging.info(json.dumps(config, indent=4))
        scssClient = ScssEchoClientInet.connect(config['host'], config['port'])
        if scssClient:
            scssClient.setConfiguration(config)
            scssClient.setConnectionSecurity(ScssSecurityHelper.load(config))
        return scssClient

################################################################################
#                                End of file                                   #
################################################################################
