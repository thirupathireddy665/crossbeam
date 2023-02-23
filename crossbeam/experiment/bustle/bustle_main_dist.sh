#!/bin/bash

#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=1   # maximum CPU cores per GPU request: 6 on Cedar, 16 on Graham.
#SBATCH --mem=64000M        # memory per node
#SBATCH --time=03:00:00     # time of the task
#SBATCH --account=def-lelis
#SBATCH --output=%N-%j.out
#SBATCH --mail-user=emireddy@ualberta.ca
#SBATCH --mail-type=ALL

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

module load python/3.8
module load scipy-stack/2020b
source ~/scratch/crossbeam_env/bin/activate
module load cuda/11.1.1 cudnn

# export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export CUDA_VISIBLE_DEVICES=0

XLA_FLAGS=--xla_gpu_cuda_data_dir=$CUDA_PATH

tout=120
maxw=10
maxne=4
maxni=3
maxsw=12

data_folder=$HOME/data/crossbeam/bustle/t-${tout}-maxw-${maxw}-maxne-${maxne}-maxni-${maxni}

beam_size=10
grad_acc=4
io=bustle_sig
value=bustle_sig

save_dir=$HOME/results/crossbeam/bustle/vw-tout-${tout}-io-${io}-value-${value}-b-${beam_size}-g-${grad_acc}

if [ ! -e $save_dir ];
then
    mkdir -p $save_dir
fi

python3 -m crossbeam.experiment.run_crossbeam \
    --domain=bustle \
    --model_type=char \
    --io_encoder=${io} \
    --value_encoder=${value} \
    --min_task_weight=3 \
    --max_task_weight=$maxw \
    --min_num_examples=2 \
    --max_num_examples=$maxne \
    --min_num_inputs=1 \
    --max_num_inputs=$maxni \
    --max_search_weight=$maxsw \
    --data_folder $data_folder \
    --save_dir $save_dir \
    --grad_accumulate $grad_acc \
    --beam_size $beam_size \
    --gpu_list=0 \
    --num_proc=1 \
    --embed_dim=512 \
    --eval_every 10000 \
    --use_ur=False \
    --encode_weight=True \
    --train_steps 1000000 \
    --train_data_glob train-tasks*.pkl \
    --random_beam=False \
    $@
