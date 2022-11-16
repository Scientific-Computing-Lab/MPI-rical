import os
from repos_parser import REPOS_MPI_DIR
from repository import Repo

from logger import set_logger, info


set_logger()
for idx, repo_name in enumerate(os.listdir(REPOS_MPI_DIR)):
    repo = Repo(repo_name=repo_name,
                repos_dir=REPOS_MPI_DIR,
                idx=idx,
                copy=False)
    repo.init_final_slice()
