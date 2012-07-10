#!/usr/bin/env python

import glob
import csv
import os
import sys
import re

print "Opening results file..."
results_file = csv.writer(open("results.csv", "wb"))

# build headers
headers = ['subject']
labels = {1 : ('hippocampus', 'left'), 
          101 : ('hippocampus' , 'right'),
         }

validation_metrics = ['k', 'se', 'sp', 'j']
for structure in ['hippocampus']:
    headers.extend(["%s_%s" % (x, structure) for x in validation_metrics])
headers.append('hemisphere')
headers.append('method')
headers.append('top_n')
headers.append('num_atlases')
results_file.writerow(headers)

# collect data

def process_subjects(fusion_method_dir):
    print fusion_method_dir
    if "_atlases" in fusion_method_dir:
        num_atlases = re.search('(\d+)_atlases', fusion_method_dir).group(1)
    else: 
        num_atlases = 1
     
    for subject_dir in glob.glob(fusion_method_dir + "/*"):
        print "Processing subject", subject_dir
        subject_name = os.path.basename(subject_dir)
        
        for validation_csv in glob.glob(subject_dir +'/*validation.csv'):
            results = csv.reader(open(validation_csv))
                         
            data = []    
            for structure_results in results:
                data.append(structure_results)
            
            if not data:
                continue

            top_n = '0'
            # expect that we find left hippocampus and amygdala followed by right hippocampus and amygdala
            method = os.path.basename(fusion_method_dir)

            if method.startswith('majority_vote'):
		top_n  = num_atlases
                method = 'majority_vote'

            if method.startswith('xcorr'):
                top_n = method.split("_")[-1]
                method = 'xcorr'

            for structure_results in data:
                label = int(structure_results[0])
                if label in labels.keys(): 
                    results_file.writerow([subject_name] + structure_results[1:] + [labels[label][1], method, top_n, num_atlases])  

print "Collecting data..."


print "Fetching methods..."
fusion_method_dirs = glob.glob("output/fusion/*_atlases/subsample_*/*")
fusion_method_dirs.append('output/fusion/naive')
fusion_method_dirs.append('output/fusion/multiatlas')

for fusion_method_dir in fusion_method_dirs:
    print "Processing", fusion_method_dir
    if fusion_method_dir.endswith( "xcorr_vote") :
        xcorr_passes = glob.glob(fusion_method_dir + "/*")
        for sample in xcorr_passes:
            process_subjects(sample)
        continue
    process_subjects(fusion_method_dir)
