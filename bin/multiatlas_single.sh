#!/bin/bash
#
# 
# Like multi_atlas.sh, but runs this for a single template
#
#   usage: multi_atlas_single.sh <template.mnc> <output_folder> <registration_script>
#

template=$1
output_root=$2
registration_sh=$3
echo "$@" > $output_root/cmdline
for atlas in atlases/brains/anusha.mnc; do
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
    echo "$registration_sh $template $atlas $atlas_mask $xfm"
  fi

  # propogate labels
  if [ ! -e $gen_labels ]; then
    echo "mincresample -2 -near -invert -transform $xfm -like $template \
    $atlas_labels $gen_labels"
  fi 

  # check accuracy 
  echo "volume_similarity --csv $template_labels $gen_labels |  \
    grep '^1,\|^101,' > $sim_results"
  results_files="$results_files $sim_results"
done; 
