import os

from repos_parser import Repo, write_to_json, REPOS_ORIGIN_DIR, REPOS_MPI_DIR


NEW_DATABASE = False
copy = False
repos_dir = REPOS_MPI_DIR
if NEW_DATABASE:
    copy = True
    global_types = {}
    repos_dir = REPOS_ORIGIN_DIR

database = {}
for repo_name in os.listdir(repos_dir):
    repo = Repo(repo_name=repo_name,
                repos_dir=repos_dir,
                copy=copy)
    repo.scan_repo()
    if repo.included:
        database[repo_name] = repo.repo_info[repo_name]
write_to_json(database, 'database')
