import os
from repos_parser import REPOS_MPI_DIR, REPOS_ORIGIN_DIR
from repository import Repo

from logger import set_logger, info


set_logger()


def slice_all_repos():
    for idx, repo_name in enumerate(os.listdir(REPOS_MPI_DIR)):
        repo = Repo(repo_name=repo_name,
                    repos_dir=REPOS_MPI_DIR,
                    idx=idx,
                    copy=False)
        repo.init_final_slice()


def slice_repo(repo_name):
    repo = Repo(repo_name=repo_name,
                repos_dir=REPOS_MPI_DIR,
                copy=False)
    repo.init_final_slice()


slice_all_repos()
