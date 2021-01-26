#!/bin/bash

#SBATCH --partition gtx1080
#SBATCH --mem=32G  
#SBATCH --cpus-per-task=6  
#SBATCH --time=7-00:00:00      # time (D-H:MM:SS)
#SBATCH --job-name rules_then_sp
#SBATCH --output=rules_then_sp_job.out
#SBATCH --mail-user=uzifr@post.bgu.ac.il
#SBATCH --mail-type=FAIL ### conditions when to send the email. ALL,BEGIN,END,FAIL, REQUEU, NONE
#SBATCH --gres=gpu:1

gin="configs/three_phase_training.gin"

# CHECK PARTITION IS OKEY
exp_name='rules_then_sp'  # CHANGE THIS IN JOB NAME AND OUTPUT, LINES 7,8
file_to_run=three_phase_training

use_partner_data=False
partner='evolved_b'
sp_ratio=5

name="${exp_name}_${sp_ratio}"
output="outputs/${name}.out"
err="outputs/${name}.err.out"
base_dir="/home/uzifr/reworked_checkpoints/${name}"
priming_iters=5000
mixed_iters=0
priming_type=0

module load anaconda
source activate hanabi_env
python3 -um ${file_to_run} --use_partner_data=${use_partner_data} --priming_type=${priming_type} --sp_ratio=${sp_ratio} --partner=${partner} --priming_iters=${priming_iters} --mixed_iters=${mixed_iters} --base_dir=${base_dir} --gin_files=${gin} >${output}  2>${err}
