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

import os
import sys
import socket
import logging
import traceback

from threading import Thread

from secureclientserverservice import ScssSecurityType, ScssSecurityFirewall, ScssSecurityHelper, ScssProtocol
from .ScssServer import ScssServer


################################################################################
# Module                                                                       #
################################################################################

class ScssServerInet(ScssServer):
    host = port = connectionType = maxConnection = None
    max_buffer_size = 8192
    timeout = None

    def __init__(self, host, port,
                 connectionType=socket.SOCK_STREAM,
                 maxConnection=1024):
        self.host = host
        self.port = port
        self.connectionType = connectionType
        self.maxConnection = maxConnection

    def setConnectionTimeout(self, timeout=5):
        self.timeout = timeout
        logging.debug("Set connection timeout to: [{}]".format(str(self.timeout)))

    def setConfiguration(self, config):
        if config is not None and 'timeout' in config:
            self.timeout = int(config['timeout'])
            if self.timeout <= 0:
                self.setConnectionTimeout()
            logging.debug("Set connection timeout: {}".format(str(self.timeout)))

    def setConnectionFirewall(self, connectionSecurityFirewall: ScssSecurityFirewall):
        if connectionSecurityFirewall is not None and \
                isinstance(connectionSecurityFirewall, ScssSecurityFirewall):
            self.connectionSecurityFirewall = connectionSecurityFirewall
            logging.debug("Set connection firewall: {}{}".format(os.linesep, str(self.connectionSecurityFirewall)))

    def setConnectionSecurity(self, connectionSecurity: ScssSecurityHelper):
        if connectionSecurity is not None and \
                isinstance(connectionSecurity, ScssSecurityHelper):
            self.connectionSecurity = connectionSecurity
            logging.debug("Set connection security to: {}".format(str(self.connectionSecurity)))

    def start(self):
        super().start()
        logging.info("Starting Inet server ...")
        serverSocket = socket.socket(socket.AF_INET, self.connectionType)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            serverSocket.bind((self.host, self.port))
            logging.info("Socket bind complete: [{}:{}]".format(self.host, self.port))
        except socket.error as msg:
            logging.error('Bind failed. Error: {}, {}'.format(msg, str(sys.exc_info())))
            return

        serverSocket.listen(self.maxConnection)
        logging.info('Socket now listening')

        while True:
            connection, client = serverSocket.accept()
            ip, port = str(client[0]), str(client[1])
            logging.info('Accepting connection from ' + ip + ':' + port)
            try:
                if self.validateFirewall(connection, ip, port):
                    Thread(target=self.safeClientAction, args=(connection, ip, port)).start()
                else:
                    connection.close()
                    logging.debug("Connection was rejected on firewall: [{}:{}]".format(ip, port))
            except:
                logging.error("Client error!")
                logging.debug(str(traceback.format_exc()))
        serverSocket.close()

    def validateFirewall(self, connection, ip, port):
        allow = False
        if self.connectionSecurityFirewall and self.connectionSecurityFirewall.enabled:
            if self.connectionSecurityFirewall.deny is not None and \
                    isinstance(self.connectionSecurityFirewall.deny, list):
                denyValidation = ScssSecurityFirewall.checkIpInNetworks(ip, self.connectionSecurityFirewall.deny)
                if denyValidation:
                    return False
            if self.connectionSecurityFirewall.allow is not None and \
                    isinstance(self.connectionSecurityFirewall.allow, list):
                allowValidation = ScssSecurityFirewall.checkIpInNetworks(ip, self.connectionSecurityFirewall.allow)
                if allowValidation:
                    allow = True
        else:
            allow = True
        return allow

    def safeClientAction(self, connection, ip, port):
        if self.timeout is None:
            self.setConnectionTimeout()
        if self.timeout:
            logging.debug("Socket Timeout: [{}]".format(str(connection.gettimeout())))
            connection.settimeout(self.timeout)
            logging.debug("Set Socket Timeout to: [{}]".format(str(self.timeout)))
            logging.debug("Socket Timeout: [{}]".format(str(connection.gettimeout())))

        if logging.getLevelName(logging.getLogger().getEffectiveLevel()) == 'DEBUG':
            self.clientAction(connection, ip, port)
        else:
            try:
                self.clientAction(connection, ip, port)
            except:
                logging.error('Error executing safe client action! Skipping...')

    def clientAction(self, connection, ip, port):
        if self.connectionSecurity is None:
            self.clientActionNone(connection, ip, port)
        else:
            if self.connectionSecurity.type == ScssSecurityType.CERTIFICATE:
                self.clientActionCertificate(connection, ip, port)
            elif self.connectionSecurity.type == ScssSecurityType.TOKEN:
                self.clientActionToken(connection, ip, port)
            else:
                self.clientActionNone(connection, ip, port)

################################################################################
#                                End of file                                   #
################################################################################
