#!/usr/bin/env python
from __future__ import print_function
import sys

from argparse import ArgumentParser

def is_integer(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def rearrangeFile(input_file, col_order, col_names, output_file):
    with open(input_file, "r") as infl, open(output_file, "w") as outf:
        ## headers
        hdrs = infl.readline().strip()
        current_hdrs = hdrs.split("\t")

        if col_names:
            tmphdr = []
            for i in range(0, len(col_names)):
                if col_names[i].strip():
                    tmphdr.append(col_names[i])
                else:
                    if col_order:
                        tmphdr.append(current_hdrs[col_order[i]])
                    else:
                        if len(col_names) != len(current_hdrs):
                            sys.exit(4)
                        tmphdr.append(current_hdrs[i])         
            hdrs = ("\t".join(tmphdr))
        elif col_order:
            tphdr = []
            for j in col_order:
                tphdr.append(current_hdrs[j])
            hdrs = ("\t".join(tphdr))
            
        outf.write(hdrs + "\n")
        
        ## columns
        for lines in infl:
            cols = lines.strip().split("\t")
            if not col_order:
                col_order = [x for x in range(0,len(current_hdrs))]
            outf.write("\t".join([cols[c] for c in col_order]) + "\n")
                

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="editColumnHeadings",
             description="Cut, rearrange and rename columns in a tab-separated file.")

    parser.add_argument(
            '-i',
            dest="input_file",
            required=True,
            help="File location for the text file.")

    parser.add_argument(
            '-c',
            dest="columns",
            help="Columns to keep in the order to keep them in.")

    parser.add_argument(
            '-n',
            dest="column_names",
            help="Column names if renaming.")

    parser.add_argument(
            '-o',
            dest="output_file",
            required=True,
            help="Name of the output file.")

    args = parser.parse_args()

    ## check column indices
    defaultvaluecol = ["i.e.:1,5,2", "default", "Default"]
    col_order = []
    if args.columns:
        if not args.columns in defaultvaluecol:
            tmpcol = args.columns.split(",")
            if len(tmpcol) == 1:
                if not tmpcol[0].strip():
                    col_order = []
                elif not is_integer(tmpcol[0].strip()):
                    sys.exit(2)
                else:
                    col_order.append(int(tmpcol[0].strip()) - 1)
            else:
                for c in range(0, len(tmpcol)):
                    if not is_integer(tmpcol[c].strip()):
                        sys.exit(3)
                    else:
                        col_order.append(int(tmpcol[c].strip()) - 1)

    ## check column names
    defaultvaluenms = ["i.e.:Marker1,,Marker4", "default", "Default"]
    col_names = []
    if args.column_names:
        if not args.column_names in defaultvaluenms:
            tmpnames = args.column_names.split(",")
            if col_order:
                if len(col_order) != len(tmpnames):
                    sys.exit(4)
            for cn in tmpnames:
                col_names.append(cn.strip())    
                
    rearrangeFile(args.input_file, col_order, col_names, args.output_file)

    sys.exit(0)


