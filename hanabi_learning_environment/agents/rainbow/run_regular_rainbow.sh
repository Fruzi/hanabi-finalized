#!/bin/bash

#SBATCH --partition gtx1080
#SBATCH --mem=32G  
#SBATCH --cpus-per-task=6  
#SBATCH --time=7-00:00:00      # time (D-H:MM:SS)
#SBATCH --job-name baseline
#SBATCH --output=baseline_output.out 
#SBATCH --mail-user=uzifr@post.bgu.ac.il
#SBATCH --mail-type=FAIL ### conditions when to send the email. ALL,BEGIN,END,FAIL, REQUEU, NONE
#SBATCH --gres=gpu:1

gin="configs/hanabi_rainbow.gin"

module load anaconda
source activate hanabi_env
python3 -um train --base_dir="/home/uzifr/new_checkpoints/basline_rainbow" --gin_files=${gin} >Baseline_Rainbow.out  2>Baseline_Rainbow.err.out
