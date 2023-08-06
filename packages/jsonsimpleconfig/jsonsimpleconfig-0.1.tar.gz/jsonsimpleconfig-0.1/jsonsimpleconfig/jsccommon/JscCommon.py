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

import datetime


################################################################################
# Module                                                                       #
################################################################################

class JscCommon:

    @staticmethod
    def getTimestemp(time=True, seconds=False, microseconds=False, utc=False):
        if utc:
            todaydate = datetime.datetime.utcnow()
        else:
            todaydate = datetime.datetime.now()
        timestemp = (str("%04d" % todaydate.year) + "-" +
                     str("%02d" % todaydate.month) + "-" +
                     str("%02d" % todaydate.day))
        if time:
            timestemp += (" " +
                          str("%02d" % todaydate.hour) + ":" +
                          str("%02d" % todaydate.minute))
            if seconds:
                timestemp += ("." + str("%02d" % todaydate.second))
                if microseconds:
                    timestemp += ("." + str("%06d" % todaydate.microsecond))
        return timestemp

################################################################################
#                                End of file                                   #
################################################################################
