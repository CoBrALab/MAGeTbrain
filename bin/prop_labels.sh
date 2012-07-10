#!/bin/bash
#
# Do a registration and propogation of labels, and also compute label similarity 
#
# usage:
#    <register.sh> <output_root> <atlas> <template>
#
register=$1
output_root=$2
atlas=$3
template=$4


## BEGIN ##
atlas_dir=$(dirname $atlas)
atlas_stem=$(basename $atlas .mnc)
atlas_mask=$atlas_dir/${atlas_stem}-mask.mnc
atlas_labels=atlases/labels/${atlas_stem}_labels.mnc

template_stem=$(basename $template .mnc)
template_labels=input/labels/${template_stem}_labels.mnc
output_dir=$output_root/registrations/$atlas_stem/$template_stem
xfm=$output_dir/nl.xfm
gen_labels_dir=$output_root/labels/$atlas_stem/$template_stem
gen_labels=$gen_labels_dir/labels.mnc 
sim_results=$gen_labels_dir/similarity.csv

mkdir -p $output_dir $gen_labels_dir 

# register template to atlas
if [ ! -e $xfm ]; then
  $register $atlas $template $atlas_mask $xfm
fi

# propogate labels
if [ ! -e $gen_labels ]; then
  mincresample -2 -near -transform $xfm -like $template $atlas_labels $gen_labels
fi 

# check accuracy 
volume_similarity --csv $template_labels $gen_labels | grep '^1,\|^101,' > $sim_results
