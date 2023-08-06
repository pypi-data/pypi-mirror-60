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

import socket
import logging

from secureclientserverservice import ScssProtocol
from .ScssClientInet import ScssClientInet


################################################################################
# Module                                                                       #
################################################################################

class ScssEchoClientInet(ScssClientInet):

    @staticmethod
    def connect(host, port, connectionType=socket.SOCK_STREAM):
        scssClient = ScssEchoClientInet(host, port, connectionType)
        if scssClient._connect():
            return scssClient
        else:
            return None

    def sendNone(self, data):
        receivedString = None
        try:
            logging.debug("Send [None] data.")
            ScssProtocol.sendNoneData(self.clientSocket, data)
            logging.debug("Data sent.")
            receivedString = ScssProtocol.receiveNoneData(self.clientSocket, self.max_buffer_size)
            logging.debug("Data received.")
            logging.debug("Data [{}]".format(receivedString))
        except socket.timeout:
            logging.debug("Connection timeout.")

        return receivedString

    def sendToken(self, data):
        receivedString = None
        try:
            if ScssProtocol.sendTokenData(self.clientSocket, self.connectionSecurity, data):
                receivedString = ScssProtocol.receiveTokenData(self.clientSocket, self.connectionSecurity,
                                                               self.max_buffer_size)
        except socket.timeout:
            logging.debug("Connection timeout.")

        return receivedString

    def sendCertificate(self, data):
        logging.warning('CERTIFICATE access not implemented yet!')
        return None

################################################################################
#                                End of file                                   #
################################################################################
