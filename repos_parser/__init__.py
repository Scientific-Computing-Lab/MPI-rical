import os
import json
import re
import shutil
import collections

from datetime import date

REPOS_ORIGIN_DIR = '/home/nadavsc/LIGHTBITS/data_gathering_script/git_repos'
REPOS_MPI_DIR = '/home/nadavsc/LIGHTBITS/code2mpi/repositories_MPI'
REPOS_MPI_SLICED_DIR = '/home/nadavsc/LIGHTBITS/code2mpi/repositories_MPI_SLICED'
EXTENSIONS = ['.c', '.f', '.f77', '.f90', '.f95', '.f03', '.cc', '.cpp', '.cxx', '.h']
START_IDX = len(os.path.join(os.getcwd(), REPOS_ORIGIN_DIR)) + 1
FORTRAN_EXTENSIONS = ['.f', '.f77', '.f90', '.f95', '.f03']
script_types = {}


def write_to_json(data, path):
    if os.path.isfile(path):
        time = date.today().strftime("%m_%d_%y")
        path = re.sub("database\w*", f"database_info_{time}", path)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def start_idx_calc(repo_dir):
    return len(os.path.join(os.getcwd(), repo_dir)) + 1


def make_dst_folder(dst):
    dstfolder = os.path.dirname(dst)
    if not os.path.exists(dstfolder):
        os.makedirs(dstfolder)


def src_dst_prep(src, dst, src_repo):
    src = src[start_idx_calc(src_repo):]
    dst = os.path.join(dst, src)
    return src, dst


def copy_file(src, dst, src_repo):
    src, dst = src_dst_prep(src, dst, src_repo)
    make_dst_folder(dst)
    shutil.copy(os.path.join(src_repo, src), dst)


def name_split(filename):
    split = os.path.splitext(filename)
    return split[0], split[1].lower()
