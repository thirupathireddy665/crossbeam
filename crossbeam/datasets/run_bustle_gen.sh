#!/bin/bash

#SBATCH --cpus-per-task=1   # maximum CPU cores per GPU request: 6 on Cedar, 16 on Graham.
#SBATCH --mem=32000M        # memory per node
#SBATCH --time=10:00:00     # time of the task
#SBATCH --account=def-lelis
#SBATCH --output=%N-%j.out
#SBATCH --mail-user=emireddy@ualberta.ca
#SBATCH --mail-type=ALL

module load python/3.8
module load scipy-stack/2020b
source ~/scratch/crossbeam_env/bin/activate

data_dir=$HOME/data/crossbeam/bustle

tout=120
maxw=10
maxne=4
maxni=3
num_proc=90
out_dir=$data_dir/t-${tout}-maxw-${maxw}-maxne-${maxne}-maxni-${maxni}

if [ ! -e $out_dir ];
then
    mkdir -p $out_dir
fi

echo 'Generating validation'
valid_file=$out_dir/valid-tasks.pkl

python3 -m crossbeam.datasets.bottom_up_data_generation \
    --domain=bustle \
    --output_file=$valid_file \
    --data_gen_seed=10000 \
    --data_gen_timeout=$tout \
    --num_tasks=10 \
    --num_searches=1000 \
    --min_task_weight=3 \
    --max_task_weight=$maxw \
    --min_num_examples=2 \
    --max_num_examples=$maxne \
    --min_num_inputs=1 \
    --max_num_inputs=$maxni \
    --num_datagen_proc=$num_proc \
    --verbose=False

echo 'Generating training'

training_file=$out_dir/train-tasks.pkl

python3 -m crossbeam.datasets.bottom_up_data_generation \
    --domain=bustle \
    --output_file=$training_file \
    --data_gen_seed=0 \
    --data_gen_timeout=$tout \
    --num_tasks=1000 \
    --num_searches=10000 \
    --min_task_weight=3 \
    --max_task_weight=$maxw \
    --min_num_examples=2 \
    --max_num_examples=$maxne \
    --min_num_inputs=1 \
    --max_num_inputs=$maxni \
    --num_datagen_proc=$num_proc \
    --verbose=False