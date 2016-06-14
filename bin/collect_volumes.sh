#!/bin/bash
# Script to collect volumes in parallel, and use names from a csv if available, see https://github.com/CobraLab/atlases for csv examples
# CSV Format
# 1,name
# 2,name
# etc

set -euo pipefail
IFS=$'\n\t'

firstarg=${1:-}
if ! [[  ( $firstarg = *csv ) ||  ( $firstarg = *mnc )  ]]; then
    echo "usage: $0 [ label-mapping.csv ] input.mnc [ input2.mnc ... inputN.mnc ]"
    exit 1
fi


AWKCMD='BEGIN{FS=","}

{for(i=1;i<=NF;i++)a[NR,i]=$i}
END{
  for(i=1;i<=NF;i++){
    for(j=1;j<=NR;j++){
      line=line sep a[j,i]
      sep=FS
    }
    print line
    line=sep=""
  }
}
'


if [[ "$1" == *csv ]]
then
    LABELFILE=$1
    shift
    { echo "Subject"; cut -d "," -f 2 $LABELFILE; } | awk -f<(echo "$AWKCMD")
    for file in "$@"
    do
        sem -j+0 "itk_label_stats --labels $LABELFILE $file | tail -n +2 | cut -f2 -d"," | { echo -n "$file,"; awk -f<(echo '$AWKCMD') ; }"
    done
    sem --wait
else
    { echo -n "Subject,"; itk_label_stats $1; } | cut -f1 -d"," | awk -f<(echo "$AWKCMD")
    for file in "$@"
    do
        sem -j+0 "itk_label_stats $file | tail -n +2 | cut -f2 -d"," | { echo -n "$file,"; awk -f<(echo '$AWKCMD') ; }"
    done
    sem --wait
fi
