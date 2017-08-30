#!/usr/bin/Rscript
# modify channels and marker names in FCS
#
######################################################################
#                  Copyright (c) 2017 Northrop Grumman.
#                          All rights reserved.
######################################################################
#
# Version 1
# Cristel Thomas
#
#
library(flowCore)

modifyMarkersFCS <- function(input, indices, newnames, channel=FALSE, report="",
                             output="", flag_fcs=FALSE) {
  fcs <- read.FCS(input, transformation=F)
  original_channels <- colnames(fcs)
  nb_channels <- length(original_channels)
  original_markers <- as.vector(pData(parameters(fcs))$desc)
  ## marker names
  if (channel) {
    channels <- colnames(fcs)
    for (i in 1:length(indices)) {
      if (indices[[i]] > nb_channels){
        quit(save = "no", status = 14, runLast = FALSE)
      }
      channels[[indices[[i]]]] <- newnames[[i]]
    }
    colnames(fcs) <- channels
  } else {
    markers <- as.vector(pData(parameters(fcs))$desc)
    for (i in 1:length(indices)) {
      if (indices[[i]] > nb_channels){
        quit(save = "no", status = 14, runLast = FALSE)
      }
      markers[[indices[[i]]]] <- newnames[[i]]
      pm <- paste("$P", as.character(indices[[i]]), "S", sep="")
      fcs@description[[pm]] <- newnames[[i]]
    }
    pData(parameters(fcs))$desc <- markers
  }
  post_channels <- colnames(fcs)
  post_markers <- as.vector(pData(parameters(fcs))$desc)

  # write report
  sink(report)
  cat("###########################\n")
  cat("##    BEFORE RENAMING    ##\n")
  cat("###########################\nFCS Channels\n")
  cat("---------------------------\n")
  cat(original_channels,"---------------------------", "FCS Markers","---------------------------",original_markers, sep="\n")
  cat("\n###########################\n")
  cat("##    AFTER  RENAMING    ##\n")
  cat("###########################\nFCS Channels\n")
  cat("---------------------------\n")
  cat(post_channels,"---------------------------","FCS Markers","---------------------------", post_markers, sep="\n")
  sink()

  # output fcs
  if (flag_fcs) {
    write.FCS(fcs, output)
  } else {
    saveRDS(fcs, file = output)
  }
}

checkFCS <- function(fcsfile, list_indices, list_names, flag_channel=FALSE,
                     out_file ="", report="", flag_fcs=FALSE) {
  isValid <- F
  tryCatch({
    isValid <- isFCSfile(fcsfile)
  }, error = function(ex) {
    print(paste(ex))
  })

  if (isValid) {
    modifyMarkersFCS(fcsfile, list_indices, list_names, flag_channel, report,
                     out_file, flag_fcs)
  } else {
    quit(save = "no", status = 10, runLast = FALSE)
  }
}

args <- commandArgs(trailingOnly = TRUE)
flag_fcs <- FALSE
flag_channel <- FALSE

if (args[3] == "FCS"){
  flag_fcs <- TRUE
}
if (args[7] == "C"){
  flag_channel <- TRUE
}
names <- list()
indices <- list()

# get indices
if (args[5]=="None" || args[5]== "" || args[5] == "i.e.:1,2,5") {
  warning('Please indicate which channels/markers to rename.')
  quit(save = "no", status = 11, runLast = FALSE)
} else {
  indices <- as.numeric(strsplit(args[5], ",")[[1]])
  for (idx in indices){
    if (is.na(idx)){
      quit(save = "no", status = 11, runLast = FALSE)
    }
  }
}

# get names
if (args[6]=="None" || args[6]== "" || args[6] == "i.e.:Marker1,Marker6,Marker4") {
  warning('Please indicate which channels/markers to rename.')
  quit(save = "no", status = 12, runLast = FALSE)
} else {
  names <- as.character(strsplit(args[6], ",")[[1]])
  for (name in names){
    if (is.na(name)){
      quit(save = "no", status = 12, runLast = FALSE)
    }
  }
}

# check if indices & names match
if (length(indices) != length(names)) {
  quit(save = "no", status = 13, runLast = FALSE)
}

checkFCS(args[1], indices, names, flag_channel, args[2], args[4], flag_fcs)
