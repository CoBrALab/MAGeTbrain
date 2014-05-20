#!/bin/bash
# vim: set expandtab sw=4 ts=4 tw=80:#
#? morpho 0.1.0 
#
declare -A help

help["main"]="
mb is a utility for automatic image segmentation and shape analysis.

Usage: 
    mb [--help | --version | <command> [<args>...]]
  
General Options: 
    -h, --help       Show help.
    --version        Show version and exit.
 
Commands:
    init             Initialise a MAGeT project folder.
    run              Run the MAGeT pipelines.
    import           Import images into the project.
    check            Check the project configuration before the run.
    status           Report on the status of current pipeline runs.

See 'mb help <command>' for more information on a specific command.
"
function main {
    case $1 in
        init|segment|shape|import|check|status|run) eval "$1 $@";;
        --version) grep "^#? "  "$0" | cut -c 4-;;
        --help)    echo "${help["main"]}"; exit 0;;        
        *)         echo "${help["main"]}"; exit 1;;        
    esac 
}

help["help"]='
Show help for a command. 

Usage: mb help <command>
'
function help { 
    eval "$(docopts -h "${help["help"]}" -A args : "$@")"
    command=${args["<command>"]}
    echo "${help[$command]}"
    exit 1
}

help["init"]="
Initialises a MAGeT project folder. 

Usage: mb init [<folder>]

Options:
    folder           Folder name to initialize [default: $PWD] 
"
function init { 
    eval "$(docopts -h "${help["init"]}" : "$@")"
    folder=${folder:-$PWD}
    mkdir -p ${folder}/input/{model,atlases,templates,subjects}/brains    
    mkdir -p ${folder}/input/{model,atlases}/{masks,labels}
    mkdir -p ${folder}/logs
    mkdir -p ${folder}/output
}

help["run"]="
Run the MAGeT brain pipelines.

Usage: 
    mb run [options] [segment|shape|all]

Command: 
    segment                Segment the subject images. [default]
    shape                  Perform deformation-based shape analysis.
    all                    Perform all analyses
                             
General options: 	                 
    --subject NAME         Subject to analyse (filename without .mnc extension)
    --nomodelspace         Do not register subjects to model space. 
    --registerbin CMD      Script to register images. [default: mb_register]

Folder options: 
    -i PATH --input-dir PATH    Top-level for all input. [default: $PWD/input]
    -o PATH --output-dir PATH   Top-level for all output. [default: $PWD/output]

Execution options:
    -n                     Dry run. Do not take any action.
    -j N                   Number of processes to parallelize over.  [default: 8]
    --queue TYPE           Batch queue to use. [default: pbs]
    --save-temp            Save all temporary files.
    --save-xfms            Save all pairwise XFMs (always true for shape analysis).
    -v, --verbose          Be verbose.
"
function run { 
    helptxt="${help["run"]}"
    eval "$(docopts -h "${helptxt}" : "$@")"
    case $queue in pbs|sge|none) ;; *) die "$helptxt";; esac
    if [[ $segment == "false" && $shape == "false" && $all == "false" ]]; then
        segment="true";
    fi
    check
     
    local run_id=$(date -Isecond | tr -d '\-:')
    local run_dir=$output_dir/rundata
    mkdir -p $run_dir 

    local atlases=($input_dir/atlases/brains/*.mnc)
    local templates=($input_dir/templates/brains/*.mnc)
    local subjects=($input_dir/subjects/brains/*.mnc)
    if [[ $(find $input_dir/model/brains/ -name '*.mnc' | wc -l) -gt 1 ]]; then
        die "More than one model image found in $input_dir/model/brains"; 
    fi
    local model=$input_dir/model/brains/*.mnc 

    if [[ $nomodelspace == "true" && $segment == "false" ]]; then 
        die "the --nomodelspace option cannot be used when performing shape analysis."
    fi

    # register subjects and templates to model space
    if [[ $nomodelspace == "false" ]]; then 
        die_if_dne $model "No model image found in $input_dir/model/brains/" 
        local std_dir=$output_dir/std
        local std_tmpl_dir=$std_dir/templates
        local std_subj_dir=$std_dir/subjects
        local new_templates=( )
        local new_subjects=( )

        local modelspace_cmds=( )
        mkdir -p $std_tmpl_dir $std_subj_dir

        local resampled_model=$std_dir/$(basename $model)
        autocrop 
        for t in ${templates[@]}; do
            std_tmpl=$std_tmpl_dir/$(stem $t)_std.mnc
            [[ -e $std_tmpl ]] && continue
            modelspace_cmds+=( "bestlinreg $t $model $std_tmpl" )
        done

        for s in ${subjects[@]}; do
        done
    fi 

    # build template library 
    template_cmds=$run_dir/mb-mktemplib-${run_id}
    mb.mktmpl -i $input_dir -o $output_dir -j$j -n | queue

    # segment subjects
    local labelsdir=$output_dir/labels
    go mkdir -p $labelsdir;
    for s in ${subjects[@]}; do
        local workdir=/dev/shm/mb-work-$(stem $s)-${run_id}
        local labels=$labelsdir/$(stem $s).mnc 
        
        go mkdir -p $workdir

        # register templates to subject
        for t in ${templates[@]}; do
            xfm=$(regxfmpath $workdir $t $s)
            echo $registerbin $t $s $xfm
        done | goparallel -j$j

        # merge atlas->template->subject xfms
        for a in ${atlases[@]}; do for t in ${templates[@]}; do
            local at_xfm=$(regxfmpath $output_dir $a $t)
            local ts_xfm=$(regxfmpath $workdir $t $s)
            local as_xfm=$(regxfmpath $workdir $a $t $s)
            go mkdir -p $(dirname $as_xfm)
            echo xfmjoin $at_xfm $ts_xfm $as_xfm
        done; done | goparallel -j$j

        # propogate atlas labels into subject space
        go mkdir -p $workdir/labels
        for a in ${atlases[@]}; do for t in ${templates[@]}; do
            local as_xfm=$(regxfmpath $workdir $a $t $s)
            local candidate=$workdir/labels/$(stem $a).$(stem $t).$(stem $s).mnc
            echo mincresample -transform $as_xfm \
                    -like $s $(labelspath $a) $candidate
        done; done | goparallel -j$j 

        local candidates=()  # separate loop because bash arrays suck
        for a in ${atlases[@]}; do for t in ${templates[@]}; do
            candidates+=( $workdir/labels/$(stem $a).$(stem $t).$(stem $s).mnc )
        done; done 

        #fuse candidate labels 
        echo go voxel_vote.py $labels ${candidates[@]}
        
        if [[ -n $save_work ]]; then
            go tar cf $output_dir/work/$(basename $workdir).tar $workdir
        fi
        
        if [[ -n $save_xfms ]]; then
            go cp -r $workdir/xfms $output_dir
        fi

        go rm -rf $workdir
    done;
}

# Check the status of the project setup
function check {
    for i in $input_dir \
        $input_dir/{atlases,model,templates,subjects}{,/brains} \
        $input_dir/{atlases,model}/{masks,labels}; do
        die_if_dne $i
    done

    local atls_images=( $(find $input_dir/atlases/brains -iname '*.mnc') )
    local tmpl_images=( $(find $input_dir/templates/brains -iname '*.mnc') )
    local subj_images=( $(find $input_dir/subjects/brains -iname '*.mnc') )
    local num_atls=${#atls_images[@]}
    local num_tmpl=${#tmpl_images[@]}
    local num_subj=${#subj_images[@]}

    # atlases
    [[ $num_atls  -eq 0 ]] && die "No atlases found in $input_dir/atlases/brains"
    [[ $(( $num_atls % 2)) -eq 0 ]] && die "$num_atls atlases found. Use odd number."

    for i in $atls_images; do 
        local labels=$(labelspath $i);
        die_if_dne $labels "$i labels not found at $labels"
    done

    # templates
    [[ $num_tmpl  -eq 0 ]] && die "No templates found in $input_dir/templates/brains"
    [[ $(( $num_tmpl % 2)) -eq 0 ]] && die "$num_tmpl templates found. Use odd number."

    # templates
    [[ $num_subj  -eq 0 ]] && die "No subjects found in $input_dir/subjects/brains"
}

# utility functions
function die { echo $1; exit 1; }
function die_if_dne { [[ ! -e $1 ]] && die "${2:-"$1 does not exist."}"; }
function stem { echo $(basename $1 .mnc); }
function labelspath { echo $(dirname $(dirname $1))/labels/$(stem $1)_labels.mnc; }
function go { [[ $verbose == "true" ]] && echo "$@";  [[ $dry_run == "false" ]] && eval $@;}
function gosh { go "$*"; }
function goparallel { go parallel "$@"; cat; }
function regxfmpath {
    basedir=$1; shift; 
    regdir=$basedir/xfms;
    for i in ${@}; do regdir="$regdir/$(stem $i)"; done;
    echo $regdir/reg.xfm;
}
function queue.none { parallel -j1 }
    

### main ###
main $@
