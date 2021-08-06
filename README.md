# Multiple Automatically Generated Templates brain segmentation algorithm

---

Looking for the MAGeT Morphology pipeline? Use the `morpho-labelmask` branch instead.
    
---

Given a set of labelled MR images (atlases) and unlabelled images (subjects), MAGeT produces a segmentation for each subject using a multi-atlas voting procedure based on a template library made up of images from the subject set.  

Here is a schematic comparing 'traditional' multi-atlas segmentation, and MAGeT brain segmentation: 

![Multi-atlas and MAGeT brain operation schematic](doc/MA-MAGeTBrain-Schematic.png "Schematic")

The major difference between algorithms is that, in MAGeT brain, segmentations from each atlas (typically manually delineated) are propogated via image registration to a subset of the subject images (known as the 'template library') before being propogated to each subject image and fused. It is our hypothesis that by propogating labels to a template library, we are able to make use of the neuroanatomical variability of the subjects in order to 'fine tune' each individual subject's segmentation. 

To [cite MAGeTbrain in publications](CITATION), please use:

> Pipitone J, Park MT, Winterburn J, et al. Multi-atlas segmentation of the whole hippocampus
> and subfields using multiple automatically generated templates. Neuroimage. 2014;

> M Mallar Chakravarty, Patrick Steadman, Matthijs C van Eede, Rebecca D Calcott, Victoria Gu, Philip Shaw, Armin Raznahan, D Louis Collins, and Jason P Lerch.
> Performing label-fusion-based segmentation using multiple automatically generated templates. Hum Brain Mapp, 34(10):2635–54, October 2013. (doi:10.1002/hbm.22092)

## Dependencies

In order to use MAGeTBrain, you will need to install: 
- Python 3, we recommend you install the [anaconda python 3 distribution](https://www.anaconda.com/distribution/)
- ANTs (with MINC enabled)
- [minc-toolkit-v2](https://bic-mni.github.io/)
- [pyminc](https://github.com/Mouse-Imaging-Centre/pyminc)
- [minc-stuffs](https://github.com/Mouse-Imaging-Centre/minc-stuffs)
- for cluster integration [qbatch](https://github.com/pipitone/qbatch)
- [gnu-parallel](https://www.gnu.org/software/parallel/)

or

Just use the pipeline on Compute Canada's Niagara Cluster.

## Getting started, for the impatient:

    git clone https://github.com/CobraLab/MAGeTbrain.git
    source MAGeTbrain/bin/activate
    mb init segmentations
    cd segmentations
    mb import atlas1_t1.mnc atlas1_labels.mnc
    mb import atlas2_t1.mnc atlas2_labels.mnc
    ... 
    mb check
    mb run

## Quick start

0. Check out a copy of this repository somewhere handy,
    
        git clone https://github.com/CobraLab/MAGeTbrain.git

1. Add the `MAGeTbrain/bin` folder to your path. This can be done easily by
running, `source MAGeTbrain/bin/activate` (revert PATH by typing `deactivate`). 

1. Create a new folder for your project and, 

        mb init

2. Copy/link your atlases, templates, subjects into `input/atlases`,
   `input/templates`, and `input/subjects`, respectively.  As per always, MR
   images go in `brains`. 

   Atlas labels are expected to have the same name as their MR image but with a
   postfix of `_labels.mnc`. Use the `import` command to simplify the renaming
   process:
        mb import /path/to/image_file.mnc /path/to/label_file.mnc

   This copies the image and label files into the proper folder and rename the
   label file accordingly. Use the `mb import -l` to use symbolic links rather
   than copying files.

3. MAGeT Brain is operated using the `mb` command. In order to run the
   entire pipeline, simply run: 

        mb run

   This uses the default settings to execute the necessary commands. In
   particular, it assumes you have access to a qbatch-enabled batch queuing system, and
   uses the utility `qbatch` to submit commands in batches.  If you are
   running this on Niagara, you should have no problems.

   If you can also run MAGeT Brain using the GNU parallel on a single machine, 
   like so: 

        mb run -q parallel

    
Currently, only majority voting label fusion is enabled.  For a more complete
implementation, check the 'master' branch. 

## MAGeT Brain Commands


#### `mb init`

```
mb init [<folder>]

```

The `init` command is used to start a new project. It creates a folder
structure to hold MAGeT brain inputs and outputs. If no folder name is supplied
then the current folder is used.  `init` creates the following folders: 

```
project-folder/
    input/
        atlases/
            brains/
            labels/
        templates/
            brains/
        subjects/
            brains/
    output/
```    

### `mb import`

```
mb import <image.mnc> <labels.mnc> [<mask.mnc>]
```

The given image and corresponding labels are imported into the `input/atlases`
folder, with the proper naming convention. 

### `mb check`

Checks the input configuration and reports any anomalies and suggestions to
correct them. If this command doesn't return any messages then you should be
set to run MAGeT brain. 

### `mb status`

Reports on the progress of MAGeT brain and shows the number of remaining tasks.

### `mb run`

Starts the MAGeT brain pipeline. 


## Tutorials

For an in-depth guideline, follow the [MAGeTbrain](https://github.com/CobraLab/documentation/wiki/MAGeTBrain) and the [MAGeTmorph](https://github.com/CobraLab/documentation/wiki/MAGeTBrain#morpho-mode) tutorials.

---
    http://tinysong.com/y9lO
