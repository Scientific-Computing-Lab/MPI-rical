import os

from repos_parser import Repo, write_to_json, REPOS_ORIGIN_DIR, REPOS_MPI_DIR


NEW_DATABASE = True
copy = False
repos_dir = REPOS_MPI_DIR
if NEW_DATABASE:
    copy = True
    repos_dir = REPOS_ORIGIN_DIR


def scrap():
    database_info = {}
    for idx, repo_name in enumerate(os.listdir(repos_dir)):
        print(repo_name)
        repo = Repo(repo_name=repo_name,
                    repos_dir=repos_dir,
                    idx=idx,
                    copy=copy)
        repo.scan_repo()
        if repo.included:
            database_info[repo_name] = repo.repo_info[repo_name]
    write_to_json(database_info, 'database')


def slice_code():
    for repo_name in os.listdir(repos_dir):
        repo = Repo(repo_name=repo_name,
                    repos_dir=repos_dir,
                    copy=copy)
        repo.init_final_slice()

scrap()
