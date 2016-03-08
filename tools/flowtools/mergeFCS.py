#!/usr/bin/env python
from __future__ import print_function
import sys
import os
from argparse import ArgumentParser

def mergeFCS(input_files,output_file,sample_rate,tool_directory):
    filelist = open("filelist.txt","w")
    filelist.write("Files\n")
    for input_file in input_files:
        filelist.write(input_file + "\n")
    filelist.close()

    run_command = "java -jar " + tool_directory \
                      + "/bin/mergefcsdatafiles.jar " \
                      + "-InputFile:filelist.txt -OutputFile:" \
                      + output_file

    if sample_rate:
        run_command += " -SubsamplingRate:" + sample_rate

    os.system(run_command) 
    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="extractKeywords",
             description="Merge FCS files into one FCS file.")

    parser.add_argument(
            '-i',
            dest="input_files",
            required=True,
            action='append',
            help="File location for the FCS file.")

    parser.add_argument(
            '-o',
            dest="output_file",
            required=True,
            help="Name of the output file.")

    parser.add_argument(
            '-t',
            dest="tool_directory",
            required=True,
            help="Location of the tool directory.")

    parser.add_argument(
            '-s',
            dest="sample_rate",
            required=False,
            help="Sampling Rate.")


    args = parser.parse_args()
    input_files = [f for f in args.input_files]

    mergeFCS(input_files,args.output_file,args.sample_rate,args.tool_directory)
    sys.exit(0)
