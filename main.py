import os

from queries import init_finalize_count
from queries_multiprocess import openmp_mpi_count_multiprocess, init_finalize_count_multiprocess
from repos_parser import PROGRAMS_MPI_DIR, REPOS_MPI_DIR, REPOS_ORIGIN_DIR
from repos_parser import load_json
from c_parse import repo_parser, Extractor
from program import init_folder, copy_files

from logger import set_logger, info

set_logger()


def program_division(db):
    for user_id, user in db.items():
        for repo_id, repo_details in user[user_id]['repos'].items():
            repo_name, repo_dir = repo_details['name'], repo_details['path']
            programs_user_dir = os.path.join(PROGRAMS_MPI_DIR, user['name'])
            programs_repo_dir = os.path.join(programs_user_dir, repo_name)
            mains, repo_headers = repo_parser(REPOS_ORIGIN_DIR, repo_dir)
            if mains and not os.path.exists(programs_user_dir):
                os.makedirs(programs_user_dir)
            for main_path, main_name in mains.items():
                extractor = Extractor(main_name, repo_headers)
                extractor.extraction(main_path)
                headers_path = extractor.headers
                id, program_path = init_folder(programs_repo_dir)
                copy_files(id, repo_name, headers_path, program_path, main_path, repo_dir)


programs_db = load_json(os.path.join('database_programs.json'))
init_finalize_count_multiprocess(programs_db)
# init_finalize_count(programs_db)
# openmp_mpi_count_multiprocess(programs_db, n_cores=32)
