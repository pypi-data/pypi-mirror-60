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
import json


################################################################################
# Module                                                                       #
################################################################################

class Json:

    def __init__(self, file):
        self.__file = file

    def parse(self):
        data = status = None
        try:
            json_data = open(self.__file)
            data = json.load(json_data)
            json_data.close()

        except json.JSONDecodeError as e:
            data = None
            status = e.msg

        except:
            data = None
            status = sys.exc_info()

        finally:
            return {'data': data, 'status': status}

################################################################################
#                                End of file                                   #
################################################################################
