import glob
import os
from subprocess import call

output_dir = os.path.abspath("output/fusion/multiatlas")
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

script_file = "multiatlas_segmentation.sh"
script = file(script_file, "w")

for template in glob.glob('input/brains/*.mnc'):
    template_name = os.path.basename(template).replace(".mnc", "")
    template_labels = 'input/labels/%s_labels.mnc' % template_name
    
    # collect candidate labels
    candidate_labels = glob.glob('output/labels/*/%s/labels.mnc' % template_name)

    # output results
    results_dir = output_dir + "/" + template_name
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)
    
    
    # majority vote
    voted_labels = results_dir + "/labels.mnc"
    cmd = ["voxel_vote.py"] + candidate_labels + [voted_labels]
    script.write(" ".join(cmd) + '\n') 
    
    # generate results
    validation_results = results_dir + "/validation.csv"
    cmd = ["volume_similarity.sh", template_labels, voted_labels, validation_results]
    script.write(" ".join(cmd) + '\n')

print "script written to ", script_file 
