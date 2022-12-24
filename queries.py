import os

from files_parser import load_file, files_walk, count_lines, mpi_in_line, openmp_in_line, is_include
from file_slice import find_init_final, comment_in_ranges
from c_parse import functions_implementations, functions_in_header

from logger import set_logger, info


def openmp_mpi_count(db):
    count = 0
    for id, repo in db.items():
        for program_id, program_path in repo['programs'].items():
            mpi_include = False
            openmp_include = False
            fpaths = files_walk(program_path)
            for fpath in fpaths:
                if is_include(fpath, mpi_in_line):
                    mpi_include = True
                if is_include(fpath, openmp_in_line):
                    openmp_include = True
                if mpi_include and openmp_include:
                    info(f'{count} programs have been found')
                    count += 1
                    break
    return count


def init_finalize_count(db):
    count = 0
    for id, repo in db.items():
        for program_id, program_path in repo['programs'].items():
            for fpath in files_walk(program_path):
                lines, name, ext = load_file(fpath, load_by_line=False)
                if ext == '.c':
                    lines, init_match, finalize_matches = find_init_final(lines, ext, rm_comments=True)
                    if init_match and finalize_matches and not comment_in_ranges(init_match, lines, ext):
                        count += 1
                        num_lines = len(count_lines(lines))
                        init_finalize_lines = lines[init_match.span()[0] + 1:finalize_matches[-1].span()[1]]
                        num_lines_init_finalize = len(count_lines(init_finalize_lines)) + 1
                        ratio = num_lines_init_finalize/num_lines
                        info(f'{count} Init-Finalize programs\nAll lines: {num_lines}, Init-Finalize: {num_lines_init_finalize}, Ratio: {ratio:.2f}\n')
    return count


def functions_finder(db):
    for id, repo in db.items():
        header_funcs_path = os.path.join(repo['path'], 'header_funcs.txt')
        if os.path.isfile(header_funcs_path):
            funcs_file, _, _ = load_file(header_funcs_path, load_by_line=False)

        for program_id, program_path in repo['programs'].items():
            if os.path.isfile(header_funcs_path):
                funcs_file, _, _ = load_file(header_funcs_path, load_by_line=False)
            for fpath in files_walk(program_path):
                lines, name, ext = load_file(fpath, load_by_line=False)
                print(name)
                if ext == '.h' and name not in funcs_file:
                    print('IN')
                    header_functions = [f_header[2:] for f_header in functions_in_header(lines)]
                    with open(f'{header_funcs_path}', "a") as f:
                        f.write(f'{name}{ext}\n')
                        for func in header_functions:
                            f.write(f'{func}\n')
                    print(header_functions)

