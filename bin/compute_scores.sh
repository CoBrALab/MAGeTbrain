#!/bin/bash
#
# Computes the NMI and XCORR scores for each template given.
#
# Usage: template output_dir  
#
# For both we go about this same way: 
# 1. Create a generous mask around the label area for each template
# 2. Calculate the NMI/XCORR scores between the template and subject 
#
# Masks are computed by linearly registering the templates to the atlases,
# merging the resampled labels to get rough field for potential label targets,
# and expanding that masked area somewhat for good measure.
template=$1
output_root=$2

PROCESSORS=8

temp_dir=$(mktemp -d)
template_stem=$(basename $template .mnc)

shopt -s expand_aliases

# compute mask
for atlas in input/atlases/brains/*.mnc; do
  atlas_stem=$(basename $atlas .mnc)
  atlases_dir=$(dirname $(dirname $atlas))
  atlas_labels=$atlases_dir/labels/${atlas_stem}_labels.mnc

  xfm=$output_root/registrations/$atlas_stem/$template_stem/nl.xfm
  linxfm=$temp_dir/${atlas_stem}_lin.xfm
  linres=$temp_dir/${atlas_stem}_lin.mnc
  echo linxfm $xfm $linxfm "&&" mincresample -quiet -2 -like $template -transform $linxfm $atlas $linres
done | tee | parallel -j$PROCESSORS

avg=$temp_dir/avg.mnc 
mask_1=$temp_dir/mask_.mnc
mask=$temp_dir/mask.mnc

mincaverage $temp_dir/*_lin.mnc $avg
minccalc -expression 'A[0]>0' $avg $mask_1
mincmorph -successive DDD $mask_1 $mask

# calculate scores over that mask
for subject in input/subjects/brains/*.mnc; do
  subject_stem=$(basename $subject .mnc)

  score_root_dir=$output_root/scores/$template_stem/$subject_stem
  mkdir -p $score_root_dir

  xfm=$output_root/registrations/$template_stem/$subject_stem/nl.xfm
  linxfm=$temp_dir/${subject_stem}_invlin.xfm
  linres=$temp_dir/${subject_stem}_invlin.mnc

  # only do this next stem if we need to, and have the transform
  if [ -e $score_root_dir/xcorr.txt -o ! -e $xfm ]; then
    continue;
  fi

  script=$(mktemp --tmpdir=$temp_dir)
 
  cat <<EOF > $script
#!/bin/bash
linxfm $xfm $linxfm  
mincresample -2 -like $template -invert -transform $linxfm $subject $linres
xcorr_vol.sh $linres $template $mask $score_root_dir/xcorr.txt 
#nmi_vol.sh $linres $template $mask $score_root_dir/nmi.txt
rm $linxfm $linres $script
EOF
  chmod +x $script
  echo $script
done | tee | parallel -j$PROCESSORS

rm -rf $temp_dir
