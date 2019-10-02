#!/usr/bin/env python

#This file generates steps of affine registration between two images and attempts to compensate
#For ANTs' dependency on the resolution of the file

#We do this by defining two scales to step over
#blur_scale, which is the real-space steps in blurring we will do
#shrink_scale, which is the subsampling scale that is 1/2 the fwhm blur scale, adjusted for file minimum resolution

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
bins = []
fwhm_to_sigma = 2*np.sqrt(2*np.log(2))

blur_scale = 32
start_scale = blur_scale / 2 / resolution

for shrink_scale in range(int(np.ceil(start_scale)), 0, -1):
    shrinks.append(str(int(min(8.0/resolution,max(1.0,np.around(shrink_scale))))))
    blurs.append(str(shrink_scale * 2 * resolution / fwhm_to_sigma))
    iterations.append(str(min(2025, int(250 * 3**(shrink_scale)))))
    bins.append(str(int(np.around((max(32, 256 / max(1, shrink_scale * resolution)))))))

shrinks.append("1")
blurs.append("0")
iterations.append("250")

transforms = ["--transform Translation[0.5]",
              "--transform Rigid[0.5]",
              "--transform Similarity[0.25]",
              "--transform Affine[0.125]"]
masks =      ["--masks [NOMASK,NOMASK]",
              "--masks [NOMASK,NOMASK]",
              "--masks [NOMASK,NOMASK]",
              "--masks [NOMASK,NOMASK]",]


slicestart = 0
slicesize = int(np.around(len(shrinks) / (len(transforms)) * 1.5))

for transform in transforms:
  print(transform, end=' \\\n')
  print("\t--metric Mattes[${{target}},${{atlas}},1,{},None]".format(bins[slicestart+slicesize]), end=' \\\n')
  print("\t--convergence [{},1e-6,10]".format("x".join(iterations[slicestart:slicestart+slicesize])), end=' \\\n')
  print("\t--shrink-factors {}".format("x".join(shrinks[slicestart:slicestart+slicesize])), end=' \\\n')
  print("\t--smoothing-sigmas {}mm".format("x".join(blurs[slicestart:slicestart+slicesize])), end=' \\\n')
  print("\t--masks [NOMASK,NOMASK]", end=' \\\n')    
  slicestart += int(np.around(slicesize / 2))

print("--transform Affine[0.1] \\")
print("\t--metric Mattes[${{target}},${{atlas}},1,{},None]".format(bins[-1]), end=' \\\n')
print("\t--convergence [{},1e-6,20]".format("x".join(iterations[len(shrinks)-5:])), end=' \\\n')
print("\t--shrink-factors {}".format("x".join(shrinks[len(shrinks)-5:])), end=' \\\n')
print("\t--smoothing-sigmas {}mm".format("x".join(blurs[len(shrinks)-5:])), end=' \\\n')
print("\t--masks [${fixedmask},${movingmask}]")
