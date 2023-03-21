import os
import re

from config import FORTRAN_EXTENSIONS


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


def is_main(lines):
    if re.search(r'int main[\s]*[(](.*?)[)]', lines, flags=re.IGNORECASE):
        return True
    return False


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


def files_walk(root_dir):
    fpaths = []
    for idx, (root, dirs, fnames) in enumerate(os.walk(root_dir)):
        fpaths += [os.path.join(root, fname) for fname in fnames]
    return fpaths


def load_file(path, load_by_line=True):
    name, ext = name_split(os.path.basename(path))
    try:
        with open(path, 'r') as f:
            code = f.readlines() if load_by_line else str(f.read())
    except:
        with open(path, 'rb') as f:
            code = f.read().decode('latin1')
    return code, name, ext


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