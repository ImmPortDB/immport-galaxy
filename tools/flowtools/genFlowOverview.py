#!/usr/bin/env python
from __future__ import print_function
import sys
import os
from argparse import ArgumentParser
from jinja2 import Environment, FileSystemLoader

from flowstatlib import gen_overview_stats
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from color_palette import color_palette

def genFlowOverview(flow_stats,args):
    os.mkdir(args.output_directory)

    env = Environment(loader=FileSystemLoader(args.tool_directory + "/templates"))
    template = env.get_template("genOverview.template")

    real_directory = args.output_directory.replace("/job_working_directory","")
    context = { 'outputDirectory': real_directory }
    overview = template.render(**context)
    with open(args.output_file,"w") as f:
        f.write(overview)

    flow_sample_file_name = args.output_directory + "/flow.sample"
    with open(flow_sample_file_name,"w") as flow_sample_file:
        flow_stats['sample'].to_csv(flow_sample_file,sep="\t",index=False,float_format='%.0f')
    
    flow_mfi_file_name = args.output_directory + "/flow.mfi"
    with open(flow_mfi_file_name,"w") as flow_mfi_file:
        flow_stats['mfi'].to_csv(flow_mfi_file,sep="\t",float_format='%.0f')

    #flow_pop_file_name = args.output_directory + "/flow.pop"
    #flow_pop_file = open(flow_pop_file_name,"w")
    #flow_stats['population_all'].to_csv(flow_pop_file,sep="\t",float_format='%.0f')

    flow_mfi_pop_file_name = args.output_directory + "/flow.mfi_pop"
    with open(flow_mfi_pop_file_name,"w") as flow_mfi_pop_file:
        flow_stats['mfi_pop'].to_csv(flow_mfi_pop_file,sep="\t",index=False, float_format="%.2f")
    
    # Generate the Images
    fcm = flow_stats['sample_data'].values
    colors = []
    for i,j in enumerate(flow_stats['sample_population']):
        colors.append(color_palette[j])

    for i in range(flow_stats['columns']):
        for j in range(flow_stats['columns']):
            file_name = "m" + str(i) + "_m" + str(j)
            ax = plt.subplot(1,1,1)
            plt.subplots_adjust(left=0.0,bottom=0.0,right=1.0,top=1.0,wspace=0.0,hspace=0.0)
            plt.scatter(fcm[:,i],fcm[:,j],s=1,c=colors,edgecolors='none')
            plt.axis([0,1024,0,1024])
            plt.xticks([])
            plt.yticks([])
            F = plt.gcf()
            F.set_size_inches(1,1)
            F.set_dpi(90)
            png_file = file_name + "_90X90.png"
            F.savefig(args.output_directory + "/" + png_file)
            plt.clf()
            #ax = plt.subplot(1,1,1)
            #plt.subplots_adjust(left=0.0,bottom=0.0,right=1.0,top=1.0,wspace=0.0,hspace=0.0)
            #plt.scatter(fcm[:,i],fcm[:,j],s=1,c=colors,edgecolors='none')
            #plt.axis([0,1024,0,1024])
            #plt.xticks([])
            #plt.yticks([])
            #F.set_size_inches(3,3)
            #F.set_dpi(100)
            #png_file = file_name + "_300X300.png"
            #F.savefig(args.output_directory + "/" + png_file)
            #F.set_size_inches(6,6)
            #F.set_dpi(100)
            #png_file = file_name + "_600X600.png"
            #F.savefig(args.output_directory + "/" + png_file)
            #plt.clf()

    flow_overview_file_name = args.output_directory + "/flow.overview"
    with open(flow_overview_file_name,"w") as flow_overview_file:
        flow_overview_file.write("<table>\n")
        flow_overview_file.write("<tr><td>&nbsp;</td>\n")
        for i in range(flow_stats['columns']):
            flow_overview_file.write("<td>" + flow_stats['markers'][i] + "</td>\n")

        for i in range(flow_stats['columns']):
            flow_overview_file.write("<tr>\n")
            flow_overview_file.write("<td>" + flow_stats['markers'][i] + "</td>\n")
            for j in range(flow_stats['columns']):
                file_name = "m" + str(j) + "_m" + str(i)
                image_file = file_name + "_90X90.png"
                flow_overview_file.write('<td><img src="' + image_file + '"/></td>')

            flow_overview_file.write("</tr>\n")

        flow_overview_file.write("</table>\n</body>\n<html>\n")

if __name__ == "__main__":
    parser = ArgumentParser(
             prog="genOverview",
             description="Generate an overview plot of Flow results.")

    parser.add_argument(
            '-i',
            dest="input_file",
            required=True,
            help="File location for the Flow Text file.")

    parser.add_argument(
            '-o',
            dest="output_file",
            required=True,
            help="File location for the HTML output file.")

    parser.add_argument(
            '-d',
            dest="output_directory",
            required=True,
            help="Directory location for the Flow Plot.")

    parser.add_argument(
            '-t',
            dest="tool_directory",
            required=True,
            help="Location of the Tool Directory.")

    args = parser.parse_args()

    flow_stats = gen_overview_stats(args.input_file)
    genFlowOverview(flow_stats,args)
    sys.exit(0)

