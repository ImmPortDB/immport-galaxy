#!/usr/bin/Rscript
# 1D Density Plot Module for Galaxy
# ggcyto
######################################################################
#                  Copyright (c) 2016 Northrop Grumman.
#                          All rights reserved.
######################################################################
#
# Version 1
# Cristel Thomas
#
#

library(ggcyto)

generate1Dplot <- function(input, output, flag_pdf=FALSE, pdf_out="",
                           trans_method="None", factor="", log_w=0.5,
                           log_t=262144, log_m=4.5) {
  fcsfs <- read.flowSet(input, transformation=F)
  h <- 800
  w <- 1200
  if (length(fcsfs@colnames)>12){
    h <- 1200
    w <- 1600
  }
  p <- autoplot(fcsfs[[1]])
  if (trans_method == "arcsinh") {
    p <- p + scale_x_flowCore_fasinh(a = 0, b = factor, c = 0) + geom_density(fill="steelblue", alpha=0.5)
  } else if (trans_method == "logicle") {
    p <- p + scale_x_logicle(w=log_w, t=log_t, m=log_m) + geom_density(fill="paleturquoise", alpha=0.5)
  }

  png(output, type="cairo", height=h, width=w)
  print({
    p
  })
  dev.off()

  if (flag_pdf) {
    pdf(pdf_out, useDingbats=FALSE, onefile=TRUE)
    print({
      p
    })
    dev.off()
  }
}

checkFCS <- function(input_file, output_file, flag_pdf=FALSE, pdf_out="",
                     trans_met="None", factor="", w=0.5, t=262144, m=4.5) {
  isValid <- F
  # Check file beginning matches FCS standard
  tryCatch({
    isValid = isFCSfile(input_file)
  }, error = function(ex) {
    print (paste("    ! Error in isFCSfile", ex))
  })

  if (isValid) {
    generate1Dplot(input_file, output_file, flag_pdf, pdf_out, trans_met,
                   factor, w, t, m)
  } else {
    print (paste(input_file, "does not meet FCS standard"))
  }
}

args <- commandArgs(trailingOnly = TRUE)
flag_pdf <- FALSE
pdf_output <- ""
trans_method <- "None"
scaling_factor <- 1 / 150
w <- 0.5
t <- 262144
m <- 4.5

if (args[4] == "TRUE"){
  pdf_output <- args[5]
  flag_pdf <- TRUE
}

if (args[6]!="None"){
  trans_method <- args[6]
  if (args[6] == "arcsinh"){
    scaling_factor <- 1 / as.numeric(args[7])
  } else if (args[6] == "logicle"){
    w <- args[7]
    t <- args[8]
    m <- args[9]
  }
}

checkFCS(args[2], args[3], flag_pdf, pdf_output, trans_method, scaling_factor,
         w, t, m)
