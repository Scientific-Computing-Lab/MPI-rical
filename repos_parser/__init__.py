import os
import json

REPOS_ORIGIN_DIR = '/home/nadavsc/LIGHTBITS/data_gathering_script/git_repos'
REPOS_MPI_DIR = '/home/nadavsc/LIGHTBITS/code2mpi/repositories_MPI'
EXTENSIONS = ['.c', '.f', '.f77', '.f90', '.f95', '.f03', '.cc', '.cpp', '.cxx', '.h']
FORTRAN_EXTENSIONS = ['.f', '.f77', '.f90', '.f95', '.f03']
START_IDX = len(os.path.join(os.getcwd(), REPOS_ORIGIN_DIR)) + 1


def write_to_json(data, path):
    with open(os.path.join(path[:-2], '.json'), "w") as f:
        json.dump(data, f, indent=4)