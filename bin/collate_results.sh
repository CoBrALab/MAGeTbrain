#!/bin/bash
#
# A hacky script to combine outputs from vote_tar_analyse into one, coherent CSV file 
#
# This script makes a number of assumptions, but you'll have to read the code
# to figure that bit out. Sorry.
#
out=results.csv
(
echo "batch,timestamp,approach,method,atlases,templates,top_n,subject,label,k,se,sn,j"
for batch in {1..10}; do
  cat output/fusion_${batch}/*_similarity.csv | sed \
    -e "s#^#batch_${batch},#g" \
    -e 's#_templates/#_templates_0_topn/#g' \
    -e 's#/dev/shm/##g' \
    -e 's#/labels.mnc##g' \
    -e 's#_atlases_#/#g' \
    -e 's#_templates_#/#g' \
    -e 's#_topn/.*/#/#g' \
    -e 's#/#,#g' \
    -e 's#,multiatlas,#,ma,#g' 
done
) > $out

