import os
import json
import re
import shutil
import pickle
import collections

from datetime import date
from files_parser import files_walk, is_include

REPOS_ORIGIN_DIR = '/home/nadavsc/LIGHTBITS/data_gathering_script/git_repos'
REPOS_MPI_DIR = '/home/nadavsc/LIGHTBITS/code2mpi/repositories_MPI'
REPOS_MPI_SLICED_DIR = '/home/nadavsc/LIGHTBITS/code2mpi/repositories_MPI_SLICED'
PROGRAMS_MPI_DIR = '/home/nadavsc/LIGHTBITS/code2mpi/programs'
START_IDX = len(os.path.join(os.getcwd(), REPOS_ORIGIN_DIR)) + 1
script_types = {}


def save_pkl(data, path):
    with open(f'{path}.pkl', 'wb') as f:
        pickle.dump(data, f)


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def write_to_json(data, path):
    if os.path.isfile(path):
        time = date.today().strftime("%m_%d_%y")
        path = re.sub("database\w*", f"database_info_{time}", path)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def repo_mpi_include(repo_path):
    for fpath in files_walk(repo_path):
        if is_include(fpath):
            return True
    return False


def get_repos(user_dir, id=0):
    return {id + offset: {'name': repo_name, 'path': os.path.join(user_dir, repo_name), 'programs': {}} for offset, repo_name in
            enumerate(os.listdir(user_dir))}


def make_dst_folder(dst):
    dstfolder = os.path.dirname(dst)
    if not os.path.exists(dstfolder):
        os.makedirs(dstfolder)


def start_idx_calc(src_origin):
    return len(os.path.join(os.getcwd(), src_origin)) + 1


def src_dst_prep(src, dst, src_origin):
    src = src[start_idx_calc(src_origin):]
    dst = os.path.join(dst, src)
    return src, dst


def copy_file(src, dst, src_origin):
    src, dst = src_dst_prep(src, dst, src_origin)
    make_dst_folder(dst)
    shutil.copy(os.path.join(src_origin, src), dst)