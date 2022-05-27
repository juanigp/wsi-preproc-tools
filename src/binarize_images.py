import argparse
import os
import multiprocessing
from functools import partial
import cv2
import numpy as np
import utils

MODULES_DICT = {}
def add_to_registry(fun):
    fun_name = fun.__name__
    MODULES_DICT[fun_name] = fun
    return fun

@add_to_registry
def binarize_1(img):
    return utils.binarize_1(img)

@add_to_registry
def stain_entropy_otsu(img):
    return utils.stain_entropy_otsu(img)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", type=str, default='./', help='Directory with the images to binarize')
    parser.add_argument("--o", type=str, default='./', help='Directory to store the .npy outputs')
    parser.add_argument("--extension", type=str, default='.jpg', help='File extension of the input images')
    parser.add_argument("--func", type=str, help='Binarisation function')
    parser.add_argument("--num_procs", type=int, default=1, help='Number of processes')

    return parser.parse_args()


"""Complete pipeline for a single image
"""
def pipeline_single_image(fn, args):
    img = cv2.imread(os.path.join(args.i, fn))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    binarisation_func = MODULES_DICT[args.func]
    mask = binarisation_func(img)
    new_fn = os.path.join(args.o, '{}.npy'.format(fn).replace(args.extension,''))
    np.save(new_fn, mask)
    return fn

"""Main
"""
def main(args):
    os.makedirs(args.o, exist_ok = True)
    pool = multiprocessing.Pool(args.num_procs)
    files = [f for f in os.listdir(args.i) if args.extension in f]
    files = pool.map(partial(pipeline_single_image, args=args), files)
    #para usar apply_async tendria que dividir las imagenes/filenames en distintas listas y llamar apply_asnyc sobre cada lista
    #pool.apply_async(partial(pipeline_single_image, args=args), files)
    pool.close()
    pool.join()

if __name__ == '__main__':
    args = get_args()
    print(args)
    main(args)