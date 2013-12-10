#!/bin/bash
#
# A hacky script to combine outputs from vote_tar_analyse into one, coherent CSV file 
#
# This script makes a number of assumptions, but you'll have to read the code
# to figure that bit out. Sorry.
#
(
echo "batch,file,label,k,se,sn,j"
for batch in {1..10}; do
  cat output/fusion_${batch}/*_similarity.csv | sed \
    -e "s#^#batch_${batch},#g" 
done
) > raw_sim.csv

(
echo batch,$(grep -h file output/fusion_*/*_volumes.csv | sort | uniq)
for batch in {1..10}; do
  cat output/fusion_${batch}/*_volumes.csv | \
    grep -v file | \
    sed -e "s#^#batch_${batch},#g" 
done
) > raw_vol.csv

R --no-save <<'RCODE'
library(reshape)
s = read.csv('raw_sim.csv')
v = read.csv('raw_vol.csv', check.names=FALSE) # allow numeric names

melted = melt(v, id.vars=c('batch','file'))
colnames(melted) = c('batch', 'file', 'label', 'volumes')
joined = merge(s, melted, by = c('batch', 'file', 'label'))

write.csv(joined, 'raw_joined.csv')
RCODE


(
echo "batch,timestamp,approach,method,atlases,templates,top_n,subject,label,k,se,sn,j,volume"
tail -n+2 raw_joined.csv | cut -f2- -d, | sed \
    -e 's#"##g' \
    -e 's#_templates/#_templates_0_topn/#g' \
    -e 's#/dev/shm/##g' \
    -e 's#/labels.mnc##g' \
    -e 's#_atlases_#/#g' \
    -e 's#_templates_#/#g' \
    -e 's#_topn/.*/#/#g' \
    -e 's#/#,#g' \
    -e 's#,multiatlas,#,ma,#g' 
) > results.csv

rm raw_vol.csv raw_sim.csv raw_joined.csv
