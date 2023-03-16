import os
import pdb

from repos_parser import write_to_json, save_pkl
from files_parser import load_file, files_walk, count_lines, mpi_in_line, openmp_in_line, is_include
from file_slice import find_init_final, comment_in_ranges
from c_parse import functions_implementations, functions_in_header, function_starter, remove_comments, repo_parser
from parse import ast

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


def init_finalize_count(programs_db):
    count = 0
    for repo in programs_db.values():
        for program_path in repo['programs'].values():
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


def functions_finder(origin_db):
    database = {}
    repo_idx = 0
    for user_id in origin_db.keys():
        for repo in origin_db[user_id]['repos'].values():
            database[repo_idx] = {'name': repo['name'], 'path': repo['path'], 'headers': {}}
            for fpath in files_walk(repo['path']):
                lines, name, ext = load_file(fpath, load_by_line=False)
                lines = remove_comments(lines)  # remove for c only
                if ext == '.h' and name not in database[repo_idx]['headers'].keys():
                    header_functions = [f_header for f_header in functions_in_header(lines)]
                    database[repo_idx]['headers'][name] = header_functions
                    print(header_functions)
            repo_idx += 1
    write_to_json(database, 'header_funcs.json')


def ast_generator(programs_db):
    basic_fake_headers_path = r"/home/nadavsc/LIGHTBITS/code2mpi/c_parse/pycparser/utils/fake_libc_include"
    for repo in programs_db.values():
        for program_path in repo['programs'].values():
            mains, real_headers, c_files = repo_parser(repo_dir=program_path, with_ext=True)
            main_name, main_path = list(mains.keys())[0], list(mains.values())[0]
            code, _, _ = load_file(main_path, load_by_line=False)
            pdb.set_trace()
            ast_file = ast(code=code,
                           main_name=main_name,
                           main_path=main_path,
                           origin_folder=program_path,
                           real_headers=real_headers,
                           basic_fake_headers_path=basic_fake_headers_path)
            pdb.set_trace()
            save_pkl(ast, os.path.join(program_path, f'{main_name[:-2]}_ast'))
            print(ast_file)
    return

