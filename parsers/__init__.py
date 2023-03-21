import os
import re

from files_handler import load_file, files_walk, make_dst_folder
from config import exclude_headers, FORTRAN_EXTENSIONS


def is_main(lines):
    if re.search(r'int main[\s]*[(](.*?)[)]', lines, flags=re.IGNORECASE):
        return True
    return False


def extract_headers(path):
    lines, _, _ = load_file(path, load_by_line=False)
    headers = [header for header in re.findall(f'#[\s]*include[\s]*[<"](.*?)[">]', str(lines), flags=re.IGNORECASE)]
    return os.path.basename(path), headers


class Extractor:
    def __init__(self, real_headers, main_path='', main_name=''):
        self.headers = {}
        self.fake_headers = []
        self.headers_path = []
        self.visit_headers = []
        self.main_path = main_path
        self.main_name = main_name
        self.real_headers = real_headers

    def extraction(self, file_path):
        if file_path in self.headers_path:
            return

        script_name, include_headers = extract_headers(file_path)
        if script_name != self.main_name:
            self.headers_path.append(file_path)

        for header in include_headers:
            if header in self.real_headers.keys():
                self.extraction(self.real_headers[header])

    def is_real(self, fname):
        for path in self.real_headers.keys():
            if path[-len(fname):] == fname and os.path.basename(path) == os.path.basename(fname):
                return path
        return None

    def path_match(self, headers_names):
        headers = {}
        for fname in headers_names:
            if self.real_headers:
                path = self.is_real(fname)
                if path:
                    headers[path] = fname
                elif fname not in exclude_headers:
                    self.fake_headers.append(fname)
        return headers

    def include_headers(self, path):
        self.visit_headers.append(path)
        _, headers_names = extract_headers(path)
        headers = self.path_match(headers_names)

        for header_path, header_name in headers.items():
            if header_path not in self.visit_headers:
                if header_path in self.real_headers:
                    self.include_headers(header_path)
        return list(set(self.fake_headers))


def name_split(filename):
    split = os.path.splitext(filename)
    return split[0], split[1].lower()


def repo_parser(repo_dir, with_ext=True):
    mains = {}
    headers = {}
    c_files = {}
    for idx, (root, dirs, files) in enumerate(os.walk(repo_dir)):
        for fname in files:
            origin_name, ext = name_split(fname)
            name = fname if with_ext else origin_name
            path = os.path.join(root, fname)
            if ext == '.h':
                headers[path] = name
            if ext == '.c':
                lines, _, _ = load_file(path, load_by_line=False)
                if is_main(lines):
                    mains[path] = name
                else:
                    c_files[path] = name
    return mains, headers, c_files


def repo_mpi_include(repo_path):
    for fpath in files_walk(repo_path):
        if is_include(fpath):
            return True
    return False


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


def find_init_final(lines, rm_comments=True):
    if rm_comments:
        lines = remove_comments(lines)  # remove C comments only
    init_match = re.search(r'[n]\s*[a-z^n]*\s*MPI_Init.*?[\\]*[\\][n]', lines, flags=re.IGNORECASE)
    finalize_matches = [match for match in re.finditer(r'MPI_Finalize[^\\]*', lines, flags=re.IGNORECASE)]
    return lines, init_match, finalize_matches


def init_final_slice(path, dst, rm_comments=True):
    lines, name, ext = load_file(path, load_by_line=False)
    lines, init_match, finalize_matches = find_init_final(lines, ext, rm_comments)
    if init_match and finalize_matches and not comment_in_ranges(init_match, lines, ext):
        lines = lines[init_match.span()[0] + 1:finalize_matches[-1].span()[1]]
        lines = line_endings_correction(lines)
        make_dst_folder(dst)
        with open(os.path.join(os.path.split(dst)[0], f'{name}_sliced{ext}'), "w") as f:
            f.write(lines)
        return True
    return False


def remove_block_comments(lines):
    matches = re.findall(r'/\*.*?\*/', lines, re.DOTALL)
    for match in matches:
        lines = lines.replace(match, '')
    return lines


def remove_singleline_comments(lines):
    return re.sub(r'//.*$', '', lines, flags=re.MULTILINE)


def remove_comments(lines):
    lines = remove_block_comments(lines)
    lines = remove_singleline_comments(lines)
    return lines