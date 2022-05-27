#!/bin/bash -l

INPUT_FOLDER=/Users/juanigp/Desktop/CMMC/chemo/jpegs_zoom_level_2
OUTPUT_FOLDER=/Users/juanigp/Desktop/CMMC/chemo/jpegs_zoom_level_2_macenko_my_algo

NUM_PROCS=10

#conda activate nomkl
python3 macenko_normalize_folder_my_algo.py --i=$INPUT_FOLDER --o=$OUTPUT_FOLDER --num_procs=$NUM_PROCS