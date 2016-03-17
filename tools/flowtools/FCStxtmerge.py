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

def is_integer(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def compareheaders(files):
    headers = {}
    for eachfile in files:
        with open(eachfile, "r") as ef:
            headers[eachfile] = ef.readline().strip().lower().split("\t")
 
    hdgs_in_common = []
    flag = {}

    for refhdgs in headers[files[0]]:
        flag[refhdgs] = 1
        for ij in range(1, len(files)):
            if refhdgs in headers[files[ij]]:
                flag[refhdgs] += 1
        if flag[refhdgs] == len(files):
            hdgs_in_common.append(refhdgs)
    return(hdgs_in_common)

def getheadersindex(list_headings, headings):
    idxs = []
    lhdgs = [x.lower() for x in headings]
    for element in list_headings:
        idxs.append(int(lhdgs.index(element)))
    return(idxs)

def mergeFCStxt(in_files, out_file, col_names):
    """Concatenates together tab-separated files.
    The output will have only the columns in common to all the files provided as input, 
    as determined by the headers.
    All lines after the header line must contain only numbers.
    Potential errors are logged to stderr. If the number of errors reaches 10,
    the program stops.
    """

    hdgs_nb = 0
    nb_errors = 0
    errors = {
        "numbers" : 0,
        "index" : 0        
    }
    count_lines = {}
    max_error = 10

    list_hdgs = compareheaders(in_files)

    with open(out_file, "w") as outf:
        with open(in_files[0], "r") as firstfile:
            headingsff = firstfile.readline().strip()
            headings = headingsff.split("\t")
            hdgs_nb = len(headings)
            count_lines[in_files[0]] = 1

            hdrs_idx = getheadersindex(list_hdgs, headings)
            if col_names:
                for ix in col_names:
                    if not ix in hdrs_idx:
                        nb_errors += 1
                        sys.stderr.write(" ".join(["WARNING: column", str(ix), "in", in_files[0] ,
                                                   "does not exist in all files or has a different header."]) + "\n")
                        errors["index"] += 1
                hdrs_idx = col_names

            outf.write("\t".join([headings[y] for y in hdrs_idx]) + "\n")


            for fileline in firstfile:
                if nb_errors < max_error:
                    fileline = fileline.strip()
                    count_lines[in_files[0]] += 1
                    filestuff = fileline.split("\t")
                    outf.write("\t".join(filestuff[z] for z in hdrs_idx) + "\n")

                    for item in filestuff:
                        if not is_number(item): 
                            nb_errors += 1
                            sys.stderr.write(" ".join(["WARNING: line", str(count_lines[in_files[0]]),
                                                       "in", in_files[0] ,"contains non-numeric results"]) + "\n")
                            errors["numbers"] += 1
 
            for i in range(1, len(in_files)):
                if nb_errors < max_error:
                    with open(in_files[i], "r") as inf:
                        headingsinf = inf.readline().strip()
                        hdgs = headingsinf.split("\t")
                        count_lines[in_files[i]] = 1
                        
                        hdgs_idx = getheadersindex(list_hdgs, hdgs)
                        if col_names:
                            for iy in col_names:
                                if not iy in hdgs_idx:
                                    nb_errors += 1
                                    sys.stderr.write(" ".join(["WARNING: column", str(iy), "in", in_files[i],
                                                               "does not exist in all files or has a different header."]) + "\n")
                                    errors["index"] += 1
                            hdgs_idx = col_names

                        for otherlines in inf:
                            if nb_errors < max_error:
                                count_lines[in_files[i]] += 1
                                otherlines = otherlines.strip()
                                otherstuff = otherlines.split("\t")
                                outf.write("\t".join([otherstuff[xy] for xy in hdgs_idx]) + "\n")
                                
                                for item in otherstuff:
                                    if not is_number(item):
                                        nb_errors += 1
                                        sys.stderr.write(" ".join(["WARNING: line", str(count_lines[in_files[i]]),
                                                                   "in", in_files[i] ,"contains non-numeric results"]) + "\n")

    if nb_errors > 0:
        exit_code = 0
        if errors["numbers"] > 0:
            exit_code += 2
        if errors["index"] > 0:
            exit_code += 3
        if nb_errors == max_error:
            exit_code = 4
            sys.stderr.write("Run aborted - too many errors.")
            os.remove(out_file)
        sys.exit(exit_code)

    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog = "FCStxtmerge",
             description = "Merge based on headers text-converted FCS files into one text file.")

    parser.add_argument(
            '-i',
            dest = "input_files",
            required = True,
            action = 'append',
            help = "File location for the text files.")

    parser.add_argument(
            '-o',
            dest = "output_file",
            required = True,
            help = "Name of the output file.")

    parser.add_argument(
            '-c',
            dest = "columns",
            help = "Specify which column to keep in output file")


    args = parser.parse_args()
    
    defaultvalue=["i.e.:1,2,5", "default", "Default"]
    columns = []
    if args.columns:
        if not args.columns in defaultvalue:
            tmpcol = args.columns.split(",")
            if len(tmpcol) == 1:
                if not tmpcol[0].strip():
                    columns = []
                elif not is_integer(tmpcol[0].strip()):
                    sys.exit(7)
                else:
                    columns.append(int(tmpcol[0]) - 1)
            else:
                for c in range(0, len(tmpcol)):
                    if not is_integer(tmpcol[c]):
                        sys.exit(6)
                    else:
                        columns.append(int(tmpcol[c].strip()) - 1)

    input_files = [f for f in args.input_files]
    mergeFCStxt(input_files, args.output_file, columns)
    sys.exit(0)
