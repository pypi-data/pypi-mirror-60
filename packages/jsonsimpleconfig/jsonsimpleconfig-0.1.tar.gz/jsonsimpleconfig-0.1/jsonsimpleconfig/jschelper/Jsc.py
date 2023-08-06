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

import logging

from jsonsimpleconfig import JscParser


################################################################################
# Module                                                                       #
################################################################################

class Jsc:
    class __Jsc:
        def __init__(self, jscFile):
            self.__jscFile = jscFile
            logging.debug("Parsing JSC file: " + jscFile)
            jscParser = JscParser()
            self.__jscData = jscParser.parseFile(jscFile)

        __jscData = None

        def get(self):
            return self.__jscData

        def getFile(self):
            return self.__jscFile

    __instance = None

    @staticmethod
    def setLoggingLevel(level):
        logging.basicConfig(format='[%(asctime)s][%(levelname)-8s] [%(module)-20s] - %(message)s', datefmt='%Y.%m.%d %H:%M.%S', level=level)

    @staticmethod
    def setDebugLoggingLevel():
        Jsc.setLoggingLevel(logging.DEBUG)

    @staticmethod
    def get(jscFile, refresh=False):
        if refresh or \
           not Jsc.__instance or \
           Jsc.__instance.getFile() != jscFile:
            Jsc.__instance = Jsc.__Jsc(jscFile)

        return Jsc.__instance.get()

    @staticmethod
    def gets(jscData):
        jscParser = JscParser()
        return jscParser.parseString(jscData)

    @staticmethod
    def getValue(jscFile, section, key):
        jscData = Jsc.get(jscFile, True)
        if jscData is not None:
            return jscData.getValue(section, key)
        return None

################################################################################
#                                End of file                                   #
################################################################################
