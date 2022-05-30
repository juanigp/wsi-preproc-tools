import os

def recursive_listdir(root_dir):
  files_list = []
  for root, dirs, files in os.walk(root_dir):
    for filename in files:
        files_list.append(os.path.join(os.path.relpath(root, root_dir), filename))
  return files_list

