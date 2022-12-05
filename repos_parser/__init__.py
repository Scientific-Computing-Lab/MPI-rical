import os
import json
import re
import shutil
import collections

from datetime import date

REPOS_ORIGIN_DIR = '/home/nadavsc/LIGHTBITS/data_gathering_script/git_repos'
REPOS_MPI_DIR = '/home/nadavsc/LIGHTBITS/code2mpi/repositories_MPI'
REPOS_MPI_SLICED_DIR = '/home/nadavsc/LIGHTBITS/code2mpi/repositories_MPI_SLICED'
PROGRAMS_MPI_DIR = '/home/nadavsc/LIGHTBITS/code2mpi/programs'
EXTENSIONS = ['.c', '.f', '.f77', '.f90', '.f95', '.f03', '.cc', '.cpp', '.cxx', '.h']
START_IDX = len(os.path.join(os.getcwd(), REPOS_ORIGIN_DIR)) + 1
FORTRAN_EXTENSIONS = ['.f', '.f77', '.f90', '.f95', '.f03']
script_types = {}


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def write_to_json(data, path):
    if os.path.isfile(path):
        time = date.today().strftime("%m_%d_%y")
        path = re.sub("database\w*", f"database_info_{time}", path)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


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


def name_split(filename):
    split = os.path.splitext(filename)
    return split[0], split[1].lower()
