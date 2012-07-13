#!/bin/bash
#
# Register all atlases to templates, and all templates to subjects
#
usage() {
cat <<EOF
    $0 register_script 

    register_script - path to script to do registration (see bin/register.sh) 
EOF
}

if [ -z "$1" ]; then
  usage
  exit 
fi 

register=$1

output_root=$PWD/output
(
for atlas in input/atlases/brains/*.mnc; do
  atlas_stem=$(basename $atlas .mnc)
  for template in input/templates/brains/*.mnc; do
    template_stem=$(basename $template .mnc)
    output_dir=$output_root/registrations/$atlas_stem/$template_stem
    xfm=$output_dir/nl.xfm
    mkdir -p $output_dir
    [ ! -e $xfm ] && echo $register $atlas $template $xfm
    
  done
done 

for template in input/templates/brains/*.mnc; do
  template_stem=$(basename $template .mnc)
  for subject in input/subjects/brains/*.mnc; do
    subject_stem=$(basename $subject .mnc)
    output_dir=$output_root/registrations/$template_stem/$subject_stem
    xfm=$output_dir/nl.xfm
    mkdir -p $output_dir
    [ ! -e $xfm ] && echo $register $template $subject $xfm
  done
done
) > 1_register_jobs
