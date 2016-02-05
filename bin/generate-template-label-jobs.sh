#!/bin/bash
#
# Propogation labels from the atlases to the templates
# Expects that the registrations are complete.
# Helper for deciding on templates if you have issues with your random sample
#
# Usage:
# ./generate-template-label-jobs.sh > joblist
# Use parallel or bash or qbatch to run the jobs
# Be sure to run this from project dir, ie in the parent directory of input and output

output_root=$PWD/output
for atlas in input/atlases/brains/*.mnc; do

  atlas_stem=$(basename $atlas .mnc)
  atlases_dir=$(dirname $(dirname $atlas))
  atlas_labels=$atlases_dir/labels/${atlas_stem}_labels.mnc

  for template in input/templates/brains/*.mnc; do
  #for template in $output_root/modelspace/input/templates/*.mnc; do

    template_stem=$(basename $template .mnc)
    templates_dir=$(dirname $(dirname $template))
    template_labels=$templates_dir/labels/${template_stem}_labels.mnc

    xfm=$output_root/registrations/$atlas_stem/$template_stem/nl.xfm

    gen_labels_dir=$output_root/labels/$atlas_stem/$template_stem
    gen_labels=$gen_labels_dir/labels.mnc

    mkdir -p $gen_labels_dir

    [ ! -e $gen_labels ] && echo mincresample -2 -near -byte -keep -transform $xfm -like $template $atlas_labels $gen_labels
  done
done
