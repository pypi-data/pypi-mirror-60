# -*- coding: utf-8 -*-
# * ********************************************************************* *
# *   Copyright (C) 2018 by xmz                                           *
# * ********************************************************************* *

'''
JSON Simple Config

@author: Marcin Zelek (marcin.zelek@gmail.com)
         Copyright (C) xmz. All Rights Reserved.
'''

################################################################################
# Import(s)                                                                    #
################################################################################

from .jsccommon import JscComments, JscCommon
from .jscdata import JscData, JscSection
from .jscparser import Json, JscParser
from .jscextractor import JscExtractor, JscHeader, JsonExtractor
from .jschelper import Jsc, Json2JscHelper, Jsc2JsonHelper


################################################################################
# Module                                                                       #
################################################################################

def load(jscFile, refresh=False):
    return Jsc.get(jscFile, refresh)


def loads(jscString):
    return Jsc.gets(jscString)


__all__ = ('JscCommon',
           'JscComments',
           'Json2JscHelper',
           'Jsc2JsonHelper',
           'Json',
           'JscParser',
           'JscData',
           'JscSection',
           'JscExtractor',
           'JsonExtractor',
           'JscHeader',
           'Jsc')

################################################################################
#                                End of file                                   #
################################################################################
