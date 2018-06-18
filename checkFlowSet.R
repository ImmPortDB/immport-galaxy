#!/usr/bin/env Rscript
###########################################
#  Support for FlowSet sniffer function  #
############################################

sink(stdout(), type = "message")
library(flowCore)
sink(NULL, type="message")

checkFlowSet <- function(inputf) {
  isValid <- FALSE
  tryCatch({
    ff <- readRDS(inputf)
    if (class(ff)[[1]]=='flowSet'){
      isValid <- T
    }
  }, error = function(ex) {
    print("error reading file")
  })
  if (isValid) {
    print(TRUE)
  } else {
    print("not a valid flowSet object")
  }
}
args <- commandArgs(trailingOnly = TRUE)

checkFlowSet(args[1])
