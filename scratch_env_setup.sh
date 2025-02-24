#!/bin/bash

cd ~/scratch/

rm -rf crossbeam_env

module load python/3.8
module load scipy-stack/2020b
virtualenv --no-download ./crossbeam_env
source ./crossbeam_env/bin/activate
pip install --no-index --upgrade pip
pip install numpy==1.24.2
pip install torch==1.10.2+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
pip install torch-scatter -f https://data.pyg.org/whl/torch-1.10.0+cu113.html
pip install absl-py
pip install tqdm
pip install pickle5
