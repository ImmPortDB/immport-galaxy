#!/usr/bin/env python
from __future__ import print_function
import sys
from argparse import ArgumentParser
from flowstatlib import gen_overview_stats

def generateMFI(flow_stats, output_file_name):
    output_file = open(output_file_name,"w")
    flow_stats['mfi'].to_csv(output_file,sep="\t",float_format='%.0f')
    output_file.close()
    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="removeColumns",
             description="Generate MFI from Flow Result file.")

    parser.add_argument(
            '-i',
            dest="input_file",
            required=True,
            help="File location for the Flow Result file.")

    parser.add_argument(
            '-o',
            dest="output_file",
            required=True,
            help="File location for the MFI output file.")


    args = parser.parse_args()
    flow_stats = gen_overview_stats(args.input_file)
    generateMFI(flow_stats, args.output_file)
    sys.exit(0)

