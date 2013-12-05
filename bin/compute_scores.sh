#!/bin/bash
set -e 

template=$1
output_root=$2
temp_dir=$(mktemp -d)
template_stem=$(basename $template .mnc)
mask=$temp_dir/mask.mnc
PROCESSORS=16

# propogate labels from atlases to template
for atlas_labels in input/atlases/labels/*.mnc; do
    atlas_stem=$(basename $atlas_labels _labels.mnc)
    linxfm=$temp_dir/${atlas_stem}_${template_stem}_lin.xfm
    labels=$temp_dir/${atlas_stem}_${template_stem}_labels.mnc

    xfm=$output_root/registrations/$atlas_stem/$template_stem/nl.xfm
    echo linxfm $xfm $linxfm ';' \
    mincresample -2 -like $template -transform $linxfm $atlas_labels $labels 
done | tee | parallel -j$PROCESSORS

echo mincmath -max $temp_dir/*_${template_stem}_labels.mnc $temp_dir/max.mnc
mincmath -max $temp_dir/*_${template_stem}_labels.mnc $temp_dir/max.mnc
echo minccalc -expression 'max(A)>0' $temp_dir/max.mnc $temp_dir/threshold.mnc
minccalc -expression 'max(A)>0' $temp_dir/max.mnc $temp_dir/threshold.mnc
echo mincmorph -successive DDD $temp_dir/threshold.mnc $mask 
mincmorph -successive DDD $temp_dir/threshold.mnc $mask 

for subject in input/subjects/brains/*.mnc; do
    subject_stem=$(basename $subject .mnc)
    score_dir=$output_root/scores/$template_stem/$subject_stem
    mkdir -p $score_dir
    xfm=$output_root/registrations/$template_stem/$subject_stem/nl.xfm
    linxfm=$temp_dir/${subject_stem}_invlin.xfm
    linres=$temp_dir/${subject_stem}_invlin.mnc

    echo linxfm $xfm $linxfm ';' \
    mincresample -2 -like $template -invert -transform $linxfm $subject $linres ';' \
    xcorr_vol.sh $linres $template $mask $score_dir/xcorr.txt ';' \
    nmi_vol.sh $linres $template $mask $score_dir/nmi.txt 
done | tee | parallel -j$PROCESSORS
rm -rf $temp_dir

