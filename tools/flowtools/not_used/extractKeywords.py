#!/usr/bin/env python
from __future__ import print_function
import sys
from argparse import ArgumentParser
import numpy as np
import readline
import rpy2.robjects as robjects

def extractKeywords(input_file, keyword_file, tool_directory):

    r_source = tool_directory + "/FCSKeyword.R"
    R = robjects.r
    command ='source("' + r_source + '")'
    R(command)
    command = 'transformFCS("' + input_file + '","' \
                            + keyword_file + '",FALSE)'
    R(command)
    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="extractKeywords",
             description="Extract the Keywords from a FCS file.")

    parser.add_argument(
            '-i',
            dest="input_file",
            required=True,
            help="File location for the FCS file.")

    parser.add_argument(
            '-k',
            dest="keyword_file",
            required=True,
            help="Name of the keyword output file.")

    parser.add_argument(
            '-t',
            dest="tool_directory",
            required=True,
            help="Location of the tool directory.")


    args = parser.parse_args()

    extractKeywords(args.input_file, args.keyword_file, args.tool_directory)
    sys.exit(0)
