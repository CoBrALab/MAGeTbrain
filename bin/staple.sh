#!/bin/bash
#
# Computes  
#

function usage() {

cat <<EOF
        
Usage:
        staple.sh <label.mnc> [<label.mnc> ...] <target_image.mnc> <fused_label.mnc>

EOF
}

until [ $# -le 2 ]
do          #      Step through positional parameters.
  labels="$labels $1"
  shift;
done

target_image=$1
fused_labels=$2

if [ -z "$labels" ]; then
        echo "Error: no label files given."
        usage;
        exit;
fi

if [ -e $fused_labels ]; then
	echo "Label file $fused_labels exists. Exiting."
	exit;
fi

weights=/tmp/${RANDOM}.nii
echo crlSTAPLE -o $weights $labels
crlSTAPLE -o $weights $labels


fusednii=/tmp/${RANDOM}.nii
echo crlIndexOfMaxComponent $weights $fusednii
crlIndexOfMaxComponent $weights $fusednii

rawmnc=/tmp/${RANDOM}.mnc
echo nii2mnc $fusednii $rawmnc
nii2mnc $fusednii $rawmnc

echo mincresample -like $target_image $rawmnc $fused_label
mincresample -like $target_image $rawmnc $fused_label
