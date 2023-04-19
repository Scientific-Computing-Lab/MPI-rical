import pdb
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
from queries import MPI_to_serial, mpi_functions_finder, split_codes
from queries_multiprocess import create_ast_db_multiprocess, split_codes_multiprocess
from database import db_mpi_generate, db_mpi_serial_generate
from logger import set_logger

set_logger()

if __name__ == "__main__":
    # db_serial_mpi_generate()
    mpi_db = load_json(os.path.join('DB', 'database_mpi.json'))
    MPI_to_serial(mpi_db)
    # mpi_serial_db = load_json(os.path.join('DB', 'database_mpi_serial_replaced.json'))
    # split_codes(mpi_serial_db)
    # split_codes_multiprocess(mpi_serial_db)
    # mpi_functions_finder(mpi_db)
    # programs_db = load_json(os.path.join('DB', 'database_programs.json'))
    # create_ast_db_multiprocess(programs_db=programs_db, n_cores=62)
