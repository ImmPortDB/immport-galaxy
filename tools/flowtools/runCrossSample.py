#!/usr/bin/env python
from __future__ import print_function
import sys
import os
from scipy.stats import gmean
from argparse import ArgumentParser
from collections import defaultdict
import pandas as pd

#
# version 1.1 -- April 2016 -- C. Thomas
# modified to read in several input files and output to a directory + generates summary statistics
# also checks before running that input files are consistent with centroid file

def compareMFIs(inputfiles, fnames, mfi_file):
    headerMFIs = ""
    flag_error = False
    with open(mfi_file, "r") as mficheck:
        mfifl = mficheck.readline().split("\t")
        headerMFIs = "\t".join([mfifl[h] for h in range(1, len(mfifl))])
                
    for hh, files in enumerate(inputfiles):
        with open(files, "r") as inf:
            hdrs = inf.readline()
            if hdrs != headerMFIs:
                sys.stderr.write(hdrs + "headers in " + fnames[hh] + "are not consistent with FLOCK centroid file\n")
                flag_error = True
    if flag_error == True:
        sys.exit(2)
    
def statsMFIs(csdf, ctr, mfi_calc):
    if mfi_calc == "mfi":
        MFIs = csdf.groupby('Population').mean().round(decimals=2)
    elif mfi_calc == "gmfi":
        MFIs = csdf.groupby('Population').agg(lambda x: gmean(list(x))).round(decimals = 2)
    else:
        MFIs = csdf.groupby('Population').median().round(decimals=2)
    popfreq = (csdf.Population.value_counts(normalize=True) * 100).round(decimals=2)
    sortedpopfreq = popfreq.sort_index()
    MFIs['Percentage'] = sortedpopfreq
    MFIs['Population'] = MFIs.index
    MFIs['SampleName'] = "".join(["Sample", str(ctr).zfill(2)])
    return MFIs
    
def getPopProp(inputfiles, summary_stat, mfi_stats, marker_names, mfi_calc):
    popcount = defaultdict(dict)
    mrk = marker_names.strip().split("\t")
    markers = "\t".join([mrk[m] for m in range(1, len(mrk))])
    
    ctr_mfi = 0
    nbpop = 0
    tot = {}
    with open(mfi_stats, "a") as mfis:
        mfis.write("\t".join([markers, "Percentage", "Population", "SampleName"]) + "\n")
        for files in inputfiles:
            cs = pd.read_table(files)
            tot[files] = len(cs.index)
            for pops in cs.Population:
                if pops in popcount[files]:
                    popcount[files][pops] += 1
                else:
                    popcount[files][pops] = 1
            nbpop = len(popcount[files])
            ctr_mfi += 1
            cs_stats = statsMFIs(cs, ctr_mfi, mfi_calc)
            cs_stats.to_csv(mfis, sep="\t", header = False, index = False)
    
    ctr = 0            
    with open(summary_stat, "w") as outf:
        itpop = [str(x) for x in range(1, nbpop + 1)]
        cols = "\t".join(itpop)
        outf.write("FileID\tSampleName\t" + cols + "\n")
        for eachfile in popcount:
            tmp = []
            for num in range(1, nbpop + 1):
                if not num in popcount[eachfile]:
                    popcount[eachfile][num] = 0
                tmp.append(str((popcount[eachfile][num] / float(tot[eachfile])) * 100 ) )
            props = "\t".join(tmp)
            ctr += 1
            ph = "".join(["Sample", str(ctr).zfill(2)])
            outf.write("\t".join([inputfiles[eachfile], ph, props]) + "\n")

def runCrossSample(inputfiles, fnames, mfi_file, output_dir, summary_stat, mfi_stats, tool_directory, mfi_calc):
    markers = ""
    # Strip off Header Line
    with open(mfi_file,"r") as mfi_in, open("mfi.txt", "w") as mfi_out:
        markers = mfi_in.readline().strip("\n")
        for line in mfi_in:
           mfi_out.write(line)

    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
          
    outputs = {}
    # Run cent_adjust    
    for nm, flow_file in enumerate(inputfiles):
        run_command = tool_directory + "/bin/cent_adjust mfi.txt " + flow_file
        print(run_command)
        os.system(run_command)
        flowname = os.path.split(flow_file)[1]
        outfile = os.path.join(output_dir, flowname + ".crossSample")
        outputs[outfile] = fnames[nm]
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
    getPopProp(outputs, summary_stat, mfi_stats, markers, mfi_calc)
    return

def generateCSstats(mfi_stats, allstats):
    df = pd.read_table(mfi_stats)
    means = df.groupby('Population').mean().round(decimals = 2)
    medians = df.groupby('Population').median().round(decimals = 2)
    stdev = df.groupby('Population').std().round(decimals = 2)
    allmarkers = []
    with open(mfi_stats, "r") as ms:
        msfl = ms.readline().strip()
        allmarkers = msfl.split("\t")[0:-2]

    with open(allstats, "w") as mstats:
        hdgs = ["\t".join(["_".join([mrs, "mean"]),"_".join([mrs, "median"]),"_".join([mrs, "stdev"])]) for mrs in allmarkers]
        mstats.write("Population\t")
        mstats.write("\t".join(hdgs) + "\n")
        for pops in set(df.Population):
            tmpline = []
            for mar in allmarkers:
                tmpline.append("\t".join([str(means.loc[pops,mar]), str(medians.loc[pops,mar]), str(stdev.loc[pops,mar])]))
            mstats.write(str(pops) + "\t")
            mstats.write("\t".join(tmpline) + "\n")
            
                
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
            '-n',
            dest="filenames",
            required=True,
            action='append',
            help="Filenames")

    parser.add_argument(
            '-m',
            dest="mfi",
            required=True,
            help="File location for the MFI text file.")

    parser.add_argument(
            '-o',
            dest="out_path",
            required=True,
            help="Path to the directory for the output files.")

    parser.add_argument(
            '-M',
            dest="mfi_calc",
            required=True,
            help="what to calculate for centroids.")

    parser.add_argument(
            '-s',
            dest="sstat",
            required=True,
            help="File location for the summary statistics.")

    parser.add_argument(
            '-S',
            dest="mfi_stat",
            required=True,
            help="File location for the MFI summary statistics.")

    parser.add_argument(
            '-t',
            dest="tool_dir",
            required=True,
            help="File location for cent_adjust.")

    parser.add_argument(
            '-a',
            dest="allstats",
            required=True,
            help="File location for stats on all markers.")

    args = parser.parse_args()

    input_files = [f for f in args.input_files]
    input_names = [n for n in args.filenames]
    compareMFIs(input_files, input_names, args.mfi)
    runCrossSample(input_files, input_names, args.mfi, args.out_path, args.sstat, args.mfi_stat, args.tool_dir, args.mfi_calc)    
    generateCSstats(args.mfi_stat, args.allstats)
    
    sys.exit(0)
