#!/bin/bash

#SBATCH --partition ${partition}
#SBATCH --mem=32G  
#SBATCH --cpus-per-task=6  
#SBATCH --time=7-00:00:00      # time (D-H:MM:SS)
#SBATCH --job-name ${exp_name}
#SBATCH --output=${exp_name}_job.out 
#SBATCH --mail-user=uzifr@post.bgu.ac.il
#SBATCH --mail-type=FAIL ### conditions when to send the email. ALL,BEGIN,END,FAIL, REQUEU, NONE
#SBATCH --gres=gpu:1

gin="configs/hanabi_rainbow.gin"

module load anaconda
source activate hanabi_env
python3 -um ${file_to_run} --use_partner_data=${use_partner_data} --sp_ratio=${sp_ratio} --partner=${partner} --base_dir=${base_dir} --gin_files=${gin} >${output}  2>${err}
