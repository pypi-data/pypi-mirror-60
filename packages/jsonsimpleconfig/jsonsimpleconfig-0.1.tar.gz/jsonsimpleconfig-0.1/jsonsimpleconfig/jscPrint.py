#! /bin/sh
# -*- coding: utf-8 -*-
""":"
exec python3 $0 ${1+"$@"}
"""
# * ********************************************************************* *
# *   Copyright (C) 2018 by xmz                                           *
# * ********************************************************************* *

'''
Return JSON Simple Config print config file

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
import json

from jsonsimpleconfig import Jsc, JsonExtractor

################################################################################
# Module Variable(s)                                                           #
################################################################################

versionString = "0.0.1"
applicationNameString = "JSC print"


################################################################################
# Module                                                                       #
################################################################################

def parameters():
    parser = argparse.ArgumentParser(description=applicationNameString)
    parser.add_argument('-v', '--version', action='version', version=applicationNameString + " - " + versionString)
    parser.add_argument('-i', '--in', type=argparse.FileType('r'), help='Input file path (JSC file)', required=True)
    parser.add_argument('-f', '--format', choices={'TEXT', 'HTML', 'JSON'}, help='The output format', required=False)
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

    return {'jscFile': (vars(args)['in']).name, 'format': (vars(args)['format'])}


def main(argv=sys.argv):
    signal.signal(signal.SIGINT, handler)
    args = parameters()
    jscData = Jsc.get(args['jscFile'])
    if jscData is not None:
        if args['format'] is not None and "HTML".lower() == args['format'].lower():
            jscData.printHtml()
        elif args['format'] is not None and "JSON".lower() == args['format'].lower():
            jsonExtractor = JsonExtractor(jscData)
            if jsonExtractor is not None:
                jsonExtractor.extractDataToJson()
                try:
                    jsonString = json.dumps(jsonExtractor.getJson(), ensure_ascii=False)
                except json.JSONDecodeError as e:
                    jsonString = None
                if jsonString is not None:
                    print(jsonString)
        else:
            jscData.print()


def handler(signum, frame):
    sys.exit()


# Execute main function
if __name__ == '__main__':
    main()
    sys.exit()

################################################################################
#                                End of file                                   #
################################################################################
