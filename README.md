Multiple Automatically Generated Templates brain segmentation algorithm
=======

Given a set of labelled MR images (atlases) and unlabelled images (subjects),
MAGeT produces a set of labels using a multi-atlas voting procedure based on a
template library made up of images from the subject set. 

Quick start
-----------

0. Check out a copy of this repository somewhere handy. 

1. mkdir input logs 

2. Copy/link your atlases, templates, subjects into input/atlases,
   input/templates, and input/subjects, respectively.  As per always, MR images
   go in brains/ and corresponding labels go in labels/.  Labels should have
   the same name as the MR image but with a postfix of _labels.mnc

3. Run 
        bin/1_register.sh bin/ANTSregister_2_stage.sh 

    This will generate the file 1_register_jobs, which is a list of
    commands to carry out all the necessary registrations. You can submit these
    commands to a PBS system in batches using bin/qbatch, e.g. 
    
        qbatch 1_register_jobs 4 10:00:00

    (that is 4 tasks per job submitted, running for 10h in total).  You must be
    sure that the bin/ folder is in your path when you submit (or in your
    .bashrc)

4. After that stage is done, run bin/2* similarily.  Jobs in these stages can
   be run simultaneously.  Here is an example of how you might submit these
   jobs:

        qbatch 2a_template_labels_jobs 64 3:00:00  # assuming ~20m/8 tasks
        qbatch 2b_scoring_jobs 1 6:00:00           # assuming ~30 T1 subjects

   Note, if you are going to be using the default voting method, majority vote,
   you do not need to run 2b_scoring_jobs.

5. Next, run bin/3_vote_prep.sh and hope you get no errors.  If you do, you
   likely had failed jobs during the 2b_compute_scores stage (or chose not to
   run it). 

6. Lastly, label fusion.  bin/4_voting produces the jobs to do this.  You have
   a choice as to which fusion method you want to use: majority vote
   (--majvote), cross-correlation weighted (--xcorr <top_n>), or normalised
   mutual information weighted (--nmi <top n>).  Majority voting is the default
   voting method. See bin/vote.py --help for details.  

   Any options given to bin/4_vote get passed to vote.py.  A task is output for
   each subject.  Each task takes (wild guess) roughly 1h per subject (say 5min x
   # atlases x # templates + 15min x # voting methods), and is parallelised
   (--processes).  So, a safe way to submit these jobs might be: 

        qbatch 4_vote 1 3:00:00

   Voted labels appear in output/fusion/<voting_method>/

   Note: The --random_subsampling option enables, you guessed it, random
   subsampling of the current atlas and template libraries when voting. This
   can be used to profile or validate the performance of MAGeT on subject set
   with known labels. 

Tips
----

### PBS: Working with queued/running jobs

Manipulating the job queue is easily done with the help of qstat, qdel, qalter,
and a bit of command line magic.  Specifically, to get a list of job ids in the
queue, do this: 

        qstat | cut -f1 -d' '

You can extract only the queued jobs, like so:

        qstat | grep ' Q ' | cut -f1 -d' '

And then change the amount of time walltime allocated:
    
        qstat | grep ' Q ' | cut -f1 -d' ' | xargs qalter -l walltime=3:00:00 

Also consider the script qstatc which gives a short summary of the number of
jobs in the queue for each queue state. 
