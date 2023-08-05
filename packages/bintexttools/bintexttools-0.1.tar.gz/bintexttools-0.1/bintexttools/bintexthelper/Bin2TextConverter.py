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
import binascii
import codecs
import struct

from .TextFormat import TextFormat


################################################################################
# Module                                                                       #
################################################################################

class Bin2TextConverter:
    linesep = os.linesep
    format = TextFormat.HEX
    delimiter = None
    lineCharacters = -1
    showHeader = True

    def __convert(self, byte):
        if self.format == TextFormat.BINARY:
            return (bin(int(binascii.hexlify(byte), 16))[2:]).zfill(8)
        elif self.format == TextFormat.DECIMAL:
            return str(int(binascii.hexlify(byte), 16)).zfill(3)
        elif self.format == TextFormat.HEX:
            return codecs.decode(binascii.hexlify(byte), 'ascii')
        elif self.format == TextFormat.ASCII:
            return codecs.decode(binascii.b2a_uu(byte), 'ascii').rstrip(self.linesep)
        elif self.format == TextFormat.BASE64:
            return codecs.decode(binascii.b2a_base64(byte), 'ascii').rstrip('=='+self.linesep)
        return None

    def convert(self, bytes: bytearray):
        text = ''
        for byte in bytes:
            text += self.__convert(struct.pack("B", byte))
        return text

    def convertFile(self, inputFile, outputFile, writeType='a'):
        with open(inputFile, "rb") as input:
            with open(outputFile, writeType) as output:
                firstByte = True
                line = 0
                while True:
                    toWrite = ''
                    byte = input.read(1)

                    if not byte:
                        break

                    if firstByte:
                        firstByte = False
                    elif self.delimiter:
                        toWrite += self.delimiter

                    toWrite += self.__convert(byte)

                    if self.lineCharacters > 0:
                        countWriteCharacters = len(toWrite)
                        if countWriteCharacters > 0:
                            for it in range(countWriteCharacters):
                                if ((line + 1) % (self.lineCharacters + 1)) == 0:
                                    output.write(self.linesep)
                                    line = 0
                                line += output.write(toWrite[:1])
                                toWrite = toWrite[1:]

                    else:
                        line += output.write(toWrite)

################################################################################
#                                End of file                                   #
################################################################################
