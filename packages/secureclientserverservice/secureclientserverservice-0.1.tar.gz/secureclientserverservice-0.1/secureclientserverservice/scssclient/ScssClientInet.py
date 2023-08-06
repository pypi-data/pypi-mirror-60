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

from secureclientserverservice import ScssSecurityHelper, ScssSecurityType
from .ScssClient import ScssClient


################################################################################
# Module                                                                       #
################################################################################

class ScssClientInet(ScssClient):
    host = port = connectionType = clientSocket = None
    max_buffer_size = 8192
    timeout = None

    def __init__(self, host, port, connectionType=socket.SOCK_STREAM):
        self.host = host
        self.port = port
        self.connectionType = connectionType

    def setConnectionTimeout(self, timeout=10):
        self.timeout = timeout
        logging.debug("Set connection timeout to: [{}]".format(str(self.timeout)))

    def setConfiguration(self, config):
        if config is not None and 'timeout' in config:
            self.timeout = int(config['timeout'])
            if self.timeout <= 0:
                self.setConnectionTimeout()
            logging.debug("Set connection timeout: {}".format(str(self.timeout)))

    def setConnectionSecurity(self, connectionSecurity: ScssSecurityHelper):
        if connectionSecurity is not None and \
                isinstance(connectionSecurity, ScssSecurityHelper):
            self.connectionSecurity = connectionSecurity
            logging.debug("Set connection security to: {}".format(str(self.connectionSecurity)))

    @staticmethod
    def connect(host, port, connectionType=socket.SOCK_STREAM):
        scssClient = ScssClientInet(host, port, connectionType)
        if scssClient._connect():
            return scssClient
        else:
            return None

    def _connect(self):
        self.clientSocket = socket.socket(socket.AF_INET, self.connectionType)
        try:
            self.clientSocket.connect((self.host, self.port))
        except (OSError, TypeError) as message:
            logging.error(message)
            self.clientSocket.close()
            self.clientSocket = None
        return self.clientSocket is not None

    def send(self, data):
        super().send(data)
        if self.timeout is None:
            self.setConnectionTimeout(self.defaultTimeout)
        if self.clientSocket:
            if self.timeout:
                logging.debug("Socket Timeout: [{}]".format(str(self.clientSocket.gettimeout())))
                self.clientSocket.settimeout(self.timeout)
                logging.debug("Set Socket Timeout to: [{}]".format(str(self.timeout)))
                logging.debug("Socket Timeout: [{}]".format(str(self.clientSocket.gettimeout())))
        return self.sendAction(data)

    def sendAction(self, data):
        if self.connectionSecurity is None:
            receivedString = self.sendNone(data)
        else:
            if self.connectionSecurity.type == ScssSecurityType.CERTIFICATE:
                receivedString = self.sendCertificate(data)
            elif self.connectionSecurity.type == ScssSecurityType.TOKEN:
                receivedString = self.sendToken(data)
            else:
                receivedString = self.sendNone(data)

        return receivedString

################################################################################
#                                End of file                                   #
################################################################################
