#!/bin/bash -l

WSIs_FOLDER=/Users/juanigp/Desktop/CMMC/chemo/pipeline_completo_svs

ZOOM_LEVEL=1
PATCH_SIZE=224

#DOWNSAMPLED_IMAGES_FOLDER=/Users/juanigp/Desktop/CMMC/chemo/downsampled_pre_chemo_zoom_1
#BINARY_MASKS_FOLDER=/Users/juanigp/Desktop/CMMC/chemo/binary_masks_pre_chemo_zoom_1
DOWNSAMPLED_IMAGES_FOLDER=/Users/juanigp/Desktop/CMMC/chemo/pipeline_completo_downsamples
BINARY_MASKS_FOLDER=/Users/juanigp/Desktop/CMMC/chemo/pipeline_completo_masks
PATCHES_FOLDER=/Users/juanigp/Desktop/CMMC/chemo/patches_pre_chemo_zoom_1_my_macenko

NUM_PROCS=10

#conda activate nomkl
# python3 svs_to_jpg.py --i=$WSIs_FOLDER --o=$DOWNSAMPLED_IMAGES_FOLDER --num_procs=$NUM_PROCS --zoom_level=$ZOOM_LEVEL
python3 binarize_images.py --i=$DOWNSAMPLED_IMAGES_FOLDER --o=$BINARY_MASKS_FOLDER --num_procs=$NUM_PROCS
# python3 extract_patches.py --slides_dir=$WSIs_FOLDER --masks_dir=$BINARY_MASKS_FOLDER --o=$PATCHES_FOLDER --zoom_level=$ZOOM_LEVEL --patch_size=$PATCH_SIZE
python3 extract_patches_w_macenko.py \
    --slides_dir=$WSIs_FOLDER \
    --masks_dir=$BINARY_MASKS_FOLDER \
    --downsamples_dir=$DOWNSAMPLED_IMAGES_FOLDER \
    --o=$PATCHES_FOLDER \
    --zoom_level=$ZOOM_LEVEL \
    --patch_size=$PATCH_SIZE