#!/bin/bash
#
# Generates template masks before template-to-subject registration
#
# # Usage: template output_dir  
#
# For both we go about this same way: 
# 1. Create a generous mask around the label area for each template
# 2. Calculate the NMI/XCORR scores between the template and subject 
#
# Masks are computed by linearly registering the templates to the atlases,
# VOTING the resampled labels to get rough field for potential label targets,
# and expanding that masked area somewhat for good measure.

template=$1
output_root=$2

shopt -s expand_aliases
PROCESSORS=8

template_stem=$(basename $template .mnc)

#1_vote

voxel_vote.py $output_root/labels/*/$(basename $template .mnc)/labels.mnc $output_root/template_masking/1_voted/$(basename $template .mnc)_voted.mnc

#2_cropped
autocrop -bbox $output_root/template_masking/1_voted/$(basename $template .mnc)_voted.mnc -isoexpand 5 $template $output_root/template_masking/2_cropped/$(basename $template .mnc)_cropped.mnc

#3_template_mask
minccalc -expression 'A[0] > 0 ? 1 : 0' $output_root/template_masking/2_cropped/$(basename $template .mnc)_cropped.mnc $output_root/template_masking/3_template_mask/$(basename $template .mnc)-mask.mnc
