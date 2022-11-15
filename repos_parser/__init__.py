import os
import json
import re
import shutil
import collections

from datetime import date

REPOS_ORIGIN_DIR = '/home/nadavsc/LIGHTBITS/data_gathering_script/git_repos'
REPOS_MPI_DIR = '/home/nadavsc/LIGHTBITS/code2mpi/repositories_MPI'
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


def copy_file(src, dst, MPI_functions):
    src = src[START_IDX:]
    dst = os.path.join(dst, src)
    dstfolder = os.path.dirname(dst)

    if not os.path.exists(dstfolder):
        os.makedirs(dstfolder)

    shutil.copy(os.path.join(REPOS_ORIGIN_DIR, src), dst)
    with open(f'{dst}.json', "w") as f:
        json.dump(MPI_functions, f, indent=4)


def is_print_included(line, ext):
    if ext in FORTRAN_EXTENSIONS:
        return 'print' in line
    else:
        return ('printf' in line) or ('cout' in line)


def mpi_func_included(lines, ext='.c'):
    funcs_count = {}
    funcs = []
    for line in lines:
        line = str(line)
        if not is_print_included(line, ext):
            funcs += re.findall('MPI_\w*', line)  # \S* for all the function
    for func in funcs:
        funcs_count[func] = (funcs_count[func] if func in funcs_count else 0) + 1
    return funcs_count


def mpi_included(line, language='c'):
    line = str(line).lower()
    if language == 'c':
        return '#include' in line and 'mpi.h' in line
    return 'include' in line and 'mpif.h' in line


def get_extension(filename):
    return os.path.splitext(filename)[1].lower()


