#!/bin/bash

#SBATCH --partition gtx1080
#SBATCH --mem=32G  
#SBATCH --cpus-per-task=6  
#SBATCH --time=7-00:00:00      # time (D-H:MM:SS)
#SBATCH --job-name evaluation
#SBATCH --output=evaluation_job.out 
#SBATCH --mail-user=uzifr@post.bgu.ac.il
#SBATCH --mail-type=FAIL ### conditions when to send the email. ALL,BEGIN,END,FAIL, REQUEU, NONE
#SBATCH --gres=gpu:1

gin="configs/hanabi_rainbow.gin"
exp_name=eval_w_rules
file_to_run = eval_Rainbow_with_rules
use_partner_data = False
output="outputs/${exp_name}.out"
err="outputs/${exp_name}.err.out"
base_dir="/home/uzifr/reworked_checkpoints/sp_pre_and_post_2"


module load anaconda
source activate hanabi_env
python3 -um evaluate_agent --base_dir=${base_dir} --partner='evolved_b' --gin_files=${gin} >${output}  2>${err}
