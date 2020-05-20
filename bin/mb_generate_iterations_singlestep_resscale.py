#!/usr/bin/env python

# This file generates steps of affine registration between two images and attempts to compensate
# For ANTs' dependency on the resolution of the file

# We do this by defining two scales to step over
# blur_scale, which is the real-space steps in blurring we will do
# shrink_scale, which is the subsampling scale that is 1/2 the fwhm blur scale, adjusted for file minimum resolution

from __future__ import division, print_function

import sys
import numpy as np

if len(sys.argv) == 2:
    resolution = float(sys.argv[1])
else:
    resolution = 1.0

shrinks = []
blurs = []
iterations = []
fwhm_to_sigma = 2 * np.sqrt(2 * np.log(2))

blur_scale = 32
start_scale = blur_scale / 2 / resolution

for shrink_scale in range(int(np.ceil(start_scale)), 0, -1):
    shrinks.append(
        str(int(min(8.0 / resolution, max(1.0, np.around(shrink_scale))))))
    blurs.append(str(shrink_scale * 2 * resolution / fwhm_to_sigma))
    iterations.append(str(min(2025, int(25 * 3**(shrink_scale)))))

shrinks.append("1")
blurs.append("0")
iterations.append("25")

print("--convergence [ {},1e-6,10 ]".format("x".join(iterations)), end=' ')
print("--shrink-factors {}".format("x".join(shrinks)), end=' ')
print("--smoothing-sigmas {}mm".format("x".join(blurs)), end=' ')
