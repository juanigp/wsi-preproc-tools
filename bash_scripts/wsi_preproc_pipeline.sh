#!/bin/bash -l
#SBATCH --mem=200G
#SBATCH --cpus-per-task=10
#SBATCH --time=5-12:00:00
#SBATCH --output=../sbatch_out/complete_pipeline_%j.txt
#SBATCH --job-name=extract_patches

PROJECT_FOLDER=..
WSIs_FOLDER=../input
DOWNSAMPLED_IMAGES_FOLDER=../output/downsamples
BINARY_MASKS_FOLDER=../output/masks
PATCHES_FOLDER=../output/patches
PICKLES_FOLDER=../output/pickles

WSI_EXT=.ndpi
ZOOM_LEVEL_DOWNSAMPLE=2
BINARIZATION_FUNC=stain_entropy_otsu
PATCH_FILTER_FUNC=foreground_patches_filter_1
ZOOM_LEVEL_PATCH=1
PATCH_SIZE=224
NUM_PROCS=10

# select pipeline steps
SVS_TO_JPG=false
BINARIZE=false
EXTRACT_PATCHES=false
PICKLE=false

conda activate openslide-env

if [ "$SVS_TO_JPG" = true ] ; then
    echo "converting to jpeg"
    python3 $PROJECT_FOLDER/src/svs_to_jpg.py \
        --i=$WSIs_FOLDER \
        --o=$DOWNSAMPLED_IMAGES_FOLDER \
        --num_procs=$NUM_PROCS \
        --zoom_level=$ZOOM_LEVEL_DOWNSAMPLE \
        --extension=$WSI_EXT
fi

if [ "$BINARIZE" = true ] ; then
    echo "binarizing"
    python3 $PROJECT_FOLDER/src/binarize_images.py \
        --i=$DOWNSAMPLED_IMAGES_FOLDER \
        --o=$BINARY_MASKS_FOLDER \
        --num_procs=$NUM_PROCS \
        --func=$BINARIZATION_FUNC
fi

if [ "$EXTRACT_PATCHES" = true ] ; then
    echo "extracting patches"
    python3 $PROJECT_FOLDER/src/extract_patches.py \
        --slides_dir=$WSIs_FOLDER \
        --masks_dir=$BINARY_MASKS_FOLDER \
        --o=$PATCHES_FOLDER \
        --zoom_level=$ZOOM_LEVEL_PATCH \
        --patch_size=$PATCH_SIZE \
        --func=$PATCH_FILTER_FUNC \
        --extension=$WSI_EXT \
        --num_procs=$NUM_PROCS
fi

if [ "$PICKLE" = true ] ; then
    echo "pickling patches"
    python3 $PROJECT_FOLDER/src/pickle_patches.py \
        --i=$PATCHES_FOLDER \
        --o=$PICKLES_FOLDER \
        --num_procs=$NUM_PROCS
fi