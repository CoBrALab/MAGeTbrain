#!/usr/bin/env python
import logging
FORMAT = '%(asctime)-15s %(name)s %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)

logger.debug("Starting imports...")
import subprocess
from pyminc.volumes.factory import *
from numpy import *
from optparse import OptionParser

logger.debug("Done imports.  Starting program")

def execute(command, input = ""):
    """Spins off a subprocess to run the cgiven command"""
    logger.debug("Running: " + command + " on:\n" + input)
    
    proc = subprocess.Popen(command.split(), 
                            stdin = subprocess.PIPE, stdout = 2, stderr = 2)
    proc.communicate(input)
    if proc.returncode != 0: 
        raise Exception("Returns %i :: %s" %( proc.returncode, command ))

# stolen from scipy.stats
def mode(a, axis=0):
    scores = unique(ravel(a))       # get ALL unique values
    testshape = list(a.shape)
    testshape[axis] = 1
    oldmostfreq = zeros(testshape)
    oldcounts = zeros(testshape)

    for score in scores:
        template = (a == score)
        counts = expand_dims(sum(template, axis),axis)
        mostfrequent = where(counts > oldcounts, score, oldmostfreq)
        oldcounts = maximum(counts, oldcounts)
        oldmostfreq = mostfrequent

    return mostfrequent, oldcounts

if __name__ == "__main__":

    usage = "Usage text"
    description = "Description text"
    
    parser = OptionParser(usage=usage, description=description)
    parser.add_option("--clobber", dest="clobber",
                      help="clobber output file",
                      type="string")

    logger.debug("parsing arguments.")
    (options, args) = parser.parse_args()
    
    if len(args) < 3:
        parser.error("Incorrect number of arguments")

    outfilename = args[-1]
    
    
    # clobber check should go here
    
    volhandles = []

    logger.debug("loading input volumes....")
    nfiles = len(args)-1
    for i in range( nfiles ):
        volhandles.append(volumeFromFile(args[i], dtype='ubyte'))
    logger.debug("loading input volumes complete.")

    outfile = volumeFromInstance(volhandles[0], outfilename)
#    outdist = volumeFromInstance(volhandles[0], outfiledist)

    sliceArray = zeros( (nfiles,
                         volhandles[0].sizes[1],
                         volhandles[0].sizes[2]))
                         
    logger.debug("computing slice votes...")
    for i in range(volhandles[0].sizes[0]):
        for j in range(nfiles):
            t = volhandles[j].getHyperslab((i,0,0),
                                           (1,volhandles[0].sizes[1],
                                            volhandles[0].sizes[2]))
            t.shape = (volhandles[0].sizes[1], volhandles[0].sizes[2])
            sliceArray[j::] = t
            
        outfile.data[i::] = mode(sliceArray)[0]
        #outdist.data[i::] = mode(sliceArray)[1]/nfiles

    logger.debug("writing output file...")
    outfile.writeFile()
    outfile.closeVolume()
    
    execute('mv %s %s.v1' % (outfilename, outfilename))
    execute('mincconvert -2 -clob -compress 9 %s.v1 %s' % (outfilename, outfilename))
    execute('rm %s.v1' % outfilename)

    logger.debug("writing output file complete.")
    #outdist.writeFile()
    # outdist.closeVolume()

                                                          
    
