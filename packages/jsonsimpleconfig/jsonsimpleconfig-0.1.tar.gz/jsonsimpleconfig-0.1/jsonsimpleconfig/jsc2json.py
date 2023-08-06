#! /bin/sh
# -*- coding: utf-8 -*-
""":"
exec python3 $0 ${1+"$@"}
"""
# * ********************************************************************* *
# *   Copyright (C) 2018 by xmz                                           *
# * ********************************************************************* *

'''
Convert JSON Simple Config file to JSON

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

from jsonsimpleconfig import Jsc2JsonHelper

################################################################################
# Module Variable(s)                                                           #
################################################################################

versionString = "0.0.1"
applicationNameString = "JSC converter to JSON"


################################################################################
# Module                                                                       #
################################################################################

def parameters():
    parser = argparse.ArgumentParser(description=applicationNameString)
    parser.add_argument('-v', '--version', action='version', version=applicationNameString + " - " + versionString)
    parser.add_argument('-i', '--in', type=argparse.FileType('r'), help='Input file path (JSC file)', required=True)
    parser.add_argument('-o', '--out', type=argparse.FileType('w'), help='Output file path (JSON file)', required=False)
    loggingLeveChoices = {
        'CRITICAL': logging.CRITICAL,
        'ERROR':    logging.ERROR,
        'WARNING':  logging.WARNING,
        'INFO':     logging.INFO,
        'DEBUG':    logging.DEBUG
    }
    parser.add_argument('-ll', '--logging_level', dest="loggingLevel", choices=loggingLeveChoices.keys(), help='Output log level', required=False)
    args, leftovers = parser.parse_known_args()

    if vars(args)['loggingLevel'] is None:
        level = logging.CRITICAL
    else:
        level = loggingLeveChoices.get(vars(args)['loggingLevel'], logging.CRITICAL)
    logging.basicConfig(format='[%(asctime)s][%(levelname)-8s] [%(module)-20s] - %(message)s', datefmt='%Y.%m.%d %H:%M.%S', level=level)

    jscFile = (vars(args)['in']).name

    if vars(args)['out'] is None:
        jsonFile = jscFile + ".json"
    else:
        jsonFile = (vars(args)['out']).name

    return {'loggingLevel': (vars(args)['loggingLevel']), 'jsonFile': jsonFile, 'jscFile': jscFile}


def main(argv=sys.argv):
    signal.signal(signal.SIGINT, handler)
    args = parameters()

    if 'loggingLevel' in args and args['loggingLevel'] == 'DEBUG':
        Jsc2JsonHelper.convert(args['jscFile'], args['jsonFile'])
    else:
        try:
            Jsc2JsonHelper.convert(args['jscFile'], args['jsonFile'])
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
