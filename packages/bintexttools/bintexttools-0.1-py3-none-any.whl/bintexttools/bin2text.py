#! /bin/sh
# -*- coding: utf-8 -*-
""":"
exec python3 $0 ${1+"$@"}
"""
# * ********************************************************************* *
# *   Copyright (C) 2018 by xmz                                           *
# * ********************************************************************* *

'''
BIN to ASCII converter

@author: Marcin Zelek (marcin.zelek@gmail.com)
         Copyright (C) xmz. All Rights Reserved.
'''

################################################################################
# Import(s)                                                                    #
################################################################################

import os
import sys
import signal
import argparse
import logging
import re

from bintexttools import BinText, BinTextCommon

################################################################################
# Module Variable(s)                                                           #
################################################################################

versionString = "0.0.1"
applicationNameString = "BIN File to TEXT File converter"
server = None


################################################################################
# Module                                                                       #
################################################################################

def checkFilePath(filePath):
    """
    'Type' for argparse - checks that file can be written.
    """
    if not os.access(filePath, os.W_OK):
        try:
            open(filePath, 'w').close()
            os.unlink(filePath)
        except OSError:
            raise argparse.ArgumentTypeError("{} cannot be written at that location".format(filePath))
    return filePath


def str2Bool(value):
    try:
        BinTextCommon.str2Bool(value)
    except TypeError as error:
        raise argparse.ArgumentTypeError(error)


def parameters():
    defaultShowHeader = True
    defaultDelimiter = None
    defaultFormat = 'HEX'
    defaultNumberOfLineCharacters = 0
    defaultOutputFilename = BinTextCommon.getTimestempFileName(True, True) + ".b2t"

    parser = argparse.ArgumentParser(description=applicationNameString)
    parser.add_argument('-v', '--version', action='version', version=applicationNameString + " - " + versionString)
    parser.add_argument('-f', '--format', default=defaultFormat,
                        choices={'BINARY', 'DECIMAL', 'HEX', 'ASCII', 'BASE64'},
                        help='Output format.', required=False)
    parser.add_argument('-d', '--delimiter', default=defaultDelimiter, help='Data delimiter', required=False)
    parser.add_argument('-l', '--lineCharacters', type=int, default=defaultNumberOfLineCharacters,
                        help='Number of characters per line', required=False)
    parser.add_argument("--showHeader", type=str2Bool, nargs='?', const=defaultShowHeader, default=defaultShowHeader,
                        help="Show/Add to file info header data", required=False)

    parser.add_argument('-i', '--binaryFilePath', type=argparse.FileType('r'), help='Path to binary file.',
                        required=True)
    parser.add_argument('-o', '--textFilePath', type=checkFilePath,
                        help='Output path to text file.',
                        required=False,
                        default=defaultOutputFilename)

    loggingLeveChoices = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG
    }
    parser.add_argument('-ll', '--logging_level', dest="loggingLevel", choices=loggingLeveChoices.keys(),
                        help='Output log level', required=False)
    args, leftovers = parser.parse_known_args()

    if vars(args)['loggingLevel'] is None:
        level = logging.CRITICAL
    else:
        level = loggingLeveChoices.get(vars(args)['loggingLevel'], logging.CRITICAL)
    logging.basicConfig(format='[%(asctime)s][%(levelname)-8s] [%(module)-20s] - %(message)s', datefmt='%Y.%m.%d %H:%M.%S', level=level)

    return vars(args)


def main(argv=sys.argv):
    signal.signal(signal.SIGINT, handler)
    args = parameters()
    logging.info('* Arguments:')
    for key, value in args.items():
        logging.info('** [{}]: [{}]'.format(' '.join(
            ''.join([w[0].upper(), w[1:].lower()]) for w in (re.sub("([a-z])([A-Z])", "\g<1> \g<2>", key)).split()),
                                            value))

    print("Converting binary file: {}".format(args['binaryFilePath'].name))
    print("to text file: {}".format(args['textFilePath']))
    print("Wait...")

    if args['loggingLevel'] == 'DEBUG':
        BinText.convertBin2Text(args['binaryFilePath'].name,
                                args['textFilePath'],
                                args['format'],
                                args['delimiter'],
                                args['lineCharacters'],
                                args['showHeader'])
    else:
        try:
            BinText.convertBin2Text(args['binaryFilePath'].name,
                                    args['textFilePath'],
                                    args['format'],
                                    args['delimiter'],
                                    args['lineCharacters'],
                                    args['showHeader'])
        except:
            print('Error!')

    print("Done.")


def handler(signum, frame):
    sys.exit()


# Execute main function
if __name__ == '__main__':
    main()
    sys.exit()

################################################################################
#                                End of file                                   #
################################################################################
