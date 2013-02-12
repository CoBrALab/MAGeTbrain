#!/bin/bash
#
# Register all atlases to templates, and all templates to subjects
#
usage() {
cat <<EOF
    $0 [-t] register_script 

    register_script - path to script to do registration (see bin/register.sh) 
    -t              - emit tasks for template to subject registrations
EOF
}

if [ -z "$1" ]; then
  usage
  exit 
fi

if [ "$1" == "-t" ]; then
  do_tmpl_to_sub_reg=T
  shift
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

if [ -n "$do_tmpl_to_sub_reg" ]; then
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
fi;
) > 1_register_jobs
