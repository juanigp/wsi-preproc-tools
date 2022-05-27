import argparse
import os
import multiprocessing
import openslide
from functools import partial
from utils import recursive_listdir
import numpy as np

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", type=str, default='./', help='Directory with the .svs files')
    parser.add_argument("--o", type=str, default='./', help='Directory to store the .jpg outputs')
    parser.add_argument("--num_procs", type=int, default=1, help='Number of processes')
    parser.add_argument("--extension", type=str, default='.svs', help='File extension of the input images')
    parser.add_argument("--zoom_level", type=int, default=2, help='An integer level of zoom, being 0 the highest resolution')

    return parser.parse_args()

def pipeline_single_image(fn, args):
    slide = openslide.OpenSlide(os.path.join(args.i, fn))
    zoom_dims = slide.level_dimensions[args.zoom_level]
    rgba_img = slide.read_region((0,0),args.zoom_level,zoom_dims)
    rgb_img = rgba_img.convert('RGB')
    rgb_img_path = os.path.join(args.o,fn.replace(args.extension,'.jpg'))
    rgb_img.save(rgb_img_path)
    return fn

def main(args):
    # os.makedirs(args.o, exist_ok = True)
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