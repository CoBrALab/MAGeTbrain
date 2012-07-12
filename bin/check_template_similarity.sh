#!/bin/bash
#
# Compute the similarity of the propagated template labels to the actual
#
# Expects that the template labels have been generated, of course.
#
# usage: <output_root> 
#
output_root=$1

temp_dir=$(mktemp -d)

for template in $output_root/labels/*/*; do
    template_stem=$(basename $template)
    atlas_stem=$(basename $(dirname $template))

    template_labels=input/templates/labels/${template_stem}_labels.mnc
    gen_labels=$template/labels.mnc 

    temp_results_dir=$temp_dir/labels/$atlas_stem/$template_stem
    sim_results=$temp_results_dir/similarity.csv

    mkdir -p $temp_results_dir 

    echo "volume_similarity --csv $template_labels $gen_labels | grep '^1,\|^101,' \
        | sed -e 's/$/,$template_stem,$atlas_stem/' > $sim_results"
done | parallel -j8

cat $temp_dir/labels/*/*/*.csv > $output_root/multi_atlas_similarity.csv

rm -rf $temp_dir
