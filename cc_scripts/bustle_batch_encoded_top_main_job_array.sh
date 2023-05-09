#!/bin/bash
#SBATCH --cpus-per-task=1   # maximum CPU cores per GPU request: 6 on Cedar, 16 on Graham.
#SBATCH --mem=64000M        # memory per node
#SBATCH --time=01:30:00     # time of the task
#SBATCH --account=def-lelis
#SBATCH --output=%N-%j.out
#SBATCH --mail-user=emireddy@ualberta.ca
#SBATCH --mail-type=ALL
#SBATCH --array=1-89

script_name=${0##*/}
if [[ "$#" -ne 1 ]]; then
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

source ~/scratch/env/bin/activate

python3 ../$source_directory/bustle_batch_encoded_top_main.py $SLURM_ARRAY_TASK_ID

