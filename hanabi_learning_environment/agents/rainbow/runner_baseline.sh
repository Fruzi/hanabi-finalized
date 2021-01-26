#!/bin/bash

#SBATCH --partition main
#SBATCH --mem=32G  
#SBATCH --cpus-per-task=6  
#SBATCH --time=7-00:00:00      # time (D-H:MM:SS)
#SBATCH --job-name baseline
#SBATCH --output=baseline_job_output.out 
#SBATCH --mail-user=uzifr@post.bgu.ac.il
#SBATCH --mail-type=FAIL ### conditions when to send the email. ALL,BEGIN,END,FAIL, REQUEU, NONE
#SBATCH --gres=gpu:1

gin="configs/hanabi_rainbow.gin"

module load anaconda
source activate hanabi_env
python3 -um train --base_dir="/home/uzifr/reworked_checkpoints/baseline_rainbow_3" --gin_files=${gin} >outputs/baseline_rainbow_3.out  2>outputs/baseline_Rainbow_3.err.out
