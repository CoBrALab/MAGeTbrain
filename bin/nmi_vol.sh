#!/bin/bash
# usage: <source> <target> <mask> <output_file>
mincsimilarity.py --nmi --src_mask $3 --tgt_mask $3 $1 $2 > $4
