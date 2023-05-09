#!/bin/bash

cd ~/scratch/

rm -rf env

module load python/3.8
module load scipy-stack/2020b
virtualenv --no-download ./env
source ./env/bin/activate
pip install --no-index --upgrade pip
pip install scikit-learn==0.23
pip install --no-index tensorflow==2.4.1