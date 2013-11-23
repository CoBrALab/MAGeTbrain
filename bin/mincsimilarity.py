#!/usr/bin/env python
import argparse
import numpy.ma
from pyminc.volumes.factory import *
from sklearn.metrics.cluster import normalized_mutual_info_score

class DefaultHelpParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

parser = DefaultHelpParser()
parser.add_argument("--nmi", default=False, action='store_true',
        help="Normalized mutual information")
parser.add_argument("--src_mask", help="source image mask")
parser.add_argument("--tgt_mask", help="target image mask")
parser.add_argument("source", help="source image")
parser.add_argument("target", help="target image")
arguments = parser.parse_args()

source = volumeFromFile(arguments.source, dtype='ubyte').data
target = volumeFromFile(arguments.target, dtype='ubyte').data

if arguments.src_mask:
    src_mask = volumeFromFile(arguments.src_mask, dtype='ubyte').data
    source = numpy.ma.array(source, mask=src_mask>0)
    source = source[~source.mask]

if arguments.tgt_mask:
    tgt_mask = volumeFromFile(arguments.tgt_mask, dtype='ubyte').data
    target = numpy.ma.array(target, mask=tgt_mask>0)
    target = target[~target.mask]

if arguments.nmi:
    print normalized_mutual_info_score(source.flatten(), target.flatten())
