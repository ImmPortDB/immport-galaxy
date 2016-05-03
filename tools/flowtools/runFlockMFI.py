#!/usr/bin/env python
from __future__ import print_function

import sys 
import os
from argparse import ArgumentParser
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

def runFlock(input_file, method, bins, density, output_file, tool_directory):
    run_command = tool_directory + "/bin/"  + method + " " + input_file
    if bins:
        run_command += " " + bins
    if density:
        run_command += " " + density

    os.system(run_command)

    move_command = "mv flock_results.txt " + output_file
    os.system(move_command)
    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="runFlockMFI",
             description="Run Flock on text file and generate centroid file")

    parser.add_argument(
            '-i',
            dest="input_file",
            required=True,
            help="File location for the FCS file.")

    parser.add_argument(
            '-m',
            dest="method",
            required=True,
            help="Run flock1 or flock2.")

    parser.add_argument(
            '-M',
            dest="mfi_calc",
            required=True,
            help="what to calculate for centroids.")

    parser.add_argument(
            '-b',
            dest="bins",
            required=False,
            help="Number of Bins.")

    parser.add_argument(
            '-d',
            dest="density",
            required=False,
            help="Density.")

    parser.add_argument(
            '-o',
            dest="output_file",
            required=True,
            help="File location for the output file.")

    parser.add_argument(
            '-t',
            dest="tool_directory",
            required=True,
            help="File location for the output file.")

    parser.add_argument(
            '-c',
            dest="centroids",
            required=True,
            help="File location for the output centroid file.")

    args = parser.parse_args()
    runFlock(args.input_file,args.method,args.bins,
             args.density, args.output_file, args.tool_directory)

    generateMFI(args.output_file, args.centroids, args.mfi_calc)

    sys.exit(0)
