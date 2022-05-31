import argparse
import os
import multiprocessing
from functools import partial
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = pow(2,40).__str__()
import cv2
import numpy as np
from utils import recursive_listdir
from binarization_functions import *
from registry import BINARIZATION_FUNCTIONS
# from PIL import Image

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
    binarisation_func = BINARIZATION_FUNCTIONS[args.func]
    mask = binarisation_func(img)
    new_fn = os.path.join(args.o, '{}.npy'.format(fn).replace(args.extension,''))
    np.save(new_fn, mask)
    # mask_img = Image.fromarray( (mask * 255).astype(np.uint8) ).convert("L")
    # mask_img.save('{}.jpg'.format(new_fn))
    return fn

"""Main
"""
def main(args):
    pool = multiprocessing.Pool(args.num_procs)
    files = [f for f in recursive_listdir(args.i) if args.extension in f]
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