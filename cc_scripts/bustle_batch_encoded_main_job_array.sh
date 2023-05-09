#!/bin/bash
#SBATCH --cpus-per-task=1   # maximum CPU cores per GPU request: 6 on Cedar, 16 on Graham.
#SBATCH --mem=16000M        # memory per node
#SBATCH --time=02:00:00     # time of the task
#SBATCH --account=def-lelis
#SBATCH --output=%N-%j.out
#SBATCH --mail-user=saqib1@ualberta.ca
#SBATCH --mail-type=ALL
#SBATCH --array=1-38

script_name=${0##*/}
if [[ "$#" -ne 2 ]]; then
	echo " "
	echo "#############################################################################"
	echo ""
	echo " Please provide source directory argument      "
	echo " Usage: sbatch $script_name 'source directory' "
	echo " Example: sbatch $script_name src              "
	echo ""
	echo "#############################################################################"
	echo ""
	exit 1
fi

source_directory=$1

module load python/3.8
module load scipy-stack

# source ~/scratch/env/bin/activate # commenting for local env 
source ../ENV/bin/activate # change this to your environment

python3 ../$source_directory/bustle_batch_encoded_main.py $SLURM_ARRAY_TASK_ID $2
