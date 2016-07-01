#
# ImmPort FCS conversion program
#
# Authors: Yue Liu and Yu "Max" Qian
#
# Reference: FCSTrans: An open source software system for FCS
#            file conversion and data transformation
#            Qian Y, Liu Y, Campbell J, Thomson E, Kong YM,
#            Scheuermann RH. 2012 Cytometry Part A. 81A(5)
#            doi.org/10.1002/cyto.a.22037
#
# To run in R
# 1) library(flowCore)
# 2) source("FCSTrans.R")
# 3) transformFCS("filename")
#
# Version 1.4.1
# March 2016 -- added lines to run directly from command line
#

library(flowCore)

#
# Set output to 0 when input is less than cutoff value
#
ipfloor <- function (x, cutoff = 0, target = 0) {
    y = x
    if (x <= cutoff) y = target
    y
}

#
# Set output to 0 when input is less than cutoff value
#
ipceil <- function (x, cutoff = 0, target = 0) {
    y = x
    if (x >= cutoff) y = target
    y
}

#
# Calculation core of iplogicle
#
iplogicore <- function (x, w, r, d, scale) {
    tol = .Machine$double.eps^0.8
    maxit = as.integer(5000)
    d = d * log(10)
    scale = scale / d
    p = if (w == 0)
        1
    else uniroot(function(p) -w + 2 * p * log(p)/(p + 1), c(.Machine$double.eps, 
        2 * (w + d)))$root
    a = r * exp(-(d - w))
    b = 1
    c = r * exp(-(d - w)) * p^2
    d = 1/p
    f = a * (p^2 - 1)
    y = .Call("biexponential_transform", as.double(x), a, b, c, d, f, w, tol, maxit)
    y = sapply(y * scale, ipfloor)
    y
}

#
# Function for calculating w
#
iplogiclew <- function (w, cutoff = -111, r = 262144, d = 4.5, scale = 1) {
    if (w > d)
        w = d
    y = iplogicore(cutoff, w, r, d, scale) - .Machine$double.eps^0.6
    y
}

#
# ImmPort logicle function - convert fluorescent marker values to channel output
#
iplogicle <- function (x, r=262144, d=4.5, range=4096, cutoff=-111, w=-1) {
    if (w > d)
        stop("Negative range decades must be smaller than total number of decades")
    if (w < 0)
        w = uniroot(iplogiclew, c(0, d), cutoff=cutoff)$root
    y = iplogicore(x, w, r, d, range)
    y
}

#
# Convert fluorescent values to channel output using log transformation
#
iplog <- function(x) {
    x = sapply(x, ipfloor, cutoff=1, target=1)
    y = 1024 * log10(x) - 488.6
    y
}

#
# ImmPort linear function - convert scatter values to channel output
# linear transformation
#
ipscatter <- function (x, channelrange=262144) {
    y = 4095.0 * x / channelrange
    y = sapply(y, ipfloor)
    y = sapply(y, ipceil, cutoff=4095, target=4095)
    y
}

#
# ImmPort time function - convert time values to channel output
# linear transformation
iptime <- function (x, channelrange) {
    # use simple cutoff for now
    y = sapply(x, ipfloor)
    y
}


#
# Determine the type of marker. Marker type is used
# to determine type of transformation to apply for this channel.
# Before 2010 FLUO_AREA type used iplogicile and
# FLOU_NON_AREA type used iplog. In 2010 Yue, changed code so
# all flourecent channels use iplogicle. Below is the note from SVN
#
# Version 1.1
# 2010-07-02
# -----------
# Added data type checking on both FCS version 2 and 3
# Removed log conversion for non-area fluorescent channel
# Applied logicle conversion for all fluorescent channels
#
# The GenePattern version uses iplog for FLOU_NON_AREA, rather
# than iplogicle.
#
getMarkerType <- function(name,debug=FALSE) {
    type = ""
    prefix2 = toupper(substr(name, 1, 2))
    prefix3 = toupper(substr(name, 1, 3))
    prefix4 = toupper(substr(name, 1, 4))
    if (prefix2 == "FS" || prefix2 == "SS") {
        type = "SCATTER"
    } else if (prefix3 == "FSC" || prefix3 == "SSC") {
        type = "SCATTER"
    } else if (prefix4 == "TIME") {
        type = "TIME"
    } else {
        pieces = unlist(strsplit(name, "-"))
        if (toupper(pieces[length(pieces)]) == "A") {
            type = "FLUO_AREA"
        } else {
            type = "FLUO_NON_AREA"
        }
    }
    if (debug) {
        print(paste("Marker:", name, ", Type:", type))
    }
    type
}

#
# Scale data
#
scaleData <- function(data, channelrange=0) {
    datamax = range(data)[2]  # range() returns [min, max]
    if (datamax > channelrange) {
        channelrange = datamax
    }
    #if (channelrange == 0) {
    #    channelrange = range(data)[2]
    #}
    data = 262144 * data / channelrange
    data
}


#
# Check if AccuriData. Accuri data needs different conversion
#
isAccuriData <- function(keywords) {
    isTRUE(as.character(keywords$"$CYT") == "Accuri C6")
}

#
# Convert Accuri FCS file
#
convertAccuriFCS <- function(fcs,compensate=FALSE,debug=FALSE) {
    if (debug) {
     print("Inside convertAccuriFCS")
     print(paste("Compensate: ",compensate))
    }
}

#
# Convert FCS file
#
convertFCS <- function(fcs,compensate=FALSE,debug=FALSE) {
    # Check file type and FCS version
    if (class(fcs)[1] != "flowFrame") {
        print("convertFCS requires flowFrame object as input")
        return(FALSE)
    }

    keywords = keyword(fcs)
    markers = colnames(fcs)
    print_markers = as.vector(pData(parameters(fcs))$desc)
    # Update print_markers if the $P?S not in the FCS file
    for (i in 1:length(print_markers)) {
        if (is.na(print_markers[i])) {
            print_markers[i] = markers[i]
        }
    }

    if (debug) {
        print("****Inside convertFCS")
        print(paste("    FCS version:", keywords$FCSversion))
        print(paste("    DATATYPE:", keywords['$DATATYPE']))
    }

    if (keywords$FCSversion == "2" ||
        keywords$FCSversion == "3" ||
        keywords$FCSversion == "3.1" ) {
        datatype = unlist(keywords['$DATATYPE'])
        if (datatype == 'F') {
            # Apply compensation if available and requested
            spill = keyword(fcs)$SPILL

            if (is.null(spill) == FALSE && compensate == TRUE) {
                if (debug) {
                    print("Attempting compensation")
                }
                tryCatch({ fcs = compensate(fcs, spill) },
                           error = function(ex) { str(ex); })
            }

            # Process fcs expression data, using transformation
            # based on category of the marker.
            fcs.exprs = exprs(fcs)
            fcs.channel = NULL
            for (i in 1:length(markers)){
                markertype = getMarkerType(markers[i],debug)
                rangekeyword = paste("$P", i, "R", sep="")
                channelrange = as.numeric(keywords[rangekeyword])
                if (debug) {
                    print(paste("    Marker name:",markers[i]))
                    print(paste("    Marker type:",markertype))
                    print(paste("    Range value:", keywords[rangekeyword]))
                }
                if (markertype == "SCATTER") {
                    channel = ipscatter(scaleData(fcs.exprs[, i], channelrange))
                } else if (markertype == "TIME") {
                    channel = iptime(fcs.exprs[, i])
                } else {
                    # Apply logicle transformation on fluorescent channels
                    channel = iplogicle(scaleData(fcs.exprs[, i], channelrange))
                }
                fcs.channel = cbind(fcs.channel, round(channel))
            }
            colnames(fcs.channel) = print_markers
        } else if (datatype == 'I') {
            fcs.channel = exprs(fcs)
            colnames(fcs.channel) = print_markers
        } else {
            print(paste("Data type", datatype, "in FCS 3 is not supported"))
            fcs.channel = FALSE
        }
    } else {
        print(paste("FCS version", keyword(fcs)$FCSversion, "is not supported"))
        fcs.channel = FALSE
    }
    fcs.channel
}


#
# Starting function for processing a FCS file
#
processFCSFile <- function(input_file, output_file="",
                           keyword_file="",compensate=FALSE, debug=FALSE) {

    #
    # Generate the file names for the output_file and keyword_file
    #
    pieces = unlist(strsplit(input_file, .Platform$file.sep))
    filename = pieces[length(pieces)]

    if (output_file == "") {
        filepieces = unlist(strsplit(filename, '\\.'))
        #replace .fcs with .txt; append .txt if not ending in .fcs
        if (filepieces[length(filepieces)] == 'fcs') {
            filepieces[length(filepieces)] = 'txt'
        } else {
            filepieces[length(filepieces)+1] = 'txt'
        }
        output_file = paste(filepieces, collapse = '.')
    }

    if (keyword_file == "") {
        filepieces = unlist(strsplit(filename, '\\.'))
        #replace .fcs with .keyword; append .keyword if not ending in .fcs
        if (filepieces[length(filepieces)] == 'fcs') {
            filepieces[length(filepieces)] = 'keyword'
        } else {
            filepieces[length(filepieces)+1] = 'keyword'
        }
        keyword_file = paste(filepieces, collapse = '.')
    }

    if (debug) {
        print (paste("Converting file: ",input_file))
        print (paste("Original file name: ",filename))
        print (paste("Output file name: ",output_file))
        print (paste("Keyword file name: ",keyword_file))
    }
    fcs <- read.FCS(input_file, transformation=F)
    keywords <- keyword(fcs)
    write.table(as.matrix(keywords),file=keyword_file, quote=F,
                row.names=T, col.names=F, sep='=', append=F)

    # 
    # Now Transform the data
    #
    if (isAccuriData(keywords)) {
      transformed_data = convertAccuriFCS(fcs,compensate,debug)
    } else {
      transformed_data = convertFCS(fcs,compensate,debug)
    }
    write.table(transformed_data, file=output_file, quote=F,
                row.names=F,col.names=T, sep='\t', append=F)
}

# Convert FCS file using FCSTrans logicile transformation
# @param input_file     FCS file to be transformed
# @param output_file    FCS file transformed ".txt" extension
# @param keyword_file   FCS file keywords ".keywords" extension"
# @param compensate     Flag indicating whether to apply compensation
#                       matrix if it exists.
transformFCS <- function(input_file, output_file="", compensate=FALSE,
                         keyword_file="", debug=FALSE) {

    isValid = F
    # Check file beginning matches FCS standard
    tryCatch({
        isValid = isFCSfile(input_file)
    }, error = function(ex) {
        print (paste("    ! Error in isFCSfile", ex))
    })

    if (isValid) {
        processFCSFile(input_file, output_file, keyword_file, compensate, debug)
    } else {
        print (paste(input_file, "does not meet FCS standard"))
    }
}

args <- commandArgs(trailingOnly = TRUE)
transformFCS(args[2], args[3], args[4])
