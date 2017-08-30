#!/usr/bin/env Rscript
############################################
#  Support for FlowSOM sniffer function  #
############################################

checkFlowSOM <- function(inputf) {
  isValid <- FALSE
  tryCatch({
    ff <- readRDS(inputf)
    if (class(ff)[[1]]=='FlowSOM'){
      isValid <- T
    }
  }, error = function(ex) {
    print("error reading file")
  })
  if (isValid) {
    print(TRUE)
  } else {
    print("not a valid flowSOM object")
  }
}
args <- commandArgs(trailingOnly = TRUE)

checkFlowSOM(args[1])
