#!/bin/env python
from optparse import OptionParser
import re
import sys
import shutil
import logging
import os
import os.path
import glob
import subprocess
import errno
import random
import tempfile
import csv 

logger = logging.getLogger(__name__)

class Template:
    def __init__(self, image, labels = None):
        """Represents an MR image (labels, potentially)."""
        image_path      = os.path.realpath(image)
        self.stem       = os.path.basename(os.path.splitext(image_path)[0])
        self.image      = image
        self.labels = labels

        expected_labels = os.path.join(dirname(dirname(image_path)), 'labels', self.stem + "_labels.mnc")
        if not labels and os.path.exists(expected_labels):
            self.labels = expected_labels 

def read_scores(scoresfile):
    """Read the scores from the given file"""
    import csv
    scores = {}
    for row in csv.reader(open(scoresfile)):
        scores[(row[0].strip(),row[1].strip())] = float(row[2])
    return scores
     
def get_templates(path):
    """return a list of MR image Templates from the given path.  Expect to find
    a child folder named brains/ containing MR images, and labels/ containing
    corresponding labels."""
    return [Template(i) for i in glob.glob(os.path.join(path, 'brains', "*.mnc"))]

def dirname(path):
    return os.path.split(path)[0];
   
def resample_labels(atlas, template, target, labels_dir, registration_dir, output_dir, inverse = True):
    """Produces a command that resamples the labels from the atlas-template to target"""

    template_labels  = os.path.join(labels_dir, atlas.stem, template.stem, 'labels.mnc')
    target_labels    = os.path.join(mkdirp(output_dir, atlas.stem, template.stem, target.stem), 'labels.mnc')
    nlxfm = os.path.join(registration_dir, template.stem, target.stem, 'nl.xfm')
    invert = inverse and '-invert' or ''

    cmd = "mincresample -2 -near -byte -keep -transform %s -like %s %s %s %s" % \
        (nlxfm, target.image, invert, template_labels, target_labels)
    return (target_labels, cmd)      
 
def parallel(commands, processors = 8):
    "Runs the list of commands through parallel"
    command = 'parallel -j%i' % processors
    execute(command, input='\n'.join(commands))

def execute(command, input = ""):
    """Spins off a subprocess to run the cgiven command"""
    logger.debug("Running: " + command + " on:\n" + input)
    
    proc = subprocess.Popen(command.split(), 
                            stdin = subprocess.PIPE, stdout = 2, stderr = 2)
    proc.communicate(input)
    if proc.returncode != 0: 
        raise Exception("Returns %i :: %s" %( proc.returncode, command ))
    
def mkdirp(*p):
    """Like mkdir -p"""
    path = os.path.join(*p)
         
    try:
        os.makedirs(path)
    except OSError as exc: 
        if exc.errno == errno.EEXIST:
            pass
        else: raise
    return path

def command(command_name,  output_base, output, input_files = [], args = []):
    output_file = os.path.join(output_base, output)
    cmd = " ".join([command_name] + args + input_files + [output_file]) 
    return (cmd, output_file)

def compare_similarity(image_path, expected_labels_path, computed_labels_path, output_dir, validation):
    cmd, validation_output_file = command("volume_similarity.sh", output_dir, \
        "validation_v%i.csv" % validation, [expected_labels_path, computed_labels_path])
    return (validation_output_file, cmd)
        
def majority_vote(subject, labels, output_dir):
    cmd, voted_labels = command("vote_majority.py", output_dir, "labels.mnc", labels)
    return (voted_labels, cmd)

def weighted_vote(labels_dir, vote_dir, scores, target, templates, atlases, top_n):
        """Produces a command that does a weighted voting for the given target

           labels_dir - the directory containing the atlas/template/target/labels.mnc files
           score_dir  - the directory containing the template/target/<score>.txt files
           score_filename - the actually name of the score file (xcorr.txt, nmi.txt, etc..)
           target     - the target image (Template instance)
           atlases    - the atlases (as Template instances) to consider labels from 
           templates  - templates (as Template instances) to consider labels from
           top_n      - the number of templates to consider labels from when voting

           Returns the path to the voted on labels, along with the command to run.
        """

        # STEP 2: select the top_n templates, and all of the labels for them from the atlases
        labels_list = []
        sorted_templates = sorted(templates, key= lambda x:scores.get((x.stem,target.stem),0), reverse=True)
        for template in sorted_templates[:top_n]:
            labels_list.extend([os.path.join(labels_dir, atlas.stem, template.stem, target.stem, "labels.mnc") for atlas in atlases])
            
        # STEP 3: majority vote!
        cmd, weighted_voted_labels = command("vote_majority.py", vote_dir, "labels.mnc", labels_list)
        return (weighted_voted_labels, cmd)

def xcorr_vote(labels_dir, vote_dir, target, templates, atlases, top_n):
    return weighted_vote(labels_dir, vote_dir, xcorr_scores, target, templates, atlases, top_n)
    
def nmi_vote(labels_dir, vote_dir, target, templates, atlases, top_n):
    return weighted_vote(labels_dir, vote_dir, nmi_scores, target, templates, atlases, top_n)

def mk_dir(dirlist, *p):
    dir = os.path.join(*p)
    dirlist.append(dir)
    return dir

def consolidate_results_cmd(files, label_ids, output_file):
    return "grep '^%s,' %s > %s" % (',\|'.join(map(str,label_ids)), ' '.join(files), output_file)
   
def vote(target):
    """Generate the commands to vote on this target image.

       This "function" relies on lots of stuff being in module scope, specifically: 
        - atlases
        - templates
        - temp_labels_dir
        - registrations_dir
        - temp_labels_dir
        - fusion_dir
        - score_dir
        - options
        - logger
        - voting_cmds
        - resample_cmds

    """
    temp_dir   = tempfile.mkdtemp(dir='/dev/shm/')
    temp_labels_dir = mkdirp(temp_dir, "labels")    

    resample_cmds = []
    voting_cmds = []

    ####################################################
    # Resample labels
    #################################################### 
    target_labels = {}
    for atlas in atlases:
        l = []
        for template in templates:
            labels, cmd = resample_labels(atlas, template, target, template_labels_dir, registrations_dir, temp_labels_dir, inverse=False)
            resample_cmds.append(cmd)
            l.append(labels)
        target_labels[target] = l 
    
    ####################################################
    # VOTE 
    #################################################### 
    
    # majority voting fusion
    #################################################### 
    if options.majvote:
        target_vote_dir = mkdirp(fusion_dir, "majority_vote", target.stem)
        labels, vote_cmd = majority_vote(target.image, target_labels[target], target_vote_dir)
        voting_cmds.append(vote_cmd)

    if options.xcorr:
        top_n_templates = options.xcorr
        top_n_labels = top_n_templates * len(atlases)  # one label for each atlas per template
        logger.info("XCorr weighted voting with %i templates", top_n_templates)
        xcorr_dir = mkdirp(fusion_dir, "xcorr")
        xcorr_vote_dir = mkdirp(xcorr_dir, target.stem)
        
        xcorr_vote_labels, vote_cmd = xcorr_vote(temp_labels_dir, xcorr_vote_dir, target, templates, atlases, top_n_labels) 
        voting_cmds.append(vote_cmd)

    if options.nmi:
        top_n_templates = options.nmi
        top_n_labels = top_n_templates * len(atlases)  # one label for each atlas per template
        logger.info("NMI weighted voting with %i templates", top_n_templates)
        nmi_dir = mkdirp(fusion_dir, "nmi")
        nmi_vote_dir = mkdirp(nmi_dir, target.stem)

        nmi_vote_labels, vote_cmd = nmi_vote(temp_labels_dir, score_dir, nmi_vote_dir, target, templates, atlases, top_n_labels) 
        voting_cmds.append(vote_cmd)

    ####################################################
    # Run commands
    #################################################### 
    
    # sort the resampling commands to help with disk caching (maybe?)
    def extract_xfm(cmd):
        return re.search(r'\S*.xfm',cmd).group(0)
    resample_cmds = list(set(resample_cmds))
    resample_cmds.sort(lambda x,y: cmp(extract_xfm(x), extract_xfm(y))) 
    
    logger.info("Resampling labels ...")
    parallel(resample_cmds, options.processes)

    logger.info("Voting...")
    parallel(set(voting_cmds), options.processes)

    logger.info("Cleaning up...")
    shutil.rmtree(temp_dir)
    
if __name__ == "__main__":
    FORMAT = '%(asctime)-15s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    
    parser = OptionParser()
    parser.set_usage("%prog [options]")        
    parser.add_option("--majvote", dest="majvote",
        action="store_true", default=False,
        help="Do majority voting")
    parser.add_option("--xcorr", dest="xcorr",
        type="int", 
        help="Do XCORR voting with the top n number of templates.")
    parser.add_option("--nmi", dest="nmi",
        type="int", 
        help="Do NMI voting with the top n number of templates.")
    parser.add_option("--processes", dest="processes",
        default=8, type="int", 
        help="Number of processes to parallelize over.")
    parser.add_option("--output_dir", dest="output_dir",
        default="output", type="string", 
        help="Path to output folder")
    options, args = parser.parse_args()

    output_dir        = os.path.abspath(options.output_dir)
    registrations_dir = os.path.join(output_dir, "registrations")
    fusion_dir        = mkdirp(output_dir, "fusion")
    
    ## Set up TEMP space
    persistent_temp_dir   = tempfile.mkdtemp(dir='/dev/shm/')
    execute("tar xzf output/labels.tar.gz -C " + persistent_temp_dir)
    xcorr_scores = read_scores(os.path.join(output_dir, "xcorr.csv"))
    template_labels_dir = mkdirp(persistent_temp_dir, "labels")    
    score_dir = os.path.join(persistent_temp_dir, "scores") 

    # 
    atlases   = get_templates('input/atlases')
    templates = get_templates('input/templates')
    targets   = get_templates('input/subjects')

    # print state
    logger.debug("ATLASES:\n\t"+"\n\t".join([i.image for i in atlases]))
    logger.debug("TEMPLATES:\n\t"+"\n\t".join([i.image for i in templates]))
    logger.debug("-" * 40)

    for target in targets:
        logger.debug("Generating commands for target: " + target.image)
        vote(target)

    shutil.rmtree(persistent_temp_dir)
