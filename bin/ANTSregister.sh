#!/bin/bash
from_image=$1
to_image=$2
output_xfm=$3

MINC_COMPRESS=9
mincANTS 3 -m PR[$from_image,$to_image,1,4] \
    --number-of-affine-iterations 10000x10000x10000x10000x10000 \
    --MI-option 32x16000 \
    --affine-gradient-descent-option 0.5x0.95x1.e-4x1.e-4 \
    --use-Histogram-Matching \
    -r Gauss[3,0] \
    -t SyN[0.5] \
    -o $output_xfm \
    -i 100x100x100x20

# clean up
rm $(dirname $output_xfm)/*inverse*
