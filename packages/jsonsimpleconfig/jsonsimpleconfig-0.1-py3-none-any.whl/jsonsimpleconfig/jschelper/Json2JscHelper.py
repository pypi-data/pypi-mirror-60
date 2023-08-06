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

from jsonsimpleconfig import Json, JscData, JscExtractor


################################################################################
# Module                                                                       #
################################################################################

class Json2JscHelper:

    @staticmethod
    def convert(jsonFile, jscFile):

        jsonParser = Json(jsonFile)
        jsonData = jsonParser.parse()

        if jsonData['data'] is not None:
            if isinstance(jsonData['data'], dict):
                logging.info('JSON file is correct. Generating JSC ...')
                logging.info('JSC location: ' + jscFile)
                jscData = JscData.fromJson(jsonData['data'])
                jscExtractor = JscExtractor(jscData)
                jscExtractor.extractToFile(jscFile)
            else:
                logging.error('JSON data without root name cannot be converted into JSC.')

        else:
            logging.error('Incorrect JSON or file is empty.')
            if jsonData['status'] is not None:
                logging.debug(jsonData['status'])

################################################################################
#                                End of file                                   #
################################################################################
