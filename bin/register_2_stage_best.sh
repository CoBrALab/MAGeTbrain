#!/bin/bash
#
# usage:
#      register <atlas.mnc> <target.mnc> <atlas_mask.mnc> <output.xfm>
#
#   
atlas=$1
target=$2
atlas_mask=$3
output_xfm=$4
output_dir=$(dirname $output_xfm)
AT_lin_xfm=$output_dir/ATlin.xfm
TA_lin_xfm=$output_dir/ATlin_inverse.xfm
TA_nl_xfm=$output_dir/TAnl.xfm
AT_nl_xfm=$output_dir/TAnl_inverse.xfm
atlas_res=$output_dir/linres.mnc
atlas_res_mask=$output_dir/masklinres.mnc

# LINEAR  
mincANTS 3 -m PR[$atlas,$target,1,4] \
    -i 0 \
    -o $AT_lin_xfm \
    --number-of-affine-iterations 10000x10000x10000x10000x10000 \
    --affine-gradient-descent-option 0.5x0.95x1.e-4x1.e-4 \
    --MI-option 32x16000 

mincresample -like $target -transform $AT_lin_xfm $atlas $atlas_res 
mincresample -like $target -transform $AT_lin_xfm $atlas_mask $atlas_res_mask

# NONLINEAR
mincANTS 3 -m PR[$target,$atlas_res,1,4] \
    -x $atlas_res_mask \
    --continue-affine false \
    --use-Histogram-Matching \
    -r Gauss[7,0] \
    -t SyN[0.5] \
    -o $TA_nl_xfm \
    -i 20x20x20

xfmconcat $AT_lin_xfm $AT_nl_xfm $output_xfm
