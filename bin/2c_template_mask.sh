#!/bin/bash
#
# Generate template masks
# 

output_dir=$PWD/output/
mkdir -p $output_dir/template_masking/{1_voted,2_cropped,3_template_mask}

for template in input/templates/brains/*.mnc; do
  echo template_masking.sh $template $output_dir
done > 2b_maskings_jobs