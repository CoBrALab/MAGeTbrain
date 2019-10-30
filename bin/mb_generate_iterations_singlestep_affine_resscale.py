#!/usr/bin/env python

# This file generates steps of affine registration between two images and attempts to compensate
# For ANTs' dependency on the resolution of the file

# We do this by defining two scales to step over
# blur_scale, which is the real-space steps in blurring we will do
# shrink_scale, which is the subsampling scale that is 1/2 the fwhm blur scale, adjusted for file minimum resolution

from __future__ import division, print_function

import sys
import numpy as np
import math

if len(sys.argv) == 2:
    resolution = float(sys.argv[1])
else:
    resolution = 1.0

shrinks = []
blurs = []
iterations = []
bins = []
fwhm_to_sigma = 2 * np.sqrt(2 * np.log(2))

blur_scale = 32
start_scale = blur_scale / 2 / resolution

for shrink_scale in range(int(np.ceil(start_scale)), 0, -1):
    shrinks.append(
        str(int(min(8.0 / resolution, max(1.0, np.around(shrink_scale))))))
    blurs.append(str(shrink_scale * 2 * resolution / fwhm_to_sigma))
    iterations.append(str(min(2025, int(100 * 3**(shrink_scale)))))
    bins.append(
        str(int(np.around((max(32, 256 / max(1, shrink_scale * resolution)))))))

shrinks.append("1")
blurs.append("0")
iterations.append("100")
bins.append(str(int(np.around((max(32, 256 / max(1, 1 * resolution)))))))

transforms = ["--transform Translation[ 0.5 ]",
              "--transform Rigid[ 0.5 ]",
              "--transform Similarity[ 0.25 ]",
              "--transform Similarity[ 0.125 ]",
              "--transform Affine[ 0.1 ]"]
masks = ["--masks [ NOMASK,NOMASK ]",
         "--masks [ NOMASK,NOMASK ]",
         "--masks [ NOMASK,NOMASK ]",
         "--masks [ ${fixedmask},${movingmask} ]",
         "--masks [ ${fixedmask},${movingmask} ]" ]

slicestart = 0
slicestartfloat = 0.0
slicesize = int(np.ceil(len(shrinks) / (len(transforms))))

for i,transform in enumerate(transforms):
    print(transform, end=' \\\n')
    if ( (slicestart + slicesize) > (len(shrinks) - 1)):
        print("\t--metric Mattes[ ${{target}},${{atlas}},1,{},None ]".format(bins[-1]), end=' \\\n')
        print("\t--convergence [ {},1e-6,10 ]".format("x".join(iterations[slicestart:])), end=' \\\n')
        print("\t--shrink-factors {}".format("x".join(shrinks[slicestart:])), end=' \\\n')
        print("\t--smoothing-sigmas {}mm".format("x".join(blurs[slicestart:])), end=' \\\n')
    else:
        print("\t--metric Mattes[ ${{target}},${{atlas}},1,{},None ]".format(bins[slicestart + slicesize]), end=' \\\n')
        print("\t--convergence [ {},1e-6,10 ]".format("x".join(iterations[slicestart:slicestart + slicesize])), end=' \\\n')
        print("\t--shrink-factors {}".format("x".join(shrinks[slicestart:slicestart + slicesize])), end=' \\\n')
        print("\t--smoothing-sigmas {}mm".format("x".join(blurs[slicestart:slicestart + slicesize])), end=' \\\n')
        slicestartfloat += (len(shrinks) / (len(transforms)))
        slicestart = int(np.ceil(slicestartfloat))
    print("\t" + masks[i], end=' \\\n')


print("--transform Affine[ 0.05 ] \\")
print("\t--metric Mattes[ ${{target}},${{atlas}},1,{},None ]".format(bins[-1]), end=' \\\n')
print("\t--convergence [ {},1e-7,10 ]".format("x".join(iterations[slicestart:])), end=' \\\n')
print("\t--shrink-factors {}".format("x".join(shrinks[slicestart:])), end=' \\\n')
print("\t--smoothing-sigmas {}mm".format("x".join(blurs[slicestart:])), end=' \\\n')
print("\t--masks [ ${fixedmaskfine},${movingmaskfine} ]")
