#!/usr/bin/env python
from __future__ import print_function
import sys
import os
from argparse import ArgumentParser

def run_flowCL(phenotype, output_txt, output_pdf, tool_dir):
    tool = "/".join([tool_dir, "getOntology.R"])
    run_command = " ". join(["Rscript --slave --vanilla", tool, "--args", output_txt, phenotype])
    os.system(run_command)
    
    with open(output_txt, "r") as check_file:
        check = check_file.readline().strip()
        if (not check):
            sys.exit(2)
    
    get_graph = " ".join(["mv flowCL_results/*.pdf", output_pdf])
    os.system(get_graph)
    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog = "getOntology",
             description = "runs flowCL on a set of markers.")

    parser.add_argument(
            '-m',
            dest = "markers",
            required = True,
            action = 'append',
            help = "File location for the text files.")

    parser.add_argument(
            '-o',
            dest = "output",
            required = True,
            help = "Name of the output txt file.")

    parser.add_argument(
            '-g',
            dest = "graph",
            required = True,
            help = "Name of the graph file")

    parser.add_argument(
            '-t',
            dest = "tool_dir",
            required = True,
            help = "path to the tool directory")

    args = parser.parse_args()
    
    markers = "".join(args.markers)
    run_flowCL(markers, args.output, args.graph, args.tool_dir)
    sys.exit(0)
