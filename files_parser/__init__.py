import os
import re

from logger import set_logger, info

EXTENSIONS = ['.c', '.f', '.f77', '.f90', '.f95', '.f03', '.cc', '.cpp', '.cxx', '.h']
FORTRAN_EXTENSIONS = ['.f', '.f77', '.f90', '.f95', '.f03']


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


def name_split(filename):
    split = os.path.splitext(filename)
    return split[0], split[1].lower()


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


def space_remove(lines):
    lines = re.sub(r"\\n", " ", lines)  # new line in Mac OS
    lines = re.sub(r"\\r", " ", lines)  # new line in Unix/Mac OS
    lines = re.sub(r"\\t", " ", lines)
    lines = re.sub(r"\s+", " ", lines)
    return lines.strip()


def line_endings_correction(lines):
    lines = re.sub(r"\\n", "\n", lines)
    lines = re.sub(r"\\r", "\r", lines)
    lines = re.sub(r"\\t", "\t", lines)
    return lines


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


def comment_matches(lines, ext):
    if ext in FORTRAN_EXTENSIONS:
        return [match for match in re.finditer(r'C[\s].*', lines, flags=re.IGNORECASE)]
    return [match for match in re.finditer(r'\/\*(.*?)\*\/', lines, flags=re.IGNORECASE)]  # r'\/\*[^!]*?\*\/'


def comment_ranges(lines, ext):
    return [range(match.span()[0], match.span()[1]) for match in comment_matches(lines, ext)]


def comment_in_ranges(match, lines, ext):
    for print_range in comment_ranges(lines, ext):
        if match.span()[0] in print_range:
            return True
    return False


def del_comment_line(lines, ext):
    pattern = r'[!][\s]*.*?[\\]*[\\][n]' if ext in FORTRAN_EXTENSIONS else r'[\/][\/].*?[\\]*[\\][n]'
    return re.sub(pattern, '', lines, flags=re.IGNORECASE)


def del_comments(lines, ext):
    lines = del_comment_line(lines, ext)
    if ext not in FORTRAN_EXTENSIONS:
        return re.sub(r'\/\*(.*?)\*\/', '', lines, flags=re.IGNORECASE)