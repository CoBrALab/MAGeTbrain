find_medians <- function(x_path, y_path, z_path, x_out, y_out, z_out){

	x <- read.csv(x_path, header=F)
	y <- read.csv(y_path, header=F)
	z <- read.csv(z_path, header=F)

	x_median <- apply(x, 1, median)
	y_median <- apply(y, 1, median)
	z_median <- apply(z, 1, median)


	write.table(x_median, file=x_out, append=FALSE, quote=FALSE, sep =" ", eol = "\n", row.names = F, col.names = F)	
	write.table(y_median, file=y_out, append=FALSE, quote=FALSE, sep =" ", eol = "\n", row.names = F, col.names = F)
	write.table(z_median, file=z_out, append=FALSE, quote=FALSE, sep =" ", eol = "\n", row.names = F, col.names = F)	

}