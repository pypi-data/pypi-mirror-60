# -*- coding: utf-8 -*-
# * ********************************************************************* *
# *   Copyright (C) 2018 by xmz                                           *
# * ********************************************************************* *

'''
Tools for binary and text data

@author: Marcin Zelek (marcin.zelek@gmail.com)
         Copyright (C) xmz. All Rights Reserved.
'''

################################################################################
# Import(s)                                                                    #
################################################################################

from .bintextcommon import BinTextCommon
from .bintexthelper import BinText, Bin2TextConverter, TextFormat, Text2BinConverter


################################################################################
# Module                                                                       #
################################################################################

def bin2text(binaryFilePath: str,
             textFilePath: str,
             format='HEX',
             delimiter=None,
             lineCharacters=0,
             showHeader=True):
    BinText.convertBin2Text(binaryFilePath,
                            textFilePath,
                            format,
                            delimiter,
                            lineCharacters,
                            showHeader)


def text2bin(textFilePath: str,
             binaryFilePath: str,
             format='HEX',
             delimiter=None):
    BinText.convertText2Bin(textFilePath,
                            binaryFilePath,
                            format,
                            delimiter)


__all__ = ('BinTextCommon',
           'Bin2TextConverter',
           'BinText',
           'TextFormat',
           'Text2BinConverter')

################################################################################
#                                End of file                                   #
################################################################################
