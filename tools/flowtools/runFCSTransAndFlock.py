#!/usr/bin/env python
from __future__ import print_function
import sys 
import os
from argparse import ArgumentParser
import numpy as np
import readline
import rpy2.robjects as robjects

def runFCSTransAndFlock(input_file,compensate,
                        method,bins,density,
                        output_text_file,output_clr_file,
                        keyword_file,tool_directory):

    print("COMPENSATE: ",compensate)
    r_source = tool_directory + "/FCSTrans.R"
    R = robjects.r
    command ='source("' + r_source + '")'
    R(command)
    command = 'transformFCS("' + input_file + '","' + output_text_file \
                         + '","' + keyword_file + '",' + compensate \
                         + ',FALSE)'
    R(command)

    run_command = tool_directory + "/bin/"  + method + " " + output_text_file
    if bins:
        run_command += " " + bins
    if density:
        run_command += " " + density

    os.system(run_command)

    move_command = "mv flock_results.txt " + output_clr_file
    os.system(move_command)
    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="runFCSTransAndFlock",
             description="Run FCSTrans and Flock on a FCS file")

    parser.add_argument(
            '-i',
            dest="input_file",
            required=True,
            help="File location for the FCS file.")

    parser.add_argument(
            '-c',
            dest="compensate",
            required=True,
            help="Whether to try and run compensation if available.")

    parser.add_argument(
            '-m',
            dest="method",
            required=True,
            help="Run flock1 or flock2.")

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
            '-f',
            dest="output_text_file",
            required=True,
            help="File location for the output file.")

    parser.add_argument(
            '-o',
            dest="output_clr_file",
            required=True,
            help="File location for the output file.")

    parser.add_argument(
            '-t',
            dest="tool_directory",
            required=True,
            help="File location for the output file.")


    args = parser.parse_args()
    runFCSTransAndFlock(args.input_file,args.compensate,
                        args.method,args.bins, args.density,
                        args.output_text_file, args.output_clr_file,
                        "",args.tool_directory)
    sys.exit(0)
