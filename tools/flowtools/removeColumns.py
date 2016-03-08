#!/usr/bin/env python
from __future__ import print_function
import sys
from argparse import ArgumentParser

def removeColumns(input_file_name, output_file_name, column_list):
    remove_column_str = column_list.split(",")
    remove_columns = []
    for c in remove_column_str:
        remove_columns.append(int(c) -1)
    input_file = open(input_file_name,"r")
    output_file = open(output_file_name,"w")
    for line in input_file:
        line = line.strip()
        data = line.split("\t")
        new_data = []
        for i,c in enumerate(data):
            if i not in remove_columns:
                new_data.append(c)
        
        new_line = "\t".join(new_data) + "\n"
        output_file.write(new_line)
    input_file.close()
    output_file.close()
    return

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="removeColumns",
             description="Remove columns from Flow Text file.")

    parser.add_argument(
            '-i',
            dest="input_file",
            required=True,
            help="File location for the FCS Text file.")

    parser.add_argument(
            '-o',
            dest="output_file",
            required=True,
            help="File location for the output file.")

    parser.add_argument(
            '-c',
            dest="column_list",
            required=True,
            help="List of columns to remove.")


    args = parser.parse_args()

    removeColumns(args.input_file, args.output_file, args.column_list)
    sys.exit(0)

