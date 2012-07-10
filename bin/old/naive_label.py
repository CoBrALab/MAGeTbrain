import glob
import os
from subprocess import call

output_dir = os.path.abspath("output/fusion/naive")
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

script = file("naive_label.sh", "w")

for template in glob.glob('input/brains/*.mnc'):
    template_name = os.path.basename(template).replace(".mnc", "")
    template_labels = 'input/labels/%s_labels.mnc' % template_name
    
    # collect template library labels
    template_library_labels = glob.glob('output/labels/*/%s/labels.mnc' % template_name)

    results_dir = output_dir + "/" + template_name
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)
   
    for labels in template_library_labels:
        atlas = labels.split("/")[2]
        validation_results = results_dir + "/%s_validation.csv" % atlas
        cmd = ["volume_similarity.sh", template_labels, labels, validation_results]
        script.write(" ".join(cmd) + '\n')

    
    
    
