#!/usr/bin/env python
from __future__ import print_function
import sys
import os

from argparse import ArgumentParser
from jinja2 import Environment, FileSystemLoader
from shutil import copyfile

def csOverview(inputfile, inputmfi, outputfile, outputdir, toolsdir):
    os.mkdir(outputdir)

    env = Environment(loader=FileSystemLoader(toolsdir + "/templates"))
    template = env.get_template("csOverview.template")

    real_directory = outputdir.replace("/job_working_directory","")
    context = { 'outputDirectory': real_directory }
    overview = template.render(**context)
    with open(outputfile,"w") as outf:
        outf.write(overview)

    csoverview_file = outputdir + "/csOverview.tsv"
    copyfile(inputfile, csoverview_file)

    csoverview_mfis = outputdir + "/csAllMFIs.tsv"
    copyfile(inputmfi, csoverview_mfis)

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="csOverview",
             description="Generate an overview plot of crossSample results.")

    parser.add_argument(
            '-i',
            dest="input_file",
            required=True,
            help="File location for the summary statistics from CrossSample.")

    parser.add_argument(
            '-I',
            dest="input_mfi",
            required=True,
            help="File location for the MFI summary statistics from CrossSample.")

    parser.add_argument(
            '-o',
            dest="output_file",
            required=True,
            help="File location for the HTML output file.")

    parser.add_argument(
            '-d',
            dest="output_directory",
            required=True,
            help="Directory location for the html supporting files.")

    parser.add_argument(
            '-t',
            dest="tool_directory",
            required=True,
            help="Location of the Tool Directory.")
    

    args = parser.parse_args()

    csOverview(args.input_file, args.input_mfi, args.output_file, args.output_directory, args.tool_directory)
    sys.exit(0)

