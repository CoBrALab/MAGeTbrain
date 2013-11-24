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
parser.add_argument("--mask", help="image mask")
parser.add_argument("source", help="source image")
parser.add_argument("target", help="target image")
arguments = parser.parse_args()

source = volumeFromFile(arguments.source, dtype='ubyte').data
target = volumeFromFile(arguments.target, dtype='ubyte').data

if arguments.mask:
    mask = volumeFromFile(arguments.mask, dtype='ubyte').data
    source = numpy.ma.array(source, mask=mask>0)
    source = source[~source.mask]
    target = numpy.ma.array(target, mask=mask>0)
    target = target[~target.mask]

if arguments.nmi:
    print normalized_mutual_info_score(source.flatten(), target.flatten())
