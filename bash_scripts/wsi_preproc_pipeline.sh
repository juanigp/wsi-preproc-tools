#!/bin/bash -l

#SBATCH --mem=200G
#SBATCH --cpus-per-task=10
#SBATCH --time=5-12:00:00
#SBATCH --output=../sbatch_out/complete_pipeline_%j.txt
#SBATCH --job-name=extract_patches

PROJECT_FOLDER=/data/jpisula/code/patch-extraction

# WSIs preproc. args
NUM_PROCS=1

WSIs_FOLDER=/data/jpisula/data/scc-debug-patching

WSI_EXT=.ndpi
ZOOM_LEVEL_DS=2
BINARIZATION_FUNC=stain_entropy_otsu
PATCH_FILTER_FUNC=foreground_patches_filter_1
ZOOM_LEVEL_PATCH=1
PATCH_SIZE=224

DOWNSAMPLED_IMAGES_FOLDER=/data/jpisula/data/scc-debug-patching
BINARY_MASKS_FOLDER=/data/jpisula/data/scc-debug-patching
PATCHES_FOLDER=/data/jpisula/data/scc-debug-patching/patches

# pickling args
PICKLE_IN_CSV=$PROJECT_FOLDER/csvs/tumor_regression_3_as_2.csv
PICKLES_DIR=/scratch/jpisula/data/patches/zoom_1_224_20percent_pickled_with_edges
PICKLE_OUT_CSV=$PROJECT_FOLDER/csvs/zoom_1_224_20percent_pickled_with_edges.csv
PICKLE_FUNC=pickle_row_patches_and_edge_index

# 5fold args
FOLDS_IN_CSV=$PICKLE_OUT_CSV
FOLDS_OUT_CSV_DIR=$PROJECT_FOLDER/csvs/zoom_1_224_20percent_with_edges

#filter csvs args
CSVS_ROOT=$PROJECT_FOLDER/csvs/zoom_1_224_20percent_with_edges

# select pipeline steps
SVS_TO_JPG=false
BINARIZE=true
EXTRACT_PATCHES=true
EXTRACT_PATCHES_MACENKO=false
PICKLE=false
MAKE_FOLDS=false
MAKE_SYMLINKS=false
EDIT_CSVS=false

# EXTRACT_PATCHES Y EXTRACT_PATCHES_MACENKO no pueden ser simultaneamente verdaderos
if [ "$EXTRACT_PATCHES" = true ] && [ "$EXTRACT_PATCHES_MACENKO" = true ] ; then
    echo "EXTRACT_PATCHES and EXTRACT_PATCHES_MACENKO can not be simultaneously true"
    exit 1
fi

conda activate openslide-env

# ver de ejecutar bien los scripts con sus directorios
if [ "$SVS_TO_JPG" = true ] ; then
    echo "converting to jpeg"
    python3 $PROJECT_FOLDER/src/svs_to_jpg.py \
        --i=$WSIs_FOLDER \
        --o=$DOWNSAMPLED_IMAGES_FOLDER \
        --num_procs=$NUM_PROCS \
        --zoom_level=$ZOOM_LEVEL_DS \
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
        --extension=$WSI_EXT
fi

if [ "$EXTRACT_PATCHES_MACENKO" = true ] ; then
    echo "extracting patches with normalisation"
    python3 $PROJECT_FOLDER/src/extract_patches_w_macenko.py \
        --slides_dir=$WSIs_FOLDER \
        --masks_dir=$BINARY_MASKS_FOLDER \
        --downsamples_dir=$DOWNSAMPLED_IMAGES_FOLDER \
        --o=$PATCHES_FOLDER \
        --zoom_level=$ZOOM_LEVEL_PATCH \
        --patch_size=$PATCH_SIZE \
        --func=$PATCH_FILTER_FUNC \
        --extension=$WSI_EXT
fi

conda deactivate
conda activate lit-env

if [ "$PICKLE" = true ] ; then
    echo "pickling patches"
    python3 $PROJECT_FOLDER/patch_extraction/make_pickles_csv.py \
        --in_csv=$PICKLE_IN_CSV \
        --patches_root=$PATCHES_FOLDER \
        --pickles_dir=$PICKLES_DIR \
        --csv_out=$PICKLE_OUT_CSV \
        --func=$PICKLE_FUNC
fi

if [ "$MAKE_FOLDS" = true ] ; then
    echo "making 5 fold csvs"
    python3 $PROJECT_FOLDER/preprocessing/make_5fold_csvs.py \
        --csv_in=$FOLDS_IN_CSV \
        --csvs_out_dir=$FOLDS_OUT_CSV_DIR
fi

# if [ "$MAKE_SYMLINKS" = true ] ; then
# fi

if [ "$EDIT_CSVS" = true ] ; then
    echo "editing csvs"
    python3 $PROJECT_FOLDER/preprocessing/filter_csv.py \
        --root=$CSVS_ROOT
fi



