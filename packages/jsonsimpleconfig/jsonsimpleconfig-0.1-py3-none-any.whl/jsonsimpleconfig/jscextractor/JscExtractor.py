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
import json
import collections

from .JscHeader import JscHeader
from jsonsimpleconfig import JscData, JscSection, JscCommon


################################################################################
# Module                                                                       #
################################################################################

class JscExtractor:

    def __init__(self, jscData, options=None):
        self.__jscData = jscData
        self.__file = None
        self.__version = '1.0'
        self.__options = options

    def getVersion(self):
        return self.__version

    def __extractSectionToFile(self, sectionName):
        section = self.__jscData.getSection(sectionName)
        if isinstance(section, collections.Iterable):
            for item in section:
                self.__file.write(json.dumps({item:section[item]}).strip().lstrip("{").rstrip("}")+os.linesep)
            self.__file.write(os.linesep)

    def __extractDataToFile(self):
        if JscSection.GLOBAL_SECTION_NAME in self.__jscData.getSectionNames():
            self.__extractSectionToFile(JscSection.GLOBAL_SECTION_NAME)
        for sectionName in self.__jscData.getSectionNames():
            if sectionName != JscSection.GLOBAL_SECTION_NAME:
                self.__file.write('[' + sectionName + ']' + os.linesep)
                self.__extractSectionToFile(sectionName)

    def extractToFile(self, filePath):
        if self.__jscData is not None and isinstance(self.__jscData, JscData):
            self.__file = open(filePath, 'w', encoding='utf-8')
            if self.__file is not None:
                jscHeader = JscHeader({
                    'defaultHeader': True,
                    'allowCustomHeader': True,
                    'customHeaderFilePath': '/etc/jsonsimpleconfig/header.template',
                    'headerTemplateData':
                    {
                        'JscExtractor_version': self.__version,
                        'Jsc_timestamp': JscCommon.getTimestemp()
                    }
                }).str()
                if jscHeader is not None:
                    self.__file.write(jscHeader)
                self.__extractDataToFile()
                self.__file.close()

################################################################################
#                                End of file                                   #
################################################################################
