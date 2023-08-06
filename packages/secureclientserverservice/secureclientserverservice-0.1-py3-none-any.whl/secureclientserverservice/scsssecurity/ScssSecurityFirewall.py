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
import netaddr
import logging


################################################################################
# Module                                                                       #
################################################################################

class ScssSecurityFirewall:
    allow = None
    deny = ['127.0.0.1']
    enabled = False

    @staticmethod
    def load(config):
        scssSecurityFirewall = ScssSecurityFirewall()
        if 'Firewall' in config:
            configFirewall = config['Firewall']
            if 'enabled' in configFirewall and configFirewall['enabled'] is True:
                scssSecurityFirewall.enabled = True
                if 'allow' in configFirewall and isinstance(configFirewall['allow'], list):
                    scssSecurityFirewall.allow = configFirewall['allow']
                if 'deny' in configFirewall and isinstance(configFirewall['deny'], list):
                    scssSecurityFirewall.deny = configFirewall['deny']
        return scssSecurityFirewall

    def __str__(self):
        securityString = "Firewall enabled: [{}]".format(str(self.enabled)) + os.linesep
        securityString += "Firewall allow: [{}]".format(str(self.allow)) + os.linesep
        securityString += "Firewall deny: [{}]".format(str(self.deny)) + os.linesep
        return securityString

    @staticmethod
    def checkIpInNetworks(ip: str, networks: list) -> bool:
        """
        Validate ip in the list of networks
        :param ip: - ip to check
        :param networks: - list of network ranges
        :rtype: bool
        :return: True if ip is in range of networks, False otherwise
        """
        for network in networks:
            check = ScssSecurityFirewall.checkIpInNetwork(ip, network)
            if check:
                return True
        return False

    @staticmethod
    def checkIpInNetwork(ip: str, network: str) -> bool:
        """
        Validate if provided IP is in the range of network
        :param ip: - ip to check
        :param network: - network range
        :rtype: bool
        :return: True if ip is in range of network, False otherwise
        """
        ip = netaddr.IPNetwork(ip)
        network = netaddr.IPNetwork(network)

        if ip.version == network.version:
            ip = ip.first
            first = network.first
            last = network.last
            return first <= ip <= last
        else:
            logging.debug("Incompatible IP versions for [{}] and [{}].".format(str(ip), str(network)))

        return False

################################################################################
#                                End of file                                   #
################################################################################
