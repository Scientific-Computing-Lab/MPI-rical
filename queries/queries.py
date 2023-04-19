import os
import pdb
import shutil

from pycparser import c_generator, c_ast

from files_parse import remove_comments, count_lines, mpi_in_line, openmp_in_line, is_include, find_init_final, comment_in_ranges
from files_handler import save_pkl, load_file, load_pkl, files_walk, write_to_json
from funcs_extract_reg import functions_in_header
from funcs_extract_ast import func_export
from if_handler import IfCallsHandler
from funcs_handler import FuncCallsHandler, FuncCallsPlaceHolder
from ast_parse import main_node, origin_funcs

from config import MPI_SERIAL_DIR, MPI_SERIAL_REPLACED_DIR, MPI_SERIAL_SNIPPET_DIR
from logger import info


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
                    lines, init_match, finalize_matches = find_init_final(lines, rm_comments=True)
                    if init_match and finalize_matches and not comment_in_ranges(init_match, lines, ext):  ##TODO: write a comment in ranges function
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


def MPI_to_serial(mpi_db, mode='place_holder'):
    generator = c_generator.CGenerator()
    count_fails = 0
    count_success = 0
    for program_name, paths in mpi_db.items():
        print(program_name)
        ast_file = load_pkl(path=paths['ast'])
        ast_main = main_node(ast_file)
        mpi_re_code = origin_funcs(generator.visit(ast_main))

        try:
            if mode == 'place_holder':
                funcs_handler = FuncCallsPlaceHolder()
            else:
                funcs_handler = FuncCallsHandler()
                if_handler = IfCallsHandler()
                if_handler.visit(ast_main)

            funcs_handler.visit(ast_main)
            re_code = origin_funcs(generator.visit(ast_main))
        except:
            count_fails += 1
            info(f'success: {count_success} | failure: {count_fails} | fail ratio: {count_fails / (count_success + count_fails):2f}')
            continue

        save_dir = os.path.join(MPI_SERIAL_REPLACED_DIR, program_name)
        ast_save_path = os.path.join(save_dir, 'ast')
        os.mkdir(save_dir)

        with open(f'{save_dir}/re_code.c', 'w') as f:
            f.write(re_code)
        with open(f'{save_dir}/mpi_re_code.c', 'w') as f:
            f.write(mpi_re_code)
        save_pkl(data=ast_main, path=ast_save_path)
        count_success += 1
        info(f'success: {count_success} | failure: {count_fails} | fail ratio: {count_fails/(count_success + count_fails):2f}')


def snippets(code):
    snippets = []
    code_length = len(code)
    if code_length < 1000:
        return code
    else:
        for idx in range(0, code_length, 1000):
            snippet = code[idx:idx + 1000]
            if len(snippet) > 700:
                snippets.append(snippet)
    '___SNIPPET'.join(snippets)
    return snippets


def split_codes(mpi_serial_db):
    for program_id, (program_name, paths) in enumerate(mpi_serial_db.items()):
        save_dir = os.path.join(MPI_SERIAL_SNIPPET_DIR, program_name)
        os.mkdir(save_dir)
        code, _, _ = load_file(paths['code'], load_by_line=False)
        mpi_code, _, _ = load_file(paths['mpi_code'], load_by_line=False)
        code_snippets = snippets(code)
        mpi_code_snippets = snippets(mpi_code)
        for idx, snippet in enumerate(code_snippets):
            with open(f'{save_dir}/re_code_{idx}.c', 'w') as f:
                f.write(snippet)
        for idx, snippet in enumerate(mpi_code_snippets):
            with open(f'{save_dir}/mpi_re_code_{idx}.c', 'w') as f:
                f.write(snippet)
        print(f'{program_id} programs have been saved')


def mpi_functions_finder(mpi_db):
    database = {}
    fails = 0
    for idx, (program_name, paths) in enumerate(mpi_db.items()):
        ast = load_pkl(paths['ast'])
        try:
            functions = list(set(func_export(ast)))
        except:
            fails += 1
            continue
        for func_name in functions:
            if 'MPI' in func_name:
                database[func_name] = (database[func_name] if func_name in database else 0) + 1
        print(f'Success: {idx+1-fails} | Fails: {fails} | Ratio: {fails/(idx+1)}')
    write_to_json(database, 'mpi_funcs_per_file.json')
