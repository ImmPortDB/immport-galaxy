#
# Density Plot Module for Galaxy
# FlowDensity
# 
# Version 1
# Cristel Thomas
#
#

library(flowCore)
library(flowDensity)

generateGraph <- function(input, channels, output) {
  fcs <- read.FCS(input, transformation=F)
  nb_markers <- length(channels)
  ## marker names
  markers <- colnames(fcs)
  print_markers <- as.vector(pData(parameters(fcs))$desc)
  # Update print_markers if the $P?S not in the FCS file
  for (i in 1:length(print_markers)) {
    if (is.na(print_markers[i])) {
      print_markers[i] <- markers[i]
    }
  }
  pdf(output, useDingbats=FALSE, onefile=TRUE) 
  par(mfrow=c(2,2))
  for (m in 1:(nb_markers - 1)) {
    for (n in (m+1):nb_markers) {
      plotDens(fcs, c(channels[m],channels[n]), xlab = print_markers[channels[m]], ylab = print_markers[channels[n]])
    }
  }
  dev.off()
}

checkFCS <- function(input_file, channels, output_file) {
  isValid <- F
  # Check file beginning matches FCS standard
  tryCatch({
    isValid = isFCSfile(input_file)
  }, error = function(ex) {
    print (paste("    ! Error in isFCSfile", ex))
  })

  if (isValid) {
    generateGraph(input_file, channels, output_file)
  } else {
    print (paste(input_file, "does not meet FCS standard"))
  }
}

args <- commandArgs(trailingOnly = TRUE)
channels <- ""

if (args[3]!="None") {
  if (args[3] == "i.e.:1,3,4"){
  	quit(save = "no", status = 10, runLast = FALSE)
  }
  channels <- as.numeric(strsplit(args[3], ",")[[1]])
  for (channel in channels){
	if (is.na(channel)){
	  quit(save = "no", status = 11, runLast = FALSE)
	} 
  }
} else {
  quit(save = "no", status = 10, runLast = FALSE)
}

checkFCS(args[2], channels, args[4])
