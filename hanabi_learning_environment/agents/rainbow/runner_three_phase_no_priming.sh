#!/bin/bash

#SBATCH --partition main
#SBATCH --mem=32G  
#SBATCH --cpus-per-task=6  
#SBATCH --time=7-00:00:00      # time (D-H:MM:SS)
#SBATCH --job-name 2_phase
#SBATCH --output=3_phase_no_priming_job.out
#SBATCH --mail-user=uzifr@post.bgu.ac.il
#SBATCH --mail-type=FAIL ### conditions when to send the email. ALL,BEGIN,END,FAIL, REQUEU, NONE
#SBATCH --gres=gpu:1

gin="configs/three_phase_training.gin"

# CHECK PARTITION IS OKEY
exp_name='3_phase_no_priming'  # CHANGE THIS IN JOB NAME AND OUTPUT, LINES 7,8
file_to_run=three_phase_training

use_partner_data=False
partner='evolved_b'
sp_ratio=3

name="${exp_name}_${sp_ratio}"
output="outputs/${name}.out"
err="outputs/${name}.err.out"
base_dir="/home/uzifr/reworked_checkpoints/${name}"
priming_iters=0
mixed_iters=6000

module load anaconda
source activate hanabi_env
python3 -um ${file_to_run} --use_partner_data=${use_partner_data} --sp_ratio=${sp_ratio} --partner=${partner} --priming_iters=${priming_iters} --mixed_iters=${mixed_iters} --base_dir=${base_dir} --gin_files=${gin} >${output}  2>${err}
