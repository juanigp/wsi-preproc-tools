#!/bin/bash -l

#SBATCH --partition=zmmk-exclusive
#SBATCH --mem=200G
#SBATCH --cpus-per-task=10
#SBATCH --time=0-12:00:00
#SBATCH --output=normalize_out.txt
#SBATCH --job-name=normalize


INPUT_FOLDER=/projects/ag-bozek/jpisula/data/downsampled_pre_chemo_zoom_1
OUTPUT_FOLDER=/projects/ag-bozek/jpisula/data/pre_chemo_zoom_1_macenko

NUM_PROCS=10

conda activate torch_env
python3 macenko_normalize_folder.py --i=$INPUT_FOLDER --o=$OUTPUT_FOLDER --num_procs=$NUM_PROCS