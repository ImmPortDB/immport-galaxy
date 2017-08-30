#!/usr/bin/env Rscript
############################################
#  Support for FlowFrame sniffer function  #
############################################

library(flowCore)

checkFlowFrame <- function(inputf) {
  isValid <- FALSE
  tryCatch({
    ff <- readRDS(inputf)
    if (class(ff)[[1]]=='flowFrame'){
      isValid <- T
    }
  }, error = function(ex) {
    print("error reading file")
  })
  if (isValid) {
    print(TRUE)
  } else {
    print("not a valid flowframe")
  }
}
args <- commandArgs(trailingOnly = TRUE)

checkFlowFrame(args[1])
