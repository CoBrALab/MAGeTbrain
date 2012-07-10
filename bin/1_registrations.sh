#!/bin/bash
#
# Register all atlases to templates, and all templates to subjects
#
# usage:
#    <register.sh> <output_root>
#
#    where register.sh produces a transform from one image to another
# 
# parallel --semaphore --semaphorename 'multiatlas' --eta -j2
# sge_batch -l vf=4G -J multi \
#  bin/prop_labels.sh $register $output_root $atlas $template
register=$1
output_root=$2

(
for atlas in input_atlases/brains/*.mnc input_templates/brains/*.mnc; do
  atlas_stem=$(basename $atlas .mnc)
  for template in input_templates/brains/*.mnc; do
    template_stem=$(basename $template .mnc)
    output_dir=$output_root/registrations/$atlas_stem/$template_stem
    xfm=$output_dir/nl.xfm
    mkdir -p $output_dir
    echo $register $atlas $template $xfm
  done
done 

for template in input_templates/brains/*.mnc; do
  template_stem=$(basename $template .mnc)
  for subject in input_subjects/brains/*.mnc; do
    subject_stem=$(basename $subject .mnc)
    output_dir=$output_root/registrations/$atlas_stem/$template_stem
    xfm=$output_dir/nl.xfm
    mkdir -p $output_dir
    echo $register $template $subject $xfm
  done
done
) > 1_registrations_jobs
