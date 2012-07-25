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

3. Run bin/1_register.sh bin/ANTSregister_2_stage.sh output

    This will generate the file 1_register_jobs, which is a list of
    commands to carry out all the necessary registrations. You can submit these
    commands to a PBS system in batches using bin/qsub_batched.sh, e.g. 
    
        qsub_batched 1_register_jobs 4 10:00:00

    (that is 4 tasks per job submitted, running for 10h in total).  You must be
    sure that the bin/ folder is in your path when you submit (or in your
    .bashrc)

4. After that stage is done, run bin/2* similarily.  Jobs in these stages can
   be run simultaneously.

5. Next, run bin/3_vote_prep.sh and hope you get no errors.  If you do, you
   likely had failed jobs during the 2b_compute_scores stage.  

6. Lastly, you will want to run (or submit a job to run) all of the voting,
   e.g.:

        bin/vote.py -xcorr 15 

   This produces voted labels using the cross-correlation similarity metric to
   choose the top 15 templates to vote from for each subject.  There are other
   options for various voting regimes.

   This stage takes (wild guess) roughly 30m - 1h per subject.  Voted labels
   appear in output/fusion/<voting_method>/
