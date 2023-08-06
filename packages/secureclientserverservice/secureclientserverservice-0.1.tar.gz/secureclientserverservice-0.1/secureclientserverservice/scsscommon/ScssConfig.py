# -*- coding: utf-8 -*-
# * ********************************************************************* *
# *   Copyright (C) 2019 by Identity Bank EU                              *
# * ********************************************************************* *

'''
@author: Marcin Zelek (marcin.zelek@identitybank.eu)
         Copyright (C) Identity Bank. All Rights Reserved.
'''

################################################################################
# Import(s)                                                                    #
################################################################################

import jsonsimpleconfig


################################################################################
# Module                                                                       #
################################################################################

class ScssConfig:

    @staticmethod
    def getConfig(jscConfigFilePath: str) -> dict:
        configuration = jsonsimpleconfig.load(jscConfigFilePath)
        if not configuration:
            raise ValueError("Wrong configuration file!")

        if configuration:
            args = configuration.getSection(None)

            security = configuration.getSection('Security')
            if security is not None:
                args['Security'] = security

            securityFirewall = configuration.getSection('"Security"."Firewall"')
            if securityFirewall is not None:
                args['Firewall'] = securityFirewall

            return args

        return None

################################################################################
#                                End of file                                   #
################################################################################
