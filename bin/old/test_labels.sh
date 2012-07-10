#!/bin/bash
mincinfo $1 >/dev/null 2>&1
if [ "$?" != "0" ]; then 
  echo $1; 
fi

