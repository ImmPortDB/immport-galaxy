#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import pandas as pd

from argparse import ArgumentParser

def extract_pop(infile, poplist, outfile):
    df = pd.read_table(infile, dtype={'Population': object})
    dfout = df.loc[df['Population'].isin(poplist)]
    dfout.to_csv(outfile, sep="\t", index = False)
    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="ExtractPop",
             description="Extract events associated to given population numbers.")

    parser.add_argument(
            '-i',
            dest="input_file",
            required=True,
            help="File location for the text file.")

    parser.add_argument(
            '-p',
            dest="pops",
            required=True,
            help="List of populations to extract.")

    parser.add_argument(
            '-o',
            dest="output_file",
            required=True,
            help="Name of the output file.")

    args = parser.parse_args()
    
    ## check populations
    defaultvalues = ["i.e.:2,3,11,25", "default", "Default"]
    populations = []
    if args.pops:
        if not args.pops in defaultvalues:
            tmppops = args.pops.split(",")
            for popn in tmppops:
                populations.append(popn.strip())    
        else:
            sys.exit(3)
    extract_pop(args.input_file, populations, args.output_file)
    sys.exit(0)
