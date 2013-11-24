#!/bin/bash
# usage: <source> <target> <mask> <output_file>
mincsimilarity.py --nmi --mask $3 $1 $2 > $4
