#!/bin/bash

mkdir -p output/final

for dir in output/objects/*; do
	mkdir -p output/final/$(basename $dir)
	for file in ${dir}/*; do
		subject=$(basename $file .obj)
		object=$(basename $dir)
		echo morpho_2.sh $subject $object
	done
done > submit_morpho_2 
