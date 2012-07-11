b2a
===

Awesome Brain to ADNI MAGeT Validation

Quick start
-----------

1. Copy/link your atlases/templates/subjects into input/atlases,
   input/templates, and input/subjects.  As per always, MR images go in brains/
   and corresponding labels go in labels/.  Labels should have the same name as
   the MR image but with a postfix of _labels.mnc

2. Run bin/1_registrations.sh bin/register_2_stage.sh output

    This will generate the file 1_registrations_jobs, which is a list of
    commands to carry out all the necessary registrations. You can submit these
    commands in batches using bin/qsub_batched.sh, e.g. 
    
        qsub_batched 1_registrations_jobs 4 10:00:00

    (that is 4 tasks per job submitted, running for 10h in total) 

3. After that stage is done, run bin/2* similarily. 

4. Similarily, run bin/3*, then bin/4* and so on.
