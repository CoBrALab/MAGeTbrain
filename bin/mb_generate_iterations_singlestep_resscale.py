#!/usr/bin/env python

from __future__ import division, print_function

import sys
import numpy as np

resscale = (1.0 / float(sys.argv[1]))

shrinks = []
blurs = []
iterations = []

# Based on intrinsic PSF of MRIs, FWHM of pixels are 1/1.2*res (sinc function)
# We assume the base blur resolution is this
s0 = 1 / (1.20670912432525704588 * resscale) * 1 / (2 * np.sqrt(2 * np.log(2)))

startscale = 16 * resscale

for scale in range(int(np.around(startscale)), 0, -1):
    shrinks.append(str(min(int(np.around(8*resscale)),scale)))
    blurs.append(str(np.sqrt((scale / 2)**2 - s0**2)))
    iterations.append(str(min(2025, int(np.around(30.0 * 3**(scale - 1))))))

shrinks.append("1")
blurs.append("0")
iterations.append("25")

print("--convergence [{},1e-6,10]".format("x".join(iterations)), end=' ')
print("--shrink-factors {}".format("x".join(shrinks)), end=' ')
print("--smoothing-sigmas {}vox".format("x".join(blurs)), end=' ')
