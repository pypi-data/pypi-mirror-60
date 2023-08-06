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
import re


################################################################################
# Module                                                                       #
################################################################################

class JscComments:

    @staticmethod
    def stripComments(text):

        def replacer(match):
            startGroup = match.group(0)
            if startGroup.startswith(';') or \
               startGroup.startswith('#') or \
               startGroup.startswith('/'):
                return " "
            else:
                return startGroup

        pattern = re.compile(
            r'#.*?$|;.*?$|//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )

        replaced = re.sub(pattern, replacer, text)

        return os.linesep.join([s for s in replaced.splitlines() if s.strip()])

    @staticmethod
    def stripCommentsFile(inFilePath, outFilePath):
        inFile = open(inFilePath)
        if inFile:
            if inFile.readable():
                outFile = open(outFilePath, 'w', encoding='utf-8')
                if outFile:
                    if outFile.writable():
                        outFile.write(JscComments.stripComments(inFile.read()))
                    outFile.close()
            inFile.close()


################################################################################
#                                End of file                                   #
################################################################################
