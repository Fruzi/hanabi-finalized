#!/bin/bash



exp_name=sp_pre_and_post
file_to_run = sp_priming_sp_finale
partition = 'short'


use_partner_data = False
partner = 'evolved_b'

declare -a iter_arr=(1)
declare -a ratio_arr=(2 3 4 5)

for iter in ${iter_arr[@]}; do
	for ratio in ${ratio_arr[@]}; do
		name="${exp_name}_${ratio}_${iter}"
		output="outputs/${name}.out"
		err="outputs/${name}.err.out"
		base_dir="/home/uzifr/new_checkpoints/${name}"
		sbatch --export=beam=${beam_size},depth=${depth},memory=${game_memory},sample_size=${sample_size},sp_ratio=${ratio},partner=${partner},base_dir=${base_dir},output=${output},err=${err},exp_name=${exp_name} runner.sh
	done
done
