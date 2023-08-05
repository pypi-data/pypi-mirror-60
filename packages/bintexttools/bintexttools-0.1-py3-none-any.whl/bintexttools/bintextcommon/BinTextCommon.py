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
import datetime
import hashlib
import string
import codecs
import unicodedata


################################################################################
# Module                                                                       #
################################################################################

class BinTextCommon:

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

    @staticmethod
    def getTimestempFileName(time=True, seconds=False, microseconds=False, utc=False):
        if utc:
            todaydate = datetime.datetime.utcnow()
        else:
            todaydate = datetime.datetime.now()
        timestemp = (str("%04d" % todaydate.year) + "_" +
                     str("%02d" % todaydate.month) + "_" +
                     str("%02d" % todaydate.day))
        if time:
            timestemp += ("." +
                          str("%02d" % todaydate.hour) + "_" +
                          str("%02d" % todaydate.minute))
            if seconds:
                timestemp += ("_" + str("%02d" % todaydate.second))
                if microseconds:
                    timestemp += ("_" + str("%06d" % todaydate.microsecond))
        return timestemp

    @staticmethod
    def md5sum(filename, seek=0, blocksize=4096):
        hash = hashlib.md5()
        with open(filename, "rb") as file:
            if seek > 0:
                file.seek(seek)
            for block in iter(lambda: file.read(blocksize), b""):
                hash.update(block)
        return hash.hexdigest()

    @staticmethod
    def queryYesNo(question, default="yes"):

        valid = {"yes": True, "y": True, "True": True, "T": True, "t": True, '1': True,
                 "no": False, "n": False, "False": False, "F": False, "f": False, '0': False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes/y/t/1' or 'no/n/f/0'" + os.linesep)

    @staticmethod
    def slugify(value):
        validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        value = codecs.decode(unicodedata.normalize('NFKD', value).encode('ascii', 'ignore'), 'ascii')
        return ''.join(str(char) for char in value if str(char) in validFilenameChars)

    @staticmethod
    def str2Bool(value):
        if value.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif value.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise TypeError('Boolean value expected.')

################################################################################
#                                End of file                                   #
################################################################################
