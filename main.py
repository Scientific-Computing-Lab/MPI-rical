import os
import sys

project_path = r'/home/nadavsc/LIGHTBITS/code2mpi'
sys.path.append(project_path)
sys.path.append(os.path.join(project_path, 'ast_parse'))
sys.path.append(os.path.join(project_path, 'make'))
sys.path.append(os.path.join(project_path, 'files_parse'))
sys.path.append(os.path.join(project_path, 'queries'))

from make import ast_generator
from files_handler import load_json
from queries_multiprocess import create_ast_db_multiprocess
from logger import set_logger

set_logger()

if __name__ == "__main__":
    programs_db = load_json(os.path.join('DB', 'database_programs.json'))
    create_ast_db_multiprocess(programs_db=programs_db, n_cores=62)
