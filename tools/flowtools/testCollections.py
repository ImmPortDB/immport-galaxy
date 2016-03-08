#!/usr/bin/env python
from __future__ import print_function
import sys
from argparse import ArgumentParser
import numpy as np
import readline
import rpy2.robjects as robjects

def testCollections():
    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="extractKeywords",
             description="Extract the Keywords from a FCS file.")

    parser.add_argument(
            '-i',
            dest="input_files",
            required=True,
            action='append',
            help="File location for the FCS file.")

    parser.add_argument(
            '-o',
            dest="collections_file",
            required=True,
            help="Name of the keyword output file.")

    parser.add_argument(
            '-t',
            dest="tool_directory",
            required=True,
            help="Location of the tool directory.")


    args = parser.parse_args()
    input_files = [f for f in args.input_files]

    print(input_files)

    testCollections()
    sys.exit(0)
