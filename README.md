# Multiple Automatically Generated Templates

MAGeT is a tool for *MR image segmentation and shape analysis* designed for situations when only a small number of "ground truth" labelled images ('atlases') are available. MAGeT operates by using image registration to create
a template library from a representative sample of a pool unlabelled images. It is our hypothesis that by propogating labels to such a template library, we are able to _tune_ the neuroanatomical variability of the atlas library to match
that of the target population, and so improve accuracy and consistency. 

MAGeT is currently designed to be used with the MINC imaging formats.

## MAGeT Morphology 

---

**NOTE: this tool is under development. Stay tuned for usage changes.**
  
  Currently available at: 
  - https://github.com/pipitone/MAGeTbrain/tree/morpho

---

### Installation

MAGeT depends on having the minc-tools available, as well as GNU parallel. If
you are on SciNET, you may be able to run the following commands to set up your
environment (put these in your ~/.bashrc for extra points): 

```sh
$ module load gnu-parallel
$ module load ~pipitone/privatemodules/minc-tools-chihiro
```

Then, to install MAGeT itself, I recommend the following: 

```sh
$ mkdir projectX
$ cd projectX
$ git clone -b morpho https://github.com/pipitone/MAGeTbrain.git 
```

To put the MAGeT brain scripts into your path, simply run: 

```sh
$ source MAGeTbrain/bin/activate
```

### Preparing your inputs

MAGeT expects your inputs to be organized in a very specific way:

```
  project_folder/
    input/
      model/
          brains/    - a single .mnc image
          xfms/      - model to atlas XFMs, as to_<atlas name>.xfm 
          objects/   - .obj files

      atlases/     
          brains/    - one or more .mnc image
          objects/   - .obj files

      subjects/
          brains/    - target .mnc images to be labelled

      templates/     (optional)
          brains/    - copies/symlinks to some of the subject images
```

Starting in your project folder (following the install instructions above) you
can use this command to create this folder structure (approximately): 

```sh    
$ mkdir -p input/{model,atlases,subjects,templates}/brains  input/{model,atlases}/objects input/model/xfms
```

If you only have a single atlas (and so your atlas and model are effectively the same thing), you may leave out the ```atlases/``` folder and the ```model/xfms``` folder, and MAGeT brain will do the right thing.

### Running MAGeT morph

The main interface to the MAGeT morphological analysis tools is via the ```morpho``` command. Use ```morpho --help``` to see detailed options and usage. **```morpho``` must be run from within a project folder. That is, it expects to find an ```input/``` folder in the current directory.**

If you have set up the folder structure as described above, then you can simply run ```morpho -n``` to get a play-by-play of the commands that will be run. This is likely overwhelming, but it will confirm that your inputs are configured correctly since any missing or misconfiguration should be reported as an error early on. 

Running ```morpho``` by itself will start the processing pipeline on the current machine, by default using up to 8 parallel processes (change that with the ```-j``` option). If you are on a compute cluster, like Scinet, you can specify that the commands will be batched up and submitted to the cluster queueing system by using the ```--queue``` option (for SciNET, use ```--queue pbs```) and setting the ```--walltime``` to something long. 

```morpho``` can also dump the commands to a single file shell script (```--write-to-script```, which also makes use of ```-j```) which you can then submit yourself or keep around for documentation/reproducibility.  

Lastly, you can control which subjects are processed using the ```-s``` flag. List the subject file names without the .mnc extension (e.g. ```-s s001 s002 s003```). Likewise, you can specify which subjects are used as templates in the template library by using the ```-t``` flag. This option can be used in-place of creating an ```input/templates``` folder, or to override it. 

### MAGeT morph output

Upon completing successfully, the output will held in the following folders: 

```
  project_folder/
    output/
      nuc/            - corrected subject images
      modelspace/     - subject images registered (lsq9) to the model image
      registrations/  - XFM files (e.g. from pairwise registrations)
      gridavg/        - averaged grid transform for each subject, as <subject>_grid.mnc
      displacement/   - .txt vertex displacement files for each subject, as <subject>_<obj>.txt
```

## Segmentation

--- 

MAGeT brain for segmentation can be found at:
  - https://github.com/pipitone/MAGeTbrain/tree/simplified

**The version in this branch is unstable and so you probably do not want to be using it.**

---

Given a set of labelled MR images (atlases) and unlabelled images (subjects), MAGeT produces a segmentation for each subject using a multi-atlas voting procedure based on a template library made up of images from the subject set.  

Here is a schematic comparing 'traditional' multi-atlas segmentation, and MAGeT brain segmentation: 

![Multi-atlas and MAGeT brain operation
schematic](doc/MA-MAGeTBrain-Schematic.png "Schematic")

The major difference between algorithms is that, in MAGeT brain, segmentations from each atlas (typically manually delineated) are propogated via image registration to a subset of the subject images (known as the 'template library')
before being propogated to each subject image and fused. It is our hypothesis that by propogating labels to a template library, we are able to make use of the neuroanatomical variability of the subjects in order to 'fine tune' each
individual subject's segmentation. 

### For the impatient:

    git clone http://pipitone.github.com/MAGeTbrain
    export PATH=$PWD/MAGeTBrain/bin:$PATH
    mb init segmentations
    cd segmentations
    mb import atlas1_t1.mnc atlas1_labels.mnc
    mb import atlas2_t1.mnc atlas2_labels.mnc
    ... 
    mb check
    mb run

### Quick start

0. Check out a copy of this repository somewhere handy,
    
        git clone  git://github.com/pipitone/MAGeTbrain.git 

1. Add the `bin` folder to your path. Create a new folder for your project and, 

        mb init

2. Copy/link your atlases, templates, subjects into `input/atlases`,  `input/templates`, and `input/subjects`, respectively.  As per always, MR images go in `brains`. 

   Atlas labels are expected to have the same name as their MR image but with a postfix of `_labels.mnc`. Use the `import` command to simplify the renaming process:
        mb import /path/to/image_file.mnc /path/to/label_file.mnc

   This copies the image and label files into the proper folder and rename the
   label file accordingly. Use the `mb import -l` to use symbolic links rather
   than copying files.

3. MAGeT Brain is operated using the ```mb``` command. In order to run the
   entire pipeline, simply run: 

        mb run

   This uses the default settings to execute the necessary commands. In
   particular, it assumes you have access to a PBS batch queuing system, and
   uses the utility ```bin/qbatch``` to submit commands in batches.  If you are
   running this on SciNet, you should no problems.

   If you can also run MAGeT Brain using the GNU parallel on a single machine, 
   like so: 

        mb run -q parallel

    
Currently, only majority voting label fusion is enabled.  For a more complete
implementation, check the 'master' branch. 

### MAGeT Brain Commands


#### ```mb init```

```
mb init [<folder>]

```

The ```init``` command is used to start a new project. It creates a folder
structure to hold MAGeT brain inputs and outputs. If no folder name is supplied
then the current folder is used.  ```init`` creates the following folders: 
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

#### ```mb import```
```
mb import <image.mnc> <labels.mnc> [<mask.mnc>]
```

#### ```mb check```
#### ```mb status```
#### ```mb run```

---
    http://tinysong.com/y9lO
