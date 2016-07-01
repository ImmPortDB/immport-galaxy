#!/usr/bin/env python
from __future__ import print_function
import sys
import os

from argparse import ArgumentParser

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
        
def mergeFCStxt(in_files, out_file, headingscheck):
    """Concatenates together tab-separated files provided:
    a. the number of columns is the same in all files
    b. all lines after the header line contain only numbers
    c. the headings are the same in all files (optional)
    Potential errors are logged to stderr. If the number of errors reaches 10,
    the program stops.
    """

    hdgs_nb = 0
    nb_errors = 0
    errors = {
        "numbers": 0,
        "columnsnb": 0,
        "headings": 0
    }
    count_lines = {}
    max_error = 10

    with open(out_file, "w") as outf:
        with open(in_files[0], "r") as firstfile:
            headingsff = firstfile.readline()
            headings = headingsff.split("\t")
            hdgs_nb = len(headings)
            outf.write(headingsff)
            count_lines[in_files[0]] = 1

            for fileline in firstfile:
                if nb_errors < max_error:
                    outf.write(fileline)
                    fileline = fileline.strip()
                    count_lines[in_files[0]] += 1
                    for item in fileline.split("\t"):
                        if not is_number(item): 
                            nb_errors += 1
                            sys.stderr.write(" ".join(["WARNING: line", str(count_lines[in_files[0]]),
                                                       "in", in_files[0] ,"contains non-numeric results"]) + "\n")
                            errors["numbers"] += 1

            for i in range(1, len(in_files)):
                if nb_errors < max_error:
                    with open(in_files[i], "r") as inf:
                        headingsinf = inf.readline()
                        hdgs = headingsinf.split("\t")
                        count_lines[in_files[i]] = 1

                        if len(hdgs) != hdgs_nb:
                            nb_errors += 1
                            sys.stderr.write(" ".join(["WARNING: the number of columns in file", in_files[i], 
                                                       "is not consistent with", in_files[0]]) + "\n")
                            errors["columnsnb"] += 1

                        if nb_errors >= max_error:
                            break

                        if headingscheck:
                            heading_error = 0
                            for k in range(0, hdgs_nb):
                                if hdgs[k].lower() != headings[k].lower():
                                    heading_error += 1
                            if heading_error > 0:
                                nb_errors += 1
                                sys.stderr.write(" ".join(["WARNING: the headings in file", in_files[i], 
                                                           "are not consistent with", in_files[0]]) + "\n")
                                errors["headings"] += 1

                        for otherlines in inf:
                            if nb_errors < max_error:
                                outf.write(otherlines)
                                count_lines[in_files[i]] += 1
                                otherlines = otherlines.strip()
                                for item in otherlines.split("\t"):
                                    if not is_number(item):
                                        nb_errors += 1
                                        sys.stderr.write(" ".join(["WARNING: line", str(count_lines[in_files[i]]),
                                                                   "in", in_files[i] ,"contains non-numeric results"]) + "\n")
                                        errors["numbers"] += 1

    if nb_errors > 0:
        exit_code = 0
        if errors["headings"] > 0:
            exit_code += 3
        if errors["columnsnb"] > 0:
            exit_code += 2
        if errors["numbers"] > 0:
            exit_code += 4
        if nb_errors == max_error:
            sys.stderr.write("Run aborted - too many errors.")
            os.remove(out_file)
        sys.exit(exit_code)

    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="simpleFCStxtmerge",
             description="Merge FCS files converted to text into one FCS-text file provided they have the same number of columns.")

    parser.add_argument(
            '-i',
            dest="input_files",
            required=True,
            action='append',
            help="File location for the text files.")

    parser.add_argument(
            '-o',
            dest="output_file",
            required=True,
            help="Name of the output file.")

    parser.add_argument(
            '-c',
            dest="check_headings",
            default=False,
            help="Checks the headings in each file")

    args = parser.parse_args()
    input_files = [f for f in args.input_files]

    mergeFCStxt(input_files, args.output_file, args.check_headings)
    sys.exit(0)
