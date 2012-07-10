#!/bin/bash
#PBS -l nodes=1:ppn=8,walltime=1:06:00:00
#$ -l vf=3G
#$ -N adni_validation
#$ -cwd
#$ -shell y
#$ -j y     # join the error streams
#$ -o logs  # stick the error streams in the log folder

if [ ! -z "$PBS_O_WORKDIR" ]; then
     cd $PBS_O_WORKDIR
fi

export PYD_HOME=$PWD/pydpiper
export PRJ_HOME=$PWD

export PATH=$PYD_HOME:$PYD_HOME/pydpiper:$PYD_HOME/applications/MAGeT_human:$PATH
export PYTHONPATH=$PYD_HOME:$PYD_HOME/applications/MAGeT_human:$PRJ_HOME/src:$PYTHONPATH


ARGS="--random-seed=1 \
      --num-validations=10 \
      --uri-file uri \
      --queue sge_script \
      --output-dir output  \
      $PRJ_HOME/input/brains/ \
      $PRJ_HOME/input/labels/ "

#      --restart \
# 	--queue sge_script \
#      --restart-failed \

cd $PRJ_HOME
echo Starting server
python -m cProfile -o profile.dat $PRJ_HOME/src/MAGeTValidation.py $ARGS  
