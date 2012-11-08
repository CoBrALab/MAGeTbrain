#!/bin/env python
#
# Votes using a random sample of atlases and templates
# 
# Assumes that all registrations and template labels exist in their standard
# locations.
# 
from optparse import OptionParser
import re
import sys
import shutil
import logging
import os
import os.path
from os.path import join as joinp
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

def get_range(range):
    """Given a string like "5" or "5:10" convert this to a tuple that gives the range [start,finish)"""
    try:
        l = range.split(":")
        l = len(l) == 2 and l or [range, range]   
        return (int(l[0]), int(l[1])+1)
    except: 
        raise Exception("Improperly formated range '%s'" % range)
    
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

    # TODO: concatenate xfms and resample once (i.e. ditch the template labels). 
    template_labels  = os.path.join(labels_dir, atlas.stem, template.stem, 'labels.mnc')
    target_labels    = os.path.join(mkdirp(output_dir, atlas.stem, template.stem, target.stem), 'labels.mnc')
    nlxfm = os.path.join(registration_dir, template.stem, target.stem, 'nl.xfm')
    invert = inverse and '-invert' or ''

    cmd = "mincresample -2 -near -byte -keep -transform %s -like %s %s %s %s" % \
        (nlxfm, target.image, invert, template_labels, target_labels)
    return (target_labels, cmd)      
 
def parallel(commands, processors = 8, dry_run = False):
    "Runs the list of commands through parallel"
    command = 'parallel -j%i' % processors
    execute(command, input='\n'.join(commands), dry_run = dry_run)

def execute(command, input = "", dry_run = False):
    """Spins off a subprocess to run the cgiven command"""
    logger.debug("Running: " + command + " on:\n" + input)
   
    if not dry_run:  
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
        
def do_vote(voting_templates, target_vote_dir, temp_labels_dir):
    """Helper function for vote() """
    resample_cmds = []
    target_labels =  []
    for atlas in atlases:
        for template in voting_templates:
            labels, cmd = resample_labels(atlas, template, target, template_labels_dir, registrations_dir, temp_labels_dir, inverse=options.invert)
            resample_cmds.append(cmd)
            target_labels.append(labels)

    vote_cmd, labels = command("voxel_vote.py", target_vote_dir, "labels.mnc", target_labels)
    return (vote_cmd, resample_cmds)
    
   
def vote(target):
    """Generate the commands to vote on this target image.

       This "function" relies on lots of stuff being in module scope, specifically: 
        - atlases
        - templates
        - registrations_dir
        - fusion_dir
        - score_dir
        - options
        - logger
        - voting_cmds
        - resample_cmds

    """

    if options.majvote:
        target_vote_dir = mkdirp(fusion_dir, "majvote", target.stem)
        if not os.path.exists(joinp(target_vote_dir, 'labels.mnc')):
            vote_cmd, resamples = do_vote(templates, target_vote_dir, template_labels_dir)
            voting_cmds.append(vote_cmd)
            resample_cmds.extend(resamples)

    if options.xcorr:
        target_vote_dir = mkdirp(fusion_dir, "xcorr", target.stem)
        if not os.path.exists(joinp(target_vote_dir, 'labels.mnc')):
            top_n            = options.xcorr
            scores           = xcorr_scores
            sorted_templates = sorted(templates, key= lambda x:scores.get((x.stem,target.stem),0), reverse=True)
            vote_cmd, resamples = do_vote(sorted_templates[:top_n], target_vote_dir, template_labels_dir)
            voting_cmds.append(vote_cmd)
            resample_cmds.extend(resamples)

    if options.nmi:
        target_vote_dir = mkdirp(fusion_dir, "nmi", target.stem)
        if not os.path.exists(joinp(target_vote_dir, 'labels.mnc')):
            top_n            = options.nmi
            scores           = nmi_scores
            sorted_templates = sorted(templates, key= lambda x:scores.get((x.stem,target.stem),0), reverse=True)
            vote_cmd, resamples = do_vote(sorted_templates[:top_n], target_vote_dir, template_labels_dir)
            voting_cmds.append(vote_cmd)
            resample_cmds.extend(resamples)

if __name__ == "__main__":
    FORMAT = '%(asctime)-15s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    
    parser = OptionParser()
    parser.set_usage("%prog [options] [<target stem> ...]")        

    # Voting options
    parser.add_option("--majvote", dest="majvote",
        action="store_true", default=True,
        help="Do majority voting")
    parser.add_option("--xcorr", dest="xcorr",
        type="int", 
        help="Do XCORR voting with the top n number of templates.")
    parser.add_option("--nmi", dest="nmi",
        type="int", 
        help="Do NMI voting with the top n number of templates.")

    # In/out directory options
    parser.add_option("--atlas_dir", dest="atlas_dir",
        default="input/atlases", type="string", 
        help="Directory containing atlas brains and labels")
    parser.add_option("--template_dir", dest="template_dir",
        default="input/templates", type="string", 
        help="Directory containing template brains and labels")
    parser.add_option("--subject_dir", dest="subject_dir",
        default="input/subjects", type="string", 
        help="Directory containing subject brains and labels")
    parser.add_option("--registrations_dir", dest="registrations_dir",
        default=None, type="string", 
        help="Directory containing registrations from template library to subject.")
    parser.add_option("--output_dir", dest="output_dir",
        default="output", type="string", 
        help="Path to output folder")
    parser.add_option("--fusion_dir", dest="fusion_dir",
        default="output/fusion", type="string", 
        help="Directory containing label fusion results.")

    # Validation parameters
    parser.add_option("--num_atlases", dest="num_atlases",
        default=None,
        type="string", help="Number of atlases to randomly select.  Use lower:upper to specify a range.")
    parser.add_option("--num_templates", dest="num_templates",
        default=None, type="string", 
        help="Number of templates to randomly select. Use lower:upper to specify a range.")

    # Run state options
    parser.add_option("-n", dest="dry_run",
        default=False,
        action="store_true", 
        help="Short string to use to uniquely identify the results file (default: date & time)")
    parser.add_option("--invert", dest="invert",
        action="store_true", default=False,
        help="Invert the transformations during resampling from the template library.")
    parser.add_option("--processes", dest="processes",
        default=8, type="int", 
        help="Number of processes to parallelize over.")
    options, args = parser.parse_args()
    
    target_stems      = args[:]
    output_dir        = os.path.abspath(options.output_dir)
    registrations_dir = options.registrations_dir or os.path.join(output_dir, "registrations")
    base_fusion_dir   = mkdirp(options.fusion_dir)
    
    ## Set up TEMP space
    persistent_temp_dir   = tempfile.mkdtemp(dir='/dev/shm/')
    execute("tar xzf output/labels.tar.gz -C " + persistent_temp_dir, dry_run = options.dry_run)
    if options.xcorr > 0:
        xcorr_scores = read_scores(os.path.join(output_dir, "xcorr.csv"))
    if options.nmi > 0:
        nmi_scores = read_scores(os.path.join(output_dir, "nmi.csv"))
    template_labels_dir = mkdirp(persistent_temp_dir, "labels")    

    #
    # Select atlas and template library entries
    all_atlases   = get_templates(options.atlas_dir)
    all_templates = get_templates(options.template_dir)
    targets   = get_templates(options.subject_dir)
    random.shuffle(all_atlases)
    random.shuffle(all_templates)

    

    # Vote
    resample_cmds = []
    voting_cmds = []

    for num_atlases in range(*get_range(options.num_atlases)):
        for num_templates in range(*get_range(options.num_templates)):
            fusion_dir = mkdirp(base_fusion_dir, "%i_atlases_%i_templates" %(num_atlases, num_templates))
        
            atlases   = all_atlases[:num_atlases]
            templates = all_templates[:num_templates]

            # print state
            logger.debug("ATLASES:\n\t"+"\n\t".join([i.image for i in atlases]))
            logger.debug("TEMPLATES:\n\t"+"\n\t".join([i.image for i in templates]))
            logger.debug("-" * 40)

            for target in targets: 
                if not target_stems or target.stem in target_stems:
                    vote(target)   # global variables FTW

    resample_cmds = set(resample_cmds)
    voting_cmds   = set(voting_cmds) 

    logger.info("Running %i resamplings, %i voting comands", \
        len(resample_cmds), len(voting_cmds))

    logger.info("Resampling labels ...")
    parallel(set(resample_cmds), options.processes, options.dry_run)

    logger.info("Voting...")
    parallel(set(voting_cmds), options.processes, options.dry_run)

    logger.info("Cleaning up...")
    shutil.rmtree(persistent_temp_dir)
