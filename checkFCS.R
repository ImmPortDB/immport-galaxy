#!/usr/bin/env Rscript
######################################
#  Support for FCS sniffer function  #
######################################

sink(stdout(), type = "message") 
library(flowCore)
sink(NULL, type="message")

checkFCSfile <- function(inputf) {
  isValid <- FALSE
  tryCatch({
    isValid <- isFCSfile(inputf)
  }, error = function(ex) {
    print("error reading file")
  })
  if (isValid) {
    print(TRUE)
  } else {
    print("not a valid FCS file")
  }
}
args <- commandArgs(trailingOnly = TRUE)

checkFCSfile(args[1])
