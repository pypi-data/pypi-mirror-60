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
import json
import logging

from .JscSection import JscSection


################################################################################
# Module                                                                       #
################################################################################

class JscData:

    def __init__(self):
        self.__section = JscSection()
        self.__jsc = {}

    def __sectionFromJson(self, sectionData):
        if isinstance(sectionData, dict):
            keys = list(sectionData.keys())
            if not keys:
                self.__section.down()
            else:
                for key, value in sectionData.items():
                    if isinstance(value, dict):
                        self.__section.up(key)
                        self.__sectionFromJson(value)
                    else:
                        sectionName = self.__section.str()
                        if sectionName is None:
                            sectionName = JscSection.GLOBAL_SECTION_NAME

                        if sectionName not in self.__jsc:
                            self.__jsc[sectionName] = {}
                        self.__jsc[sectionName][key] = value

                    if key == keys[-1]:
                        self.__section.down()

    def addSectionData(self, sectionName, sectionData):
        if sectionName[0] == '[':
            sectionName = sectionName.lstrip('[')
        if sectionName[-1] == ']':
            sectionName = sectionName.rstrip(']')
        for key, value in sectionData.items():
            if sectionName not in self.__jsc:
                self.__jsc[sectionName] = {}
            self.__jsc[sectionName][key] = value

    def addSectionJsonString(self, sectionName, sectionJsonString):
        try:
            sectionData = json.loads(sectionJsonString)
            self.addSectionData(sectionName, sectionData)

        except json.JSONDecodeError as e:
            logging.error(e.msg)
            logging.error(sys.exc_info())
            logging.error(sectionJsonString)
        except:
            logging.error(sys.exc_info())

    def getValue(self, sectionName, key, default=None) -> dict:
        value = default
        sectionData = self.getSection(sectionName)
        if sectionData:
            value = sectionData.get(key)
        return value

    def getSection(self, sectionName=None) -> dict:
        if sectionName is None or sectionName == '':
            sectionName = JscSection.GLOBAL_SECTION_NAME
        elif sectionName != JscSection.GLOBAL_SECTION_NAME:
            sectionName = sectionName.strip()
            if sectionName[0] != '"':
                sectionName = '"' + sectionName
            if sectionName[-1] != '"':
                sectionName = sectionName + '"'
        if sectionName in self.getSectionNames():
            return self.__jsc[sectionName]
        else:
            return None

    def getSectionNames(self):
        if self.__jsc is not None:
            return self.__jsc.keys()
        else:
            return None

    def merge(self, jscData):
        if jscData is not None and isinstance(jscData, JscData):
            sectionNames = jscData.getSectionNames()
            if sectionNames is not None:
                for sectionName in sectionNames:
                    sectionData = jscData.getSection(sectionName)
                    if isinstance(sectionData, dict):
                        for key in sectionData:
                            value = sectionData.get(key)
                            if sectionName not in self.__jsc:
                                self.__jsc[sectionName] = {}
                            self.__jsc[sectionName][key] = value

    def str(self) -> str:
        jscDataString = os.linesep
        sectionNames = self.getSectionNames()
        if sectionNames is not None:
            for sectionName in sectionNames:
                sectionPrint = "* Section"
                if sectionName == JscSection.GLOBAL_SECTION_NAME:
                    sectionPrint += " (Global):"
                else:
                    sectionPrint += " - {}:".format(sectionName)
                jscDataString += sectionPrint + os.linesep
                sectionData = self.getSection(sectionName)
                if isinstance(sectionData, dict):
                    for key in sectionData:
                        value = sectionData.get(key)
                        jscDataString += '*** [' + str(key) + '] : [' + str(value) + ']' + os.linesep

        return jscDataString

    def strHtml(self) -> str:
        return self.str().replace(os.linesep, '<br>' + os.linesep)

    def print(self):
        print(self.str())

    def printHtml(self):
        print(self.strHtml())

    def convertFromJson(self, jsonData):
        self.__sectionFromJson(jsonData)

    @staticmethod
    def fromJson(jsonData):
        jscData = JscData()
        jscData.convertFromJson(jsonData)
        return jscData

################################################################################
#                                End of file                                   #
################################################################################
