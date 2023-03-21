import os

from parsers import Extractor, repo_parser
from files_handler import copy_file
from config import PROGRAMS_MPI_DIR, REPOS_MPI_DIR, REPOS_ORIGIN_DIR
from logger import info


def copy_files(id, name, headers_path, c_files_path, program_path, main_path, repo_dir):
    copy_file(src=main_path, dst=program_path, src_origin=repo_dir)
    for header_path in headers_path:
        copy_file(src=header_path, dst=program_path, src_origin=repo_dir)
    for c_file_path in c_files_path:
        copy_file(src=c_file_path, dst=program_path, src_origin=repo_dir)
    # info(f'PROGRAM {id} has been created - Origin repo: {name}')


def init_folder(programs_repo_dir):
    if not os.path.exists(programs_repo_dir):
        os.makedirs(programs_repo_dir)
    programs_names = os.listdir(programs_repo_dir)
    if programs_names:
        id = int(programs_names[-1].split('_')[1]) + 1
    else:
        id = 0
    path = os.path.join(os.path.join(programs_repo_dir, f'program_{id}'))
    os.makedirs(path)
    return id, path


def program_division(origin_db, functions_db):
    for user_id, user in origin_db.items():
        for repo_id, repo_details in user['repos'].items():
            repo_name, repo_dir = repo_details['name'], repo_details['path']
            programs_user_dir = os.path.join(PROGRAMS_MPI_DIR, user['name'])
            programs_repo_dir = os.path.join(programs_user_dir, repo_name)
            mains, real_headers, _ = repo_parser(repo_dir)
            if mains and not os.path.exists(programs_user_dir):
                os.makedirs(programs_user_dir)
            for main_name, main_path in mains.items():
                extractor = Extractor(main_path, main_name, real_headers)
                extractor.extraction(main_path)
                headers_path = extractor.headers
                c_files_path = extractor.c_files(functions_db, repo_dir, headers_path)
                id, program_path = init_folder(programs_repo_dir)
                copy_files(id, repo_name, headers_path, c_files_path, program_path, main_path, repo_dir)