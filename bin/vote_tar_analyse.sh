#!/bin/bash
# Analyse a tarfile full of labels output from vote.py for a single subject 
# 
# See 5_analyse for more info.
#
tarfile=$1
gold_standard_labels=$2

outdir=$(dirname $tarfile)
bn=$(basename $tarfile .tar)
volume_out=$outdir/${bn}_volumes.csv
similarity_out=$outdir/${bn}_similarity.csv

tmpdir=/dev/shm
tar_root=$tmpdir/$bn
tar -C $tmpdir -xf $tarfile 
find $tar_root -name '*.mnc' | label_vols > $volume_out
find $tar_root -name '*.mnc' | while read i; do 
    volume_similarity --csv $gold_standard_labels $i | \
        grep -v '0,0,0,0$' | sed -e "s#^#$i,#g" 
    done > $similarity_out
rm -rf $tar_root
