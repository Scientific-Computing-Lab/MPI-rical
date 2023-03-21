import os
import shutil

from parsers import repo_parser, remove_comments, count_lines, mpi_in_line, openmp_in_line, is_include, find_init_final, comment_in_ranges
from files_handler import load_file, files_walk, write_to_json, save_pkl
from funcs_extract_reg import functions_in_header
from datetime import datetime
from parse import ast

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


def init_folders(save_repo_outputs_dir, idx):
    save_outputs_dir = os.path.join(save_repo_outputs_dir, idx)
    fake_headers_path = os.path.join(save_outputs_dir, 'fake_headers')

    os.mkdir(save_outputs_dir)
    os.mkdir(fake_headers_path)
    return save_outputs_dir, fake_headers_path


def ast_generator(programs_db):
    count_success = 0
    count_failure = 0
    basic_fake_headers_path = r"../parsers/pycparser/utils/fake_libc_include"
    cur_time = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    logger_path = fr'/home/nadavsc/LIGHTBITS/code2mpi/logger/ast_logger_{cur_time}.txt'
    with open(logger_path, 'w') as f:
        f.write('')

    for repo in programs_db.values():
        save_repo_outputs_dir = os.path.join(os.path.dirname(repo['programs']['0']), 'outputs')
        if os.path.exists(save_repo_outputs_dir):
            shutil.rmtree(save_repo_outputs_dir)
        os.mkdir(save_repo_outputs_dir)
        for idx, program_path in repo['programs'].items():
            print(program_path)
            fake_files = os.path.join(program_path, 'fake_files')
            fake_headers = os.path.join(program_path, 'fake_headers')
            if os.path.exists(fake_files):
                shutil.rmtree(fake_files)
            if os.path.exists(fake_headers):
                shutil.rmtree(fake_headers)
            save_outputs_dir, fake_headers_path = init_folders(save_repo_outputs_dir, idx)
            try:
                mains, real_headers, c_files = repo_parser(repo_dir=program_path, with_ext=True)
                main_path, main_name = list(mains.keys())[0], list(mains.values())[0]
                code, _, _ = load_file(main_path, load_by_line=False)
                ast_file = ast(code=code,
                               main_name=main_name,
                               main_path=main_path,
                               origin_folder=program_path,
                               real_headers=real_headers,
                               save_outputs_dir=save_outputs_dir,
                               fake_headers_path=fake_headers_path,
                               basic_fake_headers_path=basic_fake_headers_path)
                save_pkl(ast_file, os.path.join(save_outputs_dir, f'ast_{main_name[:-2]}'))
                count_success += 1
            except:
                cur_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                with open(logger_path, 'a') as f:
                    f.write(f'{cur_time}: {program_path}\n')
                count_failure += 1
            info(f'ast success: {count_success} | ast failure: {count_failure}')
    return


# 16/03/2023 22:13:55: ast success: 11,603 | ast failure: 3832 | fail ratio: 24.8%
# 18/03/2023 16:59:38: ast success: 11,150 | ast failure: 4285 | fail ratio: 27.7%
# 19/03/2023 04:48:33: ast success: 50,396 | ast failure: 23,462 | fail ratio:
