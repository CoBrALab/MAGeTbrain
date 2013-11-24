#!/bin/bash
set -e 

template=$1
output_root=$2
temp_dir=$(mktemp -d)
template_stem=$(basename $template .mnc)
mask=$temp_dir/mask.mnc
PROCESSORS=8

mincmath -max $output_root/labels/*/$template_stem/labels.mnc $temp_dir/max.mnc
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

