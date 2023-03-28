#!/bin/bash
#SBATCH --job-name=z_tracking
#SBATCH --output=/n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker/slurm_out/slurm-%A_%a.out
#SBATCH -t 01:00:00
#SBATCH -p short
#SBATCH --mem=8G
#SBATCH -c 1
#SBATCH -n 1
set -e

module load gcc/6.2.0
module load conda2/4.2.13

source activate ROICaT

cd /n/data1/hms/neurobio/sabatini/gyu/github_clone/z_position_tracker
echo "$@"
python3 -c "import slurm_z_tracking; slurm_z_tracking.z_tracking()" "$@"