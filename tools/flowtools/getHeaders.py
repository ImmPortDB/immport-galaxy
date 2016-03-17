#!/usr/bin/env python
from __future__ import print_function
import sys
import os

from argparse import ArgumentParser

def printheaders(files, outfile):
    with open(outfile, "w") as outf:
        for eachfile in files:
            with open(eachfile, "r") as ef:
                headers = ef.readline()
                outf.write("\t".join([eachfile, headers]))
    return


if __name__ == "__main__":
    parser = ArgumentParser(
             prog="GetHeaders",
             description="Gets the headers of all files in given set.")

    parser.add_argument(
            '-i',
            dest="input_files",
            required=True,
            action='append',
            help="File location for the text files.")

    parser.add_argument(
            '-o',
            dest="output_file",
            required=True,
            help="Name of the output file.")

    args = parser.parse_args()
    input_files = [f for f in args.input_files]
    printheaders(input_files, args.output_file)
    sys.exit(0)
