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

import logging
import traceback

from secureclientserverservice import ScssProtocol
from .ScssServerInet import ScssServerInet


################################################################################
# Module                                                                       #
################################################################################

class ScssEchoServerInet(ScssServerInet):

    def clientActionNone(self, connection, ip, port):
        logging.info("Waiting  for data ...")
        inputFromClient = ScssProtocol.receiveNoneData(connection, self.max_buffer_size)
        logging.info("Received: {}".format(str(inputFromClient)))
        logging.info("Sending response ...")
        ScssProtocol.sendNoneData(connection, inputFromClient)
        logging.info("Response sent.")
        connection.close()
        logging.info('Connection ' + ip + ':' + port + " ended")

    def clientActionToken(self, connection, ip, port):
        try:
            data = ScssProtocol.receiveTokenData(connection, self.connectionSecurity, self.max_buffer_size)
            logging.info("Received: {}".format(data))
            ScssProtocol.sendTokenData(connection, self.connectionSecurity, data)
        except:
            logging.debug("Error for client action token.")
            logging.debug(str(traceback.format_exc()))
        finally:
            connection.close()
            logging.info('Connection ' + ip + ':' + port + " ended")

    def clientActionCertificate(self, connection, ip, port):
        logging.warning('CERTIFICATE access not implemented yet!')

################################################################################
#                                End of file                                   #
################################################################################
