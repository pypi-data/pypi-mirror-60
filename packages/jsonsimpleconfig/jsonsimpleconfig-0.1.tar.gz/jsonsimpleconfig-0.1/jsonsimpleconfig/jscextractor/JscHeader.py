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

import os, os.path
import logging
import jsonsimpleconfig

from string import Template


################################################################################
# Module                                                                       #
################################################################################

class JscHeader:

    def __init__(self, options={'defaultHeader': True,
                                'allowCustomHeader': False,
                                'customHeaderFilePath': '/etc/jsonsimpleconfig/header.template'}):
        self.__options = options

    def __headerTemplate(self, filePath) -> Template:
        header = None
        try:
            if os.path.isfile(filePath):
                filein = open(filePath)
                if filein:
                    jscTemplateFile = Template(filein.read())
                    if self.__options.get('headerTemplateData'):
                        header = jscTemplateFile.substitute(self.__options.get('headerTemplateData'))
        except OSError as e:
            logging.debug(e)
        return header

    def str(self) -> str:
        header = filePath = None

        if self.__options.get('allowCustomHeader') and \
           ("customHeaderFilePath" in self.__options) and \
           os.path.isfile(self.__options.get('customHeaderFilePath')):
            filePath = self.__options.get('customHeaderFilePath')

        elif self.__options.get('defaultHeader'):
            path = os.path.abspath(jsonsimpleconfig.__file__)
            path = os.path.dirname(path)
            filePath = os.path.join(path, 'jscresources/defaultHeader.template')

        if filePath is not None:
            header = self.__headerTemplate(filePath)

        return header

################################################################################
#                                End of file                                   #
################################################################################
