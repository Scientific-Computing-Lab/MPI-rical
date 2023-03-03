import os
from repos_parser import PROGRAMS_MPI_DIR, REPOS_MPI_DIR, REPOS_ORIGIN_DIR, copy_file

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