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

import collections
import json

from jsonsimpleconfig import JscData, JscSection


################################################################################
# Module                                                                       #
################################################################################

class JsonExtractor:

    def __init__(self, jscData, options=None):
        self.__jscData = jscData
        self.__jsonData = {}
        self.__file = None
        self.__version = '1.0'
        self.__options = options

    def getVersion(self):
        return self.__version

    def getJson(self):
        return self.__jsonData

    def __extractSectionToJson(self, sectionName):
        branches = sectionName.split(JscSection.SECTION_GLUE)
        jsonData = self.__jsonData
        if isinstance(branches, collections.Iterable):
            for branch in branches:
                branch = branch.strip().strip('"')
                if branch != JscSection.GLOBAL_SECTION_NAME:
                    if branch not in jsonData:
                        jsonData[branch] = {}
                    jsonData = jsonData[branch]
        section = self.__jscData.getSection(sectionName)
        if isinstance(section, collections.Iterable):
            for item in section:
                jsonData[item]=section[item]

    def extractDataToJson(self):
        if JscSection.GLOBAL_SECTION_NAME in self.__jscData.getSectionNames():
            self.__extractSectionToJson(JscSection.GLOBAL_SECTION_NAME)
        for sectionName in self.__jscData.getSectionNames():
            if sectionName != JscSection.GLOBAL_SECTION_NAME:
                self.__extractSectionToJson(sectionName)

    def extractToFile(self, filePath):
        if self.__jscData is not None and isinstance(self.__jscData, JscData):
            self.extractDataToJson()
            try:
                jsonString = json.dumps(self.__jsonData, ensure_ascii=False, indent=4)

            except json.JSONDecodeError as e:
                jsonString = None

            if jsonString is not None:
                self.__file = open(filePath, 'w', encoding='utf-8')
                if self.__file is not None:
                    self.__file.write(jsonString)
                    self.__file.close()

################################################################################
#                                End of file                                   #
################################################################################
