#!/usr/bin/env python
from __future__ import print_function
import sys
import os
from argparse import ArgumentParser

def runCrossSample(args):
    tool_directory = args.tool_directory
    # Strip off Header Line
    mfi_in = open(args.mfi_file,"r")
    mfi_out = open("mfi.txt","w")
    mfi_in.readline
    for line in mfi_in:
       mfi_out.write(line)
    mfi_in.close()
    mfi_out.close()

    run_command = tool_directory + "/bin/cent_adjust mfi.txt " + args.flow_file
    print(run_command)
    os.system(run_command)

    flow_file = open(args.flow_file,"r")
    pop_file = open("population_id.txt","r")
    result_file = open(args.output_file,"w")
    line = flow_file.readline()
    line = line.rstrip()
    line = line + "\tPopulation\n"
    result_file.write(line)
    for line in flow_file:
        line = line.rstrip()
        pop_line = pop_file.readline()
        pop_line = pop_line.rstrip()
        line = line + "\t" + pop_line + "\n"
        result_file.write(line)

    flow_file.close()
    pop_file.close()
    result_file.close()
    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="runCrossSample",
             description="Run CrossSamle on Flow file")

    parser.add_argument(
            '-i',
            dest="flow_file",
            required=True,
            help="File location for the Flow text file.")

    parser.add_argument(
            '-m',
            dest="mfi_file",
            required=True,
            help="File location for the MFI text file.")

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

    args = parser.parse_args()

    runCrossSample(args)
    sys.exit(0)
