#!/usr/bin/env python
from __future__ import print_function
import sys
from argparse import ArgumentParser
import numpy as np
import readline
import rpy2.robjects as robjects

def convertFCSToText(input_file,compensate,output_file,
                       keyword_file, tool_directory):

    r_source = tool_directory + "/FCSConvert.R"
    R = robjects.r
    command ='source("' + r_source + '")'
    R(command)
    command = 'transformFCS("' + input_file + '","' + output_file \
                         + '","' + keyword_file + '",' + compensate \
                         + ',FALSE)'
    R(command)
    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="transformFCSTrans1",
             description="Read in an FCS file and convert to Text")

    parser.add_argument(
            '-i',
            dest="input_file",
            required=True,
            help="File location for the FCS file.")

    parser.add_argument(
            '-c',
            dest="compensate",
            required=True,
            help="Whether to try compensation if the SPILL matrix is available.")

    parser.add_argument(
            '-o',
            dest="output_file",
            required=True,
            help="File location for the output file.")

    parser.add_argument(
            '-t',
            dest="tool_directory",
            required=True,
            help="Location of the tool directory.")


    args = parser.parse_args()

    convertFCSToText(args.input_file, args.compensate, args.output_file,
                       "", args.tool_directory)
    sys.exit(0)
