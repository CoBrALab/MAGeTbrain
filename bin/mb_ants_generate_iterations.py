#!/usr/bin/env python

# This file generates steps of registration between two images and attempts to compensate
# For ANTs' dependency on the resolution of the file

# We do this by defining two scales to step over
# blur_scale, which is the real-space steps in blurring we will do
# shrink_scale, which is the subsampling scale that is 1/2 the fwhm blur scale, adjusted for file minimum resolution and max size

from __future__ import division, print_function

import argparse
import math
import sys

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)


parser.add_argument(
    '--min', help='minimum resolution of fixed file (mm)', type=float, required=True)
parser.add_argument(
    '--max', help='max size of fixed file (mm)', type=float, required=True)
parser.add_argument(
    '--start-scale', help='set starting scale (mm), default calculated from max size', type=float)
parser.add_argument(
    '--final-iterations', help='total number of iterations at lowest scale', type=int, default=25)
parser.add_argument(
    '--output', help='type of output to generate', default='generic',
      choices=['generic', 'affine', 'modelbuild', 'twolevel_dbm', 'multilevel-halving', 'exhaustive-affine',
                'lsq6', 'lsq9', 'lsq12', 'rigid', 'similarity'])
parser.add_argument('--step-size', help='step mode for generation', default=1)
parser.add_argument(
    '--convergence', help='set convergence for generated stages', default='1e-6')
parser.add_argument(
    '--close', help='images are already close, skip large scales of pyramid for affine', action='store_true')
parser.add_argument('--reg-pairs', help='number of pairs of input scans for affine output', default=1, type=int)

args = parser.parse_args()

# Setup inital inputs
min_resolution = args.min
max_size = args.max

if RepresentsInt(args.step_size):
    step_size = int(args.step_size)
elif args.step_size == "power2":
    step_size = args.step_size
else:
    sys.exit("Unrecognized step size")

# Make empty arrays
shrinks = []
blurs = []
iterations = []

if args.output == "affine" or args.output == "multilevel-halving" and args.final_iterations == 25:
  args.final_iterations = 50

# Converter
fwhm_to_sigma = 2 * math.sqrt(2 * math.log(2))

# Inital resolution scaling
if args.start_scale:
  start_shrink = args.start_scale / min_resolution
else:
  start_shrink = max_size / 28 / min_resolution * 2

max_shrink = max_size / min_resolution / 32

if isinstance(step_size, int):
    for shrink_scale in range(int(round(start_shrink)), 0, -1 * step_size):
        shrinks.append(
            str(int(min(max_shrink , max(1.0, round(shrink_scale))))))
        blurs.append(str(math.sqrt(((shrink_scale*min_resolution)**2.0 - min_resolution**2.0)/(2.0*math.sqrt(2*math.log(2.0)))**2)))
        iterations.append(str(min(500, int(args.final_iterations * 3**(max(0,shrink_scale - 1))))))
else:
    blur_scale = start_shrink * 2 * min_resolution
    shrink_scale = start_shrink
    while (blur_scale > 0.5 * min_resolution):
        shrinks.append(
            str(int(min(max_size / 32 / min_resolution, max(1.0, round(shrink_scale))))))
        blurs.append(str(blur_scale / fwhm_to_sigma))
        iterations.append(str(min(500, int(args.final_iterations * 3**(max(0,shrink_scale-1))))))
        blur_scale = blur_scale / 2
        shrink_scale = shrink_scale / 2

if args.output == 'exhaustive-affine':
    transforms = ["--transform Translation[ ",
                  "--transform Rigid[ ",
                  "--transform Similarity[ ",
                  "--transform Affine[ "]
    gradient_steps = [ 0.5, 0.33437015, 0.2236068, 0.1 ]
    gradient_steps_repeat = [ 0.5, 0.33437015, 0.14953488, 0.1 ]
    masks = ["--masks [ NOMASK,NOMASK ]",
             "--masks [ NOMASK,NOMASK ]",
             "--masks [ NOMASK,NOMASK ]",
             "--masks [ ${fixedmask},${movingmask} ]" ]
    repeatmask = [ False,
                   False,
                   "--masks [ ${fixedmask},${movingmask} ]",
                   False ]

    for i, transform in enumerate(transforms):
        if args.close and i < 2:
            pass
        else:
            if i == len(transforms) - 1:
              print(transform + str(gradient_steps[i]) + " ]", end=' \\\n')
              for j in range(1, args.reg_pairs+1):
                  print("\t--metric Mattes[ ${{fixedfile{j}}},${{movingfile{j}}},1,32,None ]".format(j=""), end=' \\\n')
              print("\t--convergence [ {},{},10 ]".format("x".join(iterations), args.convergence), end=' \\\n')
              print("\t--shrink-factors {}".format("x".join(shrinks)), end=' \\\n')
              print("\t--smoothing-sigmas {}mm".format("x".join(blurs)), end=' \\\n')
              print("\t" + masks[i], end=' ')
            else:
              print(transform + str(gradient_steps[i]) + " ]", end=' \\\n')
              for j in range(1, args.reg_pairs+1):
                  print("\t--metric Mattes[ ${{fixedfile{j}}},${{movingfile{j}}},1,32,None ]".format(j=""), end=' \\\n')
              print("\t--convergence [ {},{},10 ]".format("x".join(iterations), args.convergence), end=' \\\n')
              print("\t--shrink-factors {}".format("x".join(shrinks)), end=' \\\n')
              print("\t--smoothing-sigmas {}mm".format("x".join(blurs)), end=' \\\n')
              print("\t" + masks[i], end=' \\\n')
              if repeatmask[i]:
                print(transform + str(gradient_steps[i]) + " ]", end=' \\\n')
                for j in range(1, args.reg_pairs+1):
                  print("\t--metric Mattes[ ${{fixedfile{j}}},${{movingfile{j}}},1,32,None ]".format(j=""), end=' \\\n')
                print("\t--convergence [ {},{},10 ]".format("x".join(iterations), args.convergence), end=' \\\n')
                print("\t--shrink-factors {}".format("x".join(shrinks)), end=' \\\n')
                print("\t--smoothing-sigmas {}mm".format("x".join(blurs)), end=' \\\n')
                print("\t" + repeatmask[i], end=' \\\n')

elif args.output == 'twolevel_dbm':
    print("--reg-iterations {}".format("x".join(iterations)), end=' \\\n')
    print("--reg-shrinks {}".format("x".join(shrinks)), end=' \\\n')
    print("--reg-smoothing {}mm".format("x".join(blurs)), end=' ')

elif args.output == 'modelbuild':
    print("-q {}".format("x".join(iterations)), end=' \\\n')
    print("-f {}".format("x".join(shrinks)), end=' \\\n')
    print("-s {}mm".format("x".join(blurs)), end=' ')

elif args.output == 'generic':
    print("--convergence [ {},{},10 ]".format("x".join(iterations), args.convergence), end=' \\\n')
    print("--shrink-factors {}".format("x".join(shrinks)), end=' \\\n')
    print("--smoothing-sigmas {}mm".format("x".join(blurs)), end=' ')

else:
    if args.output in ["multilevel-halving", "affine", "lsq12"]:
      transforms = ["--transform Translation[ ",
                    "--transform Rigid[ ",
                    "--transform Similarity[ ",
                    "--transform Affine[ "]
    elif args.output in ["lsq9","similarity"]:
      transforms = ["--transform Translation[ ",
                    "--transform Rigid[ ",
                    "--transform Similarity[ ",
                    "--transform Similarity[ "]
    elif args.output in ["lsq6","rigid"]:
      transforms = ["--transform Translation[ ",
                    "--transform Rigid[ ",
                    "--transform Rigid[ ",
                    "--transform Rigid[ "]
    gradient_steps = [ 0.5, 0.33437015, 0.2236068, 0.1 ]
    gradient_steps_repeat = [ 0.5, 0.33437015, 0.14953488, 0.1 ]
    repeatmask = [ False,
                   False,
                   "--masks [ ${fixedmask},${movingmask} ]",
                   "--masks [ ${fixedmaskfine},${movingmaskfine} ]" ]
    masks = ["--masks [ NOMASK,NOMASK ]",
             "--masks [ NOMASK,NOMASK ]",
             "--masks [ NOMASK,NOMASK ]",
             "--masks [ ${fixedmask},${movingmask} ]" ]
    slicestart = [ 0,
                   int(round(0.25*len(blurs))),
                   int(round(0.50*len(blurs))),
                   int(round(0.75*len(blurs)))]
    sliceend = [ int(round(0.50*len(blurs))),
                   int(round(0.75*len(blurs))),
                   int(round(0.95*len(blurs))),
                   -1]

    for i, transform in enumerate(transforms):
        if args.close and i < 2:
            pass
        else:
          if i == len(transforms) - 1:
            print(transform + str(gradient_steps[i]) + " ]", end=' \\\n')
            for j in range(1, args.reg_pairs+1):
              print("\t--metric Mattes[ ${{fixedfile{j}}},${{movingfile{j}}},1,64,None ]".format(j=""), end=' \\\n')
              if i > (len(transforms) - 3):
                print("\t--metric GC[ ${{fixedfile{j}}},${{movingfile{j}}},1,NA,None ]".format(j=""), end=' \\\n')
            print("\t--convergence [ {},{},10 ]".format("x".join(iterations[slicestart[i]:]), args.convergence), end=' \\\n')
            print("\t--shrink-factors {}".format("x".join(shrinks[slicestart[i]:])), end=' \\\n')
            print("\t--smoothing-sigmas {}mm".format("x".join(blurs[slicestart[i]:])), end=' \\\n')
            if repeatmask[i]:
              print("\t" + masks[i], end=' \\\n')
              print(transform + str(gradient_steps[i]) + " ]", end=' \\\n')
              for j in range(1, args.reg_pairs+1):
                print("\t--metric Mattes[ ${{fixedfile{j}}},${{movingfile{j}}},1,64,None ]".format(j=""), end=' \\\n')
              if i > (len(transforms) - 3):
                print("\t--metric GC[ ${{fixedfile{j}}},${{movingfile{j}}},1,NA,None ]".format(j=""), end=' \\\n')
              print("\t--convergence [ {},{},10 ]".format("x".join(iterations[slicestart[i]:]), args.convergence), end=' \\\n')
              print("\t--shrink-factors {}".format("x".join(shrinks[slicestart[i]:])), end=' \\\n')
              print("\t--smoothing-sigmas {}mm".format("x".join(blurs[slicestart[i]:])), end=' \\\n')
              print("\t" + repeatmask[i], end=' ')
            else:
              print("\t" + masks[i], end=' ')
          else:
            print(transform + str(gradient_steps[i]) + " ]", end=' \\\n')
            for j in range(1, args.reg_pairs+1):
              print("\t--metric Mattes[ ${{fixedfile{j}}},${{movingfile{j}}},1,32,None ]".format(j=""), end=' \\\n')
              if i > (len(transforms) - 3):
                print("\t--metric GC[ ${{fixedfile{j}}},${{movingfile{j}}},1,NA,None ]".format(j=""), end=' \\\n')
            print("\t--convergence [ {},{},10 ]".format("x".join(iterations[slicestart[i]:sliceend[i]]), args.convergence), end=' \\\n')
            print("\t--shrink-factors {}".format("x".join(shrinks[slicestart[i]:sliceend[i]])), end=' \\\n')
            print("\t--smoothing-sigmas {}mm".format("x".join(blurs[slicestart[i]:sliceend[i]])), end=' \\\n')
            print("\t" + masks[i], end=' \\\n')
            if repeatmask[i]:
              print(transform + str(gradient_steps_repeat[i]) + " ]", end=' \\\n')
              for j in range(1, args.reg_pairs+1):
                  print("\t--metric Mattes[ ${{fixedfile{j}}},${{movingfile{j}}},1,32,None ]".format(j=""), end=' \\\n')
              if i > (len(transforms) - 3):
                print("\t--metric GC[ ${{fixedfile{j}}},${{movingfile{j}}},1,NA,None ]".format(j=""), end=' \\\n')
              print("\t--convergence [ {},{},10 ]".format("x".join(iterations[slicestart[i]:sliceend[i]]), args.convergence), end=' \\\n')
              print("\t--shrink-factors {}".format("x".join(shrinks[slicestart[i]:sliceend[i]])), end=' \\\n')
              print("\t--smoothing-sigmas {}mm".format("x".join(blurs[slicestart[i]:sliceend[i]])), end=' \\\n')
              print("\t" + repeatmask[i], end=' \\\n')
