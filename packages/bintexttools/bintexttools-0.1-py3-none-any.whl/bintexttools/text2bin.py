#! /bin/sh
# -*- coding: utf-8 -*-
""":"
exec python3 $0 ${1+"$@"}
"""
# * ********************************************************************* *
# *   Copyright (C) 2018 by xmz                                           *
# * ********************************************************************* *

'''
ASCII to BIN converter

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
import json

from bintexttools import BinText, BinTextCommon

################################################################################
# Module Variable(s)                                                           #
################################################################################

versionString = "0.0.1"
applicationNameString = "TEXT File to BIN File converter"
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
    defaultHeader = json.dumps({
        "textFile":
            {
                "format": "HEX",
                "linesep": "\n",
                "byteorder": "little",
                "delimiter": None,
                "lineCharacters": 0
            }
    })
    defaultOutputFilename = BinTextCommon.getTimestempFileName(True, True) + ".t2b"

    parser = argparse.ArgumentParser(description=applicationNameString)
    parser.add_argument('-v', '--version', action='version', version=applicationNameString + " - " + versionString)
    parser.add_argument('--header', default=defaultHeader,
                        help='The header to decode data. Default: ' + defaultHeader, required=False)
    parser.add_argument("--renameFile", type=str2Bool, nargs='?', const=False, default=True,
                        help="Ask to rename file to original.", required=False)

    parser.add_argument('-i', '--textFilePath', type=argparse.FileType('r'), help='Path to file with text data.',
                        required=True)
    parser.add_argument('-o', '--outputFilePath', type=checkFilePath,
                        help='Output path.',
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
    args.defaultOutputFilename = defaultOutputFilename
    if args.outputFilePath != args.defaultOutputFilename:
        args.renameFile = False

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

    print("Converting text file: {}".format(args['textFilePath'].name))
    print("to original file: {}".format(args['outputFilePath']))
    print("Wait...")

    if args['loggingLevel'] == 'DEBUG':
        BinText.convertText2Bin(args['textFilePath'].name,
                                args['outputFilePath'],
                                args['header'],
                                args['renameFile'],
                                args['defaultOutputFilename'])
    else:
        try:
            BinText.convertText2Bin(args['textFilePath'].name,
                                    args['outputFilePath'],
                                    args['header'],
                                    args['renameFile'],
                                    args['defaultOutputFilename'])
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
