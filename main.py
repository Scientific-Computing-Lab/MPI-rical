import os
import sys

project_path = r'/home/nadavsc/LIGHTBITS/code2mpi'
sys.path.append(project_path)
sys.path.append(os.path.join(project_path, 'make'))
sys.path.append(os.path.join(project_path, 'files_parser'))
sys.path.append(os.path.join(project_path, 'parsers'))

from queries import ast_generator
from files_parser import load_json
from logger import set_logger

set_logger()

if __name__ == "__main__":
    programs_db = load_json(os.path.join('DB', 'database_programs.json'))
    ast_generator(programs_db)
