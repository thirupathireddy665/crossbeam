#!/bin/bash

#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=1   # maximum CPU cores per GPU request: 6 on Cedar, 16 on Graham.
#SBATCH --mem=64000M        # memory per node
#SBATCH --time=00:10:00     # time of the task
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

# Baseline
python3 -m crossbeam.experiment.run_baseline_synthesizer \
  --eval_set_pkl=crossbeam/data/sygus/test-tasks-sygus.pkl \
  --domain=bustle \
  --timeout=30 \
  --verbose=True \
  --json_results_file=${results_dir}/baseline.sygus.30s.json

python3 -m crossbeam.experiment.run_baseline_synthesizer \
  --eval_set_pkl=crossbeam/data/new/test-tasks-new.pkl \
  --domain=bustle \
  --timeout=30 \
  --verbose=True \
  --json_results_file=${results_dir}/baseline.new.30s.json

# CrossBeam
maxni=3
maxsw=20
beam_size=10
data_root=crossbeam/data
models_dir=trained_models/bustle/

for run in 1 2 3 4 5 ; do
  for model in vw-bustle_sig-vsize randbeam ; do
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
          --timeout=600 \
          --max_values_explored=50000 \
          --load_model=${model}/model-best-valid.ckpt \
          --io_encoder=bustle_sig --value_encoder=bustle_sig --encode_weight=True \
          --json_results_file=${results_dir}/run_${run}.${model}.${dataset}.json

      if [[ "${model}" != "randbeam" ]] ; then
        if (( $run == 1)) ; then
          # CrossBeam with Beam Search during evaluation
          # This is deterministic, only 1 run needed
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
              --use_ur=False \
              --timeout=600 \
              --max_values_explored=50000 \
              --load_model=${model}/model-best-valid.ckpt \
              --io_encoder=bustle_sig --value_encoder=bustle_sig --encode_weight=True \
              --json_results_file=${results_dir}/run_${run}.${model}.beam_search.${dataset}.json
        fi

        # CrossBeam with multinomial random sampling during evaluation
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
            --use_ur=False \
            --stochastic_beam=True \
            --timeout=600 \
            --max_values_explored=50000 \
            --load_model=${model}/model-best-valid.ckpt \
            --io_encoder=bustle_sig --value_encoder=bustle_sig --encode_weight=True \
            --json_results_file=${results_dir}/run_${run}.${model}.stochastic_beam.${dataset}.json
      fi
    done
  done
done