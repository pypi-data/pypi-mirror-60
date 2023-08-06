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

import sys

from jsonsimpleconfig import JscComments, JscData, JscSection


################################################################################
# Module                                                                       #
################################################################################

class JscParser:

    def __init__(self):
        self.__jscData = None
        self.__currentSection = None
        self.__currentSectionData = None

    def __newSection(self, sectionName):
        if sectionName[0] == '[':
            sectionName = sectionName.lstrip('[')
        if sectionName[-1] == ']':
            sectionName = sectionName.rstrip(']')
        if sectionName != JscSection.GLOBAL_SECTION_NAME:
            sectionName = sectionName.strip()
            if sectionName[0] != '"':
                sectionName = '"' + sectionName
            if sectionName[-1] != '"':
                sectionName = sectionName + '"'

        self.__currentSection = sectionName
        self.__currentSectionData = '{'

    def __endSection(self):
        self.__currentSectionData += '}'
        if self.__jscData == None:
            self.__jscData = JscData()

        sectionName = self.__currentSection
        jsonString = self.__currentSectionData
        self.__currentSectionData = self.__currentSection = None
        self.__jscData.addSectionJsonString(sectionName, jsonString)

    def __parseLine(self, line):
        line = JscComments.stripComments(line)
        line = line.strip()
        if line:
            if line[0] == '[' and line[-1] == ']':
                if self.__currentSection != None and \
                   self.__currentSectionData != None:
                    self.__endSection()
                self.__newSection(line)

            else:
                if self.__currentSection == None and \
                   self.__currentSectionData == None:
                    self.__newSection(JscSection.GLOBAL_SECTION_NAME)
                if self.__currentSectionData != '{':
                    self.__currentSectionData += ','
                self.__currentSectionData += line

    def parseFile(self, jscFile, parseLineByLine=False) -> JscData:
        self.__jscData = None
        try:
            with open(jscFile) as jscFile:

                if jscFile.readable():
                    if parseLineByLine:
                        for line in jscFile:
                            self.__parseLine(line)
                    else:
                        jscText = JscComments.stripComments(jscFile.read())
                        lines = jscText.splitlines()
                        for line in lines:
                            self.__parseLine(line)
            self.__endSection()
            jscFile.close()

        except:
            self.__jscData = None

        finally:
            return self.__jscData

    def parseString(self, jscString) -> JscData:
        self.__jscData = None
        try:
            jscText = JscComments.stripComments(jscString)
            lines = jscText.splitlines()
            for line in lines:
                self.__parseLine(line)
            self.__endSection()

        except:
            self.__jscData = None

        finally:
            return self.__jscData

################################################################################
#                                End of file                                   #
################################################################################
