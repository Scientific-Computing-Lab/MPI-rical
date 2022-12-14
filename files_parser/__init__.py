import os
import re

from repos_parser import FORTRAN_EXTENSIONS
from logger import set_logger, info


def files_walk(root_dir):
    fpaths = []
    for idx, (root, dirs, fnames) in enumerate(os.walk(root_dir)):
        fpaths += [os.path.join(root, fname) for fname in fnames]
    return fpaths


def load_file(path, load_by_line=True):
    name, ext = name_split(os.path.basename(path))
    with open(path, 'rb') as f:
        if load_by_line:
            return f.readlines(), name, ext
        return str(f.read()), name, ext


def file_headers(path):
    lines = load_file(path, load_by_line=False)
    headers = [f'{header}.h' for header in re.findall(f'[<"](.*?).h[">]', str(lines), flags=re.IGNORECASE)]
    return os.path.basename(path), [header.split('/')[-1] for header in headers]


def name_split(filename):
    split = os.path.splitext(filename)
    return split[0], split[1].lower()


def get_headers(lines):
    headers = [f'{header}.h' for header in re.findall(f'[<"](.*?).h[">]', str(lines), flags=re.IGNORECASE)]
    return [header.split('/')[-1] for header in headers]


def is_main(lines):
    if re.search(r'int main[(](.*?)[)]', lines, flags=re.IGNORECASE):
        return True


def count_lines(lines):
    return re.findall(r'[^n\\][a-z](.*?)[\\][n]', lines, flags=re.IGNORECASE)


def print_in_line(line, ext):
    line = str(line).lower()
    if ext in FORTRAN_EXTENSIONS:
        return 'print' in line
    return ('printf' in line) or ('cout' in line)


def mpi_in_line(line, ext):
    line = str(line).lower()
    if ext in FORTRAN_EXTENSIONS:
        return 'include' in line and 'mpif.h' in line
    return '#include' in line and 'mpi.h' in line


def openmp_in_line(line, ext):
    line = str(line).lower()
    if ext in FORTRAN_EXTENSIONS:
        return 'use' in line and 'omp_lib' in line
    return '#include' in line and 'omp.h' in line


def is_include(path, func=mpi_in_line):
    lines, name, ext = load_file(path, load_by_line=True)
    for line in lines:
        if func(line, ext):
            return True
    return False


def mpi_funcs_counter(path):
    lines, name, ext = load_file(path, load_by_line=True)
    funcs = []
    funcs_counter = {}
    for line in lines:
        line = str(line)
        if not print_in_line(line, ext):
            funcs += re.findall('MPI_\w*', line)  # \S* for all the function
    for func in funcs:
        funcs_counter[func] = (funcs_counter[func] if func in funcs_counter else 0) + 1
    return funcs_counter
