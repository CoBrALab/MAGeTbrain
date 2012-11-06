#!/bin/bash
#
# Registers <atlas> to <target> and outputs the resulting xfm to output.xfm
#
# usage:
#      $0 <atlas.mnc> <target.mnc> <output.xfm>
#   
from_image=$1
to_image=$2
output_xfm=$3

MINC_COMPRESS=9

echo "-------------------------------------------------------------"
echo "$0:"
echo "From: $from_image"
echo "To: $to_image"
echo "Output: $output_xfm"
echo "-------------------------------------------------------------"

tmpdir=$(mktemp -d)
bestlinreg $from_image $to_image $tmpdir/lin.xfm && \
nlfit_smr_modelless -transform $tmpdir/lin.xfm $from_image $to_image $output_xfm
rm -rf $tmpdir

echo "-------------------------------------------------------------"
echo "$0: registration complete"
echo "-------------------------------------------------------------"
