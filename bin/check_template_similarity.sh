#!/bin/bash
#
# Compute the similarity of the propagated template labels to the actual
#
# Expects that the template labels have been generated, of course.
#
# usage: <output_root> 
#
#PBS -l nodes=1:ppn=8,walltime=2:00:00
#PBS -j oe
#PBS -o logs
#PBS -V
cd $PBS_O_WORKDIR
output_root=output

for template in $output_root/labels/*/*; do
    template_stem=$(basename $template)
    atlas_stem=$(basename $(dirname $template))

    template_labels=input/templates/labels/${template_stem}_labels.mnc
    gen_labels=$template/labels.mnc 

    temp_results_dir=$temp_dir/labels/$atlas_stem/$template_stem
    sim_results=$temp_results_dir/similarity.csv

    echo "volume_similarity --csv $template_labels $gen_labels | grep -v 0,0,0$ \
        | sed -e 's/$/,$template_stem,$atlas_stem/'
done | parallel -j8 > $output_root/multi_atlas_similarity.csv

