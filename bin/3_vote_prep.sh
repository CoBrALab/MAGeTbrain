#!/bin/bash
#
# Prepare for voting / validation by getting things ready to run on the cluster.
#
# This includes:
#  - TARing up the labels so that they can be moved to each node
#  - consolidating the similarity scores into single CSV files (to save space)
#
# 


output_dir=$PWD/output

echo "Consolidating scores..."
for scoretype in xcorr nmi; do 
    csv=$output_dir/$scoretype.csv
    find $output_dir/scores -name $scoretype.txt | \
        parallel 'echo -n "{}, "; cat {}' | \
        sed -e "s#$output_dir/scores/##g" -e "s#/$scoretype.txt##g" -e 's#/#, #g' > $csv
done

echo "TARing labels..."
cd $output_dir && tar czf labels.tar.gz labels/

echo "If the above completed without errors, you can now safely remove the folders:"
echo "    $output_dir/scores"
echo "    $output_dir/labels"
echo
