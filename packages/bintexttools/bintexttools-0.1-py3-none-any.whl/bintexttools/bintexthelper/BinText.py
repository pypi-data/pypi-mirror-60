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
import ntpath
import json
import tempfile
import logging

from bintexttools import BinTextCommon
from .TextFormat import TextFormat
from .Bin2TextConverter import Bin2TextConverter
from .Text2BinConverter import Text2BinConverter


################################################################################
# Module                                                                       #
################################################################################

class BinText:
    version = 1

    @staticmethod
    def convertBin2Text(binaryFilePath: str,
                        textFilePath: str,
                        format,
                        delimiter,
                        lineCharacters,
                        showHeader):

        logging.info('Convert BIN data to TEXT Data ...')

        inputFile = binaryFilePath
        outputFileWithHeader = outputFile = textFilePath

        filestat = os.stat(inputFile)
        headerData = {'version': BinText.version}
        headerData['binFile'] = \
        {
            "timestamp": BinTextCommon.getTimestemp(),
            "filename": ntpath.basename(inputFile),
            "filesize": filestat.st_size,
            "md5": BinTextCommon.md5sum(inputFile),
        }

        if showHeader:
            outputFile = tempfile.NamedTemporaryFile(delete=True).name

        bin2text = Bin2TextConverter()
        bin2text.format = TextFormat[format]
        bin2text.delimiter = delimiter
        bin2text.lineCharacters = lineCharacters
        bin2text.convertFile(inputFile, outputFile)

        filestat = os.stat(outputFile)
        headerData['textFile'] = \
        {
            "filesize": filestat.st_size,
            "md5Data": BinTextCommon.md5sum(outputFile),
            "format": format,
            "delimiter": delimiter,
            "lineCharacters": lineCharacters,
            "linesep": os.linesep,
            "byteorder": sys.byteorder
        }

        if showHeader:
            with open(outputFileWithHeader, 'w') as output:
                output.write(Text2BinConverter.startHeaderTag + os.linesep)
                headerString = json.dumps(headerData, indent=4) + os.linesep
                logging.info(headerString)
                output.write(headerString)
                output.write(Text2BinConverter.endHeaderTag + os.linesep)
                with open(outputFile, "r") as input:
                    while True:
                        data = input.read(1024)
                        if not data:
                            break
                        output.write(data)
                os.remove(outputFile)
        else:
            headerString = json.dumps(headerData, indent=4) + os.linesep
            print(os.linesep)
            print("********************************************************************************")
            print("* Header - save it and use to decode data")
            print("********************************************************************************")
            print(headerString)
            print("********************************************************************************")
            print(os.linesep)

    @staticmethod
    def __getHeaderForConvertText2Bin(header):
        try:
            headerData = json.loads(header)
        except json.decoder.JSONDecodeError as error:
            print('Error decoding header data: ' + str(error))
            headerData = None
        finally:
            return headerData

    @staticmethod
    def __useHeaderForConvertText2Bin(header, text2bin):
        headerData = BinText.__getHeaderForConvertText2Bin(header)
        if headerData:
            if 'textFile' in headerData:
                if 'byteorder' in headerData['textFile']:
                    text2bin.byteorder = headerData['textFile']['byteorder']
                if 'linesep' in headerData['textFile']:
                    text2bin.linesep = headerData['textFile']['linesep']
                if 'format' in headerData['textFile']:
                    text2bin.format = TextFormat[headerData['textFile']['format']]
                if 'delimiter' in headerData['textFile']:
                    text2bin.delimiter = headerData['textFile']['delimiter']
        return text2bin

    @staticmethod
    def convertText2Bin(textFilePath: str,
                        outputFilePath: str,
                        header=None,
                        renameFile = False,
                        defaultOutputFilename = None):

        logging.info('Convert TEXT data to BIN Data ...')

        inputFile = textFilePath
        outputFile = outputFilePath
        text2bin = Text2BinConverter()
        text2bin = BinText.__useHeaderForConvertText2Bin(header, text2bin)
        inputFileSeek = text2bin.detectDataSeek(inputFile)
        detectedHeader = text2bin.detectHeader(inputFile)
        if detectedHeader:
            header = detectedHeader
        if header:
            headerData = BinText.__getHeaderForConvertText2Bin(header)
            if headerData and 'textFile' in headerData:
                if not detectedHeader:
                    logging.debug("HeaderData: " + json.dumps(headerData, indent=4))
                text2bin = BinText.__useHeaderForConvertText2Bin(header, text2bin)
                if all(key in headerData['textFile'] for key in ['filesize', 'md5Data']):
                    status = text2bin.verifyInputFile(inputFile, inputFileSeek,
                                                      headerData['textFile']['filesize'],
                                                      headerData['textFile']['md5Data'])
                    if "verified" in status:
                        if status["verified"]:
                            print("The text file is correct.")
                            logging.debug(json.dumps(status, indent=4) + os.linesep)
                        else:
                            print("The text file is corrupted.")
                            print(json.dumps(status, indent=4) + os.linesep)
                            answer = BinTextCommon.queryYesNo("Ignore validation and continue anyway?")
                            if answer:
                                print("Trying to convert invalid text data ...")
                            else:
                                print("The conversion skipped ...")
                                return
        else:
            headerData = None

        outputFileName = ntpath.basename(outputFile)
        outputFilePath = ntpath.dirname(outputFile)
        text2bin.convertFile(inputFile, outputFile, inputFileSeek)

        if headerData and 'binFile' in headerData:
            if all(key in headerData['binFile'] for key in ['filesize', 'md5']):
                status = text2bin.verifyOutputFile(outputFile,
                                                   headerData['binFile']['filesize'],
                                                   headerData['binFile']['md5'])
                if "verified" in status:
                    if status["verified"]:
                        print("The output file is correct.")
                        logging.debug(json.dumps(status, indent=4) + os.linesep)
                        if renameFile and 'filename' in headerData['binFile'] and headerData['binFile']['filename'] != outputFileName:
                            if defaultOutputFilename == outputFileName:
                                answer = True
                            else:
                                print("The output filename: '{}' does not match original filename: '{}'.".format(outputFileName, headerData['binFile']['filename']))
                                answer = BinTextCommon.queryYesNo("Update file to original name?", "no")
                            if answer:
                                outputFileLocation = os.path.join(outputFilePath, BinTextCommon.slugify(headerData['binFile']['filename']))
                                print("Updating output file into original to location: {}".format(outputFileLocation))
                                if os.path.exists(outputFileLocation):
                                    print("The file '{}' already exist. Skipped ...".format(outputFileLocation))
                                else:
                                    os.rename(outputFile, outputFileLocation)
                    else:
                        print("The output file is corrupted.")
                        print(json.dumps(status, indent=4) + os.linesep)

################################################################################
#                                End of file                                   #
################################################################################
