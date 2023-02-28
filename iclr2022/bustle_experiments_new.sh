#!/bin/bash

#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --ntasks-per-node=4
#SBATCH --mem=64000M        # memory per node
#SBATCH --time=10:00:00     # time of the task
#SBATCH --account=def-lelis
#SBATCH --output=%N-%j.out
#SBATCH --mail-user=emireddy@ualberta.ca
#SBATCH --mail-type=ALL

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

module load python/3.8
module load scipy-stack/2020b
source ~/scratch/crossbeam_env/bin/activate
module load cuda/11.1.1 cudnn

# export CUDA_VISIBLE_DEVICES=0,1,2,3
export CUDA_VISIBLE_DEVICES=0

XLA_FLAGS=--xla_gpu_cuda_data_dir=$CUDA_PATH

results_dir=iclr2022/bustle_results

# CrossBeam
maxni=3
maxsw=20
beam_size=10
data_root=crossbeam/data
models_dir=trained_models/bustle/

for run in 1 2 3 4 5 ; do
  for model in vw-bustle_sig-vsize ; do
    for dataset in sygus new ; do
      # Normal CrossBeam with UR for evaluation
      python3 -m crossbeam.experiment.run_crossbeam \
          --seed=${run} \
          --domain=bustle \
          --model_type=char \
          --max_num_inputs=$maxni \
          --max_search_weight=$maxsw \
          --data_folder=${data_root}/${dataset} \
          --save_dir=${models_dir} \
          --beam_size=$beam_size \
          --gpu_list=0 \
          --num_proc=1 \
          --eval_every=1 \
          --train_steps=0 \
          --do_test=True \
          --use_ur=True \
          --max_values_explored=1000000 \
          --load_model=${model}/model-best-valid.ckpt \
          --io_encoder=bustle_sig --value_encoder=bustle_sig --encode_weight=True \
          --json_results_file=${results_dir}/run_${run}.${model}.${dataset}.json
    done
  done
done