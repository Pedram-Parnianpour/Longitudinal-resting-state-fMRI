#!/bin/bash
set -e  # Exit on error
set -x  # Debug: print each command as it runs
#Template provided by Daniel Levitas of Indiana University
#Edits by Andrew Jahn, University of Michigan, 07.22.2020
#Modified by Pedram Parnianpour, University of British Columbia, 02.02.2025

#User inputs:
bids_root_dir=/path/to/project_root
subjects=("01" "02" "03") # <-- Add as many subjects as you want
nthreads=16
mem=60 #gb

#Begin:

#Convert virtual memory from gb to mb
mem=`echo "${mem//[!0-9]/}"` #remove gb at end
mem_mb=`echo $(((mem*1000)-5000))` #reduce some memory for buffer space during pre-processing

#export FreeSurfer License
export FS_LICENSE=/path/to/freesurfer/license.txt

for subj in "${subjects[@]}"; do
  fmriprep-docker $bids_root_dir $bids_root_dir/derivatives \
    participant \
    --participant-label $subj \
    --skip-bids-validation \
    --md-only-boilerplate \
    --fs-license-file $FS_LICENSE \
    --fs-no-reconall \
    --output-spaces MNI152NLin2009cAsym:res-2 \
    --nthreads $nthreads \
    --stop-on-first-crash \
    --mem_mb $mem_mb
done
