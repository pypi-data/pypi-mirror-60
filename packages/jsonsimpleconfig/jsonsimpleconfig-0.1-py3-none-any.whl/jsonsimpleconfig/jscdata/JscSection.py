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


################################################################################
# Module                                                                       #
################################################################################


class JscSection:
    SECTION_GLUE = "."
    GLOBAL_SECTION_NAME = "__GLOBAL__"

    def __init__(self, name=GLOBAL_SECTION_NAME):
        self.__section = list()
        self.__section.append(name)

    def __append(self, name):
        self.__section.append('"'+name+'"')

    def up(self, name):
        if len(self.__section) == 1 and JscSection.GLOBAL_SECTION_NAME in self.__section:
            self.__section = list()
        self.__append(name)

    def down(self):
        if len(self.__section) == 1:
            self.__section = list()
            self.__section.append(JscSection.GLOBAL_SECTION_NAME)
        else:
            del self.__section[-1]

    def str(self):
        if len(self.__section) == 1 and JscSection.GLOBAL_SECTION_NAME in self.__section:
            sectionName = None
        else:
            sectionName = JscSection.SECTION_GLUE.join(self.__section)
        return sectionName

################################################################################
#                                End of file                                   #
################################################################################
