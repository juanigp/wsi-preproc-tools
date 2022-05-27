
   
import argparse
import os
import multiprocessing
from functools import partial
from torchstain import MacenkoNormalizer
import numpy as np
from PIL import Image
import cv2

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", type=str, default='./', help='Directory with the .svs files')
    parser.add_argument("--o", type=str, default='./', help='Directory to store the .jpg outputs')
    parser.add_argument("--num_procs", type=int, default=1, help='Number of processes')
    #other arguments you may have

    return parser.parse_args()

def pipeline_single_image(fn, args):
    img = cv2.imread(os.path.join(args.i, fn))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #do the processing of a single image
    HERef = np.array([
        [0.60572728, 0.30469822],
        [0.65218983, 0.87287363],
        [0.44714489, 0.36041555]])
    maxCRef = 0.9350767513968594

    normalizer = MacenkoNormalizer(backend = 'numpy')
    normalizer.HERef = HERef
    normalizer.maxCRef = maxCRef

    normalized_img = normalizer.normalize(I = img, stains = False)[0]
    normalized_img = Image.fromarray(normalized_img)
    normalized_img.save(os.path.join(args.o, fn))
    return fn

def main(args):
    os.makedirs(args.o, exist_ok = True)
    pool = multiprocessing.Pool(args.num_procs)
    files = [f for f in os.listdir(args.i)]
    files = pool.map(partial(pipeline_single_image, args=args), files)
    pool.close()
    pool.join()

if __name__ == '__main__':
    args = get_args()
    print(args)
    main(args)

