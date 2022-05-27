import argparse
import pickle
from PIL import Image
from torchvision import transforms
import pandas as pd
import os
import torch
import torch_geometric


MODULES_DICT = {}
def add_to_registry(fun):
    fun_name = fun.__name__
    MODULES_DICT[fun_name] = fun
    return fun

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_csv", type=str, help='.csv file containing the slides IDs and their labels')
    parser.add_argument("--patches_root", type=str, help='Root of the slides folder with the extracted patches')
    parser.add_argument("--pickles_dir", type=str, help='Out directory for the pickles')
    parser.add_argument("--func", type=str, help='Pickling function')
    parser.add_argument("--csv_out", type=str, help='Out .csv with the pickles filenames')

    return parser.parse_args()

@add_to_registry
def pickle_row_patches(row, root_folder, pickles_folder):
    no_ext = os.path.splitext(row['filename'])[0]
    patches_folder = os.path.join(root_folder, no_ext)
    patches_folder_files = os.listdir(patches_folder)
    patches_tensors_list = list(map(lambda x: transforms.ToTensor()(Image.open(os.path.join(patches_folder, x)).convert('RGB')), patches_folder_files))
    patches_tensors = torch.stack(patches_tensors_list)
    #print(patches_tensors.shape)
    pickle_fn = os.path.join(pickles_folder,'{}.pickle'.format(no_ext))
    with open(pickle_fn, 'wb') as handle:
        pickle.dump(patches_tensors, handle)
    row['filename'] = pickle_fn
    return row

@add_to_registry
def pickle_row_patches_and_edge_index(row, root_folder, pickles_folder):

    def are_adjacent(node_idx_i, node_idx_j):
        x1, y1 = node_idx_i
        x2, y2 = node_idx_j
        return (x2 in range(x1-1, x1+2) ) and (y2 in range(y1-1, y1+2))
    
    
    def make_edge_index(node_indices_list, are_adjacent):
        edge_index = []
    #     print(node_indices_list)
        for i, node_idx_i in enumerate(node_indices_list):
            for j, node_idx_j in enumerate(node_indices_list):
    #             print(node_idx_i)
                if are_adjacent(node_idx_i, node_idx_j):
    #                 print(node_idx_i, node_idx_j)
                    edge_index.append([i, j])
        
        return torch.tensor(edge_index).t().contiguous()

    slide_id = row['filename']
    patches_folder = os.path.join(root_folder, slide_id)
    patches_folder_files = os.listdir(patches_folder)
    patches_idcs = list(map(lambda x: x.split('.')[0], patches_folder_files))
    patches_idcs = list(map(lambda x: [int(x.split('_')[0]), int(x.split('_')[1])], patches_idcs))
    edge_index = make_edge_index(patches_idcs, are_adjacent)

    patches_tensors_list = list(map(lambda x: transforms.ToTensor()(Image.open(os.path.join(patches_folder, x)).convert('RGB')), patches_folder_files))
    patches_tensors = torch.stack(patches_tensors_list)
    #print(patches_tensors.shape)
    to_pickle = (patches_tensors, edge_index)
    pickle_fn = os.path.join(pickles_folder,'{}.pickle'.format(slide_id))
    with open(pickle_fn, 'wb') as handle:
        pickle.dump(to_pickle, handle)
    row['filename'] = pickle_fn
    return row

if __name__ == '__main__':
    args = get_args()
    print(args)
    original_csv = args.in_csv
    root_folder = args.patches_root
    pickles_folder = args.pickles_dir
    os.makedirs(pickles_folder, exist_ok = True)
    original_df = pd.read_csv(original_csv)
    row_pickling_function = MODULES_DICT[args.func]
    new_df = original_df.apply(lambda x: row_pickling_function(x, root_folder, pickles_folder), axis = 1)
    new_csv = args.csv_out
    new_df.to_csv(new_csv, index = False)