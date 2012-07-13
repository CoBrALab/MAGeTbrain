#!/usr/bin/env python
#
# Computes a majority vote across input labels, but only selecting the top n labels by xcorrelation  
# 
# Depends on voxel_vote.py
#
from optparse import OptionParser
from subprocess import call
import re
DEFAULT_TOP_N = 15

if __name__ == "__main__":

    usage = """xcorr_vote.py [label1.mnc label2.mnc ...] [xcorr1.txt xcorr2.txt ...] output.mnc"""
    description = "Description text"
    
    parser = OptionParser(usage=usage, description=description)
    parser.add_option("--clobber", dest="clobber",
                      help="clobber output file",
                      type="string")
    parser.add_option("-n", dest="top_n",
                      default=DEFAULT_TOP_N, 
                      help="Top n input labels to use.",
                      type=int)

    (options, args) = parser.parse_args()
 

    num_labels = (len(args) - 1) / 2

    labels = args[:num_labels]
    xcorr_files = args[num_labels:-1]
    outfilename = args[-1]
    
    # read in the xcorr values
    xcorrs = [float(re.search("\d+\.\d+", open(i).read()).group(0)) for i in xcorr_files]
    sorted_labels = [x[0] for x in sorted(zip(labels, xcorrs), key= lambda x:x[1], reverse=True)]
    
  
    top_n = options.top_n
    
    cmd = ["voxel_vote.py"] + sorted_labels[:top_n] + [outfilename]
    call(cmd, shell=False)
         
    
    
    
