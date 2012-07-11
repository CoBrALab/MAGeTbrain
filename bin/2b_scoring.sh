#!/bin/bash
#
# Calculate the various weighting measures between subjects and templates
# 
# Usage: <output_dir>
#

output_dir=$1
for template in input/templates/brains/*.mnc; do
  echo $PWD/bin/compute_scores.sh $template $output_dir
done > 2b_scoring_jobs
