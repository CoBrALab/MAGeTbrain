#!/bin/bash

# Set up file to run 5a_morpho.sh

mkdir output/objects

for file in input/subjects/brains/*; do
	echo 5a_morpho.sh $(basename $file .mnc)
done > submit_morpho_1
