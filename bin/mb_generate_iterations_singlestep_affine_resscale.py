#!/usr/bin/env python

from __future__ import division, print_function

import sys
import numpy as np

resscale = (1.0 / float(sys.argv[1]))

shrinks = []
blurs = []
iterations = []
bins = []

# Based on intrinsic PSF of MRIs, FWHM of pixels are 1/1.2*res (sinc function)
# We assume the base blur resolution is this
s0 = 1 / (1.20670912432525704588 * resscale) * 1 / (2 * np.sqrt(2 * np.log(2)))

startscale = 16 * resscale

for scale in range(int(np.around(startscale)), 0, -1):
    shrinks.append(str(min(int(8*resscale),scale)))
    blurs.append(str(np.sqrt((scale / 2)**2 - s0**2)))
    iterations.append(str(min(2025, int(25.0 * 3**(scale - 1)))))
    bins.append(str(int(np.around((max(32, 256 / max(1, scale/resscale)))))))

shrinks.append("1")
blurs.append("0")
iterations.append("25")

transforms = ["--transform Rigid[0.1]",
              "--transform Similarity[0.1]",
              "--transform Similarity[0.1]",
              "--transform Affine[0.1]",
              "--transform Affine[0.05]"]
masks =      ["--masks [NULL,NULL]",
              "--masks [NULL,NULL]",
              "--masks [${fixedmask},${movingmask}]",
              "--masks [${fixedmask},${movingmask}]",
              "--masks [${fixedmask},${movingmask}]"]

slicesize = int(np.around(len(shrinks) / (len(transforms) - 1)))
slicestart = 0

for start in range(0, len(transforms), 1):
    if ((slicestart + slicesize + 1) > len(bins)) or (start == len(transforms) - 1):
        print(transforms[start], end=' \\\n')
        print("\t--metric Mattes[${{target}},${{atlas}},1,{},None]".format(bins[-1]), end=' \\\n')
        print("\t--convergence [{},1e-6,10]".format("x".join(iterations[slicestart:])), end=' \\\n')
        print("\t--shrink-factors {}".format("x".join(shrinks[slicestart:])), end=' \\\n')
        print("\t--smoothing-sigmas {}vox".format("x".join(blurs[slicestart:])), end=' \\\n')
        print("\t"+masks[start], end=' ')
    else:
        print(transforms[start], end=' \\\n')
        print("\t--metric Mattes[${{target}},${{atlas}},1,{},None]".format(bins[slicestart+slicesize]), end=' \\\n')
        print("\t--convergence [{},1e-6,10]".format("x".join(iterations[slicestart:slicestart+slicesize])), end=' \\\n')
        print("\t--shrink-factors {}".format("x".join(shrinks[slicestart:slicestart+slicesize])), end=' \\\n')
        print("\t--smoothing-sigmas {}vox".format("x".join(blurs[slicestart:slicestart+slicesize])), end=' \\\n')
        print("\t"+masks[start], end=' \\\n')
    slicestart = int(np.around(slicestart + slicesize*0.75))
