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
import binascii

from bintexttools import BinTextCommon
from .TextFormat import TextFormat


################################################################################
# Module                                                                       #
################################################################################

class Text2BinConverter:
    byteorder = sys.byteorder
    linesep = os.linesep
    startHeaderTag = "<<< HEADER"
    endHeaderTag = ">>> HEADER"
    format = TextFormat.HEX
    delimiter = None
    filesize = None
    md5 = None

    def __readSize(self):
        size = {
            TextFormat.BINARY: 8,
            TextFormat.DECIMAL: 3,
            TextFormat.HEX: 2,
            TextFormat.ASCII: 5,
            TextFormat.BASE64: 2,
        }
        return size[self.format]

    def __convert(self, byte):
        try:
            if self.format == TextFormat.BINARY:
                return int(byte, 2).to_bytes(1, byteorder=self.byteorder)
            elif self.format == TextFormat.DECIMAL:
                return int(byte, 10).to_bytes(1, byteorder=self.byteorder)
            elif self.format == TextFormat.HEX:
                return binascii.unhexlify(byte)
            elif self.format == TextFormat.ASCII:
                return binascii.a2b_uu('{}'.format(byte) + self.linesep)
            elif self.format == TextFormat.BASE64:
                return binascii.a2b_base64('{}=='.format(byte) + self.linesep)
        except binascii.Error:
            pass
        return None

    def convert(self, textData: str):
        data = None
        while True:
            try:
                if self.__readSize() <= len(textData):
                    byteText = textData[:self.__readSize()]
                    textData = textData[self.__readSize():]
                    byte = self.__convert(byteText)
                    if data:
                        data += byte
                    else:
                        data = byte
                else:
                    break
            except (TypeError, EOFError):
                break
        return data

    def detectHeader(self, inputFile) -> str:
        header = ''
        with open(inputFile, "r") as file:
            start = end = False
            for line in file:
                if line.strip().startswith(self.startHeaderTag):
                    start = True
                elif line.strip().startswith(self.endHeaderTag):
                    end = True
                    break
                else:
                    header += line
            if not (start and end):
                header = None
        return header

    def detectDataSeek(self, inputFile) -> int:
        filesize = seek = 0
        try:
            filestat = os.stat(inputFile)
            filesize = filestat.st_size
        except Exception:
            filesize = 0

        with open(inputFile, "rb") as file:
            start = end = False
            headerSize = 0
            while True:
                line = file.readline()
                if not line:
                    break
                line = line.decode('ascii')
                headerSize += len(line)
                if line.strip().startswith(self.startHeaderTag):
                    start = True
                elif line.strip().startswith(self.endHeaderTag):
                    end = True
                    break
            if start and end:
                seek = file.tell()
                if 0 < filesize and filesize < seek:
                    if 0 < headerSize and headerSize < filesize:
                        seek = headerSize
                    else:
                        seek = 0
        return seek

    def verifyInputFile(self, inputFile, seek, filesize, md5) -> dict:
        try:
            filestat = os.stat(inputFile)
            sizeInputData = (filestat.st_size - seek)
            md5InputData = BinTextCommon.md5sum(inputFile, seek)
        except Exception:
            sizeInputData = md5InputData = None

        status = {
            "verified": sizeInputData == filesize and md5InputData == md5,
            "expected":
                {
                    "size": filesize,
                    "md5": md5
                },
            "obtained":
                {
                    "size": sizeInputData,
                    "md5": md5InputData
                }
        }
        return status

    def verifyOutputFile(self, outputFile, filesize, md5) -> dict:
        try:
            filestat = os.stat(outputFile)
            sizeOutputFile = filestat.st_size
            md5OutputFile = BinTextCommon.md5sum(outputFile)
        except Exception:
            sizeInputData = md5InputData = None

        status = {
            "verified": sizeOutputFile == filesize and md5OutputFile == md5,
            "expected":
                {
                    "size": filesize,
                    "md5": md5
                },
            "obtained":
                {
                    "size": sizeOutputFile,
                    "md5": md5OutputFile
                }
        }
        return status

    def convertFile(self, inputFile, outputFile, inputFileSeek=0, readBlockSize=4096):
        with open(inputFile, "r") as input:
            if inputFileSeek > 0:
                input.seek(inputFileSeek)
            with open(outputFile, "wb") as output:
                blockData = ''
                while True:
                    try:

                        if self.__readSize() > len(blockData):
                            # Read new data block
                            blockData += input.read(readBlockSize)
                            if not blockData:
                                return
                            # Remove line separators
                            blockData = blockData.replace(self.linesep, '').lstrip()

                        if self.__readSize() <= len(blockData):
                            byte = blockData[:self.__readSize()]
                            blockData = blockData[self.__readSize():]

                            toWrite = self.__convert(byte)
                            if toWrite:
                                output.write(toWrite)
                        else:
                            break

                        # Detect delimiter
                        if self.delimiter:
                            if len(self.delimiter) > len(blockData):
                                # Read new data block
                                blockData += input.read(readBlockSize)
                                if not blockData:
                                    return
                                blockData = blockData.replace(self.linesep, '')

                            if len(self.delimiter) <= len(blockData):
                                delimiter = blockData[:len(self.delimiter)]
                                blockData = blockData[len(self.delimiter):]

                                if delimiter != self.delimiter:
                                    return
                            else:
                                break

                    except (TypeError, EOFError):
                        break

################################################################################
#                                End of file                                   #
################################################################################
