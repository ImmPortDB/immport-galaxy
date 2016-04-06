#!/usr/bin/env python
from __future__ import print_function
import sys
import os
from argparse import ArgumentParser
from collections import defaultdict
import pandas as pd

#
# version 1.1 -- April 2016 -- C. Thomas
# modified to read in several input files and output to a directory + generates summary statistics
#

def getPopProp(inputfiles, summary_stat):
    popcount = defaultdict(dict)
    for files in inputfiles:
        cs = pd.read_table(files)
        for pops in cs.Population:
            if pops in popcount[files]:
                popcount[files][pops] += 1
            else:
                popcount[files][pops] = 1
                
    with open(summary_stat, "w") as outf:
        itpop = [str(x) for x in range(1, len(popcount[inputfiles[0]]))]
        cols = "\t".join(itpop)
        outf.write("fileID\tnameToDisplay\t" + cols + "\n")
        for eachfile in popcount:
            tmp = []
            for num in range(1, len(popcount[inputfiles[0]])):
                if not num in popcount[eachfile]:
                    popcount[eachfile][num] = 0
                tmp.append(str(popcount[eachfile][num]))
            props = "\t".join(tmp)
            outf.write("\t".join([eachfile, eachfile, props]) + "\n")


def runCrossSample(inputfiles, mfi_file, output_dir, summary_stat, tool_directory):

    # Strip off Header Line
    with open(mfi_file,"r") as mfi_in, open("mfi.txt", "w") as mfi_out:
        mfi_in.readline()
        for line in mfi_in:
           mfi_out.write(line)

    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
          
    outputs = []
    # Run cent_adjust    
    for flow_file in inputfiles:
        run_command = tool_directory + "/bin/cent_adjust mfi.txt " + flow_file
        print(run_command)
        os.system(run_command)
        flowname = os.path.split(flow_file)[1]
        outfile = os.path.join(output_dir, flowname + ".crossSample")
        outputs.append(outfile)
        with open(flow_file,"r") as flowf, open("population_id.txt","r") as popf, open(outfile, "w") as outf:
            fline = flowf.readline()
            fline = fline.rstrip()
            fline = fline + "\tPopulation\n"
            outf.write(fline)
            
            for line in flowf:
                line = line.rstrip()
                pop_line = popf.readline()
                pop_line = pop_line.rstrip()
                line = line + "\t" + pop_line + "\n"
                outf.write(line)
    getPopProp(outputs, summary_stat)

    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="runCrossSample",
             description="Run CrossSample on Flow file")

    parser.add_argument(
            '-i',
            dest="input_files",
            required=True,
            action='append',
            help="File locations for flow text files.")

    parser.add_argument(
            '-m',
            dest="mfi_file",
            required=True,
            help="File location for the MFI text file.")

    parser.add_argument(
            '-o',
            dest="output_path",
            required=True,
            help="Path to the directory for the output files.")

    parser.add_argument(
            '-s',
            dest="summary_stat",
            required=True,
            help="File location for the summary statistics.")

    parser.add_argument(
            '-t',
            dest="tool_directory",
            required=True,
            help="File location for the output file.")

    args = parser.parse_args()

    input_files = [f for f in args.input_files]
    runCrossSample(input_files, args.mfi_file, args.output_path, args.summary_stat, args.tool_directory)
    sys.exit(0)
