#!/bin/bash -l

#SBATCH --partition=zmmk-exclusive
#SBATCH --mem=200G
#SBATCH --cpus-per-task=10
#SBATCH --time=0-12:00:00
#SBATCH --output=patch_extraction_out.txt
#SBATCH --job-name=extract_patches

WSIs_FOLDER=/projects/ag-bozek/jjung/pre_chemo

ZOOM_LEVEL=1
PATCH_SIZE=448

DOWNSAMPLED_IMAGES_FOLDER=/projects/ag-bozek/jpisula/data/downsampled_pre_chemo_zoom_1
BINARY_MASKS_FOLDER=/projects/ag-bozek/jpisula/data/binary_masks_pre_chemo_zoom_1
PATCHES_FOLDER=/scratch/jpisula/data/patches/zoom_1_448_20percent

NUM_PROCS=10

conda activate openslide_env
#this script does not do the complete pipeline
#first i should convert to jpg, then binarize, then extract the patches
#python3 svs_to_jpg.py --i=$WSIs_FOLDER --o=$DOWNSAMPLED_IMAGES_FOLDER --num_procs=$NUM_PROCS --zoom_level=$ZOOM_LEVEL
#python3 binarize_images.py --i=$DOWNSAMPLED_IMAGES_FOLDER --o=$BINARY_MASKS_FOLDER --num_procs=$NUM_PROCS
python3 extract_patches.py --slides_dir=$WSIs_FOLDER --masks_dir=$BINARY_MASKS_FOLDER --o=$PATCHES_FOLDER --zoom_level=$ZOOM_LEVEL --patch_size=$PATCH_SIZE