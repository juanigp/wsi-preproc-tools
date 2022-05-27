import argparse
import os
import multiprocessing
from functools import partial
import numpy as np
import torch
import openslide
from utils import recursive_listdir

MODULES_DICT = {}
def add_to_registry(fun):
    fun_name = fun.__name__
    MODULES_DICT[fun_name] = fun
    return fun

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slides_dir", type=str, default='./', help='Directory with the images to binarize')
    parser.add_argument("--masks_dir", type=str, default='./', help='Directory with the binary masks')
    parser.add_argument("--o", type=str, default='./', help='Directory to store the extracted patches')
    parser.add_argument("--extension", type=str, default='.svs', help='File extension of the input images')
    parser.add_argument("--patch_size", type=int, default=500, help='Size of the patches')
    parser.add_argument("--num_procs", type=int, default=1, help='Number of processes')
    parser.add_argument("--zoom_level", type=int, default=0, help='Zoom level for the WSI')
    parser.add_argument("--func", type=str, help='Foreground patches filter function')

    return parser.parse_args()

""" Patch extraction functions
"""
#transforms shape of tensor from (..., h, w) to (..., num_patches_y, num_patches_x, tile_size, tile_size)
# ..., num_patches_y, num_patches_x, tile_size, tile_size
def get_patches(tensor, tile_size, stride):
    dims = tensor.dim()
    tensor_unfold = tensor.unfold(dims-2, size = tile_size, step = stride).unfold(dims-1, size = tile_size, step = stride)
    return tensor_unfold

#calculate the areas of each patch for a tensor that was unfolded with the function get_patches
def calculate_areas(tensor):
    dims = tensor.dim()
    return tensor.sum(dim = dims-2).sum(dim = dims-2)

#get the indices of the foreground patches in an unfolded tensor
#based on area calculation, with content threshold 0.2
@add_to_registry
def foreground_patches_filter_1(unfolded_tensor):
    mask_patches_areas = calculate_areas(unfolded_tensor)
    tile_size = unfolded_tensor.shape[-1]
    area_th = 0.2* tile_size * tile_size #0.05
    foreground_patches_idcs = mask_patches_areas > area_th
    return foreground_patches_idcs

#no uso esta funcion ta mal hecha
#read the patch with index (index[0], index[1]) of a slide which was tiled with a size of tile_size
def read_wsi_patch(slide, index, tile_size, zoom_level):
    y_bot, x_bot = tile_size * index[0], tile_size * index[1]
    patch = slide.read_region((x_bot, y_bot), zoom_level, (tile_size, tile_size))
    return patch

#save the foreground patches of a wsi
def save_wsi_foreground_patches(slide_fn, mask_fn, tile_size, zoom_level, output_folder):
    slide = openslide.OpenSlide(slide_fn)
    mask = np.load(mask_fn)
    
    slide_w, slide_h = slide.level_dimensions[0]
    zoom_level_w, zoom_level_h = slide.level_dimensions[zoom_level]    
    mask_h, mask_w = mask.shape

    f = slide_h / zoom_level_h
    tile_size_slide = int(tile_size * f)

    f = zoom_level_h / mask_h
    tile_size_mask = int(tile_size / f)
    
    mask_tensor = torch.Tensor(mask)
    mask_tensor_unfolded = get_patches(mask_tensor, tile_size_mask, tile_size_mask)
    foreground_patches_filter = MODULES_DICT[args.func]
    foreground_patches_idcs = foreground_patches_filter(mask_tensor_unfolded)
    for index, is_foreground in np.ndenumerate(foreground_patches_idcs):
        if is_foreground:
            y_bot, x_bot = tile_size_slide * index[0], tile_size_slide * index[1]
            patch = slide.read_region((x_bot, y_bot), zoom_level, (tile_size, tile_size))
            fn = os.path.join(output_folder, '{}_{}.png'.format(index[0], index[1]))
            patch.save(fn)

"""Complete pipeline for a single image
"""
def pipeline_single_image(fn, args):
    slide_fn = os.path.join(args.slides_dir, fn)
    slide_output_dir = os.path.join(args.o,fn.replace(args.extension, ''))
    os.makedirs(slide_output_dir, exist_ok = True)
    mask_fn = os.path.join(args.masks_dir, fn.replace(args.extension, '.npy'))
    save_wsi_foreground_patches(slide_fn, mask_fn, args.patch_size, args.zoom_level, slide_output_dir)
    return fn

"""Main
"""
def main(args):
    pool = multiprocessing.Pool(args.num_procs)
    files = [f for f in recursive_listdir(args.slides_dir) if args.extension in f]
    dirs = np.unique([os.path.split(f)[0] for f in files])
    output_dirs = [os.path.join(args.o, dir) for dir in dirs]
    for dir in output_dirs:
        os.makedirs(dir, exist_ok=True)
    files = pool.map(partial(pipeline_single_image, args=args), files)
    #para usar apply_async tendria que dividir las imagenes/filenames en distintas listas y llamar apply_asnyc sobre cada lista
    #pool.apply_async(partial(pipeline_single_image, args=args), files)
    pool.close()
    pool.join()

if __name__ == '__main__':
    args = get_args()
    print(args)
    main(args)