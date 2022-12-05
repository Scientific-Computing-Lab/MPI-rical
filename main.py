import os
import sys, threading
from repos_parser import REPOS_MPI_DIR, REPOS_ORIGIN_DIR
from user import User

from logger import set_logger, info

# sys.settrace
# sys.setrecursionlimit(10000) # max depth of recursion
# threading.stack_size(2**27)  # new thread will get stack of such size
set_logger()


def slice_all_repos():
    for idx, user_name in enumerate(os.listdir(REPOS_MPI_DIR)):
        user = User(user_name=user_name,
                    users_dir=REPOS_MPI_DIR,
                    idx=idx,
                    copy=False)
        user.init_final_slice()


def program_division():
    for idx, user_name in enumerate(os.listdir(REPOS_ORIGIN_DIR)):
        user = User(user_name=user_name,
                    users_dir=REPOS_ORIGIN_DIR,
                    idx=idx,
                    copy=False)
        user.program_division()


# slice_all_repos()
program_division()