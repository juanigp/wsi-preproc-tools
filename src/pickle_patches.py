import argparse
import pickle
from PIL import Image
from torchvision import transforms
import os
import torch
from utils import recursive_listdir
import numpy as np
import multiprocessing
from functools import partial

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--i", type=str, default='./', help='Directory with the patches')
    parser.add_argument("--o", type=str, default='./', help='Directory to store the pickles')
    parser.add_argument("--num_procs", type=int, default=1, help='Number of processes')
    return parser.parse_args()

def pipeline_single_image(fn, args):
    
    def are_adjacent(node_idx_i, node_idx_j):
        x1, y1 = node_idx_i
        x2, y2 = node_idx_j
        return (x2 in range(x1-1, x1+2) ) and (y2 in range(y1-1, y1+2))
    
    def make_edge_index(node_indices_list, are_adjacent):
        edge_index = []
        for i, node_idx_i in enumerate(node_indices_list):
            for j, node_idx_j in enumerate(node_indices_list):
                if are_adjacent(node_idx_i, node_idx_j):
                    edge_index.append([i, j])
        
        return torch.tensor(edge_index).t().contiguous()

    pickle_fn = os.path.join(args.o,'{}.pickle'.format(fn)) 
    if os.path.exists(pickle_fn):
        return fn
        
    patches_folder = os.path.join(args.i, fn)
    patches_folder_files = os.listdir(patches_folder)
    patches_idcs = list(map(lambda x: x.split('.')[0], patches_folder_files))
    patches_idcs = list(map(lambda x: [int(x.split('_')[0]), int(x.split('_')[1])], patches_idcs))
    edge_index = make_edge_index(patches_idcs, are_adjacent)

    patches_tensors_list = list(map(lambda x: transforms.ToTensor()(Image.open(os.path.join(patches_folder, x)).convert('RGB')), patches_folder_files))
    patches_tensors = torch.stack(patches_tensors_list)
    to_pickle = (patches_tensors, edge_index)
    
    with open(pickle_fn, 'wb') as handle:
        pickle.dump(to_pickle, handle)
    return fn

def main(args):
    pool = multiprocessing.Pool(args.num_procs)
    files = list(filter(lambda x: '.png' in x, recursive_listdir(args.i))) # patches are always saved in .png format
    patches_dirs = np.unique([os.path.split(f)[0] for f in files])
    output_dirs = np.unique(list(map(lambda x: os.path.split(x)[0], patches_dirs )))
    output_dirs = list(map(lambda x: os.path.join(args.o, x), output_dirs))
    for dir in output_dirs:
        os.makedirs(dir, exist_ok=True)
    patches_dirs = pool.map(partial(pipeline_single_image, args=args), patches_dirs)
    pool.close()
    pool.join()

if __name__ == '__main__':
    args = get_args()
    print(args)
    main(args)