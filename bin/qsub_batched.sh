#!/bin/bash
#
# Takes a "task list" of commands to run, and divides them up into separate
# scripts and submits them.

if [ -z "$1" ]; then
  echo
  echo "$0 [-n] <task_list> <chunk_size> <walltime> <qsub options>"
  echo 
  echo     eg.  $0 jobs 50 03:00:00
  echo
  echo     -n  no execution.  just print what would happen
  exit
fi

if [ "$1" = "-n" ]; then
    NOP=TRUE
    shift;
fi

TASK_LIST=$1    # file with the list of tasks
CHUNK_SIZE=$2  
WALLTIME=$3
shift; shift; shift;

START_CHUNK=0  
task_list_size=$(cat $TASK_LIST | wc -l)
END_CHUNK=$(($task_list_size / $CHUNK_SIZE+1))

echo $END_CHUNK chunks to process. 

mkdir -p .scripts
for chunk in `seq $START_CHUNK $END_CHUNK`; do
    script_file=.scripts/${TASK_LIST}_$chunk.sh
    (
    echo "#!/bin/bash" 
    echo "#PBS -l nodes=1:ppn=8,walltime=$WALLTIME" 
    echo "#PBS -d $PWD"
    echo "#PBS -j oe"
    echo "#PBS -o logs"
    echo "#PBS -V"
    echo "cd $PBS_O_WORKDIR"

    STARTLINE=$(($chunk*$CHUNK_SIZE+1))
    NUMLINES=$(($CHUNK_SIZE-1))

    echo "parallel -j8 << TASKS"
    sed -n -e "$STARTLINE,+${NUMLINES}p" $TASK_LIST
    echo TASKS 

    ) > $script_file
    chmod +x $script_file

    echo qsub $@ $script_file
    if [ -z "$NOP" ]; then
        echo calling qsub $@ $script_file
    fi
done
