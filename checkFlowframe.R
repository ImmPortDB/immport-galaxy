#!/usr/bin/env Rscript
############################################
#  Support for FlowFrame sniffer function  #
############################################

sink(stdout(), type = "message")
library(flowCore)
sink(NULL, type="message")

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
