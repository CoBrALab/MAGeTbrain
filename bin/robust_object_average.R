library(MASS)

trimean <- function(X){
  #Implementation of Tukey's trimean robust average
  a <- quantile(X)
  result <- as.numeric(a[2] + 2*a[3] + a[4])/4
  return(result)
}

efficient_trimean <- function(X){
  #Boosted effciency (sensitivity) trimean, average of 20th, 50th and 80th percentiles
  a <- quantile(X, c(0.2,0.5,0.8))
  result <- mean(a)
  return(result)
}


huber_wrapper <- function(X){
  #huber M-estimator of central tendency, robust yet sensitive, computationally expensive
  result = huber(X)
  #Return only the mean estimate, throw away the SD estimate
  return(result$mu)
}

args_in <- commandArgs()

output = args_in[6]
inputs = args_in[7:length(args_in)]

conread = file(description=inputs[1], open="r")
header = readLines(conread, n = 1, warn = FALSE)
close(conread)

conwrite = file(description=output, open="w")
writeLines(header, con = conwrite)
close(conwrite)

npoints = as.numeric(strsplit(header, " ")[[1]][7])

xpoints = data.frame(matrix(nrow=npoints,ncol=0))
ypoints = data.frame(matrix(nrow=npoints,ncol=0))
zpoints = data.frame(matrix(nrow=npoints,ncol=0))

for (file in inputs){
  points <- read.table(file, skip = 1, nrows=npoints)
  xpoints = cbind(xpoints, points[,1])
  ypoints = cbind(ypoints, points[,2])
  zpoints = cbind(zpoints, points[,3])
}

#pointaverage = cbind(apply(xpoints,1,trimean), apply(ypoints,1,trimean), apply(zpoints,1,trimean))
#pointaverage = cbind(apply(xpoints,1,median), apply(ypoints,1,median), apply(zpoints,1,median))
pointaverage = cbind(apply(xpoints,1,huber_wrapper), apply(ypoints,1,huber_wrapper), apply(zpoints,1,huber_wrapper))

#Write out average points
write.table(pointaverage, file=output, append=TRUE, row.names=FALSE, col.names=FALSE)

#Re-open first input file to copy remaining data
conread = file(description=inputs[1], open="r")
sink("/dev/null")
#Read to the end of the points to skip this data
scan(conread, "", nlines = 1 + npoints, blank.lines.skip = FALSE, sep="\n")
sink()
#Read in trailer of file
trailer = scan(conread, "", blank.lines.skip = FALSE, sep="\n")
#Write out remaining data to new average file
cat(trailer, file = output, sep="\n", append = TRUE)
close(conread)
quit()
