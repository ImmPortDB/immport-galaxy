#!/usr/bin/env python
from __future__ import print_function
import sys
from argparse import ArgumentParser
from flowstatlib import gen_overview_stats
import pandas as pd

def generateMFI(input_file_name, output_file_name, mfi_calc):
    flockdf = pd.read_table(input_file_name)
    if mfi_calc == "mfi":
        MFIs = flockdf.groupby('Population').mean().round(decimals=2)
    elif mfi_calc == "gmfi":
        MFIs = flockdf.groupby('Population').agg(lambda x: gmean(list(x))).round(decimals = 2)
    else:
        MFIs = flockdf.groupby('Population').median().round(decimals=2)

    with open(output_file_name,"w") as outf:
		MFIs.to_csv(outf, sep="\t", float_format='%.0f')
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
            '-M',
            dest="mfi_calc",
            required=True,
            help="what to calculate for centroids.")

    parser.add_argument(
            '-o',
            dest="output_file",
            required=True,
            help="File location for the MFI output file.")


    args = parser.parse_args()
    generateMFI(args.input_file, args.output_file, args.mfi_calc)
    sys.exit(0)

