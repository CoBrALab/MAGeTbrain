#!/bin/bash
#
# mincANTS registration using the "optimal" parameters for awesome brain to adni brain 
#
from_image=$1
to_image=$2
to_image_mask=$3
output_xfm=$4

# linear
#mincANTS 3 -m PR[$from_image,$to_image,1,4] \
#    -i 0 \
#    -o $linreg_xfm \
#    --number-of-affine-iterations 10000x10000x10000x10000x10000 \
#    --affine-gradient-descent-option 0.5x0.95x1.e-4x1.e-4 \
#    --MI-option 32x16000 

mincANTS 3 -m PR[$from_image,$to_image,1,4] \
    --number-of-affine-iterations 10000x10000x10000x10000x10000 \
    --MI-option 32x16000 \
    --affine-gradient-descent-option 0.5x0.95x1.e-4x1.e-4 \
    --use-Histogram-Matching \
    -x $to_image_mask \
    -r Gauss[7,0] \
    -t SyN[0.5] \
    -o $output_xfm \
    -i 5x3x1
    #-i 20x20x20 

