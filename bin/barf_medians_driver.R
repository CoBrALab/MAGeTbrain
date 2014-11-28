#source("/projects/mallar/archive/NIH_COS_2/Median_surface_code/barf_medians.R")
source("/home/m/mchakrav/patelmo6/Median_code/barf_medians.R")

args_in <- commandArgs()

x_path=args_in[6]
y_path=args_in[7]
z_path=args_in[8]
x_out =args_in[9]
y_out =args_in[10]
z_out =args_in[11]


print(x_path)
print(y_path)
print(z_path)
print(x_out)
print(y_out)
print(z_out)

find_medians(x_path, y_path, z_path, x_out, y_out, z_out)
