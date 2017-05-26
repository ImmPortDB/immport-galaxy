#!/usr/bin/Rscript
# Stacked 1D Density Plot Module for Galaxy
# flowviz
######################################################################
#                  Copyright (c) 2016 Northrop Grumman.
#                          All rights reserved.
######################################################################
#
# Version 1
# Cristel Thomas
#
#

library(flowViz)
library(methods)

generateStackedPlots <- function(fs, chans="", output="", flag_pdf=FALSE, pdf_out="") {
  h <- 800
  w <- 1200
  if (length(fs@colnames)>8){
    h <- 1200
    w <- 1600
  }
  channels_to_plot <- fs@colnames
  if (chans != ""){
    channels_to_plot <- fs@colnames[chans]
  }
  png(output, type="cairo", height=h, width=w)
  print({
    densityplot(~., fs, channels = channels_to_plot)
  })
  dev.off()

  if (flag_pdf) {
    pdf(pdf_out, useDingbats=FALSE, onefile=TRUE)
    print({
      densityplot(~., fs, channels = channels_to_plot)
    })
    dev.off()
  }
}

checkFlowSet <- function(fcsfiles, newnames, channels="", out_file ="",
                         flag_pdf=FALSE, pdf_out="") {
  isValid <- F
  # Check file beginning matches FCS standard
  tryCatch({
    fs <- read.flowSet(files=fcsfiles, transformation=FALSE)
    isValid <- T
  }, error = function(ex) {
    print(paste(ex))
  })

  if (isValid) {
    fs@phenoData@data$name <- newnames
    generateStackedPlots(fs, channels, out_file, flag_pdf, pdf_out)
  } else {
    quit(save = "no", status = 12, runLast = FALSE)
  }
}

args <- commandArgs(trailingOnly = TRUE)
channels <- ""
flag_pdf <- FALSE
pdf_output <- ""

if (args[2]=="None") {
  flag_default <- TRUE
} else {
  if (args[2] == "i.e.:1,3,4"){
    flag_default <- TRUE
  } else {
    channels <- as.numeric(strsplit(args[2], ",")[[1]])
    for (channel in channels){
      if (is.na(channel)){
        quit(save = "no", status = 11, runLast = FALSE)
      }
    }
    if (length(channels) == 1){
      warning('Please indicate more than one marker to plot.')
      quit(save = "no", status = 10, runLast = FALSE)
    }
  }
}

if (args[4] == "TRUE"){
  pdf_output <- args[5]
  flag_pdf <- TRUE
}

nb_files <- (length(args) - 5) / 2
fcsfiles <- character(nb_files)
newnames <- character(nb_files)
j <- 1
## get files and file names
for (i in 6:length(args)) {
  if (!i%%2){
    fcsfiles[j] <- args[i]
    newnames[j] <- args[i+1]
    j <- j + 1
  }
}

checkFlowSet(fcsfiles, newnames, channels, args[3], flag_pdf, pdf_output)
