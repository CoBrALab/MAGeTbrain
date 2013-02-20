# Multiple Automatically Generated Templates brain segmentation algorithm

Given a set of labelled MR images (atlases) and unlabelled images (subjects),
MAGeT produces a set of labels using a multi-atlas voting procedure based on a
template library made up of images from the subject set. 

## For the impatient (Really quick start) 

    git clone http://pipitone.github.com/MAGeTbrain
    cd MAGeTbrain
    export PATH=$PWD/bin:$PATH
    mkdir -p input/{atlases,subjects,templates}/{brains,labels} logs
    # 
    # put MR images in /brains folders, labels in /labels
    #
    bin/1_register.sh ANTSregister_2_stage.sh 
    qbatch 1_register_jobs 4 10:00:00
    #
    # wait for these to complete. 
    #
    4_vote --majvote --do_subject_registrations ANTSregister.sh 
    qbatch 4_vote 1 10:00:00 
    #
    # check output/fusion/majvote for labels
    # re-run any stage to generate commands for missing steps

## Quick start

0. Check out a copy of this repository somewhere handy,
    
        git clone  git://github.com/pipitone/MAGeTbrain.git 

1. Add the `bin` folder to your path. Create a new folder for your project and, 

        mkdir input/{atlases,subjects,templates}/brains logs 

2. Copy/link your atlases, templates, subjects into `input/atlases`,
   `input/templates`, and `input/subjects`, respectively.  As per always, MR
   images go in `brains` and corresponding labels go in `labels`.  Labels should
   have the same name as the MR image but with a postfix of `_labels.mnc`.

3. Registrations. Run,

        bin/1_register.sh bin/ANTSregister_2_stage.sh 

    This will generate the file `1_register_jobs`, which is a list of
    commands to carry out all the necessary registrations. You can submit these
    commands to a PBS system in batches using `qbatch`, e.g. 
    
        qbatch 1_register_jobs 4 10:00:00

    (that is 4 tasks per job submitted, running for 10h in total).  You must be
    sure that the `MAGeTbrain/bin/` folder is in your path when you submit.

4. Voting.  `4_voting` produces the tasks to do this by emitting calls to
   `vote.py` for each subject.  You have a choice as to which fusion method you
   want to use: majority vote (`--majvote`), cross-correlation weighted
   (`--xcorr <top_n>`), or normalised mutual information weighted (`--nmi <top
   n>`).  Majority voting is the default voting method; to use one of weighted
   voting methods you'll need to first compute similarity scores (see
   `2b_scoring.sh` and `3_vote_prep.sh` for details on how to do this).   

   Any options given to `4_vote` get passed to `vote.py`. See `vote.py --help`
   for details on the various options. Following the example so far, run:  

        4_vote --majvote --do_subject_registrations ANTSregister.sh 

   The script passed to `--do_subject_registrations` will be used to register
   each template library image to each subject before doing label propagation
   and voting.  The transformations produced here are kept in temporary space
   (`/dev/shm`) so be sure you have enough of that, and because each job does a
   pile of registrations, you will need to allocate a fair chunk of time per
   job...  for example, with 1x1x1mm 1.5T human brain images, a template library
   of 20 images, and an 8 core machine (like on SciNet), give yourself around
   6-7 hours at least. 
   
        qbatch 4_vote 1 6:00:00
   
   Voted labels appear in `output/fusion/<voting_method>`

   Note: The `--random_subsampling` option causes the atlas and template
   libraries to be randomly subsampled from the atlas and template library
   folders. This can be used to profile or validate the performance of MAGeT on
   subject set with known labels. 

## Tips

### PBS: Working with queued/running jobs

Manipulating the job queue is easily done with the help of qstat, qdel, qalter,
and a bit of command line magic.  Specifically, to get a list of job ids in the
queue, do this: 

        qstat | cut -f1 -d' '

You can extract only the queued jobs, like so:

        qstat | grep ' Q ' | cut -f1 -d' '

And then change the amount of time walltime allocated:
    
        qstat | grep ' Q ' | cut -f1 -d' ' | xargs qalter -l walltime=3:00:00 

Also consider the script `qstatc` which gives a short summary of the number of
jobs in the queue for each queue state. 

---
    http://tinysong.com/y9lO
