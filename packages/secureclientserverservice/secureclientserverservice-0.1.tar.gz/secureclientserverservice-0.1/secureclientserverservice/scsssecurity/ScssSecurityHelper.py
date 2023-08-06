# -*- coding: utf-8 -*-
# * ********************************************************************* *
# *   Copyright (C) 2019 by xmz                                           *
# * ********************************************************************* *

'''
@author: Marcin Zelek (marcin.zelek@gmail.com)
         Copyright (C) xmz. All Rights Reserved.
'''

################################################################################
# Import(s)                                                                    #
################################################################################

import os
from enum import Enum


################################################################################
# Module                                                                       #
################################################################################

class ScssSecurityHelper:
    type = None
    chunks = False
    securityOptions = None
    latestVersion = 1
    messageAttributesSize = {
        'protocolVersion': 4,
        'size': 8,
        'id': 8,
        'checksumType': 8
    }
    checksumSize = {
        'MD5': 32
    }

    @staticmethod
    def load(config):
        scssSecurity = ScssSecurityHelper()
        scssSecurity.type = ScssSecurityType.fromString('none')
        if 'Security' in config:
            security = config['Security']
            if 'type' in security:
                scssSecurity.type = ScssSecurityType.fromString(security['type'])
                scssSecurity.setupToken(security)
        return scssSecurity

    def setupToken(self, configToken: dict):
        self.securityOptions = {
            'tokenSizeBytes': 2,
            'protocolVersion': ScssSecurityHelper.latestVersion,
            'tokens': None,
            'token': None,
            'checksumType': 'MD5'
        }
        for key, value in configToken.items():
            self.securityOptions[key] = configToken[key]

    def __str__(self):
        securityString = "Security Type: [{}]".format(str(ScssSecurityType.toString(self.type))) + os.linesep
        securityString += "Security Options: [{}]".format(str(self.securityOptions)) + os.linesep
        return securityString


class ScssSecurityType(Enum):
    NONE = 0
    TOKEN = 1
    CERTIFICATE = 2

    @staticmethod
    def fromString(typeName: str):
        returnData = {
            'NONE': ScssSecurityType.NONE,
            'TOKEN': ScssSecurityType.TOKEN,
            'CERTIFICATE': ScssSecurityType.CERTIFICATE
        }
        return returnData.get(typeName.upper(), ScssSecurityType.NONE)

    @staticmethod
    def toString(type):
        returnData = {
            ScssSecurityType.NONE: 'NONE',
            ScssSecurityType.TOKEN: 'TOKEN',
            ScssSecurityType.CERTIFICATE: 'CERTIFICATE'
        }
        return returnData.get(type, '')

################################################################################
#                                End of file                                   #
################################################################################
