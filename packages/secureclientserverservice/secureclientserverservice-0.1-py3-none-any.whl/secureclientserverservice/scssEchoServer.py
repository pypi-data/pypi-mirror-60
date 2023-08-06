#! /bin/sh
# -*- coding: utf-8 -*-
""":"
exec python3 $0 ${1+"$@"}
"""
# * ********************************************************************* *
# *   Copyright (C) 2018 by xmz                                           *
# * ********************************************************************* *

'''
Example Secure Client-Server Service - Echo Server

@author: Marcin Zelek (marcin.zelek@gmail.com)
         Copyright (C) xmz. All Rights Reserved.
'''

################################################################################
# Import(s)                                                                    #
################################################################################

import sys
import signal
import argparse
import logging
import re

from secureclientserverservice import ScssConfig, ScssServerHelper

################################################################################
# Module Variable(s)                                                           #
################################################################################

versionString = "0.0.1"
applicationNameString = "SCSS Echo Server"
server = None


################################################################################
# Module                                                                       #
################################################################################

def parameters():
    defaultInetSocketPort = 72
    defaultInetSocketHost = "0.0.0.0"
    defaultFamily = 'INET'
    defaultUnixSocket = "/tmp/scss_unix_sockets"

    parser = argparse.ArgumentParser(description=applicationNameString)
    parser.add_argument('-v', '--version', action='version', version=applicationNameString + " - " + versionString)
    parser.add_argument('-f', '--family', choices={'INET', 'UNIX'}, default=defaultFamily, help='Server family')

    group = parser.add_mutually_exclusive_group(required=False)
    groupInet = group.add_mutually_exclusive_group(required=False)
    groupInet.add_argument('--host', default=defaultInetSocketHost,
                           help='Server host - "0.0.0.0" for all network interfaces and "127.0.0.1" or "localhost" for localhost connections. Default: ' + defaultInetSocketHost)
    groupInet.add_argument('--port', type=int, default=defaultInetSocketPort,
                           help='Server port. Default: ' + str(defaultInetSocketPort))
    groupUnix = group.add_mutually_exclusive_group(required=False)
    groupUnix.add_argument('--path', default=defaultUnixSocket,
                           help='Server socket location. Default: ' + defaultUnixSocket)

    parser.add_argument('-t', '--type', default='STREAM', choices={'STREAM'}, help='Socket type. Default: "STREAM".',
                        required=False)
    parser.add_argument('--jscConfigFilePath', type=argparse.FileType('r'),
                        help='Server JSC config file. When config file is provided all other server configs are ignored.',
                        required=False)
    loggingLeveChoices = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG
    }
    parser.add_argument('-ll', '--logging_level', dest="loggingLevel", choices=loggingLeveChoices.keys(),
                        help='Output log level', required=False)
    args, leftovers = parser.parse_known_args()

    args = vars(args)

    if 'jscConfigFilePath' in args and args['jscConfigFilePath']:
        args['jscConfigFilePath'] = args['jscConfigFilePath'].name
        argsConfig = ScssConfig.getConfig(args['jscConfigFilePath'])
        if argsConfig and isinstance(argsConfig, dict):
            for argConfigKey, argConfigValue in argsConfig.items():
                if argConfigKey is not None:
                    args[argConfigKey] = argConfigValue

    if args['loggingLevel'] is None:
        level = logging.CRITICAL
    else:
        level = loggingLeveChoices.get(args['loggingLevel'], logging.CRITICAL)
    logging.basicConfig(format='[%(asctime)s][%(levelname)-8s] [%(module)-20s] - %(message)s',
                        datefmt='%Y.%m.%d %H:%M.%S', level=level)
    logging.getLogger().setLevel(level)

    return args


def main(argv=sys.argv):
    signal.signal(signal.SIGINT, handler)
    args = parameters()
    logging.info('* Arguments:')
    for key, value in args.items():
        logging.info('** [{}]: [{}]'.format(' '.join(
            ''.join([w[0].upper(), w[1:].lower()]) for w in (re.sub("([a-z])([A-Z])", "\g<1> \g<2>", key)).split()),
            value))

    if args['loggingLevel'] == 'DEBUG':
        server = ScssServerHelper.instantiateEchoServer(args)
        if server is not None:
            server.start()
    else:
        try:
            server = ScssServerHelper.instantiateEchoServer(args)
            if server is not None:
                server.start()
        except:
            print('Error!')


def handler(signum, frame):
    sys.exit()


# Execute main function
if __name__ == '__main__':
    main()
    sys.exit()

################################################################################
#                                End of file                                   #
################################################################################
