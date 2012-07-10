#!/bin/bash

if [ -z "$1" ]; then
  echo
  echo "$0 <task_list> <chunk_size> <walltime>"
  echo 
  echo     eg.  $0 jobs 50 03:00:00
  exit
fi

TASK_LIST=$1    # file with the list of tasks
CHUNK_SIZE=$2  
WALLTIME=$3
START_CHUNK=0  
task_list_size=$(cat $TASK_LIST | wc -l)
END_CHUNK=$(($task_list_size / $CHUNK_SIZE+1))

echo $END_CHUNK chunks to process. 

for chunk in `seq $START_CHUNK $END_CHUNK`; do
script_file=scripts/${TASK_LIST}_$chunk.sh
echo $script_file
(
echo "#!/bin/bash" 
echo "#PBS -l nodes=1:ppn=8,walltime=$WALLTIME" 

cat <<'EOF'
# -o logs    # stick the error streams in the log folder
# 

# set up our environment
#module load minc-tools/2012.01
#module load gnu-parallel

cd $PBS_O_WORKDIR
EOF

echo CHUNK_NUMBER=$chunk 
echo TASK_LIST=$TASK_LIST
echo TASKSPERJOB=$CHUNK_SIZE

cat <<'EOF'
PROCESSESPERNODE=8
STARTLINE=$(($CHUNK_NUMBER*$TASKSPERJOB+1))
NUMLINES=$(($TASKSPERJOB-1))

echo -------------------------------
echo sed -n -e "$STARTLINE,+${NUMLINES}p" $TASK_LIST
echo $* 
echo -------------------------------

sed -n -e "$STARTLINE,+${NUMLINES}p" $TASK_LIST  | parallel -j$PROCESSESPERNODE 
EOF
) > $script_file
chmod +x $script_file
done
