import pdb
import os
import sys

project_path = r'/home/nadavsc/LIGHTBITS/code2mpi'
sys.path.append(project_path)
sys.path.append(os.path.join(project_path, 'ast_parse'))
sys.path.append(os.path.join(project_path, 'make'))
sys.path.append(os.path.join(project_path, 'files_parse'))
sys.path.append(os.path.join(project_path, 'queries'))

import re

from make import ast_generator
from files_handler import load_json
from queries import MPI_to_serial, mpi_functions_finder, lines_counting
from queries_multiprocess import MPI_to_serial_multiprocess, create_ast_db_multiprocess
from database import db_mpi_generate, db_mpi_serial_generate, line_count_stats
from logger import set_logger
from model_eval import conf_matrix, metrics_calc

set_logger()


def F1_calc(results_path):
    with open(results_path, 'r') as f:
        results = f.read()
    references = re.findall(r'reference: (.*?)\n', results)
    candidates = re.findall(r'candidate: (.*?)\n', results)
    all_tp, all_fp, all_tn, all_fn, all_p, all_n = (0, 0, 0, 0, 0, 0)
    for idx, (reference, candidate) in enumerate(zip(references, candidates)):
        tp, fp, tn, fn, p, n = conf_matrix(reference, candidate, metrics=False)
        all_tp += tp
        all_fp += fp
        all_tn += tn
        all_fn += fn
        all_p += p
        all_n += n
        print(idx)
    tpr, tnr, fnr, fpr, precision, recall, f1 = metrics_calc(tp=all_tp, tn=all_tn, fn=all_fn, fp=all_fp)
    # print(f'TP: {tp} TN: {tn} FP: {fp} FN: {fn}')
    print(f'TNR: {tnr:.2f} | FPR: {fpr:.2f} | TPR: {tpr:.2f} | FNR: {fnr:.2f}')
    print(f'Precision: {precision:.2f}')
    print(f'Recall: {recall:.2f}')
    print(f'F1: {f1:.2f}')


if __name__ == "__main__":
    # results_path = '/home/nadavsc/LIGHTBITS/SPT-Code/outputs/5_epochs_320_close_placeholder_translation/translation_test_results.txt'
    results_path = '/home/nadavsc/LIGHTBITS/SPT-Code/outputs/5_epochs_320_close_placeholder_completion/completion_test_results.txt'
    F1_calc(results_path)
    # db_serial_mpi_generate()
    # mpi_db = load_json(os.path.join('DB', 'database_mpi.json'))
    # mpi_lines_count_db = load_json(os.path.join('DB', 'mpi_lines_count.json'))
    # line_count_stats(mpi_lines_count_db)
    # lines_counting(mpi_db)
    # MPI_to_serial_multiprocess(mpi_db)
    # MPI_to_serial(mpi_db)
    # mpi_serial_db = load_json(os.path.join('DB', 'database_mpi_serial_replaced.json'))
    # split_codes(mpi_serial_db)
    # split_codes_multiprocess(mpi_serial_db)
    # mpi_functions_finder(mpi_db)
    # programs_db = load_json(os.path.join('DB', 'database_programs.json'))
    # create_ast_db_multiprocess(programs_db=programs_db, n_cores=62)
