#!/bin/bash
# usage: <source> <target> <mask> <output_file>
itk_similarity --nmi --src_mask $3 --target_mask $3 $1 $2 > $4
